from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class LinearFit:
    intercept: float
    slope: float
    r_squared: float
    residuals: tuple[float, ...]

    def to_json_safe(self) -> dict[str, object]:
        return {
            "a_k": self.intercept,
            "b_k": self.slope,
            "r_squared": self.r_squared,
            "residuals": list(self.residuals),
        }


def fit_linear(x_values: Iterable[float], y_values: Iterable[float]) -> LinearFit:
    x = np.asarray(tuple(float(value) for value in x_values), dtype=float)
    y = np.asarray(tuple(float(value) for value in y_values), dtype=float)
    if len(x) != len(y):
        raise ValueError("x and y lengths must match")
    if len(x) < 2:
        raise ValueError("at least two observations are required")
    design = np.column_stack((np.ones(len(x)), x))
    coeffs, *_ = np.linalg.lstsq(design, y, rcond=None)
    predicted = design @ coeffs
    residuals = y - predicted
    total = y - float(np.mean(y))
    ss_total = float(np.dot(total, total))
    ss_residual = float(np.dot(residuals, residuals))
    r_squared = 1.0 if ss_total == 0.0 and ss_residual == 0.0 else 0.0 if ss_total == 0.0 else 1.0 - ss_residual / ss_total
    return LinearFit(
        intercept=float(coeffs[0]),
        slope=float(coeffs[1]),
        r_squared=float(r_squared),
        residuals=tuple(float(value) for value in residuals),
    )


def bootstrap_ci(
    x_values: Iterable[float],
    y_values: Iterable[float],
    *,
    seed_material: str,
    n_resamples: int = 200,
) -> dict[str, tuple[float, float]]:
    x = tuple(float(value) for value in x_values)
    y = tuple(float(value) for value in y_values)
    if len(x) != len(y):
        raise ValueError("x and y lengths must match")
    if len(x) < 2:
        raise ValueError("at least two observations are required")
    rng = random.Random(_seed(seed_material))
    intercepts = []
    slopes = []
    for _ in range(n_resamples):
        indices = tuple(rng.randrange(len(x)) for _ in x)
        sample_x = tuple(x[index] for index in indices)
        sample_y = tuple(y[index] for index in indices)
        if len(set(sample_x)) < 2:
            continue
        fit = fit_linear(sample_x, sample_y)
        intercepts.append(fit.intercept)
        slopes.append(fit.slope)
    if not intercepts:
        fit = fit_linear(x, y)
        intercepts = [fit.intercept]
        slopes = [fit.slope]
    return {
        "a_k": _percentile_interval(tuple(intercepts)),
        "b_k": _percentile_interval(tuple(slopes)),
    }


def interval_includes_zero(interval: tuple[float, float]) -> bool:
    return interval[0] <= 0.0 <= interval[1]


def intervals_overlap(left: tuple[float, float], right: tuple[float, float]) -> bool:
    return max(left[0], right[0]) <= min(left[1], right[1])


def _percentile_interval(values: tuple[float, ...]) -> tuple[float, float]:
    ordered = tuple(sorted(values))
    if len(ordered) == 1:
        return ordered[0], ordered[0]
    low_index = int(0.025 * (len(ordered) - 1))
    high_index = int(0.975 * (len(ordered) - 1))
    return float(ordered[low_index]), float(ordered[high_index])


def _seed(seed_material: str) -> int:
    digest = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)
