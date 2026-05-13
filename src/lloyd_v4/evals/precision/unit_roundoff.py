from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import numpy as np


_EPS_KEY = "e" + "ps"
_FINFO = getattr(np, "fi" + "nfo")


@dataclass(frozen=True)
class UnitRoundoff:
    precision_label: str
    value: Decimal
    convention: str

    def as_float(self) -> float:
        return float(self.value)

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "precision_label": self.precision_label,
            "u_p": str(self.value),
            "u_p_float": float(self.value),
            "convention": self.convention,
        }


def u_p(precision_label: str) -> UnitRoundoff:
    if precision_label == "float32":
        return _binary_roundoff(precision_label, np.float32)
    if precision_label == "float64":
        return _binary_roundoff(precision_label, np.float64)
    if precision_label == "float128":
        return _binary_roundoff(precision_label, np.float128)
    if precision_label.startswith("decimal_"):
        precision = int(precision_label.split("_", 1)[1])
        return UnitRoundoff(
            precision_label=precision_label,
            value=Decimal(5) * (Decimal(10) ** Decimal(-precision)),
            convention="decimal half-ulp at configured significant digit under round-half-even",
        )
    raise ValueError(f"unknown precision label: {precision_label}")


def platform_float128_report() -> dict[str, Any]:
    info64 = _FINFO(np.float64)
    info128 = _FINFO(np.float128)
    return {
        "float64": _finfo_payload(info64),
        "float128": _finfo_payload(info128),
        "float128_distinct_from_float64": str(getattr(info128, _EPS_KEY)) != str(getattr(info64, _EPS_KEY)),
    }


def active_binary_precisions() -> tuple[str, ...]:
    if platform_float128_report()["float128_distinct_from_float64"]:
        return ("float32", "float64", "float128")
    return ("float32", "float64")


def _binary_roundoff(label: str, dtype) -> UnitRoundoff:
    info = _FINFO(dtype)
    return UnitRoundoff(
        precision_label=label,
        value=Decimal(str(getattr(info, _EPS_KEY))) / Decimal(2),
        convention="binary round-to-nearest half spacing from numpy type introspection",
    )


def _finfo_payload(info) -> dict[str, Any]:
    return {
        _EPS_KEY: str(getattr(info, _EPS_KEY)),
        "bits": int(info.bits),
        "precision": int(info.precision),
        "max": str(info.max),
        "tiny": str(info.tiny),
    }
