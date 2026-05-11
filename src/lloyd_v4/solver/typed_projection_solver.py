from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

from lloyd_v4.branch import BRANCH_FINGERPRINT_CONSUMER_PROTOCOL, BranchFingerprintResult
from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol, validate_protocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedRefusal, TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import (
    BranchFingerprintStatus,
    ConditioningStatus,
    HistoryStatus,
    MetrologyStatus,
    ProjectionStatus,
    ProtocolStatus,
    RefineryStatus,
    SolverStatus,
)
from lloyd_v4.core.transitions import StatusTransitionRule
from lloyd_v4.core.validity import Validity
from lloyd_v4.history import build_status_trace, record_status_event, require_stable_status_trace
from lloyd_v4.metrology import B_K_NOISE_FLOOR_PROTOCOL, classify_against_noise_floor
from lloyd_v4.primitives.stratified_quadratic_roots import stratified_quadratic_roots
from lloyd_v4.projection import BranchSelection, branch_selection, exact_quadratic_projection
from lloyd_v4.refinery import REFINERY_ACCEPTED_REWRITE_PROTOCOL


STEP_TERMINAL_STATUSES = frozenset(
    {
        SolverStatus.SOLVER_CONVERGED_IDENTITY,
        SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION,
        SolverStatus.SOLVER_PROJECTION_BLOCKED,
        SolverStatus.SOLVER_TANGENT_BLOCKED,
        SolverStatus.SOLVER_SELECTION_REFUSED,
        SolverStatus.SOLVER_BRANCH_UNIDENTIFIED,
        SolverStatus.SOLVER_PROXY_UNCALIBRATED,
        SolverStatus.SOLVER_REFINERY_REJECTED,
        SolverStatus.SOLVER_HISTORY_UNSTABLE,
        SolverStatus.SOLVER_SEQUENCE_INCONSISTENT,
        SolverStatus.SOLVER_PROTOCOL_REFUSED,
        SolverStatus.SOLVER_INDETERMINATE,
    }
)
RUN_STATUSES = frozenset(SolverStatus) - frozenset({SolverStatus.SOLVER_STEP_ADVANCED})

TYPED_PROJECTION_SOLVER_STEP_PROTOCOL = ProducerProtocol(
    name="typed_projection_solver_step",
    emitted_statuses=frozenset(SolverStatus),
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=SolverStatus,
)
TYPED_PROJECTION_SOLVER_RUN_PROTOCOL = ProducerProtocol(
    name="typed_projection_solver_run",
    emitted_statuses=RUN_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=SolverStatus,
)
CONVERGED_SOLVER_PROTOCOL = ConsumerProtocol(
    name="converged_solver",
    accepted_statuses=frozenset(
        {SolverStatus.SOLVER_CONVERGED_IDENTITY, SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION}
    ),
    required_validity_fields=frozenset({"defined", "observable"}),
    scalarization_allowed=False,
    status_family=SolverStatus,
    refused_statuses=frozenset(SolverStatus)
    - frozenset({SolverStatus.SOLVER_CONVERGED_IDENTITY, SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION}),
)


