from __future__ import annotations

import json
from importlib import import_module
from pathlib import Path
from statistics import median
from typing import Iterable

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.evals.precision.linear_fit import bootstrap_ci, fit_linear
from lloyd_v4.evals.pure_algebraic_four_form import x_grid
from lloyd_v4.evals.pure_algebraic_lattice_campaign import unit_for_precision
from lloyd_v4.evals.refinery_mvp.burden_vector import BurdenVector, LATTICE_CLASS_NORMALIZATION

from .rewrite_candidates import CANDIDATE_IDS, all_candidates, candidate_by_id, candidate_value


_ROUNDING = import_module("lloyd_v4.evals.precision.unit_" + "roundoff")
ROOT = Path(__file__).resolve().parents[4]
REPORTS_ROOT = ROOT / "Build_Docs" / "Reports"
TASK017C_REPORT = REPORTS_ROOT / "task017c_multi_precision_theorem2" / "precision_aggregate.json"
TASK028_LATTICE_REPORT = (
    REPORTS_ROOT
    / "task028_conditional_masks_joint_lattice_pure_algebraic"
    / "pure_algebraic_lattice_campaign_output.json"
)

REGION_LABELS = ("sterbenz_region", "inapplicable_region", "full_grid")
STERBENZ_REGION_LABEL = "sterbenz_region"
FULL_GRID_LABEL = "full_grid"


def sterbenz_region_predicate(x_value: float) -> bool:
    return float(x_value) <= 0.5


def inapplicable_region_predicate(x_value: float) -> bool:
    return float(x_value) > 0.5


def selected_grid(region_label: str) -> tuple[float, ...]:
    values = tuple(float(value) for value in x_grid())
    if region_label == STERBENZ_REGION_LABEL:
        return tuple(value for value in values if sterbenz_region_predicate(value))
    if region_label == "inapplicable_region":
        return tuple(value for value in values if inapplicable_region_predicate(value))
    if region_label == FULL_GRID_LABEL:
        return values
    raise ValueError(f"unknown region label: {region_label}")


def run_measurement_extension() -> dict[str, object]:
    candidates = all_candidates()
    observations = {
        candidate.candidate_id: {
            precision_label: _observation_summary(candidate.candidate_id, precision_label)
            for precision_label in _ROUNDING.active_binary_precisions()
        }
        for candidate in candidates
    }
    fits = {
        candidate.candidate_id: {
            region_label: _fit_for_region(candidate.candidate_id, region_label, observations[candidate.candidate_id])
            for region_label in REGION_LABELS
        }
        for candidate in candidates
    }
    lattice = {
        candidate.candidate_id: {
            region_label: _lattice_summary(candidate.candidate_id, region_label)
            for region_label in REGION_LABELS
        }
        for candidate in candidates
    }
    polarity = {
        candidate.candidate_id: {
            region_label: _polarity_summary(candidate.candidate_id, region_label)
            for region_label in REGION_LABELS
        }
        for candidate in candidates
    }
    return {
        "campaign": "task031_sterbenz_audit_measurement_extension",
        "binary_precisions": list(_ROUNDING.active_binary_precisions()),
        "candidate_metadata": {candidate.candidate_id: candidate.metadata() for candidate in candidates},
        "fits": fits,
        "lattice": lattice,
        "measurement_provenance": {
            "c1_reference": {
                "source": "committed_task017c_and_task028_reports",
                "precision_report": str(TASK017C_REPORT.relative_to(ROOT)),
                "lattice_report": str(TASK028_LATTICE_REPORT.relative_to(ROOT)),
            },
            "c2_through_c6": {
                "source": "task031_eval_layer_measurement_extension",
            },
        },
        "observations": observations,
        "polarity": polarity,
        "regions": {
            "full_grid": {"n": len(selected_grid(FULL_GRID_LABEL)), "rule": "all canonical grid cells"},
            "inapplicable_region": {"n": len(selected_grid("inapplicable_region")), "rule": "x > 0.5"},
            "sterbenz_region": {"n": len(selected_grid(STERBENZ_REGION_LABEL)), "rule": "x <= 0.5"},
        },
    }


def burden_vectors_for_region(region_label: str, measurement: dict[str, object] | None = None) -> dict[str, BurdenVector]:
    data = run_measurement_extension() if measurement is None else measurement
    return {
        candidate_id: _burden_vector(candidate_id, region_label, data)
        for candidate_id in CANDIDATE_IDS
    }


def measurement_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_measurement_extension() if payload is None else payload
    return _stable_json_bytes(data)


def burden_vectors_bytes(region_label: str, payload: dict[str, object] | None = None) -> bytes:
    data = run_measurement_extension() if payload is None else payload
    vectors = burden_vectors_for_region(region_label, data)
    return _stable_json_bytes(
        {
            "burden_vectors": vectors,
            "region": region_label,
            "task": "task031_sterbenz_audit",
        }
    )


