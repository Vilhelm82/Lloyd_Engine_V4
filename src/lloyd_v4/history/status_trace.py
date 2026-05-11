from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol, validate_protocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedRefusal, TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import ConditioningStatus, HistoryStatus, ProtocolStatus
from lloyd_v4.core.transitions import StatusTransitionRule
from lloyd_v4.core.validity import Validity
from lloyd_v4.refinery import snapshot_typed_result


EVENT_STATUSES = frozenset({HistoryStatus.HISTORY_EVENT_RECORDED})
TRANSITION_STATUSES = frozenset(
    {
        HistoryStatus.HISTORY_TRANSITION_STABLE,
        HistoryStatus.HISTORY_TRANSITION_PROTOCOL_CHANGED,
        HistoryStatus.HISTORY_TRANSITION_STATUS_FAMILY_CHANGED,
        HistoryStatus.HISTORY_TRANSITION_STATUS_CHANGED,
        HistoryStatus.HISTORY_TRANSITION_VALIDITY_CHANGED,
        HistoryStatus.HISTORY_TRANSITION_GEOMETRY_CHANGED,
        HistoryStatus.HISTORY_TRANSITION_INCOMPARABLE,
    }
)
TRACE_STATUSES = frozenset(
    {
        HistoryStatus.HISTORY_TRACE_EMPTY,
        HistoryStatus.HISTORY_TRACE_SINGLETON,
        HistoryStatus.HISTORY_TRACE_STABLE,
        HistoryStatus.HISTORY_TRACE_TRANSITIONED,
        HistoryStatus.HISTORY_TRACE_INCOMPLETE,
        HistoryStatus.HISTORY_TRACE_UNORDERED,
    }
)

HISTORY_EVENT_PROTOCOL = ProducerProtocol(
    name="history_event",
    emitted_statuses=EVENT_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=HistoryStatus,
)
HISTORY_TRANSITION_PROTOCOL = ProducerProtocol(
    name="history_transition",
    emitted_statuses=TRANSITION_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=HistoryStatus,
)
HISTORY_TRACE_PROTOCOL = ConsumerProtocol(
    name="history_trace",
    accepted_statuses=TRACE_STATUSES,
    required_validity_fields=frozenset({"observable"}),
    scalarization_allowed=False,
    status_family=HistoryStatus,
)
STABLE_HISTORY_TRACE_PROTOCOL = ConsumerProtocol(
    name="stable_history_trace",
    accepted_statuses=frozenset({HistoryStatus.HISTORY_TRACE_STABLE}),
    required_validity_fields=frozenset({"defined", "observable"}),
    scalarization_allowed=False,
    status_family=HistoryStatus,
    refused_statuses=TRACE_STATUSES - frozenset({HistoryStatus.HISTORY_TRACE_STABLE}),
)

HISTORY_RECORD_EVENT_TRANSITION_RULE = StatusTransitionRule(
    rule_id="history.record_event",
    input_status_family=Enum,
    output_status_family=HistoryStatus,
    input_protocol_id=None,
    output_protocol_id=HISTORY_EVENT_PROTOCOL.name,
    accepted_input_statuses=frozenset(),
    refused_input_statuses=frozenset(),
    mapped_statuses={},
    context_keys=("stream_id", "observation_key", "step_index"),
    description="Records a V4 typed-result status as compact history event evidence.",
)
HISTORY_EVENT_PAIR_COMPARE_TRANSITION_RULE = StatusTransitionRule(
    rule_id="history.event_pair.compare",
    input_status_family=HistoryStatus,
    output_status_family=HistoryStatus,
    input_protocol_id=HISTORY_EVENT_PROTOCOL.name,
    output_protocol_id=HISTORY_TRANSITION_PROTOCOL.name,
    accepted_input_statuses=EVENT_STATUSES,
    refused_input_statuses=frozenset(),
    mapped_statuses={},
    context_keys=("previous_event", "next_event"),
    description="Compares adjacent history events by caller-supplied sequence order.",
    emitted_input_statuses=EVENT_STATUSES,
)
HISTORY_EVENTS_TO_TRACE_TRANSITION_RULE = StatusTransitionRule(
    rule_id="history.events.to_trace",
    input_status_family=HistoryStatus,
    output_status_family=HistoryStatus,
    input_protocol_id=HISTORY_EVENT_PROTOCOL.name,
    output_protocol_id=HISTORY_TRACE_PROTOCOL.name,
    accepted_input_statuses=EVENT_STATUSES,
    refused_input_statuses=frozenset(),
    mapped_statuses={},
    context_keys=("events",),
    description="Builds a compact trace summary from ordered history event evidence.",
    emitted_input_statuses=EVENT_STATUSES,
)
HISTORY_TRACE_REQUIRE_STABLE_TRANSITION_RULE = StatusTransitionRule(
    rule_id="history.trace.require_stable",
    input_status_family=HistoryStatus,
    output_status_family=None,
    input_protocol_id=HISTORY_TRACE_PROTOCOL.name,
    output_protocol_id=STABLE_HISTORY_TRACE_PROTOCOL.name,
    accepted_input_statuses=frozenset({HistoryStatus.HISTORY_TRACE_STABLE}),
    refused_input_statuses=TRACE_STATUSES - frozenset({HistoryStatus.HISTORY_TRACE_STABLE}),
    mapped_statuses={},
    emitted_input_statuses=TRACE_STATUSES,
)


