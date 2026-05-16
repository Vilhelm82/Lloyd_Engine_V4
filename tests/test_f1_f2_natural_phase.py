import json
import subprocess
from pathlib import Path

from lloyd_v4.evals import f1_f2_natural_phase as audit
from lloyd_v4.evals.multi_precision_four_form import ulp_of_double
from lloyd_v4.evals.sr_four_form import beta_grid, four_form_float64


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "f1_f2_natural_phase"
ARTIFACT = REPORT_DIR / "artifact_f1_f2_natural_phase.json"
CLOSEOUT = REPORT_DIR / "closeout_f1_f2_natural_phase.md"


def _artifact() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _fixture(name: str) -> dict[str, object]:
    return next(fixture for fixture in _artifact()["fixtures"] if fixture["fixture"] == name)


def test_phase_helpers_are_modular() -> None:
    assert audit.phase_mod(-0.25) == 0.75
    assert audit.circular_distance(0.95, 0.05) == 0.10000000000000009
    assert audit.phase_distance_to_half(0.5) == 0.0
    assert audit.phase_distance_to_zero(1.0) == 0.0


def test_sr_fixture_uses_existing_grid_and_lattice_unit() -> None:
    beta_value = beta_grid()[0]
    values = four_form_float64(beta_value)
    unit = ulp_of_double(1.0 - beta_value * beta_value)
    fixture = _fixture("sr_four_form")
    first_point = fixture["primary_pair"]["points"][0]

    assert fixture["coordinate_metadata"]["count"] == 137
    assert fixture["lattice_unit_convention"] == "ulp(1 - beta^2)"
    assert unit > 0.0
    assert "F1" in values and "F2" in values
    assert first_point["coordinate"] == beta_value


def test_primary_sr_outcome_is_phase_drift_not_supported() -> None:
    artifact = _artifact()
    primary = _fixture("sr_four_form")["primary_pair"]

    assert artifact["accepted_outcome"] == "phase_drift_not_mergeable"
    assert primary["pair"] == "F1_vs_F2"
    assert primary["usable_pair_count"] == 95
    assert primary["relation"] == "half_phase_present_but_drifting"
    assert primary["F1_phase_summary"]["fraction_within_tol"] == 1.0
    assert primary["F2_phase_summary"]["fraction_within_0_05"] < audit.GLOBAL_HALF_FRACTION
    assert primary["distance_to_half_summary"]["fraction_within_0_05"] < audit.STABLE_FRACTION


def test_pointwise_evidence_preserves_coordinate_pairing() -> None:
    primary = _fixture("sr_four_form")["primary_pair"]
    points = primary["points"]

    assert points
    assert len(points) == primary["usable_pair_count"]
    assert any(point["distance_delta_to_half"] == 0.0 for point in points)
    assert any(point["distance_delta_to_half"] == 0.5 for point in points)
    assert len({point["delta_phase"] for point in points}) > 10
    assert set(primary["region_summaries"]) == {"mildly_relativistic", "non_relativistic"}


def test_controls_do_not_manufacture_supported_half_phase() -> None:
    controls = _fixture("sr_four_form")["control_summaries"]

    assert controls["same_route_F1_F1"]["relation"] == "same_phase_stable"
    assert controls["same_route_F2_F2"]["relation"] == "same_phase_stable"
    assert controls["calibration_F1_F3"]["relation"] == "same_phase_stable"
    assert controls["calibration_F3_F3"]["relation"] == "insufficient_usable_pairs"
    assert controls["route_stressor_F1_F4"]["relation"] == "same_phase_stable"
    assert controls["route_stressor_F2_F4"]["relation"] != "pointwise_half_stable"


def test_secondary_schwarzschild_fixture_is_recorded() -> None:
    fixture = _fixture("schwarzschild_four_form")

    assert fixture["available"] is True
    assert fixture["coordinate_metadata"]["coordinate"] == "r"
    assert fixture["coordinate_metadata"]["count"] == 137
    assert fixture["primary_pair"]["usable_pair_count"] == 81


def test_artifact_and_closeout_are_byte_stable() -> None:
    assert audit.campaign_bytes() == ARTIFACT.read_bytes()
    closeout = CLOSEOUT.read_text(encoding="utf-8")
    assert "Accepted outcome: `phase_drift_not_mergeable`" in closeout
    assert "candidate interleaved lattice readback: `False`" in closeout
    assert "PYTHONPATH=src python -m lloyd_v4.evals.f1_f2_natural_phase" in closeout


def test_eval_layer_only_no_architecture_or_fixture_changes() -> None:
    paths = (
        "Build_Docs/Architecture/layer_manifest.json",
        "Build_Docs/Architecture/LAYER_MANIFEST.md",
        "src/lloyd_v4/evals/sr_four_form.py",
        "src/lloyd_v4/evals/schwarzschild_four_form.py",
    )
    subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=ROOT, check=True)
