from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol, validate_protocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedRefusal, TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import (
    BranchFingerprintStatus,
    ConditioningStatus,
    MetrologyStatus,
    ProjectiveRatioStatus,
    ProjectionStatus,
    ProtocolStatus,
    QuadraticRootStatus,
    RefineryStatus,
)
from lloyd_v4.core.transitions import StatusTransitionRule, apply_status_transition
from lloyd_v4.core.validity import Validity
from lloyd_v4.refinery.observations import RefineryObservation, TypedResultSnapshot
from lloyd_v4.refinery.slag import SlagComparison, SlagVector, aggregate_slag_vectors, compare_slag_vectors, compute_slag_vector


REFINERY_OBSERVATION_PROTOCOL = ProducerProtocol(
    name="refinery.observation",
    emitted_statuses=frozenset(RefineryStatus),
    required_fields=frozenset({"snapshot"}),
    status_family=RefineryStatus,
)

REFINERY_DECISION_PROTOCOL = ConsumerProtocol(
    name="refinery.decision",
    accepted_statuses=frozenset(RefineryStatus),
    required_validity_fields=frozenset({"defined", "observable"}),
    scalarization_allowed=False,
    status_family=RefineryStatus,
)

REFINERY_ACCEPTED_REWRITE_PROTOCOL = ConsumerProtocol(
    name="refinery.accepted_rewrite",
    accepted_statuses=frozenset({RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG}),
    required_validity_fields=frozenset({"defined", "observable"}),
    scalarization_allowed=False,
    status_family=RefineryStatus,
    refused_statuses=frozenset(
        status
        for status in RefineryStatus
        if status is not RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG
    ),
)


def _preservation_rule(rule_id: str, family: type[Enum]) -> StatusTransitionRule:
    return StatusTransitionRule(
        rule_id=rule_id,
        input_status_family=family,
        output_status_family=family,
        input_protocol_id="refinery.observation",
        output_protocol_id="refinery.observation",
        accepted_input_statuses=frozenset(family),
        refused_input_statuses=frozenset(),
        mapped_statuses={},
        context_keys=("reference_status", "candidate_status", "reference_snapshot", "candidate_snapshot", "scenario_id"),
        description="Refinery status preservation requires matching typed status evidence.",
        emitted_input_statuses=frozenset(family),
    )


PROJECTIVE_RATIO_STATUS_PRESERVATION_TRANSITION_RULE = _preservation_rule(
    "refinery.projective_ratio.status_preservation",
    ProjectiveRatioStatus,
)
QUADRATIC_ROOT_STATUS_PRESERVATION_TRANSITION_RULE = _preservation_rule(
    "refinery.quadratic_roots.status_preservation",
    QuadraticRootStatus,
)
PROJECTION_STATUS_PRESERVATION_TRANSITION_RULE = _preservation_rule(
    "refinery.projection.status_preservation",
    ProjectionStatus,
)
METROLOGY_STATUS_PRESERVATION_TRANSITION_RULE = _preservation_rule(
    "refinery.metrology.status_preservation",
    MetrologyStatus,
)
BRANCH_FINGERPRINT_STATUS_PRESERVATION_TRANSITION_RULE = _preservation_rule(
    "refinery.branch_fingerprint.status_preservation",
    BranchFingerprintStatus,
)

REFINERY_REQUIRE_ACCEPTED_TRANSITION_RULE = StatusTransitionRule(
    rule_id="refinery.decision.require_accepted",
    input_status_family=RefineryStatus,
    output_status_family=RefineryStatus,
    input_protocol_id=REFINERY_DECISION_PROTOCOL.name,
    output_protocol_id=REFINERY_ACCEPTED_REWRITE_PROTOCOL.name,
    accepted_input_statuses=frozenset({RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG}),
    refused_input_statuses=frozenset(
        status
        for status in RefineryStatus
        if status is not RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG
    ),
    mapped_statuses={},
    emitted_input_statuses=frozenset(RefineryStatus),
)

