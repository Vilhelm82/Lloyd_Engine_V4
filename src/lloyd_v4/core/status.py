from __future__ import annotations

from enum import StrEnum


class DomainStatus(StrEnum):
    DEFINED = "defined"
    UNDEFINED = "undefined"
    OUT_OF_DOMAIN = "out_of_domain"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class StratumStatus(StrEnum):
    REGULAR = "regular"
    DEGENERATE = "degenerate"
    BOUNDARY = "boundary"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class ValidityStatus(StrEnum):
    VALID = "valid"
    INVALID = "invalid"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class ConditioningStatus(StrEnum):
    WELL_CONDITIONED = "well_conditioned"
    ILL_CONDITIONED = "ill_conditioned"
    SINGULAR = "singular"
    WARNING = "warning"
    UNKNOWN = "unknown"


class MetrologyStatus(StrEnum):
    IDENTITY_ZERO = "identity_zero"
    BELOW_LIMIT_OF_DETECTION = "below_limit_of_detection"
    INDETERMINATE = "indeterminate"
    DETECTED_NONZERO = "detected_nonzero"
    UNCALIBRATED_PROXY = "uncalibrated_proxy"
    NOISE_FLOOR_DECLARED = "noise_floor_declared"
    NOISE_FLOOR_ESTIMATED = "noise_floor_estimated"
    NOISE_FLOOR_INDETERMINATE = "noise_floor_indeterminate"
    DETECTED = "detected"
    DETECTION_INDETERMINATE = "detection_indeterminate"
    CALIBRATION_VALID = "calibration_valid"
    CALIBRATION_INVALID = "calibration_invalid"
    CALIBRATION_INDETERMINATE = "calibration_indeterminate"
    PROXY_UNCALIBRATED = "proxy_uncalibrated"
    UNKNOWN = "unknown"


class ProtocolStatus(StrEnum):
    OK = "ok"
    VIOLATION = "violation"
    UNCERTAIN = "uncertain"
    SCALARIZATION_REFUSED = "scalarization_refused"


class ProvenanceStatus(StrEnum):
    COMPLETE = "complete"
    COMPACTED = "compacted"
    LOST = "lost"
    UNKNOWN = "unknown"


class CollectionStatus(StrEnum):
    COLLECTION_EMPTY = "collection_empty"
    COLLECTION_SINGLETON = "collection_singleton"
    COLLECTION_OBSERVED = "collection_observed"


class ValueStatus(StrEnum):
    VALUE_ABSENT = "value_absent"
    VALUE_OBSERVED = "value_observed"


class ProjectiveRatioStatus(StrEnum):
    FINITE_RATIO = "finite_ratio"
    SIGNED_ZERO = "signed_zero"
    INFINITE_DIRECTION = "infinite_direction"
    INDETERMINATE = "indeterminate"


class QuadraticRootStatus(StrEnum):
    TWO_REAL_ROOTS = "two_real_roots"
    REPEATED_ROOT = "repeated_root"
    NO_REAL_ROOT = "no_real_root"
    LINEAR_ROOT = "linear_root"
    CONSTANT_IDENTITY = "constant_identity"
    CONSTANT_NO_SOLUTION = "constant_no_solution"


class TransferStatus(StrEnum):
    TRANSFER_OBSERVED = "transfer_observed"
    TRANSFER_CANCELLATION_DOMINATED = "transfer_cancellation_dominated"
    TRANSFER_NON_FINITE = "transfer_non_finite"
    TRANSFER_DOMAIN_REFUSED = "transfer_domain_refused"
    TRANSFER_DELTA_INDETERMINATE = "transfer_delta_indeterminate"


class SlopeStatus(StrEnum):
    SLOPE_OBSERVED = "slope_observed"
    SLOPE_INSUFFICIENT_DATA = "slope_insufficient_data"
    SLOPE_DEGENERATE_INPUT = "slope_degenerate_input"


class AlphaProbeStatus(StrEnum):
    ALPHA_REGULAR_INTEGER = "alpha_regular_integer"
    ALPHA_FRACTIONAL_BRANCH = "alpha_fractional_branch"
    ALPHA_NEGATIVE_SINGULARITY = "alpha_negative_singularity"
    ALPHA_MODEL_AMBIGUOUS = "alpha_model_ambiguous"
    ALPHA_MODEL_NO_MATCH = "alpha_model_no_match"
    ALPHA_CANCELLATION_DOMINATED = "alpha_cancellation_dominated"
    ALPHA_INSUFFICIENT_DATA = "alpha_insufficient_data"
    ALPHA_DOMAIN_REFUSED = "alpha_domain_refused"
    ALPHA_NONFINITE = "alpha_nonfinite"
    ALPHA_INDETERMINATE = "alpha_indeterminate"
    ALPHA_ZERO_BOUNDARY = "alpha_zero_boundary"
    ALPHA_UNSTABLE_WINDOW = "alpha_unstable_window"


