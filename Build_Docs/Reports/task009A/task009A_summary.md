# Task 009A Summary

## Files created

- `tests/test_task009a_solver_status_coverage.py`
- `tests/test_task009a_projection_strata_scenarios.py`
- `tests/test_task009a_metrology_policy_scenarios.py`
- `tests/test_task009a_branch_refinery_gate_scenarios.py`
- `tests/test_task009a_history_and_sequence_scenarios.py`
- `tests/test_task009a_transition_rule_coverage.py`
- `tests/test_task009a_solver_serialization_regression.py`
- `tests/test_task009a_source_purity.py`
- `Build_Docs/Reports/task009A/task009A_summary.md`
- `Build_Docs/Reports/task009A/solver_scenario_matrix.md`
- `Build_Docs/Reports/task009A/design_decisions.md`
- `Build_Docs/Reports/task009A/status_coverage_matrix.md`
- `Build_Docs/Reports/task009A/transition_rule_coverage.md`

## Files modified

- `src/lloyd_v4/solver/typed_projection_solver.py`

## Scenario slice command and result

```text
python -m pytest tests/test_task009a_*.py -q
..........                                                               [100%]
```

## Full suite command and result

```text
python -m pytest tests -q
........................................................................ [ 33%]
........................................................................ [ 67%]
.....................................................................    [100%]
```

An additional standard run reported:

```text
213 passed in 0.28s
```

## Source audit commands and results

All required audits returned no matches:

```text
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance|confidence_score|weighted_score|smoothing|hysteresis|interpolate|extrapolate" src/lloyd_v4 -n
rg -i "lloyd_core|lloyd_core_nvar|lloyd_decomposition|hyperdual|halley|multi_start|route_score" src/lloyd_v4 -n
rg "lloyd_v4\.solver|from lloyd_v4\.solver|import .*solver" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery src/lloyd_v4/history -n
rg "TypedProjectionSolver|SolverStatus|solver_step|solver_converged|solver_projection|solver_branch|solver_refinery|solver_history" src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery src/lloyd_v4/history -n
rg "JetBundle|shape_operator|singularity|symmetry|centrifuge|surface_mesh|implicit_chart|finite_eta|domain_consumer|domain_classifier|bearing|aerospace|betting|scanner|parser|cas|symbolic_simplifier" src/lloyd_v4/solver -n
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

## Solver source fixes made

The scenario battery exposed two Task 009 solver bugs:

- Detection-indeterminate residual evidence was allowed to advance through projection. It now returns `solver_indeterminate`.
- Projection-history events erased projection status by recording a fixed transverse event. Solver steps now preserve projection status and history records the actual projection status.

## Unreachable status coverage

No unreachable `SolverStatus` remains. Every status is intentionally produced through public APIs in `tests/test_task009a_solver_status_coverage.py`.

## Deviations

No Task 010 behavior was added. The solver still consumes caller-supplied local quadratic models.

## Task 010 readiness

Task 010 remains ready to scope as `JetBundle` primitive and typed second-order local model extraction.
