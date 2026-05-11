from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol, validate_protocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import ConditioningStatus, MetrologyStatus, ProtocolStatus
from lloyd_v4.core.transitions import StatusTransitionOutcome, StatusTransitionRule, TransitionDisposition
from lloyd_v4.core.validity import Validity


B_K_NOISE_FLOOR_PROTOCOL = ProducerProtocol(
    name="b_k_noise_floor",
    emitted_statuses=frozenset(
        {
            MetrologyStatus.NOISE_FLOOR_DECLARED,
            MetrologyStatus.NOISE_FLOOR_ESTIMATED,
            MetrologyStatus.NOISE_FLOOR_INDETERMINATE,
        }
    ),
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
)

LIMIT_OF_DETECTION_PROTOCOL = ConsumerProtocol(
    name="limit_of_detection",
    accepted_statuses=B_K_NOISE_FLOOR_PROTOCOL.emitted_statuses,
    required_validity_fields=frozenset({"observable"}),
    scalarization_allowed=False,
)


@dataclass(frozen=True, slots=True)
class NoiseFloorValue:
    label: str
    noise_floor: int | float | None
    method: str
    unit: str | None
    measurement_resolution: int | float | None
    sample_count: int
    observations: tuple[int | float, ...]

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "noise_floor": to_json_safe(self.noise_floor),
            "method": self.method,
            "unit": self.unit,
            "measurement_resolution": to_json_safe(self.measurement_resolution),
            "sample_count": self.sample_count,
            "observations": to_json_safe(self.observations),
        }


@dataclass(frozen=True, slots=True)
class LimitOfDetectionValue:
    observable_label: str
    observable_value: int | float
    absolute_observable: int | float
    noise_floor: int | float | None
    noise_floor_trace_id: str
    comparison: str
    unit: str | None
    identity_evidence: bool

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "observable_label": self.observable_label,
            "observable_value": to_json_safe(self.observable_value),
            "absolute_observable": to_json_safe(self.absolute_observable),
            "noise_floor": to_json_safe(self.noise_floor),
            "noise_floor_trace_id": self.noise_floor_trace_id,
            "comparison": self.comparison,
            "unit": self.unit,
            "identity_evidence": self.identity_evidence,
        }


NoiseFloorResult = TypedResult[NoiseFloorValue, MetrologyStatus]
LimitOfDetectionResult = TypedResult[LimitOfDetectionValue, MetrologyStatus]


def _limit_transition(status, context):
    if status is MetrologyStatus.NOISE_FLOOR_INDETERMINATE:
        output = MetrologyStatus.DETECTION_INDETERMINATE
    else:
        observable = context["observable"]
        floor = context["noise_floor"]
        identity_evidence = context["identity_evidence"]
        if identity_evidence:
            if observable != 0:
                raise ProtocolViolationError("identity evidence requires exact zero observable")
            output = MetrologyStatus.IDENTITY_ZERO
        elif abs(observable) > floor:
            output = MetrologyStatus.DETECTED
        elif abs(observable) == 0 and floor == 0:
            output = MetrologyStatus.DETECTION_INDETERMINATE
        else:
            output = MetrologyStatus.BELOW_LIMIT_OF_DETECTION
    return StatusTransitionOutcome(
        rule_id=LIMIT_OF_DETECTION_TRANSITION_RULE.rule_id,
        input_status=status,
        disposition=TransitionDisposition.MAPPED,
        output_status=output,
    )


LIMIT_OF_DETECTION_TRANSITION_RULE = StatusTransitionRule(
    rule_id="metrology.noise_floor.limit_of_detection",
    input_status_family=MetrologyStatus,
    output_status_family=MetrologyStatus,
    input_protocol_id=B_K_NOISE_FLOOR_PROTOCOL.name,
    output_protocol_id=LIMIT_OF_DETECTION_PROTOCOL.name,
    accepted_input_statuses=frozenset(),
    refused_input_statuses=frozenset(),
    mapped_statuses={
        MetrologyStatus.NOISE_FLOOR_DECLARED: MetrologyStatus.DETECTED,
        MetrologyStatus.NOISE_FLOOR_ESTIMATED: MetrologyStatus.DETECTED,
        MetrologyStatus.NOISE_FLOOR_INDETERMINATE: MetrologyStatus.DETECTION_INDETERMINATE,
    },
    context_keys=("observable", "noise_floor", "identity_evidence"),
    description="Classifies scalar observables against typed b_k noise-floor evidence.",
    emitted_input_statuses=B_K_NOISE_FLOOR_PROTOCOL.emitted_statuses,
    transition=_limit_transition,
)