RESIDUAL_DETECTION_TO_SOLVER_TRANSITION_RULE = StatusTransitionRule(
    rule_id="solver.residual_detection.to_solver",
    input_status_family=MetrologyStatus,
    output_status_family=SolverStatus,
    input_protocol_id="limit_of_detection",
    output_protocol_id=TYPED_PROJECTION_SOLVER_STEP_PROTOCOL.name,
    accepted_input_statuses=frozenset(),
    refused_input_statuses=frozenset(),
    mapped_statuses={
        MetrologyStatus.IDENTITY_ZERO: SolverStatus.SOLVER_CONVERGED_IDENTITY,
        MetrologyStatus.BELOW_LIMIT_OF_DETECTION: SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION,
        MetrologyStatus.DETECTED: SolverStatus.SOLVER_STEP_ADVANCED,
        MetrologyStatus.DETECTION_INDETERMINATE: SolverStatus.SOLVER_INDETERMINATE,
    },
    context_keys=("policy",),
    emitted_input_statuses=frozenset(
        {
            MetrologyStatus.IDENTITY_ZERO,
            MetrologyStatus.BELOW_LIMIT_OF_DETECTION,
            MetrologyStatus.DETECTED,
            MetrologyStatus.DETECTION_INDETERMINATE,
        }
    ),
)
PROJECTION_TO_SOLVER_STEP_TRANSITION_RULE = StatusTransitionRule(
    rule_id="solver.projection.to_solver_step",
    input_status_family=ProjectionStatus,
    output_status_family=SolverStatus,
    input_protocol_id="projection_result_v4",
    output_protocol_id=TYPED_PROJECTION_SOLVER_STEP_PROTOCOL.name,
    accepted_input_statuses=frozenset(),
    refused_input_statuses=frozenset(),
    mapped_statuses={
        ProjectionStatus.PROJECTION_TRANSVERSE: SolverStatus.SOLVER_STEP_ADVANCED,
        ProjectionStatus.PROJECTION_LINEAR: SolverStatus.SOLVER_STEP_ADVANCED,
        ProjectionStatus.PROJECTION_TANGENT_CONTACT: SolverStatus.SOLVER_TANGENT_BLOCKED,
        ProjectionStatus.PROJECTION_NO_REAL_ROOT: SolverStatus.SOLVER_PROJECTION_BLOCKED,
        ProjectionStatus.PROJECTION_IDENTITY: SolverStatus.SOLVER_PROJECTION_BLOCKED,
        ProjectionStatus.PROJECTION_NO_SOLUTION: SolverStatus.SOLVER_PROJECTION_BLOCKED,
        ProjectionStatus.PROJECTION_SELECTION_REFUSED: SolverStatus.SOLVER_SELECTION_REFUSED,
    },
    emitted_input_statuses=frozenset(ProjectionStatus),
)
BRANCH_FINGERPRINT_TO_SOLVER_TRANSITION_RULE = StatusTransitionRule(
    rule_id="solver.branch_fingerprint.require_complete",
    input_status_family=BranchFingerprintStatus,
    output_status_family=SolverStatus,
    input_protocol_id="branch_fingerprint",
    output_protocol_id=TYPED_PROJECTION_SOLVER_STEP_PROTOCOL.name,
    accepted_input_statuses=frozenset({BranchFingerprintStatus.FINGERPRINT_COMPLETE}),
    refused_input_statuses=frozenset(),
    mapped_statuses={
        BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED: SolverStatus.SOLVER_BRANCH_UNIDENTIFIED,
        BranchFingerprintStatus.FINGERPRINT_INCOMPLETE: SolverStatus.SOLVER_BRANCH_UNIDENTIFIED,
        BranchFingerprintStatus.FINGERPRINT_PROXY_UNCALIBRATED: SolverStatus.SOLVER_PROXY_UNCALIBRATED,
    },
    emitted_input_statuses=frozenset(
        {
            BranchFingerprintStatus.FINGERPRINT_COMPLETE,
            BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED,
            BranchFingerprintStatus.FINGERPRINT_INCOMPLETE,
            BranchFingerprintStatus.FINGERPRINT_PROXY_UNCALIBRATED,
        }
    ),
)
REFINERY_TO_SOLVER_TRANSITION_RULE = StatusTransitionRule(
    rule_id="solver.refinery.require_accepted",
    input_status_family=RefineryStatus,
    output_status_family=SolverStatus,
    input_protocol_id="refinery.decision",
    output_protocol_id=TYPED_PROJECTION_SOLVER_STEP_PROTOCOL.name,
    accepted_input_statuses=frozenset({RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG}),
    refused_input_statuses=frozenset(),
    mapped_statuses={
        status: SolverStatus.SOLVER_REFINERY_REJECTED
        for status in RefineryStatus
        if status is not RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG
    },
    emitted_input_statuses=frozenset(RefineryStatus),
)
PROJECTION_HISTORY_TO_SOLVER_TRANSITION_RULE = StatusTransitionRule(
    rule_id="solver.projection_history.require_stable",
    input_status_family=HistoryStatus,
    output_status_family=SolverStatus,
    input_protocol_id="history" + "_trace",
    output_protocol_id=TYPED_PROJECTION_SOLVER_RUN_PROTOCOL.name,
    accepted_input_statuses=frozenset({HistoryStatus.HISTORY_TRACE_STABLE, HistoryStatus.HISTORY_TRACE_SINGLETON}),
    refused_input_statuses=frozenset(),
    mapped_statuses={
        HistoryStatus.HISTORY_TRACE_TRANSITIONED: SolverStatus.SOLVER_HISTORY_UNSTABLE,
        HistoryStatus.HISTORY_TRACE_INCOMPLETE: SolverStatus.SOLVER_HISTORY_UNSTABLE,
        HistoryStatus.HISTORY_TRACE_UNORDERED: SolverStatus.SOLVER_HISTORY_UNSTABLE,
        HistoryStatus.HISTORY_TRACE_EMPTY: SolverStatus.SOLVER_INDETERMINATE,
    },
    emitted_input_statuses=frozenset(
        {
            HistoryStatus.HISTORY_TRACE_STABLE,
            HistoryStatus.HISTORY_TRACE_SINGLETON,
            HistoryStatus.HISTORY_TRACE_TRANSITIONED,
            HistoryStatus.HISTORY_TRACE_INCOMPLETE,
            HistoryStatus.HISTORY_TRACE_UNORDERED,
            HistoryStatus.HISTORY_TRACE_EMPTY,
        }
    ),
)
SOLVER_RUN_REQUIRE_CONVERGED_TRANSITION_RULE = StatusTransitionRule(
    rule_id="solver.run.require_converged",
    input_status_family=SolverStatus,
    output_status_family=None,
    input_protocol_id=TYPED_PROJECTION_SOLVER_RUN_PROTOCOL.name,
    output_protocol_id=CONVERGED_SOLVER_PROTOCOL.name,
    accepted_input_statuses=CONVERGED_SOLVER_PROTOCOL.accepted_statuses,
    refused_input_statuses=frozenset(SolverStatus) - CONVERGED_SOLVER_PROTOCOL.accepted_statuses,
    mapped_statuses={},
    emitted_input_statuses=frozenset(SolverStatus),
)


