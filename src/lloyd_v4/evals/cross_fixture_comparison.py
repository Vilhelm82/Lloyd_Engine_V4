from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .cbrt_four_form import four_form_float64 as cbrt_float64
from .cbrt_lattice_campaign import DEFAULT_OUTPUT as CBRT_LATTICE_OUTPUT
from .cbrt_lattice_campaign import write_campaign_output as write_cbrt_lattice_output
from .cbrt_polarity_grid_stability import DEFAULT_OUTPUT as CBRT_POLARITY_OUTPUT
from .cbrt_polarity_grid_stability import write_campaign_output as write_cbrt_polarity_output
from .multi_precision_four_form import four_form_float64 as schwarzschild_float64
from .pure_algebraic_four_form import four_form_float64 as pure_float64
from .pure_algebraic_four_form import x_grid
from .pure_algebraic_lattice_campaign import DEFAULT_OUTPUT as PURE_LATTICE_OUTPUT
from .pure_algebraic_lattice_campaign import write_campaign_output as write_pure_lattice_output
from .pure_algebraic_polarity_grid_stability import DEFAULT_OUTPUT as PURE_POLARITY_OUTPUT
from .schwarzschild_four_form import sweep_r_values
from .sr_four_form import beta_grid
from .sr_four_form import four_form_float64 as sr_float64
from .sr_lattice_campaign import DEFAULT_OUTPUT as SR_LATTICE_OUTPUT
from .sr_lattice_campaign import write_campaign_output as write_sr_lattice_output
from .sr_polarity_grid_stability import DEFAULT_OUTPUT as SR_POLARITY_OUTPUT
from .sr_polarity_grid_stability import PAIR_ORDER
from .sr_polarity_grid_stability import write_campaign_output as write_sr_polarity_output


ROOT = Path(__file__).resolve().parents[3]
TASK028_REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task028_conditional_masks_joint_lattice_pure_algebraic"
DEFAULT_OUTPUT = TASK028_REPORT_DIR / "three_fixture_comparison.json"
SCHWARZSCHILD_POLARITY_OUTPUT = ROOT / "Build_Docs" / "Reports" / "task026c_prime_polarity_grid_stability" / "campaign_output.json"
SCHWARZSCHILD_LATTICE_OUTPUT = ROOT / "Build_Docs" / "Reports" / "task026_lattice_anomaly_investigation" / "campaign_output.json"
PER_PAIR_CSV = TASK028_REPORT_DIR / "three_fixture_per_pair_table.csv"
LATTICE_CSV = TASK028_REPORT_DIR / "three_fixture_lattice_grain_table.csv"
STERBENZ_CSV = TASK028_REPORT_DIR / "three_fixture_sterbenz_boundary_table.csv"


def load_fixture_results(fixture: str) -> dict[str, object]:
    if fixture == "schwarzschild":
        return _read_json(SCHWARZSCHILD_POLARITY_OUTPUT)
    if fixture == "sr":
        if not SR_POLARITY_OUTPUT.is_file():
            write_sr_polarity_output(SR_POLARITY_OUTPUT)
        return _read_json(SR_POLARITY_OUTPUT)
    if fixture == "pure_algebraic":
        return _read_json(PURE_POLARITY_OUTPUT)
    if fixture == "cbrt_chain":
        if not CBRT_POLARITY_OUTPUT.is_file():
            write_cbrt_polarity_output(CBRT_POLARITY_OUTPUT)
        return _read_json(CBRT_POLARITY_OUTPUT)
    raise ValueError(f"unknown fixture: {fixture}")


