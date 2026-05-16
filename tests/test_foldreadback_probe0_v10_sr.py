import json
from pathlib import Path

from lloyd_v4.evals.sr_four_form import beta_grid, eta_of_beta, four_form_float64

import scratch.run_foldreadback_probe0_v10_active_dualarm as v10


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "foldreadback_probe0_v10_active_dualarm"
REPORT_ARTIFACT = REPORT_DIR / "artifact_v10_sr.json"
CLOSEOUT = REPORT_DIR / "closeout_v10_sr.md"


def _artifact() -> dict[str, object]:
    return json.loads(REPORT_ARTIFACT.read_text(encoding="utf-8"))


def test_sr_fixture_grid_contract() -> None:
    values = beta_grid()
    assert len(values) == 137
    assert values[0] == 0.01
    assert values[-1] == 0.9999
    assert all(left < right for left, right in zip(values, values[1:]))
    assert eta_of_beta(values[-1]) > 0.0
    assert "F4" in four_form_float64(values[-1])


def test_sr_points_encode_singular_surface_and_f4_levels() -> None:
    points = v10.sr_surface_points("F4_float64")
    creg = v10.creg(points)

    assert len(points) == 137
    assert len(creg) == 41
    assert float(creg[0]["beta"]) == 0.9999
    assert float(creg[-1]["beta"]) < float(creg[0]["beta"])
    assert any(point["L"] != 0 for point in creg)
    assert all(point["e_f"] < point["e_x"] for point in creg)


def test_sr_artifact_schema_and_precise_outcome_label() -> None:
    artifact = _artifact()
    accepted = artifact["accepted_outcome"]

    assert accepted in set(v10.SR_OUTCOMES.values())
    assert accepted == "active_handoff_gap_resolved"
    assert {"primary_scan", "controls", "invariance", "closeout_answers", "verification"} <= set(artifact)
    assert artifact["primary_scan"]["fixture"] == "sr_four_form"
    assert artifact["primary_scan"]["coordinate"] == "beta"
    assert artifact["closeout_verdict"] == accepted


def test_sr_reuses_v10_v7_v8_without_new_dual_arm_method() -> None:
    reuse = _artifact()["source_reuse"]

    assert reuse["new_dual_arm_method"] is False
    assert reuse["v7_primitives_copied_or_modified"] is False
    assert "ols_design_pivot_ok" in reuse["v7_imported"]
    assert "classify_instrument" in reuse["v8_imported"]
    assert reuse["sr_imported"] == ["beta_grid", "eta_of_beta", "four_form_float64"]


def test_sr_armw_falloff_activates_armn() -> None:
    artifact = _artifact()
    answers = artifact["closeout_answers"]
    primary = artifact["primary_scan"]

    assert answers["armW_warning_or_below_near_endpoint"] is True
    assert answers["armN_activated_from_armW_falloff"] is True
    assert primary["active_N_intervals"]
    assert any(record["armN"]["activation_reason"] == "core_gap" for record in primary["records"])
    assert answers["armW_state_counts"]["warning"] > 0
    assert answers["armW_state_counts"]["below_floor"] > 0


def test_sr_gap_resolution_and_overlap_agreement() -> None:
    answers = _artifact()["closeout_answers"]

    assert answers["armN_valid_read_inside_gap"] is True
    assert answers["armN_valid_core_count"] == 13
    assert answers["overlap_both_valid_count"] == 9
    assert answers["overlap_agreements"] == ["agree"]


def test_sr_controls_and_invariance_hold() -> None:
    artifact = _artifact()
    controls = artifact["controls"]

    assert artifact["invariance"]["partition_phase_0_1_match"] is True
    assert artifact["invariance"]["guard_1_2_outcome_safe"] is True
    assert controls["exact_zero"]["silent"] is True
    assert controls["matched_affine"]["silent"] is True
    assert artifact["closeout_answers"]["controls_remained_silent"] is True


def test_sr_outcome_discipline_and_byte_stability() -> None:
    unresolved = {
        "active_N_intervals": [{"core_start": 0, "core_end": 0, "active_start": 0, "active_end": 0, "guard": 1}],
        "records": [{"armW": {"inference": "searched_no_separation", "falloff_state": "below_floor"}, "armN": {"active": True, "valid": False, "activation_reason": "core_gap"}}],
    }
    separated_wide = {
        "active_N_intervals": [],
        "records": [{"beta": "0.9999", "armW": {"inference": "separated", "falloff_state": "readable"}, "armN": {"active": False, "valid": False, "activation_reason": "none"}}],
    }

    assert v10.select_sr_outcome(unresolved) == "active_handoff_gap_unresolved"
    assert v10.select_sr_outcome(separated_wide) == "active_dual_read_wide_only_with_separation"
    assert v10.artifact_sr_bytes() == REPORT_ARTIFACT.read_bytes()
    closeout = CLOSEOUT.read_text(encoding="utf-8")
    assert "PYTHONPATH=src python scratch/run_foldreadback_probe0_v10_active_dualarm.py --sr" in closeout
    assert "Result: passed" in closeout