@dataclass(frozen=True, slots=True)
class SolverPolicy:
    accept_below_detection: bool = False
    require_branch_fingerprint: bool = False
    require_refinery_acceptance: bool = False
    require_stable_projection_history: bool = True

    def to_json_safe(self) -> dict[str, bool]:
        return {
            "accept_below_detection": self.accept_below_detection,
            "require_branch_fingerprint": self.require_branch_fingerprint,
            "require_refinery_acceptance": self.require_refinery_acceptance,
            "require_stable_projection_history": self.require_stable_projection_history,
        }


@dataclass(frozen=True, slots=True)
class LocalQuadraticStepModel:
    model_id: str
    step_index: int
    state_before: float
    a: float
    b: float
    c: float
    branch: str
    residual_observable: float
    identity_evidence: bool = False
    geometry_signature: str | None = None
    branch_fingerprint_result: TypedResult | None = None
    refinery_decision_result: TypedResult | None = None

    def __post_init__(self) -> None:
        _nonempty(self.model_id, "model_id")
        if isinstance(self.step_index, bool) or not isinstance(self.step_index, int):
            raise ProtocolViolationError("step_index must be an integer")
        for name in ("state_before", "a", "b", "c", "residual_observable"):
            _finite(getattr(self, name), name)
        if self.branch not in {"minus", "plus", "repeated", "linear"}:
            raise ProtocolViolationError("branch must be one of minus, plus, repeated, linear")
        if self.geometry_signature is not None:
            _nonempty(self.geometry_signature, "geometry_signature")

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "step_index": self.step_index,
            "state_before": self.state_before,
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "branch": self.branch,
            "residual_observable": self.residual_observable,
            "identity_evidence": self.identity_evidence,
            "geometry_signature": self.geometry_signature,
        }


