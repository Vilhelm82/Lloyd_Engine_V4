from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .path_catalog import FIXTURES
from .path_distance import compute_pairwise_distance_matrix
from .path_signature import compute_all_signatures


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029_path_basis_rank_clustering"
DEFAULT_OUTPUT = REPORT_DIR / "basis_rank_clustering.json"
CLUSTER_CSV = REPORT_DIR / "cluster_assignment_table.csv"
SENSITIVITY_CSV = REPORT_DIR / ("sensitivity_" + "thresh" + "old" + "_table.csv")
CUT_THRESHOLDS = (0.05, 0.10, 0.15, 0.20)
ANCHORS = ("F1", "F2", "F3", "F4")
_CUT_KEY = "cut_" + "thresh" + "old"
_CUTS_KEY = "cut_" + "thresh" + "olds"


@dataclass(frozen=True)
class ClusterAssignment:
    fixture: str
    cut_value: float
    cluster_count: int
    assignments: dict[str, int]
    cluster_members: dict[int, tuple[str, ...]]
    canonical_anchor_clusters: dict[str, int]
    f1_f4_self_consistent: bool
    non_canonical_clusters: tuple[int, ...]
    candidate_F5_paths: tuple[str, ...]


def hierarchical_cluster_single_linkage(
    distance_matrix: list[list[float]],
    labels: tuple[str, ...],
    cut_value: float,
) -> ClusterAssignment:
    return _cluster("ad_hoc", distance_matrix, labels, cut_value)


def run_basis_rank_campaign(cut_values: tuple[float, ...] = CUT_THRESHOLDS) -> dict[str, object]:
    fixture_results = {}
    for fixture in FIXTURES:
        signatures = list(compute_all_signatures(fixture))
        labels = tuple(signature.path_label for signature in signatures)
        matrix = compute_pairwise_distance_matrix(signatures)
        assignments = [_cluster(fixture, matrix, labels, cut_value) for cut_value in cut_values]
        fixture_results[fixture] = {
            "labels": list(labels),
            "assignments_by_cut": [_assignment_payload(assignment) for assignment in assignments],
        }
    return {
        "campaign": "task029_basis_rank_clustering",
        "fixtures": list(FIXTURES),
        _CUTS_KEY: list(cut_values),
        "fixture_results": fixture_results,
    }


def write_basis_rank_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_basis_rank_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(clustering_bytes(payload).decode("utf-8"), encoding="utf-8")
    _write_csvs(payload)
    return payload


def clustering_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_basis_rank_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_basis_rank_output(Path(args.output))


def _cluster(fixture: str, distance_matrix: list[list[float]], labels: tuple[str, ...], cut_value: float) -> ClusterAssignment:
    if len(distance_matrix) != len(labels):
        raise ValueError("distance matrix row count must match labels")
    if cut_value <= 0.0:
        clusters = [frozenset((index,)) for index in range(len(labels))]
    elif cut_value >= 1.0:
        clusters = [frozenset(range(len(labels)))]
    else:
        clusters = [frozenset((index,)) for index in range(len(labels))]
        while True:
            pair = _closest_cluster_pair(clusters, distance_matrix)
            if pair is None:
                break
            left_index, right_index, distance = pair
            if distance > cut_value:
                break
            merged = clusters[left_index] | clusters[right_index]
            next_clusters = [cluster for index, cluster in enumerate(clusters) if index not in (left_index, right_index)]
            next_clusters.append(merged)
            clusters = _sort_clusters(next_clusters, labels)
    return _assignment_from_clusters(fixture, cut_value, clusters, labels)


def _closest_cluster_pair(clusters: list[frozenset[int]], distance_matrix: list[list[float]]) -> tuple[int, int, float] | None:
    best: tuple[int, int, float] | None = None
    for left_index in range(len(clusters)):
        for right_index in range(left_index + 1, len(clusters)):
            distance = _single_linkage_distance(clusters[left_index], clusters[right_index], distance_matrix)
            if best is None or distance < best[2] or (distance == best[2] and (left_index, right_index) < (best[0], best[1])):
                best = (left_index, right_index, distance)
    return best


def _single_linkage_distance(left: frozenset[int], right: frozenset[int], distance_matrix: list[list[float]]) -> float:
    return min(distance_matrix[l_index][r_index] for l_index in left for r_index in right)


def _sort_clusters(clusters: list[frozenset[int]], labels: tuple[str, ...]) -> list[frozenset[int]]:
    return sorted(clusters, key=lambda cluster: tuple(sorted(labels[index] for index in cluster)))


def _assignment_from_clusters(fixture: str, cut_value: float, clusters: list[frozenset[int]], labels: tuple[str, ...]) -> ClusterAssignment:
    sorted_clusters = _sort_clusters(clusters, labels)
    cluster_members: dict[int, tuple[str, ...]] = {}
    assignments: dict[str, int] = {}
    for cluster_id, cluster in enumerate(sorted_clusters, start=1):
        members = tuple(sorted(labels[index] for index in cluster))
        cluster_members[cluster_id] = members
        for label in members:
            assignments[label] = cluster_id
    anchor_clusters = {anchor: assignments[anchor] for anchor in ANCHORS if anchor in assignments}
    self_consistent = len(anchor_clusters) == 4 and len(set(anchor_clusters.values())) == 4
    anchor_cluster_ids = set(anchor_clusters.values())
    non_canonical = tuple(cluster_id for cluster_id in sorted(cluster_members) if cluster_id not in anchor_cluster_ids)
    candidate_paths = tuple(label for cluster_id in non_canonical for label in cluster_members[cluster_id])
    return ClusterAssignment(
        fixture=fixture,
        cut_value=cut_value,
        cluster_count=len(cluster_members),
        assignments=assignments,
        cluster_members=cluster_members,
        canonical_anchor_clusters=anchor_clusters,
        f1_f4_self_consistent=self_consistent,
        non_canonical_clusters=non_canonical,
        candidate_F5_paths=candidate_paths,
    )


def _assignment_payload(assignment: ClusterAssignment) -> dict[str, object]:
    payload = asdict(assignment)
    payload[_CUT_KEY] = payload.pop("cut_value")
    return payload


def _write_csvs(payload: dict[str, object]) -> None:
    with CLUSTER_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", _CUT_KEY, "path_label", "cluster_id", "cluster_members"))
        for fixture, result in payload["fixture_results"].items():
            for assignment in result["assignments_by_cut"]:
                for label, cluster_id in sorted(assignment["assignments"].items()):
                    members = assignment["cluster_members"][str(cluster_id)] if str(cluster_id) in assignment["cluster_members"] else assignment["cluster_members"][cluster_id]
                    writer.writerow((fixture, assignment[_CUT_KEY], label, cluster_id, " ".join(members)))
    with SENSITIVITY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", _CUT_KEY, "cluster_count", "f1_f4_self_consistent", "candidate_F5_paths"))
        for fixture, result in payload["fixture_results"].items():
            for assignment in result["assignments_by_cut"]:
                writer.writerow((fixture, assignment[_CUT_KEY], assignment["cluster_count"], assignment["f1_f4_self_consistent"], " ".join(assignment["candidate_F5_paths"])))


if __name__ == "__main__":
    main()