def declare_bk_noise_floor(
    noise_floor: int | float,
    *,
    label: str = "b_k",
    unit: str | None = None,
    measurement_resolution: int | float | None = None,
) -> TypedResult:
    floor = _require_nonnegative_real(noise_floor, "noise_floor")
    resolution = _require_optional_nonnegative_real(measurement_resolution, "measurement_resolution")
    value = NoiseFloorValue(
        label=label,
        noise_floor=floor,
        method="declared",
        unit=unit,
        measurement_resolution=resolution,
        sample_count=0,
        observations=(),
    )
    return _noise_floor_result(
        value=value,
        status=MetrologyStatus.NOISE_FLOOR_DECLARED,
        operation_id="declare_bk_noise_floor",
        expression_path="declared_bk_noise_floor",
        conditioning=ConditioningStatus.WELL_CONDITIONED,
    )


def estimate_bk_noise_floor(
    observations: Any,
    *,
    label: str = "b_k",
    unit: str | None = None,
    measurement_resolution: int | float | None = None,
    method: str = "max_abs_observed",
) -> TypedResult:
    if method != "max_abs_observed":
        raise ProtocolViolationError("unsupported noise-floor estimation method")
    resolution = _require_optional_nonnegative_real(measurement_resolution, "measurement_resolution")
    observed = tuple(_require_real(item, "observation") for item in observations)
    if not observed:
        value = NoiseFloorValue(label, None, method, unit, resolution, 0, ())
        return _noise_floor_result(
            value=value,
            status=MetrologyStatus.NOISE_FLOOR_INDETERMINATE,
            operation_id="estimate_bk_noise_floor",
            expression_path="max_abs_observed_bk_noise_floor",
            conditioning=ConditioningStatus.WARNING,
        )
    floor = max(abs(item) for item in observed)
    value = NoiseFloorValue(label, floor, method, unit, resolution, len(observed), observed)
    return _noise_floor_result(
        value=value,
        status=MetrologyStatus.NOISE_FLOOR_ESTIMATED,
        operation_id="estimate_bk_noise_floor",
        expression_path="max_abs_observed_bk_noise_floor",
        conditioning=ConditioningStatus.WARNING,
    )


def classify_against_noise_floor(
    observable: int | float,
    noise_floor_result: TypedResult,
    *,
    observable_label: str = "observable",
    identity_evidence: bool = False,
) -> TypedResult:
    observed = _require_real(observable, "observable")
    _require_noise_floor_result(noise_floor_result)
    check = validate_protocol(noise_floor_result, LIMIT_OF_DETECTION_PROTOCOL)
    if not check.ok:
        raise ProtocolViolationError(check.reason)

    floor_value = noise_floor_result.value
    absolute = abs(observed)
    if noise_floor_result.status is MetrologyStatus.NOISE_FLOOR_INDETERMINATE:
        return _lod_result(
            observable_label,
            observed,
            absolute,
            floor_value,
            "indeterminate_floor",
            MetrologyStatus.DETECTION_INDETERMINATE,
            identity_evidence,
            noise_floor_result,
        )

    floor = floor_value.noise_floor
    if identity_evidence:
        if observed != 0:
            raise ProtocolViolationError("identity evidence requires exact zero observable")
        return _lod_result(
            observable_label,
            observed,
            absolute,
            floor_value,
            "identity_zero_evidence",
            MetrologyStatus.IDENTITY_ZERO,
            True,
            noise_floor_result,
        )

    if absolute > floor:
        return _lod_result(
            observable_label,
            observed,
            absolute,
            floor_value,
            "above_limit",
            MetrologyStatus.DETECTED,
            False,
            noise_floor_result,
        )
    if absolute == 0 and floor == 0:
        return _lod_result(
            observable_label,
            observed,
            absolute,
            floor_value,
            "exact_zero_without_identity_evidence",
            MetrologyStatus.DETECTION_INDETERMINATE,
            False,
            noise_floor_result,
        )
    comparison = "on_limit" if absolute == floor else "below_limit"
    return _lod_result(
        observable_label,
        observed,
        absolute,
        floor_value,
        comparison,
        MetrologyStatus.BELOW_LIMIT_OF_DETECTION,
        False,
        noise_floor_result,
    )


