from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .status import ConditioningStatus


@dataclass(frozen=True, slots=True)
class Conditioning:
    status: ConditioningStatus = ConditioningStatus.UNKNOWN
    notes: tuple[str, ...] = ()

    def to_json_safe(self) -> dict[str, Any]:
        return {"status": self.status.value, "notes": list(self.notes)}
