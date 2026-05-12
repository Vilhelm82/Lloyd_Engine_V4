from __future__ import annotations

from typing import Dict

import numpy as np


FORM_KEYS = ("F1", "F2", "F3", "F4")
_X_MIN = 0.01
_X_MAX = 0.99
_GRID_COUNT = 137


def x_grid() -> tuple[float, ...]:
    interval = (_X_MAX - _X_MIN) / float(_GRID_COUNT - 1)
    return tuple(_X_MIN + interval * index for index in range(_GRID_COUNT))


def f_of_x(x: float) -> float:
    return 1.0 - float(x)


def f_of_x_split_routing(x: float) -> float:
    x_value = float(x)
    return (1.0 - x_value / 2.0) - x_value / 2.0


def R_of_x(x: float) -> float:
    return f_of_x(x) ** 0.5


def F1_of_x(x: float) -> float:
    x_value = float(x)
    root = R_of_x(x_value)
    return root**2 - f_of_x(x_value)


def F2_of_x(x: float) -> float:
    x_value = float(x)
    root = R_of_x(x_value)
    return root**2 - 1.0 + x_value


def F3_of_x(x: float) -> float:
    root = R_of_x(x)
    return root - root


def F4_of_x(x: float) -> float:
    x_value = float(x)
    return R_of_x(x_value) - f_of_x_split_routing(x_value) ** 0.5


def four_form_float32(x: float) -> Dict[str, float]:
    s = np.float32
    one = s(1.0)
    two = s(2.0)
    half = s(0.5)
    x_value = s(x)
    direct = one - x_value
    split = (one - x_value / two) - x_value / two
    root = direct**half
    split_root = split**half
    return {
        "F1": float(root**two - direct),
        "F2": float(root**two - one + x_value),
        "F3": float(root - root),
        "F4": float(root - split_root),
    }


def four_form_float64(x: float) -> Dict[str, float]:
    return {
        "F1": F1_of_x(x),
        "F2": F2_of_x(x),
        "F3": F3_of_x(x),
        "F4": F4_of_x(x),
    }


def four_form_decimal_oracle(x: float, precision: int = 50) -> Dict[str, float]:
    from decimal import Decimal, localcontext

    with localcontext() as context:
        context.prec = precision
        one = Decimal(1)
        two = Decimal(2)
        half = one / two
        x_value = Decimal.from_float(float(x))
        direct = one - x_value
        split = (one - x_value / two) - x_value / two
        root = direct**half
        split_root = split**half
        return {
            "F1": float(root**two - direct),
            "F2": float(root**two - one + x_value),
            "F3": float(root - root),
            "F4": float(root - split_root),
        }


def pure_algebraic_four_form_battery() -> dict[str, object]:
    points = []
    nonzero_counts = {form_id: {"float32": 0, "float64": 0, "decimal_50": 0} for form_id in FORM_KEYS}
    values = x_grid()
    for x_value in values:
        values32 = four_form_float32(x_value)
        values64 = four_form_float64(x_value)
        values_decimal = four_form_decimal_oracle(x_value, 50)
        for form_id in FORM_KEYS:
            if values32[form_id] != 0.0:
                nonzero_counts[form_id]["float32"] += 1
            if values64[form_id] != 0.0:
                nonzero_counts[form_id]["float64"] += 1
            if values_decimal[form_id] != 0.0:
                nonzero_counts[form_id]["decimal_50"] += 1
        points.append({"x": x_value, "float32": values32, "float64": values64, "decimal_50": values_decimal})
    return {
        "campaign": "task028_pure_algebraic_four_form_battery",
        "x_count": len(values),
        "x_min": values[0],
        "x_max": values[-1],
        "per_form_nonzero": nonzero_counts,
        "points": points,
    }
