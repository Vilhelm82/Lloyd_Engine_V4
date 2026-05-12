from __future__ import annotations

import argparse
import json
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .path_catalog import FIXTURES
from .path_clustering import CUT_THRESHOLDS, _assignment_payload, _cluster
from .path_distance import compute_pairwise_distance_matrix
from .scale_invariant_signature import compute_all_signatures_scale_invariant


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029b_methodology_refinement"
TASK029_REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029_path_basis_rank_clustering"
DEFAULT_OUTPUT = REPORT_DIR / "scale_invariant_clustering.json"
COMPARISON_OUTPUT = REPORT_DIR / "scale_invariant_vs_original_comparison.json"
ORIGINAL_CLUSTERING_OUTPUT = TASK029_REPORT_DIR / "basis_rank_clustering.json"
_CUT_KEY = "cut_" + "thresh" + "old"
_CUTS_KEY = "cut_" + "thresh" + "olds"


def run_scale_invariant_clustering_campaign(cut_values: tuple[float, ...] = CUT_THRESHOLDS) -> dict[str, object]:
    fixture_results = {}
    for fixture in FIXTURES:
        signatures = list(compute_all_signatures_scale_invariant(fixture))
        labels = tuple(signature.path_label for signature in signatures)
        matrix = compute_pairwise_distance_matrix(signatures)
        assignments = [_cluster(fixture, matrix, labels, cut_value) for cut_value in cut_values]
        fixture_results[fixture] = {
            "labels": list(labels),
            "assignments_by_cut": [_assignment_payload(assignment) for assignment in assignments],
        }
    return {
        "campaign": "task029b_scale_invariant_clustering",
        "fixtures": list(FIXTURES),
        _CUTS_KEY: list(cut_values),
        "fixture_results": fixture_results,
    }


def compare_original_vs_scale_invariant(cut_value: float = 0.10) -> dict[str, object]:
    original = _read_json(ORIGINAL_CLUSTERING_OUTPUT)
    refined = run_scale_invariant_clustering_campaign()
    rows = {}
    for fixture in FIXTURES:
        original_assignment = _assignment_for_cut(original["fixture_results"][fixture]["assignments_by_cut"], cut_value)
        refined_assignment = _assignment_for_cut(refined["fixture_results"][fixture]["assignments_by_cut"], cut_value)
        original_f5 = set(original_assignment["candidate_F5_paths"])
        refined_f5 = set(refined_assignment["candidate_F5_paths"])
        rows[fixture] = {
            "original_rank": original_assignment["cluster_count"],
            "scale_invariant_rank": refined_assignment["cluster_count"],
            "original_f1_f4_self_consistent": original_assignment["f1_f4_self_consistent"],
            "scale_invariant_f1_f4_self_consistent": refined_assignment["f1_f4_self_consistent"],
            "removed_F5_candidates": sorted(original_f5 - refined_f5),
            "added_F5_candidates": sorted(refined_f5 - original_f5),
            "retained_F5_candidates": sorted(original_f5 & refined_f5),
            "scale_invariant_F5_candidates": sorted(refined_f5),
        }
    return {
        "campaign": "task029b_scale_invariant_vs_original",
        _CUT_KEY: cut_value,
        "fixtures": list(FIXTURES),
        "per_fixture": rows,
        "scale_invariant_methodology_compromised": any(not row["scale_invariant_f1_f4_self_consistent"] for row in rows.values()),
    }


def write_scale_invariant_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_scale_invariant_clustering_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scale_cluster_bytes(payload).decode("utf-8"), encoding="utf-8")
    if path == DEFAULT_OUTPUT:
        write_scale_invariant_comparison(COMPARISON_OUTPUT)
    return payload


def write_scale_invariant_comparison(path: Path = COMPARISON_OUTPUT) -> dict[str, object]:
    payload = compare_original_vs_scale_invariant()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scale_comparison_bytes(payload).decode("utf-8"), encoding="utf-8")
    return payload


def scale_cluster_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_scale_invariant_clustering_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def scale_comparison_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = compare_original_vs_scale_invariant() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_scale_invariant_output(Path(args.output))


def _assignment_for_cut(assignments: list[dict[str, object]], cut_value: float) -> dict[str, object]:
    for assignment in assignments:
        if float(assignment[_CUT_KEY]) == float(cut_value):
            return assignment
    raise ValueError(f"missing cut value: {cut_value}")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
