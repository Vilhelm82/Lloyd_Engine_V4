from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Sequence

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import four_form_float32 as schwarzschild_float32
from .multi_precision_four_form import four_form_float64 as schwarzschild_float64
from .polarity_grid_stability import DEFAULT_OUTPUT as SCHWARZSCHILD_POLARITY_OUTPUT
from .polarity_grid_stability import GRID_ORDER, GRID_SEEDS, PAIR_ORDER
from .polarity_grid_stability import construct_grid as construct_schwarzschild_grid
from .pure_algebraic_polarity_grid_stability import DEFAULT_OUTPUT as PURE_POLARITY_OUTPUT
from .pure_algebraic_polarity_grid_stability import construct_grid as construct_pure_grid
from .pure_algebraic_four_form import four_form_float32 as pure_float32
from .pure_algebraic_four_form import four_form_float64 as pure_float64
from .sr_four_form import four_form_float32 as sr_float32
from .sr_four_form import four_form_float64 as sr_float64
from .sr_polarity_grid_stability import DEFAULT_OUTPUT as SR_POLARITY_OUTPUT
from .sr_polarity_grid_stability import construct_grid as construct_sr_grid


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task028_conditional_masks_joint_lattice_pure_algebraic"
DEFAULT_OUTPUT = REPORT_DIR / "conditional_mask_output.json"
CONDITIONAL_CSV = REPORT_DIR / "conditional_mask_table.csv"
DEFAULT_FIXTURES = ("schwarzschild", "sr")


def compute_conditional_masks(fixture: str, grid: str, precision: str) -> dict[str, object]:
    if grid not in GRID_ORDER:
        raise ValueError(f"unknown grid: {grid}")
    if precision not in ("float32", "float64"):
        raise ValueError(f"unknown precision: {precision}")
    _assert_existing_table(fixture, grid, precision)
    grid_payload = _construct_grid(fixture, grid)
    values = tuple(float(value) for value in grid_payload["r_values"])
    rows = [_values_for_precision(fixture, value, precision) for value in values]
    pairs = {pair: _pair_decomposition(pair, rows) for pair in PAIR_ORDER}
    return {
        "fixture": fixture,
        "grid": grid,
        "precision": precision,
        "n_cells": len(rows),
        "pairs": pairs,
    }


def run_conditional_mask_campaign(fixtures: Sequence[str] = DEFAULT_FIXTURES) -> dict[str, object]:
    entries = [
        compute_conditional_masks(fixture, grid, precision)
        for fixture in fixtures
        for grid in GRID_ORDER
        for precision in ("float32", "float64")
    ]
    return {
        "campaign": "task028_conditional_mask_analysis",
        "fixtures": list(fixtures),
        "grids": list(GRID_ORDER),
        "precisions": ["float32", "float64"],
        "entries": entries,
        "headline_findings": _headline_findings(entries),
    }


def write_conditional_mask_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_conditional_mask_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(campaign_bytes(payload).decode("utf-8"), encoding="utf-8")
    _write_csv(payload, CONDITIONAL_CSV)
    return payload


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_conditional_mask_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_conditional_mask_output(Path(args.output))


def _pair_decomposition(pair: str, rows: Sequence[dict[str, float]]) -> dict[str, object]:
    left, right = pair.split("_")
    left_fires = 0
    right_fires = 0
    cofire = 0
    left_only = 0
    right_only = 0
    neither = 0
    same = 0
    opposite = 0
    for row in rows:
        left_sign = _sign(row[left])
        right_sign = _sign(row[right])
        left_on = left_sign != 0
        right_on = right_sign != 0
        if left_on:
            left_fires += 1
        if right_on:
            right_fires += 1
        if left_on and right_on:
            cofire += 1
            if left_sign == right_sign:
                same += 1
            else:
                opposite += 1
        elif left_on:
            left_only += 1
        elif right_on:
            right_only += 1
        else:
            neither += 1
    return {
        "left_form": left,
        "right_form": right,
        "left_fires": left_fires,
        "right_fires": right_fires,
        "left_only": left_only,
        "right_only": right_only,
        "F1_fires": left_fires,
        "F2_fires": right_fires,
        "cofire": cofire,
        "F1_only": left_only,
        "F2_only": right_only,
        "neither": neither,
        "p_F2_given_F1": _fraction(cofire, left_fires),
        "p_F1_given_F2": _fraction(cofire, right_fires),
        "asymmetry_ratio": _fraction(right_only, left_only),
        "cofire_same_sign": same,
        "cofire_opposite_sign": opposite,
        "form_fires": {left: left_fires, right: right_fires},
        "form_only": {left: left_only, right: right_only},
    }


