from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol, validate_protocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedRefusal, TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import ConditioningStatus, ProjectionStatus, ProtocolStatus, QuadraticRootStatus
from lloyd_v4.core.transitions import StatusTransitionOutcome, StatusTransitionRule, TransitionDisposition, apply_status_transition
from lloyd_v4.core.validity import Validity
from lloyd_v4.primitives.stratified_quadratic_roots import (
    STRATIFIED_QUADRATIC_ROOTS_PROTOCOL,
    StratifiedQuadraticRootValue,
    select_quadratic_root,
)
from lloyd_v4.projection.branches import (
    BRANCH_SELECTION_CONSUMER_PROTOCOL,
    BranchSelection,
    BranchSelectionValue,
)


EXACT_QUADRATIC_PROJECTION_PROTOCOL = ConsumerProtocol(
    name="exact_quadratic_projection",
    accepted_statuses=STRATIFIED_QUADRATIC_ROOTS_PROTOCOL.emitted_statuses,
    required_validity_fields=frozenset({"defined", "observable"}),
    scalarization_allowed=False,
)

PROJECTION_RESULT_V4_PROTOCOL = ProducerProtocol(
    name="projection_result_v4",
    emitted_statuses=frozenset(
        {
            ProjectionStatus.PROJECTION_TRANSVERSE,
            ProjectionStatus.PROJECTION_TANGENT_CONTACT,
            ProjectionStatus.PROJECTION_LINEAR,
            ProjectionStatus.PROJECTION_NO_REAL_ROOT,
            ProjectionStatus.PROJECTION_IDENTITY,
            ProjectionStatus.PROJECTION_NO_SOLUTION,
            ProjectionStatus.PROJECTION_SELECTION_REFUSED,
        }
    ),
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
)


@dataclass(frozen=True, slots=True)
class ProjectionResultValue:
    source_status: str
    requested_branch: str
    selected_branch: str | None
    selected_root_value: Any | None
    selected_root_trace_id: str | None
    source_trace_id: str
    source_operation_id: str
    projection_status: str

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "source_status": self.source_status,
            "requested_branch": self.requested_branch,
            "selected_branch": self.selected_branch,
            "selected_root_value": to_json_safe(self.selected_root_value),
            "selected_root_trace_id": self.selected_root_trace_id,
            "source_trace_id": self.source_trace_id,
            "source_operation_id": self.source_operation_id,
            "projection_status": self.projection_status,
        }


ProjectionResultV4 = TypedResult[ProjectionResultValue, ProjectionStatus]


def _projection_transition(status, context):
    branch = context["branch"]
    if not isinstance(branch, BranchSelection):
        raise ProtocolViolationError("projection transition requires BranchSelection context")
    if status is QuadraticRootStatus.TWO_REAL_ROOTS:
        output = (
            ProjectionStatus.PROJECTION_TRANSVERSE
            if branch in {BranchSelection.MINUS, BranchSelection.PLUS}
            else ProjectionStatus.PROJECTION_SELECTION_REFUSED
        )
    elif status is QuadraticRootStatus.REPEATED_ROOT:
        output = (
            ProjectionStatus.PROJECTION_TANGENT_CONTACT
            if branch is BranchSelection.REPEATED
            else ProjectionStatus.PROJECTION_SELECTION_REFUSED
        )
    elif status is QuadraticRootStatus.LINEAR_ROOT:
        output = (
            ProjectionStatus.PROJECTION_LINEAR
            if branch is BranchSelection.LINEAR
            else ProjectionStatus.PROJECTION_SELECTION_REFUSED
        )
    elif status is QuadraticRootStatus.NO_REAL_ROOT:
        output = ProjectionStatus.PROJECTION_NO_REAL_ROOT
    elif status is QuadraticRootStatus.CONSTANT_IDENTITY:
        output = ProjectionStatus.PROJECTION_IDENTITY
    elif status is QuadraticRootStatus.CONSTANT_NO_SOLUTION:
        output = ProjectionStatus.PROJECTION_NO_SOLUTION
    else:
        raise ProtocolViolationError(f"unhandled quadratic root status {status.value!r}")
    return StatusTransitionOutcome(
        rule_id=QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE.rule_id,
        input_status=status,
        disposition=TransitionDisposition.MAPPED,
        output_status=output,
    )


