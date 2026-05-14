from __future__ import annotations

import argparse
import json
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .pure_algebraic_four_form import x_grid
from .pure_algebraic_quartic_four_form import four_form_float64, quartic_four_form_battery
from .pure_algebraic_quartic_lattice_campaign import run_campaign as run_lattice_campaign
from .pure_algebraic_quartic_polarity_grid_stability import run_campaign as run_polarity_campaign


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task032_quartic_lattice_grain_discrimination"
DEFAULT_OUTPUT = REPORT_DIR / "campaign_results.json"
HEADLINE_OUTPUT = REPORT_DIR / "headline_classification.md"
BATTERY_OUTPUT = REPORT_DIR / "quartic_four_form_battery.json"
LATTICE_OUTPUT = REPORT_DIR / "quartic_lattice_campaign_output.json"
PRE_REGISTRATION = REPORT_DIR / "pre_registration.md"
ADMISSIBLE_F2_GRAINS = (0.0, 0.125, 0.25, 0.5)


def run_campaign() -> dict[str, object]:
    battery = quartic_four_form_battery()
    lattice = run_lattice_campaign()
    polarity = run_polarity_campaign()
    sterbenz = sterbenz_boundary_observation()
    discrimination = hypothesis_discrimination(lattice)
    return {
        "campaign": "task032_quartic_lattice_grain_discrimination",
        "pre_registration_file": str(PRE_REGISTRATION.relative_to(ROOT)),
        "fixture": "quartic_identity_operand",
        "fixture_construction": {
            "operand": "identity",
            "radical_degree": 4,
            "radical_implementation": "numpy.sqrt(numpy.sqrt(1 - x))",
            "root_rounding_events": 2,
            "grid": "pure_algebraic_four_form.x_grid",
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
    BATTERY_OUTPUT.write_text((json.dumps(to_json_safe(payload["four_form_battery"]), sort_keys=True, indent=2, allow_nan=False) + "\n"), encoding="utf-8")
    LATTICE_OUTPUT.write_text((json.dumps(to_json_safe(payload["lattice_campaign"]), sort_keys=True, indent=2, allow_nan=False) + "\n"), encoding="utf-8")
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
        "# Task 032 Headline Classification",
        "",
        f"Headline: `{payload['headline_classification']}`",
        "",
        "| Hypothesis | Predicted | Observed | Match? |",
        "| --- | ---: | ---: | --- |",
        f"| H1: grain = 2^(1-n) | 0.125 | {observed} | {'Y' if row['h1_match'] else 'N'} |",
        f"| H2: operand-transformation law | 0.25 | {observed} | {'Y' if row['h2_match'] else 'N'} |",
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
        "h1_prediction": 0.125,
        "h2_prediction": 0.25,
        "h1_match": observed == 0.125,
        "h2_match": observed == 0.25,
        "headline_classification": headline,
    }


def headline_for_grain(observed: float) -> str:
    if observed == 0.125:
        return "lattice_grain_h1_quartic"
    if observed == 0.25:
        return "lattice_grain_h2_operand"
    return "lattice_grain_indeterminate"


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
        "supports_prediction": nearest == boundary and observed == "below_boundary_higher",
    }


if __name__ == "__main__":
    main()
