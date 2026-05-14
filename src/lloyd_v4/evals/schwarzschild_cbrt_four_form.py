from __future__ import annotations

from typing import Dict

import numpy as np

from .schwarzschild_four_form import f_of_r, sweep_r_values


FORM_KEYS = ("F1", "F2", "F3", "F4")


def f_direct(r: float) -> float:
    return f_of_r(float(r))


def f_alt_routing(r: float) -> float:
    r_value = float(r)
    return (r_value - 2.0) / r_value


def R_of_r(r: float) -> float:
    return float(np.cbrt(f_direct(r)))


def root_cubed_from_root(root: float) -> float:
    return root * root * root


def F1_of_r(r: float) -> float:
    r_value = float(r)
    root = R_of_r(r_value)
    return root_cubed_from_root(root) - f_direct(r_value)


def F2_of_r(r: float) -> float:
    r_value = float(r)
    root = R_of_r(r_value)
    return root_cubed_from_root(root) - 1.0 + 2.0 / r_value


def F3_of_r(r: float) -> float:
    r_value = float(r)
    return R_of_r(r_value) - float(np.cbrt(f_direct(r_value)))


def F4_of_r(r: float) -> float:
    r_value = float(r)
    return R_of_r(r_value) - float(np.cbrt(f_alt_routing(r_value)))


def four_form_float32(r: float) -> Dict[str, float]:
    s = np.float32
    one = s(1.0)
    two = s(2.0)
    r_value = s(r)
    direct = one - two / r_value
    alternate = (r_value - two) / r_value
    root = np.cbrt(direct)
    alternate_root = np.cbrt(alternate)
    root_cubed = root * root * root
    return {
        "F1": float(root_cubed - direct),
        "F2": float(root_cubed - one + two / r_value),
        "F3": float(root - np.cbrt(direct)),
        "F4": float(root - alternate_root),
    }


def four_form_float64(r: float) -> Dict[str, float]:
    return {
        "F1": F1_of_r(r),
        "F2": F2_of_r(r),
        "F3": F3_of_r(r),
        "F4": F4_of_r(r),
    }


def schwarzschild_cbrt_four_form_battery() -> dict[str, object]:
    points = []
    nonzero_counts = {form_id: {"float32": 0, "float64": 0} for form_id in FORM_KEYS}
    values = sweep_r_values()
    for r_value in values:
        values32 = four_form_float32(r_value)
        values64 = four_form_float64(r_value)
        for form_id in FORM_KEYS:
            if values32[form_id] != 0.0:
                nonzero_counts[form_id]["float32"] += 1
            if values64[form_id] != 0.0:
                nonzero_counts[form_id]["float64"] += 1
        points.append({"r": r_value, "float32": values32, "float64": values64})
    return {
        "campaign": "task033_schwarzschild_cbrt_four_form_battery",
        "r_count": len(values),
        "r_min": values[0],
        "r_max": values[-1],
        "per_form_nonzero": nonzero_counts,
        "points": points,
    }
