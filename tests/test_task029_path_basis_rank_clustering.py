import subprocess
from pathlib import Path

from lloyd_v4.core import status as status_module
from lloyd_v4.evals import basis_rank_comparison as comparison
from lloyd_v4.evals import path_catalog as catalog
from lloyd_v4.evals import path_clustering as clustering
from lloyd_v4.evals import path_distance as distance
from lloyd_v4.evals import path_signature as signature
from lloyd_v4.evals.multi_precision_four_form import four_form_decimal_oracle as schwarzschild_decimal
from lloyd_v4.evals.multi_precision_four_form import four_form_float32 as schwarzschild_float32
from lloyd_v4.evals.multi_precision_four_form import four_form_float64 as schwarzschild_float64
from lloyd_v4.evals.path_law_discovery import build_candidate_library
from lloyd_v4.evals.pure_algebraic_four_form import four_form_decimal_oracle as pure_decimal
from lloyd_v4.evals.pure_algebraic_four_form import four_form_float32 as pure_float32
from lloyd_v4.evals.pure_algebraic_four_form import four_form_float64 as pure_float64
from lloyd_v4.evals.sr_four_form import four_form_decimal_oracle as sr_decimal
from lloyd_v4.evals.sr_four_form import four_form_float32 as sr_float32
from lloyd_v4.evals.sr_four_form import four_form_float64 as sr_float64


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports"
TASK027_DIR = REPORT_DIR / "task027_sr_four_form_cross_fixture"
TASK028_DIR = REPORT_DIR / "task028_conditional_masks_joint_lattice_pure_algebraic"


def _status_values() -> set[str]:
    values: set[str] = set()
    for enum_type in status_module.StatusCode.__args__:
        values.update(item.value for item in enum_type)
    return values


def _paths_for_fixture(fixture: str) -> tuple[catalog.CandidatePath, ...]:
    return tuple(path for path in catalog.all_candidate_paths() if path.fixture == fixture)


def _anchor_expected(fixture: str, precision: str, operand: float) -> dict[str, float]:
    if fixture == "schwarzschild":
        if precision == "float32":
            return schwarzschild_float32(operand)
        if precision == "float64":
            return schwarzschild_float64(operand)
        return schwarzschild_decimal(operand, 50)
    if fixture == "sr":
        if precision == "float32":
            return sr_float32(operand)
        if precision == "float64":
            return sr_float64(operand)
        return sr_decimal(operand, 50)
    if precision == "float32":
        return pure_float32(operand)
    if precision == "float64":
        return pure_float64(operand)
    return pure_decimal(operand, 50)


def _evaluate(path: catalog.CandidatePath, precision: str, operand: float) -> float:
    if precision == "float32":
        return catalog.evaluate_path_float32(path, operand)
    if precision == "float64":
        return catalog.evaluate_path_float64(path, operand)
    return catalog.evaluate_path_decimal_oracle(path, operand, 50)


def test_candidate_catalog_completeness() -> None:
    for fixture in catalog.FIXTURES:
        paths = _paths_for_fixture(fixture)
        assert len(paths) == 15
        assert {path.rewrite_class for path in paths} == set(catalog.REWRITE_CLASSES)
        assert {path.label for path in paths} == {
            "F1",
            "F2",
            "F3",
            "F4",
            "P_sign_a",
            "P_sign_b",
            "P_sign_c",
            "P_factor_b",
            "P_diff_squares",
            "P_scaled_2",
            "P_scaled_half",
            "P_distrib_mul",
            "P_distrib_sqrt_mul",
            "P_compound_split",
            "P_compound_zero",
        }


def test_candidate_catalog_byte_stable() -> None:
    assert catalog.catalog_bytes() == catalog.catalog_bytes()


def test_canonical_anchors_recover_existing_forms() -> None:
    for fixture in catalog.FIXTURES:
        operands = signature.canonical_operands(fixture)
        anchors = {path.label: path for path in _paths_for_fixture(fixture) if path.label in clustering.ANCHORS}
        for operand in operands:
            for precision in signature.PRECISIONS:
                expected = _anchor_expected(fixture, precision, operand)
                for label, path in anchors.items():
                    assert _evaluate(path, precision, operand) == expected[label]


