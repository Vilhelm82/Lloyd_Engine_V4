# Layer Manifest

This manifest renders the current V4 layers, their parent layers, and the concepts they provide. The sibling `layer_manifest.json` is the normative machine-readable source; this Markdown is the human-readable rendering and keeps the same category order.

## core

Core typed substrate.

### Parents

- none

### Provides

- Status families: `DomainStatus`, `StratumStatus`, `ValidityStatus`, `ConditioningStatus`, `ProtocolStatus`, `ProvenanceStatus`.
- Value types: `TypedResult`, `TypedRefusal`, `Validity`, `Conditioning`, `Provenance`.
- Protocol types: `ProducerProtocol`, `ConsumerProtocol`, `ProtocolCheck`.
- Transition types: `StatusTransitionRule`, `TransitionDisposition`, `StatusTransitionOutcome`.
- Errors and utilities: `LloydV4Error`, `ProtocolViolationError`, `ScalarizationError`, `HiddenGuardRailError`, `UnhandledStratumError`, `StatusCode`, `join_statuses`, `propagate_invalid`, `require_handled_status`, `require_protocol_ok`, `to_json_safe`.
- Operations: `validate_protocol`, `apply_status_transition`, `assert_transition_rule_complete`.
- Calibrated primitive operations: none.
- Internal operations: none.
- All exports: `StatusTransitionOutcome`, `StatusTransitionRule`, `TransitionDisposition`, `apply_status_transition`, `assert_transition_rule_complete`.

## primitives

Layer 1 primitive geometric operations.

### Parents

- `core`

### Provides

