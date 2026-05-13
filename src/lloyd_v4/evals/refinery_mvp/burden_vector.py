from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_REPORTS_ROOT = ROOT / "Build_Docs" / "Reports"
PRECISION_REPORT = Path("task017c_multi_precision_theorem2") / "precision_aggregate.json"
PURE_LATTICE_REPORT = Path("task028_conditional_masks_joint_lattice_pure_algebraic") / "pure_algebraic_lattice_campaign_output.json"
PURE_POLARITY_REPORT = Path("task028_conditional_masks_joint_lattice_pure_algebraic") / "pure_algebraic_polarity_grid_stability.json"
PURE_FORM_SOURCE = Path("src") / "lloyd_v4" / "evals" / "pure_algebraic_four_form.py"

SENTINELS = {
    "b_k_point_estimate": "b_k_unavailable",
    "b_k_ci_lower": "b_k_ci_lower_unavailable",
    "b_k_ci_upper": "b_k_ci_upper_unavailable",
    "lattice_class": "lattice_class_unavailable",
    "max_integer_residual": "max_integer_residual_unavailable",
    "polarity_class": "polarity_class_unavailable",
    "calibration_zero_preserved": "calibration_zero_preserved_unavailable",
    "operation_chain_depth": "operation_chain_depth_unavailable",
}

LATTICE_CLASS_NORMALIZATION = {
    "lattice_integer": "integer_lattice",
    "single_level": "integer_lattice",
    "non_integer_lattice": "non_integer_lattice",
    "lattice_empty": "unclassified",
}

CALIBRATION_ZERO_BY_PATH = {
    "F1": False,
    "F2": False,
    "F3": True,
    "F4": False,
}

OPERATION_CHAIN_DEPTH_BY_PATH = {
    "F1": 1,
    "F2": 2,
    "F3": 1,
    "F4": 2,
}


@dataclass(frozen=True)
class BurdenVector:
    fixture_name: str
    path_name: str
    b_k_point_estimate: float | str
    b_k_ci_lower: float | str
    b_k_ci_upper: float | str
    lattice_class: str
    max_integer_residual: float | str
    polarity_class: str
    calibration_zero_preserved: bool | str
    operation_chain_depth: int | str
    provenance: dict[str, dict[str, str]]

    def to_json_safe(self) -> dict[str, object]:
        return {
            "b_k_ci_lower": self.b_k_ci_lower,
            "b_k_ci_upper": self.b_k_ci_upper,
            "b_k_point_estimate": self.b_k_point_estimate,
            "calibration_zero_preserved": self.calibration_zero_preserved,
            "fixture_name": self.fixture_name,
            "lattice_class": self.lattice_class,
            "max_integer_residual": self.max_integer_residual,
            "operation_chain_depth": self.operation_chain_depth,
            "path_name": self.path_name,
            "polarity_class": self.polarity_class,
            "provenance": self.provenance,
        }


def extract_burden_vector(
    fixture_name: str,
    path_name: str,
    campaign_reports_root: str | Path = DEFAULT_REPORTS_ROOT,
) -> BurdenVector:
    reports_root = Path(campaign_reports_root)
    values: dict[str, Any] = {field: sentinel for field, sentinel in SENTINELS.items()}
    provenance: dict[str, dict[str, str]] = {}

    _load_b_k_fields(fixture_name, path_name, reports_root, values, provenance)
    _load_lattice_fields(fixture_name, path_name, reports_root, values, provenance)
    _load_polarity_field(fixture_name, path_name, reports_root, values, provenance)
    _load_static_fields(fixture_name, path_name, values, provenance)

    return BurdenVector(
        fixture_name=fixture_name,
        path_name=path_name,
        b_k_point_estimate=values["b_k_point_estimate"],
        b_k_ci_lower=values["b_k_ci_lower"],
        b_k_ci_upper=values["b_k_ci_upper"],
        lattice_class=values["lattice_class"],
        max_integer_residual=values["max_integer_residual"],
        polarity_class=values["polarity_class"],
        calibration_zero_preserved=values["calibration_zero_preserved"],
        operation_chain_depth=values["operation_chain_depth"],
        provenance=provenance,
    )


def _load_b_k_fields(
    fixture_name: str,
    path_name: str,
    reports_root: Path,
    values: dict[str, Any],
    provenance: dict[str, dict[str, str]],
) -> None:
    report_data = _read_json_report(reports_root, PRECISION_REPORT)
    report_path = _report_path(PRECISION_REPORT)
    base_path = f"fits.{fixture_name}.{path_name}.regular_region"
    if not isinstance(report_data, dict):
        _record_absent(provenance, ("b_k_point_estimate", "b_k_ci_lower", "b_k_ci_upper"), report_path, "report_unavailable")
        return
    try:
        node = report_data["fits"][fixture_name][path_name]["regular_region"]
        values["b_k_point_estimate"] = float(node["fit"]["b_k"])
        values["b_k_ci_lower"] = float(node["b_k_ci_95"][0])
        values["b_k_ci_upper"] = float(node["b_k_ci_95"][1])
        provenance["b_k_point_estimate"] = _json_source(report_path, f"{base_path}.fit.b_k")
        provenance["b_k_ci_lower"] = _json_source(report_path, f"{base_path}.b_k_ci_95[0]")
        provenance["b_k_ci_upper"] = _json_source(report_path, f"{base_path}.b_k_ci_95[1]")
    except (KeyError, IndexError, TypeError, ValueError):
        _record_absent(
            provenance,
            ("b_k_point_estimate", "b_k_ci_lower", "b_k_ci_upper"),
            report_path,
            f"{base_path}.missing",
        )


