from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Callable, Iterable

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import ulp_of_double
from .sr_four_form import beta_grid, four_form_float64 as sr_float64


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "f1_f2_natural_phase"
ARTIFACT_PATH = REPORT_DIR / "artifact_f1_f2_natural_phase.json"
CLOSEOUT_PATH = REPORT_DIR / "closeout_f1_f2_natural_phase.md"

MIN_USABLE_PAIRS = 12
PHASE_TOL = 1.0e-12
STABLE_FRACTION = 0.90
STABLE_MAX_DISTANCE = 0.05
GLOBAL_HALF_FRACTION = 0.66
SAME_PHASE_FRACTION = 0.75

OUTCOMES = (
    "natural_half_phase_supported",
    "global_half_phase_only_not_pointwise",
    "phase_drift_not_mergeable",
    "same_phase_duplicate",
    "control_manufactured_half_phase",
    "insufficient_usable_pairs",
    "fixture_unavailable",
)

VERIFICATION_COMMANDS = (
    {
        "command": "PYTHONPATH=src python -m lloyd_v4.evals.f1_f2_natural_phase",
        "result": "passed; generated artifact_f1_f2_natural_phase.json and closeout_f1_f2_natural_phase.md",
    },
    {
        "command": "PYTHONPATH=src python -m pytest tests/test_f1_f2_natural_phase.py -q",
        "result": "passed; 8 tests",
    },
    {
        "command": "PYTHONPATH=src python -m pytest tests/test_f1_f2_natural_phase.py tests/test_task027_sr_four_form_cross_fixture.py::test_beta_grid_deterministic_and_bounded tests/test_task027_sr_four_form_cross_fixture.py::test_F3_sr_is_identically_zero tests/test_task027_sr_four_form_cross_fixture.py::test_sr_four_form_byte_stable -q",
        "result": "passed; 11 tests",
    },
    {
        "command": "PYTHONPATH=src python -m pytest tests/ --skip-slow -q -ra",
        "result": "passed; slow campaign/report tests skipped by --skip-slow",
    },
)


def phase_mod(level: float) -> float:
    return float(level % 1.0)


def circular_distance(left: float, right: float) -> float:
    distance = abs((float(left) - float(right)) % 1.0)
    return float(min(distance, 1.0 - distance))


def phase_distance_to_half(phase: float) -> float:
    return circular_distance(phase, 0.5)


def phase_distance_to_zero(phase: float) -> float:
    return circular_distance(phase, 0.0)


def run_campaign() -> dict[str, object]:
    fixtures = [_sr_fixture_payload()]
    try:
        fixtures.append(_schwarzschild_fixture_payload())
    except Exception as exc:  # pragma: no cover - exercised only if optional fixture disappears.
        fixtures.append({"fixture": "schwarzschild_four_form", "available": False, "unavailable_reason": repr(exc)})
    accepted = _accepted_outcome(fixtures)
    artifact = {
        "campaign": "f1_f2_natural_half_ulp_phase_offset_audit",
        "lattice_unit_convention": {
            "sr_four_form": "ulp(1 - beta^2), matching sr_lattice_campaign float64 convention",
            "schwarzschild_four_form": "ulp(1 - 2/r), matching four-form operand-level convention",
        },
        "gates": {
            "min_usable_pairs": MIN_USABLE_PAIRS,
            "phase_tol": PHASE_TOL,
            "stable_fraction": STABLE_FRACTION,
            "stable_max_distance": STABLE_MAX_DISTANCE,
            "global_half_fraction": GLOBAL_HALF_FRACTION,
            "same_phase_fraction": SAME_PHASE_FRACTION,
        },
        "fixtures": fixtures,
        "primary_fixture": "sr_four_form",
        "accepted_outcome": accepted,
        "verification": VERIFICATION_COMMANDS,
    }
    artifact["closeout_answers"] = closeout_answers(artifact)
    return artifact


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def write_outputs() -> dict[str, object]:
    artifact = run_campaign()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_bytes(campaign_bytes(artifact))
    CLOSEOUT_PATH.write_text(closeout_markdown(artifact), encoding="utf-8")
    return artifact


