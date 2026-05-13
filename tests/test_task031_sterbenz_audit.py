import math
import re
import subprocess
from pathlib import Path

import pytest

from lloyd_v4.evals.pure_algebraic_four_form import four_form_float64, x_grid
from lloyd_v4.evals.refinery_mvp.burden_vector import BurdenVector
from lloyd_v4.evals.sterbenz_audit import audit_run, measurement_extension as measurement
from lloyd_v4.evals.sterbenz_audit.n_way_pareto import compute_pareto_frontier
from lloyd_v4.evals.sterbenz_audit.rewrite_candidates import (
    CANDIDATE_IDS,
    DECIMAL_EMULATED_UNSUPPORTED_MESSAGE,
    candidate_by_id,
    candidate_value,
    precision_spec,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task031_sterbenz_audit"
SUMMARY = ROOT / "Build_Docs" / "Reports" / "task031_sterbenz_audit_summary.md"
PRE_REG_COMMIT = "4c97759"
BASELINE_HEAD = "d7a846658f4bd9144f69620cedbb3a70cb01292c"
BASELINE_TEST_COUNT = 644
NEW_SOURCE_FILES = (
    "src/lloyd_v4/evals/sterbenz_audit/__init__.py",
    "src/lloyd_v4/evals/sterbenz_audit/rewrite_candidates.py",
    "src/lloyd_v4/evals/sterbenz_audit/measurement_extension.py",
    "src/lloyd_v4/evals/sterbenz_audit/n_way_pareto.py",
    "src/lloyd_v4/evals/sterbenz_audit/audit_run.py",
)


def test_task030_commit_is_ancestor_of_head() -> None:
    subprocess.run(["git", "merge-base", "--is-ancestor", "d7a8466", "HEAD"], cwd=ROOT, check=True)
    subprocess.run(["git", "merge-base", "--is-ancestor", "d7a8466", "origin/main"], cwd=ROOT, check=True)


def test_required_prior_reports_exist() -> None:
    required = (
        "task017c_multi_precision_theorem2/precision_aggregate.json",
        "task026c_prime_polarity_grid_stability/campaign_output.json",
        "task028_conditional_masks_joint_lattice_pure_algebraic/pure_algebraic_lattice_campaign_output.json",
        "task029c_cbrt_four_form_battery/cbrt_lattice_campaign_output.json",
        "task030_refinery_mvp/mvp_decision_record.json",
        "task030_refinery_mvp/burden_vectors.json",
    )
    for relative in required:
        assert (ROOT / "Build_Docs" / "Reports" / relative).exists(), relative


def test_pre_task_baseline_recorded_in_summary() -> None:
    text = SUMMARY.read_text(encoding="utf-8")
    assert BASELINE_HEAD in text
    assert f"{BASELINE_TEST_COUNT} passing" in text


@pytest.mark.parametrize("candidate_id", CANDIDATE_IDS)
def test_candidate_float64_values_are_finite(candidate_id: str) -> None:
    for value in x_grid():
        residual = candidate_value(candidate_id, value, "float64")
        assert math.isfinite(residual)


def test_reference_candidate_matches_pure_algebraic_f2() -> None:
    for value in x_grid():
        assert candidate_value("c1_reference", value, "float64") == four_form_float64(value)["F2"]


def test_power_operator_is_bit_identical_to_reference() -> None:
    for value in x_grid():
        assert candidate_value("c4_power_operator", value, "float64") == candidate_value("c1_reference", value, "float64")


def test_identity_padded_is_bit_identical_to_reference() -> None:
    for value in x_grid():
        assert candidate_value("c5_identity_padded", value, "float64") == candidate_value("c1_reference", value, "float64")


def test_factored_candidate_has_cancellation_signal() -> None:
    pairs = [
        (abs(candidate_value("c1_reference", value, "float64")), abs(candidate_value("c3_factored", value, "float64")))
        for value in x_grid()
    ]
    assert any(reference == 0.0 and factored != 0.0 for reference, factored in pairs)


def test_decimal_emulated_rejects_decimal_output_precision() -> None:
    with pytest.raises(NotImplementedError, match=re.escape(DECIMAL_EMULATED_UNSUPPORTED_MESSAGE)):
        candidate_by_id("c6_decimal_emulated").evaluate(0.5, precision_spec("decimal_50"))


def test_measurement_extension_records_precision_fits_for_new_candidates() -> None:
    output = measurement.run_measurement_extension()
    for candidate_id in CANDIDATE_IDS[1:]:
        for precision_label in output["binary_precisions"]:
            row = output["observations"][candidate_id][precision_label]
            assert row["per_region"]["sterbenz_region"]["n_cells"] > 0
        fit = output["fits"][candidate_id]["sterbenz_region"]["fit"]
        assert {"a_k", "b_k", "r_squared", "residuals"} <= set(fit)


def test_measurement_extension_records_lattice_for_new_candidates() -> None:
    output = measurement.run_measurement_extension()
    for candidate_id in CANDIDATE_IDS[1:]:
        lattice = output["lattice"][candidate_id]["sterbenz_region"]
        assert lattice["normalized_lattice_class"] in {"integer_lattice", "non_integer_lattice", "unclassified"}
        assert lattice["level_integer_residual_max"] is not None


def test_measurement_extension_records_polarity_pairing_for_new_candidates() -> None:
    output = measurement.run_measurement_extension()
    for candidate_id in CANDIDATE_IDS[1:]:
        polarity = output["polarity"][candidate_id]["sterbenz_region"]
        assert polarity["aggregate"] in {"grid_stable_polarity_coupling", "depolarized_invariant", "open_underpowered"}


def test_reference_measurements_are_sourced_from_existing_reports() -> None:
    output = measurement.run_measurement_extension()
    source = output["measurement_provenance"]["c1_reference"]
    assert source["source"] == "committed_task017c_and_task028_reports"
    assert "task017c_multi_precision_theorem2/precision_aggregate.json" in source["precision_report"]


def test_synthetic_frontier_with_one_dominated_candidate() -> None:
    vectors = [_synthetic_vector("a", 1.0, 0.0, 1), _synthetic_vector("b", 1.0, 0.0, 1), _synthetic_vector("c", 2.0, 0.25, 2)]
    result = compute_pareto_frontier(vectors)
    assert result.frontier_members == ["a", "b"]
    assert result.dominated_candidates["c"] == ["a", "b"]


def test_synthetic_frontier_all_tied() -> None:
    vectors = [_synthetic_vector("a", 1.0, 0.0, 1), _synthetic_vector("b", 1.0, 0.0, 1)]
    result = compute_pareto_frontier(vectors)
    assert result.frontier_members == ["a", "b"]
    assert result.pairwise_dominance["a"]["b"]["outcome"] == "forms_structurally_tied"


def test_synthetic_frontier_all_incomparable() -> None:
    vectors = [
        _synthetic_vector("a", 1.0, 0.25, 1),
        _synthetic_vector("b", 2.0, 0.0, 2),
    ]
    result = compute_pareto_frontier(vectors)
    assert result.frontier_members == ["a", "b"]
    assert result.incomparable_pairs == [["a", "b"]]


def test_pairwise_dominance_matrix_is_symmetric_in_interpretation() -> None:
    vectors = [_synthetic_vector("a", 1.0, 0.0, 1), _synthetic_vector("b", 2.0, 0.25, 2)]
    result = compute_pareto_frontier(vectors)
    assert result.pairwise_dominance["a"]["b"]["outcome"] == "rejected"
    assert result.pairwise_dominance["b"]["a"]["outcome"] == "accepted"


def test_pairwise_result_records_each_pair() -> None:
    result = compute_pareto_frontier([_synthetic_vector("a", 1.0, 0.0, 1), _synthetic_vector("b", 2.0, 0.25, 2)])
    assert set(result.pairwise_dominance) == {"a", "b"}
    assert set(result.pairwise_dominance["a"]) == {"a", "b"}
    assert set(result.pairwise_dominance["b"]) == {"a", "b"}


def test_sterbenz_region_subset_uses_inclusive_boundary() -> None:
    values = measurement.selected_grid("sterbenz_region")
    assert all(value <= 0.5 for value in values)
    assert 0.5 in values


def test_inapplicable_region_subset_is_strictly_above_boundary() -> None:
    values = measurement.selected_grid("inapplicable_region")
    assert values
    assert all(value > 0.5 for value in values)


def test_region_restriction_changes_at_least_one_burden_vector() -> None:
    output = measurement.run_measurement_extension()
    region_vectors = measurement.burden_vectors_for_region("sterbenz_region", output)
    full_vectors = measurement.burden_vectors_for_region("full_grid", output)
    assert any(
        region_vectors[candidate_id].to_json_safe()["b_k_point_estimate"]
        != full_vectors[candidate_id].to_json_safe()["b_k_point_estimate"]
        for candidate_id in CANDIDATE_IDS
    )


def test_grid_contains_boundary_cell() -> None:
    assert 0.5 in x_grid()


def test_sterbenz_audit_headline_and_frontier() -> None:
    result = audit_run.run_sterbenz_audit()
    assert result.headline_classification == "sterbenz_dominated_by_alternative"
    assert result.frontier.frontier_members == ["c2_reassociated"]
    assert "c1_reference" in result.frontier.dominated_candidates


def test_calibration_factored_candidate_is_off_frontier() -> None:
    result = audit_run.run_sterbenz_audit()
    assert "c3_factored" not in result.frontier.frontier_members
    assert "c3_factored" in result.frontier.dominated_candidates


def test_decimal_emulated_candidate_position_recorded() -> None:
    result = audit_run.run_sterbenz_audit()
    assert "c6_decimal_emulated" in result.frontier.dominated_candidates
    assert "c2_reassociated" in result.frontier.dominated_candidates["c6_decimal_emulated"]


def test_c2_region_swap_recorded_as_refuted_in_sterbenz_region_and_tied_above_boundary() -> None:
    result = audit_run.run_sterbenz_audit()
    assert result.region_comparison["sterbenz_region"]["frontier_members"] == ["c2_reassociated"]
    assert result.region_comparison["inapplicable_region"]["frontier_members"] == ["c1_reference", "c2_reassociated"]


def test_measurement_aggregate_byte_stable() -> None:
    assert measurement.measurement_bytes() == (REPORT_DIR / "measurement_aggregate.json").read_bytes()
    assert measurement.measurement_bytes() == measurement.measurement_bytes()


def test_sterbenz_region_burden_vectors_byte_stable() -> None:
    assert measurement.burden_vectors_bytes("sterbenz_region") == (REPORT_DIR / "sterbenz_region_burden_vectors.json").read_bytes()
    assert measurement.burden_vectors_bytes("sterbenz_region") == measurement.burden_vectors_bytes("sterbenz_region")


def test_full_grid_burden_vectors_byte_stable() -> None:
    assert measurement.burden_vectors_bytes("full_grid") == (REPORT_DIR / "full_grid_burden_vectors.json").read_bytes()


def test_pareto_frontier_and_headline_byte_stable() -> None:
    assert audit_run.pareto_frontier_bytes() == (REPORT_DIR / "pareto_frontier.json").read_bytes()
    assert audit_run.headline_bytes() == (REPORT_DIR / "headline_classification.md").read_bytes()


def test_pre_registration_unchanged_since_pre_registration_commit() -> None:
    committed = subprocess.run(
        ["git", "show", f"{PRE_REG_COMMIT}:Build_Docs/Reports/task031_sterbenz_audit/pre_registration.md"],
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


def test_no_forbidden_imports_or_patterns() -> None:
    result = subprocess.run(
        ["rg", r"math\.fma|math\.cbrt|cmath|scipy|sympy|mpmath|statsmodels|numpy\.special|numpy\.random", *NEW_SOURCE_FILES],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_no_hardcoded_named_math_constants() -> None:
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


def test_no_physics_interpretive_language_in_task031_files() -> None:
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


def test_typed_finite_difference_source_unchanged() -> None:
    current = (ROOT / "src/lloyd_v4/primitives/typed_finite_difference.py").read_bytes()
    baseline = subprocess.run(
        ["git", "show", f"{BASELINE_HEAD}:src/lloyd_v4/primitives/typed_finite_difference.py"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    assert current == baseline


def _synthetic_vector(candidate_id: str, b_value: float, residual: float, chain_depth: int) -> BurdenVector:
    return BurdenVector(
        fixture_name="synthetic",
        path_name=candidate_id,
        b_k_point_estimate=b_value,
        b_k_ci_lower=b_value,
        b_k_ci_upper=b_value,
        lattice_class="integer_lattice",
        max_integer_residual=residual,
        polarity_class="grid_stable_polarity_coupling",
        calibration_zero_preserved=False,
        operation_chain_depth=chain_depth,
        provenance={},
    )