@dataclass(frozen=True, slots=True)
class StatusEventValue:
    stream_id: str
    observation_key: str
    step_index: int
    scenario_id: str | None
    source_protocol: str
    source_status_family: str
    source_status: str
    source_validity: dict[str, Any]
    source_conditioning: str
    source_trace_id: str
    source_operation_id: str | None
    source_expression_path: str | None
    source_precision: str | None
    source_backend: str | None
    source_device: str | None
    geometry_signature: str | None

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "observation_key": self.observation_key,
            "step_index": self.step_index,
            "scenario_id": self.scenario_id,
            "source_protocol": self.source_protocol,
            "source_status_family": self.source_status_family,
            "source_status": self.source_status,
            "source_validity": to_json_safe(self.source_validity),
            "source_conditioning": self.source_conditioning,
            "source_trace_id": self.source_trace_id,
            "source_operation_id": self.source_operation_id,
            "source_expression_path": self.source_expression_path,
            "source_precision": self.source_precision,
            "source_backend": self.source_backend,
            "source_device": self.source_device,
            "geometry_signature": self.geometry_signature,
        }


@dataclass(frozen=True, slots=True)
class StatusTransitionValue:
    stream_id: str
    observation_key: str
    previous_step_index: int | None
    next_step_index: int | None
    previous_event_trace_id: str | None
    next_event_trace_id: str | None
    previous_source_trace_id: str | None
    next_source_trace_id: str | None
    changed_fields: tuple[str, ...]
    comparison_reason: str

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "observation_key": self.observation_key,
            "previous_step_index": self.previous_step_index,
            "next_step_index": self.next_step_index,
            "previous_event_trace_id": self.previous_event_trace_id,
            "next_event_trace_id": self.next_event_trace_id,
            "previous_source_trace_id": self.previous_source_trace_id,
            "next_source_trace_id": self.next_source_trace_id,
            "changed_fields": list(self.changed_fields),
            "comparison_reason": self.comparison_reason,
        }


@dataclass(frozen=True, slots=True)
class StatusTraceValue:
    stream_id: str | None
    observation_key: str | None
    event_count: int
    first_step_index: int | None
    last_step_index: int | None
    event_trace_ids: tuple[str, ...]
    source_trace_ids: tuple[str, ...]
    transition_trace_ids: tuple[str, ...]
    transition_status_counts: dict[str, int]
    stable: bool
    transition_count: int
    notes: tuple[str, ...]

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "observation_key": self.observation_key,
            "event_count": self.event_count,
            "first_step_index": self.first_step_index,
            "last_step_index": self.last_step_index,
            "event_trace_ids": list(self.event_trace_ids),
            "source_trace_ids": list(self.source_trace_ids),
            "transition_trace_ids": list(self.transition_trace_ids),
            "transition_status_counts": dict(self.transition_status_counts),
            "stable": self.stable,
            "transition_count": self.transition_count,
            "notes": list(self.notes),
        }


HistoryResult = TypedResult[StatusEventValue | StatusTransitionValue | StatusTraceValue, HistoryStatus]
HistoryEventResult = TypedResult[StatusEventValue, HistoryStatus]
HistoryTransitionResult = TypedResult[StatusTransitionValue, HistoryStatus]
HistoryTraceResult = TypedResult[StatusTraceValue, HistoryStatus]


