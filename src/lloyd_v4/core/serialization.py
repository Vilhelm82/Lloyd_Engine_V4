from __future__ import annotations

import math
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any


def to_json_safe(value: Any) -> Any:
    if isinstance(value, float):
        if math.isnan(value):
            return {"kind": "nonfinite_float", "value": "nan"}
        if math.isinf(value):
            return {"kind": "nonfinite_float", "value": "inf" if value > 0 else "-inf"}
        return value
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        if hasattr(value, "to_json_safe"):
            return value.to_json_safe()
        return to_json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): to_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]
    if isinstance(value, set | frozenset):
        return sorted(to_json_safe(item) for item in value)
    return value
