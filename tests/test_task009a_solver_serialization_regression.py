import json

from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.solver import LocalQuadraticStepModel, SolverPolicy, evaluate_solver_step, run_typed_projection_solver


def test_solver_step_and_run_json_evidence_is_stable() -> None:
    model0 = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, 0.0, -1.0, "plus", 1.0, geometry_signature="g")
    model1 = LocalQuadraticStepModel("m1", 1, 1.0, 1.0, 0.0, -1.0, "plus", 1.0, geometry_signature="g")
    policy = SolverPolicy(require_stable_projection_history=True)

    step_payload = evaluate_solver_step(model0, declare_bk_noise_floor(0.1), policy).to_json_safe()
    run_payload = run_typed_projection_solver([model0, model1], declare_bk_noise_floor(0.1), policy).to_json_safe()

    assert step_payload["value"]["model_id"] == "m0"
    assert step_payload["value"]["state_before"] == 0.0
    assert step_payload["value"]["state_after"] == 1.0
    assert step_payload["value"]["requested_branch"] == "plus"
    assert step_payload["value"]["projection_trace_id"] is not None
    assert step_payload["value"]["residual_detection_trace_id"] is not None
    assert run_payload["value"]["terminal_status"] == "solver_step_budget_exhausted"
    assert run_payload["value"]["projection_history_trace_id"] is not None
    assert len(run_payload["value"]["steps"]) == 2
    json.dumps(run_payload, allow_nan=False)