def _construct_grid(fixture: str, grid: str) -> dict[str, object]:
    seed = GRID_SEEDS[grid]
    if fixture == "schwarzschild":
        return construct_schwarzschild_grid(grid, seed)
    if fixture == "sr":
        return construct_sr_grid(grid, seed)
    if fixture == "pure_algebraic":
        return construct_pure_grid(grid, seed)
    raise ValueError(f"unknown fixture: {fixture}")


def _values_for_precision(fixture: str, value: float, precision: str) -> dict[str, float]:
    if fixture == "schwarzschild":
        return schwarzschild_float32(value) if precision == "float32" else schwarzschild_float64(value)
    if fixture == "sr":
        return sr_float32(value) if precision == "float32" else sr_float64(value)
    if fixture == "pure_algebraic":
        return pure_float32(value) if precision == "float32" else pure_float64(value)
    raise ValueError(f"unknown fixture: {fixture}")


def _assert_existing_table(fixture: str, grid: str, precision: str) -> None:
    output = _polarity_output_path(fixture)
    if not output.is_file():
        if fixture == "pure_algebraic":
            return
        raise FileNotFoundError(output)
    data = json.loads(output.read_text(encoding="utf-8"))
    known = {(table["grid_name"], table["precision"]) for table in data["polarity_tables"]}
    if (grid, precision) not in known:
        raise ValueError(f"missing existing polarity table for {fixture} {grid} {precision}")


def _polarity_output_path(fixture: str) -> Path:
    if fixture == "schwarzschild":
        return SCHWARZSCHILD_POLARITY_OUTPUT
    if fixture == "sr":
        return SR_POLARITY_OUTPUT
    if fixture == "pure_algebraic":
        return PURE_POLARITY_OUTPUT
    raise ValueError(f"unknown fixture: {fixture}")


def _headline_findings(entries: Sequence[dict[str, object]]) -> list[str]:
    findings = []
    for fixture in sorted({str(entry["fixture"]) for entry in entries}):
        f1_f2 = [entry["pairs"]["F1_F2"] for entry in entries if entry["fixture"] == fixture]
        partial = sum(1 for item in f1_f2 if item["F1_only"] > 0 and item["F2_only"] > 0)
        full = sum(1 for item in f1_f2 if item["F1_only"] == 0 or item["F2_only"] == 0)
        findings.append(f"{fixture}: partial_overlap_tables={partial}, subset_like_tables={full}")
    return findings


def _write_csv(payload: dict[str, object], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", "grid", "precision", "pair", "left_form", "right_form", "left_fires", "right_fires", "left_only", "right_only", "cofire", "neither", "p_right_given_left", "p_left_given_right", "asymmetry_ratio", "cofire_same_sign", "cofire_opposite_sign"))
        for entry in payload["entries"]:
            for pair in PAIR_ORDER:
                item = entry["pairs"][pair]
                writer.writerow((entry["fixture"], entry["grid"], entry["precision"], pair, item["left_form"], item["right_form"], item["left_fires"], item["right_fires"], item["left_only"], item["right_only"], item["cofire"], item["neither"], _csv_float(item["p_F2_given_F1"]), _csv_float(item["p_F1_given_F2"]), _csv_float(item["asymmetry_ratio"]), item["cofire_same_sign"], item["cofire_opposite_sign"]))


def _csv_float(value: object) -> str:
    if value is None:
        return "null"
    return f"{float(value):.6f}"


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
