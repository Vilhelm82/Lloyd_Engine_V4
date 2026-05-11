from lloyd_v4.core.status import SolverStatus
from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.solver import LocalQuadraticStepModel, SolverPolicy, evaluate_solver_step


def _noise():
    return declare_bk_noise_floor(0.1)


def test_transverse_local_quadratic_projection_advances_by_selected_displacement() -> None:
    model = LocalQuadraticStepModel("m0", 0, 10.0, 1.0, -3.0, 2.0, "minus", 1.0)

    result = evaluate_solver_step(model, _noise(), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert result.value.selected_displacement == 1.0
    assert result.value.state_after == 11.0
    assert result.value.root_state_trace_id is not None
    assert result.value.projection_trace_id is not None


def test_linear_local_quadratic_projection_advances() -> None:
    model = LocalQuadraticStepModel("m0", 0, 5.0, 0.0, 2.0, -4.0, "linear", 1.0)

    result = evaluate_solver_step(model, _noise(), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert result.value.selected_displacement == 2.0
    assert result.value.state_after == 7.0


def test_tangent_contact_blocks_advancement() -> None:
    model = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, 2.0, 1.0, "repeated", 1.0)

    result = evaluate_solver_step(model, _noise(), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_TANGENT_BLOCKED
    assert result.value.state_after is None


def test_no_real_root_blocks_projection() -> None:
    model = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, 0.0, 1.0, "minus", 1.0)

    result = evaluate_solver_step(model, _noise(), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_PROJECTION_BLOCKED
    assert result.value.state_after is None


def test_incompatible_branch_returns_selection_refused() -> None:
    model = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, -3.0, 2.0, "linear", 1.0)

    result = evaluate_solver_step(model, _noise(), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_SELECTION_REFUSED
    assert result.value.state_after is None