class ScalarAlphaJetBundleStatus(StrEnum):
    SCALAR_JET_REGULAR_INTEGER_ALPHA = "scalar_jet_regular_integer_alpha"
    SCALAR_JET_FRACTIONAL_ALPHA_BRANCH = "scalar_jet_fractional_alpha_branch"
    SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY = "scalar_jet_negative_alpha_singularity"
    SCALAR_JET_ALPHA_MODEL_REFUSED = "scalar_jet_alpha_model_refused"
    SCALAR_JET_ALPHA_CANCELLATION_DOMINATED = "scalar_jet_alpha_cancellation_dominated"
    SCALAR_JET_ALPHA_INDETERMINATE = "scalar_jet_alpha_indeterminate"
    SCALAR_JET_ALPHA_ZERO_BOUNDARY = "scalar_jet_alpha_zero_boundary"
    SCALAR_JET_ALPHA_UNSTABLE_WINDOW = "scalar_jet_alpha_unstable_window"
    SCALAR_JET_DOMAIN_REFUSED = "scalar_jet_domain_refused"
    SCALAR_JET_NONFINITE = "scalar_jet_nonfinite"
    SCALAR_JET_PROTOCOL_REFUSED = "scalar_jet_protocol_refused"


class SingularAlphaJetBundleStatus(StrEnum):
    SINGULAR_JET_REGULAR_INTEGER_ALPHA = "singular_jet_regular_integer_alpha"
    SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH = "singular_jet_fractional_alpha_branch"
    SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY = "singular_jet_negative_alpha_singularity"
    SINGULAR_JET_ALPHA_MODEL_REFUSED = "singular_jet_alpha_model_refused"
    SINGULAR_JET_ALPHA_CANCELLATION_DOMINATED = "singular_jet_alpha_cancellation_dominated"
    SINGULAR_JET_ALPHA_INDETERMINATE = "singular_jet_alpha_indeterminate"
    SINGULAR_JET_ALPHA_ZERO_BOUNDARY = "singular_jet_alpha_zero_boundary"
    SINGULAR_JET_ALPHA_UNSTABLE_WINDOW = "singular_jet_alpha_unstable_window"
    SINGULAR_JET_DOMAIN_REFUSED = "singular_jet_domain_refused"
    SINGULAR_JET_NONFINITE = "singular_jet_nonfinite"
    SINGULAR_JET_PROTOCOL_REFUSED = "singular_jet_protocol_refused"


class ProjectionStatus(StrEnum):
    PROJECTION_TRANSVERSE = "projection_transverse"
    PROJECTION_TANGENT_CONTACT = "projection_tangent_contact"
    PROJECTION_LINEAR = "projection_linear"
    PROJECTION_NO_REAL_ROOT = "projection_no_real_root"
    PROJECTION_IDENTITY = "projection_identity"
    PROJECTION_NO_SOLUTION = "projection_no_solution"
    PROJECTION_SELECTION_REFUSED = "projection_selection_refused"


class BranchFingerprintStatus(StrEnum):
    SLOPE_FLOW_OBSERVED = "slope_flow_observed"
    SLOPE_MODEL_RESIDUALS = "slope_model_residuals"
    SLOPE_MODEL_UNIQUE_MATCH = "slope_model_unique_match"
    SLOPE_MODEL_AMBIGUOUS = "slope_model_ambiguous"
    SLOPE_MODEL_NO_MATCH = "slope_model_no_match"
    SLOPE_FLOW_INSUFFICIENT_SAMPLES = "slope_flow_insufficient_samples"
    SLOPE_FLOW_INDETERMINATE = "slope_flow_indeterminate"
    SLOPE_FLOW_PROXY_UNCALIBRATED = "slope_flow_proxy_uncalibrated"
    KQ_FLOW_STABLE = "kq_flow_stable"
    KQ_FLOW_UNSTABLE = "kq_flow_unstable"
    KQ_FLOW_INDETERMINATE = "kq_flow_indeterminate"
    KQ_FLOW_UNCALIBRATED = "kq_flow_uncalibrated"
    FINGERPRINT_COMPLETE = "fingerprint_complete"
    FINGERPRINT_UNIDENTIFIED = "fingerprint_unidentified"
    FINGERPRINT_INCOMPLETE = "fingerprint_incomplete"
    FINGERPRINT_PROXY_UNCALIBRATED = "fingerprint_proxy_uncalibrated"


