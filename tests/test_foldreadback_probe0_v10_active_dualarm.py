import json
import subprocess
from decimal import Decimal
from pathlib import Path

import scratch.run_foldreadback_probe0_v10_active_dualarm as v10


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "foldreadback_probe0_v10_active_dualarm"
REPORT_ARTIFACT = REPORT_DIR / "artifact_v10.json"
SCRATCH_ARTIFACT = ROOT / "scratch" / "foldreadback_probe0_v10_active_dualarm_artifact.json"
V10_SOURCE = ROOT / "scratch" / "run_foldreadback_probe0_v10_active_dualarm.py"


def _point(name: str, rank_value: str, level: int = 1) -> dict[str, object]:
    return {"name": name, "f0": Decimal(rank_value), "L": level, "e_f": -2, "e_x": -1}


def _half_assignment(points: list[dict[str, object]], rank_map: dict[str, int]) -> dict[str, str]:
    left, right = v10.anchored_halves(points, rank_map)
    result = {}
    for point in left:
        result[point["name"]] = "left"
    for point in right:
        result[point["name"]] = "right"
    return result


def test_v10_does_not_emit_v9_overlap_labels() -> None:
    source = V10_SOURCE.read_text(encoding="utf-8")
    artifact_text = REPORT_ARTIFACT.read_text(encoding="utf-8")
    assert "two_tier_" not in source
    assert "two_tier_" not in artifact_text
    artifact = json.loads(artifact_text)
    assert not artifact["accepted_outcome"].startswith("two_tier_")


def test_anchored_halves_stable_under_boundary_extension() -> None:
    full = [_point("boundary_low", "0.00"), _point("a", "0.10"), _point("b", "0.20"), _point("c", "0.30"), _point("boundary_high", "0.40")]
    rank_map = v10.global_rank_map(full)
    base = full[1:4]
    extended_low = full[0:4]
    extended_high = full[1:5]

    base_assignment = _half_assignment(base, rank_map)
    low_assignment = _half_assignment(extended_low, rank_map)
    high_assignment = _half_assignment(extended_high, rank_map)

    for name in ("a", "b", "c"):
        assert low_assignment[name] == base_assignment[name]
        assert high_assignment[name] == base_assignment[name]


def test_partition_phase_invariance() -> None:
    phase0 = v10.run_fixture("0.500", "0.501", label="phase0", phase=0, guard=1)
    phase1 = v10.run_fixture("0.500", "0.501", label="phase1", phase=1, guard=1)
    assert phase0["outcome_basis"] == phase1["outcome_basis"]


def test_armN_activation_depends_on_armW_falloff_not_W_overlap() -> None:
    no_gap = v10.activation_intervals_from_falloff(["readable", "warning", "recovered"], guard=1)
    with_gap = v10.activation_intervals_from_falloff(["readable", "below_floor", "below_floor", "readable"], guard=1)

    assert no_gap == []
    assert with_gap == [{"core_start": 1, "core_end": 2, "active_start": 0, "active_end": 3, "guard": 1}]
    assert v10.activation_reason(1, with_gap) == "core_gap"
    assert v10.activation_reason(0, with_gap) == "guard"


def test_armN_validity_independent_of_armW_validity() -> None:
    arm_w_invalid = v10.arm_w_validity_from_parts(True, {"sign_pattern": "collapsed"}, False, True)
    arm_n_valid = v10.arm_n_validity_from_parts(True, {"level_histogram": "nondegenerate", "transition": "saturated"})
    arm_w_valid = v10.arm_w_validity_from_parts(True, {"sign_pattern": "nondegenerate"}, True, True)
    arm_n_untested = v10.arm_n_validity_from_parts(True, {"level_histogram": "saturated", "lattice_rank": "collapsed"})

    assert arm_w_invalid is False
    assert arm_n_valid is True
    assert arm_w_valid is True
    assert arm_n_untested is False


def test_overlap_is_diagnostic_not_outcome_definition() -> None:
    scan = {
        "active_N_intervals": [],
        "records": [
            {
                "armN": {"valid": True, "activation_reason": "guard"},
                "overlap": {"both_active": True, "both_valid": True, "agreement": "agree"},
            }
        ],
    }
    assert v10.select_outcome(scan) == "active_dual_read_wide_only_no_falloff"


