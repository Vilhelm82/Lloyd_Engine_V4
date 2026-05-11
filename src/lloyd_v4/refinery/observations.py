from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from lloyd_v4.branch import (
    BRANCH_FINGERPRINT_PROTOCOL,
    KQ_SLOPE_STABILITY_PROTOCOL,
    SLOPE_FLOW_COMPARISON_PROTOCOL,
    BranchFingerprintValue,
    KqSlopeStabilityValue,
    SlopeFlowComparisonValue,
)
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import BranchFingerprintStatus, MetrologyStatus, ProjectiveRatioStatus, ProjectionStatus, QuadraticRootStatus
from lloyd_v4.metrology import (
    B_K_NOISE_FLOOR_PROTOCOL,
    KQ_PROXY_CALIBRATION_PROTOCOL,
    LIMIT_OF_DETECTION_PROTOCOL,
    VALID_PROXY_CALIBRATION_PROTOCOL,
    LimitOfDetectionValue,
    NoiseFloorValue,
    ProxyCalibrationValue,
    ValidProxyCalibrationValue,
)
from lloyd_v4.primitives.projective_ratio import PROJECTIVE_RATIO_PROTOCOL, ProjectiveRatioValue
from lloyd_v4.primitives.stratified_quadratic_roots import STRATIFIED_QUADRATIC_ROOTS_PROTOCOL, StratifiedQuadraticRootValue
from lloyd_v4.projection.exact_projection import PROJECTION_RESULT_V4_PROTOCOL, ProjectionResultValue


@dataclass(frozen=True, slots=True)
class TypedResultSnapshot:
    label: str
    scenario_id: str
    trace_id: str
    operation_id: str
    expression_path: str
    protocol_identity: str
    status_family: str
    status: str
    validity: dict[str, Any]
    conditioning: dict[str, Any]
    value_fingerprint: dict[str, Any]
    source_trace_ids: tuple[str, ...]

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "scenario_id": self.scenario_id,
            "trace_id": self.trace_id,
            "operation_id": self.operation_id,
            "expression_path": self.expression_path,
            "protocol_identity": self.protocol_identity,
            "status_family": self.status_family,
            "status": self.status,
            "validity": to_json_safe(self.validity),
            "conditioning": to_json_safe(self.conditioning),
            "value_fingerprint": to_json_safe(self.value_fingerprint),
            "source_trace_ids": list(self.source_trace_ids),
        }


@dataclass(frozen=True, slots=True)
class RefineryObservation:
    snapshot: TypedResultSnapshot

    def to_json_safe(self) -> dict[str, Any]:
        return self.snapshot.to_json_safe()


def snapshot_typed_result(
    result: object,
    *,
    label: str,
    scenario_id: str,
) -> TypedResultSnapshot:
    if not isinstance(result, TypedResult):
        raise ProtocolViolationError("refinery observation requires a V4 TypedResult")
    if not isinstance(result.status, Enum):
        raise ProtocolViolationError("refinery observation requires enum status evidence")

    fingerprint = _value_fingerprint(result)
    return TypedResultSnapshot(
        label=label,
        scenario_id=scenario_id,
        trace_id=str(result.provenance.trace_id),
        operation_id=result.provenance.operation_id,
        expression_path=result.provenance.expression_path,
        protocol_identity=_protocol_identity(result),
        status_family=type(result.status).__name__,
        status=result.status.value,
        validity=result.validity.to_json_safe(),
        conditioning=result.conditioning.to_json_safe(),
        value_fingerprint=fingerprint,
        source_trace_ids=_source_trace_ids(result, fingerprint),
    )


def _protocol_identity(result: TypedResult) -> str:
    value = result.value
    status = result.status
    if isinstance(status, ProjectiveRatioStatus) and isinstance(value, ProjectiveRatioValue):
        return PROJECTIVE_RATIO_PROTOCOL.name
    if isinstance(status, QuadraticRootStatus) and isinstance(value, StratifiedQuadraticRootValue):
        return STRATIFIED_QUADRATIC_ROOTS_PROTOCOL.name
    if isinstance(status, ProjectionStatus) and isinstance(value, ProjectionResultValue):
        return PROJECTION_RESULT_V4_PROTOCOL.name
    if isinstance(status, MetrologyStatus):
        if isinstance(value, NoiseFloorValue):
            return B_K_NOISE_FLOOR_PROTOCOL.name
        if isinstance(value, LimitOfDetectionValue):
            return LIMIT_OF_DETECTION_PROTOCOL.name
        if isinstance(value, ProxyCalibrationValue):
            return KQ_PROXY_CALIBRATION_PROTOCOL.name
        if isinstance(value, ValidProxyCalibrationValue):
            return VALID_PROXY_CALIBRATION_PROTOCOL.name
    if isinstance(status, BranchFingerprintStatus):
        if isinstance(value, SlopeFlowComparisonValue):
            return SLOPE_FLOW_COMPARISON_PROTOCOL.name
        if isinstance(value, KqSlopeStabilityValue):
            return KQ_SLOPE_STABILITY_PROTOCOL.name
        if isinstance(value, BranchFingerprintValue):
            return BRANCH_FINGERPRINT_PROTOCOL.name
    return result.provenance.operation_id


