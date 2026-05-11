from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.status import ConditioningStatus, ProtocolStatus, SlopeStatus, TransferStatus
from lloyd_v4.core.validity import Validity
from lloyd_v4.primitives.typed_collection import TypedCollectionResult, TypedCollectionValue


LOG_LOG_SLOPE_SPACE = "LogLogSlopeObservation"
SLOPE_STATUSES = frozenset(
    {
        SlopeStatus.SLOPE_OBSERVED,
        SlopeStatus.SLOPE_INSUFFICIENT_DATA,
        SlopeStatus.SLOPE_DEGENERATE_INPUT,
    }
)

TYPED_LOG_LOG_SLOPE_PROTOCOL = ProducerProtocol(
    name="typed_log_log_slope",
    emitted_statuses=SLOPE_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=SlopeStatus,
)

LOG_LOG_SLOPE_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="log_log_slope_consumer",
    accepted_statuses=frozenset({SlopeStatus.SLOPE_OBSERVED}),
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
    status_family=SlopeStatus,
    refused_statuses=SLOPE_STATUSES - frozenset({SlopeStatus.SLOPE_OBSERVED}),
)


@dataclass(frozen=True, slots=True)
class LogLogSlopeObservation:
    slope: float | None
    intercept: float | None
    r_squared: float | None
    standard_error: float | None
    n_input_observations: int
    n_used: int
    log_f_min: float | None
    log_f_max: float | None
    expression_path: str

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe

        return {
            "slope": to_json_safe(self.slope),
            "intercept": to_json_safe(self.intercept),
            "r_squared": to_json_safe(self.r_squared),
            "standard_error": to_json_safe(self.standard_error),
            "n_input_observations": self.n_input_observations,
            "n_used": self.n_used,
            "log_f_min": to_json_safe(self.log_f_min),
            "log_f_max": to_json_safe(self.log_f_max),
            "expression_path": self.expression_path,
        }


LogLogSlopeResult = TypedResult[LogLogSlopeObservation, SlopeStatus]


def typed_log_log_slope(
    observations: TypedCollectionResult,
    *,
    precision: str = "raw_python",
    backend: str = "python",
    device: str = "cpu",
    measurement_resolution: Any | None = None,
    expression_path: str = "ordinary_least_squares",
) -> LogLogSlopeResult:
    _validate_collection(observations)
    items = observations.value.items
    filtered = tuple(item for item in items if item.status is TransferStatus.TRANSFER_OBSERVED)
    n_input = len(items)
    pairs = tuple(_usable_pair(item) for item in filtered)
    pairs = tuple(pair for pair in pairs if pair is not None)
    n_used = len(pairs)

    if n_used < 3:
        return _result(
            SlopeStatus.SLOPE_INSUFFICIENT_DATA,
            _empty_value(n_input, n_used, expression_path),
            observations,
            precision,
            backend,
            device,
            measurement_resolution,
            expression_path,
            (f"n_used={n_used}", "n_used_below_minimum_3"),
        )

    log_f = tuple(math.log(f_value) for f_value, _transfer in pairs)
    log_t = tuple(math.log(abs(transfer)) for _f_value, transfer in pairs)
    log_f_min = min(log_f)
    log_f_max = max(log_f)

    if log_f_max - log_f_min == 0:
        return _degenerate(n_input, n_used, log_f_min, log_f_max, observations, precision, backend, device, measurement_resolution, expression_path, "zero_variance_in_log_f")
    if max(log_t) - min(log_t) == 0:
        return _degenerate(n_input, n_used, log_f_min, log_f_max, observations, precision, backend, device, measurement_resolution, expression_path, "zero_variance_in_log_transfer")

    slope, intercept, r_squared, standard_error = _ordinary_least_squares(log_f, log_t)
    value = LogLogSlopeObservation(
        slope=slope,
        intercept=intercept,
        r_squared=r_squared,
        standard_error=standard_error,
        n_input_observations=n_input,
        n_used=n_used,
        log_f_min=log_f_min,
        log_f_max=log_f_max,
        expression_path=expression_path,
    )
    return _result(
        SlopeStatus.SLOPE_OBSERVED,
        value,
        observations,
        precision,
        backend,
        device,
        measurement_resolution,
        expression_path,
        (f"r_squared={r_squared:.6g}", f"standard_error={standard_error:.3e}", f"n_used={n_used}"),
    )


