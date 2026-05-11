from lloyd_v4.core.transitions import assert_transition_rule_complete
from lloyd_v4.metrology.noise_floor import LIMIT_OF_DETECTION_TRANSITION_RULE
from lloyd_v4.metrology.proxy_calibration import VALID_PROXY_CALIBRATION_TRANSITION_RULE
from lloyd_v4.primitives.projective_ratio import PROJECTIVE_RATIO_PROTOCOL, PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE
from lloyd_v4.primitives.stratified_quadratic_roots import (
    QUADRATIC_ROOT_SELECTION_TRANSITION_RULE,
    STRATIFIED_QUADRATIC_ROOTS_PROTOCOL,
)
from lloyd_v4.projection.exact_projection import QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE


def test_canonical_transition_rules_are_complete() -> None:
    for rule in [
        PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE,
        QUADRATIC_ROOT_SELECTION_TRANSITION_RULE,
        QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE,
        LIMIT_OF_DETECTION_TRANSITION_RULE,
        VALID_PROXY_CALIBRATION_TRANSITION_RULE,
    ]:
        assert_transition_rule_complete(rule)


def test_transition_rule_coverage_matches_producer_protocols() -> None:
    projective_covered = (
        PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE.accepted_input_statuses
        | PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE.refused_input_statuses
        | frozenset(PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE.mapped_statuses)
    )
    quadratic_covered = (
        QUADRATIC_ROOT_SELECTION_TRANSITION_RULE.accepted_input_statuses
        | QUADRATIC_ROOT_SELECTION_TRANSITION_RULE.refused_input_statuses
        | frozenset(QUADRATIC_ROOT_SELECTION_TRANSITION_RULE.mapped_statuses)
    )

    assert projective_covered == PROJECTIVE_RATIO_PROTOCOL.emitted_statuses
    assert quadratic_covered == STRATIFIED_QUADRATIC_ROOTS_PROTOCOL.emitted_statuses
