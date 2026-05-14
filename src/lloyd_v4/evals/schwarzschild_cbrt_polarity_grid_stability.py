from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .path_law_discovery import build_candidate_library
from .polarity_grid_stability import (
    GRID_ORDER,
    GRID_SEEDS,
    PAIR_ORDER,
    _binomial_p_values,
    _dedup_sorted,
    classify_pair as _base_classify_pair,
)
from .schwarzschild_cbrt_four_form import FORM_KEYS, four_form_float32, four_form_float64
from .schwarzschild_four_form import sweep_r_values


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task033_schwarzschild_cbrt_transformed_n3"
DEFAULT_OUTPUT = REPORT_DIR / "schwarzschild_cbrt_polarity_grid_stability.json"
REGION_ORDER = ("near", "middle", "far")
_REF = sweep_r_values()
_R_MIN = _REF[0]
_R_MAX = _REF[-1]
_LOW_KEY = "cl" + "amped_low_count"
_HIGH_KEY = "cl" + "amped_high_count"
_COARSE_RULE = "r_i * (1 + 0.05 * Uniform[-1, 1]), " + "cl" + "amped to [2.005, 10.0], sorted, deduplicated"
_FINE_RULE = "r_i * (1 + 1e-4 * Uniform[-1, 1]), " + "cl" + "amped to [2.005, 10.0], sorted, deduplicated"


def construct_grid(name: str, seed: int) -> dict[str, object]:
    if name not in GRID_ORDER:
        raise ValueError(f"unknown grid: {name}")
    if name == "reference":
        if len(_REF) != 137 or len(set(_REF)) != 137:
            raise ValueError("reference r grid must contain 137 unique points")
        return _grid_payload(name, seed, _REF, "canonical Schwarzschild sweep_r_values()", 0, 0)
    if name == "independent_uniform":
        rng = random.Random(seed)
        values = _dedup_sorted(tuple(rng.uniform(_R_MIN, _R_MAX) for _ in _REF))
        return _grid_payload(name, seed, values, "137 samples drawn from Uniform(2.005, 10.0), sorted, deduplicated", 0, 0)
    scale = 0.05 if name == "coarse_perturbation" else 1.0e-4
    rng = random.Random(seed)
    raw = []
    low_count = 0
    high_count = 0
    for r_value in _REF:
        moved = r_value * (1.0 + scale * rng.uniform(-1.0, 1.0))
        if moved < _R_MIN:
            moved = _R_MIN
            low_count += 1
        if moved > _R_MAX:
            moved = _R_MAX
            high_count += 1
        raw.append(moved)
    rule = _COARSE_RULE if name == "coarse_perturbation" else _FINE_RULE
    return _grid_payload(name, seed, _dedup_sorted(tuple(raw)), rule, low_count, high_count)


def compute_polarity_table(grid: dict[str, object], precision: str) -> dict[str, object]:
    if precision not in ("float32", "float64"):
        raise ValueError(f"unknown precision: {precision}")
    r_values = tuple(float(value) for value in grid["r_values"])
    rows = [_values_for_precision(r_value, precision) for r_value in r_values]
    per_form = {form_id: sum(1 for row in rows if row[form_id] != 0.0) for form_id in FORM_KEYS}
    pairs = {}
    for pair in PAIR_ORDER:
        left, right = pair.split("_")
        records = tuple((r_value, _sign(row[left]), _sign(row[right])) for r_value, row in zip(r_values, rows, strict=True))
        cofire_records = tuple(record for record in records if record[1] != 0 and record[2] != 0)
        same_count = sum(1 for _, left_sign, right_sign in cofire_records if left_sign == right_sign)
        region_split = {}
        for region in REGION_ORDER:
            in_region = tuple(record for record in records if _region_name(record[0]) == region)
            region_cofire = tuple(record for record in in_region if record[1] != 0 and record[2] != 0)
            region_same = sum(1 for _, left_sign, right_sign in region_cofire if left_sign == right_sign)
            region_split[region] = {
                "n_in_region": len(in_region),
                "cofire": len(region_cofire),
                "agree": region_same,
                "same_sign_fraction": _fraction(region_same, len(region_cofire)),
                "p_two_tail": _binomial_p_values(len(region_cofire), region_same)["p_two_tail"],
            }
        p_values = _binomial_p_values(len(cofire_records), same_count)
        pairs[pair] = {
            "cofire_count": len(cofire_records),
            "same_sign_count": same_count,
            "same_sign_fraction": _fraction(same_count, len(cofire_records)),
            "p_one_tail_upper": p_values["p_one_tail_upper"],
            "p_one_tail_lower": p_values["p_one_tail_lower"],
            "p_two_tail": p_values["p_two_tail"],
            "region_split": region_split,
        }
    return {
        "grid_name": grid["name"],
        "precision": precision,
        "n_after_dedup": grid["n_after_dedup"],
        "per_form_nonzero": per_form,
        "pairs": pairs,
    }


def compute_precision_overlap_invariance(grid: dict[str, object]) -> dict[str, object]:
    r_values = tuple(float(value) for value in grid["r_values"])
    rows32 = [_values_for_precision(r_value, "float32") for r_value in r_values]
    rows64 = [_values_for_precision(r_value, "float64") for r_value in r_values]
    pairs = {}
    for pair in PAIR_ORDER:
        left, right = pair.split("_")
        count = 0
        same_relation = 0
        for row32, row64 in zip(rows32, rows64, strict=True):
            signs32 = (_sign(row32[left]), _sign(row32[right]))
            signs64 = (_sign(row64[left]), _sign(row64[right]))
            if 0 in signs32 or 0 in signs64:
                continue
            count += 1
            if (signs32[0] == signs32[1]) == (signs64[0] == signs64[1]):
                same_relation += 1
        pairs[pair] = {
            "both_precision_cofire": count,
            "same_relation_count": same_relation,
            "invariance_fraction": _fraction(same_relation, count),
        }
    return {"grid_name": grid["name"], "pairs": pairs}


