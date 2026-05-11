from lloyd_v4.core.status import SolverStatus
from lloyd_v4.metrology import declare_bk_noise_floor, estimate_bk_noise_floor
from lloyd_v4.solver import LocalQuadraticStepModel, SolverPolicy, evaluate_solver_step, require_converged_solver, run_typed_projection_solver


def _model(residual, *, identity=False):
    return LocalQuadraticStepModel("m", 0, 0.0, 1.0, 0.0, -1.0, "plus", residual, identity_evidence=identity)


def test_identity_below_detection_detected_and_indeterminate_metrology_paths() -> None:
    noise = declare_bk_noise_floor(0.1)

    identity = evaluate_solver_step(_model(0.0, identity=True), noise, SolverPolicy())
    below_accepted = evaluate_solver_step(_model(0.05), noise, SolverPolicy(accept_below_detection=True))
    below_not_accepted = run_typed_projection_solver([_model(0.05)], noise, SolverPolicy(accept_below_detection=False))
    detected = evaluate_solver_step(_model(1.0), noise, SolverPolicy())
    indeterminate = evaluate_solver_step(_model(1.0), estimate_bk_noise_floor([]), SolverPolicy())

    assert identity.status is SolverStatus.SOLVER_CONVERGED_IDENTITY
    assert require_converged_solver(run_typed_projection_solver([_model(0.0, identity=True)], noise, SolverPolicy())).refusal is None
    assert below_accepted.status is SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION
    assert below_not_accepted.status is SolverStatus.SOLVER_STEP_BUDGET_EXHAUSTED
    assert detected.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert indeterminate.status is SolverStatus.SOLVER_INDETERMINATE
    assert require_converged_solver(run_typed_projection_solver([_model(1.0)], estimate_bk_noise_floor([]), SolverPolicy())).refusal is not None
