from dataclasses import replace

from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.status import HistoryStatus, ProjectiveRatioStatus, ProtocolStatus
from lloyd_v4.history import HISTORY_TRACE_PROTOCOL, STABLE_HISTORY_TRACE_PROTOCOL, build_status_trace, record_status_event, require_stable_status_trace
from lloyd_v4.primitives.projective_ratio import projective_ratio


def _trace(status: HistoryStatus):
    event = record_status_event(projective_ratio(1, 2), stream_id="s", observation_key="o", step_index=0)
    trace = build_status_trace([event, record_status_event(projective_ratio(1, 2), stream_id="s", observation_key="o", step_index=1)])
    return replace(trace, status=status)


def test_history_trace_protocol_is_status_family_aware() -> None:
    trace = _trace(HistoryStatus.HISTORY_TRACE_STABLE)
    wrong_family = replace(trace, status=ProjectiveRatioStatus.FINITE_RATIO)

    assert validate_protocol(trace, HISTORY_TRACE_PROTOCOL).ok is True
    assert validate_protocol(wrong_family, HISTORY_TRACE_PROTOCOL).ok is False


def test_require_stable_status_trace_accepts_only_stable_trace() -> None:
    for status in [
        HistoryStatus.HISTORY_TRACE_STABLE,
        HistoryStatus.HISTORY_TRACE_EMPTY,
        HistoryStatus.HISTORY_TRACE_SINGLETON,
        HistoryStatus.HISTORY_TRACE_TRANSITIONED,
        HistoryStatus.HISTORY_TRACE_INCOMPLETE,
        HistoryStatus.HISTORY_TRACE_UNORDERED,
    ]:
        result = require_stable_status_trace(_trace(status))
        if status is HistoryStatus.HISTORY_TRACE_STABLE:
            assert result.protocol is ProtocolStatus.OK
            assert result.refusal is None
        else:
            assert result.protocol is ProtocolStatus.SCALARIZATION_REFUSED
            assert result.status is status
            assert result.refusal is not None


def test_stable_trace_protocol_rejects_nonstable_statuses() -> None:
    assert validate_protocol(_trace(HistoryStatus.HISTORY_TRACE_STABLE), STABLE_HISTORY_TRACE_PROTOCOL).ok is True
    assert validate_protocol(_trace(HistoryStatus.HISTORY_TRACE_SINGLETON), STABLE_HISTORY_TRACE_PROTOCOL).ok is False
