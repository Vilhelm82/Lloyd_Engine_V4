# Task 006 Status Transition Rules

## branch.slope_flow.model_comparison

- input protocol: `slope_flow_comparison`
- output protocol: `slope_flow_consumer`
- input status family: `BranchFingerprintStatus`
- output status family: `BranchFingerprintStatus`
- accepted statuses: `slope_flow_observed`, `slope_model_residuals`, `slope_model_unique_match`, `slope_model_ambiguous`, `slope_model_no_match`
- refused statuses: `slope_flow_insufficient_samples`, `slope_flow_indeterminate`, `slope_flow_proxy_uncalibrated`
- mapped statuses: none
- context keys: none
- notes: identifies which transfer-flow results are usable evidence for fingerprint composition.

## branch.kq_flow.require_stable

- input protocol: `kq_slope_stability`
- output protocol: `branch.kq_flow.require_stable`
- input status family: `BranchFingerprintStatus`
- output status family: none
- accepted statuses: `kq_flow_stable`
- refused statuses: `kq_flow_unstable`, `kq_flow_indeterminate`, `kq_flow_uncalibrated`
- mapped statuses: none
- context keys: none
- notes: proxy fingerprints require stable Kq flow.

## branch.projection_to_fingerprint

- input protocol: `projection_result_v4`
- output protocol: `branch_fingerprint`
- input status family: `ProjectionStatus`
- output status family: `BranchFingerprintStatus`
- accepted statuses: `projection_transverse`, `projection_tangent_contact`, `projection_linear`
- refused statuses: `projection_no_real_root`, `projection_identity`, `projection_no_solution`, `projection_selection_refused`
- mapped statuses: none
- context keys: none
- notes: tangent contact remains usable projection evidence but keeps `advance_valid=False`.

## branch.transfer_flow_to_fingerprint

- input protocol: `slope_flow_comparison`
- output protocol: `branch_fingerprint`
- input status family: `BranchFingerprintStatus`
- output status family: `BranchFingerprintStatus`
- accepted statuses: `slope_flow_observed`, `slope_model_residuals`, `slope_model_unique_match`
- refused statuses: `slope_flow_insufficient_samples`, `slope_flow_indeterminate`, `slope_flow_proxy_uncalibrated`
- mapped statuses:
  - `slope_model_ambiguous` -> `fingerprint_unidentified`
  - `slope_model_no_match` -> `fingerprint_unidentified`
- context keys: none
- notes: ambiguous and no-match model evidence is observable but unidentified.

## branch.compose_fingerprint

- input protocol: `branch_fingerprint`
- output protocol: `branch_fingerprint_consumer`
- input status family: `BranchFingerprintStatus`
- output status family: `BranchFingerprintStatus`
- accepted statuses: `fingerprint_complete`, `fingerprint_unidentified`, `fingerprint_incomplete`, `fingerprint_proxy_uncalibrated`
- refused statuses: none
- mapped statuses: none
- context keys: none
- notes: final evidence status is produced by named composition using projection, transfer-flow, and optional Kq-flow rules.