def record_status_event(
    result: TypedResult[Any, Any],
    *,
    stream_id: str,
    observation_key: str,
    step_index: int,
    scenario_id: str | None = None,
    geometry_signature: str | None = None,
) -> HistoryEventResult:
    if not isinstance(result, TypedResult):
        raise ProtocolViolationError("status event recording requires a V4 TypedResult")
    _nonempty(stream_id, "stream_id")
    _nonempty(observation_key, "observation_key")
    if isinstance(step_index, bool) or not isinstance(step_index, int) or step_index < 0:
        raise ProtocolViolationError("step_index must be a nonnegative integer")
    if scenario_id is not None:
        _nonempty(scenario_id, "scenario_id")
    if geometry_signature is not None:
        _nonempty(geometry_signature, "geometry_signature")

    snapshot = snapshot_typed_result(result, label="history_event_source", scenario_id=scenario_id or "history_event")
    value = StatusEventValue(
        stream_id=stream_id,
        observation_key=observation_key,
        step_index=step_index,
        scenario_id=scenario_id,
        source_protocol=snapshot.protocol_identity,
        source_status_family=snapshot.status_family,
        source_status=snapshot.status,
        source_validity=snapshot.validity,
        source_conditioning=snapshot.conditioning["status"],
        source_trace_id=snapshot.trace_id,
        source_operation_id=snapshot.operation_id,
        source_expression_path=snapshot.expression_path,
        source_precision=result.provenance.precision,
        source_backend=result.provenance.backend,
        source_device=result.provenance.device,
        geometry_signature=geometry_signature,
    )
    return TypedResult(
        value=value,
        space="HistoryEvent",
        status=HistoryStatus.HISTORY_EVENT_RECORDED,
        validity=_validity(HistoryStatus.HISTORY_EVENT_RECORDED),
        conditioning=_conditioning(HistoryStatus.HISTORY_EVENT_RECORDED),
        provenance=Provenance(
            operation_id="record_status_event",
            expression_path="history_status_event_recording",
            precision=result.provenance.precision,
            backend=result.provenance.backend,
            device=result.provenance.device,
            measurement_resolution=result.provenance.measurement_resolution,
            parents=(snapshot.trace_id,),
        ),
        protocol=ProtocolStatus.OK,
    )


def compare_status_events(previous_event: HistoryResult, next_event: HistoryResult) -> HistoryTransitionResult:
    previous_ok = _event_result(previous_event)
    next_ok = _event_result(next_event)
    if previous_ok is None or next_ok is None:
        return _transition_result(
            None,
            None,
            HistoryStatus.HISTORY_TRANSITION_INCOMPARABLE,
            ("event_status",),
            "both inputs must be recorded history events",
        )
    previous = previous_ok.value
    next_value = next_ok.value
    changed = _changed_fields(previous, next_value)
    if previous.stream_id != next_value.stream_id:
        status = HistoryStatus.HISTORY_TRANSITION_INCOMPARABLE
        reason = "stream_id differs"
    elif previous.observation_key != next_value.observation_key:
        status = HistoryStatus.HISTORY_TRANSITION_INCOMPARABLE
        reason = "observation_key differs"
    elif next_value.step_index <= previous.step_index:
        status = HistoryStatus.HISTORY_TRANSITION_INCOMPARABLE
        reason = "step_index is not increasing"
    elif "source_protocol" in changed:
        status = HistoryStatus.HISTORY_TRANSITION_PROTOCOL_CHANGED
        reason = "source protocol changed"
    elif "source_status_family" in changed:
        status = HistoryStatus.HISTORY_TRANSITION_STATUS_FAMILY_CHANGED
        reason = "source status family changed"
    elif "source_status" in changed:
        status = HistoryStatus.HISTORY_TRANSITION_STATUS_CHANGED
        reason = "source status changed"
    elif "source_validity" in changed:
        status = HistoryStatus.HISTORY_TRANSITION_VALIDITY_CHANGED
        reason = "source validity changed"
    elif "geometry_signature" in changed:
        status = HistoryStatus.HISTORY_TRANSITION_GEOMETRY_CHANGED
        reason = "geometry signature changed"
    else:
        status = HistoryStatus.HISTORY_TRANSITION_STABLE
        reason = "status event evidence is stable"
    return _transition_result(previous_ok, next_ok, status, tuple(changed), reason)


