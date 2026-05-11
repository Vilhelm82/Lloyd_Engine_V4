# Manifest Completeness Findings

## Runtime Operation IDs Missing From The 010A/010B Operation Registry

These operation IDs appeared in the runtime corpus but were not covered by the 010B `operations` category:

- `projective_ratio.scalarize`: declared by `primitives`
- `stratified_quadratic_roots.select`: declared by `primitives`
- `solver_projection_history_event`: declared by `solver`

## Manifest Updates Made

- Added `projective_ratio.scalarize` to `primitives.internal_operations`.
- Added `stratified_quadratic_roots.select` to `primitives.internal_operations`.
- Added `solver_projection_history_event` to `solver.internal_operations`.

The terminal audit also required explicit calibrated primitive declarations for operations that can legitimately emit a `TypedResult` without a parent in the current substrate:

- `primitives.calibrated_primitive_operations`: `projective_ratio`, `stratified_quadratic_roots`
- `metrology.calibrated_primitive_operations`: `declare_bk_noise_floor`, `estimate_bk_noise_floor`, `proxy_uncalibrated`
- `branch.calibrated_primitive_operations`: `compare_slope_flow_to_models`
- `history.calibrated_primitive_operations`: `build_status_trace`
- `solver.calibrated_primitive_operations`: `evaluate_solver_step`, `run_typed_projection_solver`

## Final Registry State

All operation IDs in the captured substrate corpus are now present in the manifest through `operations`, `calibrated_primitive_operations`, or `internal_operations`.

No operation IDs in the substrate corpus were untraceable in source.
