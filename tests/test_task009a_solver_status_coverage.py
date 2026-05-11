from dataclasses import replace

from lloyd_v4.branch import SlopeFlowModel, SlopeFlowSample, build_branch_fingerprint, compare_slope_flow_to_models
from lloyd_v4.core.status import BranchFingerprintStatus, RefineryStatus, SolverStatus
from lloyd_v4.history import build_status_trace
from lloyd_v4.metrology import declare_bk_noise_floor, estimate_bk_noise_floor
from lloyd_v4.primitives.projective_ratio import projective_ratio
from lloyd_v4.primitives.stratified_quadratic_roots import stratified_quadratic_roots
from _projection_branch import project_with_branch
from lloyd_v4.refinery import evaluate_rewrite_candidate, snapshot_typed_result
from lloyd_v4.solver import LocalQuadraticStepModel, SolverPolicy, evaluate_solver_step, run_typed_projection_solver


def _noise():
    return declare_bk_noise_floor(0.1)


def _model(model_id="m", step=0, state=0.0, a=1.0, b=0.0, c=-1.0, branch="plus", residual=1.0, **kwargs):
    return LocalQuadraticStepModel(model_id, step, state, a, b, c, branch, residual, **kwargs)


def _fingerprint(status: BranchFingerprintStatus):
    projection = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")
    flow = compare_slope_flow_to_models(
        [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.0), SlopeFlowSample(4.0, 16.0)],
        [SlopeFlowModel("square", 2.0)],
        declared_model_band=0.1,
    )
    fingerprint = build_branch_fingerprint(projection, flow)
    return replace(fingerprint, status=status)


def _refinery(status: RefineryStatus):
    snapshot = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    decision = evaluate_rewrite_candidate([snapshot], [snapshot], candidate_name="candidate")
    return replace(decision, status=status)


def test_every_solver_status_is_intentionally_produced() -> None:
    produced = {
        evaluate_solver_step(_model(), _noise(), SolverPolicy()).status,
        evaluate_solver_step(_model(residual=0.0, identity_evidence=True), _noise(), SolverPolicy()).status,
        evaluate_solver_step(_model(residual=0.05), _noise(), SolverPolicy(accept_below_detection=True)).status,
        evaluate_solver_step(_model(a=1.0, b=0.0, c=1.0), _noise(), SolverPolicy()).status,
        evaluate_solver_step(_model(a=1.0, b=-2.0, c=1.0, branch="repeated"), _noise(), SolverPolicy()).status,
        evaluate_solver_step(_model(branch="linear"), _noise(), SolverPolicy()).status,
        evaluate_solver_step(
            _model(branch_fingerprint_result=_fingerprint(BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED)),
            _noise(),
            SolverPolicy(require_branch_fingerprint=True),
        ).status,
        evaluate_solver_step(
            _model(branch_fingerprint_result=_fingerprint(BranchFingerprintStatus.FINGERPRINT_PROXY_UNCALIBRATED)),
            _noise(),
            SolverPolicy(require_branch_fingerprint=True),
        ).status,
        evaluate_solver_step(
            _model(refinery_decision_result=_refinery(RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT)),
            _noise(),
            SolverPolicy(require_refinery_acceptance=True),
        ).status,
        run_typed_projection_solver(
            [_model("m0", 0, 0.0, geometry_signature="a"), _model("m1", 1, 1.0, geometry_signature="b")],
            _noise(),
            SolverPolicy(require_stable_projection_history=True),
        ).status,
        run_typed_projection_solver([_model("m1", 1, 0.0), _model("m0", 0, 1.0)], _noise(), SolverPolicy()).status,
        run_typed_projection_solver([_model()], _noise(), SolverPolicy()).status,
        evaluate_solver_step(_model(), projective_ratio(1, 2), SolverPolicy()).status,
        evaluate_solver_step(_model(a=1.0, b=0.0, c=1.0, residual=1.0), estimate_bk_noise_floor([]), SolverPolicy()).status,
    }

    assert produced == set(SolverStatus)