- Status families: `CollectionStatus`, `ValueStatus`, `ProjectiveRatioStatus`, `QuadraticRootStatus`, `TransferStatus`, `SlopeStatus`, `AlphaProbeStatus`, `ScalarAlphaJetBundleStatus`, `SingularAlphaJetBundleStatus`.
- Value types: `TypedCollectionValue`, `TypedCollectionResult`, `TypedValueValue`, `TypedValueResult`, `ProjectiveRatioValue`, `ProjectiveRatioResult`, `QuadraticCoefficients`, `QuadraticRootCoordinate`, `StratifiedQuadraticRootValue`, `QuadraticRootStateResult`, `TransferObservation`, `TransferObservationResult`, `LogLogSlopeObservation`, `LogLogSlopeResult`, `DeclaredAlphaModel`, `AlphaWindowFit`, `AlphaWindowStabilityStatus`, `AlphaProbeObservation`, `AlphaProbeResult`, `ScalarAlphaJetBundleObservation`, `ScalarAlphaJetBundleResult`, `SingularAlphaJetBundleObservation`, `SingularAlphaJetBundleResult`.
- Protocol types: `NON_EMPTY_TYPED_COLLECTION_PROTOCOL`, `NON_NULL_TYPED_VALUE_PROTOCOL`, `TYPED_COLLECTION_PROTOCOL`, `TYPED_VALUE_PROTOCOL`, `PROJECTIVE_RATIO_PROTOCOL`, `PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL`, `STRATIFIED_QUADRATIC_ROOTS_PROTOCOL`, `QUADRATIC_ROOT_SELECTION_PROTOCOL`, `TYPED_FINITE_DIFFERENCE_PROTOCOL`, `TRANSFER_OBSERVATION_CONSUMER_PROTOCOL`, `TYPED_LOG_LOG_SLOPE_PROTOCOL`, `LOG_LOG_SLOPE_CONSUMER_PROTOCOL`, `DIRECTIONAL_ALPHA_PROBE_PROTOCOL`, `ALPHA_PROBE_CONSUMER_PROTOCOL`, `SCALAR_ALPHA_JET_BUNDLE_PROTOCOL`, `SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL`, `SINGULAR_ALPHA_JET_BUNDLE_PROTOCOL`, `SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL`.
- Transition types: `PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE`, `QUADRATIC_ROOT_SELECTION_TRANSITION_RULE`.
- Errors and utilities: `PROJECTIVE_RATIO_SPACE`, `QUADRATIC_ROOT_SPACE`, `SCALAR_SPACE`, `BRANCHES_BY_STATUS`, `TRANSFER_SPACE`, `LOG_LOG_SLOPE_SPACE`, `ALPHA_PROBE_SPACE`, `K_BOUNDARY`, `K_DRIFT`, `ALPHA_NUMERIC_FLOOR`, `DEFAULT_ALPHA_MATERIALITY`, `MIN_WINDOW_POINTS`, `MIN_WINDOW_COUNT`, `SCALAR_ALPHA_JET_BUNDLE_SPACE`, `SINGULAR_ALPHA_JET_BUNDLE_SPACE`.
- Operations: `typed_collection`, `typed_value`, `projective_ratio`, `scalarize_projective_ratio`, `stratified_quadratic_roots`, `select_quadratic_root`, `typed_finite_difference`, `typed_log_log_slope`, `directional_alpha_probe`, `scalar_alpha_jet_bundle`, `singular_alpha_jet_bundle`.
- Calibrated primitive operations: `typed_collection`, `typed_value`, `projective_ratio`, `stratified_quadratic_roots`, `typed_finite_difference`, `directional_alpha_probe`, `scalar_alpha_jet_bundle`, `singular_alpha_jet_bundle`.
- Internal operations: `projective_ratio.scalarize`, `stratified_quadratic_roots.select`, `typed_log_log_slope`.
- All exports: `ALPHA_NUMERIC_FLOOR`, `ALPHA_PROBE_CONSUMER_PROTOCOL`, `ALPHA_PROBE_SPACE`, `AlphaProbeObservation`, `AlphaProbeResult`, `AlphaWindowFit`, `AlphaWindowStabilityStatus`, `DEFAULT_ALPHA_MATERIALITY`, `DIRECTIONAL_ALPHA_PROBE_PROTOCOL`, `DeclaredAlphaModel`, `K_BOUNDARY`, `K_DRIFT`, `LOG_LOG_SLOPE_CONSUMER_PROTOCOL`, `LOG_LOG_SLOPE_SPACE`, `LogLogSlopeObservation`, `LogLogSlopeResult`, `MIN_WINDOW_COUNT`, `MIN_WINDOW_POINTS`, `NON_EMPTY_TYPED_COLLECTION_PROTOCOL`, `NON_NULL_TYPED_VALUE_PROTOCOL`, `PROJECTIVE_RATIO_PROTOCOL`, `PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL`, `PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE`, `ProjectiveRatioResult`, `ProjectiveRatioValue`, `QUADRATIC_ROOT_SELECTION_PROTOCOL`, `QUADRATIC_ROOT_SELECTION_TRANSITION_RULE`, `SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL`, `SCALAR_ALPHA_JET_BUNDLE_PROTOCOL`, `SCALAR_ALPHA_JET_BUNDLE_SPACE`, `SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL`, `SINGULAR_ALPHA_JET_BUNDLE_PROTOCOL`, `SINGULAR_ALPHA_JET_BUNDLE_SPACE`, `STRATIFIED_QUADRATIC_ROOTS_PROTOCOL`, `ScalarAlphaJetBundleObservation`, `ScalarAlphaJetBundleResult`, `SingularAlphaJetBundleObservation`, `SingularAlphaJetBundleResult`, `TRANSFER_OBSERVATION_CONSUMER_PROTOCOL`, `TRANSFER_SPACE`, `TYPED_COLLECTION_PROTOCOL`, `TYPED_FINITE_DIFFERENCE_PROTOCOL`, `TYPED_LOG_LOG_SLOPE_PROTOCOL`, `TYPED_VALUE_PROTOCOL`, `QuadraticCoefficients`, `QuadraticRootCoordinate`, `QuadraticRootStateResult`, `StratifiedQuadraticRootValue`, `TransferObservation`, `TransferObservationResult`, `TypedCollectionResult`, `TypedCollectionValue`, `TypedValueResult`, `TypedValueValue`, `directional_alpha_probe`, `projective_ratio`, `scalar_alpha_jet_bundle`, `scalarize_projective_ratio`, `select_quadratic_root`, `singular_alpha_jet_bundle`, `stratified_quadratic_roots`, `typed_collection`, `typed_finite_difference`, `typed_log_log_slope`, `typed_value`.

## projection

Layer 1.5 exact quadratic projection consumer.

### Parents

- `core`
- `primitives`

### Provides

