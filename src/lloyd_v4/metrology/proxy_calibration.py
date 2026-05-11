from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol, validate_protocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedRefusal, TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import MetrologyStatus, ProjectiveRatioStatus, ProtocolStatus, ConditioningStatus
from lloyd_v4.core.transitions import StatusTransitionRule
from lloyd_v4.core.validity import Validity
from lloyd_v4.primitives.projective_ratio import projective_ratio, scalarize_projective_ratio


KQ_PROXY_CALIBRATION_PROTOCOL = ProducerProtocol(
    name="kq_proxy_calibration",
    emitted_statuses=frozenset(
        {
            MetrologyStatus.CALIBRATION_VALID,
            MetrologyStatus.CALIBRATION_INVALID,
            MetrologyStatus.CALIBRATION_INDETERMINATE,
            MetrologyStatus.PROXY_UNCALIBRATED,
        }
    ),
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
)

VALID_PROXY_CALIBRATION_PROTOCOL = ConsumerProtocol(
    name="valid_proxy_calibration",
    accepted_statuses=frozenset({MetrologyStatus.CALIBRATION_VALID}),
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
)


@dataclass(frozen=True, slots=True)
class ProxyCalibrationValue:
    proxy_label: str
    transfer_label: str
    proxy_observable: int | float | None
    transfer_observable: int | float | None
    frequency_label: str | None
    kq_projective_coordinates: dict[str, Any] | None
    kq_projective_trace_id: str | None
    kq_projective_status: str | None
    kq_scalar_value: int | float | None
    kq_scalar_trace_id: str | None
    calibration_reason: str
    refusal_evidence: dict[str, Any] | None
    reason: str | None = None

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "proxy_label": self.proxy_label,
            "transfer_label": self.transfer_label,
            "proxy_observable": to_json_safe(self.proxy_observable),
            "transfer_observable": to_json_safe(self.transfer_observable),
            "frequency_label": self.frequency_label,
            "kq_projective_coordinates": to_json_safe(self.kq_projective_coordinates),
            "kq_projective_trace_id": self.kq_projective_trace_id,
            "kq_projective_status": self.kq_projective_status,
            "kq_scalar_value": to_json_safe(self.kq_scalar_value),
            "kq_scalar_trace_id": self.kq_scalar_trace_id,
            "calibration_reason": self.calibration_reason,
            "refusal_evidence": to_json_safe(self.refusal_evidence),
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class ValidProxyCalibrationValue:
    parent_calibration_trace_id: str
    kq_scalar_value: int | float
    proxy_label: str
    transfer_label: str

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "parent_calibration_trace_id": self.parent_calibration_trace_id,
            "kq_scalar_value": to_json_safe(self.kq_scalar_value),
            "proxy_label": self.proxy_label,
            "transfer_label": self.transfer_label,
        }


ProxyCalibrationResult = TypedResult[ProxyCalibrationValue, MetrologyStatus]

VALID_PROXY_CALIBRATION_TRANSITION_RULE = StatusTransitionRule(
    rule_id="metrology.proxy_calibration.require_valid",
    input_status_family=MetrologyStatus,
    output_status_family=None,
    input_protocol_id=KQ_PROXY_CALIBRATION_PROTOCOL.name,
    output_protocol_id=VALID_PROXY_CALIBRATION_PROTOCOL.name,
    accepted_input_statuses=frozenset({MetrologyStatus.CALIBRATION_VALID}),
    refused_input_statuses=frozenset(
        {
            MetrologyStatus.CALIBRATION_INVALID,
            MetrologyStatus.CALIBRATION_INDETERMINATE,
            MetrologyStatus.PROXY_UNCALIBRATED,
        }
    ),
    mapped_statuses={},
    description="Requires pointwise valid Kq proxy calibration evidence.",
    emitted_input_statuses=KQ_PROXY_CALIBRATION_PROTOCOL.emitted_statuses,
)


def calibrate_proxy_kq(
    proxy_observable: int | float,
    transfer_observable: int | float,
    *,
    proxy_label: str = "Y_q",
    transfer_label: str = "T",
    frequency_label: str | None = None,
) -> TypedResult:
    proxy = _require_real(proxy_observable, "proxy_observable")
    transfer = _require_real(transfer_observable, "transfer_observable")
    kq_projective = projective_ratio(proxy, transfer)
    kq_scalar = scalarize_projective_ratio(kq_projective)
    status, reason = _calibration_status(kq_projective.status)
    scalar_value = kq_scalar.value if status is MetrologyStatus.CALIBRATION_VALID else None
    scalar_trace = kq_scalar.provenance.trace_id if kq_scalar.refusal is None else None
    refusal_evidence = None if kq_scalar.refusal is None else kq_scalar.refusal.to_json_safe()
    value = ProxyCalibrationValue(
        proxy_label=proxy_label,
        transfer_label=transfer_label,
        proxy_observable=proxy,
        transfer_observable=transfer,
        frequency_label=frequency_label,
        kq_projective_coordinates=kq_projective.value.to_json_safe(),
        kq_projective_trace_id=kq_projective.provenance.trace_id,
        kq_projective_status=kq_projective.status.value,
        kq_scalar_value=scalar_value,
        kq_scalar_trace_id=scalar_trace,
        calibration_reason=reason,
        refusal_evidence=refusal_evidence,
    )
    parents = (kq_projective.provenance.trace_id,) if scalar_trace is None else (kq_projective.provenance.trace_id, scalar_trace)
    return TypedResult(
        value=value,
        space="ProxyCalibrationEvidence",
        status=status,
        validity=_validity_for_status(status),
        conditioning=_conditioning_for_status(status),
        provenance=Provenance(
            operation_id="calibrate_proxy_kq",
            expression_path="projective_ratio_kq_calibration",
            parents=parents,
        ),
        protocol=ProtocolStatus.OK,
    )


