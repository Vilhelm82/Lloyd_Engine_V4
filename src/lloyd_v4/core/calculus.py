from __future__ import annotations

from collections.abc import Iterable

from .errors import ProtocolViolationError, UnhandledStratumError
from .status import ProtocolStatus, StatusCode, ValidityStatus


def join_statuses(name: str, statuses: Iterable[StatusCode]) -> StatusCode:
    unique = frozenset(statuses)
    if not unique:
        raise ProtocolViolationError(f"{name}: status join requires at least one status")
    if len(unique) == 1:
        return next(iter(unique))
    raise ProtocolViolationError(
        f"{name}: mixed status join is not implicit: "
        + ", ".join(sorted(status.value for status in unique))
    )


def propagate_invalid(status: StatusCode) -> StatusCode:
    if status is ValidityStatus.INVALID:
        return ValidityStatus.INVALID
    if status is ValidityStatus.UNKNOWN:
        return ValidityStatus.UNKNOWN
    return status


def require_handled_status(status: StatusCode, handled: frozenset[StatusCode], context: str) -> None:
    if status not in handled:
        raise UnhandledStratumError(f"{context}: unhandled status {status.value!r}")


def require_protocol_ok(status: ProtocolStatus, context: str) -> None:
    if status is not ProtocolStatus.OK:
        raise ProtocolViolationError(f"{context}: protocol status {status.value!r}")