- Status families: `ProjectionStatus`.
- Value types: `BranchSelectionValue`, `BranchSelectionResult`, `ProjectionResultValue`, `ProjectionResultV4`.
- Protocol types: `BRANCH_SELECTION_PROTOCOL`, `BRANCH_SELECTION_CONSUMER_PROTOCOL`, `EXACT_QUADRATIC_PROJECTION_PROTOCOL`, `PROJECTION_RESULT_V4_PROTOCOL`.
- Transition types: `QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE`.
- Errors and utilities: none.
- Operations: `branch_selection`, `exact_quadratic_projection`.
- Calibrated primitive operations: none.
- Internal operations: none.
- All exports: `BRANCH_SELECTION_CONSUMER_PROTOCOL`, `BRANCH_SELECTION_PROTOCOL`, `BranchSelection`, `BranchSelectionResult`, `BranchSelectionValue`, `EXACT_QUADRATIC_PROJECTION_PROTOCOL`, `PROJECTION_RESULT_V4_PROTOCOL`, `QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE`, `ProjectionResultV4`, `ProjectionResultValue`, `branch_selection`, `exact_quadratic_projection`.

## metrology

Layer 2 finite-observation and proxy calibration evidence.

### Parents

- `core`
- `primitives`

### Provides

- Status families: `MetrologyStatus`.
- Value types: `NoiseFloorValue`, `NoiseFloorResult`, `LimitOfDetectionValue`, `LimitOfDetectionResult`, `ProxyCalibrationValue`, `ProxyCalibrationResult`, `ValidProxyCalibrationValue`.
- Protocol types: `B_K_NOISE_FLOOR_PROTOCOL`, `LIMIT_OF_DETECTION_PROTOCOL`, `KQ_PROXY_CALIBRATION_PROTOCOL`, `VALID_PROXY_CALIBRATION_PROTOCOL`.
- Transition types: `LIMIT_OF_DETECTION_TRANSITION_RULE`, `VALID_PROXY_CALIBRATION_TRANSITION_RULE`.
- Errors and utilities: none.
- Operations: `declare_bk_noise_floor`, `estimate_bk_noise_floor`, `classify_against_noise_floor`, `calibrate_proxy_kq`, `proxy_uncalibrated`, `require_valid_proxy_calibration`.
- Calibrated primitive operations: `declare_bk_noise_floor`, `estimate_bk_noise_floor`, `proxy_uncalibrated`.
- Internal operations: none.
- All exports: `B_K_NOISE_FLOOR_PROTOCOL`, `KQ_PROXY_CALIBRATION_PROTOCOL`, `LIMIT_OF_DETECTION_PROTOCOL`, `LIMIT_OF_DETECTION_TRANSITION_RULE`, `LimitOfDetectionResult`, `VALID_PROXY_CALIBRATION_PROTOCOL`, `VALID_PROXY_CALIBRATION_TRANSITION_RULE`, `LimitOfDetectionValue`, `NoiseFloorResult`, `NoiseFloorValue`, `ProxyCalibrationResult`, `ProxyCalibrationValue`, `ValidProxyCalibrationValue`, `calibrate_proxy_kq`, `classify_against_noise_floor`, `declare_bk_noise_floor`, `estimate_bk_noise_floor`, `proxy_uncalibrated`, `require_valid_proxy_calibration`.

## branch

Layer 2 branch fingerprint and slope-flow evidence.

### Parents

- `core`
- `primitives`
- `projection`
- `metrology`

### Provides

- Status families: `BranchFingerprintStatus`.
- Value types: `KqSlopeStabilityValue`, `KqSlopeStabilityResult`, `BranchFingerprintValue`, `BranchFingerprintResult`, `SlopeFlowSample`, `SlopeFlowModel`, `SlopeSegmentEvidence`, `SlopeModelResidual`, `SlopeFlowComparisonValue`, `SlopeFlowComparisonResult`.
- Protocol types: `KQ_SLOPE_STABILITY_PROTOCOL`, `BRANCH_FINGERPRINT_PROTOCOL`, `BRANCH_FINGERPRINT_CONSUMER_PROTOCOL`, `SLOPE_FLOW_COMPARISON_PROTOCOL`, `SLOPE_FLOW_CONSUMER_PROTOCOL`.
- Transition types: `KQ_FLOW_REQUIRE_STABLE_TRANSITION_RULE`, `PROJECTION_TO_FINGERPRINT_TRANSITION_RULE`, `TRANSFER_FLOW_TO_FINGERPRINT_TRANSITION_RULE`, `BRANCH_COMPOSE_FINGERPRINT_TRANSITION_RULE`, `SLOPE_FLOW_MODEL_COMPARISON_TRANSITION_RULE`.
- Errors and utilities: `KQ_FLOW_STATUSES`, `FINGERPRINT_STATUSES`, `SLOPE_FLOW_STATUSES`.
- Operations: `compare_kq_slope_stability`, `build_branch_fingerprint`, `compare_slope_flow_to_models`.
- Calibrated primitive operations: `compare_slope_flow_to_models`.
- Internal operations: none.
- All exports: `BRANCH_COMPOSE_FINGERPRINT_TRANSITION_RULE`, `BRANCH_FINGERPRINT_CONSUMER_PROTOCOL`, `BRANCH_FINGERPRINT_PROTOCOL`, `KQ_FLOW_REQUIRE_STABLE_TRANSITION_RULE`, `KQ_SLOPE_STABILITY_PROTOCOL`, `PROJECTION_TO_FINGERPRINT_TRANSITION_RULE`, `SLOPE_FLOW_COMPARISON_PROTOCOL`, `SLOPE_FLOW_CONSUMER_PROTOCOL`, `SLOPE_FLOW_MODEL_COMPARISON_TRANSITION_RULE`, `TRANSFER_FLOW_TO_FINGERPRINT_TRANSITION_RULE`, `BranchFingerprintResult`, `BranchFingerprintValue`, `KqSlopeStabilityResult`, `KqSlopeStabilityValue`, `SlopeFlowComparisonResult`, `SlopeFlowComparisonValue`, `SlopeFlowModel`, `SlopeFlowSample`, `SlopeModelResidual`, `SlopeSegmentEvidence`, `build_branch_fingerprint`, `compare_kq_slope_stability`, `compare_slope_flow_to_models`.

