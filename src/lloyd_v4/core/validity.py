from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ArrayLike = Any


@dataclass(frozen=True, slots=True)
class Validity:
    defined: ArrayLike | None = None
    finite: ArrayLike | None = None
    selectable: ArrayLike | None = None
    advanceable: ArrayLike | None = None
    observable: ArrayLike | None = None

    def to_json_safe(self) -> dict[str, Any]:
        from .serialization import to_json_safe

        return {
            "defined": to_json_safe(self.defined),
            "finite": to_json_safe(self.finite),
            "selectable": to_json_safe(self.selectable),
            "advanceable": to_json_safe(self.advanceable),
            "observable": to_json_safe(self.observable),
        }
