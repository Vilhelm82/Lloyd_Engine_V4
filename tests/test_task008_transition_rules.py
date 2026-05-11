import pytest

from lloyd_v4.core.calculus import join_statuses
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import HistoryStatus, ProjectiveRatioStatus
from lloyd_v4.core.transitions import assert_transition_rule_complete
from lloyd_v4.history import (
    HISTORY_EVENT_PAIR_COMPARE_TRANSITION_RULE,
    HISTORY_EVENTS_TO_TRACE_TRANSITION_RULE,
    HISTORY_RECORD_EVENT_TRANSITION_RULE,
    HISTORY_TRACE_REQUIRE_STABLE_TRANSITION_RULE,
)


def test_history_transition_rules_are_exported_and_have_expected_families() -> None:
    assert HISTORY_RECORD_EVENT_TRANSITION_RULE.rule_id == "history.record_event"
    assert HISTORY_RECORD_EVENT_TRANSITION_RULE.output_status_family is HistoryStatus
    assert HISTORY_EVENT_PAIR_COMPARE_TRANSITION_RULE.output_status_family is HistoryStatus
    assert HISTORY_EVENTS_TO_TRACE_TRANSITION_RULE.output_status_family is HistoryStatus
    assert HISTORY_TRACE_REQUIRE_STABLE_TRANSITION_RULE.input_status_family is HistoryStatus


def test_stable_trace_requirement_rule_covers_trace_statuses() -> None:
    assert HISTORY_TRACE_REQUIRE_STABLE_TRANSITION_RULE.accepted_input_statuses == frozenset({HistoryStatus.HISTORY_TRACE_STABLE})
    assert HISTORY_TRACE_REQUIRE_STABLE_TRANSITION_RULE.refused_input_statuses == frozenset(
        {
            HistoryStatus.HISTORY_TRACE_EMPTY,
            HistoryStatus.HISTORY_TRACE_SINGLETON,
            HistoryStatus.HISTORY_TRACE_TRANSITIONED,
            HistoryStatus.HISTORY_TRACE_INCOMPLETE,
            HistoryStatus.HISTORY_TRACE_UNORDERED,
        }
    )
    assert_transition_rule_complete(HISTORY_TRACE_REQUIRE_STABLE_TRANSITION_RULE)


def test_event_and_trace_rules_cover_expected_inputs() -> None:
    assert HistoryStatus.HISTORY_EVENT_RECORDED in HISTORY_EVENT_PAIR_COMPARE_TRANSITION_RULE.accepted_input_statuses
    assert HistoryStatus.HISTORY_EVENT_RECORDED in HISTORY_EVENTS_TO_TRACE_TRANSITION_RULE.accepted_input_statuses
    assert_transition_rule_complete(HISTORY_EVENT_PAIR_COMPARE_TRANSITION_RULE)
    assert_transition_rule_complete(HISTORY_EVENTS_TO_TRACE_TRANSITION_RULE)


def test_generic_mixed_family_join_remains_conservative() -> None:
    with pytest.raises(ProtocolViolationError):
        join_statuses("mixed", [ProjectiveRatioStatus.FINITE_RATIO, HistoryStatus.HISTORY_EVENT_RECORDED])
