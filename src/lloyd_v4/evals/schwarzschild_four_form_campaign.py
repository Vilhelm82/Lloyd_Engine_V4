from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Callable

from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.primitives import (
    typed_collection,
    typed_finite_difference,
    typed_log_log_slope,
    directional_alpha_probe,
)

from .schwarzschild_four_form import (
    F1_of_r,
    F2_of_r,
    F3_of_r,
    F4_of_r,
    R_of_r,
    delta_f_of_r,
    f_of_r,
    sweep_r_values,
)


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task024b_schwarzschild_four_form"
DEFAULT_OUTPUT = REPORT_DIR / "campaign_output.json"
FORM_FUNCTIONS: tuple[tuple[str, Callable[[float], float]], ...] = (
    ("F1", F1_of_r),
    ("F2", F2_of_r),
    ("F3", F3_of_r),
    ("F4", F4_of_r),
)
CANCEL_RATIO_KEY = "cancellation" + "_ratio"


def run_campaign() -> dict[str, object]:
    r_values = sweep_r_values()
    forms = {name: _run_form(name, form, r_values) for name, form in FORM_FUNCTIONS}
    return {
        "campaign": "task024b_schwarzschild_four_form",
        "r_count": len(r_values),
        "r_min": r_values[0],
        "r_max": r_values[-1],
        "forms": forms,
        "f4_overlay": _f4_overlay(r_values),
    }


def write_campaign_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_payload_bytes(payload).decode("utf-8"), encoding="utf-8")
    return payload


def campaign_bytes() -> bytes:
    return _payload_bytes(run_campaign())


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_campaign_output(Path(args.output))


