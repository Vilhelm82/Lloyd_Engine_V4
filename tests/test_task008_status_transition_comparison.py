from dataclasses import replace

from lloyd_v4.core.status import HistoryStatus
from lloyd_v4.history import compare_status_events, record_status_event
from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.primitives.projective_ratio import projective_ratio


def _event(step: int, *, signature: str | None = None):
    return record_status_event(projective_ratio(1, 2), stream_id="s", observation_key="o", step_index=step, geometry_signature=signature)


def test_stable_pair_requires_same_protocol_status_validity_and_signature() -> None:
    transition = compare_status_events(_event(0, signature="g"), _event(1, signature="g"))

    assert transition.status is HistoryStatus.HISTORY_TRANSITION_STABLE
    assert transition.value.changed_fields == ()


def test_pairwise_transition_precedence_and_changed_fields() -> None:
    protocol_changed = compare_status_events(_event(0), record_status_event(declare_bk_noise_floor(1.0), stream_id="s", observation_key="o", step_index=1))
    assert protocol_changed.status is HistoryStatus.HISTORY_TRANSITION_PROTOCOL_CHANGED
    assert "source_protocol" in protocol_changed.value.changed_fields
    assert "source_status_family" in protocol_changed.value.changed_fields

    family_changed = compare_status_events(_event(0), replace(_event(1), value=replace(_event(1).value, source_protocol="projective_ratio", source_status_family="MetrologyStatus")))
    assert family_changed.status is HistoryStatus.HISTORY_TRANSITION_STATUS_FAMILY_CHANGED

    status_changed = compare_status_events(_event(0), record_status_event(projective_ratio(1, 0), stream_id="s", observation_key="o", step_index=1))
    assert status_changed.status is HistoryStatus.HISTORY_TRANSITION_STATUS_CHANGED

    validity_changed_event = replace(_event(1), value=replace(_event(1).value, source_validity={**_event(1).value.source_validity, "finite": False}))
    assert compare_status_events(_event(0), validity_changed_event).status is HistoryStatus.HISTORY_TRANSITION_VALIDITY_CHANGED

    geometry_changed = compare_status_events(_event(0, signature="a"), _event(1, signature="b"))
    assert geometry_changed.status is HistoryStatus.HISTORY_TRANSITION_GEOMETRY_CHANGED

    signature_missing = compare_status_events(_event(0, signature="a"), _event(1))
    assert signature_missing.status is HistoryStatus.HISTORY_TRANSITION_GEOMETRY_CHANGED


def test_incomparable_pairs_for_stream_key_or_step_order() -> None:
    different_stream = compare_status_events(_event(0), record_status_event(projective_ratio(1, 2), stream_id="other", observation_key="o", step_index=1))
    different_key = compare_status_events(_event(0), record_status_event(projective_ratio(1, 2), stream_id="s", observation_key="other", step_index=1))
    same_step = compare_status_events(_event(0), _event(0))

    assert different_stream.status is HistoryStatus.HISTORY_TRANSITION_INCOMPARABLE
    assert different_key.status is HistoryStatus.HISTORY_TRANSITION_INCOMPARABLE
    assert same_step.status is HistoryStatus.HISTORY_TRANSITION_INCOMPARABLE
