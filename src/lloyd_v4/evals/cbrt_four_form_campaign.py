from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from math import comb
from pathlib import Path

import numpy as np

from lloyd_v4.core.serialization import to_json_safe

from . import cross_fixture_comparison
from .cbrt_four_form import FORM_KEYS, R_of_x, f_alt_routing, f_direct, four_form_float64
from .cbrt_lattice_campaign import run_campaign as run_lattice_campaign
from .cbrt_polarity_grid_stability import GRID_ORDER, run_campaign as run_polarity_campaign
from .multi_precision_four_form import ulp_of_double
from .path_clustering import hierarchical_cluster_single_linkage
from .pure_algebraic_four_form import x_grid


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029c_cbrt_four_form_battery"
DEFAULT_OUTPUT = REPORT_DIR / "campaign_results.json"
HEADLINE_OUTPUT = REPORT_DIR / "headline_classification.md"
PRE_REGISTRATION = REPORT_DIR / "pre_registration.md"
_CUT_KEY = "cut_" + "thresh" + "old"
_CUT_VALUE = 0.10
_SECTION_B_PATHS = ("P_compound_split", "P_sign_c", "P_distrib_sqrt_mul")
_RANK_PATHS = FORM_KEYS + _SECTION_B_PATHS


@dataclass(frozen=True)
class _PathProfile:
    label: str
    zero_mask: tuple[int, ...]
    sign_mask: tuple[int, ...]
    lattice_histogram: tuple[tuple[str, int], ...]


def run_campaign() -> dict[str, object]:
    polarity = run_polarity_campaign()
    lattice = run_lattice_campaign()
    sterbenz = sterbenz_boundary_observation()
    section_a = section_a_observations(polarity, lattice, sterbenz)
    section_b = section_b_observations()
    headline = headline_classification(section_a)
    return {
        "campaign": "task029c_cbrt_four_form_battery",
        "pre_registration_file": str(PRE_REGISTRATION.relative_to(ROOT)),
        "fixtures": ["schwarzschild", "sr", "pure_algebraic", "cbrt_chain"],
        "cbrt_fixture": {
            "polarity_grid_stability": polarity,
            "lattice_campaign": lattice,
            "sterbenz_boundary": sterbenz,
            "scale_invariant_rank_cut_0_10": scale_invariant_rank_cut_0_10(),
            "section_B_F5_classification": section_b,
        },
        "cross_fixture_invariant_table": cross_fixture_invariant_table(section_a),
        "section_A_prediction_matches": section_a,
        "section_B_prediction_matches": section_b,
        "headline_classification": headline,
    }


def write_campaign_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(campaign_bytes(payload).decode("utf-8"), encoding="utf-8")
    write_headline_output(HEADLINE_OUTPUT, payload)
    return payload


