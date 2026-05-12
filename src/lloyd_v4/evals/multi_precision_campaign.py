from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import (
    FLOAT32_TO_FLOAT64_UNIT_RATIO,
    FORM_KEYS,
    four_form_decimal_oracle,
    four_form_float32,
    four_form_float64,
    predicted_chain_envelope,
    ulp_of_double,
)
from .schwarzschild_four_form import sweep_r_values


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task017b_multi_precision_instrument_model"
DEFAULT_OUTPUT = REPORT_DIR / "campaign_output.json"


def run_campaign() -> dict[str, object]:
    r_values = sweep_r_values()
    phase_a = _phase_a(r_values)
    phase_b = _phase_b(r_values)
    phase_c = _phase_c(r_values)
    return {
        "campaign": "task017b_multi_precision_instrument_model",
        "r_count": len(r_values),
        "r_min": r_values[0],
        "r_max": r_values[-1],
        "phase_a": phase_a,
        "phase_b": phase_b,
        "phase_c": phase_c,
        "model_supported": bool(phase_a["pass"] and phase_b["pass"] and phase_c["pass"]),
    }


def write_campaign_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(campaign_bytes(payload).decode("utf-8"), encoding="utf-8")
    return payload


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_campaign_output(Path(args.output))


def _phase_a(r_values: tuple[float, ...]) -> dict[str, object]:
    forms: dict[str, object] = {}
    for form_key in FORM_KEYS:
        point_records = []
        residuals = []
        chain_envelopes = []
        chain_ratios = []
        result_bound_ratios = []
        abs_ratios = []
        nonzero_count = 0
        exceed_chain_count = 0
        exceed_allowed_chain_count = 0
        result_bound_exceed_count = 0
        near_values = []
        middle_values = []
        far_values = []
        for r_value in r_values:
            float64_value = four_form_float64(r_value)[form_key]
            decimal_value = four_form_decimal_oracle(r_value, 50)[form_key]
            residual = abs(float64_value - decimal_value)
            chain_envelope = predicted_chain_envelope(r_value)
            chain_ratio = _ratio_or_none(residual, chain_envelope)
            result_ulp = ulp_of_double(float64_value)
            result_bound = 10.0 * result_ulp
            result_bound_ratio = _ratio_or_none(residual, result_bound)
            abs_ratio = _ratio_or_none(residual, abs(float64_value))
            if float64_value != 0.0:
                nonzero_count += 1
                residuals.append(residual)
                chain_envelopes.append(chain_envelope)
                if chain_ratio is not None:
                    chain_ratios.append(chain_ratio)
                if result_bound_ratio is not None:
                    result_bound_ratios.append(result_bound_ratio)
                if abs_ratio is not None:
                    abs_ratios.append(abs_ratio)
                if r_value < 2.05:
                    near_values.append(residual)
                elif r_value < 3.0:
                    middle_values.append(residual)
                else:
                    far_values.append(residual)
                if residual > chain_envelope:
                    exceed_chain_count += 1
                if residual > 10.0 * chain_envelope:
                    exceed_allowed_chain_count += 1
                if residual > result_bound:
                    result_bound_exceed_count += 1
            point_records.append(
                {
                    "r": r_value,
                    "float64": float64_value,
                    "decimal50": decimal_value,
                    "residual": residual,
                    "chain_envelope": chain_envelope,
                    "ratio_to_chain_envelope": chain_ratio,
                    "result_ulp": result_ulp,
                    "result_bound": result_bound,
                    "ratio_to_result_bound": result_bound_ratio,
                    "residual_over_abs_float64": abs_ratio,
                }
            )
        forms[form_key] = {
            "float64_nonzero_count": nonzero_count,
            "median_residual": _median(residuals),
            "median_chain_envelope": _median(chain_envelopes),
            "median_ratio_to_chain_envelope": _median(chain_ratios),
            "max_ratio_to_chain_envelope": max(chain_ratios) if chain_ratios else None,
            "exceed_chain_envelope_count": exceed_chain_count,
            "exceed_allowed_chain_count": exceed_allowed_chain_count,
            "result_bound_exceed_count": result_bound_exceed_count,
            "median_ratio_to_result_bound": _median(result_bound_ratios),
            "median_residual_over_abs_float64": _median(abs_ratios),
            "near_field_nonzero_count": len(near_values),
            "middle_field_nonzero_count": len(middle_values),
            "far_field_nonzero_count": len(far_values),
            "near_field_median_residual": _median(near_values),
            "middle_field_median_residual": _median(middle_values),
            "far_field_median_residual": _median(far_values),
            "chain_diagnostic_pass": exceed_allowed_chain_count == 0,
            "pass": result_bound_exceed_count == 0,
            "points": point_records,
        }
    return {
        "forms": forms,
        "pass": all(bool(form["pass"]) for form in forms.values()),
        "result_bound_multiplier": 10.0,
        "chain_diagnostic_multiplier": 10.0,
        "finding": "result_ulp_bound_fails_by_construction",
    }


def _phase_b(r_values: tuple[float, ...]) -> dict[str, object]:
    ratios = []
    strict_larger_count = 0
    records = []
    for r_value in r_values:
        f32 = four_form_float32(r_value)["F4"]
        f64 = four_form_float64(r_value)["F4"]
        magnitude32 = abs(f32)
        magnitude64 = abs(f64)
        if magnitude32 > magnitude64:
            strict_larger_count += 1
        ratio = None
        if f32 != 0.0 and f64 != 0.0:
            ratio = magnitude32 / magnitude64
            ratios.append(ratio)
        records.append(
            {
                "r": r_value,
                "F4_float32": f32,
                "F4_float64": f64,
                "abs_float32": magnitude32,
                "abs_float64": magnitude64,
                "ratio": ratio,
            }
        )
    observed = _median(ratios)
    observed_over_expected = None if observed is None else observed / FLOAT32_TO_FLOAT64_UNIT_RATIO
    phase_pass = observed_over_expected is not None and 0.2 <= observed_over_expected <= 5.0
    return {
        "both_nonzero_count": len(ratios),
        "float32_strictly_larger_count": strict_larger_count,
        "median_ratio": observed,
        "expected_ratio": FLOAT32_TO_FLOAT64_UNIT_RATIO,
        "observed_over_expected": observed_over_expected,
        "pass": phase_pass,
        "points": records,
    }


def _phase_c(r_values: tuple[float, ...]) -> dict[str, object]:
    nonzero = []
    for r_value in r_values:
        values_by_path = {
            "float32": four_form_float32(r_value)["F3"],
            "float64": four_form_float64(r_value)["F3"],
            "decimal50": four_form_decimal_oracle(r_value, 50)["F3"],
        }
        for path_name, value in values_by_path.items():
            if value != 0.0:
                nonzero.append({"r": r_value, "path": path_name, "F3": value})
    return {
        "path_count": 3,
        "points_per_path": len(r_values),
        "nonzero_count": len(nonzero),
        "nonzero_points": nonzero,
        "pass": len(nonzero) == 0,
    }


def _median(values: Iterable[float]) -> float | None:
    sorted_values = tuple(sorted(values))
    if not sorted_values:
        return None
    count = len(sorted_values)
    middle = count // 2
    if count % 2 == 1:
        return sorted_values[middle]
    return (sorted_values[middle - 1] + sorted_values[middle]) / 2.0


def _ratio_or_none(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0:
        return None
    return numerator / denominator


if __name__ == "__main__":
    main()
