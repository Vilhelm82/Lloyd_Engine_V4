import json

from lloyd_v4.core.status import SolverStatus
from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.solver import LocalQuadraticStepModel, SolverPolicy, evaluate_solver_step, require_converged_solver, run_typed_projection_solver


def test_solver_step_and_run_serialization_preserves_policy_and_traces() -> None:
    model = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, -3.0, 2.0, "minus", 1.0, geometry_signature="g")
    policy = SolverPolicy(require_stable_projection_history=True)
    step = evaluate_solver_step(model, declare_bk_noise_floor(0.1), policy)
    run = run_typed_projection_solver([model], declare_bk_noise_floor(0.1), policy)

    step_payload = step.to_json_safe()
    run_payload = run.to_json_safe()

    assert step_payload["status"] == SolverStatus.SOLVER_STEP_ADVANCED.value
    assert step_payload["value"]["policy"]["require_stable_projection_history"] is True
    assert step_payload["value"]["selected_displacement"] == 1.0
    assert step_payload["value"]["projection_trace_id"] is not None
    assert run_payload["value"]["steps"][0]["model_id"] == "m0"
    json.dumps(run_payload, allow_nan=False)


def test_require_converged_solver_refusal_serializes_without_recursive_results() -> None:
    model = LocalQuadraticStepModel("m0", 0, 0.0, 1.0, -3.0, 2.0, "minus", 1.0)
    run = run_typed_projection_solver([model], declare_bk_noise_floor(0.1), SolverPolicy())
    refused = require_converged_solver(run).to_json_safe()
    encoded = json.dumps(refused, allow_nan=False)

    assert refused["protocol"] == "scalarization_refused"
    assert "nonfinite_float" not in encoded
    assert "StratifiedQuadraticRootValue" not in encoded
    assert "ProjectionResultValue" not in encoded
