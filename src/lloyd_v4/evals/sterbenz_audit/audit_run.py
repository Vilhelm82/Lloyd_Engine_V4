from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.evals.refinery_mvp.geometry_admissibility import check_geometry_admissibility

from .measurement_extension import (
    FULL_GRID_LABEL,
    REGION_LABELS,
    STERBENZ_REGION_LABEL,
    burden_vectors_bytes,
    burden_vectors_for_region,
    measurement_bytes,
    run_measurement_extension,
)
from .n_way_pareto import ParetoFrontierResult, compute_pareto_frontier
from .rewrite_candidates import CANDIDATE_IDS, all_candidates, candidate_by_id


ROOT = Path(__file__).resolve().parents[4]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task031_sterbenz_audit"
PRE_REGISTRATION_COMMIT = "4c97759"


@dataclass(frozen=True)
class SterbenzAuditResult:
    admissibility: dict[str, object]
    frontier: ParetoFrontierResult
    full_grid_burden_vectors: dict[str, object]
    headline_classification: str
    measurement_aggregate: dict[str, object]
    region_comparison: dict[str, object]
    sterbenz_region_burden_vectors: dict[str, object]

    def to_json_safe(self) -> dict[str, object]:
        return {
            "admissibility": self.admissibility,
            "frontier": self.frontier,
            "full_grid_burden_vectors": self.full_grid_burden_vectors,
            "headline_classification": self.headline_classification,
            "measurement_aggregate": self.measurement_aggregate,
            "pre_registration_commit": PRE_REGISTRATION_COMMIT,
            "region_comparison": self.region_comparison,
            "sterbenz_region_burden_vectors": self.sterbenz_region_burden_vectors,
            "task": "task031_sterbenz_audit",
        }


def run_sterbenz_audit(
    fixture_name: str = "pure_algebraic",
    region_predicate: str = STERBENZ_REGION_LABEL,
    candidate_ids: tuple[str, ...] = CANDIDATE_IDS,
) -> SterbenzAuditResult:
    if fixture_name != "pure_algebraic":
        raise ValueError("task031 only supports pure_algebraic")
    if region_predicate != STERBENZ_REGION_LABEL:
        raise ValueError("task031 headline only supports sterbenz_region")
    measurement = run_measurement_extension()
    sterbenz_vectors = burden_vectors_for_region(STERBENZ_REGION_LABEL, measurement)
    full_vectors = burden_vectors_for_region(FULL_GRID_LABEL, measurement)
    selected_vectors = {candidate_id: sterbenz_vectors[candidate_id] for candidate_id in candidate_ids}
    frontier = compute_pareto_frontier(selected_vectors)
    headline = _headline(frontier, selected_vectors)
    return SterbenzAuditResult(
        admissibility=_admissibility_records(candidate_ids),
        frontier=frontier,
        full_grid_burden_vectors=full_vectors,
        headline_classification=headline,
        measurement_aggregate=measurement,
        region_comparison=_region_comparison(measurement),
        sterbenz_region_burden_vectors=sterbenz_vectors,
    )


def write_audit_outputs(output_dir: str | Path = REPORT_DIR) -> SterbenzAuditResult:
    result = run_sterbenz_audit()
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "measurement_aggregate.json").write_bytes(measurement_bytes(result.measurement_aggregate))
    (target / "sterbenz_region_burden_vectors.json").write_bytes(burden_vectors_bytes(STERBENZ_REGION_LABEL, result.measurement_aggregate))
    (target / "full_grid_burden_vectors.json").write_bytes(burden_vectors_bytes(FULL_GRID_LABEL, result.measurement_aggregate))
    (target / "pareto_frontier.json").write_bytes(pareto_frontier_bytes(result))
    (target / "headline_classification.md").write_bytes(headline_bytes(result))
    return result


def pareto_frontier_bytes(result: SterbenzAuditResult | None = None) -> bytes:
    data = run_sterbenz_audit() if result is None else result
    return _stable_json_bytes(
        {
            "frontier": data.frontier,
            "headline_classification": data.headline_classification,
            "region": STERBENZ_REGION_LABEL,
            "task": "task031_sterbenz_audit",
        }
    )


def headline_bytes(result: SterbenzAuditResult | None = None) -> bytes:
    data = run_sterbenz_audit() if result is None else result
    return f"{data.headline_classification}\n\n{_headline_justification(data)}\n".encode("utf-8")


def audit_result_bytes(result: SterbenzAuditResult | None = None) -> bytes:
    data = run_sterbenz_audit() if result is None else result
    return _stable_json_bytes(data.to_json_safe())


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output-dir", default=str(REPORT_DIR))
    args = cli.parse_args()
    write_audit_outputs(Path(args.output_dir))


def _admissibility_records(candidate_ids: tuple[str, ...]) -> dict[str, object]:
    reference = candidate_by_id("c1_reference").metadata()
    records = {}
    for candidate_id in candidate_ids:
        candidate = candidate_by_id(candidate_id).metadata()
        records[candidate_id] = check_geometry_admissibility(reference, candidate)
    return records


def _headline(frontier: ParetoFrontierResult, vectors: dict[str, object]) -> str:
    unavailable_count = 0
    for vector in vectors.values():
        for value in vector.to_json_safe().values():
            if isinstance(value, str) and value.endswith("_unavailable"):
                unavailable_count += 1
    if unavailable_count >= 3 or "c3_factored" in frontier.frontier_members:
        return "sterbenz_audit_indeterminate"
    if "c1_reference" not in frontier.frontier_members:
        return "sterbenz_dominated_by_alternative"
    if frontier.frontier_members == ["c1_reference"]:
        return "sterbenz_minimum_burden_form_confirmed"
    return "sterbenz_tied_with_alternatives"


def _headline_justification(result: SterbenzAuditResult) -> str:
    if result.headline_classification == "sterbenz_minimum_burden_form_confirmed":
        return "The reference candidate is the sole Sterbenz-region Pareto-frontier member, and the calibration control is off the frontier."
    if result.headline_classification == "sterbenz_dominated_by_alternative":
        dominators = result.frontier.dominated_candidates.get("c1_reference", [])
        return (
            "The reference candidate is outside the Sterbenz-region Pareto frontier. "
            f"Its recorded dominators are {dominators}, while the calibration control remains off the frontier."
        )
    if result.headline_classification == "sterbenz_tied_with_alternatives":
        return (
            "The reference candidate remains on the Sterbenz-region Pareto frontier, but the frontier also contains "
            f"{[item for item in result.frontier.frontier_members if item != 'c1_reference']}."
        )
    return "The calibration control landed on the frontier or unavailable-data sentinels blocked the audit."


def _region_comparison(measurement: dict[str, object]) -> dict[str, object]:
    comparisons = {}
    for region_label in REGION_LABELS:
        vectors = burden_vectors_for_region(region_label, measurement)
        frontier = compute_pareto_frontier({"c1_reference": vectors["c1_reference"], "c2_reassociated": vectors["c2_reassociated"]})
        comparisons[region_label] = {
            "c1_reference": vectors["c1_reference"],
            "c2_reassociated": vectors["c2_reassociated"],
            "pairwise": frontier.pairwise_dominance,
            "frontier_members": frontier.frontier_members,
        }
    return comparisons


def _stable_json_bytes(payload: object) -> bytes:
    return (json.dumps(to_json_safe(payload), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


if __name__ == "__main__":
    main()