def compare_fixtures(fixtures: tuple[str, ...] | None = None) -> dict[str, object]:
    fixture_names = fixtures if fixtures is not None else _available_fixtures()
    polarity = {fixture: load_fixture_results(fixture) for fixture in fixture_names}
    lattice = _load_lattice_results(fixture_names)
    per_pair = _per_pair_aggregate_comparison(polarity, fixture_names)
    grid_precision = _per_grid_per_precision_comparison(polarity, fixture_names)
    lattice_grain = _lattice_grain_comparison(lattice, fixture_names)
    sterbenz = _sterbenz_boundary_comparison(fixture_names)
    headline, reasons = _headline(per_pair, lattice_grain, sterbenz, fixture_names)
    return {
        "campaign": "task028_three_fixture_comparison" if "pure_algebraic" in fixture_names else "task027_cross_fixture_comparison",
        "fixtures": list(fixture_names),
        "per_pair_aggregate_comparison": per_pair,
        "per_grid_per_precision_comparison": grid_precision,
        "lattice_grain_comparison": lattice_grain,
        "sterbenz_boundary_comparison": sterbenz,
        "headline_finding": headline,
        "headline_reasons": reasons,
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


def _available_fixtures() -> tuple[str, ...]:
    if PURE_POLARITY_OUTPUT.is_file():
        return ("schwarzschild", "sr", "pure_algebraic")
    return ("schwarzschild", "sr")


def _load_lattice_results(fixture_names: tuple[str, ...]) -> dict[str, dict[str, object]]:
    if not SR_LATTICE_OUTPUT.is_file():
        write_sr_lattice_output(SR_LATTICE_OUTPUT)
    if "pure_algebraic" in fixture_names and not PURE_LATTICE_OUTPUT.is_file():
        write_pure_lattice_output(PURE_LATTICE_OUTPUT)
    if "cbrt_chain" in fixture_names and not CBRT_LATTICE_OUTPUT.is_file():
        write_cbrt_lattice_output(CBRT_LATTICE_OUTPUT)
    result = {
        "schwarzschild": _read_json(SCHWARZSCHILD_LATTICE_OUTPUT),
        "sr": _read_json(SR_LATTICE_OUTPUT),
    }
    if "pure_algebraic" in fixture_names:
        result["pure_algebraic"] = _read_json(PURE_LATTICE_OUTPUT)
    if "cbrt_chain" in fixture_names:
        result["cbrt_chain"] = _read_json(CBRT_LATTICE_OUTPUT)
    return result


def _per_pair_aggregate_comparison(polarity: dict[str, dict[str, object]], fixture_names: tuple[str, ...]) -> list[dict[str, object]]:
    rows = []
    for pair in PAIR_ORDER:
        statuses = {fixture: polarity[fixture]["aggregate_classifications"][pair]["aggregate"] for fixture in fixture_names}
        row = {
            "pair": pair,
            "schwarzschild_aggregate": statuses["schwarzschild"],
            "sr_aggregate": statuses["sr"],
            "same_aggregate": statuses["schwarzschild"] == statuses["sr"],
            "all_same_aggregate": len(set(statuses.values())) == 1,
        }
        if "pure_algebraic" in statuses:
            row["pure_algebraic_aggregate"] = statuses["pure_algebraic"]
        if "cbrt_chain" in statuses:
            row["cbrt_chain_aggregate"] = statuses["cbrt_chain"]
        rows.append(row)
    return rows


def _per_grid_per_precision_comparison(polarity: dict[str, dict[str, object]], fixture_names: tuple[str, ...]) -> list[dict[str, object]]:
    rows = []
    tables = {
        fixture: {(table["grid_name"], table["precision"]): table for table in polarity[fixture]["polarity_tables"]}
        for fixture in fixture_names
    }
    for grid_name, precision in sorted(tables["schwarzschild"]):
        for pair in PAIR_ORDER:
            row: dict[str, object] = {"grid": grid_name, "precision": precision, "pair": pair}
            for fixture in fixture_names:
                data = tables[fixture][(grid_name, precision)]["pairs"][pair]
                row[f"{fixture}_cofire"] = data["cofire_count"]
                row[f"{fixture}_same_fraction"] = data["same_sign_fraction"]
            rows.append(row)
    return rows


def _lattice_grain_comparison(lattice: dict[str, dict[str, object]], fixture_names: tuple[str, ...]) -> list[dict[str, object]]:
    rows = []
    for form_id in ("F1", "F2", "F3", "F4"):
        row: dict[str, object] = {"form": form_id, "precision": "float64"}
        for fixture in fixture_names:
            data = _lattice_form_data(lattice[fixture], fixture, form_id)
            row[f"{fixture}_classification"] = data["candidate_classification"]
            row[f"{fixture}_nonzero"] = data["n_nonzero"]
            row[f"{fixture}_distinct_levels"] = data["n_distinct_levels"]
            row[f"{fixture}_integer_residual_max"] = data["level_integer_residual_max"]
        rows.append(row)
    return rows


def _lattice_form_data(data: dict[str, object], fixture: str, form_id: str) -> dict[str, object]:
    if fixture == "schwarzschild":
        return data["submodules"]["A_lattice_structure"]["by_form"][form_id]["by_precision"]["float64"]
    return data["by_form"][form_id]["by_precision"]["float64"]


def _sterbenz_boundary_comparison(fixture_names: tuple[str, ...]) -> list[dict[str, object]]:
    rows = []
    if "schwarzschild" in fixture_names:
        schwarzschild_values = sweep_r_values()
        boundary = 4.0
        below = tuple(value for value in schwarzschild_values if value < boundary)
        above = tuple(value for value in schwarzschild_values if value >= boundary)
        rows.append(_sterbenz_row("schwarzschild", "r", boundary, below, above, lambda value: schwarzschild_float64(value)["F2"], "above_boundary_higher"))
    if "sr" in fixture_names:
        sr_values = beta_grid()
        boundary = 2.0 ** -0.5
        below = tuple(value for value in sr_values if value <= boundary)
        above = tuple(value for value in sr_values if value > boundary)
        rows.append(_sterbenz_row("sr", "beta", boundary, below, above, lambda value: sr_float64(value)["F2"], "below_boundary_higher"))
    if "pure_algebraic" in fixture_names:
        pure_values = x_grid()
        boundary = 0.5
        below = tuple(value for value in pure_values if value <= boundary)
        above = tuple(value for value in pure_values if value > boundary)
        rows.append(_sterbenz_row("pure_algebraic", "x", boundary, below, above, lambda value: pure_float64(value)["F2"], "below_boundary_higher"))
    if "cbrt_chain" in fixture_names:
        cbrt_values = x_grid()
        boundary = 0.5
        below = tuple(value for value in cbrt_values if value <= boundary)
        above = tuple(value for value in cbrt_values if value > boundary)
        rows.append(_sterbenz_row("cbrt_chain", "x", boundary, below, above, lambda value: cbrt_float64(value)["F2"], "below_boundary_higher"))
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


def _headline(per_pair: list[dict[str, object]], lattice: list[dict[str, object]], sterbenz: list[dict[str, object]], fixture_names: tuple[str, ...]) -> tuple[str, list[str]]:
    pair_map = {row["pair"]: row for row in per_pair}
    lattice_map = {row["form"]: row for row in lattice}
    f1_f2_supported = all(pair_map["F1_F2"][f"{fixture}_aggregate"] == "grid_stable_polarity_coupling" for fixture in fixture_names)
    f3_silent = all(int(lattice_map["F3"][f"{fixture}_nonzero"]) == 0 for fixture in fixture_names)
    f2_lattice = all(lattice_map["F2"][f"{fixture}_classification"] in {"lattice_integer", "non_integer_lattice"} for fixture in fixture_names)
    f4_integer = all(lattice_map["F4"][f"{fixture}_classification"] in {"lattice_integer", "single_level"} for fixture in fixture_names)
    sterbenz_match = all(bool(row["supports_prediction"]) for row in sterbenz)
    invariants = {
        "F1/F2 grid-stable polarity": f1_f2_supported,
        "F3 silence": f3_silent,
        "F2 lattice grain": f2_lattice,
        "F4 integer lattice": f4_integer,
        "Sterbenz direction": sterbenz_match,
    }
    failed = [name for name, ok in invariants.items() if not ok]
    if not failed:
        return "chain_property_supported", ["all requested substrate-level invariants agree across available fixtures"]
    if "pure_algebraic" in fixture_names:
        pure_diverges = (
            pair_map["F1_F2"]["schwarzschild_aggregate"] == "grid_stable_polarity_coupling"
            and pair_map["F1_F2"]["sr_aggregate"] == "grid_stable_polarity_coupling"
            and pair_map["F1_F2"]["pure_algebraic_aggregate"] != "grid_stable_polarity_coupling"
            and not f2_lattice
            and not f4_integer
        )
        if pure_diverges:
            return "chain_property_rejected", failed
    return "chain_property_partial", failed


def _write_csvs(payload: dict[str, object]) -> None:
    fixture_names = tuple(payload["fixtures"])
    with PER_PAIR_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        header = ["pair"] + [f"{fixture}_aggregate" for fixture in fixture_names] + ["all_same_aggregate"]
        writer.writerow(header)
        for row in payload["per_pair_aggregate_comparison"]:
            writer.writerow([row["pair"]] + [row[f"{fixture}_aggregate"] for fixture in fixture_names] + [row["all_same_aggregate"]])
    with LATTICE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        header = ["form", "precision"]
        for fixture in fixture_names:
            header.extend([f"{fixture}_classification", f"{fixture}_nonzero", f"{fixture}_distinct_levels", f"{fixture}_integer_residual_max"])
        writer.writerow(header)
        for row in payload["lattice_grain_comparison"]:
            out = [row["form"], row["precision"]]
            for fixture in fixture_names:
                out.extend([row[f"{fixture}_classification"], row[f"{fixture}_nonzero"], row[f"{fixture}_distinct_levels"], row[f"{fixture}_integer_residual_max"]])
            writer.writerow(out)
    with STERBENZ_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", "coordinate", "boundary", "f2_count_below_boundary", "f2_count_above_boundary", "below_density", "above_density", "predicted_direction", "observed_direction", "supports_prediction"))
        for row in payload["sterbenz_boundary_comparison"]:
            writer.writerow((row["fixture"], row["coordinate"], row["boundary"], row["f2_count_below_boundary"], row["f2_count_above_boundary"], row["below_density"], row["above_density"], row["predicted_direction"], row["observed_direction"], row["supports_prediction"]))


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
