"""
Fold-Readback Probe 0 v10 -- active threshold-governed dual-arm probe.

Eval-layer runner only. Imports the frozen v7 mechanics and corrected v8
instrument law; it does not paste or modify them.
"""
from __future__ import annotations

import importlib.util as ilu
import json
import os
from decimal import Decimal
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "foldreadback_probe0_v10_active_dualarm"
SCRATCH_ARTIFACT = ROOT / "scratch" / "foldreadback_probe0_v10_active_dualarm_artifact.json"
REPORT_ARTIFACT = REPORT_DIR / "artifact_v10.json"
CLOSEOUT = REPORT_DIR / "closeout_v10.md"
PREREGISTRY = REPORT_DIR / "preregistry_v10.md"

_D = os.path.dirname(__file__)


def _load(name: str, filename: str):
    spec = ilu.spec_from_file_location(name, os.path.join(_D, filename))
    module = ilu.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V7 = _load("_fr_v7_v10", "run_foldreadback_probe0_v7.py")
LAW = _load("_fr_v8_law_v10", "foldreadback_probe0_v8_outcomelaw.py")

reseat = V7.reseat
fit_ols = V7.fit_ols
sweep = V7.sweep
measure_point = V7.measure_point
binade_exp = V7.binade_exp
DISTRIB = V7.DISTRIB
SCALARS = V7.SCALARS
disc = V7.disc
ols_design_pivot_ok = V7.ols_design_pivot_ok
classify_instrument = LAW.classify_instrument
ANALYTIC_MAX = LAW.ANALYTIC_MAX

MB = 24
MIN_POINTS = 5
CONTEXT_POINTS = 9
CONTEXT_RADIUS = CONTEXT_POINTS // 2
DEFAULT_GUARD = 1
GUARD_VARIANT = 2
ARM_W_FUNCS = ["sign_pattern"]
ARM_N_FUNCS = ["level_histogram", "transition", "signed_occ", "lattice_rank"]
OUTCOMES = {
    "manufactured": "active_dual_read_disqualified_manufactured",
    "partition": "active_dual_read_invalidated_partition_dependence",
    "refused": "active_dual_read_protocol_refused",
    "conflict": "active_dual_read_handover_conflict",
    "resolved": "active_dual_read_gap_resolved",
    "unresolved": "active_dual_read_gap_unresolved",
    "wide_only": "active_dual_read_wide_only_no_falloff",
}