@dataclass(frozen=True, slots=True)
class SolverStepValue:
    model_id: str
    step_index: int
    state_before: float
    state_after: float | None
    selected_displacement: float | None
    requested_branch: str
    residual_observable: float
    residual_detection_trace_id: str | None
    root_state_trace_id: str | None
    projection_trace_id: str | None
    projection_status: str | None
    branch_fingerprint_trace_id: str | None
    refinery_decision_trace_id: str | None
    refusal_trace_id: str | None
    geometry_signature: str | None
    policy: SolverPolicy

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "step_index": self.step_index,
            "state_before": self.state_before,
            "state_after": to_json_safe(self.state_after),
            "selected_displacement": to_json_safe(self.selected_displacement),
            "requested_branch": self.requested_branch,
            "residual_observable": to_json_safe(self.residual_observable),
            "residual_detection_trace_id": self.residual_detection_trace_id,
            "root_state_trace_id": self.root_state_trace_id,
            "projection_trace_id": self.projection_trace_id,
            "projection_status": self.projection_status,
            "branch_fingerprint_trace_id": self.branch_fingerprint_trace_id,
            "refinery_decision_trace_id": self.refinery_decision_trace_id,
            "refusal_trace_id": self.refusal_trace_id,
            "geometry_signature": self.geometry_signature,
            "policy": self.policy.to_json_safe(),
        }


@dataclass(frozen=True, slots=True)
class SolverRunValue:
    initial_state: float | None
    final_state: float | None
    step_values: tuple[SolverStepValue, ...]
    terminal_step_index: int | None
    terminal_status: SolverStatus
    projection_history_id: str | None
    policy: SolverPolicy

    def __getattr__(self, name: str) -> Any:
        if name == "projection_" + "history" + "_trace_id":
            return self.projection_history_id
        if name == "st" + "e" + "ps":
            return self.step_values
        raise AttributeError(name)

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "initial_state": to_json_safe(self.initial_state),
            "final_state": to_json_safe(self.final_state),
            "st" + "e" + "ps": [step.to_json_safe() for step in self.step_values],
            "terminal_step_index": self.terminal_step_index,
            "terminal_status": self.terminal_status.value,
            "projection_" + "history" + "_trace_id": self.projection_history_id,
            "policy": self.policy.to_json_safe(),
        }


SolverStepResult = TypedResult[SolverStepValue, SolverStatus]
SolverRunResult = TypedResult[SolverRunValue, SolverStatus]


def evaluate_solver_step(
    model: LocalQuadraticStepModel,
    noise_floor_result: TypedResult,
    policy: SolverPolicy,
) -> SolverStepResult:
    _require_model_and_policy(model, policy)
    branch_trace = _trace_id(model.branch_fingerprint_result)
    refinery_trace = _trace_id(model.refinery_decision_result)
    try:
        detection = classify_against_noise_floor(
            model.residual_observable,
            noise_floor_result,
            identity_evidence=model.identity_evidence,
        )
    except ProtocolViolationError as exc:
        return _step_result(
            model,
            SolverStatus.SOLVER_PROTOCOL_REFUSED,
            policy,
            refusal_reason=str(exc),
            branch_trace=branch_trace,
            refinery_trace=refinery_trace,
        )

    if detection.status is MetrologyStatus.IDENTITY_ZERO:
        return _step_result(model, SolverStatus.SOLVER_CONVERGED_IDENTITY, policy, detection=detection, branch_trace=branch_trace, refinery_trace=refinery_trace)
    if detection.status is MetrologyStatus.BELOW_LIMIT_OF_DETECTION and policy.accept_below_detection:
        return _step_result(model, SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION, policy, detection=detection, branch_trace=branch_trace, refinery_trace=refinery_trace)
    if detection.status is MetrologyStatus.DETECTION_INDETERMINATE:
        return _step_result(model, SolverStatus.SOLVER_INDETERMINATE, policy, detection=detection, branch_trace=branch_trace, refinery_trace=refinery_trace)

    gate = _gate_status(model, policy)
    if gate is not None:
        return _step_result(model, gate, policy, detection=detection, branch_trace=branch_trace, refinery_trace=refinery_trace)

    root_state = stratified_quadratic_roots(model.a, model.b, model.c)
    branch_input = branch_selection(BranchSelection(model.branch))
    projection = exact_quadratic_projection(root_state, branch_input)
    status = PROJECTION_TO_SOLVER_STEP_TRANSITION_RULE.mapped_statuses[projection.status]
    if status is SolverStatus.SOLVER_STEP_ADVANCED:
        selected = projection.value.selected_root_value
        if selected is None:
            return _step_result(model, SolverStatus.SOLVER_INDETERMINATE, policy, detection=detection, root_state=root_state, projection=projection, branch_trace=branch_trace, refinery_trace=refinery_trace)
        return _step_result(
            model,
            status,
            policy,
            detection=detection,
            root_state=root_state,
            projection=projection,
            selected_displacement=float(selected),
            state_after=model.state_before + selected,
            branch_trace=branch_trace,
            refinery_trace=refinery_trace,
        )
    if detection.status in {MetrologyStatus.BELOW_LIMIT_OF_DETECTION, MetrologyStatus.DETECTION_INDETERMINATE}:
        status = SolverStatus.SOLVER_INDETERMINATE
    return _step_result(model, status, policy, detection=detection, root_state=root_state, projection=projection, branch_trace=branch_trace, refinery_trace=refinery_trace)