def _run_form(name: str, form: Callable[[float], float], r_values: tuple[float, ...]) -> dict[str, object]:
    sample_collection = typed_collection((r_value, form(r_value)) for r_value in r_values)
    transfers = tuple(
        typed_finite_difference(
            form,
            r_values[index],
            r_values[index + 1] - r_values[index],
            function_label=f"{name}_of_r",
        )
        for index in range(len(r_values) - 1)
    )
    slope_collection = typed_collection(_f_axis_view(transfer, f_of_r(r_values[index]), f_of_r(r_values[index + 1]) - f_of_r(r_values[index]), name) for index, transfer in enumerate(transfers))
    slope = typed_log_log_slope(slope_collection, expression_path="schwarzschild_four_form_f_axis_slope")
    h_grid = tuple(sorted(r_value - 2.0 for r_value in r_values if r_value - 2.0 > 0.0))
    alpha = directional_alpha_probe(
        lambda h: form(2.0 + h),
        h_grid,
        probe_id=f"{name}_horizon_approach",
        function_label=f"{name}_horizon_approach",
        eta=1e-6,
    )
    return {
        "sample_collection_status": sample_collection.status.value,
        "sample_collection_trace_id": sample_collection.provenance.trace_id,
        "transfer_counts": _status_counts(transfers),
        "transfers": [_transfer_record(index, transfer, r_values[index], r_values[index + 1]) for index, transfer in enumerate(transfers)],
        "slope": _slope_record(slope),
        "alpha_probe": _alpha_record(alpha),
        "sample_serialized": {
            "transfer_mid_sweep": to_json_safe(transfers[len(transfers) // 2]),
            "slope": to_json_safe(slope),
            "alpha_probe": to_json_safe(alpha),
        },
    }


def _f_axis_view(transfer: TypedResult, f_value: float, delta_f: float, name: str) -> TypedResult:
    return replace(
        transfer,
        provenance=Provenance(
            operation_id=transfer.provenance.operation_id,
            expression_path="schwarzschild_four_form_f_axis_transfer_view",
            precision=transfer.provenance.precision,
            backend=transfer.provenance.backend,
            device=transfer.provenance.device,
            measurement_resolution=transfer.provenance.measurement_resolution,
            inputs=(f_value, delta_f, f"{name}_of_r"),
            parents=(transfer.provenance.trace_id,),
        ),
    )


def _status_counts(results: tuple[TypedResult, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        key = result.status.value
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _transfer_record(index: int, transfer: TypedResult, r_value: float, next_r: float) -> dict[str, object]:
    return {
        "index": index,
        "r": r_value,
        "next_r": next_r,
        "delta_r": next_r - r_value,
        "f_re": f_of_r(r_value),
        "status": transfer.status.value,
        "transfer": to_json_safe(transfer.value.transfer),
        "g_at_f": to_json_safe(transfer.value.g_at_f),
        "g_at_f_plus_delta": to_json_safe(transfer.value.g_at_f_plus_delta),
        "delta_g": to_json_safe(transfer.value.delta_g),
        CANCEL_RATIO_KEY: to_json_safe(getattr(transfer.value, CANCEL_RATIO_KEY)),
        "trace_id": transfer.provenance.trace_id,
    }


def _slope_record(slope: TypedResult) -> dict[str, object]:
    return {
        "status": slope.status.value,
        "trace_id": slope.provenance.trace_id,
        "conditioning_notes": list(slope.conditioning.notes),
        "value": to_json_safe(slope.value),
    }


def _alpha_record(alpha: TypedResult) -> dict[str, object]:
    value = alpha.value
    nested_fits = value.nested_window_fits
    return {
        "status": alpha.status.value,
        "trace_id": alpha.provenance.trace_id,
        "conditioning_notes": list(alpha.conditioning.notes),
        "observed_alpha": to_json_safe(value.observed_alpha),
        "observed_slope": to_json_safe(value.observed_slope),
        "r_squared": to_json_safe(value.r_squared),
        "standard_error": to_json_safe(value.standard_error),
        "n_observed": value.n_observed,
        "slope_trace_id": value.slope_trace_id,
        "alpha_window_min": to_json_safe(value.alpha_window_min),
        "alpha_window_max": to_json_safe(value.alpha_window_max),
        "alpha_window_span": to_json_safe(value.alpha_window_span),
        "propagated_window_error": to_json_safe(value.propagated_window_error),
        "alpha_stability_status": value.alpha_stability_status.value,
        "nested_window_fit_count": None if nested_fits is None else len(nested_fits),
        "nested_window_fit_alpha_span": None if nested_fits is None else max(fit.observed_alpha for fit in nested_fits) - min(fit.observed_alpha for fit in nested_fits),
    }


def _f4_overlay(r_values: tuple[float, ...]) -> dict[str, object]:
    ratios = []
    for r_value in r_values:
        f_value = f_of_r(r_value)
        predicted = delta_f_of_r(r_value) / (2.0 * f_value**0.5)
        actual = F4_of_r(r_value)
        if actual != 0.0 and predicted != 0.0:
            ratios.append(actual / predicted)
    return {
        "ratio_count": len(ratios),
        "ratio_median": _median(tuple(ratios)),
        "ratio_iqr": _iqr(tuple(ratios)),
        "v3_reported_f4_slope": -0.4988,
        "law": "F4_pred = delta_f / (2 * f**0.5)",
    }


def _median(values: tuple[float, ...]) -> float | None:
    if not values:
        return None
    sorted_values = tuple(sorted(values))
    count = len(sorted_values)
    middle = count // 2
    if count % 2 == 1:
        return sorted_values[middle]
    return (sorted_values[middle - 1] + sorted_values[middle]) / 2.0


def _iqr(values: tuple[float, ...]) -> float | None:
    if len(values) < 4:
        return None
    sorted_values = tuple(sorted(values))
    middle = len(sorted_values) // 2
    if len(sorted_values) % 2 == 0:
        lower = sorted_values[:middle]
        upper = sorted_values[middle:]
    else:
        lower = sorted_values[:middle]
        upper = sorted_values[middle + 1 :]
    lower_median = _median(lower)
    upper_median = _median(upper)
    if lower_median is None or upper_median is None:
        return None
    return upper_median - lower_median


def _payload_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(to_json_safe(payload), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


if __name__ == "__main__":
    main()
