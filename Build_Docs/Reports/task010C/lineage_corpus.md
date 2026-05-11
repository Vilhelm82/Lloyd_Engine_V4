# Lineage Corpus

## Runtime Corpus

- Total `TypedResult` instances captured during the measured full test session: 1595
- Distinct operation_ids encountered: 24
- Distinct status families encountered: 8
- Cycle audit result: 0 cycles

## Operation IDs

- `build_branch_fingerprint`
- `build_status_trace`
- `calibrate_proxy_kq`
- `classify_against_noise_floor`
- `compare_kq_slope_stability`
- `compare_slope_flow_to_models`
- `compare_status_events`
- `declare_bk_noise_floor`
- `estimate_bk_noise_floor`
- `evaluate_rewrite_candidate`
- `evaluate_solver_step`
- `exact_quadratic_projection`
- `projective_ratio`
- `projective_ratio.scalarize`
- `proxy_uncalibrated`
- `record_status_event`
- `require_accepted_rewrite`
- `require_converged_solver`
- `require_stable_status_trace`
- `require_valid_proxy_calibration`
- `run_typed_projection_solver`
- `solver_projection_history_event`
- `stratified_quadratic_roots`
- `stratified_quadratic_roots.select`

## Status Families

- `BranchFingerprintStatus`
- `HistoryStatus`
- `MetrologyStatus`
- `ProjectionStatus`
- `ProjectiveRatioStatus`
- `QuadraticRootStatus`
- `RefineryStatus`
- `SolverStatus`

## Per-Layer Breakdown

- `core`: 0
- `primitives`: 801
- `projection`: 118
- `metrology`: 230
- `branch`: 79
- `refinery`: 38
- `history`: 179
- `solver`: 150

## Longest Chain

- Longest observed chain depth: 34
- Representative chain:

```text
run_typed_projection_solver[SolverStatus]
-> exact_quadratic_projection[ProjectionStatus]
-> stratified_quadratic_roots[QuadraticRootStatus]
-> stratified_quadratic_roots.select[QuadraticRootStatus]
-> stratified_quadratic_roots[QuadraticRootStatus]
-> projective_ratio[ProjectiveRatioStatus]
-> projective_ratio.scalarize[ProjectiveRatioStatus]
-> projective_ratio[ProjectiveRatioStatus]
-> exact_quadratic_projection[ProjectionStatus]
-> stratified_quadratic_roots[QuadraticRootStatus]
-> stratified_quadratic_roots.select[QuadraticRootStatus]
-> stratified_quadratic_roots[QuadraticRootStatus]
-> projective_ratio[ProjectiveRatioStatus]
-> projective_ratio.scalarize[ProjectiveRatioStatus]
-> projective_ratio[ProjectiveRatioStatus]
-> build_status_trace[HistoryStatus]
-> record_status_event[HistoryStatus]
-> solver_projection_history_event[ProjectionStatus]
-> exact_quadratic_projection[ProjectionStatus]
-> stratified_quadratic_roots[QuadraticRootStatus]
-> stratified_quadratic_roots.select[QuadraticRootStatus]
-> stratified_quadratic_roots[QuadraticRootStatus]
-> projective_ratio[ProjectiveRatioStatus]
-> projective_ratio.scalarize[ProjectiveRatioStatus]
-> projective_ratio[ProjectiveRatioStatus]
-> record_status_event[HistoryStatus]
-> solver_projection_history_event[ProjectionStatus]
-> exact_quadratic_projection[ProjectionStatus]
-> stratified_quadratic_roots[QuadraticRootStatus]
-> stratified_quadratic_roots.select[QuadraticRootStatus]
-> stratified_quadratic_roots[QuadraticRootStatus]
-> projective_ratio[ProjectiveRatioStatus]
-> projective_ratio.scalarize[ProjectiveRatioStatus]
-> projective_ratio[ProjectiveRatioStatus]
```

## Terminals

Every observed chain terminal resolves to an operation declared in `calibrated_primitive_operations`.
