from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from lloyd_v4.evals.refinery_mvp.burden_vector import BurdenVector
from lloyd_v4.evals.refinery_mvp.pareto_decision import DEFAULT_BURDEN_POLICY, BurdenPolicy, compare_burden_vectors


@dataclass(frozen=True)
class ParetoFrontierResult:
    frontier_members: list[str]
    pairwise_dominance: dict[str, dict[str, dict[str, object]]]
    dominated_candidates: dict[str, list[str]]
    incomparable_pairs: list[list[str]]

    def to_json_safe(self) -> dict[str, object]:
        return {
            "dominated_candidates": self.dominated_candidates,
            "frontier_members": self.frontier_members,
            "incomparable_pairs": self.incomparable_pairs,
            "pairwise_dominance": self.pairwise_dominance,
        }


def compute_pareto_frontier(
    burden_vectors: Sequence[BurdenVector] | dict[str, BurdenVector],
    burden_policy: Sequence[BurdenPolicy] = DEFAULT_BURDEN_POLICY,
) -> ParetoFrontierResult:
    vectors = list(burden_vectors.values()) if isinstance(burden_vectors, dict) else list(burden_vectors)
    by_id = {vector.path_name: vector for vector in vectors}
    pairwise: dict[str, dict[str, dict[str, object]]] = {candidate_id: {} for candidate_id in by_id}
    dominators: dict[str, list[str]] = {candidate_id: [] for candidate_id in by_id}
    incomparable_pairs: list[list[str]] = []

    for left_id, left in by_id.items():
        for right_id, right in by_id.items():
            if left_id == right_id:
                pairwise[left_id][right_id] = {"outcome": "forms_structurally_tied", "interpretation": "self"}
                continue
            result = compare_burden_vectors(left, right, burden_policy)
            interpretation = _interpret_pair(result.outcome)
            pairwise[left_id][right_id] = {
                "outcome": result.outcome,
                "interpretation": interpretation,
                "per_dimension": result.per_dimension,
            }
            if result.outcome == "accepted":
                dominators[left_id].append(right_id)

    candidate_ids = list(by_id)
    for index, left_id in enumerate(candidate_ids):
        for right_id in candidate_ids[index + 1 :]:
            left_outcome = pairwise[left_id][right_id]["outcome"]
            right_outcome = pairwise[right_id][left_id]["outcome"]
            if left_outcome == "comparison_indeterminate" and right_outcome == "comparison_indeterminate":
                incomparable_pairs.append([left_id, right_id])

    dominated = {candidate_id: sorted(values) for candidate_id, values in dominators.items() if values}
    frontier = [candidate_id for candidate_id in candidate_ids if candidate_id not in dominated]
    return ParetoFrontierResult(
        frontier_members=frontier,
        pairwise_dominance=pairwise,
        dominated_candidates=dominated,
        incomparable_pairs=incomparable_pairs,
    )


def _interpret_pair(outcome: str) -> str:
    if outcome == "accepted":
        return "right_dominates_left"
    if outcome == "rejected":
        return "left_dominates_right"
    if outcome == "forms_structurally_tied":
        return "tied"
    return "incomparable"