def test_F3_anchor_silent_in_catalog() -> None:
    for fixture in catalog.FIXTURES:
        path = next(path for path in _paths_for_fixture(fixture) if path.label == "F3")
        for operand in signature.canonical_operands(fixture):
            for precision in signature.PRECISIONS:
                assert _evaluate(path, precision, operand) == 0.0


def test_all_candidates_finite_or_nan_documented() -> None:
    for path in catalog.all_candidate_paths():
        for operand in signature.canonical_operands(path.fixture):
            for precision in signature.PRECISIONS:
                value = _evaluate(path, precision, operand)
                assert value == value
                assert value not in (float("inf"), float("-inf"))


def test_signature_schema_complete() -> None:
    for fixture in catalog.FIXTURES:
        for item in signature.compute_all_signatures(fixture):
            assert len(item.zero_mask_fingerprint) == 411
            assert isinstance(item.signed_lattice_histogram, dict)
            assert len(item.precision_scaling) == 3
            assert len(item.alpha_status_at_characteristic) == 5
            assert set(item.cofire_polarity_with_canonical) == set(clustering.ANCHORS)
            assert len(item.envelope_shape) == 4


def test_signature_byte_stable() -> None:
    assert signature.signature_bytes() == signature.signature_bytes()


def test_signature_anchor_self_distance_zero() -> None:
    for fixture in catalog.FIXTURES:
        signatures = {item.path_label: item for item in signature.compute_all_signatures(fixture)}
        for anchor in clustering.ANCHORS:
            assert distance.composite_distance(signatures[anchor], signatures[anchor]) == 0.0


def test_signature_anchor_pairwise_distances_nonzero() -> None:
    for fixture in catalog.FIXTURES:
        signatures = {item.path_label: item for item in signature.compute_all_signatures(fixture)}
        for index, left in enumerate(clustering.ANCHORS):
            for right in clustering.ANCHORS[index + 1 :]:
                assert distance.composite_distance(signatures[left], signatures[right]) > 0.0


def test_F3_distinct_from_F1_F2_F4() -> None:
    for fixture in catalog.FIXTURES:
        signatures = {item.path_label: item for item in signature.compute_all_signatures(fixture)}
        for anchor in ("F1", "F2", "F4"):
            assert distance.composite_distance(signatures["F3"], signatures[anchor]) > 0.5


def test_composite_distance_is_simple_mean() -> None:
    signatures = {item.path_label: item for item in signature.compute_all_signatures("pure_algebraic")}
    left = signatures["F1"]
    right = signatures["F2"]
    components = (
        distance.zero_mask_distance(left, right),
        distance.signed_lattice_distance(left, right) / 2.0,
        distance.precision_scaling_distance(left, right),
        distance.alpha_status_distance(left, right),
        distance.cofire_polarity_distance(left, right),
        min(distance.envelope_shape_distance(left, right) / 2.0, 1.0),
    )
    assert distance.composite_distance(left, right) == sum(components) / 6.0


def test_pairwise_distance_matrix_symmetric() -> None:
    for fixture in catalog.FIXTURES:
        signatures = list(signature.compute_all_signatures(fixture))
        matrix = distance.compute_pairwise_distance_matrix(signatures)
        for row_index, row in enumerate(matrix):
            for col_index, value in enumerate(row):
                assert value == matrix[col_index][row_index]


def test_pairwise_distance_matrix_diagonal_zero() -> None:
    for fixture in catalog.FIXTURES:
        signatures = list(signature.compute_all_signatures(fixture))
        matrix = distance.compute_pairwise_distance_matrix(signatures)
        for index in range(len(matrix)):
            assert matrix[index][index] == 0.0


def test_clustering_byte_stable() -> None:
    assert clustering.clustering_bytes() == clustering.clustering_bytes()


def test_clustering_at_threshold_zero_no_merges() -> None:
    signatures = []
    labels = []
    for fixture in catalog.FIXTURES:
        for item in signature.compute_all_signatures(fixture):
            signatures.append(item)
            labels.append(f"{fixture}:{item.path_label}")
    matrix = distance.compute_pairwise_distance_matrix(signatures)
    assignment = clustering.hierarchical_cluster_single_linkage(matrix, tuple(labels), 0.0)
    assert assignment.cluster_count == 45