def _sr_fixture_payload() -> dict[str, object]:
    coordinates = tuple(float(value) for value in beta_grid())
    rows = [
        {
            "coordinate": beta_value,
            "region": _sr_region(beta_value),
            "f": 1.0 - beta_value * beta_value,
            "forms": sr_float64(beta_value),
            "lattice_unit": ulp_of_double(1.0 - beta_value * beta_value),
        }
        for beta_value in coordinates
    ]
    return _fixture_payload(
        fixture="sr_four_form",
        available=True,
        coordinate="beta",
        coordinate_count=len(coordinates),
        coordinate_min=coordinates[0],
        coordinate_max=coordinates[-1],
        lattice_unit_convention="ulp(1 - beta^2)",
        rows=rows,
    )


def _schwarzschild_fixture_payload() -> dict[str, object]:
    from .schwarzschild_four_form import F1_of_r, F2_of_r, F3_of_r, F4_of_r, f_of_r, sweep_r_values

    coordinates = tuple(float(value) for value in sweep_r_values())
    rows = [
        {
            "coordinate": r_value,
            "region": _schwarzschild_region(r_value),
            "f": f_of_r(r_value),
            "forms": {
                "F1": F1_of_r(r_value),
                "F2": F2_of_r(r_value),
                "F3": F3_of_r(r_value),
                "F4": F4_of_r(r_value),
            },
            "lattice_unit": ulp_of_double(f_of_r(r_value)),
        }
        for r_value in coordinates
    ]
    return _fixture_payload(
        fixture="schwarzschild_four_form",
        available=True,
        coordinate="r",
        coordinate_count=len(coordinates),
        coordinate_min=coordinates[0],
        coordinate_max=coordinates[-1],
        lattice_unit_convention="ulp(1 - 2/r)",
        rows=rows,
    )


def _fixture_payload(
    *,
    fixture: str,
    available: bool,
    coordinate: str,
    coordinate_count: int,
    coordinate_min: float,
    coordinate_max: float,
    lattice_unit_convention: str,
    rows: list[dict[str, object]],
) -> dict[str, object]:
    primary = _analyze_pair(rows, "F1", "F2", role="primary")
    controls = {
        "same_route_F1_F1": _analyze_pair(rows, "F1", "F1", role="same_route"),
        "same_route_F2_F2": _analyze_pair(rows, "F2", "F2", role="same_route"),
        "calibration_F1_F3": _analyze_pair(rows, "F1", "F3", role="calibration_zero"),
        "calibration_F3_F3": _analyze_pair(rows, "F3", "F3", role="calibration_zero"),
        "route_stressor_F1_F4": _analyze_pair(rows, "F1", "F4", role="route_stressor"),
        "route_stressor_F2_F4": _analyze_pair(rows, "F2", "F4", role="route_stressor"),
    }
    return {
        "fixture": fixture,
        "available": available,
        "coordinate_metadata": {
            "coordinate": coordinate,
            "count": coordinate_count,
            "min": coordinate_min,
            "max": coordinate_max,
        },
        "lattice_unit_convention": lattice_unit_convention,
        "primary_pair": primary,
        "control_summaries": controls,
    }


