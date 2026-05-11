# Status Transition Rules

## projective_ratio.scalarization

- input protocol: `projective_ratio`
- output/consumer protocol: `projective_ratio_scalarization`
- input status family: `ProjectiveRatioStatus`
- output status family: none
- accepted statuses: `finite_ratio`, `signed_zero`
- refused statuses: `infinite_direction`, `indeterminate`
- mapped statuses: none
- context keys: none
- notes: preserves Task 001 scalarization behavior.

## quadratic_roots.selection

- input protocol: `stratified_quadratic_roots`
- output/consumer protocol: `quadratic_root_selection`
- input status family: `QuadraticRootStatus`
- output status family: none
- accepted statuses: `two_real_roots`, `repeated_root`, `linear_root`
- refused statuses: `no_real_root`, `constant_identity`, `constant_no_solution`
- mapped statuses: none
- context keys: `branch`
- notes: branch compatibility remains contextual and enforced by Task 002 selection.

## quadratic_roots.to_exact_projection

- input protocol: `stratified_quadratic_roots`
- output/consumer protocol: `projection_result_v4`
- input status family: `QuadraticRootStatus`
- output status family: `ProjectionStatus`
- accepted statuses: none
- refused statuses: none
- mapped statuses:
  - `two_real_roots` -> `projection_transverse` for compatible `minus` or `plus`, otherwise `projection_selection_refused`
  - `repeated_root` -> `projection_tangent_contact` for compatible `repeated`, otherwise `projection_selection_refused`
  - `linear_root` -> `projection_linear` for compatible `linear`, otherwise `projection_selection_refused`
  - `no_real_root` -> `projection_no_real_root`
  - `constant_identity` -> `projection_identity`
  - `constant_no_solution` -> `projection_no_solution`
- context keys: `branch`
- notes: preserves tangent-contact and identity semantics from Task 003.

## metrology.noise_floor.limit_of_detection

- input protocol: `b_k_noise_floor`
- output/consumer protocol: `limit_of_detection`
- input status family: `MetrologyStatus`
- output status family: `MetrologyStatus`
- accepted statuses: none
- refused statuses: none
- mapped statuses:
  - `noise_floor_declared` -> contextual `detected`, `below_limit_of_detection`, `detection_indeterminate`, or `identity_zero`
  - `noise_floor_estimated` -> contextual `detected`, `below_limit_of_detection`, `detection_indeterminate`, or `identity_zero`
  - `noise_floor_indeterminate` -> `detection_indeterminate`
- context keys: `observable`, `noise_floor`, `identity_evidence`
- notes: metrology classifies observability only and does not alter exact algebraic strata.

## metrology.proxy_calibration.require_valid

- input protocol: `kq_proxy_calibration`
- output/consumer protocol: `valid_proxy_calibration`
- input status family: `MetrologyStatus`
- output status family: none
- accepted statuses: `calibration_valid`
- refused statuses: `calibration_invalid`, `calibration_indeterminate`, `proxy_uncalibrated`
- mapped statuses: none
- context keys: none
- notes: pointwise valid Kq evidence only; no slope-flow stability or branch inference.