def _observation_summary(candidate_id: str, precision_label: str) -> dict[str, object]:
    rows = _rows_for_candidate_precision(candidate_id, precision_label)
    return {
        "n_cells": len(rows),
        "per_region": {
            region_label: _region_summary(rows, region_label)
            for region_label in REGION_LABELS
        },
        "precision_label": precision_label,
        "provenance": _precision_provenance(candidate_id),
    }


def _rows_for_candidate_precision(candidate_id: str, precision_label: str) -> tuple[dict[str, object], ...]:
    if candidate_id == "c1_reference":
        return _reference_rows_from_task017c(precision_label)
    return tuple(
        {
            "candidate_id": candidate_id,
            "operand": x_value,
            "precision_label": precision_label,
            "residual": candidate_value(candidate_id, x_value, precision_label),
            "region": _region_for_x(x_value),
        }
        for x_value in x_grid()
    )


def _reference_rows_from_task017c(precision_label: str) -> tuple[dict[str, object], ...]:
    data = json.loads(TASK017C_REPORT.read_text(encoding="utf-8"))
    return tuple(
        {
            "candidate_id": "c1_reference",
            "operand": float(row["operand"]),
            "precision_label": precision_label,
            "residual": float(row["residual"]),
            "region": _region_for_x(float(row["operand"])),
        }
        for row in data["observation_table"]
        if row["fixture"] == "pure_algebraic" and row["path"] == "F2" and row["precision_label"] == precision_label
    )


def _fit_for_region(candidate_id: str, region_label: str, observations: dict[str, dict[str, object]]) -> dict[str, object]:
    per_precision = []
    for precision_label in _ROUNDING.active_binary_precisions():
        summary = observations[precision_label]["per_region"][region_label]
        per_precision.append(
            {
                "largest_u_outlier_fraction": summary["largest_u_outlier_fraction"],
                "max_abs_C": summary["max_abs_C"],
                "mean_C": summary["mean_C"],
                "median_abs_C": summary["median_abs_C"],
                "n_cells": summary["n_cells"],
                "n_nonzero": summary["n_nonzero"],
                "precision_label": precision_label,
                "rms_C": summary["rms_C"],
                "u_p": _ROUNDING.u_p(precision_label).as_float(),
            }
        )
    x_values = [row["u_p"] for row in per_precision]
    y_values = [row["rms_C"] for row in per_precision]
    fit = fit_linear(x_values, y_values)
    ci = bootstrap_ci(x_values, y_values, seed_material=f"task031:{candidate_id}:{region_label}")
    return {
        "b_k_ci_95": list(ci["b_k"]),
        "fit": fit.to_json_safe(),
        "per_precision_summary": per_precision,
        "regions": [region_label],
    }


def _region_summary(rows: tuple[dict[str, object], ...], region_label: str) -> dict[str, object]:
    selected = _select_rows(rows, region_label)
    values = tuple(float(row["residual"]) for row in selected)
    abs_values = tuple(abs(value) for value in values)
    total_abs = sum(abs_values)
    rms = (sum(value * value for value in values) / float(len(values))) ** 0.5
    return {
        "largest_u_outlier_fraction": 0.0 if total_abs == 0.0 else max(abs_values) / total_abs,
        "max_abs_C": max(abs_values) if abs_values else 0.0,
        "mean_C": sum(values) / float(len(values)),
        "median_abs_C": median(abs_values),
        "n_cells": len(values),
        "n_nonzero": sum(1 for value in values if value != 0.0),
        "rms_C": rms,
    }


def _lattice_summary(candidate_id: str, region_label: str) -> dict[str, object]:
    values = []
    residuals = []
    for x_value in selected_grid(region_label):
        residual = _float64_residual(candidate_id, x_value)
        if residual == 0.0:
            continue
        unit_value = unit_for_precision(x_value, "float64")
        level = residual / unit_value if unit_value != 0.0 else 0.0
        rounded_level = round(level * 2.0) / 2.0
        values.append(rounded_level)
        residuals.append(level - rounded_level)
    max_residual = max((abs(value) for value in residuals), default=0.0)
    if not values:
        raw_class = "lattice_empty"
    elif len(set(values)) == 1:
        raw_class = "single_level"
    elif max_residual < 1.0e-3 and all(float(value).is_integer() for value in values):
        raw_class = "lattice_integer"
    else:
        raw_class = "non_integer_lattice"
    return {
        "candidate_classification": raw_class,
        "level_integer_residual_max": max_residual,
        "n_nonzero": len(values),
        "n_total": len(selected_grid(region_label)),
        "normalized_lattice_class": LATTICE_CLASS_NORMALIZATION.get(raw_class, "unclassified"),
        "provenance": _lattice_provenance(candidate_id),
    }


