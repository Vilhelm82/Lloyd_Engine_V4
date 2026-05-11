from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

from lloyd_v4.branch.slope_flow import (
    SLOPE_FLOW_STATUSES,
    SlopeFlowComparisonValue,
    SlopeFlowComparisonResult,
    compare_slope_flow_to_models,
)
from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol, validate_protocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import BranchFingerprintStatus, ConditioningStatus, ProjectionStatus, ProtocolStatus
from lloyd_v4.core.transitions import StatusTransitionOutcome, StatusTransitionRule, TransitionDisposition, apply_status_transition
from lloyd_v4.core.validity import Validity
from lloyd_v4.metrology import ProxyCalibrationResult, require_valid_proxy_calibration
from lloyd_v4.projection.exact_projection import ProjectionResultV4


KQ_FLOW_STATUSES = frozenset(
    {
        BranchFingerprintStatus.KQ_FLOW_STABLE,
        BranchFingerprintStatus.KQ_FLOW_UNSTABLE,
        BranchFingerprintStatus.KQ_FLOW_INDETERMINATE,
        BranchFingerprintStatus.KQ_FLOW_UNCALIBRATED,
    }
)
FINGERPRINT_STATUSES = frozenset(
    {
        BranchFingerprintStatus.FINGERPRINT_COMPLETE,
        BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED,
        BranchFingerprintStatus.FINGERPRINT_INCOMPLETE,
        BranchFingerprintStatus.FINGERPRINT_PROXY_UNCALIBRATED,
    }
)

KQ_SLOPE_STABILITY_PROTOCOL = ProducerProtocol(
    name="kq_slope_stability",
    emitted_statuses=KQ_FLOW_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
)
BRANCH_FINGERPRINT_PROTOCOL = ProducerProtocol(
    name="branch_fingerprint",
    emitted_statuses=FINGERPRINT_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
)
BRANCH_FINGERPRINT_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="branch_fingerprint_consumer",
    accepted_statuses=FINGERPRINT_STATUSES,
    required_validity_fields=frozenset({"observable"}),
)


def _kq_transition(status, context):
    return StatusTransitionOutcome(
        KQ_FLOW_REQUIRE_STABLE_TRANSITION_RULE.rule_id,
        status,
        TransitionDisposition.ACCEPTED if status is BranchFingerprintStatus.KQ_FLOW_STABLE else TransitionDisposition.REFUSED,
    )


KQ_FLOW_REQUIRE_STABLE_TRANSITION_RULE = StatusTransitionRule(
    rule_id="branch.kq_flow.require_stable",
    input_status_family=BranchFingerprintStatus,
    output_status_family=None,
    input_protocol_id=KQ_SLOPE_STABILITY_PROTOCOL.name,
    output_protocol_id="branch.kq_flow.require_stable",
    accepted_input_statuses=frozenset({BranchFingerprintStatus.KQ_FLOW_STABLE}),
    refused_input_statuses=frozenset(
        {
            BranchFingerprintStatus.KQ_FLOW_UNSTABLE,
            BranchFingerprintStatus.KQ_FLOW_INDETERMINATE,
            BranchFingerprintStatus.KQ_FLOW_UNCALIBRATED,
        }
    ),
    mapped_statuses={},
    emitted_input_statuses=KQ_FLOW_STATUSES,
    transition=_kq_transition,
)

PROJECTION_TO_FINGERPRINT_TRANSITION_RULE = StatusTransitionRule(
    rule_id="branch.projection_to_fingerprint",
    input_status_family=ProjectionStatus,
    output_status_family=BranchFingerprintStatus,
    input_protocol_id="projection_result_v4",
    output_protocol_id=BRANCH_FINGERPRINT_PROTOCOL.name,
    accepted_input_statuses=frozenset(
        {
            ProjectionStatus.PROJECTION_TRANSVERSE,
            ProjectionStatus.PROJECTION_TANGENT_CONTACT,
            ProjectionStatus.PROJECTION_LINEAR,
        }
    ),
    refused_input_statuses=frozenset(
        {
            ProjectionStatus.PROJECTION_NO_REAL_ROOT,
            ProjectionStatus.PROJECTION_IDENTITY,
            ProjectionStatus.PROJECTION_NO_SOLUTION,
            ProjectionStatus.PROJECTION_SELECTION_REFUSED,
        }
    ),
    mapped_statuses={},
    emitted_input_statuses=frozenset(ProjectionStatus),
)

