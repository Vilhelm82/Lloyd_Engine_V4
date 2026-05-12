from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Sequence

import numpy as np

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import four_form_decimal_oracle as schwarzschild_decimal
from .multi_precision_four_form import four_form_float32 as schwarzschild_float32
from .multi_precision_four_form import four_form_float64 as schwarzschild_float64
from .multi_precision_four_form import ulp_of_double
from .pure_algebraic_four_form import four_form_decimal_oracle as pure_decimal
from .pure_algebraic_four_form import four_form_float32 as pure_float32
from .pure_algebraic_four_form import four_form_float64 as pure_float64
from .pure_algebraic_four_form import x_grid
from .pure_algebraic_lattice_campaign import unit_for_precision as pure_unit_for_precision
from .schwarzschild_four_form import f_of_r, sweep_r_values
from .sr_four_form import beta_grid
from .sr_four_form import four_form_decimal_oracle as sr_decimal
from .sr_four_form import four_form_float32 as sr_float32
from .sr_four_form import four_form_float64 as sr_float64


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task028_conditional_masks_joint_lattice_pure_algebraic"
DEFAULT_OUTPUT = REPORT_DIR / "joint_signed_lattice_output.json"
JOINT_CSV = REPORT_DIR / "joint_signed_lattice_table.csv"
DEFAULT_FIXTURES = ("schwarzschild", "sr")
FORM_ORDER = ("F1", "F2", "F4")
PRECISIONS = ("float32", "float64", "decimal_50")


def compute_joint_signed_lattice_histogram(fixture: str, precision: str) -> dict[str, object]:
    if precision not in PRECISIONS:
        raise ValueError(f"unknown precision: {precision}")
    values = _fixture_values(fixture)
    rows = []
    for index, coordinate in enumerate(values):
        form_values = _values_for_precision(fixture, coordinate, precision)
        levels = {form_id: _level_for_value(fixture, form_id, precision, coordinate, form_values[form_id]) for form_id in FORM_ORDER}
        signs = {form_id: _sign(form_values[form_id]) for form_id in FORM_ORDER}
        rows.append({"index": index, "levels": levels, "signs": signs})
    state_counts: dict[str, dict[str, object]] = {}
    for row in rows:
        key = _state_key(row["levels"], row["signs"])
        if key not in state_counts:
            state_counts[key] = {"state_key": key, "count": 0, "example_indices": []}
        state_counts[key]["count"] = int(state_counts[key]["count"]) + 1
        examples = state_counts[key]["example_indices"]
        if isinstance(examples, list) and len(examples) < 5:
            examples.append(row["index"])
    joint_states = []
    for state in state_counts.values():
        joint_states.append(
            {
                "state_key": state["state_key"],
                "count": state["count"],
                "fraction": int(state["count"]) / float(len(rows)),
                "example_indices": state["example_indices"],
            }
        )
    joint_states.sort(key=lambda item: (-int(item["count"]), str(item["state_key"])))
    return {
        "fixture": fixture,
        "precision": precision,
        "n_cells": len(rows),
        "joint_states": joint_states,
        "marginals": _marginals(rows),
        "conditional_summaries": _conditional_summaries(rows),
    }


def run_joint_lattice_campaign(fixtures: Sequence[str] = DEFAULT_FIXTURES) -> dict[str, object]:
    entries = [
        compute_joint_signed_lattice_histogram(fixture, precision)
        for fixture in fixtures
        for precision in PRECISIONS
    ]
    return {
        "campaign": "task028_joint_signed_lattice_analysis",
        "fixtures": list(fixtures),
        "precisions": list(PRECISIONS),
        "entries": entries,
        "headline_findings": _headline_findings(entries),
    }


def write_joint_lattice_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_joint_lattice_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(campaign_bytes(payload).decode("utf-8"), encoding="utf-8")
    _write_csv(payload, JOINT_CSV)
    return payload


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_joint_lattice_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_joint_lattice_output(Path(args.output))