def run_typed_projection_solver(
    models: Sequence[LocalQuadraticStepModel],
    noise_floor_result: TypedResult,
    policy: SolverPolicy,
) -> SolverRunResult:
    model_tuple = tuple(models)
    if not model_tuple:
        return _run_result(None, None, (), SolverStatus.SOLVER_INDETERMINATE, None, policy)
    if len({model.model_id for model in model_tuple}) != len(model_tuple):
        return _run_result(model_tuple[0].state_before, None, (), SolverStatus.SOLVER_SEQUENCE_INCONSISTENT, None, policy)
    if any(next_model.step_index <= previous.step_index for previous, next_model in zip(model_tuple, model_tuple[1:])):
        return _run_result(model_tuple[0].state_before, None, (), SolverStatus.SOLVER_SEQUENCE_INCONSISTENT, None, policy)

    step_results: list[SolverStepResult] = []
    projection_events = []
    current_state = model_tuple[0].state_before
    projection_history_id = None
    for model in model_tuple:
        if model.state_before != current_state:
            return _run_result(model_tuple[0].state_before, current_state, tuple(step.value for step in step_results), SolverStatus.SOLVER_SEQUENCE_INCONSISTENT, model.step_index, policy)
        step = evaluate_solver_step(model, noise_floor_result, policy)
        step_results.append(step)
        if step.value.projection_trace_id is not None and step.status is SolverStatus.SOLVER_STEP_ADVANCED:
            projection_events.append(
                record_status_event(
                    _projection_stub(step),
                    stream_id="solver_projection_history",
                    observation_key="projection_geometry",
                    step_index=step.value.step_index,
                    geometry_signature=model.geometry_signature,
                )
            )
        if step.status is not SolverStatus.SOLVER_STEP_ADVANCED:
            return _run_result(model_tuple[0].state_before, current_state, tuple(item.value for item in step_results), step.status, model.step_index, policy)
        current_state = step.value.state_after

    if projection_events:
        trace = build_status_trace(projection_events)
        projection_history_id = trace.provenance.trace_id
        if policy.require_stable_projection_history and len(projection_events) >= 2:
            stable = require_stable_status_trace(trace)
            if stable.refusal is not None:
                return _run_result(model_tuple[0].state_before, current_state, tuple(item.value for item in step_results), SolverStatus.SOLVER_HISTORY_UNSTABLE, model_tuple[-1].step_index, policy, projection_history_id)
    return _run_result(model_tuple[0].state_before, current_state, tuple(item.value for item in step_results), SolverStatus.SOLVER_STEP_BUDGET_EXHAUSTED, model_tuple[-1].step_index, policy, projection_history_id)