## refinery

Layer 2 protocol-aware rewrite evaluation.

### Parents

- `core`
- `primitives`
- `projection`
- `metrology`
- `branch`

### Provides

- Status families: `RefineryStatus`.
- Value types: `TypedResultSnapshot`, `RefineryObservation`, `SlagVector`, `SlagComparison`, `RefineryScenarioComparison`, `RefineryDecisionValue`, `RefineryDecisionResult`.
- Protocol types: `REFINERY_OBSERVATION_PROTOCOL`, `REFINERY_DECISION_PROTOCOL`, `REFINERY_ACCEPTED_REWRITE_PROTOCOL`.
- Transition types: `PROJECTIVE_RATIO_STATUS_PRESERVATION_TRANSITION_RULE`, `QUADRATIC_ROOT_STATUS_PRESERVATION_TRANSITION_RULE`, `PROJECTION_STATUS_PRESERVATION_TRANSITION_RULE`, `METROLOGY_STATUS_PRESERVATION_TRANSITION_RULE`, `BRANCH_FINGERPRINT_STATUS_PRESERVATION_TRANSITION_RULE`, `REFINERY_REQUIRE_ACCEPTED_TRANSITION_RULE`.
- Errors and utilities: `DEFAULT_SLAG_DIMENSIONS`, `_STATUS_PRESERVATION_RULES`, `ProjectiveLike`.
- Operations: `snapshot_typed_result`, `compute_slag_vector`, `compare_slag_vectors`, `aggregate_slag_vectors`, `compare_refinery_scenario`, `evaluate_rewrite_candidate`, `require_accepted_rewrite`.
- Calibrated primitive operations: none.
- Internal operations: none.
- All exports: `BRANCH_FINGERPRINT_STATUS_PRESERVATION_TRANSITION_RULE`, `DEFAULT_SLAG_DIMENSIONS`, `METROLOGY_STATUS_PRESERVATION_TRANSITION_RULE`, `PROJECTIVE_RATIO_STATUS_PRESERVATION_TRANSITION_RULE`, `PROJECTION_STATUS_PRESERVATION_TRANSITION_RULE`, `QUADRATIC_ROOT_STATUS_PRESERVATION_TRANSITION_RULE`, `REFINERY_ACCEPTED_REWRITE_PROTOCOL`, `REFINERY_DECISION_PROTOCOL`, `REFINERY_OBSERVATION_PROTOCOL`, `REFINERY_REQUIRE_ACCEPTED_TRANSITION_RULE`, `RefineryDecisionResult`, `RefineryDecisionValue`, `RefineryObservation`, `RefineryScenarioComparison`, `SlagComparison`, `SlagVector`, `TypedResultSnapshot`, `_STATUS_PRESERVATION_RULES`, `compare_refinery_scenario`, `compute_slag_vector`, `evaluate_rewrite_candidate`, `require_accepted_rewrite`, `snapshot_typed_result`.

## history

Layer 2 status-history evidence.

### Parents

- `core`
- `primitives`
- `projection`
- `metrology`
- `branch`
- `refinery`

### Provides

