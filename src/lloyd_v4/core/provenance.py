from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .serialization import to_json_safe
from .status import ProvenanceStatus


@dataclass(frozen=True, slots=True)
class Provenance:
    operation_id: str
    expression_path: str
    precision: str = "unspecified"
    backend: str = "python"
    device: str = "cpu"
    measurement_resolution: Any | None = None
    inputs: tuple[Any, ...] = ()
    parents: tuple[str, ...] = ()
    trace_id: str | None = None
    status: ProvenanceStatus = ProvenanceStatus.COMPLETE

    def __post_init__(self) -> None:
        if self.trace_id is None:
            object.__setattr__(self, "trace_id", self._derive_trace_id())

    def _derive_trace_id(self) -> str:
        payload = {
            "operation_id": self.operation_id,
            "expression_path": self.expression_path,
            "precision": self.precision,
            "backend": self.backend,
            "device": self.device,
            "measurement_resolution": to_json_safe(self.measurement_resolution),
            "inputs": _identity_safe_inputs(self.inputs),
            "parents": list(self.parents),
            "status": self.status.value,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "expression_path": self.expression_path,
            "precision": self.precision,
            "backend": self.backend,
            "device": self.device,
            "measurement_resolution": to_json_safe(self.measurement_resolution),
            "inputs": _identity_safe_inputs(self.inputs),
            "parents": list(self.parents),
            "trace_id": self.trace_id,
            "status": self.status.value,
        }


def _identity_safe_inputs(inputs: tuple[Any, ...]) -> list[Any]:
    return _json_compatible(to_json_safe(list(inputs)))


def _json_compatible(value: Any) -> Any:
    if value is None or isinstance(value, str | int | bool):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, list | tuple):
        return [_json_compatible(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_compatible(item) for key, item in value.items()}
    try:
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError):
        return {
            "kind": "python_object",
            "type": f"{type(value).__module__}.{type(value).__qualname__}",
            "repr": repr(value),
        }
    return value