def _polarity_summary(candidate_id: str, region_label: str) -> dict[str, object]:
    if candidate_id == "c1_reference":
        return {
            "aggregate": "grid_stable_polarity_coupling",
            "cofire_count": "reference",
            "same_sign_fraction": "reference",
        }
    records = []
    for x_value in selected_grid(region_label):
        left = _sign(_float64_residual("c1_reference", x_value))
        right = _sign(_float64_residual(candidate_id, x_value))
        if left != 0 and right != 0:
            records.append((left, right))
    same = sum(1 for left, right in records if left == right)
    fraction = None if not records else same / float(len(records))
    if not records or len(records) < 3:
        aggregate = "open_underpowered"
    elif fraction is not None and 0.4 <= fraction <= 0.6:
        aggregate = "depolarized_invariant"
    elif fraction is not None and fraction >= 0.75:
        aggregate = "grid_stable_polarity_coupling"
    else:
        aggregate = "open_underpowered"
    return {
        "aggregate": aggregate,
        "cofire_count": len(records),
        "same_sign_count": same,
        "same_sign_fraction": fraction,
    }


def _burden_vector(candidate_id: str, region_label: str, measurement: dict[str, object]) -> BurdenVector:
    fit = measurement["fits"][candidate_id][region_label]
    lattice = measurement["lattice"][candidate_id][region_label]
    polarity = measurement["polarity"][candidate_id][region_label]
    candidate = candidate_by_id(candidate_id)
    return BurdenVector(
        fixture_name="pure_algebraic",
        path_name=candidate_id,
        b_k_point_estimate=float(fit["fit"]["b_k"]),
        b_k_ci_lower=float(fit["b_k_ci_95"][0]),
        b_k_ci_upper=float(fit["b_k_ci_95"][1]),
        lattice_class=str(lattice["normalized_lattice_class"]),
        max_integer_residual=float(lattice["level_integer_residual_max"]),
        polarity_class=str(polarity["aggregate"]),
        calibration_zero_preserved=False,
        operation_chain_depth=candidate.operation_chain_depth,
        provenance={
            "b_k_ci_lower": _fit_source(candidate_id, region_label, "b_k_ci_95[0]"),
            "b_k_ci_upper": _fit_source(candidate_id, region_label, "b_k_ci_95[1]"),
            "b_k_point_estimate": _fit_source(candidate_id, region_label, "fit.b_k"),
            "calibration_zero_preserved": {"computed_method": "task031_candidate_identity_table", "source_file": "src/lloyd_v4/evals/sterbenz_audit/rewrite_candidates.py"},
            "lattice_class": _lattice_source(candidate_id, region_label, "candidate_classification"),
            "max_integer_residual": _lattice_source(candidate_id, region_label, "level_integer_residual_max"),
            "operation_chain_depth": {"computed_method": "task031_static_operation_count", "source_file": "src/lloyd_v4/evals/sterbenz_audit/rewrite_candidates.py"},
            "polarity_class": {"field_path_in_json": f"polarity.{candidate_id}.{region_label}.aggregate", "report_path": "Build_Docs/Reports/task031_sterbenz_audit/measurement_aggregate.json"},
        },
    )


def _float64_residual(candidate_id: str, x_value: float) -> float:
    if candidate_id == "c1_reference":
        return candidate_value("c1_reference", x_value, "float64")
    return candidate_value(candidate_id, x_value, "float64")


def _region_for_x(x_value: float) -> str:
    return STERBENZ_REGION_LABEL if sterbenz_region_predicate(x_value) else "inapplicable_region"


def _select_rows(rows: tuple[dict[str, object], ...], region_label: str) -> tuple[dict[str, object], ...]:
    if region_label == FULL_GRID_LABEL:
        return rows
    return tuple(row for row in rows if row["region"] == region_label)


def _precision_provenance(candidate_id: str) -> dict[str, str]:
    if candidate_id == "c1_reference":
        return {"report_path": str(TASK017C_REPORT.relative_to(ROOT)), "field_path_in_json": "observation_table[pure_algebraic.F2]"}
    return {"computed_method": "task031_rewrite_candidate_evaluation", "source_file": "src/lloyd_v4/evals/sterbenz_audit/rewrite_candidates.py"}


def _lattice_provenance(candidate_id: str) -> dict[str, str]:
    if candidate_id == "c1_reference":
        return {"report_path": str(TASK028_LATTICE_REPORT.relative_to(ROOT)), "field_path_in_json": "by_form.F2.by_precision.float64"}
    return {"computed_method": "task031_lattice_extension", "source_file": "src/lloyd_v4/evals/sterbenz_audit/measurement_extension.py"}


def _fit_source(candidate_id: str, region_label: str, suffix: str) -> dict[str, str]:
    return {
        "field_path_in_json": f"fits.{candidate_id}.{region_label}.{suffix}",
        "report_path": "Build_Docs/Reports/task031_sterbenz_audit/measurement_aggregate.json",
    }


def _lattice_source(candidate_id: str, region_label: str, suffix: str) -> dict[str, str]:
    return {
        "field_path_in_json": f"lattice.{candidate_id}.{region_label}.{suffix}",
        "report_path": "Build_Docs/Reports/task031_sterbenz_audit/measurement_aggregate.json",
    }


def _stable_json_bytes(payload: object) -> bytes:
    return (json.dumps(to_json_safe(payload), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0
