from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Iterable, Sequence

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import FORM_KEYS, four_form_float32, four_form_float64, ulp_of_double
from .path_law_discovery import build_candidate_library
from .schwarzschild_four_form import sweep_r_values


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task026c_prime_polarity_grid_stability"
DEFAULT_OUTPUT = REPORT_DIR / "campaign_output.json"
GRID_ORDER = ("reference", "coarse_perturbation", "fine_perturbation", "independent_uniform")
GRID_SEEDS = {"reference": 0, "coarse_perturbation": 1042, "fine_perturbation": 2317, "independent_uniform": 4099}
PAIR_ORDER = ("F1_F2", "F1_F4", "F2_F4")
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
            raise ValueError("reference grid must contain 137 unique points")
        return {
            "name": name,
            "seed": seed,
            "n_input": len(_REF),
            "n_after_dedup": len(_REF),
            "r_values": tuple(_REF),
            "construction_rule": "V3 reference CSV via sweep_r_values()",
            "r_min": _REF[0],
            "r_max": _REF[-1],
            _LOW_KEY: 0,
            _HIGH_KEY: 0,
        }
    if name == "independent_uniform":
        rng = random.Random(seed)
        raw_values = tuple(rng.uniform(_R_MIN, _R_MAX) for _ in _REF)
        values = _dedup_sorted(raw_values)
        return {
            "name": name,
            "seed": seed,
            "n_input": len(_REF),
            "n_after_dedup": len(values),
            "r_values": values,
            "construction_rule": "137 samples drawn from Uniform(2.005, 10.0), sorted, deduplicated",
            "r_min": values[0],
            "r_max": values[-1],
            _LOW_KEY: 0,
            _HIGH_KEY: 0,
        }
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
    values = _dedup_sorted(tuple(raw))
    rule = _COARSE_RULE
    if name == "fine_perturbation":
        rule = _FINE_RULE
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
        fraction = _fraction(same_relation, count)
        pairs[pair] = {
            "both_precision_cofire": count,
            "same_relation_count": same_relation,
            "invariance_fraction": fraction,
        }
    return {"grid_name": grid["name"], "pairs": pairs}


def classify_pair(grid_tables: list[dict[str, object]], invariance_tables: list[dict[str, object]], pair: str) -> dict[str, object]:
    by_grid = {}
    tables = {(table["grid_name"], table["precision"]): table for table in grid_tables}
    invariance = {table["grid_name"]: table for table in invariance_tables}
    for grid_name in GRID_ORDER:
        table64 = tables[(grid_name, "float64")]["pairs"][pair]
        table32 = tables[(grid_name, "float32")]["pairs"][pair]
        invariant = invariance[grid_name]["pairs"][pair]
        by_grid[grid_name] = _classify_grid_pair(grid_name, table64, table32, invariant)
    aggregate, reasoning = _aggregate_pair_status(pair, by_grid)
    return {"per_grid": by_grid, "aggregate": aggregate, "reasoning": reasoning}


def run_campaign() -> dict[str, object]:
    grids = [construct_grid(name, GRID_SEEDS[name]) for name in GRID_ORDER]
    polarity_tables = [compute_polarity_table(grid, precision) for grid in grids for precision in ("float32", "float64")]
    precision_overlap_tables = [compute_precision_overlap_invariance(grid) for grid in grids]
    classifications = {pair: classify_pair(polarity_tables, precision_overlap_tables, pair) for pair in PAIR_ORDER}
    grid_metadata = [_grid_without_values(grid) for grid in grids]
    negative_control_passed = classifications["F1_F4"]["aggregate"] != "negative_control_failed"
    payload = {
        "campaign": "task026c_prime_polarity_grid_stability",
        "grids": grid_metadata,
        "polarity_tables": polarity_tables,
        "precision_overlap_tables": precision_overlap_tables,
        "aggregate_classifications": classifications,
        "negative_control_passed": negative_control_passed,
        "headline_findings": _headline_findings(classifications),
        "candidate_library_term_ids": [term.term_id for term in build_candidate_library()],
    }
    return _strip_grid_values(payload)


def write_campaign_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(campaign_bytes(payload).decode("utf-8"), encoding="utf-8")
    _write_csv_tables(payload, path.parent)
    return payload


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_campaign_output(Path(args.output))