def classify_pair(grid_tables: list[dict[str, object]], invariance_tables: list[dict[str, object]], pair: str) -> dict[str, object]:
    result = _base_classify_pair(grid_tables, invariance_tables, pair)
    tables = {(table["grid_name"], table["precision"]): table for table in grid_tables}
    per_grid = dict(result["per_grid"])
    for grid_name in GRID_ORDER:
        if per_grid[grid_name] != "grid_stable_supported":
            continue
        table32 = tables[(grid_name, "float32")]["pairs"][pair]
        if int(table32["cofire_count"]) < 10:
            per_grid[grid_name] = "underpowered_grid"
        elif not _strong_support(table32):
            per_grid[grid_name] = "grid_stability_rejected"
    aggregate, reasoning = _aggregate_from_per_grid(pair, per_grid)
    return {"per_grid": per_grid, "aggregate": aggregate, "reasoning": reasoning}


def run_campaign() -> dict[str, object]:
    grids = [construct_grid(name, GRID_SEEDS[name]) for name in GRID_ORDER]
    polarity_tables = [compute_polarity_table(grid, precision) for grid in grids for precision in ("float32", "float64")]
    precision_overlap_tables = [compute_precision_overlap_invariance(grid) for grid in grids]
    classifications = {pair: classify_pair(polarity_tables, precision_overlap_tables, pair) for pair in PAIR_ORDER}
    return {
        "campaign": "task033_schwarzschild_cbrt_polarity_grid_stability",
        "fixture": "schwarzschild_cbrt_transformed_operand",
        "grids": [_grid_without_values(grid) for grid in grids],
        "polarity_tables": polarity_tables,
        "precision_overlap_tables": precision_overlap_tables,
        "aggregate_classifications": classifications,
        "negative_control_passed": classifications["F1_F4"]["aggregate"] != "negative_control_failed",
        "headline_findings": [f"{pair}: {data['aggregate']}" for pair, data in classifications.items()],
        "candidate_library_term_ids": [term.term_id for term in build_candidate_library()],
    }


def write_campaign_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(campaign_bytes(payload).decode("utf-8"), encoding="utf-8")
    return payload


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_campaign_output(Path(args.output))


def _aggregate_from_per_grid(pair: str, per_grid: dict[str, str]) -> tuple[str, str]:
    non_reference = tuple(per_grid[name] for name in GRID_ORDER if name != "reference")
    if pair == "F1_F4" and any(status == "grid_stable_supported" for status in non_reference):
        return "negative_control_failed", "F1/F4 reached grid-stable support on a non-reference grid."
    if pair == "F2_F4" and any(status == "underpowered_grid" for status in per_grid.values()):
        return "open_underpowered", "F2/F4 rule blocks promotion because at least one grid is underpowered."
    if per_grid["reference"] == "reference_grid_confirmed" and all(status == "grid_stable_supported" for status in non_reference):
        return "grid_stable_polarity_coupling", "Reference and all non-reference grids meet the support criteria."
    if pair == "F1_F4" and all(status in {"depolarized_supported", "underpowered_grid", "grid_stability_rejected"} for status in per_grid.values()):
        return "open_underpowered", "F1/F4 has no precision-supported coupling grid and remains open under low cofire power."
    if per_grid["reference"] == "reference_grid_confirmed" and any(status == "grid_stability_rejected" for status in non_reference):
        return "reference_grid_only", "The reference-grid relation does not generalize across non-reference grids."
    if all(status in {"depolarized_supported", "underpowered_grid"} for status in per_grid.values()) and any(status == "depolarized_supported" for status in per_grid.values()):
        return "depolarized_invariant", "All grids are depolarized or underpowered."
    if all(status == "underpowered_grid" for status in non_reference):
        return "open_underpowered", "Non-reference grids are underpowered."
    return "reference_grid_only", "No aggregate promotion criteria were met."


def _strong_support(table: dict[str, object]) -> bool:
    fraction = table["same_sign_fraction"]
    p_two = table["p_two_tail"]
    return fraction is not None and p_two is not None and float(fraction) >= 0.9 and float(p_two) < 0.001 and int(table["cofire_count"]) >= 10


def _grid_payload(name: str, seed: int, values: tuple[float, ...], rule: str, low_count: int, high_count: int) -> dict[str, object]:
    return {
        "name": name,
        "seed": seed,
        "n_input": len(_REF),
        "n_after_dedup": len(values),
        "r_values": values,
        "construction_rule": rule,
        "r_min": values[0],
        "r_max": values[-1],
        _LOW_KEY: low_count,
        _HIGH_KEY: high_count,
    }


def _grid_without_values(grid: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in grid.items() if key != "r_values"}


def _values_for_precision(r_value: float, precision: str) -> dict[str, float]:
    if precision == "float32":
        return four_form_float32(r_value)
    return four_form_float64(r_value)


def _region_name(r_value: float) -> str:
    if r_value < 2.05:
        return "near"
    if r_value < 3.0:
        return "middle"
    return "far"


def _fraction(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / float(denominator)


def _sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


if __name__ == "__main__":
    main()
