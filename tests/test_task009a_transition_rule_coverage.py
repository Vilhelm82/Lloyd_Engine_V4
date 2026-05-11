from lloyd_v4.core.status import SolverStatus
from lloyd_v4.metrology import declare_bk_noise_floor, estimate_bk_noise_floor
from lloyd_v4.solver import LocalQuadraticStepModel, SolverPolicy, require_converged_solver, run_typed_projection_solver


def _model(model_id="m", step=0, state=0.0, a=1.0, b=0.0, c=-1.0, branch="plus", residual=1.0, identity=False):
    return LocalQuadraticStepModel(model_id, step, state, a, b, c, branch, residual, identity_evidence=identity)


def test_task009_named_transition_rules_are_exercised_by_public_scenarios() -> None:
    noise = declare_bk_noise_floor(0.1)
    cases = {
        "solver.residual_detection.to_solver identity": run_typed_projection_solver([_model(residual=0.0, identity=True)], noise, SolverPolicy()).status,
        "solver.residual_detection.to_solver below": run_typed_projection_solver([_model(residual=0.05)], noise, SolverPolicy(accept_below_detection=True)).status,
        "solver.residual_detection.to_solver indeterminate": run_typed_projection_solver([_model()], estimate_bk_noise_floor([]), SolverPolicy()).status,
        "solver.projection.to_solver_step advance": run_typed_projection_solver([_model()], noise, SolverPolicy()).status,
        "solver.projection.to_solver_step tangent": run_typed_projection_solver([_model(a=1.0, b=-2.0, c=1.0, branch="repeated")], noise, SolverPolicy()).status,
        "solver.projection.to_solver_step blocked": run_typed_projection_solver([_model(a=1.0, b=0.0, c=1.0)], noise, SolverPolicy()).status,
        "solver.projection.to_solver_step selection": run_typed_projection_solver([_model(branch="linear")], noise, SolverPolicy()).status,
        "solver.projection_history.require_stable pass": run_typed_projection_solver([_model("m0", 0, 0.0), _model("m1", 1, 1.0)], noise, SolverPolicy()).status,
        "solver.projection_history.require_stable block": run_typed_projection_solver(
            [_model("m0", 0, 0.0), LocalQuadraticStepModel("m1", 1, 1.0, 1.0, 0.0, -1.0, "plus", 1.0, geometry_signature="changed")],
            noise,
            SolverPolicy(),
        ).status,
    }
    converged = run_typed_projection_solver([_model(residual=0.0, identity=True, a=1.0, b=0.0, c=-1.0)], noise, SolverPolicy())
    refused = require_converged_solver(run_typed_projection_solver([_model()], noise, SolverPolicy()))

    assert cases["solver.residual_detection.to_solver identity"] is SolverStatus.SOLVER_CONVERGED_IDENTITY
    assert cases["solver.residual_detection.to_solver below"] is SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION
    assert cases["solver.residual_detection.to_solver indeterminate"] is SolverStatus.SOLVER_INDETERMINATE
    assert cases["solver.projection.to_solver_step advance"] is SolverStatus.SOLVER_STEP_BUDGET_EXHAUSTED
    assert cases["solver.projection.to_solver_step tangent"] is SolverStatus.SOLVER_TANGENT_BLOCKED
    assert cases["solver.projection.to_solver_step blocked"] is SolverStatus.SOLVER_PROJECTION_BLOCKED
    assert cases["solver.projection.to_solver_step selection"] is SolverStatus.SOLVER_SELECTION_REFUSED
    assert cases["solver.projection_history.require_stable pass"] is SolverStatus.SOLVER_STEP_BUDGET_EXHAUSTED
    assert cases["solver.projection_history.require_stable block"] is SolverStatus.SOLVER_HISTORY_UNSTABLE
    assert require_converged_solver(converged).refusal is None
    assert refused.refusal is not None
