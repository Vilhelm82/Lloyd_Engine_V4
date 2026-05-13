from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from lloyd_v4.core.serialization import to_json_safe

from .burden_vector import BurdenVector, DEFAULT_REPORTS_ROOT, extract_burden_vector
from .geometry_admissibility import AdmissibilityResult, check_geometry_admissibility
from .pareto_decision import ParetoComparisonResult, compare_burden_vectors


ROOT = Path(__file__).resolve().parents[4]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task030_refinery_mvp"
DECISION_RECORD_OUTPUT = REPORT_DIR / "mvp_decision_record.json"
BURDEN_VECTORS_OUTPUT = REPORT_DIR / "burden_vectors.json"
HEADLINE_OUTPUT = REPORT_DIR / "headline_classification.md"
PRE_REGISTRATION_COMMIT = "b907d93"
PRE_REGISTERED_EXPECTED_OUTCOME = "accepted"

FORM_METADATA = {
    "pure_algebraic": {
        "F1": {
            "calibration_status": "non_calibration",
            "declared_algebraic_identity": "pure_algebraic_zero_constraint",
            "domain_stratum_label": "canonical_137_point_domain",
            "fixture_name": "pure_algebraic",
            "operand_grid_label": "pure_algebraic_x_grid_137",
            "path_name": "F1",
        },
        "F2": {
            "calibration_status": "non_calibration",
            "declared_algebraic_identity": "pure_algebraic_zero_constraint",
            "domain_stratum_label": "canonical_137_point_domain",
            "fixture_name": "pure_algebraic",
            "operand_grid_label": "pure_algebraic_x_grid_137",
            "path_name": "F2",
        },
    }
}


@dataclass(frozen=True)
class MvpDecisionRecord:
    admissibility: AdmissibilityResult
    burden_vectors: dict[str, BurdenVector]
    comparison: ParetoComparisonResult
    final_outcome: str
    headline_classification: str
    match_against_pre_registration: bool
    reference_form: dict[str, object]
    candidate_form: dict[str, object]

    def to_json_safe(self) -> dict[str, object]:
        return {
            "admissibility": self.admissibility,
            "burden_vectors": self.burden_vectors,
            "candidate_form": self.candidate_form,
            "comparison": self.comparison,
            "final_outcome": self.final_outcome,
            "headline_classification": self.headline_classification,
            "match_against_pre_registration": self.match_against_pre_registration,
            "pre_registration": {
                "commit": PRE_REGISTRATION_COMMIT,
                "expected_outcome": PRE_REGISTERED_EXPECTED_OUTCOME,
            },
            "reference_form": self.reference_form,
            "task": "task030_refinery_mvp",
        }


def form_metadata(fixture_name: str, path_name: str) -> dict[str, object]:
    try:
        return dict(FORM_METADATA[fixture_name][path_name])
    except KeyError:
        return {
            "calibration_status": "metadata_field_unavailable",
            "declared_algebraic_identity": "metadata_field_unavailable",
            "domain_stratum_label": "metadata_field_unavailable",
            "fixture_name": fixture_name,
            "operand_grid_label": "metadata_field_unavailable",
            "path_name": path_name,
        }


def run_default_mvp_decision(campaign_reports_root: str | Path = DEFAULT_REPORTS_ROOT) -> MvpDecisionRecord:
    return run_mvp_decision("F2", "F1", campaign_reports_root)


