from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import four_form_float64 as schwarzschild_float64
from .schwarzschild_four_form import sweep_r_values
from .sr_four_form import beta_grid, four_form_float64 as sr_float64
from .sr_lattice_campaign import DEFAULT_OUTPUT as SR_LATTICE_OUTPUT
from .sr_lattice_campaign import write_campaign_output as write_sr_lattice_output
from .sr_polarity_grid_stability import DEFAULT_OUTPUT as SR_POLARITY_OUTPUT
from .sr_polarity_grid_stability import PAIR_ORDER
from .sr_polarity_grid_stability import write_campaign_output as write_sr_polarity_output


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task027_sr_four_form_cross_fixture"
DEFAULT_OUTPUT = REPORT_DIR / "cross_fixture_comparison.json"
SCHWARZSCHILD_POLARITY_OUTPUT = ROOT / "Build_Docs" / "Reports" / "task026c_prime_polarity_grid_stability" / "campaign_output.json"
SCHWARZSCHILD_LATTICE_OUTPUT = ROOT / "Build_Docs" / "Reports" / "task026_lattice_anomaly_investigation" / "campaign_output.json"
PER_PAIR_CSV = REPORT_DIR / "cross_fixture_per_pair_table.csv"
LATTICE_CSV = REPORT_DIR / "cross_fixture_lattice_grain_table.csv"
STERBENZ_CSV = REPORT_DIR / "cross_fixture_sterbenz_boundary_table.csv"


def load_fixture_results(fixture: str) -> dict[str, object]:
    if fixture == "schwarzschild":
        return _read_json(SCHWARZSCHILD_POLARITY_OUTPUT)
    if fixture == "sr":
        if not SR_POLARITY_OUTPUT.is_file():
            write_sr_polarity_output(SR_POLARITY_OUTPUT)
        return _read_json(SR_POLARITY_OUTPUT)
    raise ValueError(f"unknown fixture: {fixture}")


def compare_fixtures() -> dict[str, object]:
    schwarzschild_polarity = load_fixture_results("schwarzschild")
    sr_polarity = load_fixture_results("sr")
    if not SR_LATTICE_OUTPUT.is_file():
        write_sr_lattice_output(SR_LATTICE_OUTPUT)
    schwarzschild_lattice = _read_json(SCHWARZSCHILD_LATTICE_OUTPUT)
    sr_lattice = _read_json(SR_LATTICE_OUTPUT)
    per_pair = _per_pair_aggregate_comparison(schwarzschild_polarity, sr_polarity)
    grid_precision = _per_grid_per_precision_comparison(schwarzschild_polarity, sr_polarity)
    lattice_grain = _lattice_grain_comparison(schwarzschild_lattice, sr_lattice)
    sterbenz = _sterbenz_boundary_comparison()
    headline = _headline(per_pair, lattice_grain, sterbenz)
    return {
        "campaign": "task027_cross_fixture_comparison",
        "per_pair_aggregate_comparison": per_pair,
        "per_grid_per_precision_comparison": grid_precision,
        "lattice_grain_comparison": lattice_grain,
        "sterbenz_boundary_comparison": sterbenz,
        "headline_finding": headline,
    }


def write_comparison_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = compare_fixtures()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(campaign_bytes(payload).decode("utf-8"), encoding="utf-8")
    _write_csvs(payload)
    return payload


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = compare_fixtures() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_comparison_output(Path(args.output))


