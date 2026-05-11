from dataclasses import replace

from lloyd_v4.branch import SlopeFlowModel, SlopeFlowSample, build_branch_fingerprint, compare_slope_flow_to_models
from lloyd_v4.core.status import BranchFingerprintStatus, RefineryStatus, SolverStatus
from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.primitives.projective_ratio import projective_ratio
from lloyd_v4.primitives.stratified_quadratic_roots import stratified_quadratic_roots
from _projection_branch import project_with_branch
from lloyd_v4.refinery import evaluate_rewrite_candidate, snapshot_typed_result
from lloyd_v4.solver import LocalQuadraticStepModel, SolverPolicy, evaluate_solver_step


def _model(**kwargs):
    base = dict(model_id="m", step_index=0, state_before=0.0, a=1.0, b=0.0, c=-1.0, branch="plus", residual_observable=1.0)
    base.update(kwargs)
    return LocalQuadraticStepModel(**base)


def _fingerprint(status):
    projection = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")
    flow = compare_slope_flow_to_models(
        [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.0), SlopeFlowSample(4.0, 16.0)],
        [SlopeFlowModel("square", 2.0)],
        declared_model_band=0.1,
    )
    return replace(build_branch_fingerprint(projection, flow), status=status)


def _refinery(status):
    snapshot = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    return replace(evaluate_rewrite_candidate([snapshot], [snapshot], candidate_name="candidate"), status=status)


def test_branch_gate_disabled_complete_unidentified_incomplete_and_proxy_paths() -> None:
    noise = declare_bk_noise_floor(0.1)

    disabled = evaluate_solver_step(_model(), noise, SolverPolicy(require_branch_fingerprint=False))
    complete = evaluate_solver_step(_model(branch_fingerprint_result=_fingerprint(BranchFingerprintStatus.FINGERPRINT_COMPLETE)), noise, SolverPolicy(require_branch_fingerprint=True))
    unidentified = evaluate_solver_step(_model(branch_fingerprint_result=_fingerprint(BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED)), noise, SolverPolicy(require_branch_fingerprint=True))
    incomplete = evaluate_solver_step(_model(branch_fingerprint_result=_fingerprint(BranchFingerprintStatus.FINGERPRINT_INCOMPLETE)), noise, SolverPolicy(require_branch_fingerprint=True))
    proxy = evaluate_solver_step(_model(branch_fingerprint_result=_fingerprint(BranchFingerprintStatus.FINGERPRINT_PROXY_UNCALIBRATED)), noise, SolverPolicy(require_branch_fingerprint=True))

    assert disabled.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert complete.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert unidentified.status is SolverStatus.SOLVER_BRANCH_UNIDENTIFIED
    assert incomplete.status is SolverStatus.SOLVER_BRANCH_UNIDENTIFIED
    assert proxy.status is SolverStatus.SOLVER_PROXY_UNCALIBRATED


def test_refinery_gate_disabled_accepted_and_rejected_paths() -> None:
    noise = declare_bk_noise_floor(0.1)

    disabled = evaluate_solver_step(_model(refinery_decision_result=_refinery(RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT)), noise, SolverPolicy(require_refinery_acceptance=False))
    accepted = evaluate_solver_step(_model(refinery_decision_result=_refinery(RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG)), noise, SolverPolicy(require_refinery_acceptance=True))
    rejected = evaluate_solver_step(_model(refinery_decision_result=_refinery(RefineryStatus.REWRITE_INDETERMINATE_INSUFFICIENT_EVIDENCE)), noise, SolverPolicy(require_refinery_acceptance=True))

    assert disabled.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert accepted.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert rejected.status is SolverStatus.SOLVER_REFINERY_REJECTED