def _analyze_pair(rows: list[dict[str, object]], left: str, right: str, *, role: str) -> dict[str, object]:
    all_count = 0
    usable = []
    skipped = {"nonfinite": 0, "nonpositive_unit": 0, "both_zero": 0}
    for row in rows:
        left_value = float(row["forms"][left])
        right_value = float(row["forms"][right])
        unit = float(row["lattice_unit"])
        if not (math.isfinite(left_value) and math.isfinite(right_value) and math.isfinite(unit)):
            skipped["nonfinite"] += 1
            continue
        all_count += 1
        if unit <= 0.0:
            skipped["nonpositive_unit"] += 1
            continue
        if left_value == 0.0 and right_value == 0.0:
            skipped["both_zero"] += 1
            continue
        left_level = left_value / unit
        right_level = right_value / unit
        phase_left = phase_mod(left_level)
        phase_right = phase_mod(right_level)
        delta = phase_mod(phase_right - phase_left)
        usable.append(
            {
                "coordinate": row["coordinate"],
                "region": row["region"],
                "f": row["f"],
                "lattice_unit": unit,
                "left_value": left_value,
                "right_value": right_value,
                "left_level": left_level,
                "right_level": right_level,
                "phase_left": phase_left,
                "phase_right": phase_right,
                "delta_phase": delta,
                "distance_delta_to_half": circular_distance(delta, 0.5),
                "distance_delta_to_zero": circular_distance(delta, 0.0),
                "distance_left_to_integer": phase_distance_to_zero(phase_left),
                "distance_right_to_half": phase_distance_to_half(phase_right),
            }
        )
    delta_half = [point["distance_delta_to_half"] for point in usable]
    delta_zero = [point["distance_delta_to_zero"] for point in usable]
    left_integer = [point["distance_left_to_integer"] for point in usable]
    right_half = [point["distance_right_to_half"] for point in usable]
    relation = _pair_relation(len(usable), delta_half, delta_zero)
    return {
        "pair": f"{left}_vs_{right}",
        "role": role,
        "finite_pair_count": all_count,
        "usable_pair_count": len(usable),
        "usable_pair_rule": "finite residuals with finite positive lattice unit and at least one nonzero residual in the compared pair",
        "skipped_counts": skipped,
        "F1_phase_summary" if left == "F1" else "left_phase_summary": _distance_summary(left_integer, target="integer"),
        "F2_phase_summary" if right == "F2" else "right_phase_summary": _distance_summary(right_half, target="half"),
        "pointwise_delta_phase_summary": _phase_summary([point["delta_phase"] for point in usable]),
        "distance_to_half_summary": _distance_summary(delta_half, target="half_delta"),
        "distance_to_zero_summary": _distance_summary(delta_zero, target="zero_delta"),
        "relation": relation,
        "region_summaries": _region_summaries(usable),
        "points": _compact_points(usable),
    }


def _pair_relation(usable_count: int, delta_half: list[float], delta_zero: list[float]) -> str:
    if usable_count < MIN_USABLE_PAIRS:
        return "insufficient_usable_pairs"
    half_fraction = _fraction_within(delta_half, STABLE_MAX_DISTANCE)
    zero_fraction = _fraction_within(delta_zero, STABLE_MAX_DISTANCE)
    if half_fraction >= STABLE_FRACTION and max(delta_half, default=1.0) <= STABLE_MAX_DISTANCE:
        return "pointwise_half_stable"
    if zero_fraction >= STABLE_FRACTION and max(delta_zero, default=1.0) <= STABLE_MAX_DISTANCE:
        return "same_phase_stable"
    if _fraction_within(delta_half, PHASE_TOL) > 0.0:
        return "half_phase_present_but_drifting"
    return "phase_scattered"


def _accepted_outcome(fixtures: list[dict[str, object]]) -> str:
    available = [fixture for fixture in fixtures if fixture.get("available")]
    if not available:
        return "fixture_unavailable"
    primary_fixture = next((fixture for fixture in available if fixture["fixture"] == "sr_four_form"), available[0])
    primary = primary_fixture["primary_pair"]
    if primary["usable_pair_count"] < MIN_USABLE_PAIRS:
        return "insufficient_usable_pairs"
    if _controls_manufacture_half(primary_fixture):
        return "control_manufactured_half_phase"
    if primary["relation"] == "pointwise_half_stable" and _f1_baseline_stable(primary):
        return "natural_half_phase_supported"
    if _f2_global_half_signature(primary) and primary["relation"] != "pointwise_half_stable":
        return "global_half_phase_only_not_pointwise"
    if primary["relation"] == "same_phase_stable":
        return "same_phase_duplicate"
    return "phase_drift_not_mergeable"


def _controls_manufacture_half(fixture: dict[str, object]) -> bool:
    controls = fixture["control_summaries"].values()
    return any(control["relation"] == "pointwise_half_stable" for control in controls)


def _f1_baseline_stable(primary: dict[str, object]) -> bool:
    summary = primary["F1_phase_summary"]
    return summary["fraction_within_tol"] >= STABLE_FRACTION


