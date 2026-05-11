from lloyd_v4.branch import (
    BRANCH_COMPOSE_FINGERPRINT_TRANSITION_RULE,
    KQ_FLOW_REQUIRE_STABLE_TRANSITION_RULE,
    PROJECTION_TO_FINGERPRINT_TRANSITION_RULE,
    SLOPE_FLOW_MODEL_COMPARISON_TRANSITION_RULE,
    TRANSFER_FLOW_TO_FINGERPRINT_TRANSITION_RULE,
)
from lloyd_v4.core.calculus import join_statuses
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import BranchFingerprintStatus, MetrologyStatus, ProjectionStatus
from lloyd_v4.core.transitions import apply_status_transition, assert_transition_rule_complete


def test_task006_transition_rules_are_complete_and_contextual() -> None:
    for rule in [
        SLOPE_FLOW_MODEL_COMPARISON_TRANSITION_RULE,
        KQ_FLOW_REQUIRE_STABLE_TRANSITION_RULE,
        PROJECTION_TO_FINGERPRINT_TRANSITION_RULE,
        TRANSFER_FLOW_TO_FINGERPRINT_TRANSITION_RULE,
        BRANCH_COMPOSE_FINGERPRINT_TRANSITION_RULE,
    ]:
        assert_transition_rule_complete(rule)

    assert apply_status_transition(PROJECTION_TO_FINGERPRINT_TRANSITION_RULE, ProjectionStatus.PROJECTION_TANGENT_CONTACT).disposition.value == "accepted"
    assert apply_status_transition(KQ_FLOW_REQUIRE_STABLE_TRANSITION_RULE, BranchFingerprintStatus.KQ_FLOW_STABLE).disposition.value == "accepted"
    assert apply_status_transition(KQ_FLOW_REQUIRE_STABLE_TRANSITION_RULE, BranchFingerprintStatus.KQ_FLOW_UNSTABLE).disposition.value == "refused"
    assert apply_status_transition(TRANSFER_FLOW_TO_FINGERPRINT_TRANSITION_RULE, BranchFingerprintStatus.SLOPE_MODEL_AMBIGUOUS).output_status is BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED


def test_wrong_family_transitions_and_generic_joins_refuse() -> None:
    try:
        apply_status_transition(KQ_FLOW_REQUIRE_STABLE_TRANSITION_RULE, MetrologyStatus.CALIBRATION_VALID)
    except ProtocolViolationError:
        pass
    else:
        raise AssertionError("wrong family transition was accepted")

    try:
        join_statuses("mixed", [ProjectionStatus.PROJECTION_TRANSVERSE, BranchFingerprintStatus.FINGERPRINT_COMPLETE])
    except ProtocolViolationError:
        pass
    else:
        raise AssertionError("mixed join was accepted")