_STATUS_PRESERVATION_RULES = {
    ProjectiveRatioStatus: PROJECTIVE_RATIO_STATUS_PRESERVATION_TRANSITION_RULE,
    QuadraticRootStatus: QUADRATIC_ROOT_STATUS_PRESERVATION_TRANSITION_RULE,
    ProjectionStatus: PROJECTION_STATUS_PRESERVATION_TRANSITION_RULE,
    MetrologyStatus: METROLOGY_STATUS_PRESERVATION_TRANSITION_RULE,
    BranchFingerprintStatus: BRANCH_FINGERPRINT_STATUS_PRESERVATION_TRANSITION_RULE,
}


@dataclass(frozen=True, slots=True)
class RefineryScenarioComparison:
    scenario_id: str
    status: RefineryStatus
    reference_snapshot: TypedResultSnapshot
    candidate_snapshot: TypedResultSnapshot
    protocol_match: bool
    status_family_match: bool
    status_match: bool
    validity_match: bool
    geometry_match: bool
    source_trace_preserved: bool
    reference_slag: SlagVector
    candidate_slag: SlagVector
    slag_comparison: SlagComparison
    transition_rule_id: str | None
    decision_reason: str
    rejection_reasons: tuple[str, ...]

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "status": self.status.value,
            "reference_snapshot": self.reference_snapshot.to_json_safe(),
            "candidate_snapshot": self.candidate_snapshot.to_json_safe(),
            "protocol_match": self.protocol_match,
            "status_family_match": self.status_family_match,
            "status_match": self.status_match,
            "validity_match": self.validity_match,
            "geometry_match": self.geometry_match,
            "source_trace_preserved": self.source_trace_preserved,
            "reference_slag": self.reference_slag.to_json_safe(),
            "candidate_slag": self.candidate_slag.to_json_safe(),
            "slag_comparison": self.slag_comparison.to_json_safe(),
            "transition_rule_id": self.transition_rule_id,
            "decision_reason": self.decision_reason,
            "rejection_reasons": list(self.rejection_reasons),
        }


@dataclass(frozen=True, slots=True)
class RefineryDecisionValue:
    reference_name: str
    candidate_name: str
    scenario_comparisons: tuple[RefineryScenarioComparison, ...]
    aggregate_reference_slag: SlagVector
    aggregate_candidate_slag: SlagVector
    componentwise_comparison: SlagComparison
    accepted: bool
    decision_reason: str
    rejection_reasons: tuple[str, ...]

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "reference_name": self.reference_name,
            "candidate_name": self.candidate_name,
            "scenario_comparisons": [comparison.to_json_safe() for comparison in self.scenario_comparisons],
            "aggregate_reference_slag": self.aggregate_reference_slag.to_json_safe(),
            "aggregate_candidate_slag": self.aggregate_candidate_slag.to_json_safe(),
            "componentwise_comparison": self.componentwise_comparison.to_json_safe(),
            "accepted": self.accepted,
            "decision_reason": self.decision_reason,
            "rejection_reasons": list(self.rejection_reasons),
        }


RefineryDecisionResult = TypedResult[RefineryDecisionValue, RefineryStatus]