def proxy_uncalibrated(
    *,
    proxy_label: str = "Y_q",
    reason: str = "missing_calibration_evidence",
) -> TypedResult:
    value = ProxyCalibrationValue(
        proxy_label=proxy_label,
        transfer_label="T",
        proxy_observable=None,
        transfer_observable=None,
        frequency_label=None,
        kq_projective_coordinates=None,
        kq_projective_trace_id=None,
        kq_projective_status=None,
        kq_scalar_value=None,
        kq_scalar_trace_id=None,
        calibration_reason="proxy_uncalibrated",
        refusal_evidence=None,
        reason=reason,
    )
    return TypedResult(
        value=value,
        space="ProxyCalibrationEvidence",
        status=MetrologyStatus.PROXY_UNCALIBRATED,
        validity=_validity_for_status(MetrologyStatus.PROXY_UNCALIBRATED),
        conditioning=_conditioning_for_status(MetrologyStatus.PROXY_UNCALIBRATED),
        provenance=Provenance(operation_id="proxy_uncalibrated", expression_path="missing_proxy_calibration_evidence"),
        protocol=ProtocolStatus.OK,
    )


def require_valid_proxy_calibration(calibration_result: TypedResult) -> TypedResult:
    _require_calibration_result(calibration_result)
    check = validate_protocol(calibration_result, VALID_PROXY_CALIBRATION_PROTOCOL)
    if check.ok:
        value = ValidProxyCalibrationValue(
            parent_calibration_trace_id=calibration_result.provenance.trace_id,
            kq_scalar_value=calibration_result.value.kq_scalar_value,
            proxy_label=calibration_result.value.proxy_label,
            transfer_label=calibration_result.value.transfer_label,
        )
        return TypedResult(
            value=value,
            space="ValidProxyCalibration",
            status=MetrologyStatus.CALIBRATION_VALID,
            validity=_validity_for_status(MetrologyStatus.CALIBRATION_VALID),
            conditioning=Conditioning(status=ConditioningStatus.WELL_CONDITIONED),
            provenance=Provenance(
                operation_id="require_valid_proxy_calibration",
                expression_path="valid_proxy_calibration_protocol",
                parents=(calibration_result.provenance.trace_id,),
            ),
            protocol=ProtocolStatus.OK,
        )
    refusal = TypedRefusal(
        reason=f"valid proxy calibration required: {check.reason}",
        status=ProtocolStatus.SCALARIZATION_REFUSED,
        details={"calibration_status": calibration_result.status.value, "protocol_reason": check.reason},
    )
    return TypedResult(
        value=None,
        space="ValidProxyCalibration",
        status=calibration_result.status,
        validity=Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True),
        conditioning=_conditioning_for_status(calibration_result.status),
        provenance=Provenance(
            operation_id="require_valid_proxy_calibration",
            expression_path="valid_proxy_calibration_refusal",
            parents=(calibration_result.provenance.trace_id,),
        ),
        protocol=ProtocolStatus.SCALARIZATION_REFUSED,
        refusal=refusal,
    )


def _calibration_status(status: ProjectiveRatioStatus) -> tuple[MetrologyStatus, str]:
    if status is ProjectiveRatioStatus.FINITE_RATIO:
        return MetrologyStatus.CALIBRATION_VALID, "finite_nonzero_kq"
    if status is ProjectiveRatioStatus.SIGNED_ZERO:
        return MetrologyStatus.CALIBRATION_INVALID, "zero_proxy_against_nonzero_transfer"
    if status is ProjectiveRatioStatus.INFINITE_DIRECTION:
        return MetrologyStatus.CALIBRATION_INVALID, "nonzero_proxy_against_zero_transfer"
    return MetrologyStatus.CALIBRATION_INDETERMINATE, "zero_proxy_against_zero_transfer"


def _validity_for_status(status: MetrologyStatus) -> Validity:
    if status is MetrologyStatus.CALIBRATION_VALID:
        return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
    if status is MetrologyStatus.CALIBRATION_INVALID:
        return Validity(defined=True, finite=False, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning_for_status(status: MetrologyStatus) -> Conditioning:
    if status is MetrologyStatus.CALIBRATION_VALID:
        return Conditioning(status=ConditioningStatus.WELL_CONDITIONED)
    return Conditioning(status=ConditioningStatus.WARNING)


def _require_calibration_result(result: TypedResult) -> None:
    if not isinstance(result, TypedResult):
        raise ProtocolViolationError("calibration evidence must be a TypedResult")
    if not isinstance(result.value, ProxyCalibrationValue):
        raise ProtocolViolationError("calibration evidence must carry ProxyCalibrationValue")
    if result.status not in KQ_PROXY_CALIBRATION_PROTOCOL.emitted_statuses:
        raise ProtocolViolationError("typed result is not proxy calibration evidence")


def _require_real(value: Any, name: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ProtocolViolationError(f"{name} must be a finite real scalar")
    if not math.isfinite(value):
        raise ProtocolViolationError(f"{name} must be a finite real scalar")
    return value