def test_clustering_at_threshold_one_one_cluster() -> None:
    for fixture in catalog.FIXTURES:
        signatures = list(signature.compute_all_signatures(fixture))
        labels = tuple(item.path_label for item in signatures)
        matrix = distance.compute_pairwise_distance_matrix(signatures)
        assignment = clustering.hierarchical_cluster_single_linkage(matrix, labels, 1.0)
        assert assignment.cluster_count == 1


def test_F1_F4_self_consistency_per_fixture() -> None:
    output = clustering.run_basis_rank_campaign()
    for fixture in catalog.FIXTURES:
        assignment = next(item for item in output["fixture_results"][fixture]["assignments_by_cut"] if item["cut_threshold"] == 0.10)
        assert assignment["f1_f4_self_consistent"] is True


def test_sensitivity_threshold_table_complete() -> None:
    output = clustering.run_basis_rank_campaign()
    for fixture in catalog.FIXTURES:
        cuts = {item["cut_threshold"] for item in output["fixture_results"][fixture]["assignments_by_cut"]}
        assert cuts == {0.05, 0.10, 0.15, 0.20}


def test_basis_rank_comparison_byte_stable() -> None:
    assert comparison.comparison_bytes() == comparison.comparison_bytes()


def test_basis_rank_comparison_schema() -> None:
    output = comparison.compare_basis_rank_across_fixtures()
    assert {"per_fixture", "headline_classification", "f5_rewrite_class_sets"} <= set(output)
    assert output["headline_classification"] in {
        "basis_rank_4_invariant",
        "basis_rank_5_invariant",
        "basis_rank_divergent",
        "basis_rank_methodology_compromised",
    }
    for fixture in catalog.FIXTURES:
        assert {"basis_rank", "candidate_F5_paths", "f1_f4_self_consistent"} <= set(output["per_fixture"][fixture])


def test_no_runtime_status_enum_additions() -> None:
    before = _status_values()
    import lloyd_v4.evals.path_catalog  # noqa: F401
    import lloyd_v4.evals.path_signature  # noqa: F401
    import lloyd_v4.evals.path_distance  # noqa: F401
    import lloyd_v4.evals.path_clustering  # noqa: F401
    import lloyd_v4.evals.basis_rank_comparison  # noqa: F401

    after = _status_values()
    assert after == before


def test_no_law_library_term_added() -> None:
    before = tuple(term.term_id for term in build_candidate_library())
    import lloyd_v4.evals.path_catalog  # noqa: F401

    after = tuple(term.term_id for term in build_candidate_library())
    assert after == before
    assert len(after) == 17


def test_no_manifest_changes() -> None:
    paths = ("Build_Docs/Architecture/layer_manifest.json", "Build_Docs/Architecture/LAYER_MANIFEST.md")
    subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=ROOT, check=True)


def test_no_clustering_library_imported() -> None:
    paths = [
        "src/lloyd_v4/evals/path_catalog.py",
        "src/lloyd_v4/evals/path_signature.py",
        "src/lloyd_v4/evals/path_distance.py",
        "src/lloyd_v4/evals/path_clustering.py",
        "src/lloyd_v4/evals/basis_rank_comparison.py",
    ]
    result = subprocess.run(
        ["rg", "scipy\\.cluster|sklearn\\.cluster|scipy\\.spatial\\.distance", *paths],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_existing_campaign_outputs_unchanged() -> None:
    paths = tuple(sorted(TASK027_DIR.glob("*.json"))) + tuple(sorted(TASK028_DIR.glob("*.json")))
    before = {path: path.read_bytes() for path in paths}
    catalog.write_catalog_output(REPORT_DIR / "task029_path_basis_rank_clustering" / "candidate_path_catalog.json")
    signature.write_signatures_output(REPORT_DIR / "task029_path_basis_rank_clustering" / "path_signatures.json")
    distance.write_distance_output(REPORT_DIR / "task029_path_basis_rank_clustering" / "pairwise_distance_matrices.json")
    clustering.write_basis_rank_output(REPORT_DIR / "task029_path_basis_rank_clustering" / "basis_rank_clustering.json")
    comparison.write_basis_rank_comparison(REPORT_DIR / "task029_path_basis_rank_clustering" / "basis_rank_comparison.json")
    after = {path: path.read_bytes() for path in paths}
    assert after == before