def _noise_floor_result(
    *,
    value: NoiseFloorValue,
    status: MetrologyStatus,
    operation_id: str,
    expression_path: str,
    conditioning: ConditioningStatus,
) -> TypedResult:
    return TypedResult(
        value=value,
        space="NoiseFloorEvidence",
        status=status,
        validity=_validity_for_status(status),
        conditioning=Conditioning(status=conditioning),
        provenance=Provenance(
            operation_id=operation_id,
            expression_path=expression_path,
            measurement_resolution=value.measurement_resolution,
        ),
        protocol=ProtocolStatus.OK,
    )


def _lod_result(
    observable_label: str,
    observable: int | float,
    absolute: int | float,
    floor_value: NoiseFloorValue,
    comparison: str,
    status: MetrologyStatus,
    identity_evidence: bool,
    noise_floor_result: TypedResult,
) -> TypedResult:
    value = LimitOfDetectionValue(
        observable_label=observable_label,
        observable_value=observable,
        absolute_observable=absolute,
        noise_floor=floor_value.noise_floor,
        noise_floor_trace_id=noise_floor_result.provenance.trace_id,
        comparison=comparison,
        unit=floor_value.unit,
        identity_evidence=identity_evidence,
    )
    return TypedResult(
        value=value,
        space="LimitOfDetectionEvidence",
        status=status,
        validity=_validity_for_status(status),
        conditioning=_conditioning_for_status(status),
        provenance=Provenance(
            operation_id="classify_against_noise_floor",
            expression_path="limit_of_detection_comparison",
            measurement_resolution=floor_value.measurement_resolution,
            parents=(noise_floor_result.provenance.trace_id,),
        ),
        protocol=ProtocolStatus.OK,
    )


def _validity_for_status(status: MetrologyStatus) -> Validity:
    if status in {
        MetrologyStatus.NOISE_FLOOR_DECLARED,
        MetrologyStatus.NOISE_FLOOR_ESTIMATED,
        MetrologyStatus.DETECTED,
        MetrologyStatus.IDENTITY_ZERO,
    }:
        return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
    if status is MetrologyStatus.BELOW_LIMIT_OF_DETECTION:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    if status is MetrologyStatus.DETECTION_INDETERMINATE:
        return Validity(defined=False, finite=True, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning_for_status(status: MetrologyStatus) -> Conditioning:
    if status in {MetrologyStatus.DETECTED, MetrologyStatus.IDENTITY_ZERO}:
        return Conditioning(status=ConditioningStatus.WELL_CONDITIONED)
    return Conditioning(status=ConditioningStatus.WARNING)


def _require_noise_floor_result(result: TypedResult) -> None:
    if not isinstance(result, TypedResult):
        raise ProtocolViolationError("noise-floor evidence must be a TypedResult")
    if not isinstance(result.value, NoiseFloorValue):
        raise ProtocolViolationError("noise-floor evidence must carry NoiseFloorValue")
    if result.status not in B_K_NOISE_FLOOR_PROTOCOL.emitted_statuses:
        raise ProtocolViolationError("typed result is not noise-floor evidence")


def _require_real(value: Any, name: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ProtocolViolationError(f"{name} must be a finite real scalar")
    if not math.isfinite(value):
        raise ProtocolViolationError(f"{name} must be a finite real scalar")
    return value


def _require_nonnegative_real(value: Any, name: str) -> int | float:
    number = _require_real(value, name)
    if number < 0:
        raise ProtocolViolationError(f"{name} must be nonnegative")
    return number


def _require_optional_nonnegative_real(value: Any | None, name: str) -> int | float | None:
    if value is None:
        return None
    return _require_nonnegative_real(value, name)
