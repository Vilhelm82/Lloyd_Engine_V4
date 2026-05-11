import pytest

from lloyd_v4.core.calculus import join_statuses
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import BranchFingerprintStatus, HistoryStatus, MetrologyStatus, ProjectionStatus, RefineryStatus, SolverStatus
from lloyd_v4.core.transitions import assert_transition_rule_complete
from lloyd_v4.solver import (
    BRANCH_FINGERPRINT_TO_SOLVER_TRANSITION_RULE,
    CONVERGED_SOLVER_PROTOCOL,
    PROJECTION_HISTORY_TO_SOLVER_TRANSITION_RULE,
    PROJECTION_TO_SOLVER_STEP_TRANSITION_RULE,
    REFINERY_TO_SOLVER_TRANSITION_RULE,
    RESIDUAL_DETECTION_TO_SOLVER_TRANSITION_RULE,
    SOLVER_RUN_REQUIRE_CONVERGED_TRANSITION_RULE,
)


def test_solver_transition_rules_are_exported_and_cover_sources() -> None:
    assert RESIDUAL_DETECTION_TO_SOLVER_TRANSITION_RULE.input_status_family is MetrologyStatus
    assert PROJECTION_TO_SOLVER_STEP_TRANSITION_RULE.input_status_family is ProjectionStatus
    assert BRANCH_FINGERPRINT_TO_SOLVER_TRANSITION_RULE.input_status_family is BranchFingerprintStatus
    assert REFINERY_TO_SOLVER_TRANSITION_RULE.input_status_family is RefineryStatus
    assert PROJECTION_HISTORY_TO_SOLVER_TRANSITION_RULE.input_status_family is HistoryStatus
    assert SOLVER_RUN_REQUIRE_CONVERGED_TRANSITION_RULE.input_status_family is SolverStatus

    for rule in [
        PROJECTION_TO_SOLVER_STEP_TRANSITION_RULE,
        BRANCH_FINGERPRINT_TO_SOLVER_TRANSITION_RULE,
        REFINERY_TO_SOLVER_TRANSITION_RULE,
        PROJECTION_HISTORY_TO_SOLVER_TRANSITION_RULE,
        SOLVER_RUN_REQUIRE_CONVERGED_TRANSITION_RULE,
    ]:
        assert_transition_rule_complete(rule)


def test_require_converged_rule_accepts_only_converged_statuses() -> None:
    assert SOLVER_RUN_REQUIRE_CONVERGED_TRANSITION_RULE.accepted_input_statuses == frozenset(
        {SolverStatus.SOLVER_CONVERGED_IDENTITY, SolverStatus.SOLVER_CONVERGED_BELOW_DETECTION}
    )
    assert SolverStatus.SOLVER_STEP_ADVANCED in SOLVER_RUN_REQUIRE_CONVERGED_TRANSITION_RULE.refused_input_statuses
    assert CONVERGED_SOLVER_PROTOCOL.accepted_statuses == SOLVER_RUN_REQUIRE_CONVERGED_TRANSITION_RULE.accepted_input_statuses


def test_generic_mixed_family_join_remains_conservative() -> None:
    with pytest.raises(ProtocolViolationError):
        join_statuses("mixed", [ProjectionStatus.PROJECTION_TRANSVERSE, SolverStatus.SOLVER_STEP_ADVANCED])
