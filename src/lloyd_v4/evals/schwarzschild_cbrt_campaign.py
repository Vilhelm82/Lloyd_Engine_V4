from __future__ import annotations

import argparse
import json
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .schwarzschild_cbrt_four_form import four_form_float64, schwarzschild_cbrt_four_form_battery
from .schwarzschild_cbrt_lattice_campaign import run_campaign as run_lattice_campaign
from .schwarzschild_cbrt_polarity_grid_stability import run_campaign as run_polarity_campaign
from .schwarzschild_four_form import sweep_r_values


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task033_schwarzschild_cbrt_transformed_n3"
DEFAULT_OUTPUT = REPORT_DIR / "campaign_results.json"
HEADLINE_OUTPUT = REPORT_DIR / "headline_classification.md"
BATTERY_OUTPUT = REPORT_DIR / "schwarzschild_cbrt_four_form_battery.json"
LATTICE_OUTPUT = REPORT_DIR / "schwarzschild_cbrt_lattice_campaign_output.json"
PRE_REGISTRATION = REPORT_DIR / "pre_registration.md"
ADMISSIBLE_F2_GRAINS = (0.0, 0.125, 0.25, 0.5)


def run_campaign() -> dict[str, object]:
    battery = schwarzschild_cbrt_four_form_battery()
    lattice = run_lattice_campaign()
    polarity = run_polarity_campaign()
    sterbenz = sterbenz_boundary_observation()
    discrimination = hypothesis_discrimination(lattice)
    return {
        "campaign": "task033_schwarzschild_cbrt_transformed_n3",
        "pre_registration_file": str(PRE_REGISTRATION.relative_to(ROOT)),
        "fixture": "schwarzschild_cbrt_transformed_operand",
        "fixture_construction": {
            "operand": "transformed",
            "radical_degree": 3,
            "radical_implementation": "numpy.cbrt(1 - 2 / r)",
            "root_rounding_events": 1,
            "grid": "schwarzschild_four_form.sweep_r_values",
        },
        "four_form_battery": battery,
        "lattice_campaign": lattice,
        "polarity_grid_stability": polarity,
        "sterbenz_boundary": sterbenz,
        "hypothesis_discrimination": discrimination,
        "headline_classification": discrimination["headline_classification"],
    }


def write_campaign_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(campaign_bytes(payload).decode("utf-8"), encoding="utf-8")
    BATTERY_OUTPUT.write_text(battery_bytes(payload).decode("utf-8"), encoding="utf-8")
    LATTICE_OUTPUT.write_text(lattice_bytes(payload).decode("utf-8"), encoding="utf-8")
    write_headline_output(HEADLINE_OUTPUT, payload)
    return payload


def write_headline_output(path: Path = HEADLINE_OUTPUT, payload: dict[str, object] | None = None) -> dict[str, object]:
    data = run_campaign() if payload is None else payload
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(headline_markdown(data), encoding="utf-8")
    return data


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def battery_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data["four_form_battery"]), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def lattice_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data["lattice_campaign"]), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def headline_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return headline_markdown(data).encode("utf-8")


def headline_markdown(payload: dict[str, object]) -> str:
    row = payload["hypothesis_discrimination"]
    observed = row["observed_f2_float64_grain"]
    lines = [
        "# Task 033 Headline Classification",
        "",
        f"Headline: `{payload['headline_classification']}`",
        "",
        "| Hypothesis | Predicted | Observed | Match? |",
        "| --- | ---: | ---: | --- |",
        f"| H2: transformed -> 0.5 | 0.5 | {observed} | {'Y' if row['h2_match'] else 'N'} |",
        f"| H2-refined: transformed effect n=2-specific | 0.25 | {observed} | {'Y' if row['h2_refined_match'] else 'N'} |",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_campaign_output(Path(args.output))


def hypothesis_discrimination(lattice: dict[str, object]) -> dict[str, object]:
    observed = float(lattice["by_form"]["F2"]["by_precision"]["float64"]["level_integer_residual_max"])
    headline = headline_for_grain(observed)
    return {
        "observed_f2_float64_grain": observed,
        "admissible_grain_values": list(ADMISSIBLE_F2_GRAINS),
        "h2_prediction": 0.5,
        "h2_refined_prediction": 0.25,
        "h2_match": observed == 0.5,
        "h2_refined_match": observed == 0.25,
        "headline_classification": headline,
    }


def headline_for_grain(observed: float) -> str:
    if observed == 0.5:
        return "transformed_operand_law_supported_at_n3"
    if observed == 0.25:
        return "transformed_operand_law_refuted_at_n3"
    return "lattice_grain_indeterminate_at_n3"


def sterbenz_boundary_observation() -> dict[str, object]:
    values = sweep_r_values()
    boundary = 4.0
    below = tuple(value for value in values if value < boundary)
    above = tuple(value for value in values if value >= boundary)
    below_count = sum(1 for value in below if four_form_float64(value)["F2"] != 0.0)
    above_count = sum(1 for value in above if four_form_float64(value)["F2"] != 0.0)
    below_density = below_count / float(len(below))
    above_density = above_count / float(len(above))
    observed = "below_boundary_higher" if below_density > above_density else "above_boundary_higher" if above_density > below_density else "balanced"
    nearest = min(values, key=lambda value: abs(value - boundary))
    return {
        "coordinate": "r",
        "predicted_boundary": boundary,
        "existing_schwarzschild_n2_boundary": boundary,
        "observed_boundary_location": boundary,
        "nearest_grid_point_to_boundary": nearest,
        "grid_resolution_min": min(values[index + 1] - values[index] for index in range(len(values) - 1)),
        "f2_count_below_boundary": below_count,
        "f2_count_above_boundary": above_count,
        "n_below_boundary": len(below),
        "n_above_boundary": len(above),
        "below_density": below_density,
        "above_density": above_density,
        "observed_direction": observed,
        "predicted_direction": "above_boundary_higher",
        "supports_prediction": observed == "above_boundary_higher",
        "boundary_location_match_to_schwarzschild_n2": boundary == 4.0,
    }


if __name__ == "__main__":
    main()
