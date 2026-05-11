import json

from lloyd_v4.core.status import HistoryStatus
from lloyd_v4.history import build_status_trace, compare_status_events, record_status_event, require_stable_status_trace
from lloyd_v4.primitives.projective_ratio import projective_ratio


def _event(step: int, numerator: int = 1):
    return record_status_event(projective_ratio(numerator, 2), stream_id="s", observation_key="o", step_index=step, geometry_signature="g")


def test_event_transition_and_trace_serialization_preserves_evidence() -> None:
    first = _event(0)
    second = _event(1)
    transition = compare_status_events(first, second)
    trace = build_status_trace([first, second])

    event_payload = first.to_json_safe()
    transition_payload = transition.to_json_safe()
    trace_payload = trace.to_json_safe()

    assert event_payload["status"] == HistoryStatus.HISTORY_EVENT_RECORDED.value
    assert event_payload["value"]["source_protocol"] == "projective_ratio"
    assert event_payload["value"]["source_status_family"] == "ProjectiveRatioStatus"
    assert event_payload["value"]["source_trace_id"] == projective_ratio(1, 2).provenance.trace_id
    assert transition_payload["value"]["previous_event_trace_id"] == first.provenance.trace_id
    assert trace_payload["value"]["event_count"] == 2
    assert trace_payload["value"]["transition_status_counts"] == {HistoryStatus.HISTORY_TRANSITION_STABLE.value: 1}
    json.dumps(trace_payload, allow_nan=False)


def test_stable_trace_refusal_serializes_without_recursive_source_results() -> None:
    singleton = build_status_trace([_event(0)])
    refused = require_stable_status_trace(singleton).to_json_safe()
    encoded = json.dumps(refused, allow_nan=False)

    assert refused["protocol"] == "scalarization_refused"
    assert "nonfinite_float" not in encoded
    assert "ProjectiveRatioValue" not in encoded
    assert "callable" not in encoded
