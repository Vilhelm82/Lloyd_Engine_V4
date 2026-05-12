import subprocess
from pathlib import Path

from lloyd_v4.core import status as status_module
from lloyd_v4.evals import decimal_scaled_form_audit as decimal_audit
from lloyd_v4.evals import refined_f5_report as refined
from lloyd_v4.evals import scale_invariant_clustering as scale_cluster
from lloyd_v4.evals import scale_invariant_signature as scale_sig
from lloyd_v4.evals import sqrt_roundtrip_residual as sqrt_residual
from lloyd_v4.evals.path_catalog import FIXTURES
from lloyd_v4.evals.path_law_discovery import build_candidate_library


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "Build_Docs" / "Reports"
TASK029B = REPORTS / "task029b_methodology_refinement"
TASK029_MODULES = (
    "src/lloyd_v4/evals/path_catalog.py",
    "src/lloyd_v4/evals/path_signature.py",
    "src/lloyd_v4/evals/path_distance.py",
    "src/lloyd_v4/evals/path_clustering.py",
    "src/lloyd_v4/evals/basis_rank_comparison.py",
)


def _status_values() -> set[str]:
    values: set[str] = set()
    for enum_type in status_module.StatusCode.__args__:
        values.update(item.value for item in enum_type)
    return values


def _all_frozen_json_paths() -> tuple[Path, ...]:
    dirs = (
        REPORTS / "task026c_prime_polarity_grid_stability",
        REPORTS / "task027_sr_four_form_cross_fixture",
        REPORTS / "task028_conditional_masks_joint_lattice_pure_algebraic",
        REPORTS / "task029_path_basis_rank_clustering",
    )
    return tuple(path for directory in dirs for path in sorted(directory.glob("*.json")))


def test_scale_invariant_signature_schema() -> None:
    output = scale_sig.run_scale_invariant_signature_campaign()
    for item in output["signatures"]:
        assert len(item["zero_mask_fingerprint"]) == 411
        assert isinstance(item["signed_lattice_histogram"], dict)
        assert len(item["precision_scaling"]) == 3
        assert len(item["alpha_status_at_characteristic"]) == 5
        assert set(item["cofire_polarity_with_canonical"]) == {"F1", "F2", "F3", "F4"}
        assert len(item["envelope_shape"]) == 4
        for key in item["signed_lattice_histogram"]:
            assert ":L=" in key and ":S=" in key


def test_scale_invariant_signatures_byte_stable() -> None:
    assert scale_sig.scale_invariant_bytes() == scale_sig.scale_invariant_bytes()


def test_canonical_anchors_self_consistent_under_scale_invariant() -> None:
    output = scale_cluster.run_scale_invariant_clustering_campaign()
    for fixture in FIXTURES:
        assignment = next(item for item in output["fixture_results"][fixture]["assignments_by_cut"] if item["cut_threshold"] == 0.10)
        assert assignment["f1_f4_self_consistent"] is True


def test_F3_silent_under_scale_invariant() -> None:
    for fixture in FIXTURES:
        signature = next(item for item in scale_sig.compute_all_signatures_scale_invariant(fixture) if item.path_label == "F3")
        assert signature.signed_lattice_histogram == {}


def test_scale_invariant_clustering_byte_stable() -> None:
    assert scale_cluster.scale_cluster_bytes() == scale_cluster.scale_cluster_bytes()


def test_scale_invariant_comparison_schema() -> None:
    output = scale_cluster.compare_original_vs_scale_invariant()
    for fixture in FIXTURES:
        row = output["per_fixture"][fixture]
        assert {"removed_F5_candidates", "added_F5_candidates", "retained_F5_candidates"} <= set(row)


def test_decimal_audit_schema_per_fixture() -> None:
    output = decimal_audit.run_decimal_audit()
    for fixture in FIXTURES:
        row = output["fixtures"][fixture]
        assert {
            "n_cells_divergent",
            "sample_operands",
            "decimal_context_at_evaluation",
            "hypothesized_cause",
        } <= set(row)


def test_decimal_audit_byte_stable() -> None:
    assert decimal_audit.decimal_audit_bytes() == decimal_audit.decimal_audit_bytes()


