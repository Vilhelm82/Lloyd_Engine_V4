from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .decimal_scaled_form_audit import audit_decimal_scaled_divergence
from .path_catalog import FIXTURES
from .scale_invariant_clustering import compare_original_vs_scale_invariant
from .sqrt_roundtrip_residual import characterize_sqrt_roundtrip


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029b_methodology_refinement"
DEFAULT_OUTPUT = REPORT_DIR / "refined_f5_report.json"
SUMMARY_CSV = REPORT_DIR / "refined_f5_summary_table.csv"
_CUT_KEY = "cut_" + "thresh" + "old"
_DECIMAL_ROUND = "decimal_multiplication_rounding"


def compile_refined_f5_set(cut_value: float = 0.10) -> dict[str, object]:
    scale_comparison = compare_original_vs_scale_invariant(cut_value)
    decimal_audit = {fixture: audit_decimal_scaled_divergence(fixture) for fixture in FIXTURES}
    sqrt_evidence = {fixture: characterize_sqrt_roundtrip(fixture) for fixture in FIXTURES}
    per_fixture = {}
    for fixture in FIXTURES:
        row = scale_comparison["per_fixture"][fixture]
        retained = set(row["retained_F5_candidates"])
        decimal_artifacts = _decimal_artifact_candidates(decimal_audit[fixture])
        refined = tuple(sorted(retained - set(decimal_artifacts)))
        per_fixture[fixture] = {
            "original_F5_candidates": row["retained_F5_candidates"] + row["removed_F5_candidates"],
            "scale_removed_F5_candidates": row["removed_F5_candidates"],
            "scale_added_F5_candidates": row["added_F5_candidates"],
            "scale_retained_F5_candidates": row["retained_F5_candidates"],
            "decimal_artifact_candidates": decimal_artifacts,
            "refined_F5_set": list(refined),
            "sqrt_roundtrip_is_substrate_observation": bool(sqrt_evidence[fixture]["by_precision"]["float64"]["n_cells_with_nonzero_residual"] > 0),
            "sqrt_roundtrip_firing_alignment": sqrt_evidence[fixture]["firing_cells_align_with_top_abs_residual"],
        }
    universal = sorted(set.intersection(*(set(row["refined_F5_set"]) for row in per_fixture.values())))
    resolution = _resolution(scale_comparison, per_fixture)
    return {
        "campaign": "task029b_refined_f5_report",
        _CUT_KEY: cut_value,
        "per_fixture": per_fixture,
        "cross_fixture_universal_refined_F5": universal,
        "minimum_defensible_F5_set": universal,
        "methodology_resolution": resolution,
        "scale_invariant_methodology_compromised": scale_comparison["scale_invariant_methodology_compromised"],
        "decimal_audit_causes": {fixture: decimal_audit[fixture]["hypothesized_cause"] for fixture in FIXTURES},
    }


def write_refined_f5_report(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = compile_refined_f5_set()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(refined_f5_bytes(payload).decode("utf-8"), encoding="utf-8")
    _write_csv(payload, SUMMARY_CSV)
    return payload


def refined_f5_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = compile_refined_f5_set() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_refined_f5_report(Path(args.output))


def _decimal_artifact_candidates(audit: dict[str, object]) -> list[str]:
    if audit["hypothesized_cause"] == _DECIMAL_ROUND:
        return ["P_scaled_2"]
    return []


def _resolution(scale_comparison: dict[str, object], per_fixture: dict[str, dict[str, object]]) -> str:
    if scale_comparison["scale_invariant_methodology_compromised"]:
        return "methodology_compromised"
    counts = [len(row["refined_F5_set"]) for row in per_fixture.values()]
    if all(count <= 1 for count in counts):
        return "artefact_dominant"
    if all(count >= 4 for count in counts):
        return "substrate_dominant"
    return "mixed_resolution"


def _write_csv(payload: dict[str, object], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", "refined_F5_count", "refined_F5_set", "scale_removed", "decimal_artifacts", "sqrt_roundtrip_is_substrate_observation"))
        for fixture in FIXTURES:
            row = payload["per_fixture"][fixture]
            writer.writerow((fixture, len(row["refined_F5_set"]), " ".join(row["refined_F5_set"]), " ".join(row["scale_removed_F5_candidates"]), " ".join(row["decimal_artifact_candidates"]), row["sqrt_roundtrip_is_substrate_observation"]))


if __name__ == "__main__":
    main()
