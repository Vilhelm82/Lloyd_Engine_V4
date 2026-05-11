from dataclasses import replace

from lloyd_v4.core.status import MetrologyStatus, SolverStatus
from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.primitives.projective_ratio import projective_ratio
from lloyd_v4.solver import LocalQuadraticStepModel, SolverPolicy, evaluate_solver_step


def test_identity_zero_residual_converges_before_projection() -> None:
    model = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, -3.0, 2.0, "minus", 0.0, identity_evidence=True)

    result = evaluate_solver_step(model, declare_bk_noise_floor(0.1), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_CONVERGED_IDENTITY
    assert result.value.residual_detection_trace_id is not None
    assert result.value.projection_trace_id is None


def test_below_detection_requires_explicit_policy_to_converge() -> None:
    model = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, -3.0, 2.0, "minus", 0.05)

    refused = evaluate_solver_step(model, declare_bk_noise_floor(0.1), SolverPolicy())
    accepted = evaluate_solver_step(model, declare_bk_noise_floor(0.1), SolverPolicy(accept_below_detection=True))

    assert refused.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert accepted.status is SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION


def test_below_detection_without_advance_is_indeterminate_not_identity() -> None:
    model = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, 0.0, 1.0, "minus", 0.05)

    result = evaluate_solver_step(model, declare_bk_noise_floor(0.1), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_INDETERMINATE


def test_detected_residual_proceeds_to_projection() -> None:
    model = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, -3.0, 2.0, "plus", 1.0)

    result = evaluate_solver_step(model, declare_bk_noise_floor(0.1), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_STEP_ADVANCED
    assert result.value.selected_displacement == 2.0


def test_wrong_family_noise_floor_evidence_is_protocol_refused() -> None:
    model = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, -3.0, 2.0, "minus", 1.0)

    result = evaluate_solver_step(model, projective_ratio(1, 2), SolverPolicy())

    assert result.status is SolverStatus.SOLVER_PROTOCOL_REFUSED
    assert result.refusal is not None
