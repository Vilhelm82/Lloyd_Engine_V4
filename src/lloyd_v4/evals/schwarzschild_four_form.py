from __future__ import annotations

import csv
from pathlib import Path


M = 1.0

_ROOT = Path(__file__).resolve().parents[3]
_REPORT_DIR = _ROOT / "Build_Docs" / "Reports" / "task024b_schwarzschild_four_form"
_CSV_PATH = _REPORT_DIR / "v3_reference_overlay.csv"


def f_of_r(r: float) -> float:
    return 1.0 - 2.0 / r


def R_of_r(r: float) -> float:
    return (1.0 - 2.0 / r) ** 0.5


def F1_of_r(r: float) -> float:
    return R_of_r(r) ** 2 - (1.0 - 2.0 / r)


def F2_of_r(r: float) -> float:
    return R_of_r(r) ** 2 - 1.0 + 2.0 / r


def F3_of_r(r: float) -> float:
    return R_of_r(r) - (1.0 - 2.0 / r) ** 0.5


def F4_of_r(r: float) -> float:
    return R_of_r(r) - ((r - 2.0) / r) ** 0.5


def delta_f_of_r(r: float) -> float:
    return (1.0 - 2.0 / r) - (r - 2.0) / r


def sweep_r_values() -> tuple[float, ...]:
    return tuple(float(row["re"]) for row in _reference_rows())


def _reference_rows() -> tuple[dict[str, str], ...]:
    with _CSV_PATH.open(newline="", encoding="utf-8") as handle:
        return tuple(csv.DictReader(handle))
