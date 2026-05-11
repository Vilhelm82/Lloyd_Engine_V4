from lloyd_v4.core.status import SolverStatus
from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.solver import LocalQuadraticStepModel, SolverPolicy, run_typed_projection_solver


def _model(model_id: str, step: int, state: float, branch: str = "minus", signature: str = "g"):
    return LocalQuadraticStepModel(model_id, step, state, 1.0, -3.0, 2.0, branch, 1.0, geometry_signature=signature)


def test_run_enforces_strict_step_order_and_state_continuity() -> None:
    unordered = run_typed_projection_solver([_model("m1", 1, 0.0), _model("m0", 0, 1.0)], declare_bk_noise_floor(0.1), SolverPolicy())
    repeated = run_typed_projection_solver([_model("m0", 0, 0.0), _model("m1", 0, 1.0)], declare_bk_noise_floor(0.1), SolverPolicy())
    discontinuous = run_typed_projection_solver([_model("m0", 0, 0.0), _model("m1", 1, 99.0)], declare_bk_noise_floor(0.1), SolverPolicy())

    assert unordered.status is SolverStatus.SOLVER_SEQUENCE_INCONSISTENT
    assert repeated.status is SolverStatus.SOLVER_SEQUENCE_INCONSISTENT
    assert discontinuous.status is SolverStatus.SOLVER_SEQUENCE_INCONSISTENT


def test_stable_projection_history_passes_and_budget_exhausts() -> None:
    result = run_typed_projection_solver(
        [_model("m0", 0, 0.0), _model("m1", 1, 1.0)],
        declare_bk_noise_floor(0.1),
        SolverPolicy(require_stable_projection_history=True),
    )

    assert result.status is SolverStatus.SOLVER_STEP_BUDGET_EXHAUSTED
    assert result.value.projection_history_trace_id is not None
    assert result.value.final_state == 2.0


def test_projection_history_transition_blocks_when_required() -> None:
    result = run_typed_projection_solver(
        [_model("m0", 0, 0.0, signature="a"), _model("m1", 1, 1.0, signature="b")],
        declare_bk_noise_floor(0.1),
        SolverPolicy(require_stable_projection_history=True),
    )

    assert result.status is SolverStatus.SOLVER_HISTORY_UNSTABLE


def test_single_projection_history_does_not_block_by_itself() -> None:
    result = run_typed_projection_solver([_model("m0", 0, 0.0)], declare_bk_noise_floor(0.1), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_STEP_BUDGET_EXHAUSTED


def test_empty_model_sequence_is_indeterminate() -> None:
    result = run_typed_projection_solver([], declare_bk_noise_floor(0.1), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_INDETERMINATE