TRANSFER_FLOW_TO_FINGERPRINT_TRANSITION_RULE = StatusTransitionRule(
    rule_id="branch.transfer_flow_to_fingerprint",
    input_status_family=BranchFingerprintStatus,
    output_status_family=BranchFingerprintStatus,
    input_protocol_id="slope_flow_comparison",
    output_protocol_id=BRANCH_FINGERPRINT_PROTOCOL.name,
    accepted_input_statuses=frozenset(
        {
            BranchFingerprintStatus.SLOPE_FLOW_OBSERVED,
            BranchFingerprintStatus.SLOPE_MODEL_RESIDUALS,
            BranchFingerprintStatus.SLOPE_MODEL_UNIQUE_MATCH,
        }
    ),
    refused_input_statuses=frozenset(
        {
            BranchFingerprintStatus.SLOPE_FLOW_INSUFFICIENT_SAMPLES,
            BranchFingerprintStatus.SLOPE_FLOW_INDETERMINATE,
            BranchFingerprintStatus.SLOPE_FLOW_PROXY_UNCALIBRATED,
        }
    ),
    mapped_statuses={
        BranchFingerprintStatus.SLOPE_MODEL_AMBIGUOUS: BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED,
        BranchFingerprintStatus.SLOPE_MODEL_NO_MATCH: BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED,
    },
    emitted_input_statuses=SLOPE_FLOW_STATUSES,
)

BRANCH_COMPOSE_FINGERPRINT_TRANSITION_RULE = StatusTransitionRule(
    rule_id="branch.compose_fingerprint",
    input_status_family=BranchFingerprintStatus,
    output_status_family=BranchFingerprintStatus,
    input_protocol_id=BRANCH_FINGERPRINT_PROTOCOL.name,
    output_protocol_id=BRANCH_FINGERPRINT_CONSUMER_PROTOCOL.name,
    accepted_input_statuses=FINGERPRINT_STATUSES,
    refused_input_statuses=frozenset(),
    mapped_statuses={},
    emitted_input_statuses=FINGERPRINT_STATUSES,
)


@dataclass(frozen=True, slots=True)
class KqSlopeStabilityValue:
    control_values: tuple[float, ...]
    calibration_trace_ids: tuple[str, ...]
    calibration_statuses: tuple[str, ...]
    kq_values: tuple[float | None, ...]
    slope_flow_trace_id: str | None
    declared_stability_band: float | None
    stable: bool | None
    refusal_reasons: tuple[str, ...]

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "control_values": to_json_safe(self.control_values),
            "calibration_trace_ids": list(self.calibration_trace_ids),
            "calibration_statuses": list(self.calibration_statuses),
            "kq_values": to_json_safe(self.kq_values),
            "slope_flow_trace_id": self.slope_flow_trace_id,
            "declared_stability_band": to_json_safe(self.declared_stability_band),
            "stable": self.stable,
            "refusal_reasons": list(self.refusal_reasons),
        }


@dataclass(frozen=True, slots=True)
class BranchFingerprintValue:
    projection_trace_id: str
    projection_status: str
    requested_branch: str | None
    selected_branch: str | None
    transfer_flow_trace_id: str
    transfer_flow_status: str
    transfer_selected_model_name: str | None
    observable_kind: str
    kq_flow_trace_id: str | None
    kq_flow_status: str | None
    fingerprint_components: dict[str, object]
    source_trace_ids: tuple[str, ...]

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "projection_trace_id": self.projection_trace_id,
            "projection_status": self.projection_status,
            "requested_branch": self.requested_branch,
            "selected_branch": self.selected_branch,
            "transfer_flow_trace_id": self.transfer_flow_trace_id,
            "transfer_flow_status": self.transfer_flow_status,
            "transfer_selected_model_name": self.transfer_selected_model_name,
            "observable_kind": self.observable_kind,
            "kq_flow_trace_id": self.kq_flow_trace_id,
            "kq_flow_status": self.kq_flow_status,
            "fingerprint_components": to_json_safe(self.fingerprint_components),
            "source_trace_ids": list(self.source_trace_ids),
        }


