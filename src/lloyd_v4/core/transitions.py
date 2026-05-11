from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Any

from .errors import ProtocolViolationError


class TransitionDisposition(StrEnum):
    MAPPED = "mapped"
    ACCEPTED = "accepted"
    REFUSED = "refused"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True, slots=True)
class StatusTransitionOutcome:
    rule_id: str
    input_status: Enum
    disposition: TransitionDisposition
    output_status: Enum | None = None
    reason: str | None = None

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "input_status": self.input_status.value,
            "disposition": self.disposition.value,
            "output_status": None if self.output_status is None else self.output_status.value,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class StatusTransitionRule:
    rule_id: str
    input_status_family: type[Enum]
    output_status_family: type[Enum] | None
    input_protocol_id: str | None
    output_protocol_id: str | None
    accepted_input_statuses: frozenset[Enum]
    refused_input_statuses: frozenset[Enum]
    mapped_statuses: Mapping[Enum, Enum]
    context_keys: tuple[str, ...] = ()
    description: str = ""
    emitted_input_statuses: frozenset[Enum] = frozenset()
    transition: Callable[[Enum, Mapping[str, Any]], StatusTransitionOutcome] | None = None

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "input_status_family": self.input_status_family.__name__,
            "output_status_family": None if self.output_status_family is None else self.output_status_family.__name__,
            "input_protocol_id": self.input_protocol_id,
            "output_protocol_id": self.output_protocol_id,
            "accepted_statuses": sorted(status.value for status in self.accepted_input_statuses),
            "refused_statuses": sorted(status.value for status in self.refused_input_statuses),
            "mapped_statuses": {
                source.value: target.value for source, target in self.mapped_statuses.items()
            },
            "context_keys": list(self.context_keys),
            "description": self.description,
        }


def assert_transition_rule_complete(rule: StatusTransitionRule) -> None:
    covered = (
        set(rule.accepted_input_statuses)
        | set(rule.refused_input_statuses)
        | set(rule.mapped_statuses)
    )
    expected = set(rule.emitted_input_statuses)
    if expected and covered != expected:
        missing = sorted(status.value for status in expected - covered)
        extra = sorted(status.value for status in covered - expected)
        raise ProtocolViolationError(
            f"transition rule {rule.rule_id!r} coverage mismatch; missing={missing}, extra={extra}"
        )


def apply_status_transition(rule: StatusTransitionRule, status: Enum, **context: Any) -> StatusTransitionOutcome:
    if not isinstance(status, rule.input_status_family):
        raise ProtocolViolationError(
            f"status family mismatch for rule {rule.rule_id!r}: "
            f"expected {rule.input_status_family.__name__}, got {type(status).__name__}"
        )
    missing = [key for key in rule.context_keys if key not in context]
    if missing:
        raise ProtocolViolationError(
            f"transition rule {rule.rule_id!r} missing context keys: {', '.join(missing)}"
        )
    if rule.transition is not None:
        return rule.transition(status, context)
    if status in rule.mapped_statuses:
        return StatusTransitionOutcome(
            rule_id=rule.rule_id,
            input_status=status,
            disposition=TransitionDisposition.MAPPED,
            output_status=rule.mapped_statuses[status],
        )
    if status in rule.accepted_input_statuses:
        return StatusTransitionOutcome(
            rule_id=rule.rule_id,
            input_status=status,
            disposition=TransitionDisposition.ACCEPTED,
        )
    if status in rule.refused_input_statuses:
        return StatusTransitionOutcome(
            rule_id=rule.rule_id,
            input_status=status,
            disposition=TransitionDisposition.REFUSED,
        )
    return StatusTransitionOutcome(
        rule_id=rule.rule_id,
        input_status=status,
        disposition=TransitionDisposition.NOT_APPLICABLE,
        reason="status not covered by transition rule",
    )
