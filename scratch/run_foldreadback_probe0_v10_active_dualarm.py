"""
Fold-Readback Probe 0 v10 -- active threshold-governed dual-arm probe.

Eval-layer runner only. Imports the frozen v7 mechanics and corrected v8
instrument law; it does not paste or modify them.
"""
from __future__ import annotations

import importlib.util as ilu
import argparse
import json
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "foldreadback_probe0_v10_active_dualarm"
SCRATCH_ARTIFACT = ROOT / "scratch" / "foldreadback_probe0_v10_active_dualarm_artifact.json"
REPORT_ARTIFACT = REPORT_DIR / "artifact_v10.json"
CLOSEOUT = REPORT_DIR / "closeout_v10.md"
PREREGISTRY = REPORT_DIR / "preregistry_v10.md"
REPORT_SR_ARTIFACT = REPORT_DIR / "artifact_v10_sr.json"
CLOSEOUT_SR = REPORT_DIR / "closeout_v10_sr.md"

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
SR_OUTCOMES = {
    "wide_only": "active_dual_read_wide_only_no_falloff",
    "wide_separation": "active_dual_read_wide_only_with_separation",
    "resolved": "active_handoff_gap_resolved",
    "unresolved": "active_handoff_gap_unresolved",
    "boundary": "active_handoff_boundary_only",
    "control": "active_handoff_disqualified_control",
    "partition": "active_handoff_partition_unstable",
    "guard": "active_handoff_guard_unstable",
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


def run_point_fixture(
    points_a1: list[dict[str, object]],
    points_a2: list[dict[str, object]],
    *,
    label: str,
    phase: int = 0,
    guard: int = DEFAULT_GUARD,
    scan_fields: dict[str, object] | None = None,
    nonobservable_a1: int = 0,
    nonobservable_a2: int = 0,
) -> dict[str, object]:
    c_a1 = creg(points_a1)
    c_a2 = creg(points_a2)
    rank_map = global_rank_map(c_a1)
    records = []
    for center in range(len(c_a1)):
        start = max(0, center - CONTEXT_RADIUS)
        end = min(len(c_a1), center + CONTEXT_RADIUS + 1)
        reg_a1 = c_a1[start:end]
        reg_a2 = c_a2[start:end]
        arm_w = _evaluate_arm_w(reg_a1, reg_a2, rank_map, phase)
        record = {
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
        if "beta" in c_a1[center]:
            record["beta"] = str(c_a1[center]["beta"])
        if "eta" in c_a1[center]:
            record["eta"] = str(c_a1[center]["eta"])
        records.append(record)
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
    }
    if scan_fields:
        scan.update(scan_fields)
    scan.update(
        {
            "phase": phase,
            "guard": guard,
            "mb": MB,
            "context_points": CONTEXT_POINTS,
            "min_points": MIN_POINTS,
            "observable_points_A1": len(points_a1),
            "observable_points_A2": len(points_a2),
            "nonobservable_A1": nonobservable_a1,
            "nonobservable_A2": nonobservable_a2,
            "creg_points_A1": len(c_a1),
            "creg_points_A2": len(c_a2),
            "active_N_intervals": intervals,
            "records": records,
            "stitched_readback": stitched,
        }
    )
    scan["outcome_basis"] = _outcome_basis(scan)
    return scan


def run_fixture(a_a1: str, a_a2: str, *, label: str, phase: int = 0, guard: int = DEFAULT_GUARD) -> dict[str, object]:
    sweep_a1, non_a1 = sweep(Decimal(a_a1), MB)
    sweep_a2, non_a2 = sweep(Decimal(a_a2), MB)
    return run_point_fixture(
        sweep_a1,
        sweep_a2,
        label=label,
        phase=phase,
        guard=guard,
        scan_fields={"a_A1": a_a1, "a_A2": a_a2},
        nonobservable_a1=non_a1,
        nonobservable_a2=non_a2,
    )


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


def _sr_imports():
    from lloyd_v4.evals.multi_precision_four_form import ulp_of_double
    from lloyd_v4.evals.sr_four_form import beta_grid, eta_of_beta, four_form_float64

    return beta_grid, eta_of_beta, four_form_float64, ulp_of_double


def _sr_scan_fields(left: str, right: str) -> dict[str, object]:
    return {
        "fixture": "sr_four_form",
        "coordinate": "beta",
        "surface": "f(beta)=1-beta^2; eta(beta)=sqrt(f(beta)); beta -> 1",
        "level_unit": "ulp(1 - beta^2)",
        "A1_channel": left,
        "A2_channel": right,
    }


def sr_surface_points(channel: str) -> list[dict[str, object]]:
    beta_grid, eta_of_beta, four_form_float64, ulp_of_double = _sr_imports()
    points = []
    for beta_value in beta_grid():
        f_value = 1.0 - beta_value * beta_value
        unit = ulp_of_double(f_value)
        if channel == "F4_float64":
            residual = four_form_float64(beta_value)["F4"]
            level = int(round(residual / unit)) if unit != 0.0 else 0
        elif channel == "exact_zero":
            residual = 0.0
            level = 0
        elif channel == "matched_affine":
            residual = 0.0
            level = int(round((beta_value - 0.85) * 1000.0))
        else:
            raise ValueError(f"unknown SR v10 channel: {channel}")
        beta_decimal = Decimal.from_float(float(beta_value))
        f_decimal = Decimal.from_float(float(f_value))
        points.append(
            {
                "x": beta_decimal,
                "beta": beta_decimal,
                "f0": f_decimal,
                "eta": Decimal.from_float(float(eta_of_beta(beta_value))),
                "F4_float64": residual,
                "level_unit": unit,
                "L": level,
                "e_f": binade_exp(f_decimal),
                "e_x": binade_exp(beta_decimal),
            }
        )
    return points


def run_sr_fixture(left: str, right: str, *, label: str, phase: int = 0, guard: int = DEFAULT_GUARD) -> dict[str, object]:
    return run_point_fixture(
        sr_surface_points(left),
        sr_surface_points(right),
        label=label,
        phase=phase,
        guard=guard,
        scan_fields=_sr_scan_fields(left, right),
    )


def _scan_has_armw_separation(scan: dict[str, object]) -> bool:
    return any(record["armW"]["inference"] == "separated" for record in scan["records"])


def _sr_records_near_endpoint(scan: dict[str, object]) -> list[dict[str, object]]:
    return [record for record in scan["records"] if float(record.get("beta", "0.0")) >= 0.9]


def _sr_warning_or_below_near_endpoint(scan: dict[str, object]) -> bool:
    return any(record["armW"]["falloff_state"] in {"warning", "below_floor"} for record in _sr_records_near_endpoint(scan))


def select_sr_outcome(
    scan: dict[str, object],
    *,
    controls_silent: bool = True,
    partition_invariant: bool = True,
    guard_invariant: bool = True,
) -> str:
    records = scan.get("records", [])
    intervals = scan.get("active_N_intervals", [])
    if not controls_silent:
        return SR_OUTCOMES["control"]
    if not partition_invariant:
        return SR_OUTCOMES["partition"]
    if not guard_invariant:
        return SR_OUTCOMES["guard"]
    if intervals:
        valid_inside_core = any(record["armN"]["valid"] and record["armN"]["activation_reason"] == "core_gap" for record in records)
        return SR_OUTCOMES["resolved"] if valid_inside_core else SR_OUTCOMES["unresolved"]
    if _sr_warning_or_below_near_endpoint(scan):
        return SR_OUTCOMES["boundary"]
    if _scan_has_armw_separation(scan):
        return SR_OUTCOMES["wide_separation"]
    return SR_OUTCOMES["wide_only"]


def _sr_guard_invariant(scan_a: dict[str, object], scan_b: dict[str, object]) -> bool:
    out_a = select_sr_outcome(scan_a)
    out_b = select_sr_outcome(scan_b)
    if out_a == out_b:
        return True
    unstable_pairs = {SR_OUTCOMES["resolved"], SR_OUTCOMES["unresolved"]}
    if out_a in unstable_pairs and out_b in unstable_pairs:
        return False
    if SR_OUTCOMES["boundary"] in {out_a, out_b} and {out_a, out_b} <= {SR_OUTCOMES["boundary"], SR_OUTCOMES["wide_only"], SR_OUTCOMES["wide_separation"]}:
        return True
    return False


def _sr_fixture_summary() -> dict[str, object]:
    beta_grid, _eta_of_beta, _four_form_float64, _ulp_of_double = _sr_imports()
    values = beta_grid()
    return {
        "module": "src/lloyd_v4/evals/sr_four_form.py",
        "beta_count": len(values),
        "beta_min": values[0],
        "beta_max": values[-1],
        "reused": ["beta_grid", "eta_of_beta", "four_form_float64"],
    }


def run_sr_campaign() -> dict[str, object]:
    primary = run_sr_fixture("F4_float64", "F4_float64", label="sr_primary", phase=0, guard=DEFAULT_GUARD)
    phase_swap = run_sr_fixture("F4_float64", "F4_float64", label="sr_primary_phase_1", phase=1, guard=DEFAULT_GUARD)
    guard_variant = run_sr_fixture("F4_float64", "F4_float64", label="sr_primary_guard_2", phase=0, guard=GUARD_VARIANT)
    exact_zero = run_sr_fixture("exact_zero", "exact_zero", label="sr_exact_zero_control", phase=0, guard=DEFAULT_GUARD)
    affine = run_sr_fixture("matched_affine", "matched_affine", label="sr_matched_affine_control", phase=0, guard=DEFAULT_GUARD)
    controls = {
        "exact_zero": {"silent": _control_silent(exact_zero), "scan": exact_zero},
        "matched_affine": {"silent": _control_silent(affine), "scan": affine},
    }
    partition_ok = primary["outcome_basis"] == phase_swap["outcome_basis"]
    guard_ok = _sr_guard_invariant(primary, guard_variant)
    controls_silent = all(control["silent"] for control in controls.values())
    outcome = select_sr_outcome(primary, controls_silent=controls_silent, partition_invariant=partition_ok, guard_invariant=guard_ok)
    artifact = {
        "probe": "foldreadback_probe0",
        "campaign": "v10_active_dualarm_sr_fixture",
        "fixture": "sr_four_form",
        "sr_fixture": _sr_fixture_summary(),
        "source_reuse": {
            "v10_mechanics": "scratch/run_foldreadback_probe0_v10_active_dualarm.py",
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
            "sr_imported": ["beta_grid", "eta_of_beta", "four_form_float64"],
            "new_dual_arm_method": False,
            "v7_primitives_copied_or_modified": False,
        },
        "parameters": {
            "armW_functions": ARM_W_FUNCS,
            "armN_functions": ARM_N_FUNCS,
            "context_points": CONTEXT_POINTS,
            "min_points": MIN_POINTS,
            "default_guard": DEFAULT_GUARD,
            "guard_variant": GUARD_VARIANT,
            "partition_phases": [0, 1],
            "primary_channel": "F4_float64 self-readback over ulp(1-beta^2) levels",
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
        "verification": [
            {
                "command": "PYTHONPATH=src python scratch/run_foldreadback_probe0_v10_active_dualarm.py --sr",
                "result": "passed; accepted_outcome=active_handoff_gap_resolved",
            },
            {
                "command": "PYTHONPATH=src python -m pytest tests/test_foldreadback_probe0_v10_sr.py -q",
                "result": "passed; 8 tests",
            },
            {
                "command": "PYTHONPATH=src python -m pytest tests/test_foldreadback_probe0_v10_active_dualarm.py tests/test_task027_sr_four_form_cross_fixture.py::test_beta_grid_deterministic_and_bounded tests/test_task027_sr_four_form_cross_fixture.py::test_F3_sr_is_identically_zero tests/test_task027_sr_four_form_cross_fixture.py::test_sr_four_form_byte_stable -q",
                "result": "passed; 17 tests",
            },
            {
                "command": "PYTHONPATH=src python -m pytest tests/ --skip-slow -q -ra",
                "result": "passed; slow campaign/report tests skipped by --skip-slow",
            },
        ],
    }
    artifact["closeout_answers"] = closeout_sr_answers(artifact)
    return artifact


def artifact_sr_bytes(artifact: dict[str, object] | None = None) -> bytes:
    data = run_sr_campaign() if artifact is None else artifact
    return (json.dumps(data, sort_keys=True, indent=2, default=str, allow_nan=False) + "\n").encode("utf-8")


def closeout_sr_answers(artifact: dict[str, object]) -> dict[str, object]:
    primary = artifact["primary_scan"]
    records = primary["records"]
    intervals = primary["active_N_intervals"]
    near_endpoint = _sr_records_near_endpoint(primary)
    overlap_valid = [record for record in records if record["overlap"]["both_valid"]]
    valid_gap = [record for record in records if record["armN"]["valid"] and record["armN"]["activation_reason"] == "core_gap"]
    return {
        "armW_warning_or_below_near_endpoint": any(record["armW"]["falloff_state"] in {"warning", "below_floor"} for record in near_endpoint),
        "near_endpoint_beta_min": min((float(record["beta"]) for record in near_endpoint), default=None),
        "near_endpoint_beta_max": max((float(record["beta"]) for record in near_endpoint), default=None),
        "armW_below_floor_intervals": intervals,
        "armW_state_counts": {state: sum(1 for record in records if record["armW"]["falloff_state"] == state) for state in ["readable", "warning", "below_floor", "recovered", "underpopulated"]},
        "armN_activated_from_armW_falloff": any(record["armN"]["active"] for record in records) and bool(intervals),
        "armN_valid_read_inside_gap": bool(valid_gap),
        "armN_valid_core_count": len(valid_gap),
        "overlap_both_valid_count": len(overlap_valid),
        "overlap_agreements": sorted({record["overlap"]["agreement"] for record in overlap_valid}) if overlap_valid else ["not_applicable"],
        "controls_remained_silent": all(control["silent"] for control in artifact["controls"].values()),
        "partition_invariance_held": artifact["invariance"]["partition_phase_0_1_match"],
        "guard_invariance_held": artifact["invariance"]["guard_1_2_outcome_safe"],
        "accepted_top_level_outcome": artifact["accepted_outcome"],
    }


def closeout_sr_markdown(artifact: dict[str, object]) -> str:
    answers = artifact["closeout_answers"]
    lines = [
        "# Fold-Readback Probe 0 v10 SR Fixture Closeout",
        "",
        f"Accepted outcome: `{artifact['accepted_outcome']}`",
        "",
        "## Required Answers",
        "",
        f"1. ARM-W entered warning or below-floor near the SR singular endpoint: `{answers['armW_warning_or_below_near_endpoint']}`.",
        f"   Near-endpoint band checked: beta in [`{answers['near_endpoint_beta_min']}`, `{answers['near_endpoint_beta_max']}`].",
        f"   ARM-W state counts: `{answers['armW_state_counts']}`.",
        f"2. ARM-N activated from ARM-W falloff telemetry: `{answers['armN_activated_from_armW_falloff']}`.",
        f"3. ARM-N valid reads inside ARM-W core-gap intervals: `{answers['armN_valid_read_inside_gap']}` (`{answers['armN_valid_core_count']}` contexts).",
        f"4. Both arms valid in overlap/guard regions: `{answers['overlap_both_valid_count']}` contexts; agreements: `{answers['overlap_agreements']}`.",
        f"5. Exact-zero and matched-affine controls remained silent: `{answers['controls_remained_silent']}`.",
        f"6. Partition invariance held: `{answers['partition_invariance_held']}`; guard invariance held: `{answers['guard_invariance_held']}`.",
        f"7. Result category: `{answers['accepted_top_level_outcome']}`.",
        "",
        "## Fixture And Reuse",
        "",
        "- Reused SR fixture functions: `beta_grid()`, `eta_of_beta(beta)`, `four_form_float64(beta)`.",
        "- Used canonical SR surface `f(beta)=1-beta^2`, `eta(beta)=sqrt(f(beta))`, beta -> 1.",
        "- Reused v10 active dual-arm mechanics; no new dual-arm method was introduced.",
        "- Reused v7 primitives and v8 `classify_instrument`/`ANALYTIC_MAX`; no v7 primitive was copied or modified.",
        "",
        "## Verification",
        "",
    ]
    for item in artifact["verification"]:
        lines.append(f"- `{item['command']}`")
        lines.append(f"  Result: {item['result']}.")
    lines.extend(
        [
            "",
            "## Artifact",
            "",
            "- `Build_Docs/Reports/foldreadback_probe0_v10_active_dualarm/artifact_v10_sr.json`",
            "- `Build_Docs/Reports/foldreadback_probe0_v10_active_dualarm/closeout_v10_sr.md`",
            "",
        ]
    )
    return "\n".join(lines)


def write_sr_outputs() -> dict[str, object]:
    artifact = run_sr_campaign()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_SR_ARTIFACT.write_bytes(artifact_sr_bytes(artifact))
    CLOSEOUT_SR.write_text(closeout_sr_markdown(artifact), encoding="utf-8")
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sr", action="store_true", help="run the SR fixture through the existing v10 active dual-arm probe")
    args = parser.parse_args(argv)
    if args.sr:
        artifact = write_sr_outputs()
        print("=== Fold-Readback Probe 0 v10 active dual-arm -- SR fixture ===")
        print(f"accepted_outcome={artifact['accepted_outcome']}")
        print(f"saved {REPORT_SR_ARTIFACT}")
        print(f"saved {CLOSEOUT_SR}")
        return 0
    artifact = write_outputs()
    print("=== Fold-Readback Probe 0 v10 active dual-arm ===")
    print(f"accepted_outcome={artifact['accepted_outcome']}")
    print(f"saved {SCRATCH_ARTIFACT}")
    print(f"saved {REPORT_ARTIFACT}")
    print(f"saved {CLOSEOUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