def build_status_trace(events: Sequence[HistoryResult]) -> HistoryTraceResult:
    event_tuple = tuple(events)
    if not event_tuple:
        return _trace_result((), (), HistoryStatus.HISTORY_TRACE_EMPTY, ("empty_event_list",))
    valid_events = tuple(_event_result(event) for event in event_tuple)
    if any(event is None for event in valid_events):
        return _trace_result(tuple(event for event in event_tuple if isinstance(event, TypedResult)), (), HistoryStatus.HISTORY_TRACE_INCOMPLETE, ("non_event_input",))
    recorded = tuple(event for event in valid_events if event is not None)
    if len({event.value.stream_id for event in recorded}) != 1:
        return _trace_result(recorded, (), HistoryStatus.HISTORY_TRACE_INCOMPLETE, ("mixed_stream_id",))
    if len({event.value.observation_key for event in recorded}) != 1:
        return _trace_result(recorded, (), HistoryStatus.HISTORY_TRACE_INCOMPLETE, ("mixed_observation_key",))
    if len(recorded) == 1:
        return _trace_result(recorded, (), HistoryStatus.HISTORY_TRACE_SINGLETON, ("single_event",))
    if any(next_event.value.step_index <= previous.value.step_index for previous, next_event in zip(recorded, recorded[1:])):
        return _trace_result(recorded, (), HistoryStatus.HISTORY_TRACE_UNORDERED, ("step_index_not_increasing",))

    transitions = tuple(compare_status_events(previous, next_event) for previous, next_event in zip(recorded, recorded[1:]))
    if any(transition.status is HistoryStatus.HISTORY_TRANSITION_INCOMPARABLE for transition in transitions):
        return _trace_result(recorded, transitions, HistoryStatus.HISTORY_TRACE_INCOMPLETE, ("incomparable_transition",))
    if all(transition.status is HistoryStatus.HISTORY_TRANSITION_STABLE for transition in transitions):
        return _trace_result(recorded, transitions, HistoryStatus.HISTORY_TRACE_STABLE, ())
    return _trace_result(recorded, transitions, HistoryStatus.HISTORY_TRACE_TRANSITIONED, ("status_transition_observed",))


def require_stable_status_trace(trace_result: HistoryResult) -> HistoryResult:
    check = validate_protocol(trace_result, STABLE_HISTORY_TRACE_PROTOCOL)
    if check.ok:
        return trace_result
    status = trace_result.status if isinstance(getattr(trace_result, "status", None), HistoryStatus) else HistoryStatus.HISTORY_TRACE_INCOMPLETE
    refusal = TypedRefusal(
        reason=f"stable history trace required: {check.reason}",
        status=ProtocolStatus.SCALARIZATION_REFUSED,
        details={"trace_status": getattr(getattr(trace_result, "status", None), "value", None)},
    )
    return TypedResult(
        value=trace_result.value,
        space="HistoryTrace",
        status=status,
        validity=_validity(status),
        conditioning=Conditioning(status=ConditioningStatus.WARNING),
        provenance=Provenance(
            operation_id="require_stable_status_trace",
            expression_path="history_trace_stable_requirement",
            parents=(trace_result.provenance.trace_id,),
        ),
        protocol=ProtocolStatus.SCALARIZATION_REFUSED,
        refusal=refusal,
    )


