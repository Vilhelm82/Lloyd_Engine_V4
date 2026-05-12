from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Callable

import numpy as np

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import four_form_decimal_oracle as schwarzschild_decimal
from .multi_precision_four_form import four_form_float32 as schwarzschild_float32
from .multi_precision_four_form import four_form_float64 as schwarzschild_float64
from .pure_algebraic_four_form import four_form_decimal_oracle as pure_decimal
from .pure_algebraic_four_form import four_form_float32 as pure_float32
from .pure_algebraic_four_form import four_form_float64 as pure_float64
from .sr_four_form import four_form_decimal_oracle as sr_decimal
from .sr_four_form import four_form_float32 as sr_float32
from .sr_four_form import four_form_float64 as sr_float64


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029_path_basis_rank_clustering"
DEFAULT_OUTPUT = REPORT_DIR / "candidate_path_catalog.json"
CATALOG_CSV = REPORT_DIR / "candidate_path_table.csv"
FIXTURES = ("schwarzschild", "sr", "pure_algebraic")
REWRITE_CLASSES = (
    "canonical",
    "sign_reordering",
    "factored_f_routing",
    "difference_of_squares",
    "scaled_identity",
    "distributive_rewrite",
    "compound_routing",
)


@dataclass(frozen=True)
class CandidatePath:
    label: str
    description: str
    fixture: str
    rewrite_class: str


def schwarzschild_candidate_paths() -> tuple[CandidatePath, ...]:
    return _candidate_paths_for_fixture("schwarzschild")


def sr_candidate_paths() -> tuple[CandidatePath, ...]:
    return _candidate_paths_for_fixture("sr")


def pure_algebraic_candidate_paths() -> tuple[CandidatePath, ...]:
    return _candidate_paths_for_fixture("pure_algebraic")


def all_candidate_paths() -> tuple[CandidatePath, ...]:
    return tuple(path for fixture in FIXTURES for path in _candidate_paths_for_fixture(fixture))


def evaluate_path_float32(path: CandidatePath, operand: float) -> float:
    if path.label in ("F1", "F2", "F3", "F4"):
        return _anchor_values(path.fixture, "float32", operand)[path.label]
    return float(_evaluate_np32(path, operand))


def evaluate_path_float64(path: CandidatePath, operand: float) -> float:
    if path.label in ("F1", "F2", "F3", "F4"):
        return _anchor_values(path.fixture, "float64", operand)[path.label]
    return float(_evaluate_py(path, operand))


def evaluate_path_decimal_oracle(path: CandidatePath, operand: float, precision: int = 50) -> float:
    if path.label in ("F1", "F2", "F3", "F4"):
        return _anchor_values(path.fixture, "decimal_50", operand, precision)[path.label]
    return float(_evaluate_decimal(path, operand, precision))


def run_catalog() -> dict[str, object]:
    paths = all_candidate_paths()
    return {
        "campaign": "task029_candidate_path_catalog",
        "fixtures": list(FIXTURES),
        "rewrite_classes": list(REWRITE_CLASSES),
        "path_count": len(paths),
        "paths": [asdict(path) for path in paths],
        "per_fixture_counts": {fixture: len(_candidate_paths_for_fixture(fixture)) for fixture in FIXTURES},
    }


def write_catalog_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_catalog()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(catalog_bytes(payload).decode("utf-8"), encoding="utf-8")
    _write_csv(payload, CATALOG_CSV)
    return payload


def catalog_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_catalog() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_catalog_output(Path(args.output))


def _candidate_paths_for_fixture(fixture: str) -> tuple[CandidatePath, ...]:
    if fixture not in FIXTURES:
        raise ValueError(f"unknown fixture: {fixture}")
    return (
        CandidatePath("F1", "R squared minus direct f", fixture, "canonical"),
        CandidatePath("F2", "R squared minus one plus x term", fixture, "canonical"),
        CandidatePath("F3", "R minus square root of direct f", fixture, "canonical"),
        CandidatePath("F4", "R minus square root of alternate f routing", fixture, "canonical"),
        CandidatePath("P_sign_a", "negative direct f plus R squared", fixture, "sign_reordering"),
        CandidatePath("P_sign_b", "R squared plus negative one plus x term", fixture, "sign_reordering"),
        CandidatePath("P_sign_c", "signed compound subtraction of negative one plus f", fixture, "sign_reordering"),
        CandidatePath("P_factor_b", "R minus square root of second alternate f routing", fixture, "factored_f_routing"),
        CandidatePath("P_diff_squares", "product of conjugate root difference and root sum", fixture, "difference_of_squares"),
        CandidatePath("P_scaled_2", "twice R squared minus twice direct f", fixture, "scaled_identity"),
        CandidatePath("P_scaled_half", "half R squared minus half direct f", fixture, "scaled_identity"),
        CandidatePath("P_distrib_mul", "explicit R times R minus direct f", fixture, "distributive_rewrite"),
        CandidatePath("P_distrib_sqrt_mul", "R squared minus product of two direct square roots", fixture, "distributive_rewrite"),
        CandidatePath("P_compound_split", "R squared minus one plus one minus direct f", fixture, "compound_routing"),
        CandidatePath("P_compound_zero", "R squared minus direct f plus neutral add", fixture, "compound_routing"),
    )


