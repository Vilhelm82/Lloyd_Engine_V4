# Solver Status Coverage Matrix

| SolverStatus | public scenario |
| --- | --- |
| `solver_step_advanced` | detected residual with transverse projection |
| `solver_converged_identity` | zero residual with identity evidence |
| `solver_converged_below_detection` | below-detection residual with accepting policy |
| `solver_projection_blocked` | no-real-root projection |
| `solver_tangent_blocked` | repeated-root tangent projection |
| `solver_selection_refused` | incompatible branch request |
| `solver_branch_unidentified` | required unidentified or incomplete BranchFingerprint |
| `solver_proxy_uncalibrated` | required proxy-uncalibrated BranchFingerprint |
| `solver_refinery_rejected` | required non-accepted refinery decision |
| `solver_history_unstable` | projection-history status or geometry transition |
| `solver_sequence_inconsistent` | unordered sequence or state continuity mismatch |
| `solver_step_budget_exhausted` | valid finite advance budget consumed |
| `solver_protocol_refused` | wrong-family noise-floor evidence |
| `solver_indeterminate` | indeterminate residual metrology evidence |

Every status is produced through public APIs. No status is unreachable.