def run_mvp_decision(
    reference_form: str | Mapping[str, object],
    candidate_form: str | Mapping[str, object],
    campaign_reports_root: str | Path = DEFAULT_REPORTS_ROOT,
) -> MvpDecisionRecord:
    reference_metadata = _coerce_form_metadata(reference_form)
    candidate_metadata = _coerce_form_metadata(candidate_form)
    admissibility = check_geometry_admissibility(reference_metadata, candidate_metadata)

    if admissibility.status != "admissible":
        comparison = ParetoComparisonResult(outcome="comparison_indeterminate", per_dimension={})
        return MvpDecisionRecord(
            admissibility=admissibility,
            burden_vectors={},
            comparison=comparison,
            final_outcome=comparison.outcome,
            headline_classification="mvp_decision_law_refuted",
            match_against_pre_registration=False,
            reference_form=reference_metadata,
            candidate_form=candidate_metadata,
        )

    reference_vector = extract_burden_vector(
        str(reference_metadata["fixture_name"]),
        str(reference_metadata["path_name"]),
        campaign_reports_root,
    )
    candidate_vector = extract_burden_vector(
        str(candidate_metadata["fixture_name"]),
        str(candidate_metadata["path_name"]),
        campaign_reports_root,
    )
    comparison = compare_burden_vectors(reference_vector, candidate_vector)
    headline = _classify_headline(comparison)
    return MvpDecisionRecord(
        admissibility=admissibility,
        burden_vectors={
            "candidate": candidate_vector,
            "reference": reference_vector,
        },
        comparison=comparison,
        final_outcome=comparison.outcome,
        headline_classification=headline,
        match_against_pre_registration=comparison.outcome == PRE_REGISTERED_EXPECTED_OUTCOME,
        reference_form=reference_metadata,
        candidate_form=candidate_metadata,
    )


def write_mvp_outputs(
    output_dir: str | Path = REPORT_DIR,
    campaign_reports_root: str | Path = DEFAULT_REPORTS_ROOT,
) -> MvpDecisionRecord:
    record = run_default_mvp_decision(campaign_reports_root)
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "mvp_decision_record.json").write_bytes(decision_record_bytes(record))
    (target_dir / "burden_vectors.json").write_bytes(burden_vectors_bytes(record))
    (target_dir / "headline_classification.md").write_bytes(headline_bytes(record))
    return record


def decision_record_bytes(record: MvpDecisionRecord | None = None) -> bytes:
    data = run_default_mvp_decision() if record is None else record
    return _stable_json_bytes(data.to_json_safe())


def burden_vectors_bytes(record: MvpDecisionRecord | None = None) -> bytes:
    data = run_default_mvp_decision() if record is None else record
    payload = {
        "burden_vectors": data.burden_vectors,
        "candidate_path": data.candidate_form["path_name"],
        "reference_path": data.reference_form["path_name"],
        "task": "task030_refinery_mvp",
    }
    return _stable_json_bytes(payload)


def headline_bytes(record: MvpDecisionRecord | None = None) -> bytes:
    data = run_default_mvp_decision() if record is None else record
    justification = _headline_justification(data)
    return f"{data.headline_classification}\n\n{justification}\n".encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output-dir", default=str(REPORT_DIR))
    cli.add_argument("--reports-root", default=str(DEFAULT_REPORTS_ROOT))
    args = cli.parse_args()
    write_mvp_outputs(Path(args.output_dir), Path(args.reports_root))


def _coerce_form_metadata(form: str | Mapping[str, object]) -> dict[str, object]:
    if isinstance(form, str):
        return form_metadata("pure_algebraic", form)
    return dict(form)


def _classify_headline(comparison: ParetoComparisonResult) -> str:
    has_unavailable = any(row["status"] == "unavailable" for row in comparison.per_dimension.values())
    has_mismatch = any(row["status"] == "mismatch" for row in comparison.per_dimension.values())
    if comparison.outcome == PRE_REGISTERED_EXPECTED_OUTCOME and not has_unavailable and not has_mismatch:
        return "mvp_validates_decision_law"
    if comparison.outcome in {"accepted", "rejected", "forms_structurally_tied", "comparison_indeterminate"}:
        return "mvp_decision_law_partial"
    return "mvp_decision_law_refuted"


def _headline_justification(record: MvpDecisionRecord) -> str:
    if record.headline_classification == "mvp_validates_decision_law":
        return (
            "The admissibility gate passed for F2 as reference and F1 as candidate, all required burden "
            "dimensions were available from committed reports or locked static path metadata, and the "
            "Pareto comparison produced the pre-registered accepted outcome."
        )
    if record.headline_classification == "mvp_decision_law_partial":
        return (
            "The MVP produced a typed decision record, but the decision either diverged from the "
            "pre-registered outcome or required at least one unavailable or mismatched dimension."
        )
    return "The MVP did not produce a coherent typed decision record from the committed inputs."


def _stable_json_bytes(payload: object) -> bytes:
    return (json.dumps(to_json_safe(payload), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


if __name__ == "__main__":
    main()