def creg(points: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    return sorted([p for p in points if p["e_f"] < p["e_x"]], key=lambda p: p["f0"])


def point_key(point: dict[str, object]) -> str:
    return str(point["f0"])


def global_rank_map(points: Iterable[dict[str, object]]) -> dict[str, int]:
    return {point_key(point): index for index, point in enumerate(sorted(points, key=lambda p: p["f0"]))}


def anchored_halves(points: Iterable[dict[str, object]], rank_map: dict[str, int], phase: int = 0) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    left: list[dict[str, object]] = []
    right: list[dict[str, object]] = []
    for point in sorted(points, key=lambda p: rank_map[point_key(p)]):
        if (rank_map[point_key(point)] + int(phase)) % 2 == 0:
            left.append(point)
        else:
            right.append(point)
    return left, right


def anchored_nullband(points: Iterable[dict[str, object]], rank_map: dict[str, int], phase: int = 0) -> dict[str, float]:
    half_a, half_b = anchored_halves(points, rank_map, phase)
    bands: dict[str, float] = {}
    for name in list(DISTRIB) + list(SCALARS):
        fn = DISTRIB.get(name) or SCALARS.get(name)
        bands[name] = disc(name, fn([p["L"] for p in half_a]), fn([p["L"] for p in half_b]))
    return bands


def activation_intervals_from_falloff(states: list[str], guard: int = DEFAULT_GUARD) -> list[dict[str, int]]:
    intervals: list[dict[str, int]] = []
    index = 0
    while index < len(states):
        if states[index] != "below_floor":
            index += 1
            continue
        start = index
        while index + 1 < len(states) and states[index + 1] == "below_floor":
            index += 1
        end = index
        intervals.append(
            {
                "core_start": start,
                "core_end": end,
                "active_start": max(0, start - int(guard)),
                "active_end": min(len(states) - 1, end + int(guard)),
                "guard": int(guard),
            }
        )
        index += 1
    return intervals


def activation_reason(index: int, intervals: list[dict[str, int]]) -> str:
    for interval in intervals:
        if interval["core_start"] <= index <= interval["core_end"]:
            return "core_gap"
    for interval in intervals:
        if interval["active_start"] <= index <= interval["active_end"]:
            return "guard"
    return "none"


def arm_w_validity_from_parts(enough_points: bool, instrument: dict[str, str], ols_ok: bool, occupancy_ok: bool) -> bool:
    return bool(enough_points and instrument.get("sign_pattern") == "nondegenerate" and ols_ok and occupancy_ok)


def arm_n_validity_from_parts(enough_points: bool, instrument: dict[str, str]) -> bool:
    return bool(enough_points and any(state == "nondegenerate" for state in instrument.values()))


def select_outcome(
    scan: dict[str, object],
    *,
    controls_silent: bool = True,
    partition_invariant: bool = True,
    guard_invariant: bool = True,
) -> str:
    records = scan.get("records", [])
    intervals = scan.get("active_N_intervals", [])
    if not controls_silent:
        return OUTCOMES["manufactured"]
    if not partition_invariant or not guard_invariant:
        return OUTCOMES["partition"]
    if not records:
        return OUTCOMES["refused"]
    if any(record["overlap"]["agreement"] == "conflict" for record in records):
        return OUTCOMES["conflict"]
    if intervals:
        valid_inside_core = any(record["armN"]["valid"] and record["armN"]["activation_reason"] == "core_gap" for record in records)
        return OUTCOMES["resolved"] if valid_inside_core else OUTCOMES["unresolved"]
    return OUTCOMES["wide_only"]


def _functional_values(points: list[dict[str, object]], funcs: list[str]) -> dict[str, object]:
    values = {}
    levels = [point["L"] for point in points]
    for name in funcs:
        fn = DISTRIB.get(name) or SCALARS.get(name)
        values[name] = fn(levels)
    return values


def _evaluate_functionals(
    reg_a1: list[dict[str, object]],
    reg_a2: list[dict[str, object]],
    funcs: list[str],
    rank_map: dict[str, int],
    phase: int,
) -> tuple[dict[str, str], dict[str, float], dict[str, float], dict[str, str]]:
    nb_a1 = anchored_nullband(reg_a1, rank_map, phase)
    nb_a2 = anchored_nullband(reg_a2, rank_map, phase)
    values_a1 = _functional_values(reg_a1, funcs)
    values_a2 = _functional_values(reg_a2, funcs)
    instrument = {}
    band = {}
    discrepancy = {}
    inference = {}
    for name in funcs:
        band[name] = max(nb_a1[name], nb_a2[name])
        instrument[name] = classify_instrument(name, band[name])
        discrepancy[name] = disc(name, values_a1[name], values_a2[name])
        if instrument[name] == "nondegenerate":
            inference[name] = "separated" if discrepancy[name] > band[name] else "searched_no_separation"
        else:
            inference[name] = "untested"
    return instrument, band, discrepancy, inference


def _aggregate_inference(inference: dict[str, str]) -> str:
    if any(value == "separated" for value in inference.values()):
        return "separated"
    if any(value == "searched_no_separation" for value in inference.values()):
        return "searched_no_separation"
    return "untested"


def _evaluate_arm_w(reg_a1: list[dict[str, object]], reg_a2: list[dict[str, object]], rank_map: dict[str, int], phase: int) -> dict[str, object]:
    enough = len(reg_a1) >= MIN_POINTS and len(reg_a2) >= MIN_POINTS
    if not enough:
        return {
            "active": True,
            "valid": False,
            "falloff_state": "underpopulated",
            "falloff_reason": ["underpopulated"],
            "instrument": {},
            "band": {},
            "discrepancy": {},
            "inference_by_function": {},
            "inference": "untested",
            "ols_ok": False,
            "ols_margin": None,
            "occupancy_ok": False,
        }
    instrument, band, discrepancy, inference = _evaluate_functionals(reg_a1, reg_a2, ARM_W_FUNCS, rank_map, phase)
    ols_ok = bool(ols_design_pivot_ok(reg_a1) and ols_design_pivot_ok(reg_a2))
    occupancy_ok = bool(any(point["L"] != 0 for point in reg_a1) and any(point["L"] != 0 for point in reg_a2))
    valid = arm_w_validity_from_parts(enough, instrument, ols_ok, occupancy_ok)
    reasons = []
    if not ols_ok:
        reasons.append("ols_failed")
    if not occupancy_ok:
        reasons.append("insufficient_occupancy")
    if instrument.get("sign_pattern") != "nondegenerate":
        reasons.append("instrument_" + instrument.get("sign_pattern", "missing"))
    return {
        "active": True,
        "valid": valid,
        "falloff_state": "readable" if valid else "below_floor",
        "falloff_reason": [] if valid else reasons,
        "instrument": instrument,
        "band": band,
        "discrepancy": discrepancy,
        "inference_by_function": inference,
        "inference": _aggregate_inference(inference),
        "ols_ok": ols_ok,
        "ols_margin": None,
        "occupancy_ok": occupancy_ok,
    }


def _assign_warning_and_recovery(records: list[dict[str, object]]) -> None:
    states = [record["armW"]["falloff_state"] for record in records]
    below = {index for index, state in enumerate(states) if state == "below_floor"}
    for index, record in enumerate(records):
        if record["armW"]["falloff_state"] != "readable":
            continue
        if index - 1 in below:
            record["armW"]["falloff_state"] = "recovered"
            record["armW"]["falloff_reason"] = ["readable_after_below_floor"]
        elif index + 1 in below:
            record["armW"]["falloff_state"] = "warning"
            record["armW"]["falloff_reason"] = ["adjacent_to_below_floor"]


def _evaluate_arm_n(
    reg_a1: list[dict[str, object]],
    reg_a2: list[dict[str, object]],
    rank_map: dict[str, int],
    phase: int,
    reason: str,
) -> dict[str, object]:
    if reason == "none":
        return {
            "active": False,
            "valid": False,
            "activation_reason": "none",
            "instrument": {},
            "band": {},
            "discrepancy": {},
            "inference_by_function": {},
            "inference": "untested",
        }
    enough = len(reg_a1) >= MIN_POINTS and len(reg_a2) >= MIN_POINTS
    if not enough:
        return {
            "active": True,
            "valid": False,
            "activation_reason": reason,
            "instrument": {},
            "band": {},
            "discrepancy": {},
            "inference_by_function": {},
            "inference": "untested",
        }
    instrument, band, discrepancy, inference = _evaluate_functionals(reg_a1, reg_a2, ARM_N_FUNCS, rank_map, phase)
    valid = arm_n_validity_from_parts(enough, instrument)
    return {
        "active": True,
        "valid": valid,
        "activation_reason": reason,
        "instrument": instrument,
        "band": band,
        "discrepancy": discrepancy,
        "inference_by_function": inference,
        "inference": _aggregate_inference(inference) if valid else "untested",
    }


def _overlap_record(arm_w: dict[str, object], arm_n: dict[str, object]) -> dict[str, object]:
    both_active = bool(arm_w["active"] and arm_n["active"])
    both_valid = bool(arm_w["valid"] and arm_n["valid"])
    if not both_active:
        agreement = "not_applicable"
    elif not both_valid:
        agreement = "underpowered"
    elif arm_w["inference"] == "searched_no_separation" and arm_n["inference"] == "searched_no_separation":
        agreement = "agree"
    else:
        agreement = "not_comparable"
    return {"both_active": both_active, "both_valid": both_valid, "agreement": agreement}


def run_fixture(a_a1: str, a_a2: str, *, label: str, phase: int = 0, guard: int = DEFAULT_GUARD) -> dict[str, object]:
    sweep_a1, non_a1 = sweep(Decimal(a_a1), MB)
    sweep_a2, non_a2 = sweep(Decimal(a_a2), MB)
    c_a1 = creg(sweep_a1)
    c_a2 = creg(sweep_a2)
    rank_map = global_rank_map(c_a1)
    records = []
    for center in range(len(c_a1)):
        start = max(0, center - CONTEXT_RADIUS)
        end = min(len(c_a1), center + CONTEXT_RADIUS + 1)
        reg_a1 = c_a1[start:end]
        reg_a2 = c_a2[start:end]
        arm_w = _evaluate_arm_w(reg_a1, reg_a2, rank_map, phase)
        records.append(
            {
                "idx": center,
                "center_key": point_key(c_a1[center]),
                "point_count_A1": len(reg_a1),
                "point_count_A2": len(reg_a2),
                "f_min": str(reg_a1[0]["f0"]) if reg_a1 else None,
                "f_max": str(reg_a1[-1]["f0"]) if reg_a1 else None,
                "x_min": str(min(point["x"] for point in reg_a1)) if reg_a1 else None,
                "x_max": str(max(point["x"] for point in reg_a1)) if reg_a1 else None,
                "binades": sorted({point["e_f"] for point in reg_a1}),
                "_reg_a1": reg_a1,
                "_reg_a2": reg_a2,
                "armW": arm_w,
            }
        )
    _assign_warning_and_recovery(records)
    intervals = activation_intervals_from_falloff([record["armW"]["falloff_state"] for record in records], guard)
    for record in records:
        reason = activation_reason(record["idx"], intervals)
        arm_n = _evaluate_arm_n(record["_reg_a1"], record["_reg_a2"], rank_map, phase, reason)
        record["armN"] = arm_n
        record["overlap"] = _overlap_record(record["armW"], arm_n)
        del record["_reg_a1"]
        del record["_reg_a2"]
    stitched = [_stitched_record(record) for record in records]
    scan = {
        "label": label,
        "a_A1": a_a1,
        "a_A2": a_a2,
        "phase": phase,
        "guard": guard,
        "mb": MB,
        "context_points": CONTEXT_POINTS,
        "min_points": MIN_POINTS,
        "observable_points_A1": len(sweep_a1),
        "observable_points_A2": len(sweep_a2),
        "nonobservable_A1": non_a1,
        "nonobservable_A2": non_a2,
        "creg_points_A1": len(c_a1),
        "creg_points_A2": len(c_a2),
        "active_N_intervals": intervals,
        "records": records,
        "stitched_readback": stitched,
    }
    scan["outcome_basis"] = _outcome_basis(scan)
    return scan


def _stitched_record(record: dict[str, object]) -> dict[str, object]:
    channels = []
    if record["armW"]["valid"]:
        channels.append("ARM-W")
    if record["armN"]["valid"]:
        channels.append("ARM-N")
    if not channels:
        channels.append("none")
    return {
        "idx": record["idx"],
        "center_key": record["center_key"],
        "channels": channels,
        "armW_inference": record["armW"]["inference"],
        "armN_inference": record["armN"]["inference"],
        "overlap_agreement": record["overlap"]["agreement"],
    }


def _outcome_basis(scan: dict[str, object]) -> dict[str, object]:
    return {
        "falloff_states": [record["armW"]["falloff_state"] for record in scan["records"]],
        "armW_valid": [record["armW"]["valid"] for record in scan["records"]],
        "armW_inference": [record["armW"]["inference"] for record in scan["records"]],
        "armN_active": [record["armN"]["active"] for record in scan["records"]],
        "armN_valid": [record["armN"]["valid"] for record in scan["records"]],
        "armN_inference": [record["armN"]["inference"] for record in scan["records"]],
        "overlap_agreement": [record["overlap"]["agreement"] for record in scan["records"]],
        "active_N_intervals": scan["active_N_intervals"],
    }


def _control_silent(scan: dict[str, object]) -> bool:
    for record in scan["records"]:
        if record["armW"]["inference"] == "separated":
            return False
        if record["armN"]["active"] and record["armN"]["inference"] == "separated":
            return False
    return True


def _guard_invariant(scan_a: dict[str, object], scan_b: dict[str, object]) -> bool:
    out_a = select_outcome(scan_a)
    out_b = select_outcome(scan_b)
    if out_a == out_b:
        return True
    conflict_set = {OUTCOMES["conflict"]}
    unresolved_pair = {OUTCOMES["resolved"], OUTCOMES["unresolved"]}
    if (out_a in conflict_set) != (out_b in conflict_set):
        return False
    if out_a in unresolved_pair and out_b in unresolved_pair and out_a != out_b:
        return False
    return True


def run_campaign() -> dict[str, object]:
    primary = run_fixture("0.500", "0.501", label="primary", phase=0, guard=DEFAULT_GUARD)
    phase_swap = run_fixture("0.500", "0.501", label="primary_phase_1", phase=1, guard=DEFAULT_GUARD)
    guard_variant = run_fixture("0.500", "0.501", label="primary_guard_2", phase=0, guard=GUARD_VARIANT)
    exact_zero = run_fixture("0.500", "0.500", label="exact_zero_control", phase=0, guard=DEFAULT_GUARD)
    affine = run_fixture("1.000", "1.000", label="matched_affine_control", phase=0, guard=DEFAULT_GUARD)
    controls = {
        "exact_zero": {"silent": _control_silent(exact_zero), "scan": exact_zero},
        "matched_affine": {"silent": _control_silent(affine), "scan": affine},
    }
    partition_ok = primary["outcome_basis"] == phase_swap["outcome_basis"]
    guard_ok = _guard_invariant(primary, guard_variant)
    controls_silent = all(control["silent"] for control in controls.values())
    outcome = select_outcome(primary, controls_silent=controls_silent, partition_invariant=partition_ok, guard_invariant=guard_ok)
    artifact = {
        "probe": "foldreadback_probe0",
        "preregistry": "v10_active_dualarm",
        "source_reuse": {
            "v7_imported": [
                "reseat",
                "fit_ols",
                "sweep",
                "measure_point",
                "binade_exp",
                "DISTRIB",
                "SCALARS",
                "disc",
                "ols_design_pivot_ok",
            ],
            "v8_imported": ["classify_instrument", "ANALYTIC_MAX"],
            "v7_primitives_copied_or_modified": False,
            "v9_overlap_ontology_in_accepted_logic": False,
        },
        "parameters": {
            "armW_functions": ARM_W_FUNCS,
            "armN_functions": ARM_N_FUNCS,
            "context_points": CONTEXT_POINTS,
            "min_points": MIN_POINTS,
            "default_guard": DEFAULT_GUARD,
            "guard_variant": GUARD_VARIANT,
            "partition_phases": [0, 1],
        },
        "primary_scan": primary,
        "controls": controls,
        "invariance": {
            "partition_phase_0_1_match": partition_ok,
            "phase_1_outcome_basis": phase_swap["outcome_basis"],
            "guard_1_2_outcome_safe": guard_ok,
            "guard_2_outcome_basis": guard_variant["outcome_basis"],
        },
        "accepted_outcome": outcome,
        "closeout_verdict": outcome,
    }
    artifact["closeout_answers"] = closeout_answers(artifact)
    return artifact


def artifact_bytes(artifact: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if artifact is None else artifact
    return (json.dumps(data, sort_keys=True, indent=2, default=str, allow_nan=False) + "\n").encode("utf-8")


def closeout_answers(artifact: dict[str, object]) -> dict[str, object]:
    primary = artifact["primary_scan"]
    records = primary["records"]
    intervals = primary["active_N_intervals"]
    overlap_records = [record for record in records if record["overlap"]["both_active"]]
    valid_gap = [record for record in records if record["armN"]["valid"] and record["armN"]["activation_reason"] == "core_gap"]
    return {
        "armW_below_floor_intervals": intervals,
        "armW_produced_below_floor": bool(intervals),
        "armN_activated_from_armW_falloff": any(record["armN"]["active"] for record in records) and bool(intervals),
        "armN_valid_read_inside_gap": bool(valid_gap),
        "overlap_count": len(overlap_records),
        "overlap_agreements": sorted({record["overlap"]["agreement"] for record in overlap_records}) if overlap_records else ["not_applicable"],
        "controls_remained_silent": all(control["silent"] for control in artifact["controls"].values()),
        "partition_invariance_held": artifact["invariance"]["partition_phase_0_1_match"],
        "guard_invariance_held": artifact["invariance"]["guard_1_2_outcome_safe"],
        "accepted_top_level_outcome": artifact["accepted_outcome"],
        "does_not_establish": "alpha-minus-one mission success or fold geometry beyond the predeclared v10 instrument readback.",
        "alpha_minus_one_mission_satisfied": False,
    }


def closeout_markdown(artifact: dict[str, object]) -> str:
    answers = artifact["closeout_answers"]
    lines = [
        "# Fold-Readback Probe 0 v10 Closeout",
        "",
        f"Accepted outcome: `{artifact['accepted_outcome']}`",
        "",
        "## Required Answers",
        "",
        f"1. ARM-W below-floor intervals: `{answers['armW_below_floor_intervals']}`.",
        f"2. ARM-N activated because of ARM-W telemetry: `{answers['armN_activated_from_armW_falloff']}`.",
        f"3. ARM-N valid read inside ARM-W gap: `{answers['armN_valid_read_inside_gap']}`.",
        f"4. Overlap count: `{answers['overlap_count']}`; agreements: `{answers['overlap_agreements']}`.",
        f"5. Exact-zero and affine controls remained silent: `{answers['controls_remained_silent']}`.",
        f"6. Partition invariance held: `{answers['partition_invariance_held']}`; guard invariance held: `{answers['guard_invariance_held']}`.",
        f"7. Accepted top-level outcome: `{answers['accepted_top_level_outcome']}`.",
        f"8. Does not establish: {answers['does_not_establish']}",
        f"9. Alpha-minus-one mission satisfied: `{answers['alpha_minus_one_mission_satisfied']}`.",
        "",
        "## Source Reuse",
        "",
        "- v7 primitives imported, not copied or modified.",
        "- v8 `classify_instrument` and v7-sourced `ANALYTIC_MAX` imported.",
        "- v9 passive overlap ontology is not used in accepted logic.",
        "",
        "## Artifact",
        "",
        "- `scratch/foldreadback_probe0_v10_active_dualarm_artifact.json`",
        "- `Build_Docs/Reports/foldreadback_probe0_v10_active_dualarm/artifact_v10.json`",
        "",
    ]
    return "\n".join(lines)


def write_outputs() -> dict[str, object]:
    artifact = run_campaign()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    data = artifact_bytes(artifact)
    SCRATCH_ARTIFACT.write_bytes(data)
    REPORT_ARTIFACT.write_bytes(data)
    CLOSEOUT.write_text(closeout_markdown(artifact), encoding="utf-8")
    return artifact


def main() -> int:
    artifact = write_outputs()
    print("=== Fold-Readback Probe 0 v10 active dual-arm ===")
    print(f"accepted_outcome={artifact['accepted_outcome']}")
    print(f"saved {SCRATCH_ARTIFACT}")
    print(f"saved {REPORT_ARTIFACT}")
    print(f"saved {CLOSEOUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
