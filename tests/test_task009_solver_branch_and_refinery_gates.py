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
    base = dict(model_id="m0", step_index=0, state_before=0.0, a=1.0, b=-3.0, c=2.0, branch="minus", residual_observable=1.0)
    base.update(kwargs)
    return LocalQuadraticStepModel(**base)


def _fingerprint(status: str = "complete"):
    projection = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")
    if status == "unidentified":
        flow = compare_slope_flow_to_models(
            [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.0), SlopeFlowSample(4.0, 16.0)],
            [SlopeFlowModel("a", 2.0), SlopeFlowModel("b", 2.0)],
            declared_model_band=0.1,
        )
    else:
        flow = compare_slope_flow_to_models(
            [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.0), SlopeFlowSample(4.0, 16.0)],
            [SlopeFlowModel("square", 2.0)],
            declared_model_band=0.1,
        )
    result = build_branch_fingerprint(projection, flow, observable_kind="proxy" if status == "proxy" else "direct_transfer")
    if status == "incomplete":
        return replace(result, status=BranchFingerprintStatus.FINGERPRINT_INCOMPLETE)
    return result


def _refinery(status: RefineryStatus):
    snapshot = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    result = evaluate_rewrite_candidate([snapshot], [replace(snapshot, label="candidate", value_fingerprint={**snapshot.value_fingerprint})], candidate_name="candidate")
    return replace(result, status=status)


def test_required_branch_fingerprint_complete_passes() -> None:
    result = evaluate_solver_step(
        _model(branch_fingerprint_result=_fingerprint()),
        declare_bk_noise_floor(0.1),
        SolverPolicy(require_branch_fingerprint=True),
    )

    assert result.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert result.value.branch_fingerprint_trace_id is not None


def test_required_branch_fingerprint_unidentified_or_incomplete_blocks() -> None:
    for fingerprint in [_fingerprint("unidentified"), _fingerprint("incomplete")]:
        result = evaluate_solver_step(
            _model(branch_fingerprint_result=fingerprint),
            declare_bk_noise_floor(0.1),
            SolverPolicy(require_branch_fingerprint=True),
        )
        assert result.status is SolverStatus.SOLVER_BRANCH_UNIDENTIFIED


def test_required_proxy_uncalibrated_fingerprint_blocks() -> None:
    result = evaluate_solver_step(
        _model(branch_fingerprint_result=_fingerprint("proxy")),
        declare_bk_noise_floor(0.1),
        SolverPolicy(require_branch_fingerprint=True),
    )

    assert result.status is SolverStatus.SOLVER_PROXY_UNCALIBRATED


def test_required_refinery_accepted_passes_and_other_statuses_reject() -> None:
    accepted = evaluate_solver_step(
        _model(refinery_decision_result=_refinery(RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG)),
        declare_bk_noise_floor(0.1),
        SolverPolicy(require_refinery_acceptance=True),
    )
    rejected = evaluate_solver_step(
        _model(refinery_decision_result=_refinery(RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT)),
        declare_bk_noise_floor(0.1),
        SolverPolicy(require_refinery_acceptance=True),
    )

    assert accepted.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert rejected.status is SolverStatus.SOLVER_REFINERY_REJECTED