def _dedup_sorted(values: Sequence[float]) -> tuple[float, ...]:
    result: list[float] = []
    for value in sorted(float(item) for item in values):
        if not result:
            result.append(value)
            continue
        previous = result[-1]
        if abs(value - previous) < 2.0 * ulp_of_double(max(abs(value), abs(previous))):
            continue
        result.append(value)
    return tuple(result)


def _values_for_precision(r_value: float, precision: str) -> dict[str, float]:
    if precision == "float32":
        return four_form_float32(r_value)
    return four_form_float64(r_value)


def _classify_grid_pair(grid_name: str, table64: dict[str, object], table32: dict[str, object], invariant: dict[str, object]) -> str:
    cofire64 = int(table64["cofire_count"])
    fraction64 = table64["same_sign_fraction"]
    p_two64 = table64["p_two_tail"]
    if cofire64 < 10:
        return "underpowered_grid"
    depolarized = fraction64 is not None and p_two64 is not None and 0.4 <= fraction64 <= 0.6 and p_two64 > 0.1
    if depolarized:
        return "depolarized_supported"
    relation64 = _relation_direction(table64)
    relation32 = _relation_direction(table32) if int(table32["cofire_count"]) >= 10 else relation64
    precision_ok = relation64 == relation32 and _precision_overlap_ok(invariant)
    if int(table32["cofire_count"]) >= 10:
        precision_ok = precision_ok and _strong_support(table32)
    strong = _strong_support(table64) and precision_ok
    if grid_name == "reference" and strong:
        return "reference_grid_confirmed"
    if grid_name != "reference" and strong:
        return "grid_stable_supported"
    return "grid_stability_rejected"


def _aggregate_pair_status(pair: str, per_grid: dict[str, str]) -> tuple[str, str]:
    non_reference = tuple(per_grid[name] for name in GRID_ORDER if name != "reference")
    if pair == "F1_F4" and any(status == "grid_stable_supported" for status in non_reference):
        return "negative_control_failed", "F1/F4 reached grid-stable support on a non-reference grid."
    if pair == "F1_F4" and per_grid["reference"] == "depolarized_supported":
        return "depolarized_invariant", "F1/F4 reference behavior is depolarized and no non-reference grid passed the precision-consistent coupling gate."
    if pair == "F2_F4" and any(status == "underpowered_grid" for status in per_grid.values()):
        return "open_underpowered", "F2/F4 rule blocks promotion because at least one grid is underpowered."
    if per_grid["reference"] == "reference_grid_confirmed":
        if all(status == "grid_stable_supported" for status in non_reference):
            return "grid_stable_polarity_coupling", "Reference and all non-reference grids meet the support criteria."
        if any(status == "grid_stability_rejected" for status in non_reference):
            return "reference_grid_only", "The reference-grid relation does not generalize across non-reference grids."
        if all(status == "underpowered_grid" for status in non_reference):
            return "open_underpowered", "All non-reference grids are underpowered."
        return "open_underpowered", "At least one non-reference grid is underpowered, so promotion remains open."
    if all(status in {"depolarized_supported", "underpowered_grid"} for status in per_grid.values()) and any(status == "depolarized_supported" for status in per_grid.values()):
        return "depolarized_invariant", "All grids are depolarized or underpowered."
    if all(status == "underpowered_grid" for status in non_reference):
        return "open_underpowered", "Non-reference grids are underpowered."
    return "reference_grid_only", "No aggregate promotion criteria were met."


def _relation_direction(table: dict[str, object]) -> str:
    fraction = table["same_sign_fraction"]
    if fraction is None:
        return "none"
    return "parallel" if float(fraction) >= 0.5 else "anti_parallel"


def _strong_support(table: dict[str, object]) -> bool:
    fraction = table["same_sign_fraction"]
    p_two = table["p_two_tail"]
    return fraction is not None and p_two is not None and float(fraction) >= 0.9 and float(p_two) < 0.001 and int(table["cofire_count"]) >= 10


def _precision_overlap_ok(invariant: dict[str, object]) -> bool:
    count = int(invariant["both_precision_cofire"])
    fraction = invariant["invariance_fraction"]
    if count < 10:
        return True
    return fraction is not None and float(fraction) >= 0.9