def compare_refinery_scenario(
    reference: RefineryObservation | TypedResultSnapshot,
    candidate: RefineryObservation | TypedResultSnapshot,
    *,
    declared_slag_dimensions: Sequence[str] | None = None,
) -> RefineryScenarioComparison:
    reference_snapshot = _snapshot(reference)
    candidate_snapshot = _snapshot(candidate)
    reference_slag = compute_slag_vector(reference_snapshot, declared_dimensions=declared_slag_dimensions)
    candidate_slag = compute_slag_vector(candidate_snapshot, declared_dimensions=declared_slag_dimensions)
    slag_comparison = compare_slag_vectors(reference_slag, candidate_slag)

    if reference_snapshot.scenario_id != candidate_snapshot.scenario_id:
        return _scenario_result(
            reference_snapshot,
            candidate_snapshot,
            RefineryStatus.REWRITE_INDETERMINATE_INSUFFICIENT_EVIDENCE,
            reference_slag,
            candidate_slag,
            slag_comparison,
            "scenario IDs differ",
            ("scenario_id_mismatch",),
        )

    protocol_match = reference_snapshot.protocol_identity == candidate_snapshot.protocol_identity
    status_family_match = reference_snapshot.status_family == candidate_snapshot.status_family
    status_match = reference_snapshot.status == candidate_snapshot.status
    validity_match = reference_snapshot.validity == candidate_snapshot.validity
    rule = _rule_for(reference_snapshot.status_family)
    transition_rule_id = None
    if rule is not None:
        transition_rule_id = rule.rule_id
        _apply_preservation_rule(rule, reference_snapshot, candidate_snapshot)
    source_trace_preserved = set(reference_snapshot.source_trace_ids).issubset(set(candidate_snapshot.source_trace_ids))
    geometry_match = _geometry_match(reference_snapshot, candidate_snapshot) and source_trace_preserved

    if not status_family_match:
        status = RefineryStatus.REWRITE_REJECTED_STATUS_FAMILY_MISMATCH
        reason = "status family mismatch"
        rejections = ("status_family_mismatch",)
    elif not protocol_match:
        status = RefineryStatus.REWRITE_REJECTED_PROTOCOL_MISMATCH
        reason = "protocol identity mismatch"
        rejections = ("protocol_mismatch",)
    elif not status_match:
        status = RefineryStatus.REWRITE_REJECTED_STATUS_MISMATCH
        reason = "status mismatch"
        rejections = ("status_mismatch",)
    elif not validity_match:
        status = RefineryStatus.REWRITE_REJECTED_VALIDITY_MISMATCH
        reason = "validity mismatch"
        rejections = ("validity_mismatch",)
    elif rule is None:
        status = RefineryStatus.REWRITE_INDETERMINATE_UNHANDLED_STATUS
        reason = "unhandled status family"
        rejections = ("unhandled_status_family",)
    elif not geometry_match:
        status = RefineryStatus.REWRITE_REJECTED_GEOMETRY_MISMATCH
        reason = "geometry evidence mismatch"
        rejections = ("geometry_mismatch",)
    elif not set(reference_slag.components).issubset(set(candidate_slag.components)):
        status = RefineryStatus.REWRITE_INDETERMINATE_INSUFFICIENT_EVIDENCE
        reason = "candidate dropped declared diagnostic evidence"
        rejections = ("missing_slag_dimension",)
    elif slag_comparison.regressed_dimensions:
        status = RefineryStatus.REWRITE_REJECTED_SLAG_REGRESSION
        reason = "componentwise diagnostic evidence regressed"
        rejections = ("slag_regression",)
    else:
        status = RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT
        reason = "same geometry evidence with no scenario-level acceptance"
        rejections = ()

    return RefineryScenarioComparison(
        scenario_id=reference_snapshot.scenario_id,
        status=status,
        reference_snapshot=reference_snapshot,
        candidate_snapshot=candidate_snapshot,
        protocol_match=protocol_match,
        status_family_match=status_family_match,
        status_match=status_match,
        validity_match=validity_match,
        geometry_match=geometry_match,
        source_trace_preserved=source_trace_preserved,
        reference_slag=reference_slag,
        candidate_slag=candidate_slag,
        slag_comparison=slag_comparison,
        transition_rule_id=transition_rule_id,
        decision_reason=reason,
        rejection_reasons=rejections,
    )


