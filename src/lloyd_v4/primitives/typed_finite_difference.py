from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.status import ConditioningStatus, ProtocolStatus, TransferStatus
from lloyd_v4.core.validity import Validity


TRANSFER_SPACE = "TransferObservation"
TRANSFER_STATUSES = frozenset(
    {
        TransferStatus.TRANSFER_OBSERVED,
        TransferStatus.TRANSFER_CANCELLATION_DOMINATED,
        TransferStatus.TRANSFER_NON_FINITE,
        TransferStatus.TRANSFER_DOMAIN_REFUSED,
        TransferStatus.TRANSFER_DELTA_INDETERMINATE,
    }
)

TYPED_FINITE_DIFFERENCE_PROTOCOL = ProducerProtocol(
    name="typed_finite_difference",
    emitted_statuses=TRANSFER_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=TransferStatus,
)

TRANSFER_OBSERVATION_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="transfer_observation_consumer",
    accepted_statuses=frozenset({TransferStatus.TRANSFER_OBSERVED}),
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
    status_family=TransferStatus,
    refused_statuses=TRANSFER_STATUSES - frozenset({TransferStatus.TRANSFER_OBSERVED}),
)


@dataclass(frozen=True, slots=True)
class TransferObservation:
    transfer: float | None
    g_at_f: float | None
    g_at_f_plus_delta: float | None
    delta_g: float | None
    cancellation_ratio: float | None

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe

        return {
            "transfer": to_json_safe(self.transfer),
            "g_at_f": to_json_safe(self.g_at_f),
            "g_at_f_plus_delta": to_json_safe(self.g_at_f_plus_delta),
            "delta_g": to_json_safe(self.delta_g),
            "cancellation_ratio": to_json_safe(self.cancellation_ratio),
        }


TransferObservationResult = TypedResult[TransferObservation, TransferStatus]


def typed_finite_difference(
    g_callable: Callable[[float], float],
    f: float,
    delta_f: float,
    *,
    function_label: str,
    precision: str = "raw_python",
    backend: str = "python",
    device: str = "cpu",
    measurement_resolution: Any | None = None,
    expression_path: str = "forward_difference",
) -> TransferObservationResult:
    _validate_inputs(g_callable, f, delta_f, function_label)
    precision_floor = _precision_floor(precision)

    if delta_f == 0:
        return _result(
            TransferStatus.TRANSFER_DELTA_INDETERMINATE,
            TransferObservation(None, None, None, None, None),
            f,
            delta_f,
            function_label,
            precision,
            backend,
            device,
            measurement_resolution,
            expression_path,
            ("delta_f_is_zero",),
        )

    g_f: float | None = None
    g_f_plus: float | None = None
    try:
        raw_g_f = g_callable(f)
        if not _is_numeric(raw_g_f):
            return _domain_refused(
                None,
                None,
                f,
                delta_f,
                function_label,
                precision,
                backend,
                device,
                measurement_resolution,
                expression_path,
                f"non_numeric_return:g_at_f:{type(raw_g_f).__name__}",
            )
        g_f = float(raw_g_f)
        raw_g_f_plus = g_callable(f + delta_f)
        if not _is_numeric(raw_g_f_plus):
            return _domain_refused(
                g_f,
                None,
                f,
                delta_f,
                function_label,
                precision,
                backend,
                device,
                measurement_resolution,
                expression_path,
                f"non_numeric_return:g_at_f_plus_delta:{type(raw_g_f_plus).__name__}",
            )
        g_f_plus = float(raw_g_f_plus)
    except Exception as exc:
        return _domain_refused(
            g_f,
            g_f_plus,
            f,
            delta_f,
            function_label,
            precision,
            backend,
            device,
            measurement_resolution,
            expression_path,
            f"exception:{type(exc).__name__}",
        )

    delta_g = g_f_plus - g_f
    transfer = delta_g / delta_f
    if not math.isfinite(g_f):
        return _non_finite(g_f, g_f_plus, delta_g, transfer, "g_at_f", f, delta_f, function_label, precision, backend, device, measurement_resolution, expression_path)
    if not math.isfinite(g_f_plus):
        return _non_finite(g_f, g_f_plus, delta_g, transfer, "g_at_f_plus_delta", f, delta_f, function_label, precision, backend, device, measurement_resolution, expression_path)
    if not math.isfinite(transfer):
        return _non_finite(g_f, g_f_plus, delta_g, transfer, "transfer", f, delta_f, function_label, precision, backend, device, measurement_resolution, expression_path)

    max_g = max(abs(g_f), abs(g_f_plus))
    if max_g == 0:
        return _result(
            TransferStatus.TRANSFER_OBSERVED,
            TransferObservation(transfer, g_f, g_f_plus, delta_g, None),
            f,
            delta_f,
            function_label,
            precision,
            backend,
            device,
            measurement_resolution,
            expression_path,
            (),
        )

    cancellation_ratio = abs(delta_g) / max_g
    if cancellation_ratio < precision_floor:
        return _result(
            TransferStatus.TRANSFER_CANCELLATION_DOMINATED,
            TransferObservation(transfer, g_f, g_f_plus, delta_g, cancellation_ratio),
            f,
            delta_f,
            function_label,
            precision,
            backend,
            device,
            measurement_resolution,
            expression_path,
            (f"cancellation_ratio={cancellation_ratio:.3e}", f"precision_floor={precision_floor:.3e}"),
        )

    return _result(
        TransferStatus.TRANSFER_OBSERVED,
        TransferObservation(transfer, g_f, g_f_plus, delta_g, cancellation_ratio),
        f,
        delta_f,
        function_label,
        precision,
        backend,
        device,
        measurement_resolution,
        expression_path,
        (),
    )