def _validate_collection(observations: TypedCollectionResult) -> None:
    if not isinstance(observations, TypedResult) or not isinstance(observations.value, TypedCollectionValue):
        raise ProtocolViolationError("typed_log_log_slope requires a typed_collection result")
    for item in observations.value.items:
        if not isinstance(item, TypedResult) or not isinstance(item.status, TransferStatus):
            raise ProtocolViolationError("typed_log_log_slope collection items must be TransferObservationResult instances")


def _usable_pair(observation: TypedResult) -> tuple[float, float] | None:
    if len(observation.provenance.inputs) < 1:
        return None
    f_value = observation.provenance.inputs[0]
    transfer = getattr(observation.value, "transfer", None)
    if isinstance(f_value, bool) or isinstance(transfer, bool):
        return None
    if not isinstance(f_value, int | float) or not isinstance(transfer, int | float):
        return None
    f_float = float(f_value)
    transfer_float = float(transfer)
    if not math.isfinite(f_float) or not math.isfinite(transfer_float):
        return None
    if f_float <= 0 or transfer_float == 0:
        return None
    return f_float, transfer_float


def _ordinary_least_squares(x_values: tuple[float, ...], y_values: tuple[float, ...]) -> tuple[float, float, float, float]:
    n = len(x_values)
    mean_x = sum(x_values) / n
    mean_y = sum(y_values) / n
    sxx = sum((x - mean_x) ** 2 for x in x_values)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, y_values))
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    residuals = tuple(y - (slope * x + intercept) for x, y in zip(x_values, y_values))
    ss_res = sum(residual * residual for residual in residuals)
    ss_tot = sum((y - mean_y) ** 2 for y in y_values)
    r_squared = 1.0 if ss_tot == 0 else 1.0 - ss_res / ss_tot
    standard_error = math.sqrt(ss_res / (n - 2) / sxx)
    return slope, intercept, r_squared, standard_error


def _empty_value(n_input: int, n_used: int, expression_path: str) -> LogLogSlopeObservation:
    return LogLogSlopeObservation(
        slope=None,
        intercept=None,
        r_squared=None,
        standard_error=None,
        n_input_observations=n_input,
        n_used=n_used,
        log_f_min=None,
        log_f_max=None,
        expression_path=expression_path,
    )


def _degenerate(
    n_input: int,
    n_used: int,
    log_f_min: float,
    log_f_max: float,
    observations: TypedCollectionResult,
    precision: str,
    backend: str,
    device: str,
    measurement_resolution: Any | None,
    expression_path: str,
    note: str,
) -> LogLogSlopeResult:
    value = LogLogSlopeObservation(
        slope=None,
        intercept=None,
        r_squared=None,
        standard_error=None,
        n_input_observations=n_input,
        n_used=n_used,
        log_f_min=log_f_min,
        log_f_max=log_f_max,
        expression_path=expression_path,
    )
    return _result(
        SlopeStatus.SLOPE_DEGENERATE_INPUT,
        value,
        observations,
        precision,
        backend,
        device,
        measurement_resolution,
        expression_path,
        (note,),
    )


def _result(
    status: SlopeStatus,
    value: LogLogSlopeObservation,
    observations: TypedCollectionResult,
    precision: str,
    backend: str,
    device: str,
    measurement_resolution: Any | None,
    expression_path: str,
    notes: tuple[str, ...],
) -> LogLogSlopeResult:
    parents = (observations.provenance.trace_id,) + tuple(item.provenance.trace_id for item in observations.value.items)
    return TypedResult(
        value=value,
        space=LOG_LOG_SLOPE_SPACE,
        status=status,
        validity=_validity_for_status(status),
        conditioning=_conditioning_for_status(status, notes),
        provenance=Provenance(
            operation_id="typed_log_log_slope",
            expression_path=expression_path,
            precision=precision,
            backend=backend,
            device=device,
            measurement_resolution=measurement_resolution,
            inputs=(),
            parents=parents,
        ),
        protocol=ProtocolStatus.OK,
    )


def _validity_for_status(status: SlopeStatus) -> Validity:
    if status is SlopeStatus.SLOPE_OBSERVED:
        return Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning_for_status(status: SlopeStatus, notes: tuple[str, ...]) -> Conditioning:
    if status is SlopeStatus.SLOPE_OBSERVED:
        return Conditioning(status=ConditioningStatus.WELL_CONDITIONED, notes=notes)
    return Conditioning(status=ConditioningStatus.WARNING, notes=notes)