def evaluate_rewrite_candidate(
    reference_observations: Sequence[RefineryObservation | TypedResultSnapshot],
    candidate_observations: Sequence[RefineryObservation | TypedResultSnapshot],
    *,
    reference_name: str = "reference",
    candidate_name: str,
    declared_slag_dimensions: Sequence[str] | None = None,
) -> RefineryDecisionResult:
    references = tuple(_snapshot(item) for item in reference_observations)
    candidates = tuple(_snapshot(item) for item in candidate_observations)
    scenario_status = _paired_scenarios(references, candidates)
    if scenario_status is not None:
        return _decision_result(
            reference_name,
            candidate_name,
            (),
            SlagVector({}),
            SlagVector({}),
            compare_slag_vectors(SlagVector({}), SlagVector({})),
            scenario_status,
            "paired scenario evidence is required",
            ("insufficient_scenario_evidence",),
        )

    candidate_by_id = {snapshot.scenario_id: snapshot for snapshot in candidates}
    comparisons = tuple(
        compare_refinery_scenario(
            reference,
            candidate_by_id[reference.scenario_id],
            declared_slag_dimensions=declared_slag_dimensions,
        )
        for reference in references
    )

    aggregate_reference = aggregate_slag_vectors([comparison.reference_slag for comparison in comparisons])
    aggregate_candidate = aggregate_slag_vectors([comparison.candidate_slag for comparison in comparisons])
    aggregate_comparison = compare_slag_vectors(aggregate_reference, aggregate_candidate)
    status, reason, rejections = _decision_status(comparisons, aggregate_comparison)

    return _decision_result(
        reference_name,
        candidate_name,
        comparisons,
        aggregate_reference,
        aggregate_candidate,
        aggregate_comparison,
        status,
        reason,
        rejections,
    )


def require_accepted_rewrite(result: RefineryDecisionResult) -> RefineryDecisionResult:
    check = validate_protocol(result, REFINERY_ACCEPTED_REWRITE_PROTOCOL)
    if check.ok:
        return result
    status = result.status if isinstance(getattr(result, "status", None), RefineryStatus) else RefineryStatus.REWRITE_INDETERMINATE_UNHANDLED_STATUS
    refusal = TypedRefusal(
        reason=f"accepted rewrite required: {check.reason}",
        status=ProtocolStatus.SCALARIZATION_REFUSED,
        details={"decision_status": getattr(getattr(result, "status", None), "value", None)},
    )
    return TypedResult(
        value=result.value,
        space="RefineryDecision",
        status=status,
        validity=Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True),
        conditioning=Conditioning(status=ConditioningStatus.WARNING),
        provenance=Provenance(
            operation_id="require_accepted_rewrite",
            expression_path="refinery_accepted_rewrite_protocol",
            parents=(result.provenance.trace_id,),
        ),
        protocol=ProtocolStatus.SCALARIZATION_REFUSED,
        refusal=refusal,
    )


def _snapshot(observation: RefineryObservation | TypedResultSnapshot) -> TypedResultSnapshot:
    if isinstance(observation, RefineryObservation):
        return observation.snapshot
    if isinstance(observation, TypedResultSnapshot):
        return observation
    raise ProtocolViolationError("refinery scenario comparison requires typed observation snapshots")


def _scenario_result(
    reference: TypedResultSnapshot,
    candidate: TypedResultSnapshot,
    status: RefineryStatus,
    reference_slag: SlagVector,
    candidate_slag: SlagVector,
    slag_comparison: SlagComparison,
    reason: str,
    rejections: tuple[str, ...],
) -> RefineryScenarioComparison:
    return RefineryScenarioComparison(
        scenario_id=reference.scenario_id,
        status=status,
        reference_snapshot=reference,
        candidate_snapshot=candidate,
        protocol_match=False,
        status_family_match=False,
        status_match=False,
        validity_match=False,
        geometry_match=False,
        source_trace_preserved=False,
        reference_slag=reference_slag,
        candidate_slag=candidate_slag,
        slag_comparison=slag_comparison,
        transition_rule_id=None,
        decision_reason=reason,
        rejection_reasons=rejections,
    )