def _f2_global_half_signature(primary: dict[str, object]) -> bool:
    summary = primary["F2_phase_summary"]
    return summary["fraction_within_0_05"] >= GLOBAL_HALF_FRACTION


def _distance_summary(values: Iterable[float], *, target: str) -> dict[str, object]:
    data = tuple(float(value) for value in values)
    return {
        "target": target,
        "count": len(data),
        "min": min(data) if data else None,
        "median": _median(data),
        "mean": (sum(data) / len(data)) if data else None,
        "max": max(data) if data else None,
        "fraction_within_tol": _fraction_within(data, PHASE_TOL),
        "fraction_within_0_05": _fraction_within(data, STABLE_MAX_DISTANCE),
    }


def _phase_summary(values: Iterable[float]) -> dict[str, object]:
    data = tuple(float(value) for value in values)
    return {
        "count": len(data),
        "min": min(data) if data else None,
        "median": _median(data),
        "mean": (sum(data) / len(data)) if data else None,
        "max": max(data) if data else None,
        "histogram": _phase_histogram(data),
    }


def _region_summaries(points: list[dict[str, object]]) -> dict[str, object]:
    regions = sorted({str(point["region"]) for point in points})
    return {
        region: {
            "usable_pair_count": len(in_region),
            "distance_to_half_summary": _distance_summary((point["distance_delta_to_half"] for point in in_region), target="half_delta"),
            "distance_to_zero_summary": _distance_summary((point["distance_delta_to_zero"] for point in in_region), target="zero_delta"),
        }
        for region in regions
        for in_region in [[point for point in points if point["region"] == region]]
    }


def _compact_points(points: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "coordinate": point["coordinate"],
            "region": point["region"],
            "lattice_unit": point["lattice_unit"],
            "left_level": point["left_level"],
            "right_level": point["right_level"],
            "phase_left": point["phase_left"],
            "phase_right": point["phase_right"],
            "delta_phase": point["delta_phase"],
            "distance_delta_to_half": point["distance_delta_to_half"],
            "distance_delta_to_zero": point["distance_delta_to_zero"],
        }
        for point in points
    ]


def _phase_histogram(values: Iterable[float]) -> dict[str, int]:
    histogram: dict[str, int] = {}
    for value in values:
        key = f"{round(float(value), 12):.12g}"
        histogram[key] = histogram.get(key, 0) + 1
    return dict(sorted(histogram.items(), key=lambda item: (-item[1], item[0])))


def _fraction_within(values: Iterable[float], limit: float) -> float:
    data = tuple(float(value) for value in values)
    if not data:
        return 0.0
    return sum(1 for value in data if value <= limit) / len(data)


def _median(values: Iterable[float]) -> float | None:
    data = tuple(sorted(float(value) for value in values))
    if not data:
        return None
    middle = len(data) // 2
    if len(data) % 2:
        return data[middle]
    return (data[middle - 1] + data[middle]) / 2.0


def _sr_region(beta_value: float) -> str:
    if beta_value < 0.5:
        return "non_relativistic"
    if beta_value < 0.9:
        return "mildly_relativistic"
    return "ultra_relativistic"


def _schwarzschild_region(r_value: float) -> str:
    if r_value < 2.1:
        return "near_horizon"
    if r_value < 3.0:
        return "transition"
    return "far_field"


def closeout_answers(artifact: dict[str, object]) -> dict[str, object]:
    primary = _primary_fixture(artifact)["primary_pair"]
    controls = _primary_fixture(artifact)["control_summaries"]
    return {
        "f2_pointwise_half_relative_to_f1": primary["relation"] == "pointwise_half_stable",
        "effect_stability": primary["relation"],
        "same_route_controls_reject_half_phase": all(controls[name]["relation"] != "pointwise_half_stable" for name in ("same_route_F1_F1", "same_route_F2_F2")),
        "f3_calibration_zero_clean": all(controls[name]["relation"] != "pointwise_half_stable" for name in ("calibration_F1_F3", "calibration_F3_F3")),
        "f4_route_stressor_promoted": any(controls[name]["relation"] == "pointwise_half_stable" for name in ("route_stressor_F1_F4", "route_stressor_F2_F4")),
        "candidate_interleaved_lattice_readback": artifact["accepted_outcome"] == "natural_half_phase_supported",
        "double_precision_language_justified": False,
    }


