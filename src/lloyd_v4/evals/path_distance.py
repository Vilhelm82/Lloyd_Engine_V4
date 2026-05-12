from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from lloyd_v4.core.serialization import to_json_safe

from .path_catalog import FIXTURES
from .path_signature import PathSignature, compute_all_signatures


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029_path_basis_rank_clustering"
DEFAULT_OUTPUT = REPORT_DIR / "pairwise_distance_matrices.json"


def zero_mask_distance(a: PathSignature, b: PathSignature) -> float:
    total = len(a.zero_mask_fingerprint)
    if total != len(b.zero_mask_fingerprint):
        raise ValueError("zero-mask fingerprints must have equal length")
    if total == 0:
        return 0.0
    diff = sum(1 for left, right in zip(a.zero_mask_fingerprint, b.zero_mask_fingerprint, strict=True) if left != right)
    return diff / float(total)


def signed_lattice_distance(a: PathSignature, b: PathSignature) -> float:
    left = _normalised_histogram(a.signed_lattice_histogram)
    right = _normalised_histogram(b.signed_lattice_histogram)
    keys = sorted(set(left) | set(right))
    return sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys)


def precision_scaling_distance(a: PathSignature, b: PathSignature) -> float:
    denominator = max(sum(a.precision_scaling), sum(b.precision_scaling), 1.0)
    return min(sum(abs(left - right) for left, right in zip(a.precision_scaling, b.precision_scaling, strict=True)) / denominator, 1.0)


def alpha_status_distance(a: PathSignature, b: PathSignature) -> float:
    total = len(a.alpha_status_at_characteristic)
    if total != len(b.alpha_status_at_characteristic):
        raise ValueError("alpha-status tuples must have equal length")
    if total == 0:
        return 0.0
    diff = sum(1 for left, right in zip(a.alpha_status_at_characteristic, b.alpha_status_at_characteristic, strict=True) if left != right)
    return diff / float(total)


def cofire_polarity_distance(a: PathSignature, b: PathSignature) -> float:
    anchors = sorted(set(a.cofire_polarity_with_canonical) | set(b.cofire_polarity_with_canonical))
    total = 0.0
    left_total = 0.0
    right_total = 0.0
    for anchor in anchors:
        left = a.cofire_polarity_with_canonical.get(anchor, (0, 0, 0))
        right = b.cofire_polarity_with_canonical.get(anchor, (0, 0, 0))
        left_total += sum(float(value) for value in left)
        right_total += sum(float(value) for value in right)
        total += sum(abs(float(l_value) - float(r_value)) for l_value, r_value in zip(left, right, strict=True))
    denominator = max(left_total, right_total, 1.0)
    return min(total / denominator, 1.0)


def envelope_shape_distance(a: PathSignature, b: PathSignature) -> float:
    return sum((left - right) * (left - right) for left, right in zip(a.envelope_shape, b.envelope_shape, strict=True)) ** 0.5


def composite_distance(a: PathSignature, b: PathSignature) -> float:
    components = (
        zero_mask_distance(a, b),
        signed_lattice_distance(a, b) / 2.0,
        precision_scaling_distance(a, b),
        alpha_status_distance(a, b),
        cofire_polarity_distance(a, b),
        min(envelope_shape_distance(a, b) / 2.0, 1.0),
    )
    return sum(components) / float(len(components))


def compute_pairwise_distance_matrix(signatures: list[PathSignature]) -> list[list[float]]:
    rows: list[list[float]] = []
    for left in signatures:
        row = []
        for right in signatures:
            row.append(composite_distance(left, right))
        rows.append(row)
    return rows


def run_distance_campaign() -> dict[str, object]:
    matrices = {}
    for fixture in FIXTURES:
        signatures = list(compute_all_signatures(fixture))
        labels = [signature.path_label for signature in signatures]
        matrices[fixture] = {
            "labels": labels,
            "matrix": compute_pairwise_distance_matrix(signatures),
        }
    return {
        "campaign": "task029_pairwise_path_distance",
        "fixtures": list(FIXTURES),
        "distance_dimensions": [
            "zero_mask_distance",
            "signed_lattice_distance",
            "precision_scaling_distance",
            "alpha_status_distance",
            "cofire_polarity_distance",
            "envelope_shape_distance",
        ],
        "composite_distance": "simple_unweighted_mean_of_six_normalised_dimensions",
        "matrices": matrices,
    }


def write_distance_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_distance_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(distance_bytes(payload).decode("utf-8"), encoding="utf-8")
    return payload


def distance_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_distance_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_distance_output(Path(args.output))


def _normalised_histogram(histogram: dict[str, int]) -> dict[str, float]:
    total = sum(histogram.values())
    if total == 0:
        return {"__empty__": 1.0}
    return {key: value / float(total) for key, value in histogram.items()}


if __name__ == "__main__":
    main()