def _apply_preservation_rule(rule: StatusTransitionRule, reference: TypedResultSnapshot, candidate: TypedResultSnapshot) -> None:
    status = rule.input_status_family(reference.status)
    apply_status_transition(
        rule,
        status,
        reference_status=reference.status,
        candidate_status=candidate.status,
        reference_snapshot=reference.to_json_safe(),
        candidate_snapshot=candidate.to_json_safe(),
        scenario_id=reference.scenario_id,
    )


def _rule_for(status_family_name: str) -> StatusTransitionRule | None:
    for family, rule in _STATUS_PRESERVATION_RULES.items():
        if family.__name__ == status_family_name:
            return rule
    return None


def _geometry_match(reference: TypedResultSnapshot, candidate: TypedResultSnapshot) -> bool:
    if reference.status_family == "ProjectiveRatioStatus":
        return _compare_required_keys(reference, candidate, ("coordinate_shape", "numerator_is_zero", "denominator_is_zero"))
    if reference.status_family == "QuadraticRootStatus":
        return _compare_required_keys(reference, candidate, ("branch_labels",))
    if reference.status_family == "ProjectionStatus":
        return _compare_required_keys(reference, candidate, ("source_status", "requested_branch", "selected_branch", "projection_status"))
    if reference.status_family == "MetrologyStatus":
        return _metrology_geometry_match(reference, candidate)
    if reference.status_family == "BranchFingerprintStatus":
        return _branch_geometry_match(reference, candidate)
    return False


def _compare_required_keys(reference: TypedResultSnapshot, candidate: TypedResultSnapshot, keys: tuple[str, ...]) -> bool:
    for key in keys:
        if key not in reference.value_fingerprint or key not in candidate.value_fingerprint:
            return False
        if reference.value_fingerprint[key] != candidate.value_fingerprint[key]:
            return False
    return True


def _metrology_geometry_match(reference: TypedResultSnapshot, candidate: TypedResultSnapshot) -> bool:
    role = reference.value_fingerprint.get("metrology_role")
    if role != candidate.value_fingerprint.get("metrology_role"):
        return False
    keys_by_role = {
        "noise_floor": ("metrology_role", "label", "method", "unit", "sample_count"),
        "limit_of_detection": ("metrology_role", "observable_label", "comparison", "unit", "identity_evidence"),
        "proxy_calibration": ("metrology_role", "proxy_label", "transfer_label", "frequency_label", "kq_projective_status", "calibration_reason", "proxy_mode"),
        "valid_proxy_calibration": ("metrology_role", "proxy_label", "transfer_label"),
    }
    keys = keys_by_role.get(role)
    return False if keys is None else _compare_required_keys(reference, candidate, keys)


def _branch_geometry_match(reference: TypedResultSnapshot, candidate: TypedResultSnapshot) -> bool:
    if "fingerprint_components" in reference.value_fingerprint:
        return _compare_required_keys(
            reference,
            candidate,
            (
                "projection_status",
                "requested_branch",
                "selected_branch",
                "transfer_flow_status",
                "selected_model_name",
                "observable_kind",
                "kq_flow_status",
                "proxy_mode",
                "fingerprint_components",
            ),
        )
    if "model_names" in reference.value_fingerprint:
        return _compare_required_keys(reference, candidate, ("observable_kind", "selected_model_name", "model_names"))
    if "stable" in reference.value_fingerprint:
        return _compare_required_keys(reference, candidate, ("observable_kind", "proxy_mode", "stable", "kq_flow_statuses"))
    return False


def _paired_scenarios(references: tuple[TypedResultSnapshot, ...], candidates: tuple[TypedResultSnapshot, ...]) -> RefineryStatus | None:
    if not references or not candidates or len(references) != len(candidates):
        return RefineryStatus.REWRITE_INDETERMINATE_INSUFFICIENT_EVIDENCE
    reference_ids = [snapshot.scenario_id for snapshot in references]
    candidate_ids = [snapshot.scenario_id for snapshot in candidates]
    if len(set(reference_ids)) != len(reference_ids) or len(set(candidate_ids)) != len(candidate_ids):
        return RefineryStatus.REWRITE_INDETERMINATE_INSUFFICIENT_EVIDENCE
    if set(reference_ids) != set(candidate_ids):
        return RefineryStatus.REWRITE_INDETERMINATE_INSUFFICIENT_EVIDENCE
    return None


