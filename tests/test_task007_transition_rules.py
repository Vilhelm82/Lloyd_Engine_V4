from lloyd_v4.core.status import BranchFingerprintStatus, MetrologyStatus, ProjectiveRatioStatus, ProjectionStatus, QuadraticRootStatus, RefineryStatus
from lloyd_v4.core.transitions import assert_transition_rule_complete
from lloyd_v4.refinery import (
    BRANCH_FINGERPRINT_STATUS_PRESERVATION_TRANSITION_RULE,
    METROLOGY_STATUS_PRESERVATION_TRANSITION_RULE,
    PROJECTIVE_RATIO_STATUS_PRESERVATION_TRANSITION_RULE,
    PROJECTION_STATUS_PRESERVATION_TRANSITION_RULE,
    QUADRATIC_ROOT_STATUS_PRESERVATION_TRANSITION_RULE,
    REFINERY_REQUIRE_ACCEPTED_TRANSITION_RULE,
    _STATUS_PRESERVATION_RULES,
)


def test_task007_status_preservation_rules_cover_each_family() -> None:
    expected = [
        (PROJECTIVE_RATIO_STATUS_PRESERVATION_TRANSITION_RULE, ProjectiveRatioStatus),
        (QUADRATIC_ROOT_STATUS_PRESERVATION_TRANSITION_RULE, QuadraticRootStatus),
        (PROJECTION_STATUS_PRESERVATION_TRANSITION_RULE, ProjectionStatus),
        (METROLOGY_STATUS_PRESERVATION_TRANSITION_RULE, MetrologyStatus),
        (BRANCH_FINGERPRINT_STATUS_PRESERVATION_TRANSITION_RULE, BranchFingerprintStatus),
    ]

    for rule, status_family in expected:
        assert set(rule.accepted_input_statuses) == set(status_family)
        assert rule.rule_id.startswith("refinery.")
        assert_transition_rule_complete(rule)


def test_refinery_require_accepted_rule_accepts_only_accepted_rewrite() -> None:
    assert REFINERY_REQUIRE_ACCEPTED_TRANSITION_RULE.accepted_input_statuses == frozenset(
        {RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG}
    )
    assert REFINERY_REQUIRE_ACCEPTED_TRANSITION_RULE.refused_input_statuses == frozenset(
        status for status in RefineryStatus if status is not RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG
    )
    assert_transition_rule_complete(REFINERY_REQUIRE_ACCEPTED_TRANSITION_RULE)


def test_evaluate_rewrite_candidate_has_named_preservation_rules_for_supported_families() -> None:
    assert _STATUS_PRESERVATION_RULES[ProjectiveRatioStatus] is PROJECTIVE_RATIO_STATUS_PRESERVATION_TRANSITION_RULE
    assert _STATUS_PRESERVATION_RULES[QuadraticRootStatus] is QUADRATIC_ROOT_STATUS_PRESERVATION_TRANSITION_RULE
    assert _STATUS_PRESERVATION_RULES[ProjectionStatus] is PROJECTION_STATUS_PRESERVATION_TRANSITION_RULE
    assert _STATUS_PRESERVATION_RULES[MetrologyStatus] is METROLOGY_STATUS_PRESERVATION_TRANSITION_RULE
    assert _STATUS_PRESERVATION_RULES[BranchFingerprintStatus] is BRANCH_FINGERPRINT_STATUS_PRESERVATION_TRANSITION_RULE
