from lloyd_v4.core.status import SolverStatus
from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.solver import LocalQuadraticStepModel, SolverPolicy, run_typed_projection_solver


def _model(model_id, step, state, *, branch="plus", a=1.0, b=0.0, c=-1.0, signature="g"):
    return LocalQuadraticStepModel(model_id, step, state, a, b, c, branch, 1.0, geometry_signature=signature)


def test_stable_history_geometry_history_and_sequence_cases() -> None:
    noise = declare_bk_noise_floor(0.1)

    stable = run_typed_projection_solver([_model("m0", 0, 0.0), _model("m1", 1, 1.0)], noise, SolverPolicy(require_stable_projection_history=True))
    geometry_changed = run_typed_projection_solver([_model("m0", 0, 0.0, signature="a"), _model("m1", 1, 1.0, signature="b")], noise, SolverPolicy(require_stable_projection_history=True))
    unordered = run_typed_projection_solver([_model("m1", 1, 0.0), _model("m0", 0, 1.0)], noise, SolverPolicy())
    continuity = run_typed_projection_solver([_model("m0", 0, 0.0), _model("m1", 1, 999.0)], noise, SolverPolicy())
    exhausted = run_typed_projection_solver([_model("m0", 0, 0.0)], noise, SolverPolicy())

    assert stable.status is SolverStatus.SOLVER_STEP_BUDGET_EXHAUSTED
    assert stable.value.projection_history_trace_id is not None
    assert geometry_changed.status is SolverStatus.SOLVER_HISTORY_UNSTABLE
    assert unordered.status is SolverStatus.SOLVER_SEQUENCE_INCONSISTENT
    assert continuity.status is SolverStatus.SOLVER_SEQUENCE_INCONSISTENT
    assert exhausted.status is SolverStatus.SOLVER_STEP_BUDGET_EXHAUSTED


def test_projection_status_change_is_history_unstable_when_required() -> None:
    noise = declare_bk_noise_floor(0.1)
    result = run_typed_projection_solver(
        [
            _model("m0", 0, 0.0, branch="plus", a=1.0, b=0.0, c=-1.0, signature="same"),
            _model("m1", 1, 1.0, branch="linear", a=0.0, b=1.0, c=-1.0, signature="same"),
        ],
        noise,
        SolverPolicy(require_stable_projection_history=True),
    )

    assert result.status is SolverStatus.SOLVER_HISTORY_UNSTABLE