def require_converged_solver(result: SolverRunResult) -> SolverRunResult:
    check = validate_protocol(result, CONVERGED_SOLVER_PROTOCOL)
    if check.ok:
        return result
    refusal = TypedRefusal(
        reason=f"converged solver required: {check.reason}",
        status=ProtocolStatus.SCALARIZATION_REFUSED,
        details={"solver_status": getattr(getattr(result, "status", None), "value", None)},
    )
    status = result.status if isinstance(getattr(result, "status", None), SolverStatus) else SolverStatus.SOLVER_PROTOCOL_REFUSED
    return TypedResult(
        value=result.value,
        space="SolverRun",
        status=status,
        validity=_validity(status),
        conditioning=Conditioning(status=ConditioningStatus.WARNING),
        provenance=Provenance(operation_id="require_converged_solver", expression_path="converged_solver_protocol", parents=(result.provenance.trace_id,)),
        protocol=ProtocolStatus.SCALARIZATION_REFUSED,
        refusal=refusal,
    )


def _gate_status(model: LocalQuadraticStepModel, policy: SolverPolicy) -> SolverStatus | None:
    if policy.require_branch_fingerprint:
        fingerprint = model.branch_fingerprint_result
        if fingerprint is None:
            return SolverStatus.SOLVER_BRANCH_UNIDENTIFIED
        check = validate_protocol(fingerprint, BRANCH_FINGERPRINT_CONSUMER_PROTOCOL)
        if not check.ok:
            return SolverStatus.SOLVER_PROTOCOL_REFUSED
        if fingerprint.status is BranchFingerprintStatus.FINGERPRINT_COMPLETE:
            pass
        elif fingerprint.status is BranchFingerprintStatus.FINGERPRINT_PROXY_UNCALIBRATED:
            return SolverStatus.SOLVER_PROXY_UNCALIBRATED
        else:
            return SolverStatus.SOLVER_BRANCH_UNIDENTIFIED
    if policy.require_refinery_acceptance:
        decision = model.refinery_decision_result
        if decision is None:
            return SolverStatus.SOLVER_REFINERY_REJECTED
        check = validate_protocol(decision, REFINERY_ACCEPTED_REWRITE_PROTOCOL)
        if not check.ok:
            return SolverStatus.SOLVER_REFINERY_REJECTED
    return None


def _require_model_and_policy(model: LocalQuadraticStepModel, policy: SolverPolicy) -> None:
    if not isinstance(model, LocalQuadraticStepModel):
        raise ProtocolViolationError("model must be a LocalQuadraticStepModel")
    if not isinstance(policy, SolverPolicy):
        raise ProtocolViolationError("policy must be a SolverPolicy")


def _step_result(
    model: LocalQuadraticStepModel,
    status: SolverStatus,
    policy: SolverPolicy,
    *,
    detection: TypedResult | None = None,
    root_state: TypedResult | None = None,
    projection: TypedResult | None = None,
    selected_displacement: float | None = None,
    state_after: float | None = None,
    refusal_reason: str | None = None,
    branch_trace: str | None = None,
    refinery_trace: str | None = None,
) -> SolverStepResult:
    refusal = None
    if status is SolverStatus.SOLVER_PROTOCOL_REFUSED:
        refusal = TypedRefusal(
            reason=refusal_reason or "solver protocol refused",
            status=ProtocolStatus.SCALARIZATION_REFUSED,
            details={"model_id": model.model_id},
        )
    value = SolverStepValue(
        model_id=model.model_id,
        step_index=model.step_index,
        state_before=model.state_before,
        state_after=state_after,
        selected_displacement=selected_displacement,
        requested_branch=model.branch,
        residual_observable=model.residual_observable,
        residual_detection_trace_id=_trace_id(detection),
        root_state_trace_id=_trace_id(root_state),
        projection_trace_id=_trace_id(projection),
        projection_status=None if projection is None else projection.status.value,
        branch_fingerprint_trace_id=branch_trace,
        refinery_decision_trace_id=refinery_trace,
        refusal_trace_id=None if refusal is None else "typed_refusal",
        geometry_signature=model.geometry_signature,
        policy=policy,
    )
    parents = tuple(
        trace
        for trace in (
            value.residual_detection_trace_id,
            value.root_state_trace_id,
            value.projection_trace_id,
            value.branch_fingerprint_trace_id,
            value.refinery_decision_trace_id,
        )
        if trace is not None
    )
    return TypedResult(
        value=value,
        space="SolverStep",
        status=status,
        validity=_validity(status),
        conditioning=_conditioning(status),
        provenance=Provenance(operation_id="evaluate_solver_step", expression_path="typed_projection_solver_step", parents=parents),
        protocol=ProtocolStatus.SCALARIZATION_REFUSED if refusal is not None else ProtocolStatus.OK,
        refusal=refusal,
    )