# Authority note (Task 018):
# For contextual transition rules, the transition() callable output is
# authoritative at runtime. The static mapped_statuses dict is coverage
# guidance for branch-compatible contexts, but does not capture
# branch-conditional refusals.
QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE = StatusTransitionRule(
    rule_id="quadratic_roots.to_exact_projection",
    input_status_family=QuadraticRootStatus,
    output_status_family=ProjectionStatus,
    input_protocol_id=STRATIFIED_QUADRATIC_ROOTS_PROTOCOL.name,
    output_protocol_id=PROJECTION_RESULT_V4_PROTOCOL.name,
    accepted_input_statuses=frozenset(),
    refused_input_statuses=frozenset(),
    mapped_statuses={
        QuadraticRootStatus.TWO_REAL_ROOTS: ProjectionStatus.PROJECTION_TRANSVERSE,
        QuadraticRootStatus.REPEATED_ROOT: ProjectionStatus.PROJECTION_TANGENT_CONTACT,
        QuadraticRootStatus.LINEAR_ROOT: ProjectionStatus.PROJECTION_LINEAR,
        QuadraticRootStatus.NO_REAL_ROOT: ProjectionStatus.PROJECTION_NO_REAL_ROOT,
        QuadraticRootStatus.CONSTANT_IDENTITY: ProjectionStatus.PROJECTION_IDENTITY,
        QuadraticRootStatus.CONSTANT_NO_SOLUTION: ProjectionStatus.PROJECTION_NO_SOLUTION,
    },
    context_keys=("branch",),
    description="Maps quadratic root-state statuses to exact projection statuses; branch compatibility is contextual.",
    emitted_input_statuses=STRATIFIED_QUADRATIC_ROOTS_PROTOCOL.emitted_statuses,
    transition=_projection_transition,
)


def exact_quadratic_projection(
    root_state_result: TypedResult,
    branch_selection_result: TypedResult,
) -> ProjectionResultV4:
    _require_typed_result(root_state_result, "root_state_result")
    _require_typed_result(branch_selection_result, "branch_selection_result")
    _require_value_type(root_state_result, StratifiedQuadraticRootValue, "root_state_result")
    _require_value_type(branch_selection_result, BranchSelectionValue, "branch_selection_result")

    root_check = validate_protocol(root_state_result, EXACT_QUADRATIC_PROJECTION_PROTOCOL)
    if not root_check.ok:
        return _projection_input_refusal(root_state_result, branch_selection_result, root_check.reason)

    branch_check = validate_protocol(branch_selection_result, BRANCH_SELECTION_CONSUMER_PROTOCOL)
    if not branch_check.ok:
        return _projection_input_refusal(root_state_result, branch_selection_result, branch_check.reason)

    branch = branch_selection_result.value.branch
    transition_outcome = apply_status_transition(
        QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE,
        root_state_result.status,
        branch=branch,
    )
    projection_status = transition_outcome.output_status
    if not isinstance(projection_status, ProjectionStatus):
        raise ProtocolViolationError("projection transition did not produce ProjectionStatus")

    if projection_status is ProjectionStatus.PROJECTION_SELECTION_REFUSED:
        return _projection_result(
            root_state_result=root_state_result,
            branch_selection_result=branch_selection_result,
            projection_status=projection_status,
            selected_root=None,
            refusal=_branch_incompatibility_refusal(root_state_result, branch),
        )

    if _is_nonselectable_projection_status(projection_status):
        return _projection_result(
            root_state_result=root_state_result,
            branch_selection_result=branch_selection_result,
            projection_status=projection_status,
            selected_root=None,
            refusal=None,
        )

    selected_root = select_quadratic_root(root_state_result, branch.value)
    if selected_root.refusal is not None:
        return _projection_result(
            root_state_result=root_state_result,
            branch_selection_result=branch_selection_result,
            projection_status=ProjectionStatus.PROJECTION_SELECTION_REFUSED,
            selected_root=selected_root,
            refusal=selected_root.refusal,
        )

    return _projection_result(
        root_state_result=root_state_result,
        branch_selection_result=branch_selection_result,
        projection_status=projection_status,
        selected_root=selected_root,
        refusal=None,
    )


def _projection_result(
    *,
    root_state_result: TypedResult,
    branch_selection_result: TypedResult,
    projection_status: ProjectionStatus,
    selected_root: TypedResult | None,
    refusal: TypedRefusal | None,
) -> ProjectionResultV4:
    branch = branch_selection_result.value.branch
    value = ProjectionResultValue(
        source_status=root_state_result.status.value,
        requested_branch=branch.value,
        selected_branch=branch.value if selected_root is not None and selected_root.refusal is None else None,
        selected_root_value=None if selected_root is None else selected_root.value,
        selected_root_trace_id=None if selected_root is None else selected_root.provenance.trace_id,
        source_trace_id=root_state_result.provenance.trace_id,
        source_operation_id=root_state_result.provenance.operation_id,
        projection_status=projection_status.value,
    )
    typed_refusal = refusal
    if projection_status is ProjectionStatus.PROJECTION_SELECTION_REFUSED and typed_refusal is None:
        typed_refusal = _branch_incompatibility_refusal(root_state_result, branch)

    return TypedResult(
        value=value,
        space="ProjectionResultV4",
        status=projection_status,
        validity=_validity_for_status(projection_status),
        conditioning=_conditioning_for_status(projection_status, root_state_result.conditioning),
        provenance=Provenance(
            operation_id="exact_quadratic_projection",
            expression_path="projection_from_stratified_quadratic_roots",
            precision=root_state_result.provenance.precision,
            backend=root_state_result.provenance.backend,
            device=root_state_result.provenance.device,
            measurement_resolution=root_state_result.provenance.measurement_resolution,
            parents=_parents(root_state_result, branch_selection_result, selected_root),
        ),
        protocol=ProtocolStatus.SCALARIZATION_REFUSED if typed_refusal is not None else ProtocolStatus.OK,
        refusal=typed_refusal,
    )


