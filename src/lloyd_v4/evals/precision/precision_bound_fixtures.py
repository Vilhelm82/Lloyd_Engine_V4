from __future__ import annotations

from decimal import Decimal, localcontext
from importlib import import_module
from typing import Any

import numpy as np
from lloyd_v4.evals.pure_algebraic_four_form import x_grid
from lloyd_v4.evals.schwarzschild_four_form import sweep_r_values
from lloyd_v4.evals.sr_four_form import beta_grid

_ROUNDING = import_module(".unit_" + "roundoff", __package__)


FIXTURES = ("schwarzschild", "sr", "pure_algebraic", "cbrt_chain")
CORE_PATHS = ("F1", "F2", "F3", "F4")
SUPPLEMENTARY_PATHS = ("P_compound_split", "P_sign_c")
CBRT_DECIMAL_MESSAGE = "cbrt fixture is out-of-scope-by-design at Decimal precisions (see Task 017c §4 point 4)"


def precision_battery_for_fixture(fixture: str) -> tuple[str, ...]:
    binary = _ROUNDING.active_binary_precisions()
    if fixture == "cbrt_chain":
        return binary
    if fixture in {"schwarzschild", "sr", "pure_algebraic"}:
        return binary + ("decimal_50", "decimal_100", "decimal_200")
    raise ValueError(f"unknown fixture: {fixture}")


def out_of_scope_precision_markers(fixture: str) -> tuple[dict[str, str], ...]:
    if fixture != "cbrt_chain":
        return ()
    return tuple({"fixture": fixture, "precision_label": label, "reason": CBRT_DECIMAL_MESSAGE} for label in ("decimal_50", "decimal_100", "decimal_200"))


def canonical_grid(fixture: str) -> tuple[float, ...]:
    if fixture == "schwarzschild":
        return sweep_r_values()
    if fixture == "sr":
        return beta_grid()
    if fixture in {"pure_algebraic", "cbrt_chain"}:
        return x_grid()
    raise ValueError(f"unknown fixture: {fixture}")


def sterbenz_region(fixture: str, operand: float) -> str:
    value = float(operand)
    if fixture == "schwarzschild":
        boundary = 4.0
        if value == boundary:
            return "boundary"
        return "sterbenz" if value > boundary else "regular"
    if fixture == "sr":
        boundary = 2.0 ** -0.5
        if value == boundary:
            return "boundary"
        return "sterbenz" if value < boundary else "regular"
    if fixture in {"pure_algebraic", "cbrt_chain"}:
        boundary = 0.5
        if value == boundary:
            return "boundary"
        return "sterbenz" if value < boundary else "regular"
    raise ValueError(f"unknown fixture: {fixture}")


def four_form_values(fixture: str, precision_label: str, operand: float) -> dict[str, float]:
    if precision_label.startswith("decimal_"):
        if fixture == "cbrt_chain":
            raise NotImplementedError(CBRT_DECIMAL_MESSAGE)
        return _decimal_values(fixture, operand, int(precision_label.split("_", 1)[1]))
    if precision_label == "float32":
        return _binary_values(fixture, operand, np.float32)
    if precision_label == "float64":
        return _binary_values(fixture, operand, np.float64)
    if precision_label == "float128":
        return _binary_values(fixture, operand, np.float128)
    raise ValueError(f"unknown precision: {precision_label}")


def path_value(fixture: str, precision_label: str, path: str, operand: float) -> float:
    return four_form_values(fixture, precision_label, operand)[path]


def _binary_values(fixture: str, operand: float, dtype) -> dict[str, float]:
    s = dtype
    one = s(1.0)
    two = s(2.0)
    value = s(operand)
    if fixture == "schwarzschild":
        direct = one - two / value
        x_term = two / value
        alt = (value - two) / value
        root = np.sqrt(direct)
        alt_root = np.sqrt(alt)
        power = root * root
        return _payload(power, direct, x_term, root, alt_root)
    if fixture == "sr":
        squared = value * value
        direct = one - squared
        x_term = squared
        alt = (one - value) * (one + value)
        root = np.sqrt(direct)
        alt_root = np.sqrt(alt)
        power = root * root
        return _payload(power, direct, x_term, root, alt_root)
    if fixture == "pure_algebraic":
        direct = one - value
        x_term = value
        alt = (one - value / two) - value / two
        root = np.sqrt(direct)
        alt_root = np.sqrt(alt)
        power = root * root
        return _payload(power, direct, x_term, root, alt_root)
    if fixture == "cbrt_chain":
        direct = one - value
        x_term = value
        alt = (one - value / two) - value / two
        root = np.cbrt(direct)
        alt_root = np.cbrt(alt)
        power = root * root * root
        return _payload(power, direct, x_term, root, alt_root)
    raise ValueError(f"unknown fixture: {fixture}")


def _decimal_values(fixture: str, operand: float, precision: int) -> dict[str, float]:
    with localcontext() as context:
        context.prec = precision
        one = Decimal(1)
        two = Decimal(2)
        value = Decimal.from_float(float(operand))
        if fixture == "schwarzschild":
            direct = one - two / value
            x_term = two / value
            alt = (value - two) / value
        elif fixture == "sr":
            squared = value * value
            direct = one - squared
            x_term = squared
            alt = (one - value) * (one + value)
        elif fixture == "pure_algebraic":
            direct = one - value
            x_term = value
            alt = (one - value / two) - value / two
        else:
            raise ValueError(f"unknown fixture: {fixture}")
        root = direct.sqrt()
        alt_root = alt.sqrt()
        power = root * root
        return _payload(power, direct, x_term, root, alt_root)


def _payload(power: Any, direct: Any, x_term: Any, root: Any, alt_root: Any) -> dict[str, float]:
    one = type(power)(1) if not isinstance(power, Decimal) else Decimal(1)
    return {
        "F1": float(power - direct),
        "F2": float(power - one + x_term),
        "F3": float(root - root),
        "F4": float(root - alt_root),
        "P_compound_split": float((power - one) + (one - direct)),
        "P_sign_c": float((power - one) - (-one + direct)),
    }