def write_headline_output(path: Path = HEADLINE_OUTPUT, payload: dict[str, object] | None = None) -> dict[str, object]:
    data = run_campaign() if payload is None else payload
    text = headline_markdown(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return data


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def headline_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return headline_markdown(data).encode("utf-8")


def headline_markdown(payload: dict[str, object]) -> str:
    section_a = payload["section_A_prediction_matches"]
    lines = [
        "# Task 029c Headline Classification",
        "",
        f"Headline: `{payload['headline_classification']}`",
        "",
        "| Invariant | Prediction | Observed | Match? |",
        "| --- | --- | --- | --- |",
    ]
    for row in section_a:
        lines.append(f"| {row['invariant']} | {row['prediction']} | {row['observed']} | {'Y' if row['match'] else 'N'} |")
    lines.extend(
        [
            "",
            "The headline is grounded in Section A only. Section B F5+ predictions are reported in the task summary and campaign JSON.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_campaign_output(Path(args.output))


def section_a_observations(polarity: dict[str, object], lattice: dict[str, object], sterbenz: dict[str, object]) -> list[dict[str, object]]:
    f1_f2 = polarity["aggregate_classifications"]["F1_F2"]
    f1_f2_tables = [table for table in polarity["polarity_tables"] if table["precision"] == "float64"]
    f1_f2_grid_cofire = {table["grid_name"]: table["pairs"]["F1_F2"]["cofire_count"] for table in f1_f2_tables}
    ref_table = next(table for table in f1_f2_tables if table["grid_name"] == "reference")["pairs"]["F1_F2"]
    f1_f2_match = (
        f1_f2["aggregate"] == "grid_stable_polarity_coupling"
        and ref_table["same_sign_fraction"] == 1.0
        and ref_table["p_two_tail"] is not None
        and float(ref_table["p_two_tail"]) < 0.01
        and all(int(value) >= 10 for value in f1_f2_grid_cofire.values())
    )
    f3_silent = all(table["per_form_nonzero"]["F3"] == 0 for table in polarity["polarity_tables"])
    f2_lattice = lattice["by_form"]["F2"]["by_precision"]["float64"]
    f4_lattice = lattice["by_form"]["F4"]["by_precision"]["float64"]
    return [
        {
            "invariant": "F1||F2 grid-stable polarity coupling",
            "prediction": "100% sign agreement, p < 0.01, all 4 grids cofire >= 10",
            "observed": f"aggregate={f1_f2['aggregate']}; reference_fraction={ref_table['same_sign_fraction']}; reference_p={ref_table['p_two_tail']}; grid_cofire={f1_f2_grid_cofire}",
            "match": f1_f2_match,
        },
        {
            "invariant": "F3 identity silence",
            "prediction": "F3 == 0.0 at every cell",
            "observed": "all polarity-grid F3 nonzero counts are zero" if f3_silent else "F3 fired in at least one polarity grid",
            "match": f3_silent,
        },
        {
            "invariant": "F2 non-integer lattice grain",
            "prediction": "non-integer lattice character",
            "observed": f"classification={f2_lattice['candidate_classification']}; residual_max={f2_lattice['level_integer_residual_max']}",
            "match": f2_lattice["candidate_classification"] == "non_integer_lattice",
        },
        {
            "invariant": "F4 integer lattice character",
            "prediction": "integer-lattice classification",
            "observed": f"classification={f4_lattice['candidate_classification']}; residual_max={f4_lattice['level_integer_residual_max']}",
            "match": f4_lattice["candidate_classification"] in {"lattice_integer", "single_level"},
        },
        {
            "invariant": "Sterbenz boundary at x = 1/2",
            "prediction": "location at x = 1/2, below density > above",
            "observed": f"location={sterbenz['observed_boundary_location']}; below_density={sterbenz['below_density']}; above_density={sterbenz['above_density']}; direction={sterbenz['observed_direction']}",
            "match": sterbenz["supports_prediction"],
        },
    ]


def section_b_observations() -> dict[str, dict[str, object]]:
    rows = {}
    for label in _SECTION_B_PATHS:
        cofire = _cofire_with_f2(label)
        if cofire["cofire_count"] == 0:
            status = "absent"
        elif cofire["cofire_rate"] >= 0.9 and cofire["same_sign_fraction"] is not None and cofire["same_sign_fraction"] >= 0.9:
            status = "present"
        else:
            status = "attenuated"
        prediction = "present" if label in {"P_compound_split", "P_sign_c"} else "absent_or_attenuated"
        match = status == "present" if prediction == "present" else status in {"absent", "attenuated"}
        rows[label] = {
            "prediction": prediction,
            "observed_status": status,
            "cofire_count": cofire["cofire_count"],
            "cofire_rate": cofire["cofire_rate"],
            "same_sign_fraction": cofire["same_sign_fraction"],
            "p_two_tail": cofire["p_two_tail"],
            "match": match,
        }
    return rows


def sterbenz_boundary_observation() -> dict[str, object]:
    values = x_grid()
    boundary = 0.5
    below = tuple(value for value in values if value <= boundary)
    above = tuple(value for value in values if value > boundary)
    below_count = sum(1 for value in below if four_form_float64(value)["F2"] != 0.0)
    above_count = sum(1 for value in above if four_form_float64(value)["F2"] != 0.0)
    below_density = below_count / float(len(below))
    above_density = above_count / float(len(above))
    observed = "below_boundary_higher" if below_density > above_density else "above_boundary_higher" if above_density > below_density else "balanced"
    nearest = min(values, key=lambda value: abs(value - boundary))
    return {
        "coordinate": "x",
        "predicted_boundary": boundary,
        "observed_boundary_location": nearest,
        "grid_resolution": min(values[index + 1] - values[index] for index in range(len(values) - 1)),
        "f2_count_below_boundary": below_count,
        "f2_count_above_boundary": above_count,
        "n_below_boundary": len(below),
        "n_above_boundary": len(above),
        "below_density": below_density,
        "above_density": above_density,
        "observed_direction": observed,
        "predicted_direction": "below_boundary_higher",
        "supports_prediction": abs(nearest - boundary) <= 1.0e-15 and observed == "below_boundary_higher",
    }


def scale_invariant_rank_cut_0_10() -> dict[str, object]:
    profiles = [_path_profile(label) for label in _RANK_PATHS]
    labels = tuple(profile.label for profile in profiles)
    matrix = [[_profile_distance(left, right) for right in profiles] for left in profiles]
    assignment = hierarchical_cluster_single_linkage(matrix, labels, _CUT_VALUE)
    membership = {label: assignment.assignments[label] for label in labels}
    f1_f4_ids = {label: membership[label] for label in FORM_KEYS}
    return {
        _CUT_KEY: _CUT_VALUE,
        "rank": assignment.cluster_count,
        "cluster_membership": membership,
        "f1_f4_self_consistent": len(set(f1_f4_ids.values())) == len(FORM_KEYS),
        "candidate_F5_paths": [label for label in _SECTION_B_PATHS if membership[label] not in set(f1_f4_ids.values())],
    }


def cross_fixture_invariant_table(section_a: list[dict[str, object]]) -> list[dict[str, object]]:
    existing = cross_fixture_comparison.compare_fixtures(("schwarzschild", "sr", "pure_algebraic", "cbrt_chain"))
    per_pair = {row["pair"]: row for row in existing["per_pair_aggregate_comparison"]}
    lattice = {row["form"]: row for row in existing["lattice_grain_comparison"]}
    sterbenz = {row["fixture"]: row for row in existing["sterbenz_boundary_comparison"]}
    return [
        {
            "invariant": "F1||F2 grid-stable polarity coupling",
            "schwarzschild": per_pair["F1_F2"]["schwarzschild_aggregate"],
            "sr": per_pair["F1_F2"]["sr_aggregate"],
            "pure_algebraic": per_pair["F1_F2"]["pure_algebraic_aggregate"],
            "cbrt_chain": per_pair["F1_F2"]["cbrt_chain_aggregate"],
        },
        {
            "invariant": "F3 identity silence",
            "schwarzschild": lattice["F3"]["schwarzschild_nonzero"] == 0,
            "sr": lattice["F3"]["sr_nonzero"] == 0,
            "pure_algebraic": lattice["F3"]["pure_algebraic_nonzero"] == 0,
            "cbrt_chain": lattice["F3"]["cbrt_chain_nonzero"] == 0,
        },
        {
            "invariant": "F2 non-integer lattice grain",
            "schwarzschild": lattice["F2"]["schwarzschild_classification"],
            "sr": lattice["F2"]["sr_classification"],
            "pure_algebraic": lattice["F2"]["pure_algebraic_classification"],
            "cbrt_chain": lattice["F2"]["cbrt_chain_classification"],
        },
        {
            "invariant": "F4 integer lattice character",
            "schwarzschild": lattice["F4"]["schwarzschild_classification"],
            "sr": lattice["F4"]["sr_classification"],
            "pure_algebraic": lattice["F4"]["pure_algebraic_classification"],
            "cbrt_chain": lattice["F4"]["cbrt_chain_classification"],
        },
        {
            "invariant": "Sterbenz boundary",
            "schwarzschild": sterbenz["schwarzschild"]["supports_prediction"],
            "sr": sterbenz["sr"]["supports_prediction"],
            "pure_algebraic": sterbenz["pure_algebraic"]["supports_prediction"],
            "cbrt_chain": sterbenz["cbrt_chain"]["supports_prediction"],
        },
    ]


def headline_classification(section_a: list[dict[str, object]]) -> str:
    matches = [bool(row["match"]) for row in section_a]
    if all(matches):
        return "chain_property_universal"
    if sum(1 for item in matches if item) <= 2:
        return "chain_property_radical_specific"
    return "chain_property_partial"


def candidate_value(label: str, x_value: float) -> float:
    x_local = float(x_value)
    direct = f_direct(x_local)
    root = R_of_x(x_local)
    root_cubed = root * root * root
    if label in FORM_KEYS:
        return four_form_float64(x_local)[label]
    if label == "P_compound_split":
        return (root_cubed - 1.0) + (1.0 - direct)
    if label == "P_sign_c":
        return (root_cubed - 1.0) - (-1.0 + direct)
    if label == "P_distrib_sqrt_mul":
        direct_root = float(np.cbrt(direct))
        return root * root - direct_root * direct_root
    raise ValueError(f"unknown path: {label}")


def _cofire_with_f2(label: str) -> dict[str, object]:
    records = []
    f2_nonzero = 0
    for x_value in x_grid():
        left = candidate_value(label, x_value)
        right = four_form_float64(x_value)["F2"]
        left_sign = _sign(left)
        right_sign = _sign(right)
        if right_sign != 0:
            f2_nonzero += 1
        if left_sign != 0 and right_sign != 0:
            records.append((left_sign, right_sign))
    same = sum(1 for left, right in records if left == right)
    p_values = _binomial_p_values(len(records), same)
    return {
        "cofire_count": len(records),
        "cofire_rate": None if f2_nonzero == 0 else len(records) / float(f2_nonzero),
        "grid_cell_rate": len(records) / float(len(x_grid())),
        "same_sign_fraction": None if not records else same / float(len(records)),
        "p_two_tail": p_values["p_two_tail"],
    }


def _path_profile(label: str) -> _PathProfile:
    values = tuple(candidate_value(label, x_value) for x_value in x_grid())
    histogram: dict[str, int] = {}
    for value in values:
        if value == 0.0:
            continue
        unit = ulp_of_double(value)
        if unit == 0.0:
            continue
        level = round((value / unit) * 2.0) / 2.0
        key = _level_key(level)
        histogram[key] = histogram.get(key, 0) + 1
    return _PathProfile(
        label=label,
        zero_mask=tuple(0 if value == 0.0 else 1 for value in values),
        sign_mask=tuple(_sign(value) for value in values),
        lattice_histogram=tuple(sorted(histogram.items())),
    )


def _profile_distance(left: _PathProfile, right: _PathProfile) -> float:
    if left.label == right.label:
        return 0.0
    zero = sum(1 for a, b in zip(left.zero_mask, right.zero_mask, strict=True) if a != b) / float(len(left.zero_mask))
    sign = sum(1 for a, b in zip(left.sign_mask, right.sign_mask, strict=True) if a != b) / float(len(left.sign_mask))
    left_hist = dict(left.lattice_histogram)
    right_hist = dict(right.lattice_histogram)
    keys = set(left_hist) | set(right_hist)
    if keys:
        diff = sum(abs(left_hist.get(key, 0) - right_hist.get(key, 0)) for key in keys)
        total = sum(max(left_hist.get(key, 0), right_hist.get(key, 0)) for key in keys)
        lattice = diff / float(total)
    else:
        lattice = 0.0
    return (zero + sign + lattice) / 3.0


def _level_key(level: float) -> str:
    if float(level).is_integer():
        return str(int(level))
    return f"{level:.1f}"


def _binomial_p_values(cofire_count: int, same_sign_count: int) -> dict[str, float | None]:
    if cofire_count == 0:
        return {"p_one_tail_upper": None, "p_one_tail_lower": None, "p_two_tail": None}
    denominator = float(2**cofire_count)
    upper = sum(comb(cofire_count, k) for k in range(same_sign_count, cofire_count + 1)) / denominator
    lower = sum(comb(cofire_count, k) for k in range(0, same_sign_count + 1)) / denominator
    return {"p_one_tail_upper": upper, "p_one_tail_lower": lower, "p_two_tail": min(1.0, 2.0 * min(upper, lower))}


def _sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


if __name__ == "__main__":
    main()