def _fixture_values(fixture: str) -> tuple[float, ...]:
    if fixture == "schwarzschild":
        return sweep_r_values()
    if fixture == "sr":
        return beta_grid()
    if fixture == "pure_algebraic":
        return x_grid()
    raise ValueError(f"unknown fixture: {fixture}")


def _values_for_precision(fixture: str, coordinate: float, precision: str) -> dict[str, float]:
    if fixture == "schwarzschild":
        if precision == "float32":
            return schwarzschild_float32(coordinate)
        if precision == "float64":
            return schwarzschild_float64(coordinate)
        return schwarzschild_decimal(coordinate, 50)
    if fixture == "sr":
        if precision == "float32":
            return sr_float32(coordinate)
        if precision == "float64":
            return sr_float64(coordinate)
        return sr_decimal(coordinate, 50)
    if fixture == "pure_algebraic":
        if precision == "float32":
            return pure_float32(coordinate)
        if precision == "float64":
            return pure_float64(coordinate)
        return pure_decimal(coordinate, 50)
    raise ValueError(f"unknown fixture: {fixture}")


def _level_for_value(fixture: str, form_id: str, precision: str, coordinate: float, value: float) -> float:
    if form_id not in FORM_ORDER:
        raise ValueError(f"unknown form: {form_id}")
    if value == 0.0:
        return 0.0
    unit_value = _unit_for_precision(fixture, coordinate, precision)
    if unit_value == 0.0:
        return 0.0
    level = value / unit_value
    return round(level * 2.0) / 2.0


def _unit_for_precision(fixture: str, coordinate: float, precision: str) -> float:
    if fixture == "schwarzschild":
        if precision == "float32":
            s = np.float32
            f_value = s(1.0) - s(2.0) / s(coordinate)
            return _ulp_of_float32(float(f_value))
        return ulp_of_double(f_of_r(coordinate))
    if fixture == "sr":
        if precision == "float32":
            s = np.float32
            beta_value = s(coordinate)
            q_value = s(1.0) - beta_value * beta_value
            return _ulp_of_float32(float(q_value))
        beta_float = float(coordinate)
        return ulp_of_double(1.0 - beta_float * beta_float)
    if fixture == "pure_algebraic":
        return pure_unit_for_precision(coordinate, precision)
    raise ValueError(f"unknown fixture: {fixture}")


def _marginals(rows: Sequence[dict[str, object]]) -> dict[str, object]:
    by_level = {form_id: _count_levels(tuple(row["levels"][form_id] for row in rows)) for form_id in FORM_ORDER}
    polarity_counts: dict[str, int] = {}
    for row in rows:
        state = _polarity_state(row["signs"])
        polarity_counts[state] = polarity_counts.get(state, 0) + 1
    return {
        "by_F1_level": by_level["F1"],
        "by_F2_level": by_level["F2"],
        "by_F4_level": by_level["F4"],
        "by_polarity_state": {key: polarity_counts[key] for key in sorted(polarity_counts)},
    }


def _conditional_summaries(rows: Sequence[dict[str, object]]) -> dict[str, object]:
    f2_given_f1_plus = _count_levels(tuple(row["levels"]["F2"] for row in rows if row["levels"]["F1"] == 1.0))
    f2_given_f1_minus = _count_levels(tuple(row["levels"]["F2"] for row in rows if row["levels"]["F1"] == -1.0))
    by_band: dict[str, dict[str, int]] = {}
    for row in rows:
        band = _f4_level_band(float(row["levels"]["F4"]))
        if band not in by_band:
            by_band[band] = {"aligned": 0, "opposed": 0, "single_or_silent": 0}
        signs = row["signs"]
        if signs["F1"] != 0 and signs["F2"] != 0:
            if signs["F1"] == signs["F2"]:
                by_band[band]["aligned"] += 1
            else:
                by_band[band]["opposed"] += 1
        else:
            by_band[band]["single_or_silent"] += 1
    return {
        "F2_level_given_F1_plus1": f2_given_f1_plus,
        "F2_level_given_F1_minus1": f2_given_f1_minus,
        "F1F2_polarity_given_F4_level_band": {key: by_band[key] for key in sorted(by_band)},
    }


