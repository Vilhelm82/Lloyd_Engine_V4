from __future__ import annotations

from typing import Dict

import numpy as np

from .pure_algebraic_four_form import x_grid


FORM_KEYS = ("F1", "F2", "F3", "F4")


def f_direct(x: float) -> float:
    return 1.0 - float(x)


def f_alt_routing(x: float) -> float:
    x_value = float(x)
    return (1.0 - x_value / 2.0) - x_value / 2.0


def R_of_x(x: float) -> float:
    return float(np.cbrt(f_direct(x)))


def F1_of_x(x: float) -> float:
    x_value = float(x)
    root = R_of_x(x_value)
    return root * root * root - f_direct(x_value)


def F2_of_x(x: float) -> float:
    x_value = float(x)
    root = R_of_x(x_value)
    return root * root * root - 1.0 + x_value


def F3_of_x(x: float) -> float:
    x_value = float(x)
    return R_of_x(x_value) - float(np.cbrt(f_direct(x_value)))


def F4_of_x(x: float) -> float:
    x_value = float(x)
    return R_of_x(x_value) - float(np.cbrt(f_alt_routing(x_value)))


def four_form_float32(x: float) -> Dict[str, float]:
    s = np.float32
    one = s(1.0)
    two = s(2.0)
    x_value = s(x)
    direct = one - x_value
    split = (one - x_value / two) - x_value / two
    root = np.cbrt(direct)
    split_root = np.cbrt(split)
    root_cubed = root * root * root
    return {
        "F1": float(root_cubed - direct),
        "F2": float(root_cubed - one + x_value),
        "F3": float(root - np.cbrt(direct)),
        "F4": float(root - split_root),
    }


def four_form_float64(x: float) -> Dict[str, float]:
    return {
        "F1": F1_of_x(x),
        "F2": F2_of_x(x),
        "F3": F3_of_x(x),
        "F4": F4_of_x(x),
    }


def cbrt_four_form_battery() -> dict[str, object]:
    points = []
    nonzero_counts = {form_id: {"float32": 0, "float64": 0} for form_id in FORM_KEYS}
    values = x_grid()
    for x_value in values:
        values32 = four_form_float32(x_value)
        values64 = four_form_float64(x_value)
        for form_id in FORM_KEYS:
            if values32[form_id] != 0.0:
                nonzero_counts[form_id]["float32"] += 1
            if values64[form_id] != 0.0:
                nonzero_counts[form_id]["float64"] += 1
        points.append({"x": x_value, "float32": values32, "float64": values64})
    return {
        "campaign": "task029c_cbrt_four_form_battery",
        "x_count": len(values),
        "x_min": values[0],
        "x_max": values[-1],
        "per_form_nonzero": nonzero_counts,
        "points": points,
    }