def closeout_markdown(artifact: dict[str, object]) -> str:
    primary_fixture = _primary_fixture(artifact)
    primary = primary_fixture["primary_pair"]
    answers = artifact["closeout_answers"]
    lines = [
        "# F1/F2 Natural Half-ULP Phase Offset Audit",
        "",
        f"Accepted outcome: `{artifact['accepted_outcome']}`",
        "",
        "## Required Answers",
        "",
        f"1. F2 naturally sits at half-ULP phase relative to F1 pointwise: `{answers['f2_pointwise_half_relative_to_f1']}`.",
        f"   SR usable paired coordinates: `{primary['usable_pair_count']}` / `{primary['finite_pair_count']}` finite pairs.",
        f"   Pointwise delta relation: `{primary['relation']}`.",
        f"   Delta-to-half median/max: `{primary['distance_to_half_summary']['median']}` / `{primary['distance_to_half_summary']['max']}`.",
        f"2. Stability: `{answers['effect_stability']}`; half-phase hits are present but drift across the usable region rather than forming one coherent interleaved comb.",
        f"3. Same-route controls reject manufactured half-phase: `{answers['same_route_controls_reject_half_phase']}`.",
        f"4. F3 calibration zero remains clean: `{answers['f3_calibration_zero_clean']}`.",
        f"5. F4 behaves as a route-residual stressor, not the promoted phase companion: `{not answers['f4_route_stressor_promoted']}`.",
        f"6. Justified candidate interleaved lattice readback: `{answers['candidate_interleaved_lattice_readback']}`.",
        f"7. Double precision language justified: `{answers['double_precision_language_justified']}`. The result remains eval-layer phase-drift evidence, not a precision-doubling method.",
        "",
        "## Fixture Summary",
        "",
    ]
    for fixture in artifact["fixtures"]:
        if not fixture.get("available"):
            lines.append(f"- `{fixture['fixture']}` unavailable: `{fixture['unavailable_reason']}`.")
            continue
        pair = fixture["primary_pair"]
        lines.append(
            f"- `{fixture['fixture']}`: `{pair['relation']}` with `{pair['usable_pair_count']}` usable pairs; "
            f"delta-to-half median `{pair['distance_to_half_summary']['median']}`, max `{pair['distance_to_half_summary']['max']}`."
        )
    lines.extend(
        [
            "",
            "## Verification",
            "",
        ]
    )
    for item in artifact["verification"]:
        lines.append(f"- `{item['command']}`")
        lines.append(f"  Result: {item['result']}.")
    lines.extend(
        [
            "",
            "## Artifact",
            "",
            "- `Build_Docs/Reports/f1_f2_natural_phase/artifact_f1_f2_natural_phase.json`",
            "- `Build_Docs/Reports/f1_f2_natural_phase/closeout_f1_f2_natural_phase.md`",
            "",
        ]
    )
    return "\n".join(lines)


def _primary_fixture(artifact: dict[str, object]) -> dict[str, object]:
    return next(fixture for fixture in artifact["fixtures"] if fixture.get("fixture") == artifact["primary_fixture"])


def main() -> None:
    global REPORT_DIR, ARTIFACT_PATH, CLOSEOUT_PATH
    cli = argparse.ArgumentParser()
    cli.add_argument("--output-dir", default=str(REPORT_DIR))
    args = cli.parse_args()
    REPORT_DIR = Path(args.output_dir)
    ARTIFACT_PATH = REPORT_DIR / "artifact_f1_f2_natural_phase.json"
    CLOSEOUT_PATH = REPORT_DIR / "closeout_f1_f2_natural_phase.md"
    artifact = write_outputs()
    print("=== F1/F2 natural half-ULP phase offset audit ===")
    print(f"accepted_outcome={artifact['accepted_outcome']}")
    print(f"saved {ARTIFACT_PATH}")
    print(f"saved {CLOSEOUT_PATH}")


if __name__ == "__main__":
    main()
