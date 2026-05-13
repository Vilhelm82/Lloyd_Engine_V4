import math
import subprocess
from pathlib import Path

from lloyd_v4.evals.refinery_mvp.burden_vector import SENTINELS, extract_burden_vector
from lloyd_v4.evals.refinery_mvp.geometry_admissibility import check_geometry_admissibility
from lloyd_v4.evals.refinery_mvp.mvp_run import (
    burden_vectors_bytes,
    decision_record_bytes,
    form_metadata,
    headline_bytes,
    run_default_mvp_decision,
)
from lloyd_v4.evals.refinery_mvp.pareto_decision import compare_burden_vectors


ROOT = Path(__file__).resolve().parents[1]
REPORTS_ROOT = ROOT / "Build_Docs" / "Reports"
REPORT_DIR = REPORTS_ROOT / "task030_refinery_mvp"
SUMMARY = REPORTS_ROOT / "task030_refinery_mvp_summary.md"
PRE_REG_COMMIT = "b907d93"
BASELINE_HEAD = "ac545064676578694e1c8771d3a7c64c67024ce5"
BASELINE_TEST_COUNT = 622
NEW_SOURCE_FILES = (
    "src/lloyd_v4/evals/refinery_mvp/__init__.py",
    "src/lloyd_v4/evals/refinery_mvp/geometry_admissibility.py",
    "src/lloyd_v4/evals/refinery_mvp/burden_vector.py",
    "src/lloyd_v4/evals/refinery_mvp/pareto_decision.py",
    "src/lloyd_v4/evals/refinery_mvp/mvp_run.py",
)


def test_required_input_reports_exist() -> None:
    required_reports = (
        REPORTS_ROOT / "task017c_multi_precision_theorem2" / "precision_aggregate.json",
        REPORTS_ROOT / "task029c_cbrt_four_form_battery" / "cbrt_lattice_campaign_output.json",
        REPORTS_ROOT / "task026c_prime_polarity_grid_stability" / "campaign_output.json",
        REPORTS_ROOT
        / "task028_conditional_masks_joint_lattice_pure_algebraic"
        / "pure_algebraic_lattice_campaign_output.json",
        REPORTS_ROOT
        / "task028_conditional_masks_joint_lattice_pure_algebraic"
        / "pure_algebraic_polarity_grid_stability.json",
    )
    for path in required_reports:
        assert path.exists(), path


def test_pre_task_baseline_recorded_in_summary() -> None:
    text = SUMMARY.read_text(encoding="utf-8")
    assert BASELINE_HEAD in text
    assert f"{BASELINE_TEST_COUNT} passing" in text


def test_geometry_admissibility_accepts_f1_candidate_against_f2_reference() -> None:
    result = check_geometry_admissibility(form_metadata("pure_algebraic", "F2"), form_metadata("pure_algebraic", "F1"))
    assert result.status == "admissible"
    assert result.mismatch_field == "none"


def test_geometry_admissibility_rejects_fixture_mismatch() -> None:
    reference = form_metadata("pure_algebraic", "F2")
    candidate = form_metadata("pure_algebraic", "F1")
    candidate["fixture_name"] = "other_fixture"
    result = check_geometry_admissibility(reference, candidate)
    assert result.status == "inadmissible_fixture_mismatch"
    assert result.mismatch_field == "fixture_name"
    assert result.candidate_value == "other_fixture"


def test_geometry_admissibility_records_mismatch_field() -> None:
    reference = form_metadata("pure_algebraic", "F2")
    candidate = form_metadata("pure_algebraic", "F1")
    candidate["operand_grid_label"] = "alternate_grid"
    result = check_geometry_admissibility(reference, candidate)
    assert result.status == "inadmissible_grid_mismatch"
    assert result.mismatch_field == "operand_grid_label"


def test_f1_burden_vector_populates_required_dimensions() -> None:
    vector = extract_burden_vector("pure_algebraic", "F1", REPORTS_ROOT)
    assert vector.b_k_point_estimate == 0.28291099494381716
    assert vector.b_k_ci_lower == 4.058963392730887e-101
    assert vector.b_k_ci_upper == 0.28291099494431743
    assert vector.lattice_class == "integer_lattice"
    assert vector.max_integer_residual == 0.0
    assert vector.polarity_class == "grid_stable_polarity_coupling"
    assert vector.calibration_zero_preserved is False
    assert vector.operation_chain_depth == 1


def test_f2_burden_vector_populates_required_dimensions() -> None:
    vector = extract_burden_vector("pure_algebraic", "F2", REPORTS_ROOT)
    assert vector.b_k_point_estimate == 0.3638034361836378
    assert vector.b_k_ci_lower == 2.727537910596299e-101
    assert vector.b_k_ci_upper == 0.3638034361837702
    assert vector.lattice_class == "non_integer_lattice"
    assert vector.max_integer_residual == 0.25
    assert vector.polarity_class == "grid_stable_polarity_coupling"
    assert vector.calibration_zero_preserved is False
    assert vector.operation_chain_depth == 2


