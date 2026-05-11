from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .result import TypedResult
from .status import ProtocolStatus, StatusCode


@dataclass(frozen=True, slots=True)
class ProducerProtocol:
    name: str
    emitted_statuses: frozenset[StatusCode]
    required_fields: frozenset[str] = frozenset()
    status_family: type[Enum] | None = None

    def __post_init__(self) -> None:
        if self.status_family is None and self.emitted_statuses:
            object.__setattr__(self, "status_family", type(next(iter(self.emitted_statuses))))


@dataclass(frozen=True, slots=True)
class ConsumerProtocol:
    name: str
    accepted_statuses: frozenset[StatusCode]
    required_validity_fields: frozenset[str] = frozenset()
    scalarization_allowed: bool = False
    status_family: type[Enum] | None = None
    refused_statuses: frozenset[StatusCode] | None = None

    def __post_init__(self) -> None:
        if self.status_family is None and self.accepted_statuses:
            object.__setattr__(self, "status_family", type(next(iter(self.accepted_statuses))))


@dataclass(frozen=True, slots=True)
class ProtocolCheck:
    status: ProtocolStatus
    reason: str

    @property
    def ok(self) -> bool:
        return self.status is ProtocolStatus.OK


def validate_protocol(result: TypedResult, consumer: ConsumerProtocol) -> ProtocolCheck:
    if not isinstance(result, TypedResult):
        return ProtocolCheck(
            status=ProtocolStatus.VIOLATION,
            reason=f"consumer {consumer.name!r} requires TypedResult input",
        )

    if consumer.status_family is not None and not isinstance(result.status, consumer.status_family):
        return ProtocolCheck(
            status=ProtocolStatus.VIOLATION,
            reason=(
                f"status family mismatch for consumer {consumer.name!r}: "
                f"expected {consumer.status_family.__name__}, got {type(result.status).__name__}"
            ),
        )

    missing_fields = [
        field_name
        for field_name in consumer.required_validity_fields
        if getattr(result.validity, field_name, None) is None
    ]
    if missing_fields:
        return ProtocolCheck(
            status=ProtocolStatus.VIOLATION,
            reason=f"missing required validity fields: {', '.join(sorted(missing_fields))}",
        )

    if result.status not in consumer.accepted_statuses:
        return ProtocolCheck(
            status=ProtocolStatus.VIOLATION,
            reason=f"unhandled status {result.status.value!r} for consumer {consumer.name!r}",
        )

    if result.refusal is not None and consumer.scalarization_allowed:
        return ProtocolCheck(
            status=ProtocolStatus.VIOLATION,
            reason=f"typed refusal cannot be scalarized by consumer {consumer.name!r}",
        )

    return ProtocolCheck(status=ProtocolStatus.OK, reason="accepted")
