from __future__ import annotations

from typing import Dict

import numpy as np


FORM_KEYS = ("F1", "F2", "F3", "F4")
_BETA_MIN = 0.01
_BETA_MAX = 0.9999
_GRID_COUNT = 137


def beta_grid() -> tuple[float, ...]:
    step = (_BETA_MAX - _BETA_MIN) / float(_GRID_COUNT - 1)
    return tuple(_BETA_MIN + step * index for index in range(_GRID_COUNT))


def eta_of_beta(beta: float) -> float:
    beta_value = float(beta)
    return (1.0 - beta_value * beta_value) ** 0.5


def F1_of_beta(beta: float) -> float:
    beta_value = float(beta)
    eta = eta_of_beta(beta_value)
    return eta**2 + beta_value * beta_value - 1.0


def F2_of_beta(beta: float) -> float:
    beta_value = float(beta)
    eta = eta_of_beta(beta_value)
    return (eta**2 - 1.0) + beta_value * beta_value


def F3_of_beta(beta: float) -> float:
    beta_value = float(beta)
    eta = eta_of_beta(beta_value)
    return eta - (1.0 - beta_value * beta_value) ** 0.5


def F4_of_beta(beta: float) -> float:
    beta_value = float(beta)
    eta = eta_of_beta(beta_value)
    return eta - ((1.0 - beta_value) * (1.0 + beta_value)) ** 0.5


def four_form_float32(beta: float) -> Dict[str, float]:
    s = np.float32
    one = s(1.0)
    two = s(2.0)
    half = s(0.5)
    beta_value = s(beta)
    beta_squared = beta_value * beta_value
    eta = (one - beta_squared) ** half
    factored = (one - beta_value) * (one + beta_value)
    factored_sqrt = factored**half
    return {
        "F1": float(eta**two + beta_squared - one),
        "F2": float((eta**two - one) + beta_squared),
        "F3": float(eta - (one - beta_squared) ** half),
        "F4": float(eta - factored_sqrt),
    }


def four_form_float64(beta: float) -> Dict[str, float]:
    return {
        "F1": F1_of_beta(beta),
        "F2": F2_of_beta(beta),
        "F3": F3_of_beta(beta),
        "F4": F4_of_beta(beta),
    }


def four_form_decimal_oracle(beta: float, precision: int = 50) -> Dict[str, float]:
    from decimal import Decimal, localcontext

    with localcontext() as context:
        context.prec = precision
        one = Decimal(1)
        two = Decimal(2)
        half = one / two
        beta_value = Decimal.from_float(float(beta))
        beta_squared = beta_value * beta_value
        eta = (one - beta_squared) ** half
        factored = (one - beta_value) * (one + beta_value)
        factored_sqrt = factored**half
        return {
            "F1": float(eta**two + beta_squared - one),
            "F2": float((eta**two - one) + beta_squared),
            "F3": float(eta - (one - beta_squared) ** half),
            "F4": float(eta - factored_sqrt),
        }


def sr_four_form_battery() -> dict[str, object]:
    points = []
    nonzero_counts = {form_id: {"float32": 0, "float64": 0, "decimal_50": 0} for form_id in FORM_KEYS}
    for beta_value in beta_grid():
        values32 = four_form_float32(beta_value)
        values64 = four_form_float64(beta_value)
        values_decimal = four_form_decimal_oracle(beta_value, 50)
        for form_id in FORM_KEYS:
            if values32[form_id] != 0.0:
                nonzero_counts[form_id]["float32"] += 1
            if values64[form_id] != 0.0:
                nonzero_counts[form_id]["float64"] += 1
            if values_decimal[form_id] != 0.0:
                nonzero_counts[form_id]["decimal_50"] += 1
        points.append({"beta": beta_value, "float32": values32, "float64": values64, "decimal_50": values_decimal})
    return {
        "campaign": "task027_sr_four_form_battery",
        "beta_count": len(beta_grid()),
        "beta_min": beta_grid()[0],
        "beta_max": beta_grid()[-1],
        "per_form_nonzero": nonzero_counts,
        "points": points,
    }