KqSlopeStabilityResult = TypedResult[KqSlopeStabilityValue, BranchFingerprintStatus]
BranchFingerprintResult = TypedResult[BranchFingerprintValue, BranchFingerprintStatus]


def compare_kq_slope_stability(
    control_values: Sequence[int | float],
    calibration_results: Sequence[ProxyCalibrationResult],
    *,
    declared_stability_band: float | None,
) -> TypedResult:
    controls = tuple(_positive(value, "control") for value in control_values)
    calibrations = tuple(calibration_results)
    band = _optional_nonnegative(declared_stability_band, "declared_stability_band")
    if len(controls) != len(calibrations):
        raise ProtocolViolationError("control values and calibration results must have the same length")

    statuses = []
    traces = []
    values = []
    refusals = []
    for calibration in calibrations:
        accepted = require_valid_proxy_calibration(calibration)
        traces.append(calibration.provenance.trace_id)
        statuses.append(calibration.status.value)
        if accepted.refusal is not None:
            refusals.append(accepted.refusal.reason)
            values.append(None)
        else:
            values.append(accepted.value.kq_scalar_value)
    if refusals:
        return _kq_result(controls, tuple(traces), tuple(statuses), tuple(values), None, band, None, tuple(refusals), BranchFingerprintStatus.KQ_FLOW_UNCALIBRATED)
    if len(controls) < 2 or band is None:
        return _kq_result(controls, tuple(traces), tuple(statuses), tuple(values), None, band, None, (), BranchFingerprintStatus.KQ_FLOW_INDETERMINATE)

    samples = tuple(
        __import__("lloyd_v4.branch.slope_flow", fromlist=["SlopeFlowSample"]).SlopeFlowSample(control, value, source_trace_id=trace)
        for control, value, trace in zip(controls, values, traces)
    )
    flow = compare_slope_flow_to_models(samples, comparison_kind="kq_stability")
    if flow.status not in {
        BranchFingerprintStatus.SLOPE_FLOW_OBSERVED,
        BranchFingerprintStatus.SLOPE_MODEL_RESIDUALS,
        BranchFingerprintStatus.SLOPE_MODEL_UNIQUE_MATCH,
    }:
        return _kq_result(controls, tuple(traces), tuple(statuses), tuple(values), flow.provenance.trace_id, band, None, (), BranchFingerprintStatus.KQ_FLOW_INDETERMINATE)
    stable = all(abs(segment.slope) <= band for segment in flow.value.segment_evidence if segment.slope is not None)
    status = BranchFingerprintStatus.KQ_FLOW_STABLE if stable else BranchFingerprintStatus.KQ_FLOW_UNSTABLE
    return _kq_result(controls, tuple(traces), tuple(statuses), tuple(values), flow.provenance.trace_id, band, stable, (), status)


