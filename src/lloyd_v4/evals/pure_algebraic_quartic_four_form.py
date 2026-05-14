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


def quartic_root_from_direct(value: float) -> float:
    return float(np.sqrt(np.sqrt(float(value))))


def R_of_x(x: float) -> float:
    return quartic_root_from_direct(f_direct(x))


def F1_of_x(x: float) -> float:
    x_value = float(x)
    root = R_of_x(x_value)
    root_fourth = root_fourth_from_root(root)
    return root_fourth - f_direct(x_value)


def F2_of_x(x: float) -> float:
    x_value = float(x)
    root = R_of_x(x_value)
    root_fourth = root_fourth_from_root(root)
    return root_fourth - 1.0 + x_value


def F3_of_x(x: float) -> float:
    x_value = float(x)
    return R_of_x(x_value) - quartic_root_from_direct(f_direct(x_value))


def F4_of_x(x: float) -> float:
    x_value = float(x)
    return R_of_x(x_value) - quartic_root_from_direct(f_alt_routing(x_value))


def root_fourth_from_root(root: float) -> float:
    squared = root * root
    return squared * squared


def four_form_float32(x: float) -> Dict[str, float]:
    s = np.float32
    one = s(1.0)
    two = s(2.0)
    x_value = s(x)
    direct = one - x_value
    split = (one - x_value / two) - x_value / two
    root = np.sqrt(np.sqrt(direct))
    split_root = np.sqrt(np.sqrt(split))
    root_squared = root * root
    root_fourth = root_squared * root_squared
    return {
        "F1": float(root_fourth - direct),
        "F2": float(root_fourth - one + x_value),
        "F3": float(root - np.sqrt(np.sqrt(direct))),
        "F4": float(root - split_root),
    }


def four_form_float64(x: float) -> Dict[str, float]:
    return {
        "F1": F1_of_x(x),
        "F2": F2_of_x(x),
        "F3": F3_of_x(x),
        "F4": F4_of_x(x),
    }


def quartic_four_form_battery() -> dict[str, object]:
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
        "campaign": "task032_quartic_four_form_battery",
        "x_count": len(values),
        "x_min": values[0],
        "x_max": values[-1],
        "per_form_nonzero": nonzero_counts,
        "points": points,
    }