def test_decimal_audit_hypothesized_cause_one_of_four() -> None:
    output = decimal_audit.run_decimal_audit()
    causes = {"decimal_multiplication_rounding", "ulp_threshold_artefact", "substrate_behavior", "indeterminate"}
    for fixture in FIXTURES:
        assert output["fixtures"][fixture]["hypothesized_cause"] in causes


def test_sqrt_roundtrip_residual_byte_stable() -> None:
    assert sqrt_residual.sqrt_roundtrip_bytes() == sqrt_residual.sqrt_roundtrip_bytes()


def test_sqrt_roundtrip_zero_at_F3_firing_cells() -> None:
    for fixture in FIXTURES:
        for index, _ in enumerate(sqrt_residual.canonical_operands(fixture)):
            value = sqrt_residual.sqrt_roundtrip_residual_at_cell(fixture, index, "float64")
            assert value == value
            assert value not in (float("inf"), float("-inf"))


def test_sqrt_roundtrip_alignment_with_P_distrib_sqrt_mul() -> None:
    output = sqrt_residual.run_sqrt_roundtrip_campaign()
    for fixture in ("schwarzschild", "sr"):
        row = output["fixtures"][fixture]
        top_cells = {item["cell_index"] for item in row["top_abs_residual_cells_float64"]}
        assert set(row["p_distrib_sqrt_mul_firing_cells_float64"]) <= top_cells


def test_refined_f5_report_byte_stable() -> None:
    assert refined.refined_f5_bytes() == refined.refined_f5_bytes()


def test_refined_f5_report_methodology_resolution_valid() -> None:
    output = refined.compile_refined_f5_set()
    assert output["methodology_resolution"] in {
        "artefact_dominant",
        "substrate_dominant",
        "mixed_resolution",
        "methodology_compromised",
    }


def test_no_modifications_to_task029_outputs() -> None:
    before = {path: path.read_bytes() for path in _all_frozen_json_paths()}
    scale_sig.write_scale_invariant_output(TASK029B / "scale_invariant_signatures.json")
    scale_cluster.write_scale_invariant_output(TASK029B / "scale_invariant_clustering.json")
    decimal_audit.write_decimal_audit_output(TASK029B / "decimal_scaled_form_audit.json")
    sqrt_residual.write_sqrt_roundtrip_output(TASK029B / "sqrt_roundtrip_residual.json")
    refined.write_refined_f5_report(TASK029B / "refined_f5_report.json")
    after = {path: path.read_bytes() for path in before}
    assert after == before


def test_no_runtime_status_enum_additions() -> None:
    before = _status_values()
    import lloyd_v4.evals.scale_invariant_signature  # noqa: F401
    import lloyd_v4.evals.scale_invariant_clustering  # noqa: F401
    import lloyd_v4.evals.decimal_scaled_form_audit  # noqa: F401
    import lloyd_v4.evals.sqrt_roundtrip_residual  # noqa: F401
    import lloyd_v4.evals.refined_f5_report  # noqa: F401

    after = _status_values()
    assert after == before


def test_no_law_library_term_added() -> None:
    before = tuple(term.term_id for term in build_candidate_library())
    import lloyd_v4.evals.refined_f5_report  # noqa: F401

    after = tuple(term.term_id for term in build_candidate_library())
    assert after == before
    assert len(after) == 17


def test_no_manifest_changes() -> None:
    paths = ("Build_Docs/Architecture/layer_manifest.json", "Build_Docs/Architecture/LAYER_MANIFEST.md")
    subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=ROOT, check=True)


def test_no_clustering_library_imported() -> None:
    paths = [
        "src/lloyd_v4/evals/scale_invariant_signature.py",
        "src/lloyd_v4/evals/scale_invariant_clustering.py",
        "src/lloyd_v4/evals/decimal_scaled_form_audit.py",
        "src/lloyd_v4/evals/sqrt_roundtrip_residual.py",
        "src/lloyd_v4/evals/refined_f5_report.py",
    ]
    result = subprocess.run(
        ["rg", "scipy\\.cluster|sklearn\\.cluster|scipy\\.spatial\\.distance", *paths],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_no_existing_module_modifications() -> None:
    for path in TASK029_MODULES:
        head = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=ROOT, check=True, capture_output=True).stdout
        current = (ROOT / path).read_bytes()
        assert current == head