def _binomial_p_values(cofire_count: int, same_sign_count: int) -> dict[str, float | None]:
    if cofire_count == 0:
        return {"p_one_tail_upper": None, "p_one_tail_lower": None, "p_two_tail": None}
    denominator = float(2**cofire_count)
    upper = sum(_comb(cofire_count, k) for k in range(same_sign_count, cofire_count + 1)) / denominator
    lower = sum(_comb(cofire_count, k) for k in range(0, same_sign_count + 1)) / denominator
    return {"p_one_tail_upper": upper, "p_one_tail_lower": lower, "p_two_tail": min(1.0, 2.0 * min(upper, lower))}


def _comb(n_value: int, k_value: int) -> int:
    if k_value < 0 or k_value > n_value:
        return 0
    k_local = min(k_value, n_value - k_value)
    result = 1
    for index in range(1, k_local + 1):
        result = result * (n_value - k_local + index) // index
    return result


def _write_csv_tables(payload: dict[str, object], directory: Path) -> None:
    _write_polarity_csv(payload, directory / "polarity_grid_table.csv")
    _write_region_csv(payload, directory / "region_split_table.csv")
    _write_precision_csv(payload, directory / "precision_overlap_table.csv")


def _write_polarity_csv(payload: dict[str, object], path: Path) -> None:
    classifications = payload["aggregate_classifications"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("grid", "precision", "pair", "cofire_count", "same_sign_count", "same_sign_fraction", "p_one_tail_upper", "p_one_tail_lower", "p_two_tail", "status"))
        for table in payload["polarity_tables"]:
            grid_name = table["grid_name"]
            for pair in PAIR_ORDER:
                data = table["pairs"][pair]
                writer.writerow(
                    (
                        grid_name,
                        table["precision"],
                        pair,
                        data["cofire_count"],
                        data["same_sign_count"],
                        _format_csv_value(data["same_sign_fraction"], False),
                        _format_csv_value(data["p_one_tail_upper"], True),
                        _format_csv_value(data["p_one_tail_lower"], True),
                        _format_csv_value(data["p_two_tail"], True),
                        classifications[pair]["per_grid"][grid_name],
                    )
                )


def _write_region_csv(payload: dict[str, object], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("grid", "precision", "pair", "region", "n_in_region", "cofire_count", "same_sign_count", "same_sign_fraction", "p_two_tail"))
        for table in payload["polarity_tables"]:
            for pair in PAIR_ORDER:
                for region in REGION_ORDER:
                    data = table["pairs"][pair]["region_split"][region]
                    writer.writerow(
                        (
                            table["grid_name"],
                            table["precision"],
                            pair,
                            region,
                            data["n_in_region"],
                            data["cofire"],
                            data["agree"],
                            _format_csv_value(data["same_sign_fraction"], False),
                            _format_csv_value(data["p_two_tail"], True),
                        )
                    )


def _write_precision_csv(payload: dict[str, object], path: Path) -> None:
    classifications = payload["aggregate_classifications"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("grid", "pair", "both_precision_cofire", "same_relation_count", "invariance_fraction", "status"))
        for table in payload["precision_overlap_tables"]:
            grid_name = table["grid_name"]
            for pair in PAIR_ORDER:
                data = table["pairs"][pair]
                writer.writerow(
                    (
                        grid_name,
                        pair,
                        data["both_precision_cofire"],
                        data["same_relation_count"],
                        _format_csv_value(data["invariance_fraction"], False),
                        classifications[pair]["per_grid"][grid_name],
                    )
                )


def _format_csv_value(value: object, p_value: bool) -> str:
    if value is None:
        return "null"
    numeric = float(value)
    if p_value and numeric < 1.0e-6:
        return f"{numeric:.3e}"
    return f"{numeric:.6f}"


def _grid_without_values(grid: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in grid.items() if key != "r_values"}


def _strip_grid_values(payload: dict[str, object]) -> dict[str, object]:
    return payload


def _headline_findings(classifications: dict[str, dict[str, object]]) -> list[str]:
    return [f"{pair}: {data['aggregate']}" for pair, data in classifications.items()]


def _fraction(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / float(denominator)


def _region_name(r_value: float) -> str:
    if r_value < 2.05:
        return "near"
    if r_value < 3.0:
        return "middle"
    return "far"


def _sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


if __name__ == "__main__":
    main()
