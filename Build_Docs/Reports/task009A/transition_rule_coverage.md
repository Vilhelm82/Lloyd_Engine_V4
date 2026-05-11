# Task 009 Transition Rule Coverage

| rule id | positive cases tested | blocking/mapped cases tested | test files | notes |
| --- | --- | --- | --- | --- |
| `solver.residual_detection.to_solver` | identity convergence, below-detection convergence, detected continuation | detection indeterminate | `test_task009a_metrology_policy_scenarios.py`, `test_task009a_transition_rule_coverage.py` | Below-detection behavior is policy-controlled. |
| `solver.projection.to_solver_step` | transverse and linear advance | tangent block, projection block, selection refusal | `test_task009a_projection_strata_scenarios.py`, `test_task009a_transition_rule_coverage.py` | Covers Task 003 projection strata. |
| `solver.branch_fingerprint.require_complete` | complete fingerprint pass | unidentified, incomplete, proxy uncalibrated | `test_task009a_branch_refinery_gate_scenarios.py` | Gate only active when policy requires it. |
| `solver.refinery.require_accepted` | accepted refinery decision pass | equivalent and indeterminate refinery statuses reject | `test_task009a_branch_refinery_gate_scenarios.py` | Gate only active when policy requires it. |
| `solver.projection_history.require_stable` | stable projection history pass | projection status transition and geometry transition block | `test_task009a_history_and_sequence_scenarios.py`, `test_task009a_transition_rule_coverage.py` | History tracks projection geometry only. |
| `solver.run.require_converged` | identity convergence accepted | budget-exhausted run refused | `test_task009a_metrology_policy_scenarios.py`, `test_task009a_transition_rule_coverage.py` | Below-detection convergence is also covered by status tests. |