def _load_lattice_fields(
    fixture_name: str,
    path_name: str,
    reports_root: Path,
    values: dict[str, Any],
    provenance: dict[str, dict[str, str]],
) -> None:
    if fixture_name != "pure_algebraic":
        _record_absent(
            provenance,
            ("lattice_class", "max_integer_residual"),
            _report_path(PURE_LATTICE_REPORT),
            "fixture_not_in_pure_algebraic_lattice_report",
        )
        return
    report_data = _read_json_report(reports_root, PURE_LATTICE_REPORT)
    report_path = _report_path(PURE_LATTICE_REPORT)
    base_path = f"by_form.{path_name}.by_precision.float64"
    if not isinstance(report_data, dict):
        _record_absent(provenance, ("lattice_class", "max_integer_residual"), report_path, "report_unavailable")
        return
    try:
        node = report_data["by_form"][path_name]["by_precision"]["float64"]
        values["lattice_class"] = LATTICE_CLASS_NORMALIZATION.get(str(node["candidate_classification"]), "unclassified")
        values["max_integer_residual"] = float(node["level_integer_residual_max"])
        provenance["lattice_class"] = _json_source(report_path, f"{base_path}.candidate_classification")
        provenance["max_integer_residual"] = _json_source(report_path, f"{base_path}.level_integer_residual_max")
    except (KeyError, TypeError, ValueError):
        _record_absent(provenance, ("lattice_class", "max_integer_residual"), report_path, f"{base_path}.missing")


def _load_polarity_field(
    fixture_name: str,
    path_name: str,
    reports_root: Path,
    values: dict[str, Any],
    provenance: dict[str, dict[str, str]],
) -> None:
    if fixture_name != "pure_algebraic":
        provenance["polarity_class"] = {
            "absence_reason": "fixture_not_in_pure_algebraic_polarity_report",
            "report_path": _report_path(PURE_POLARITY_REPORT),
        }
        return
    if path_name not in {"F1", "F2"}:
        values["polarity_class"] = "not_paired"
        provenance["polarity_class"] = {
            "computed_method": "task030_pair_membership",
            "source_file": str(PURE_FORM_SOURCE),
        }
        return
    report_data = _read_json_report(reports_root, PURE_POLARITY_REPORT)
    report_path = _report_path(PURE_POLARITY_REPORT)
    field_path = "aggregate_classifications.F1_F2.aggregate"
    if not isinstance(report_data, dict):
        provenance["polarity_class"] = {"absence_reason": "report_unavailable", "report_path": report_path}
        return
    try:
        values["polarity_class"] = str(report_data["aggregate_classifications"]["F1_F2"]["aggregate"])
        provenance["polarity_class"] = _json_source(report_path, field_path)
    except (KeyError, TypeError):
        provenance["polarity_class"] = {"absence_reason": f"{field_path}.missing", "report_path": report_path}


def _load_static_fields(
    fixture_name: str,
    path_name: str,
    values: dict[str, Any],
    provenance: dict[str, dict[str, str]],
) -> None:
    if fixture_name != "pure_algebraic":
        provenance["calibration_zero_preserved"] = {
            "absence_reason": "fixture_not_in_static_identity_table",
            "source_file": str(PURE_FORM_SOURCE),
        }
        provenance["operation_chain_depth"] = {
            "absence_reason": "fixture_not_in_static_operation_count",
            "source_file": str(PURE_FORM_SOURCE),
        }
        return
    if path_name in CALIBRATION_ZERO_BY_PATH:
        values["calibration_zero_preserved"] = CALIBRATION_ZERO_BY_PATH[path_name]
        provenance["calibration_zero_preserved"] = {
            "computed_method": "task030_path_identity_table",
            "source_file": str(PURE_FORM_SOURCE),
        }
    else:
        provenance["calibration_zero_preserved"] = {
            "absence_reason": "path_not_in_static_identity_table",
            "source_file": str(PURE_FORM_SOURCE),
        }
    if path_name in OPERATION_CHAIN_DEPTH_BY_PATH:
        values["operation_chain_depth"] = OPERATION_CHAIN_DEPTH_BY_PATH[path_name]
        provenance["operation_chain_depth"] = {
            "computed_method": "task030_static_operation_count",
            "source_file": str(PURE_FORM_SOURCE),
        }
    else:
        provenance["operation_chain_depth"] = {
            "absence_reason": "path_not_in_static_operation_count",
            "source_file": str(PURE_FORM_SOURCE),
        }


def _read_json_report(reports_root: Path, relative_path: Path) -> Any:
    report_path = reports_root / relative_path
    try:
        return json.loads(report_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return "json_report_unavailable"


def _json_source(report_path: str, field_path: str) -> dict[str, str]:
    return {"field_path_in_json": field_path, "report_path": report_path}


def _record_absent(
    provenance: dict[str, dict[str, str]],
    field_names: tuple[str, ...],
    report_path: str,
    reason: str,
) -> None:
    for field_name in field_names:
        provenance[field_name] = {"absence_reason": reason, "report_path": report_path}


def _report_path(relative_path: Path) -> str:
    return str(Path("Build_Docs") / "Reports" / relative_path)
