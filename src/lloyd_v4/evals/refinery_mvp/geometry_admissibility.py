from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


REQUIRED_METADATA_FIELDS = (
    ("fixture_name", "inadmissible_fixture_mismatch"),
    ("operand_grid_label", "inadmissible_grid_mismatch"),
    ("declared_algebraic_identity", "inadmissible_identity_mismatch"),
    ("calibration_status", "inadmissible_calibration_mismatch"),
    ("domain_stratum_label", "inadmissible_domain_mismatch"),
)


@dataclass(frozen=True)
class AdmissibilityResult:
    status: str
    mismatch_field: str
    reference_value: object
    candidate_value: object

    def to_json_safe(self) -> dict[str, object]:
        return {
            "candidate_value": self.candidate_value,
            "mismatch_field": self.mismatch_field,
            "reference_value": self.reference_value,
            "status": self.status,
        }


def check_geometry_admissibility(
    reference_form_metadata: Mapping[str, object],
    candidate_form_metadata: Mapping[str, object],
) -> AdmissibilityResult:
    for field_name, mismatch_status in REQUIRED_METADATA_FIELDS:
        reference_value = reference_form_metadata.get(field_name, "metadata_field_unavailable")
        candidate_value = candidate_form_metadata.get(field_name, "metadata_field_unavailable")
        if reference_value != candidate_value:
            return AdmissibilityResult(
                status=mismatch_status,
                mismatch_field=field_name,
                reference_value=reference_value,
                candidate_value=candidate_value,
            )
    return AdmissibilityResult(
        status="admissible",
        mismatch_field="none",
        reference_value="matched",
        candidate_value="matched",
    )
