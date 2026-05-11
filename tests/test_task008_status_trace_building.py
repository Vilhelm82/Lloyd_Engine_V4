from dataclasses import replace

from lloyd_v4.core.status import HistoryStatus
from lloyd_v4.history import build_status_trace, compare_status_events, record_status_event
from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.primitives.projective_ratio import projective_ratio


def _event(step: int, *, stream: str = "s", key: str = "o", numerator: int = 1):
    return record_status_event(projective_ratio(numerator, 2), stream_id=stream, observation_key=key, step_index=step)


def test_trace_empty_singleton_stable_and_transitioned() -> None:
    assert build_status_trace([]).status is HistoryStatus.HISTORY_TRACE_EMPTY
    assert build_status_trace([_event(0)]).status is HistoryStatus.HISTORY_TRACE_SINGLETON

    stable = build_status_trace([_event(0), _event(1), _event(2)])
    assert stable.status is HistoryStatus.HISTORY_TRACE_STABLE
    assert stable.value.stable is True
    assert stable.value.transition_status_counts == {HistoryStatus.HISTORY_TRANSITION_STABLE.value: 2}

    transitioned = build_status_trace([_event(0), record_status_event(projective_ratio(1, 0), stream_id="s", observation_key="o", step_index=1)])
    assert transitioned.status is HistoryStatus.HISTORY_TRACE_TRANSITIONED
    assert transitioned.value.transition_status_counts[HistoryStatus.HISTORY_TRANSITION_STATUS_CHANGED.value] == 1


def test_trace_incomplete_for_mixed_stream_key_or_wrong_inputs() -> None:
    assert build_status_trace([_event(0), _event(1, stream="other")]).status is HistoryStatus.HISTORY_TRACE_INCOMPLETE
    assert build_status_trace([_event(0), _event(1, key="other")]).status is HistoryStatus.HISTORY_TRACE_INCOMPLETE
    assert build_status_trace([_event(0), projective_ratio(1, 2)]).status is HistoryStatus.HISTORY_TRACE_INCOMPLETE
    transition = compare_status_events(_event(0), _event(1))
    assert build_status_trace([transition]).status is HistoryStatus.HISTORY_TRACE_INCOMPLETE


def test_trace_unordered_does_not_sort_or_repair_events() -> None:
    duplicate = build_status_trace([_event(0), _event(0)])
    decreasing = build_status_trace([_event(1), _event(0)])

    assert duplicate.status is HistoryStatus.HISTORY_TRACE_UNORDERED
    assert decreasing.status is HistoryStatus.HISTORY_TRACE_UNORDERED
    assert decreasing.value.first_step_index == 1
    assert decreasing.value.last_step_index == 0