def test_burden_vector_provenance_records_every_dimension() -> None:
    vector = extract_burden_vector("pure_algebraic", "F1", REPORTS_ROOT)
    expected_fields = {
        "b_k_point_estimate",
        "b_k_ci_lower",
        "b_k_ci_upper",
        "lattice_class",
        "max_integer_residual",
        "polarity_class",
        "calibration_zero_preserved",
        "operation_chain_depth",
    }
    assert set(vector.provenance) == expected_fields
    for field_name, source in vector.provenance.items():
        assert "report_path" in source or "source_file" in source
        if field_name in {"calibration_zero_preserved", "operation_chain_depth"}:
            assert "computed_method" in source
        else:
            assert "field_path_in_json" in source


def test_missing_data_uses_typed_sentinels() -> None:
    vector = extract_burden_vector("pure_algebraic", "F99", REPORTS_ROOT)
    data = vector.to_json_safe()
    assert data["b_k_point_estimate"] == SENTINELS["b_k_point_estimate"]
    assert data["lattice_class"] == SENTINELS["lattice_class"]
    assert data["max_integer_residual"] == SENTINELS["max_integer_residual"]
    assert data["calibration_zero_preserved"] == SENTINELS["calibration_zero_preserved"]
    assert data["operation_chain_depth"] == SENTINELS["operation_chain_depth"]
    _assert_no_none_or_nan(data)


def test_f1_candidate_against_f2_reference_produces_accepted_decision() -> None:
    record = run_default_mvp_decision(REPORTS_ROOT)
    assert record.admissibility.status == "admissible"
    assert record.final_outcome == "accepted"
    assert record.match_against_pre_registration is True


def test_comparison_records_per_dimension_breakdown() -> None:
    record = run_default_mvp_decision(REPORTS_ROOT)
    rows = record.comparison.per_dimension
    assert rows["b_k_point_estimate"]["status"] == "tied"
    assert rows["lattice_class"]["status"] == "candidate_better"
    assert rows["max_integer_residual"]["status"] == "candidate_better"
    assert rows["operation_chain_depth"]["status"] == "candidate_better"
    assert rows["polarity_class"]["status"] == "tied"


def test_tied_input_vectors_produce_structural_tie() -> None:
    vector = extract_burden_vector("pure_algebraic", "F1", REPORTS_ROOT)
    result = compare_burden_vectors(vector, vector)
    assert result.outcome == "forms_structurally_tied"


def test_reversed_assignment_rejects_f2_candidate() -> None:
    f1 = extract_burden_vector("pure_algebraic", "F1", REPORTS_ROOT)
    f2 = extract_burden_vector("pure_algebraic", "F2", REPORTS_ROOT)
    result = compare_burden_vectors(f1, f2)
    assert result.outcome == "rejected"


def test_mvp_decision_record_byte_stable() -> None:
    expected = (REPORT_DIR / "mvp_decision_record.json").read_bytes()
    assert decision_record_bytes() == expected
    assert decision_record_bytes() == decision_record_bytes()


def test_burden_vectors_record_byte_stable() -> None:
    expected = (REPORT_DIR / "burden_vectors.json").read_bytes()
    assert burden_vectors_bytes() == expected
    assert burden_vectors_bytes() == burden_vectors_bytes()


def test_headline_classification_byte_stable() -> None:
    expected = (REPORT_DIR / "headline_classification.md").read_bytes()
    assert headline_bytes() == expected
    assert headline_bytes() == headline_bytes()


def test_pre_registration_unchanged_since_pre_registration_commit() -> None:
    committed = subprocess.run(
        ["git", "show", f"{PRE_REG_COMMIT}:Build_Docs/Reports/task030_refinery_mvp/pre_registration.md"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    assert (REPORT_DIR / "pre_registration.md").read_bytes() == committed


def test_no_imports_from_existing_refinery_module() -> None:
    result = subprocess.run(
        ["rg", r"lloyd_v4\.refinery|src/lloyd_v4/refinery|from \.\.\.refinery", *NEW_SOURCE_FILES],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_no_forbidden_imports_in_refinery_mvp_source() -> None:
    result = subprocess.run(
        ["rg", r"scipy|sympy|mpmath|numpy\.special|scipy\.special|statsmodels", *NEW_SOURCE_FILES],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_no_hardcoded_named_math_constants_in_refinery_mvp_source() -> None:
    result = subprocess.run(
        ["rg", r"math\.pi|math\.e|math\.tau|3\.141|2\.718|6\.283", *NEW_SOURCE_FILES],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_no_manifest_changes() -> None:
    paths = ("Build_Docs/Architecture/layer_manifest.json", "Build_Docs/Architecture/LAYER_MANIFEST.md")
    subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=ROOT, check=True)


def test_no_physics_interpretive_language_in_task030_files() -> None:
    report_files = tuple(sorted(path for path in REPORT_DIR.glob("*") if path.is_file())) + (SUMMARY,)
    paths = [ROOT / path for path in NEW_SOURCE_FILES] + [path for path in report_files if path.exists()]
    result = subprocess.run(
        ["rg", r"Kerr|lightspeed|frame dragging|cosmology|relativistic", *[str(path.relative_to(ROOT)) for path in paths]],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def _assert_no_none_or_nan(value: object) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _assert_no_none_or_nan(item)
    elif isinstance(value, list):
        for item in value:
            _assert_no_none_or_nan(item)
    elif isinstance(value, float):
        assert not math.isnan(value)
    else:
        assert value is not None