- Status families: `HistoryStatus`.
- Value types: `StatusEventValue`, `StatusTransitionValue`, `StatusTraceValue`, `HistoryEventResult`, `HistoryTransitionResult`, `HistoryTraceResult`, `HistoryResult`.
- Protocol types: `HISTORY_EVENT_PROTOCOL`, `HISTORY_TRANSITION_PROTOCOL`, `HISTORY_TRACE_PROTOCOL`, `STABLE_HISTORY_TRACE_PROTOCOL`.
- Transition types: `HISTORY_RECORD_EVENT_TRANSITION_RULE`, `HISTORY_EVENT_PAIR_COMPARE_TRANSITION_RULE`, `HISTORY_EVENTS_TO_TRACE_TRANSITION_RULE`, `HISTORY_TRACE_REQUIRE_STABLE_TRANSITION_RULE`.
- Errors and utilities: `EVENT_STATUSES`, `TRANSITION_STATUSES`, `TRACE_STATUSES`.
- Operations: `record_status_event`, `compare_status_events`, `build_status_trace`, `require_stable_status_trace`.
- Calibrated primitive operations: `build_status_trace`.
- Internal operations: none.
- All exports: `HISTORY_EVENT_PAIR_COMPARE_TRANSITION_RULE`, `HISTORY_EVENT_PROTOCOL`, `HISTORY_EVENTS_TO_TRACE_TRANSITION_RULE`, `HISTORY_RECORD_EVENT_TRANSITION_RULE`, `HISTORY_TRACE_PROTOCOL`, `HISTORY_TRACE_REQUIRE_STABLE_TRANSITION_RULE`, `HISTORY_TRANSITION_PROTOCOL`, `STABLE_HISTORY_TRACE_PROTOCOL`, `HistoryEventResult`, `HistoryResult`, `HistoryTraceResult`, `HistoryTransitionResult`, `StatusEventValue`, `StatusTraceValue`, `StatusTransitionValue`, `build_status_trace`, `compare_status_events`, `record_status_event`, `require_stable_status_trace`.

## solver

Layer 3 typed projection solver consumer.

### Parents

- `core`
- `primitives`
- `projection`
- `metrology`
- `branch`
- `refinery`
- `history`

### Provides

- Status families: `SolverStatus`.
- Value types: `SolverPolicy`, `LocalQuadraticStepModel`, `SolverStepValue`, `SolverStepResult`, `SolverRunValue`, `SolverRunResult`.
- Protocol types: `TYPED_PROJECTION_SOLVER_STEP_PROTOCOL`, `TYPED_PROJECTION_SOLVER_RUN_PROTOCOL`, `CONVERGED_SOLVER_PROTOCOL`.
- Transition types: `RESIDUAL_DETECTION_TO_SOLVER_TRANSITION_RULE`, `PROJECTION_TO_SOLVER_STEP_TRANSITION_RULE`, `BRANCH_FINGERPRINT_TO_SOLVER_TRANSITION_RULE`, `REFINERY_TO_SOLVER_TRANSITION_RULE`, `PROJECTION_HISTORY_TO_SOLVER_TRANSITION_RULE`, `SOLVER_RUN_REQUIRE_CONVERGED_TRANSITION_RULE`.
- Errors and utilities: `STEP_TERMINAL_STATUSES`, `RUN_STATUSES`.
- Operations: `evaluate_solver_step`, `run_typed_projection_solver`, `require_converged_solver`.
- Calibrated primitive operations: `evaluate_solver_step`, `run_typed_projection_solver`.
- Internal operations: `solver_projection_history_event`.
- All exports: `BRANCH_FINGERPRINT_TO_SOLVER_TRANSITION_RULE`, `CONVERGED_SOLVER_PROTOCOL`, `PROJECTION_HISTORY_TO_SOLVER_TRANSITION_RULE`, `PROJECTION_TO_SOLVER_STEP_TRANSITION_RULE`, `REFINERY_TO_SOLVER_TRANSITION_RULE`, `RESIDUAL_DETECTION_TO_SOLVER_TRANSITION_RULE`, `SOLVER_RUN_REQUIRE_CONVERGED_TRANSITION_RULE`, `TYPED_PROJECTION_SOLVER_RUN_PROTOCOL`, `TYPED_PROJECTION_SOLVER_STEP_PROTOCOL`, `LocalQuadraticStepModel`, `SolverPolicy`, `SolverRunResult`, `SolverRunValue`, `SolverStepResult`, `SolverStepValue`, `evaluate_solver_step`, `require_converged_solver`, `run_typed_projection_solver`.