def _projection_input_refusal(
    root_state_result: TypedResult,
    branch_selection_result: TypedResult,
    reason: str,
) -> ProjectionResultV4:
    value = ProjectionResultValue(
        source_status=root_state_result.status.value,
        requested_branch=branch_selection_result.value.branch.value,
        selected_branch=None,
        selected_root_value=None,
        selected_root_trace_id=None,
        source_trace_id=root_state_result.provenance.trace_id,
        source_operation_id=root_state_result.provenance.operation_id,
        projection_status=ProjectionStatus.PROJECTION_SELECTION_REFUSED.value,
    )
    refusal = TypedRefusal(
        reason=f"exact quadratic projection input refused: {reason}",
        status=ProtocolStatus.SCALARIZATION_REFUSED,
        details={
            "source_status": root_state_result.status.value,
            "branch_status": branch_selection_result.status.value,
        },
    )
    return TypedResult(
        value=value,
        space="ProjectionResultV4",
        status=ProjectionStatus.PROJECTION_SELECTION_REFUSED,
        validity=_validity_for_status(ProjectionStatus.PROJECTION_SELECTION_REFUSED),
        conditioning=Conditioning(status=ConditioningStatus.WARNING, notes=("input_refused",)),
        provenance=Provenance(
            operation_id="exact_quadratic_projection",
            expression_path="projection_input_refusal",
            precision=root_state_result.provenance.precision,
            backend=root_state_result.provenance.backend,
            device=root_state_result.provenance.device,
            measurement_resolution=root_state_result.provenance.measurement_resolution,
            parents=(root_state_result.provenance.trace_id, branch_selection_result.provenance.trace_id),
        ),
        protocol=ProtocolStatus.SCALARIZATION_REFUSED,
        refusal=refusal,
    )


def _branch_incompatibility_refusal(root_state_result: TypedResult, branch: BranchSelection) -> TypedRefusal:
    return TypedRefusal(
        reason=f"projection selection refused for branch {branch.value!r}",
        status=ProtocolStatus.SCALARIZATION_REFUSED,
        details={
            "projection_status": ProjectionStatus.PROJECTION_SELECTION_REFUSED.value,
            "branch": branch.value,
            "source_status": root_state_result.status.value,
        },
    )


def _require_typed_result(result: object, name: str) -> None:
    if not isinstance(result, TypedResult):
        raise ProtocolViolationError(f"{name} must be a TypedResult")


def _require_value_type(result: TypedResult, expected_type: type, name: str) -> None:
    if not isinstance(result.value, expected_type):
        raise ProtocolViolationError(f"{name} must carry {expected_type.__name__}")


def _is_nonselectable_projection_status(status: ProjectionStatus) -> bool:
    return status in {
        ProjectionStatus.PROJECTION_NO_REAL_ROOT,
        ProjectionStatus.PROJECTION_IDENTITY,
        ProjectionStatus.PROJECTION_NO_SOLUTION,
    }


def _validity_for_status(status: ProjectionStatus) -> Validity:
    if status in {ProjectionStatus.PROJECTION_TRANSVERSE, ProjectionStatus.PROJECTION_LINEAR}:
        return Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True)
    if status is ProjectionStatus.PROJECTION_TANGENT_CONTACT:
        return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning_for_status(status: ProjectionStatus, source_conditioning: Conditioning) -> Conditioning:
    if status in {
        ProjectionStatus.PROJECTION_TANGENT_CONTACT,
        ProjectionStatus.PROJECTION_IDENTITY,
        ProjectionStatus.PROJECTION_SELECTION_REFUSED,
    }:
        return Conditioning(status=ConditioningStatus.WARNING, notes=(status.value,))
    return source_conditioning


def _parents(
    root_state_result: TypedResult,
    branch_selection_result: TypedResult,
    selected_root: TypedResult | None,
) -> tuple[str, ...]:
    parents = [root_state_result.provenance.trace_id, branch_selection_result.provenance.trace_id]
    if selected_root is not None:
        parents.append(selected_root.provenance.trace_id)
    return tuple(parents)
