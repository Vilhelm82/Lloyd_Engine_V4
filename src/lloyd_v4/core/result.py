from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

from .conditioning import Conditioning
from .provenance import Provenance
from .serialization import to_json_safe
from .status import ProtocolStatus, StatusCode
from .validity import Validity


ValueT = TypeVar("ValueT")
StatusT = TypeVar("StatusT", bound=Enum)


@dataclass(frozen=True, slots=True)
class TypedRefusal:
    reason: str
    status: ProtocolStatus = ProtocolStatus.SCALARIZATION_REFUSED
    details: dict[str, Any] | None = None

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "reason": self.reason,
            "status": self.status.value,
            "details": to_json_safe(self.details),
        }


@dataclass(frozen=True, slots=True)
class TypedResult(Generic[ValueT, StatusT]):
    value: ValueT
    space: str
    status: StatusT
    validity: Validity
    conditioning: Conditioning
    provenance: Provenance
    protocol: ProtocolStatus = ProtocolStatus.OK
    refusal: TypedRefusal | None = None

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "value": to_json_safe(self.value),
            "space": self.space,
            "status": self.status.value,
            "validity": self.validity.to_json_safe(),
            "conditioning": self.conditioning.to_json_safe(),
            "provenance": self.provenance.to_json_safe(),
            "protocol": self.protocol.value,
            "refusal": None if self.refusal is None else self.refusal.to_json_safe(),
        }