def _anchor_values(fixture: str, precision: str, operand: float, decimal_precision: int = 50) -> dict[str, float]:
    if fixture == "schwarzschild":
        if precision == "float32":
            return schwarzschild_float32(operand)
        if precision == "float64":
            return schwarzschild_float64(operand)
        return schwarzschild_decimal(operand, decimal_precision)
    if fixture == "sr":
        if precision == "float32":
            return sr_float32(operand)
        if precision == "float64":
            return sr_float64(operand)
        return sr_decimal(operand, decimal_precision)
    if fixture == "pure_algebraic":
        if precision == "float32":
            return pure_float32(operand)
        if precision == "float64":
            return pure_float64(operand)
        return pure_decimal(operand, decimal_precision)
    raise ValueError(f"unknown fixture: {fixture}")


def _evaluate_py(path: CandidatePath, operand: float) -> float:
    one = 1.0
    two = 2.0
    half = 0.5
    zero = 0.0
    values = _fixture_py_values(path.fixture, operand)
    return _evaluate_from_values(path.label, values, one, two, half, zero, lambda value: value**half)


def _evaluate_np32(path: CandidatePath, operand: float) -> np.float32:
    s = np.float32
    one = s(1.0)
    two = s(2.0)
    half = s(0.5)
    zero = s(0.0)
    values = _fixture_np32_values(path.fixture, operand)
    return _evaluate_from_values(path.label, values, one, two, half, zero, lambda value: value**half)


def _evaluate_decimal(path: CandidatePath, operand: float, precision: int) -> Decimal:
    with localcontext() as context:
        context.prec = precision
        one = Decimal(1)
        two = Decimal(2)
        half = one / two
        zero = Decimal(0)
        values = _fixture_decimal_values(path.fixture, operand)
        return _evaluate_from_values(path.label, values, one, two, half, zero, lambda value: value**half)


def _evaluate_from_values(label: str, values: dict[str, object], one, two, half, zero, root_fn: Callable[[object], object]):
    root = values["root"]
    direct = values["direct"]
    x_term = values["x_term"]
    if label == "P_sign_a":
        return (-direct) + root**two
    if label == "P_sign_b":
        return root**two + (-one) + x_term
    if label == "P_sign_c":
        return (root**two - one) - (-one + direct)
    if label == "P_factor_b":
        return root - root_fn(values["second_alt"])
    if label == "P_diff_squares":
        direct_root = root_fn(direct)
        return (root - direct_root) * (root + direct_root)
    if label == "P_scaled_2":
        return two * root**two - two * direct
    if label == "P_scaled_half":
        return half * root**two - half * direct
    if label == "P_distrib_mul":
        return root * root - direct
    if label == "P_distrib_sqrt_mul":
        return root**two - root_fn(direct) * root_fn(direct)
    if label == "P_compound_split":
        return (root**two - one) + (one - direct)
    if label == "P_compound_zero":
        return root**two - (direct + zero)
    raise ValueError(f"unknown candidate label: {label}")


def _fixture_py_values(fixture: str, operand: float) -> dict[str, float]:
    value = float(operand)
    if fixture == "schwarzschild":
        two_over = 2.0 / value
        direct = 1.0 - two_over
        return {"direct": direct, "x_term": two_over, "root": direct**0.5, "second_alt": 1.0 - two_over}
    if fixture == "sr":
        squared = value * value
        direct = 1.0 - squared
        return {"direct": direct, "x_term": squared, "root": direct**0.5, "second_alt": 1.0 - value * value}
    if fixture == "pure_algebraic":
        direct = 1.0 - value
        return {"direct": direct, "x_term": value, "root": direct**0.5, "second_alt": 1.0 - value * 1.0}
    raise ValueError(f"unknown fixture: {fixture}")


def _fixture_np32_values(fixture: str, operand: float) -> dict[str, np.float32]:
    s = np.float32
    one = s(1.0)
    two = s(2.0)
    value = s(operand)
    if fixture == "schwarzschild":
        x_term = two / value
        direct = one - x_term
        return {"direct": direct, "x_term": x_term, "root": direct**s(0.5), "second_alt": one - x_term}
    if fixture == "sr":
        squared = value * value
        direct = one - squared
        return {"direct": direct, "x_term": squared, "root": direct**s(0.5), "second_alt": one - value * value}
    if fixture == "pure_algebraic":
        direct = one - value
        return {"direct": direct, "x_term": value, "root": direct**s(0.5), "second_alt": one - value * s(1.0)}
    raise ValueError(f"unknown fixture: {fixture}")


def _fixture_decimal_values(fixture: str, operand: float) -> dict[str, Decimal]:
    one = Decimal(1)
    two = Decimal(2)
    value = Decimal.from_float(float(operand))
    if fixture == "schwarzschild":
        x_term = two / value
        direct = one - x_term
        return {"direct": direct, "x_term": x_term, "root": direct ** (one / two), "second_alt": one - x_term}
    if fixture == "sr":
        squared = value * value
        direct = one - squared
        return {"direct": direct, "x_term": squared, "root": direct ** (one / two), "second_alt": one - value * value}
    if fixture == "pure_algebraic":
        direct = one - value
        return {"direct": direct, "x_term": value, "root": direct ** (one / two), "second_alt": one - value * one}
    raise ValueError(f"unknown fixture: {fixture}")


def _write_csv(payload: dict[str, object], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", "label", "rewrite_class", "description"))
        for item in payload["paths"]:
            writer.writerow((item["fixture"], item["label"], item["rewrite_class"], item["description"]))


if __name__ == "__main__":
    main()