def _nonempty(value: str, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ProtocolViolationError(f"{name} must be a nonempty string")


def _event_result(result: object) -> HistoryEventResult | None:
    if not isinstance(result, TypedResult):
        return None
    if result.status is not HistoryStatus.HISTORY_EVENT_RECORDED:
        return None
    if not isinstance(result.value, StatusEventValue):
        return None
    return result


def _changed_fields(previous: StatusEventValue, next_value: StatusEventValue) -> tuple[str, ...]:
    changed: list[str] = []
    for field_name in (
        "stream_id",
        "observation_key",
        "source_protocol",
        "source_status_family",
        "source_status",
        "source_validity",
        "geometry_signature",
    ):
        if getattr(previous, field_name) != getattr(next_value, field_name):
            changed.append(field_name)
    return tuple(changed)


def _transition_result(
    previous_event: HistoryEventResult | None,
    next_event: HistoryEventResult | None,
    status: HistoryStatus,
    changed_fields: tuple[str, ...],
    reason: str,
) -> HistoryTransitionResult:
    previous = None if previous_event is None else previous_event.value
    next_value = None if next_event is None else next_event.value
    value = StatusTransitionValue(
        stream_id="" if previous is None else previous.stream_id,
        observation_key="" if previous is None else previous.observation_key,
        previous_step_index=None if previous is None else previous.step_index,
        next_step_index=None if next_value is None else next_value.step_index,
        previous_event_trace_id=None if previous_event is None else previous_event.provenance.trace_id,
        next_event_trace_id=None if next_event is None else next_event.provenance.trace_id,
        previous_source_trace_id=None if previous is None else previous.source_trace_id,
        next_source_trace_id=None if next_value is None else next_value.source_trace_id,
        changed_fields=changed_fields,
        comparison_reason=reason,
    )
    parents = tuple(
        trace_id
        for trace_id in (
            None if previous_event is None else previous_event.provenance.trace_id,
            None if next_event is None else next_event.provenance.trace_id,
        )
        if trace_id is not None
    )
    return TypedResult(
        value=value,
        space="HistoryTransition",
        status=status,
        validity=_validity(status),
        conditioning=_conditioning(status),
        provenance=Provenance(
            operation_id="compare_status_events",
            expression_path="history_event_pair_comparison",
            parents=parents,
        ),
        protocol=ProtocolStatus.OK,
    )


def _trace_result(
    events: tuple[HistoryEventResult | TypedResult, ...],
    transitions: tuple[HistoryTransitionResult, ...],
    status: HistoryStatus,
    notes: tuple[str, ...],
) -> HistoryTraceResult:
    event_values = tuple(event.value for event in events if isinstance(event, TypedResult) and isinstance(event.value, StatusEventValue))
    value = StatusTraceValue(
        stream_id=event_values[0].stream_id if event_values else None,
        observation_key=event_values[0].observation_key if event_values else None,
        event_count=len(events),
        first_step_index=event_values[0].step_index if event_values else None,
        last_step_index=event_values[-1].step_index if event_values else None,
        event_trace_ids=tuple(event.provenance.trace_id for event in events if isinstance(event, TypedResult) and isinstance(event.value, StatusEventValue)),
        source_trace_ids=tuple(event.source_trace_id for event in event_values),
        transition_trace_ids=tuple(transition.provenance.trace_id for transition in transitions),
        transition_status_counts=_status_counts(transitions),
        stable=status is HistoryStatus.HISTORY_TRACE_STABLE,
        transition_count=len(transitions),
        notes=notes,
    )
    return TypedResult(
        value=value,
        space="HistoryTrace",
        status=status,
        validity=_validity(status),
        conditioning=_conditioning(status),
        provenance=Provenance(
            operation_id="build_status_trace",
            expression_path="history_ordered_status_trace",
            parents=value.event_trace_ids,
        ),
        protocol=ProtocolStatus.OK,
    )


def _status_counts(transitions: tuple[HistoryTransitionResult, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for transition in transitions:
        counts[transition.status.value] = counts.get(transition.status.value, 0) + 1
    return counts


def _validity(status: HistoryStatus) -> Validity:
    if status in {
        HistoryStatus.HISTORY_EVENT_RECORDED,
        HistoryStatus.HISTORY_TRANSITION_STABLE,
        HistoryStatus.HISTORY_TRANSITION_PROTOCOL_CHANGED,
        HistoryStatus.HISTORY_TRANSITION_STATUS_FAMILY_CHANGED,
        HistoryStatus.HISTORY_TRANSITION_STATUS_CHANGED,
        HistoryStatus.HISTORY_TRANSITION_VALIDITY_CHANGED,
        HistoryStatus.HISTORY_TRANSITION_GEOMETRY_CHANGED,
        HistoryStatus.HISTORY_TRACE_STABLE,
        HistoryStatus.HISTORY_TRACE_TRANSITIONED,
    }:
        return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
    if status is HistoryStatus.HISTORY_TRACE_SINGLETON:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning(status: HistoryStatus) -> Conditioning:
    if status in {
        HistoryStatus.HISTORY_EVENT_RECORDED,
        HistoryStatus.HISTORY_TRANSITION_STABLE,
        HistoryStatus.HISTORY_TRACE_STABLE,
    }:
        return Conditioning(status=ConditioningStatus.WELL_CONDITIONED)
    return Conditioning(status=ConditioningStatus.WARNING)