def test_affine_kill_control_disqualifies_manufactured_fold() -> None:
    scan = {"active_N_intervals": [], "records": [{"armN": {"valid": False, "activation_reason": "none"}, "overlap": {"agreement": "not_applicable"}}]}
    assert v10.select_outcome(scan, controls_silent=False) == "active_dual_read_disqualified_manufactured"


def test_gap_unresolved_when_armN_never_valid() -> None:
    scan = {
        "active_N_intervals": [{"core_start": 1, "core_end": 1, "active_start": 0, "active_end": 2, "guard": 1}],
        "records": [
            {"armN": {"valid": False, "activation_reason": "guard"}, "overlap": {"agreement": "underpowered"}},
            {"armN": {"valid": False, "activation_reason": "core_gap"}, "overlap": {"agreement": "underpowered"}},
        ],
    }
    assert v10.select_outcome(scan) == "active_dual_read_gap_unresolved"


def test_gap_resolved_when_armN_valid_inside_armW_gap() -> None:
    scan = {
        "active_N_intervals": [{"core_start": 1, "core_end": 1, "active_start": 0, "active_end": 2, "guard": 1}],
        "records": [
            {"armN": {"valid": False, "activation_reason": "guard"}, "overlap": {"agreement": "underpowered"}},
            {"armN": {"valid": True, "activation_reason": "core_gap"}, "overlap": {"agreement": "agree"}},
        ],
    }
    assert v10.select_outcome(scan) == "active_dual_read_gap_resolved"


def test_conflict_precedes_gap_resolution() -> None:
    scan = {
        "active_N_intervals": [{"core_start": 0, "core_end": 0, "active_start": 0, "active_end": 0, "guard": 1}],
        "records": [
            {"armN": {"valid": True, "activation_reason": "core_gap"}, "overlap": {"agreement": "conflict"}},
        ],
    }
    assert v10.select_outcome(scan) == "active_dual_read_handover_conflict"


def test_artifact_schema_contains_telemetry_and_stitched_readback() -> None:
    artifact = json.loads(REPORT_ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["accepted_outcome"] == "active_dual_read_wide_only_no_falloff"
    assert {"primary_scan", "controls", "invariance", "closeout_answers"} <= set(artifact)
    first = artifact["primary_scan"]["records"][0]
    assert {"falloff_state", "falloff_reason", "instrument", "band", "ols_ok"} <= set(first["armW"])
    assert {"active", "valid", "activation_reason", "instrument", "band", "inference"} <= set(first["armN"])
    assert artifact["primary_scan"]["stitched_readback"]


def test_artifact_bytes_are_stable_and_copied() -> None:
    assert REPORT_ARTIFACT.read_bytes() == SCRATCH_ARTIFACT.read_bytes()
    assert v10.artifact_bytes() == REPORT_ARTIFACT.read_bytes()


def test_closeout_answers_required_questions() -> None:
    artifact = json.loads(REPORT_ARTIFACT.read_text(encoding="utf-8"))
    answers = artifact["closeout_answers"]
    required = {
        "armW_produced_below_floor",
        "armN_activated_from_armW_falloff",
        "armN_valid_read_inside_gap",
        "overlap_count",
        "controls_remained_silent",
        "partition_invariance_held",
        "guard_invariance_held",
        "accepted_top_level_outcome",
        "does_not_establish",
        "alpha_minus_one_mission_satisfied",
    }
    assert required <= set(answers)
    assert answers["alpha_minus_one_mission_satisfied"] is False


def test_v7_v8_frozen_sources_are_imported_not_modified() -> None:
    artifact = json.loads(REPORT_ARTIFACT.read_text(encoding="utf-8"))
    reuse = artifact["source_reuse"]
    assert "sweep" in reuse["v7_imported"]
    assert "classify_instrument" in reuse["v8_imported"]
    assert reuse["v7_primitives_copied_or_modified"] is False
    subprocess.run(["git", "diff", "--quiet", "--", "scratch/run_foldreadback_probe0_v7.py", "scratch/foldreadback_probe0_v8_outcomelaw.py"], cwd=ROOT, check=True)