def _decision_status(comparisons: tuple[RefineryScenarioComparison, ...], aggregate: SlagComparison) -> tuple[RefineryStatus, str, tuple[str, ...]]:
    if any(not comparison.protocol_match for comparison in comparisons):
        return RefineryStatus.REWRITE_REJECTED_PROTOCOL_MISMATCH, "protocol identity mismatch", ("protocol_mismatch",)
    ordered = (
        RefineryStatus.REWRITE_REJECTED_STATUS_FAMILY_MISMATCH,
        RefineryStatus.REWRITE_REJECTED_PROTOCOL_MISMATCH,
        RefineryStatus.REWRITE_REJECTED_STATUS_MISMATCH,
        RefineryStatus.REWRITE_REJECTED_VALIDITY_MISMATCH,
        RefineryStatus.REWRITE_REJECTED_GEOMETRY_MISMATCH,
        RefineryStatus.REWRITE_REJECTED_SLAG_REGRESSION,
        RefineryStatus.REWRITE_INDETERMINATE_INSUFFICIENT_EVIDENCE,
        RefineryStatus.REWRITE_INDETERMINATE_UNHANDLED_STATUS,
    )
    for status in ordered:
        if any(comparison.status is status for comparison in comparisons):
            return status, status.value, tuple({reason for comparison in comparisons for reason in comparison.rejection_reasons})
    if aggregate.regressed_dimensions:
        return RefineryStatus.REWRITE_REJECTED_SLAG_REGRESSION, "aggregate diagnostic evidence regressed", ("slag_regression",)
    if aggregate.no_worse and aggregate.strictly_lower:
        return RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG, "same geometry evidence with componentwise lower diagnostic burden", ()
    return RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT, "same geometry evidence with no lower diagnostic burden", ()


def _decision_result(
    reference_name: str,
    candidate_name: str,
    comparisons: tuple[RefineryScenarioComparison, ...],
    aggregate_reference: SlagVector,
    aggregate_candidate: SlagVector,
    aggregate_comparison: SlagComparison,
    status: RefineryStatus,
    reason: str,
    rejections: tuple[str, ...],
) -> RefineryDecisionResult:
    value = RefineryDecisionValue(
        reference_name=reference_name,
        candidate_name=candidate_name,
        scenario_comparisons=comparisons,
        aggregate_reference_slag=aggregate_reference,
        aggregate_candidate_slag=aggregate_candidate,
        componentwise_comparison=aggregate_comparison,
        accepted=status is RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG,
        decision_reason=reason,
        rejection_reasons=rejections,
    )
    return TypedResult(
        value=value,
        space="RefineryDecision",
        status=status,
        validity=_validity(status),
        conditioning=_conditioning(status),
        provenance=Provenance(
            operation_id="evaluate_rewrite_candidate",
            expression_path="refinery_protocol_preserving_rewrite_evaluation",
            parents=tuple(
                snapshot.trace_id
                for comparison in comparisons
                for snapshot in (comparison.reference_snapshot, comparison.candidate_snapshot)
            ),
        ),
        protocol=ProtocolStatus.OK,
    )


def _validity(status: RefineryStatus) -> Validity:
    return Validity(
        defined=True,
        finite=True,
        selectable=status is RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG,
        advanceable=False,
        observable=True,
    )


def _conditioning(status: RefineryStatus) -> Conditioning:
    if status in {
        RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG,
        RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT,
    }:
        return Conditioning(status=ConditioningStatus.WELL_CONDITIONED)
    return Conditioning(status=ConditioningStatus.WARNING)