def build_branch_fingerprint(
    projection_result: ProjectionResultV4,
    transfer_flow_result: SlopeFlowComparisonResult,
    *,
    observable_kind: str = "direct_transfer",
    kq_flow_result: KqSlopeStabilityResult | None = None,
) -> TypedResult:
    if observable_kind not in {"direct_transfer", "proxy"}:
        raise ProtocolViolationError("observable_kind must be direct_transfer or proxy")
    projection_check = apply_status_transition(PROJECTION_TO_FINGERPRINT_TRANSITION_RULE, projection_result.status)
    transfer_check = apply_status_transition(TRANSFER_FLOW_TO_FINGERPRINT_TRANSITION_RULE, transfer_flow_result.status)
    status = _fingerprint_status(projection_check, transfer_check, observable_kind, kq_flow_result)
    value = BranchFingerprintValue(
        projection_trace_id=projection_result.provenance.trace_id,
        projection_status=projection_result.status.value,
        requested_branch=projection_result.value.requested_branch,
        selected_branch=projection_result.value.selected_branch,
        transfer_flow_trace_id=transfer_flow_result.provenance.trace_id,
        transfer_flow_status=transfer_flow_result.status.value,
        transfer_selected_model_name=transfer_flow_result.value.selected_model_name,
        observable_kind=observable_kind,
        kq_flow_trace_id=None if kq_flow_result is None else kq_flow_result.provenance.trace_id,
        kq_flow_status=None if kq_flow_result is None else kq_flow_result.status.value,
        fingerprint_components={
            "projection": projection_result.status.value,
            "transfer": transfer_flow_result.status.value,
            "kq": None if kq_flow_result is None else kq_flow_result.status.value,
        },
        source_trace_ids=_source_ids(projection_result, transfer_flow_result, kq_flow_result),
    )
    return TypedResult(
        value=value,
        space="BranchFingerprint",
        status=status,
        validity=_fingerprint_validity(status),
        conditioning=_fingerprint_conditioning(status),
        provenance=Provenance(
            operation_id="build_branch_fingerprint",
            expression_path="named_transition_branch_fingerprint",
            parents=value.source_trace_ids,
        ),
        protocol=ProtocolStatus.OK,
    )


def _fingerprint_status(projection_check, transfer_check, observable_kind, kq_flow_result):
    if projection_check.disposition is TransitionDisposition.REFUSED or transfer_check.disposition is TransitionDisposition.REFUSED:
        return BranchFingerprintStatus.FINGERPRINT_INCOMPLETE
    if transfer_check.output_status is BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED:
        return BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED
    if observable_kind == "proxy":
        if kq_flow_result is None:
            return BranchFingerprintStatus.FINGERPRINT_PROXY_UNCALIBRATED
        kq_check = apply_status_transition(KQ_FLOW_REQUIRE_STABLE_TRANSITION_RULE, kq_flow_result.status)
        if kq_check.disposition is not TransitionDisposition.ACCEPTED:
            return BranchFingerprintStatus.FINGERPRINT_PROXY_UNCALIBRATED
    return BranchFingerprintStatus.FINGERPRINT_COMPLETE


def _kq_result(controls, traces, statuses, values, flow_trace, band, stable, refusals, status):
    value = KqSlopeStabilityValue(controls, traces, statuses, values, flow_trace, band, stable, refusals)
    return TypedResult(
        value=value,
        space="KqSlopeStability",
        status=status,
        validity=_kq_validity(status),
        conditioning=_kq_conditioning(status),
        provenance=Provenance(
            operation_id="compare_kq_slope_stability",
            expression_path="kq_log_magnitude_slope_flow",
            parents=traces + (() if flow_trace is None else (flow_trace,)),
        ),
        protocol=ProtocolStatus.OK,
    )


def _source_ids(projection, transfer, kq):
    ids = [projection.provenance.trace_id, transfer.provenance.trace_id]
    if kq is not None:
        ids.append(kq.provenance.trace_id)
    return tuple(ids)


def _kq_validity(status):
    if status is BranchFingerprintStatus.KQ_FLOW_STABLE:
        return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
    if status is BranchFingerprintStatus.KQ_FLOW_UNSTABLE:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _fingerprint_validity(status):
    if status is BranchFingerprintStatus.FINGERPRINT_COMPLETE:
        return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
    if status is BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _kq_conditioning(status):
    return Conditioning(status=ConditioningStatus.WELL_CONDITIONED if status is BranchFingerprintStatus.KQ_FLOW_STABLE else ConditioningStatus.WARNING)


def _fingerprint_conditioning(status):
    return Conditioning(status=ConditioningStatus.WELL_CONDITIONED if status is BranchFingerprintStatus.FINGERPRINT_COMPLETE else ConditioningStatus.WARNING)


def _finite(value, name):
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        raise ProtocolViolationError(f"{name} must be finite")
    return float(value)


def _positive(value, name):
    number = _finite(value, name)
    if number <= 0:
        raise ProtocolViolationError(f"{name} must be positive")
    return number


def _optional_nonnegative(value, name):
    if value is None:
        return None
    number = _finite(value, name)
    if number < 0:
        raise ProtocolViolationError(f"{name} must be nonnegative")
    return number