def _headline_findings(entries: Sequence[dict[str, object]]) -> list[str]:
    findings = []
    for entry in entries:
        top = entry["joint_states"][0] if entry["joint_states"] else {"state_key": "none", "count": 0}
        findings.append(f"{entry['fixture']} {entry['precision']}: states={len(entry['joint_states'])}, top={top['state_key']} count={top['count']}")
    return findings


def _write_csv(payload: dict[str, object], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", "precision", "state_key", "count", "fraction", "example_indices"))
        for entry in payload["entries"]:
            for state in entry["joint_states"]:
                writer.writerow((entry["fixture"], entry["precision"], state["state_key"], state["count"], f"{float(state['fraction']):.6f}", " ".join(str(index) for index in state["example_indices"])))


def _count_levels(levels: Sequence[float]) -> dict[str, int]:
    counts: dict[float, int] = {}
    for level in levels:
        level_value = float(level)
        counts[level_value] = counts.get(level_value, 0) + 1
    return {_level_label(level): counts[level] for level in sorted(counts)}


def _state_key(levels: dict[str, float], signs: dict[str, int]) -> str:
    return ",".join(
        (
            f"L1={_level_label(levels['F1'])}",
            f"L2={_level_label(levels['F2'])}",
            f"L4={_level_label(levels['F4'])}",
            f"S1={_sign_label(signs['F1'])}",
            f"S2={_sign_label(signs['F2'])}",
            f"S4={_sign_label(signs['F4'])}",
        )
    )


def _polarity_state(signs: dict[str, int]) -> str:
    s1 = signs["F1"]
    s2 = signs["F2"]
    s4 = signs["F4"]
    if s1 == 0 and s2 == 0 and s4 == 0:
        return "all_silent"
    if s1 != 0 and s2 != 0 and s1 == s2 and s4 == 0:
        return "F1F2_aligned_F4_silent"
    if s1 != 0 and s2 != 0 and s1 == s2 and s4 == s1:
        return "F1F2_aligned_F4_aligned"
    if s1 != 0 and s2 != 0 and s1 == s2 and s4 == -s1:
        return "F1F2_aligned_F4_opposed"
    if s1 != 0 and s2 != 0 and s1 != s2:
        return "F1F2_opposed"
    if s1 != 0 and s2 == 0 and s4 == 0:
        return "F1_only"
    if s1 == 0 and s2 != 0 and s4 == 0:
        return "F2_only"
    if s1 == 0 and s2 == 0 and s4 != 0:
        return "F4_only"
    return "mixed_partial"


def _f4_level_band(level: float) -> str:
    absolute = abs(float(level))
    if absolute == 0.0:
        return "F4_zero"
    if absolute <= 4.0:
        return "F4_abs_1_to_4"
    if absolute <= 16.0:
        return "F4_abs_4_5_to_16"
    return "F4_abs_gt_16"


def _level_label(level: float) -> str:
    value = float(level)
    if value == 0.0:
        return "0"
    sign = "+" if value > 0.0 else "-"
    absolute = abs(value)
    if absolute.is_integer():
        return f"{sign}{int(absolute)}"
    return f"{sign}{absolute:.1f}"


def _sign_label(sign: int) -> str:
    if sign > 0:
        return "+"
    if sign < 0:
        return "-"
    return "0"


def _ulp_of_float32(value: float) -> float:
    x = np.float32(abs(float(value)))
    if x == np.float32(0.0):
        return float(np.nextafter(x, np.float32(1.0), dtype=np.float32) - x)
    return float(np.nextafter(x, np.float32("inf"), dtype=np.float32) - x)


def _sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


if __name__ == "__main__":
    main()
