from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
from typing import Callable

import numpy as np


DECIMAL_EMULATED_UNSUPPORTED_MESSAGE = (
    "c6_decimal_emulated only supports binary output precisions (intermediate is always Decimal-100)"
)

CANDIDATE_IDS = (
    "c1_reference",
    "c2_reassociated",
    "c3_factored",
    "c4_power_operator",
    "c5_identity_padded",
    "c6_decimal_emulated",
)


@dataclass(frozen=True)
class PrecisionSpec:
    label: str
    dtype: object
    is_binary: bool


@dataclass(frozen=True)
class RewriteCandidate:
    candidate_id: str
    expression: str
    tested_property: str
    expected_burden_relation_to_reference: str
    operation_chain_depth: int
    evaluator: Callable[[float, PrecisionSpec], float]

    def evaluate(self, x_value: float, precision_spec: PrecisionSpec) -> float:
        return self.evaluator(x_value, precision_spec)

    def metadata(self) -> dict[str, object]:
        return {
            "calibration_status": "non_calibration",
            "candidate_id": self.candidate_id,
            "declared_algebraic_identity": "pure_algebraic_zero_constraint",
            "domain_stratum_label": "canonical_137_point_domain",
            "expected_burden_relation_to_reference": self.expected_burden_relation_to_reference,
            "expression": self.expression,
            "fixture_name": "pure_algebraic",
            "operand_grid_label": "pure_algebraic_x_grid_137",
            "operation_chain_depth": self.operation_chain_depth,
            "path_name": self.candidate_id,
            "tested_property": self.tested_property,
        }


def precision_spec(precision_label: str) -> PrecisionSpec:
    if precision_label == "float32":
        return PrecisionSpec(label=precision_label, dtype=np.float32, is_binary=True)
    if precision_label == "float64":
        return PrecisionSpec(label=precision_label, dtype=float, is_binary=True)
    if precision_label == "float128":
        return PrecisionSpec(label=precision_label, dtype=np.float128, is_binary=True)
    if precision_label.startswith("decimal_"):
        return PrecisionSpec(label=precision_label, dtype=Decimal, is_binary=False)
    raise ValueError(f"unknown precision label: {precision_label}")


def all_candidates() -> tuple[RewriteCandidate, ...]:
    return tuple(candidate_by_id(candidate_id) for candidate_id in CANDIDATE_IDS)


def candidate_by_id(candidate_id: str) -> RewriteCandidate:
    candidates = {
        "c1_reference": RewriteCandidate(
            candidate_id="c1_reference",
            expression="(R * R) - 1.0 + x",
            tested_property="Sterbenz-blessed explicit subtraction",
            expected_burden_relation_to_reference="reference",
            operation_chain_depth=2,
            evaluator=_c1_reference,
        ),
        "c2_reassociated": RewriteCandidate(
            candidate_id="c2_reassociated",
            expression="(R * R) + (x - 1.0)",
            tested_property="Reassociation that swaps the protected subtraction region",
            expected_burden_relation_to_reference="predicted_worse",
            operation_chain_depth=2,
            evaluator=_c2_reassociated,
        ),
        "c3_factored": RewriteCandidate(
            candidate_id="c3_factored",
            expression="(R - 1.0) * (R + 1.0) + x",
            tested_property="Deliberate cancellation control",
            expected_burden_relation_to_reference="predicted_worse",
            operation_chain_depth=4,
            evaluator=_c3_factored,
        ),
        "c4_power_operator": RewriteCandidate(
            candidate_id="c4_power_operator",
            expression="(R ** 2) - 1.0 + x",
            tested_property="Operator shift from multiplication syntax to power syntax",
            expected_burden_relation_to_reference="predicted_tied",
            operation_chain_depth=2,
            evaluator=_c4_power_operator,
        ),
        "c5_identity_padded": RewriteCandidate(
            candidate_id="c5_identity_padded",
            expression="((R * R) - 1.0) / 1.0 + x",
            tested_property="Identity padding with value preservation",
            expected_burden_relation_to_reference="predicted_worse",
            operation_chain_depth=3,
            evaluator=_c5_identity_padded,
        ),
        "c6_decimal_emulated": RewriteCandidate(
            candidate_id="c6_decimal_emulated",
            expression="float(Decimal(R) * Decimal(R) - Decimal(1)) + x",
            tested_property="Decimal-100 intermediate before binary final addition",
            expected_burden_relation_to_reference="genuine_uncertainty",
            operation_chain_depth=3,
            evaluator=_c6_decimal_emulated,
        ),
    }
    try:
        return candidates[candidate_id]
    except KeyError as exc:
        raise ValueError(f"unknown candidate: {candidate_id}") from exc


def candidate_value(candidate_id: str, x_value: float, precision_label: str = "float64") -> float:
    return candidate_by_id(candidate_id).evaluate(x_value, precision_spec(precision_label))


def _core_terms(x_value: float, precision: PrecisionSpec) -> tuple[object, object, object]:
    if precision.dtype is float:
        x_local = float(x_value)
        one = 1.0
        root = (one - x_local) ** 0.5
        return x_local, one, root
    s = precision.dtype
    x_local = s(x_value)
    one = s(1.0)
    root = np.sqrt(one - x_local)
    return x_local, one, root


def _to_output(value: object, precision: PrecisionSpec) -> float:
    if precision.dtype is float:
        return float(value)
    return float(precision.dtype(value))


def _c1_reference(x_value: float, precision: PrecisionSpec) -> float:
    x_local, one, root = _core_terms(x_value, precision)
    return _to_output((root * root) - one + x_local, precision)


def _c2_reassociated(x_value: float, precision: PrecisionSpec) -> float:
    x_local, one, root = _core_terms(x_value, precision)
    return _to_output((root * root) + (x_local - one), precision)


def _c3_factored(x_value: float, precision: PrecisionSpec) -> float:
    x_local, one, root = _core_terms(x_value, precision)
    return _to_output((root - one) * (root + one) + x_local, precision)


def _c4_power_operator(x_value: float, precision: PrecisionSpec) -> float:
    x_local, one, root = _core_terms(x_value, precision)
    return _to_output((root**2) - one + x_local, precision)


def _c5_identity_padded(x_value: float, precision: PrecisionSpec) -> float:
    x_local, one, root = _core_terms(x_value, precision)
    return _to_output(((root * root) - one) / one + x_local, precision)


def _c6_decimal_emulated(x_value: float, precision: PrecisionSpec) -> float:
    if not precision.is_binary:
        raise NotImplementedError(DECIMAL_EMULATED_UNSUPPORTED_MESSAGE)
    x_local, one, root = _core_terms(x_value, precision)
    with localcontext() as context:
        context.prec = 100
        intermediate = Decimal.from_float(float(root)) * Decimal.from_float(float(root)) - Decimal(1)
    if precision.dtype is float:
        rounded_mid = float(intermediate)
        return float(rounded_mid + float(x_local))
    rounded_mid = precision.dtype(str(intermediate))
    return float(rounded_mid + precision.dtype(x_local))