def _validate_inputs(g_callable: Callable[[float], float], f: float, delta_f: float, function_label: str) -> None:
    if not callable(g_callable):
        raise ProtocolViolationError("g_callable must be callable")
    if isinstance(f, bool) or not isinstance(f, int | float) or not math.isfinite(f):
        raise ProtocolViolationError("f must be a finite real scalar")
    if isinstance(delta_f, bool) or not isinstance(delta_f, int | float) or not math.isfinite(delta_f):
        raise ProtocolViolationError("delta_f must be a finite real scalar")
    if not isinstance(function_label, str) or function_label == "":
        raise ProtocolViolationError("function_label must be a non-empty string")


def _precision_floor(precision: str) -> float:
    if precision == "raw_python":
        # raw_python uses IEEE 754 double under round-to-nearest.
        # Per-operand unit roundoff: u = 2^-53.
        # For forward finite difference delta_g = g(f+delta_f) - g(f),
        # worst-case absolute round-off in delta_g is approximately
        # 2u * max(|g_f|, |g_f_plus|). The relative cancellation ratio
        # |delta_g| / max(|g_f|, |g_f_plus|) is classifiable as
        # round-off-dominated below 2u = 2^-52, which also equals
        # sys.float_info.epsilon (relative spacing of floats at 1.0).
        # Status-only: this floor never alters the computed transfer value;
        # it only classifies the stratum. See METROLOGY_PRINCIPLES.md and
        # Axiom 3 (no hidden guard rails).
        return 2.0**-52
    raise ProtocolViolationError(f"unsupported precision {precision!r}; raw_python is the only currently-supported value")


def _is_numeric(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, int | float)


def _domain_refused(
    g_f: float | None,
    g_f_plus: float | None,
    f: float,
    delta_f: float,
    function_label: str,
    precision: str,
    backend: str,
    device: str,
    measurement_resolution: Any | None,
    expression_path: str,
    note: str,
) -> TransferObservationResult:
    return _result(
        TransferStatus.TRANSFER_DOMAIN_REFUSED,
        TransferObservation(None, g_f, g_f_plus, None, None),
        f,
        delta_f,
        function_label,
        precision,
        backend,
        device,
        measurement_resolution,
        expression_path,
        (note,),
    )


def _non_finite(
    g_f: float | None,
    g_f_plus: float | None,
    delta_g: float | None,
    transfer: float | None,
    which: str,
    f: float,
    delta_f: float,
    function_label: str,
    precision: str,
    backend: str,
    device: str,
    measurement_resolution: Any | None,
    expression_path: str,
) -> TransferObservationResult:
    return _result(
        TransferStatus.TRANSFER_NON_FINITE,
        TransferObservation(transfer, g_f, g_f_plus, delta_g, None),
        f,
        delta_f,
        function_label,
        precision,
        backend,
        device,
        measurement_resolution,
        expression_path,
        (f"non_finite_endpoint:{which}",),
    )


def _result(
    status: TransferStatus,
    value: TransferObservation,
    f: float,
    delta_f: float,
    function_label: str,
    precision: str,
    backend: str,
    device: str,
    measurement_resolution: Any | None,
    expression_path: str,
    notes: tuple[str, ...],
) -> TransferObservationResult:
    return TypedResult(
        value=value,
        space=TRANSFER_SPACE,
        status=status,
        validity=_validity_for_status(status),
        conditioning=_conditioning_for_status(status, notes),
        provenance=Provenance(
            operation_id="typed_finite_difference",
            expression_path=expression_path,
            precision=precision,
            backend=backend,
            device=device,
            measurement_resolution=measurement_resolution,
            inputs=(f, delta_f, function_label),
            parents=(),
        ),
        protocol=ProtocolStatus.OK,
    )


def _validity_for_status(status: TransferStatus) -> Validity:
    if status is TransferStatus.TRANSFER_OBSERVED:
        return Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True)
    if status is TransferStatus.TRANSFER_CANCELLATION_DOMINATED:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    if status is TransferStatus.TRANSFER_NON_FINITE:
        return Validity(defined=True, finite=False, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning_for_status(status: TransferStatus, notes: tuple[str, ...]) -> Conditioning:
    if status is TransferStatus.TRANSFER_OBSERVED:
        return Conditioning(status=ConditioningStatus.WELL_CONDITIONED, notes=notes)
    return Conditioning(status=ConditioningStatus.WARNING, notes=notes)
