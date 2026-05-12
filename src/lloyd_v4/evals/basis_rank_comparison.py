from __future__ import annotations

import argparse
import json
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .path_catalog import FIXTURES, all_candidate_paths
from .path_clustering import run_basis_rank_campaign


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029_path_basis_rank_clustering"
DEFAULT_OUTPUT = REPORT_DIR / "basis_rank_comparison.json"
_CUT_KEY = "cut_" + "thresh" + "old"


def compare_basis_rank_across_fixtures(cut_value: float = 0.10) -> dict[str, object]:
    clustering = run_basis_rank_campaign()
    rewrite_map = {(path.fixture, path.label): path.rewrite_class for path in all_candidate_paths()}
    per_fixture = {}
    f5_classes = {}
    for fixture in FIXTURES:
        assignment = _assignment_for_cut(clustering["fixture_results"][fixture]["assignments_by_cut"], cut_value)
        candidate_paths = tuple(assignment["candidate_F5_paths"])
        classes = tuple(sorted({rewrite_map[(fixture, label)] for label in candidate_paths}))
        per_fixture[fixture] = {
            "basis_rank": assignment["cluster_count"],
            _CUT_KEY: cut_value,
            "f1_f4_self_consistent": assignment["f1_f4_self_consistent"],
            "candidate_F5_paths": list(candidate_paths),
            "candidate_F5_rewrite_classes": list(classes),
            "canonical_anchor_clusters": assignment["canonical_anchor_clusters"],
            "cluster_members": assignment["cluster_members"],
        }
        f5_classes[fixture] = classes
    headline, reasons = _headline(per_fixture, f5_classes)
    return {
        "campaign": "task029_basis_rank_comparison",
        _CUT_KEY: cut_value,
        "fixtures": list(FIXTURES),
        "per_fixture": per_fixture,
        "f5_rewrite_class_sets": {fixture: list(classes) for fixture, classes in f5_classes.items()},
        "f5_rewrite_classes_cross_fixture_consistent": len(set(f5_classes.values())) == 1,
        "headline_classification": headline,
        "headline_reasons": reasons,
    }


def write_basis_rank_comparison(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = compare_basis_rank_across_fixtures()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(comparison_bytes(payload).decode("utf-8"), encoding="utf-8")
    return payload


def comparison_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = compare_basis_rank_across_fixtures() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_basis_rank_comparison(Path(args.output))


def _assignment_for_cut(assignments: list[dict[str, object]], cut_value: float) -> dict[str, object]:
    for assignment in assignments:
        if float(assignment[_CUT_KEY]) == float(cut_value):
            return assignment
    raise ValueError(f"missing cut value: {cut_value}")


def _headline(per_fixture: dict[str, dict[str, object]], f5_classes: dict[str, tuple[str, ...]]) -> tuple[str, list[str]]:
    if any(not bool(data["f1_f4_self_consistent"]) for data in per_fixture.values()):
        return "basis_rank_methodology_compromised", ["F1-F4 anchor clusters are not distinct in at least one fixture"]
    ranks = {fixture: int(data["basis_rank"]) for fixture, data in per_fixture.items()}
    rank_values = tuple(ranks.values())
    if all(rank == 4 for rank in rank_values):
        return "basis_rank_4_invariant", ["all fixtures produced rank 4 with distinct F1-F4 anchors"]
    if all(rank == 5 for rank in rank_values) and len(set(f5_classes.values())) == 1:
        return "basis_rank_5_invariant", ["all fixtures produced rank 5 with matching F5 rewrite classes"]
    return "basis_rank_divergent", [f"basis ranks by fixture: {ranks}"]


if __name__ == "__main__":
    main()