class RefineryStatus(StrEnum):
    REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG = "rewrite_accepted_same_geometry_lower_slag"
    REWRITE_EQUIVALENT_NO_IMPROVEMENT = "rewrite_equivalent_no_improvement"
    REWRITE_REJECTED_PROTOCOL_MISMATCH = "rewrite_rejected_protocol_mismatch"
    REWRITE_REJECTED_STATUS_FAMILY_MISMATCH = "rewrite_rejected_status_family_mismatch"
    REWRITE_REJECTED_STATUS_MISMATCH = "rewrite_rejected_status_mismatch"
    REWRITE_REJECTED_VALIDITY_MISMATCH = "rewrite_rejected_validity_mismatch"
    REWRITE_REJECTED_GEOMETRY_MISMATCH = "rewrite_rejected_geometry_mismatch"
    REWRITE_REJECTED_SLAG_REGRESSION = "rewrite_rejected_slag_regression"
    REWRITE_INDETERMINATE_INSUFFICIENT_EVIDENCE = "rewrite_indeterminate_insufficient_evidence"
    REWRITE_INDETERMINATE_UNHANDLED_STATUS = "rewrite_indeterminate_unhandled_status"


class HistoryStatus(StrEnum):
    HISTORY_EVENT_RECORDED = "history_event_recorded"
    HISTORY_TRANSITION_STABLE = "history_transition_stable"
    HISTORY_TRANSITION_PROTOCOL_CHANGED = "history_transition_protocol_changed"
    HISTORY_TRANSITION_STATUS_FAMILY_CHANGED = "history_transition_status_family_changed"
    HISTORY_TRANSITION_STATUS_CHANGED = "history_transition_status_changed"
    HISTORY_TRANSITION_VALIDITY_CHANGED = "history_transition_validity_changed"
    HISTORY_TRANSITION_GEOMETRY_CHANGED = "history_transition_geometry_changed"
    HISTORY_TRANSITION_INCOMPARABLE = "history_transition_incomparable"
    HISTORY_TRACE_EMPTY = "history_trace_empty"
    HISTORY_TRACE_SINGLETON = "history_trace_singleton"
    HISTORY_TRACE_STABLE = "history_trace_stable"
    HISTORY_TRACE_TRANSITIONED = "history_trace_transitioned"
    HISTORY_TRACE_INCOMPLETE = "history_trace_incomplete"
    HISTORY_TRACE_UNORDERED = "history_trace_unordered"


class SolverStatus(StrEnum):
    SOLVER_STEP_ADVANCED = "solver_step_advanced"
    SOLVER_CONVERGED_IDENTITY = "solver_converged_identity"
    SOLVER_CONVERGED_BELOW_DETECTION = "solver_converged_below_detection"
    SOLVER_PROJECTION_BLOCKED = "solver_projection_blocked"
    SOLVER_TANGENT_BLOCKED = "solver_tangent_blocked"
    SOLVER_SELECTION_REFUSED = "solver_selection_refused"
    SOLVER_BRANCH_UNIDENTIFIED = "solver_branch_unidentified"
    SOLVER_PROXY_UNCALIBRATED = "solver_proxy_uncalibrated"
    SOLVER_REFINERY_REJECTED = "solver_refinery_rejected"
    SOLVER_HISTORY_UNSTABLE = "solver_history_unstable"
    SOLVER_SEQUENCE_INCONSISTENT = "solver_sequence_inconsistent"
    SOLVER_STEP_BUDGET_EXHAUSTED = "solver_step_budget_exhausted"
    SOLVER_PROTOCOL_REFUSED = "solver_protocol_refused"
    SOLVER_INDETERMINATE = "solver_indeterminate"


StatusCode = (
    DomainStatus
    | StratumStatus
    | ValidityStatus
    | ConditioningStatus
    | MetrologyStatus
    | ProtocolStatus
    | ProvenanceStatus
    | CollectionStatus
    | ValueStatus
    | ProjectiveRatioStatus
    | QuadraticRootStatus
    | TransferStatus
    | SlopeStatus
    | AlphaProbeStatus
    | ScalarAlphaJetBundleStatus
    | SingularAlphaJetBundleStatus
    | ProjectionStatus
    | BranchFingerprintStatus
    | RefineryStatus
    | HistoryStatus
    | SolverStatus
)