def _per_pair_aggregate_comparison(schwarzschild: dict[str, object], sr: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for pair in PAIR_ORDER:
        schwarzschild_status = schwarzschild["aggregate_classifications"][pair]["aggregate"]
        sr_status = sr["aggregate_classifications"][pair]["aggregate"]
        rows.append(
            {
                "pair": pair,
                "schwarzschild_aggregate": schwarzschild_status,
                "sr_aggregate": sr_status,
                "same_aggregate": schwarzschild_status == sr_status,
            }
        )
    return rows


def _per_grid_per_precision_comparison(schwarzschild: dict[str, object], sr: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    schwarzschild_tables = {(table["grid_name"], table["precision"]): table for table in schwarzschild["polarity_tables"]}
    sr_tables = {(table["grid_name"], table["precision"]): table for table in sr["polarity_tables"]}
    for grid_name, precision in sorted(schwarzschild_tables):
        for pair in PAIR_ORDER:
            left = schwarzschild_tables[(grid_name, precision)]["pairs"][pair]
            right = sr_tables[(grid_name, precision)]["pairs"][pair]
            rows.append(
                {
                    "grid": grid_name,
                    "precision": precision,
                    "pair": pair,
                    "schwarzschild_cofire": left["cofire_count"],
                    "schwarzschild_same_fraction": left["same_sign_fraction"],
                    "sr_cofire": right["cofire_count"],
                    "sr_same_fraction": right["same_sign_fraction"],
                }
            )
    return rows


def _lattice_grain_comparison(schwarzschild: dict[str, object], sr: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for form_id in ("F1", "F2", "F3", "F4"):
        left = schwarzschild["submodules"]["A_lattice_structure"]["by_form"][form_id]["by_precision"]["float64"]
        right = sr["by_form"][form_id]["by_precision"]["float64"]
        rows.append(
            {
                "form": form_id,
                "precision": "float64",
                "schwarzschild_classification": left["candidate_classification"],
                "schwarzschild_nonzero": left["n_nonzero"],
                "schwarzschild_distinct_levels": left["n_distinct_levels"],
                "sr_classification": right["candidate_classification"],
                "sr_nonzero": right["n_nonzero"],
                "sr_distinct_levels": right["n_distinct_levels"],
                "sr_integer_residual_max": right["level_integer_residual_max"],
            }
        )
    return rows


def _sterbenz_boundary_comparison() -> list[dict[str, object]]:
    schwarzschild_values = sweep_r_values()
    schwarzschild_boundary = 4.0
    schwarzschild_below = tuple(value for value in schwarzschild_values if value < schwarzschild_boundary)
    schwarzschild_above = tuple(value for value in schwarzschild_values if value >= schwarzschild_boundary)
    sr_values = beta_grid()
    sr_boundary = 2.0 ** -0.5
    sr_below = tuple(value for value in sr_values if value <= sr_boundary)
    sr_above = tuple(value for value in sr_values if value > sr_boundary)
    rows = [
        _sterbenz_row("schwarzschild", "r", schwarzschild_boundary, schwarzschild_below, schwarzschild_above, lambda value: schwarzschild_float64(value)["F2"], "above_boundary_higher"),
        _sterbenz_row("sr", "beta", sr_boundary, sr_below, sr_above, lambda value: sr_float64(value)["F2"], "below_boundary_higher"),
    ]
    return rows


def _sterbenz_row(fixture: str, coordinate: str, boundary: float, below_values: tuple[float, ...], above_values: tuple[float, ...], evaluator, predicted_direction: str) -> dict[str, object]:
    below_count = sum(1 for value in below_values if evaluator(value) != 0.0)
    above_count = sum(1 for value in above_values if evaluator(value) != 0.0)
    below_density = below_count / float(len(below_values)) if below_values else 0.0
    above_density = above_count / float(len(above_values)) if above_values else 0.0
    if above_density > below_density:
        observed = "above_boundary_higher"
    elif below_density > above_density:
        observed = "below_boundary_higher"
    else:
        observed = "balanced"
    return {
        "fixture": fixture,
        "coordinate": coordinate,
        "boundary": boundary,
        "f2_count_below_boundary": below_count,
        "f2_count_above_boundary": above_count,
        "n_below_boundary": len(below_values),
        "n_above_boundary": len(above_values),
        "below_density": below_density,
        "above_density": above_density,
        "predicted_direction": predicted_direction,
        "observed_direction": observed,
        "supports_prediction": observed == predicted_direction,
    }


def _headline(per_pair: list[dict[str, object]], lattice: list[dict[str, object]], sterbenz: list[dict[str, object]]) -> str:
    pair_map = {row["pair"]: row for row in per_pair}
    lattice_map = {row["form"]: row for row in lattice}
    pair_match = (
        pair_map["F1_F2"]["sr_aggregate"] == "grid_stable_polarity_coupling"
        and pair_map["F1_F4"]["sr_aggregate"] == "depolarized_invariant"
        and pair_map["F2_F4"]["sr_aggregate"] != "grid_stable_polarity_coupling"
    )
    lattice_match = (
        lattice_map["F3"]["sr_nonzero"] == 0
        and lattice_map["F4"]["sr_distinct_levels"] >= 20
        and lattice_map["F2"]["sr_classification"] in {"lattice_integer", "non_integer_lattice"}
    )
    sterbenz_match = all(bool(row["supports_prediction"]) for row in sterbenz)
    if pair_match and lattice_match and sterbenz_match:
        return "chain_property_supported"
    if pair_map["F1_F2"]["sr_aggregate"] != "grid_stable_polarity_coupling":
        return "chain_property_rejected"
    return "chain_property_partial"


def _write_csvs(payload: dict[str, object]) -> None:
    with PER_PAIR_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("pair", "schwarzschild_aggregate", "sr_aggregate", "same_aggregate"))
        for row in payload["per_pair_aggregate_comparison"]:
            writer.writerow((row["pair"], row["schwarzschild_aggregate"], row["sr_aggregate"], row["same_aggregate"]))
    with LATTICE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("form", "precision", "schwarzschild_classification", "schwarzschild_nonzero", "schwarzschild_distinct_levels", "sr_classification", "sr_nonzero", "sr_distinct_levels", "sr_integer_residual_max"))
        for row in payload["lattice_grain_comparison"]:
            writer.writerow((row["form"], row["precision"], row["schwarzschild_classification"], row["schwarzschild_nonzero"], row["schwarzschild_distinct_levels"], row["sr_classification"], row["sr_nonzero"], row["sr_distinct_levels"], row["sr_integer_residual_max"]))
    with STERBENZ_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", "coordinate", "boundary", "f2_count_below_boundary", "f2_count_above_boundary", "below_density", "above_density", "predicted_direction", "observed_direction", "supports_prediction"))
        for row in payload["sterbenz_boundary_comparison"]:
            writer.writerow((row["fixture"], row["coordinate"], row["boundary"], row["f2_count_below_boundary"], row["f2_count_above_boundary"], row["below_density"], row["above_density"], row["predicted_direction"], row["observed_direction"], row["supports_prediction"]))


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
