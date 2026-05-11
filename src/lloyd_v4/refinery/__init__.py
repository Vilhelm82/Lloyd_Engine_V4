"""Protocol-aware rewrite evaluation for Lloyd V4 typed observations."""

from .decision import (
    BRANCH_FINGERPRINT_STATUS_PRESERVATION_TRANSITION_RULE,
    METROLOGY_STATUS_PRESERVATION_TRANSITION_RULE,
    PROJECTIVE_RATIO_STATUS_PRESERVATION_TRANSITION_RULE,
    PROJECTION_STATUS_PRESERVATION_TRANSITION_RULE,
    QUADRATIC_ROOT_STATUS_PRESERVATION_TRANSITION_RULE,
    REFINERY_ACCEPTED_REWRITE_PROTOCOL,
    REFINERY_DECISION_PROTOCOL,
    REFINERY_OBSERVATION_PROTOCOL,
    REFINERY_REQUIRE_ACCEPTED_TRANSITION_RULE,
    _STATUS_PRESERVATION_RULES,
    RefineryDecisionResult,
    RefineryDecisionValue,
    RefineryScenarioComparison,
    compare_refinery_scenario,
    evaluate_rewrite_candidate,
    require_accepted_rewrite,
)
from .observations import RefineryObservation, TypedResultSnapshot, snapshot_typed_result
from .slag import DEFAULT_SLAG_DIMENSIONS, SlagComparison, SlagVector, compute_slag_vector

__all__ = [
    "BRANCH_FINGERPRINT_STATUS_PRESERVATION_TRANSITION_RULE",
    "DEFAULT_SLAG_DIMENSIONS",
    "METROLOGY_STATUS_PRESERVATION_TRANSITION_RULE",
    "PROJECTIVE_RATIO_STATUS_PRESERVATION_TRANSITION_RULE",
    "PROJECTION_STATUS_PRESERVATION_TRANSITION_RULE",
    "QUADRATIC_ROOT_STATUS_PRESERVATION_TRANSITION_RULE",
    "REFINERY_ACCEPTED_REWRITE_PROTOCOL",
    "REFINERY_DECISION_PROTOCOL",
    "REFINERY_OBSERVATION_PROTOCOL",
    "REFINERY_REQUIRE_ACCEPTED_TRANSITION_RULE",
    "RefineryDecisionResult",
    "RefineryDecisionValue",
    "RefineryObservation",
    "RefineryScenarioComparison",
    "SlagComparison",
    "SlagVector",
    "TypedResultSnapshot",
    "_STATUS_PRESERVATION_RULES",
    "compare_refinery_scenario",
    "compute_slag_vector",
    "evaluate_rewrite_candidate",
    "require_accepted_rewrite",
    "snapshot_typed_result",
]
