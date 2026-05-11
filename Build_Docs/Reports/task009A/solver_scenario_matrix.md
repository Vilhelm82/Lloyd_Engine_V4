# Solver Scenario Matrix

| scenario id | scenario name | input condition | policy settings | expected SolverStatus | actual SolverStatus | notes |
| --- | --- | --- | --- | --- | --- | --- |
| A | Clean transverse advance | two-real-root model, compatible branch, detected residual | default | `solver_step_advanced` | `solver_step_advanced` | selected projection trace preserved |
| B | Clean linear advance | linear model, linear branch, detected residual | default | `solver_step_advanced` | `solver_step_advanced` | Task 003 linear projection semantics used |
| C | Identity convergence | zero residual with identity evidence | default | `solver_converged_identity` | `solver_converged_identity` | accepted by converged-solver protocol |
| D | Below-detection policy split | below-limit residual | accept true versus false | true: `solver_converged_below_detection`; false: non-converged continuation | matched | proves policy-controlled termination |
| E | Detection indeterminate | indeterminate noise-floor evidence | default | `solver_indeterminate` | `solver_indeterminate` | source fix added |
| F | Tangent contact | repeated-root tangent model | default | `solver_tangent_blocked` | `solver_tangent_blocked` | no state advance |
| G1 | No real root | no-real-root model | default | `solver_projection_blocked` | `solver_projection_blocked` | projection evidence preserved |
| G2 | Constant identity | constant identity model | default | `solver_projection_blocked` | `solver_projection_blocked` | no fake scalar step |
| G3 | Constant no solution | constant no-solution model | default | `solver_projection_blocked` | `solver_projection_blocked` | no fake scalar step |
| H | Selection refused | selectable model, incompatible branch | default | `solver_selection_refused` | `solver_selection_refused` | Task 002/003 refusal path |
| I | Branch gate disabled | missing branch evidence | branch gate false | `solver_step_advanced` | `solver_step_advanced` | absence does not block |
| J | Branch gate complete | complete fingerprint | branch gate true | `solver_step_advanced` | `solver_step_advanced` | gate passes |
| K | Branch gate unidentified/incomplete | unidentified or incomplete fingerprint | branch gate true | `solver_branch_unidentified` | `solver_branch_unidentified` | blocks as typed branch evidence |
| L | Branch gate proxy uncalibrated | proxy-uncalibrated fingerprint | branch gate true | `solver_proxy_uncalibrated` | `solver_proxy_uncalibrated` | blocks proxy path |
| M | Refinery gate disabled | non-accepted refinery evidence | refinery gate false | `solver_step_advanced` | `solver_step_advanced` | absence/rejection does not block |
| N | Refinery accepted | accepted same-geometry lower-slag evidence | refinery gate true | `solver_step_advanced` | `solver_step_advanced` | gate passes |
| O | Refinery rejected | non-accepted refinery status | refinery gate true | `solver_refinery_rejected` | `solver_refinery_rejected` | gate blocks |
| P | Stable projection history | two accepted projections, same signature/status | stable history true | `solver_step_budget_exhausted` | `solver_step_budget_exhausted` | history trace serialized |
| Q | Projection status transition | transverse then linear projection, same signature | stable history true | `solver_history_unstable` | `solver_history_unstable` | source fix added |
| R | Projection geometry transition | same projection status, different signature | stable history true | `solver_history_unstable` | `solver_history_unstable` | signature transition caught |
| S | Unordered or repeated sequence | non-increasing step indices | default | `solver_sequence_inconsistent` | `solver_sequence_inconsistent` | no sorting |
| T | State continuity mismatch | next state_before differs exactly | default | `solver_sequence_inconsistent` | `solver_sequence_inconsistent` | no approximate equality |
| U | Budget exhausted | finite valid advance sequence, no convergence | default | `solver_step_budget_exhausted` | `solver_step_budget_exhausted` | explicit terminal evidence |
| V | Wrong-family evidence | wrong-family noise-floor evidence | default | `solver_protocol_refused` | `solver_protocol_refused` | typed refusal preserved |
