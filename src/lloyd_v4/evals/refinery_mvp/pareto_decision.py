from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .burden_vector import BurdenVector, SENTINELS


UNAVAILABLE_VALUES = frozenset(SENTINELS.values())
LATTICE_RANK = {"integer_lattice": 0, "non_integer_lattice": 1, "unclassified": 2}


@dataclass(frozen=True)
class BurdenPolicy:
    dimension: str
    direction: str
    required: bool


@dataclass(frozen=True)
class ParetoComparisonResult:
    outcome: str
    per_dimension: dict[str, dict[str, object]]

    def to_json_safe(self) -> dict[str, object]:
        return {
            "outcome": self.outcome,
            "per_dimension": self.per_dimension,
        }


DEFAULT_BURDEN_POLICY = (
    BurdenPolicy("b_k_point_estimate", "lower_with_ci", True),
    BurdenPolicy("lattice_class", "lower_lattice_rank", True),
    BurdenPolicy("max_integer_residual", "lower", True),
    BurdenPolicy("polarity_class", "paired_equal", True),
    BurdenPolicy("calibration_zero_preserved", "equal_required", True),
    BurdenPolicy("operation_chain_depth", "lower", True),
)


def compare_burden_vectors(
    reference: BurdenVector,
    candidate: BurdenVector,
    burden_policy: Sequence[BurdenPolicy] = DEFAULT_BURDEN_POLICY,
) -> ParetoComparisonResult:
    per_dimension: dict[str, dict[str, object]] = {}
    candidate_better = 0
    reference_better = 0
    has_blocking_dimension = False

    for policy in burden_policy:
        row = _compare_dimension(policy, reference, candidate)
        per_dimension[policy.dimension] = row
        if policy.required and row["status"] in {"unavailable", "mismatch"}:
            has_blocking_dimension = True
        if row["status"] == "candidate_better":
            candidate_better += 1
        if row["status"] == "reference_better":
            reference_better += 1

    if has_blocking_dimension:
        outcome = "comparison_indeterminate"
    elif candidate_better > 0 and reference_better == 0:
        outcome = "accepted"
    elif reference_better > 0 and candidate_better == 0:
        outcome = "rejected"
    elif candidate_better == 0 and reference_better == 0:
        outcome = "forms_structurally_tied"
    else:
        outcome = "comparison_indeterminate"

    return ParetoComparisonResult(outcome=outcome, per_dimension=per_dimension)


def _compare_dimension(policy: BurdenPolicy, reference: BurdenVector, candidate: BurdenVector) -> dict[str, object]:
    if policy.direction == "lower_with_ci":
        return _compare_b_k(reference, candidate)
    reference_value = getattr(reference, policy.dimension)
    candidate_value = getattr(candidate, policy.dimension)
    if _unavailable(reference_value) or _unavailable(candidate_value):
        return _row(policy, reference_value, candidate_value, "unavailable", "required_data_unavailable")
    if policy.direction == "lower":
        if candidate_value < reference_value:
            return _row(policy, reference_value, candidate_value, "candidate_better", "candidate_value_lower")
        if reference_value < candidate_value:
            return _row(policy, reference_value, candidate_value, "reference_better", "reference_value_lower")
        return _row(policy, reference_value, candidate_value, "tied", "equal_values")
    if policy.direction == "lower_lattice_rank":
        reference_rank = LATTICE_RANK.get(str(reference_value))
        candidate_rank = LATTICE_RANK.get(str(candidate_value))
        if reference_rank is None or candidate_rank is None:
            return _row(policy, reference_value, candidate_value, "unavailable", "lattice_rank_unavailable")
        if candidate_rank < reference_rank:
            return _row(policy, reference_value, candidate_value, "candidate_better", "candidate_lattice_rank_lower")
        if reference_rank < candidate_rank:
            return _row(policy, reference_value, candidate_value, "reference_better", "reference_lattice_rank_lower")
        return _row(policy, reference_value, candidate_value, "tied", "equal_lattice_rank")
    if policy.direction in {"paired_equal", "equal_required"}:
        if candidate_value == reference_value:
            return _row(policy, reference_value, candidate_value, "tied", "required_values_match")
        return _row(policy, reference_value, candidate_value, "mismatch", "required_values_differ")
    return _row(policy, reference_value, candidate_value, "unavailable", "policy_direction_unavailable")


def _compare_b_k(reference: BurdenVector, candidate: BurdenVector) -> dict[str, object]:
    policy = DEFAULT_BURDEN_POLICY[0]
    values = (
        reference.b_k_point_estimate,
        reference.b_k_ci_lower,
        reference.b_k_ci_upper,
        candidate.b_k_point_estimate,
        candidate.b_k_ci_lower,
        candidate.b_k_ci_upper,
    )
    if any(_unavailable(value) for value in values):
        return _row(policy, reference.b_k_point_estimate, candidate.b_k_point_estimate, "unavailable", "required_data_unavailable")
    if _intervals_overlap(reference.b_k_ci_lower, reference.b_k_ci_upper, candidate.b_k_ci_lower, candidate.b_k_ci_upper):
        return _row(policy, reference.b_k_point_estimate, candidate.b_k_point_estimate, "tied", "confidence_intervals_overlap")
    if candidate.b_k_ci_upper < reference.b_k_ci_lower:
        return _row(policy, reference.b_k_point_estimate, candidate.b_k_point_estimate, "candidate_better", "candidate_ci_below_reference_ci")
    if reference.b_k_ci_upper < candidate.b_k_ci_lower:
        return _row(policy, reference.b_k_point_estimate, candidate.b_k_point_estimate, "reference_better", "reference_ci_below_candidate_ci")
    return _row(policy, reference.b_k_point_estimate, candidate.b_k_point_estimate, "tied", "confidence_intervals_touch")


def _intervals_overlap(reference_lower: float, reference_upper: float, candidate_lower: float, candidate_upper: float) -> bool:
    return candidate_lower <= reference_upper and reference_lower <= candidate_upper


def _row(
    policy: BurdenPolicy,
    reference_value: object,
    candidate_value: object,
    status: str,
    reason: str,
) -> dict[str, object]:
    return {
        "candidate_value": candidate_value,
        "direction": policy.direction,
        "reason": reason,
        "reference_value": reference_value,
        "required": policy.required,
        "status": status,
    }


def _unavailable(value: object) -> bool:
    return isinstance(value, str) and value in UNAVAILABLE_VALUES
