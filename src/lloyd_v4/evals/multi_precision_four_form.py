from __future__ import annotations

import struct
from typing import Dict

import numpy as np

from .schwarzschild_four_form import F1_of_r, F2_of_r, F3_of_r, F4_of_r, R_of_r, f_of_r


FORM_KEYS = ("F1", "F2", "F3", "F4")
FLOAT32_TO_FLOAT64_UNIT_RATIO = pow(2.0, 29)


def four_form_float32(r: float) -> Dict[str, float]:
    s = np.float32
    one = s(1.0)
    two = s(2.0)
    half = s(0.5)
    r_value = s(r)

    f_value = one - two / r_value
    r_value_sqrt = f_value**half
    factored = (r_value - two) / r_value
    factored_sqrt = factored**half
    return {
        "F1": float(r_value_sqrt**s(2.0) - (one - two / r_value)),
        "F2": float(r_value_sqrt**s(2.0) - one + two / r_value),
        "F3": float(r_value_sqrt - (one - two / r_value) ** half),
        "F4": float(r_value_sqrt - factored_sqrt),
    }


def four_form_float64(r: float) -> Dict[str, float]:
    return {
        "F1": F1_of_r(r),
        "F2": F2_of_r(r),
        "F3": F3_of_r(r),
        "F4": F4_of_r(r),
    }


def four_form_decimal_oracle(r: float, precision: int = 50) -> Dict[str, float]:
    from decimal import Decimal, localcontext

    with localcontext() as context:
        context.prec = precision
        one = Decimal(1)
        two = Decimal(2)
        half = one / two
        r_value = Decimal.from_float(float(r))

        f_value = one - two / r_value
        r_value_sqrt = f_value**half
        factored = (r_value - two) / r_value
        factored_sqrt = factored**half
        return {
            "F1": float(r_value_sqrt**two - (one - two / r_value)),
            "F2": float(r_value_sqrt**two - one + two / r_value),
            "F3": float(r_value_sqrt - (one - two / r_value) ** half),
            "F4": float(r_value_sqrt - factored_sqrt),
        }


def ulp_of_double(x: float) -> float:
    absolute = abs(float(x))
    if absolute != absolute:
        return absolute
    if absolute == float("inf"):
        return absolute
    if absolute == 0.0:
        return _float_from_bits(1)
    bits = _bits_from_float(absolute)
    return _float_from_bits(bits + 1) - absolute


def predicted_chain_envelope(r: float, n_ops: int = 7) -> float:
    f_value = f_of_r(r)
    r_value = float(r)
    factored = (r_value - 2.0) / r_value
    intermediates = (
        f_value,
        R_of_r(r),
        factored,
        factored**0.5,
        F4_of_r(r),
    )
    chain_unit = max(ulp_of_double(value) for value in intermediates)
    return float(n_ops) * 0.5 * chain_unit


def _bits_from_float(value: float) -> int:
    return struct.unpack(">Q", struct.pack(">d", value))[0]


def _float_from_bits(bits: int) -> float:
    return struct.unpack(">d", struct.pack(">Q", bits))[0]