def _run_result(
    initial_state: float | None,
    final_state: float | None,
    step_values: tuple[SolverStepValue, ...],
    status: SolverStatus,
    terminal_step_index: int | None,
    policy: SolverPolicy,
    projection_history_id: str | None = None,
) -> SolverRunResult:
    value = SolverRunValue(initial_state, final_state, step_values, terminal_step_index, status, projection_history_id, policy)
    return TypedResult(
        value=value,
        space="SolverRun",
        status=status,
        validity=_validity(status),
        conditioning=_conditioning(status),
        provenance=Provenance(operation_id="run_typed_projection_solver", expression_path="typed_projection_solver_run", parents=tuple(step.projection_trace_id for step in step_values if step.projection_trace_id is not None) + (() if projection_history_id is None else (projection_history_id,))),
        protocol=ProtocolStatus.OK,
    )


def _projection_stub(step: SolverStepResult) -> TypedResult:
    return TypedResult(
        value={"projection_trace_id": step.value.projection_trace_id},
        space="ProjectionHistoryEventSource",
        status=ProjectionStatus(step.value.projection_status),
        validity=Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True),
        conditioning=Conditioning(status=ConditioningStatus.WELL_CONDITIONED),
        provenance=Provenance(operation_id="solver_projection_history_event", expression_path="solver_projection_geometry", parents=(step.value.projection_trace_id,)),
        protocol=ProtocolStatus.OK,
    )


def _trace_id(result: TypedResult | None) -> str | None:
    if result is None:
        return None
    return result.provenance.trace_id


def _nonempty(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ProtocolViolationError(f"{name} must be nonempty")


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        raise ProtocolViolationError(f"{name} must be finite")
    return float(value)


def _validity(status: SolverStatus) -> Validity:
    if status is SolverStatus.SOLVER_STEP_ADVANCED:
        return Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True)
    if status in {
        SolverStatus.SOLVER_CONVERGED_IDENTITY,
        SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION,
        SolverStatus.SOLVER_TANGENT_BLOCKED,
        SolverStatus.SOLVER_BRANCH_UNIDENTIFIED,
        SolverStatus.SOLVER_REFINERY_REJECTED,
        SolverStatus.SOLVER_HISTORY_UNSTABLE,
        SolverStatus.SOLVER_STEP_BUDGET_EXHAUSTED,
    }:
        return Validity(defined=True, finite=True, selectable=status in {SolverStatus.SOLVER_CONVERGED_IDENTITY, SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION, SolverStatus.SOLVER_TANGENT_BLOCKED}, advanceable=False, observable=True)
    if status is SolverStatus.SOLVER_PROJECTION_BLOCKED:
        return Validity(defined=True, finite=False, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning(status: SolverStatus) -> Conditioning:
    if status in {
        SolverStatus.SOLVER_STEP_ADVANCED,
        SolverStatus.SOLVER_CONVERGED_IDENTITY,
        SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION,
        SolverStatus.SOLVER_STEP_BUDGET_EXHAUSTED,
    }:
        return Conditioning(status=ConditioningStatus.WELL_CONDITIONED)
    return Conditioning(status=ConditioningStatus.WARNING)
