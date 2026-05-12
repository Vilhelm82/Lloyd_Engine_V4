from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import ulp_of_double
from .sr_four_form import FORM_KEYS, beta_grid, four_form_decimal_oracle, four_form_float32, four_form_float64, sr_four_form_battery


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task027_sr_four_form_cross_fixture"
DEFAULT_OUTPUT = REPORT_DIR / "sr_lattice_campaign_output.json"
BATTERY_OUTPUT = REPORT_DIR / "sr_four_form_battery.json"
REGION_ORDER = ("non_relativistic", "mildly_relativistic", "ultra_relativistic")
PRECISIONS = ("float32", "float64", "decimal_50")


def run_campaign() -> dict[str, object]:
    values = beta_grid()
    return {
        "campaign": "task027_sr_lattice_campaign",
        "beta_count": len(values),
        "beta_min": values[0],
        "beta_max": values[-1],
        "by_form": {
            form_id: {
                "by_precision": {
                    precision_name: _lattice_for_form_precision(form_id, precision_name, values)
                    for precision_name in PRECISIONS
                }
            }
            for form_id in FORM_KEYS
        },
    }


def write_campaign_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(campaign_bytes(payload).decode("utf-8"), encoding="utf-8")
    BATTERY_OUTPUT.write_text((json.dumps(to_json_safe(sr_four_form_battery()), sort_keys=True, indent=2, allow_nan=False) + "\n"), encoding="utf-8")
    return payload


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_campaign_output(Path(args.output))


def _lattice_for_form_precision(form_id: str, precision_name: str, values: tuple[float, ...]) -> dict[str, object]:
    levels = []
    residuals = []
    regions: dict[str, list[int]] = {region: [] for region in REGION_ORDER}
    for beta_value in values:
        form_value = _form_value(form_id, precision_name, beta_value)
        if form_value == 0.0:
            continue
        unit_value = _ulp_q_for_precision(beta_value, precision_name)
        level = form_value / unit_value if unit_value != 0.0 else 0.0
        integer_level = int(round(level))
        levels.append(integer_level)
        residuals.append(level - integer_level)
        regions[_region_name(beta_value)].append(integer_level)
    histogram = {str(level): levels.count(level) for level in sorted(set(levels))}
    sorted_levels = tuple(sorted(set(levels)))
    jumps = [int(sorted_levels[index + 1] - sorted_levels[index]) for index in range(len(sorted_levels) - 1)]
    max_residual = max((abs(value) for value in residuals), default=0.0)
    if not levels:
        label = "lattice_empty"
    elif len(set(levels)) == 1:
        label = "single_level"
    elif max_residual < 1.0e-3:
        label = "lattice_integer"
    else:
        label = "non_integer_lattice"
    return {
        "n_total": len(values),
        "n_nonzero": len(levels),
        "level_integer_residual_max": max_residual,
        "level_integer_residual_median": _median(tuple(abs(value) for value in residuals)),
        "n_distinct_levels": len(set(levels)),
        "level_min": min(levels) if levels else None,
        "level_max": max(levels) if levels else None,
        "level_histogram": histogram,
        "level_jump_distribution": jumps,
        "regional_distinct_level_counts": {region: len(set(region_levels)) for region, region_levels in regions.items()},
        "candidate_classification": label,
    }


def _form_value(form_id: str, precision_name: str, beta_value: float) -> float:
    if precision_name == "float32":
        return four_form_float32(beta_value)[form_id]
    if precision_name == "float64":
        return four_form_float64(beta_value)[form_id]
    return four_form_decimal_oracle(beta_value, 50)[form_id]


def _ulp_q_for_precision(beta_value: float, precision_name: str) -> float:
    if precision_name == "float32":
        s = np.float32
        beta_s = s(beta_value)
        q_value = s(1.0) - beta_s * beta_s
        return _ulp_of_float32(float(q_value))
    beta_float = float(beta_value)
    return ulp_of_double(1.0 - beta_float * beta_float)


def _ulp_of_float32(value: float) -> float:
    x = np.float32(abs(float(value)))
    if x == np.float32(0.0):
        return float(np.nextafter(x, np.float32(1.0), dtype=np.float32) - x)
    return float(np.nextafter(x, np.float32("inf"), dtype=np.float32) - x)


def _region_name(beta_value: float) -> str:
    if beta_value < 0.5:
        return "non_relativistic"
    if beta_value < 0.9:
        return "mildly_relativistic"
    return "ultra_relativistic"


def _median(values: Iterable[float]) -> float | None:
    sorted_values = tuple(sorted(float(value) for value in values))
    if not sorted_values:
        return None
    count = len(sorted_values)
    middle = count // 2
    if count % 2 == 1:
        return sorted_values[middle]
    return (sorted_values[middle - 1] + sorted_values[middle]) / 2.0


def lattice_summary_for_values(form_id: str, precision_name: str, values: Sequence[float]) -> dict[str, object]:
    return _lattice_for_form_precision(form_id, precision_name, tuple(float(value) for value in values))


if __name__ == "__main__":
    main()