def _value_fingerprint(result: TypedResult) -> dict[str, Any]:
    value = result.value
    if isinstance(value, ProjectiveRatioValue):
        return {
            "coordinate_shape": _projective_shape(result.status),
            "numerator_is_zero": value.numerator == 0,
            "denominator_is_zero": value.denominator == 0,
        }
    if isinstance(value, StratifiedQuadraticRootValue):
        return {
            "branch_labels": sorted(value.coordinates),
            "has_discriminant": value.discriminant is not None,
        }
    if isinstance(value, ProjectionResultValue):
        return {
            "source_status": value.source_status,
            "requested_branch": value.requested_branch,
            "selected_branch": value.selected_branch,
            "projection_status": value.projection_status,
            "source_operation_id": value.source_operation_id,
        }
    if isinstance(value, NoiseFloorValue):
        return {
            "metrology_role": "noise_floor",
            "label": value.label,
            "method": value.method,
            "unit": value.unit,
            "sample_count": value.sample_count,
        }
    if isinstance(value, LimitOfDetectionValue):
        return {
            "metrology_role": "limit_of_detection",
            "observable_label": value.observable_label,
            "comparison": value.comparison,
            "unit": value.unit,
            "identity_evidence": value.identity_evidence,
        }
    if isinstance(value, ProxyCalibrationValue):
        return {
            "metrology_role": "proxy_calibration",
            "proxy_label": value.proxy_label,
            "transfer_label": value.transfer_label,
            "frequency_label": value.frequency_label,
            "kq_projective_status": value.kq_projective_status,
            "calibration_reason": value.calibration_reason,
            "proxy_mode": "uncalibrated" if value.kq_scalar_trace_id is None else "calibrated",
        }
    if isinstance(value, ValidProxyCalibrationValue):
        return {
            "metrology_role": "valid_proxy_calibration",
            "proxy_label": value.proxy_label,
            "transfer_label": value.transfer_label,
        }
    if isinstance(value, SlopeFlowComparisonValue):
        return {
            "observable_kind": value.comparison_kind,
            "selected_model_name": value.selected_model_name,
            "model_names": [model.name for model in value.models],
            "max_model_residual": _max_model_residual(value),
        }
    if isinstance(value, KqSlopeStabilityValue):
        return {
            "observable_kind": "proxy",
            "proxy_mode": "kq_flow",
            "stable": value.stable,
            "declared_stability_band": value.declared_stability_band,
            "kq_flow_statuses": list(value.calibration_statuses),
        }
    if isinstance(value, BranchFingerprintValue):
        return {
            "projection_status": value.projection_status,
            "requested_branch": value.requested_branch,
            "selected_branch": value.selected_branch,
            "transfer_flow_status": value.transfer_flow_status,
            "selected_model_name": value.transfer_selected_model_name,
            "observable_kind": value.observable_kind,
            "kq_flow_status": value.kq_flow_status,
            "proxy_mode": "proxy" if value.observable_kind == "proxy" else "direct",
            "fingerprint_components": to_json_safe(value.fingerprint_components),
        }
    return {"value_type": type(value).__name__}


def _projective_shape(status: object) -> str:
    if status is ProjectiveRatioStatus.FINITE_RATIO:
        return "finite"
    if status is ProjectiveRatioStatus.SIGNED_ZERO:
        return "signed_zero"
    if status is ProjectiveRatioStatus.INFINITE_DIRECTION:
        return "infinite_direction"
    return "indeterminate"


def _max_model_residual(value: SlopeFlowComparisonValue) -> float | None:
    residuals = [
        residual.max_abs_segment_residual
        for residual in value.model_residuals
        if residual.max_abs_segment_residual is not None
    ]
    return max(residuals) if residuals else None


def _source_trace_ids(result: TypedResult, fingerprint: dict[str, Any]) -> tuple[str, ...]:
    ids: list[str] = list(result.provenance.parents)
    value = result.value
    if isinstance(value, ProjectionResultValue):
        ids.extend(item for item in (value.source_trace_id, value.selected_root_trace_id) if item is not None)
    elif isinstance(value, LimitOfDetectionValue):
        ids.append(value.noise_floor_trace_id)
    elif isinstance(value, ProxyCalibrationValue):
        ids.extend(
            item
            for item in (value.kq_projective_trace_id, value.kq_scalar_trace_id)
            if item is not None
        )
    elif isinstance(value, ValidProxyCalibrationValue):
        ids.append(value.parent_calibration_trace_id)
    elif isinstance(value, SlopeFlowComparisonValue):
        ids.extend(value.source_trace_ids)
    elif isinstance(value, KqSlopeStabilityValue):
        ids.extend(value.calibration_trace_ids)
        if value.slope_flow_trace_id is not None:
            ids.append(value.slope_flow_trace_id)
    elif isinstance(value, BranchFingerprintValue):
        ids.extend(value.source_trace_ids)
    return tuple(dict.fromkeys(ids))
