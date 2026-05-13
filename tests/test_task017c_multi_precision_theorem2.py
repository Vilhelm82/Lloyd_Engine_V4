import subprocess
from decimal import Decimal, getcontext, localcontext
from pathlib import Path

import numpy as np
import pytest

from lloyd_v4.evals.precision import multi_precision_campaign as campaign
from lloyd_v4.evals.precision import precision_bound_fixtures as fixtures
from lloyd_v4.evals.precision import unit_roundoff
from lloyd_v4.evals.precision.linear_fit import bootstrap_ci, fit_linear, interval_includes_zero


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task017c_multi_precision_theorem2"
THEOREM_SOURCE = Path("/home/william_lloydlt/projects/V4/Docs/transfer_function_exponent_family_v3.tex")
PRE_REG_COMMIT = "77dbd5a"
NEW_SOURCE_FILES = (
    "src/lloyd_v4/evals/precision/__init__.py",
    "src/lloyd_v4/evals/precision/unit_roundoff.py",
    "src/lloyd_v4/evals/precision/precision_bound_fixtures.py",
    "src/lloyd_v4/evals/precision/linear_fit.py",
    "src/lloyd_v4/evals/precision/multi_precision_campaign.py",
)


def test_task029c_commit_is_ancestor() -> None:
    subprocess.run(["git", "merge-base", "--is-ancestor", "975a3fb", "HEAD"], cwd=ROOT, check=True)


def test_theorem_source_accessible_and_contains_theorem2() -> None:
    text = THEOREM_SOURCE.read_text(encoding="utf-8")
    assert "\\begin{theorem}[Precision-scaling separation test]" in text
    assert "\\label{thm:precision-separation}" in text


def test_numpy_float32_dtype_sanity() -> None:
    assert np.float32(1.0).dtype == np.dtype(np.float32)


def test_float128_platform_report_present() -> None:
    report = unit_roundoff.platform_float128_report()
    assert {"float64", "float128", "float128_distinct_from_float64"} <= set(report)
    assert report["float128"]["eps"] != ""


def test_decimal_context_expected_precision_simple_computation() -> None:
    for precision in (50, 100, 200):
        with localcontext() as context:
            context.prec = precision
            result = Decimal(1) / Decimal(7)
            assert len(result.as_tuple().digits) == precision


def test_precision_wrappers_return_values_for_sqrt_fixtures() -> None:
    for fixture in ("schwarzschild", "sr", "pure_algebraic"):
        operand = fixtures.canonical_grid(fixture)[0]
        for precision in fixtures.precision_battery_for_fixture(fixture):
            values = fixtures.four_form_values(fixture, precision, operand)
            assert set(fixtures.CORE_PATHS) <= set(values)


def test_cbrt_precision_wrappers_return_binary_values() -> None:
    operand = fixtures.canonical_grid("cbrt_chain")[0]
    for precision in fixtures.precision_battery_for_fixture("cbrt_chain"):
        values = fixtures.four_form_values("cbrt_chain", precision, operand)
        assert set(fixtures.CORE_PATHS) <= set(values)


def test_cbrt_decimal_precision_out_of_scope_message() -> None:
    with pytest.raises(NotImplementedError, match="out-of-scope-by-design"):
        fixtures.four_form_values("cbrt_chain", "decimal_50", 0.5)


def test_decimal_context_does_not_leak() -> None:
    outer = getcontext().prec
    with localcontext() as context:
        context.prec = 50
        assert getcontext().prec == 50
    assert getcontext().prec == outer


def test_unit_roundoff_float32() -> None:
    value = unit_roundoff.u_p("float32").as_float()
    assert f"{value:.3g}" == "5.96e-08"


def test_unit_roundoff_float64() -> None:
    value = unit_roundoff.u_p("float64").as_float()
    assert f"{value:.3g}" == "1.11e-16"


def test_unit_roundoff_decimal50_exact() -> None:
    assert unit_roundoff.u_p("decimal_50").value == Decimal(5) * (Decimal(10) ** Decimal(-50))


def test_unit_roundoff_records_convention() -> None:
    assert "half spacing" in unit_roundoff.u_p("float64").convention
    assert "round-half-even" in unit_roundoff.u_p("decimal_50").convention


def test_linear_fit_matches_synthetic_line() -> None:
    fit = fit_linear((0.0, 1.0, 2.0, 3.0), (2.0, 5.0, 8.0, 11.0))
    assert abs(fit.intercept - 2.0) < 1.0e-12
    assert abs(fit.slope - 3.0) < 1.0e-12


def test_linear_fit_perfect_r2() -> None:
    assert fit_linear((0.0, 1.0, 2.0), (1.0, 3.0, 5.0)).r_squared == 1.0


def test_bootstrap_ci_deterministic() -> None:
    first = bootstrap_ci((0.0, 1.0, 2.0, 3.0), (1.0, 3.0, 5.0, 7.0), seed_material="synthetic")
    second = bootstrap_ci((0.0, 1.0, 2.0, 3.0), (1.0, 3.0, 5.0, 7.0), seed_material="synthetic")
    assert first == second


def test_bootstrap_ci_includes_true_parameter_on_synthetic_data() -> None:
    ci = bootstrap_ci((0.0, 1.0, 2.0, 3.0), (1.0, 3.0, 5.0, 7.0), seed_material="synthetic-true")
    assert ci["a_k"][0] <= 1.0 <= ci["a_k"][1]
    assert ci["b_k"][0] <= 2.0 <= ci["b_k"][1]


def test_sterbenz_region_predicates_subset_grid() -> None:
    for fixture in fixtures.FIXTURES:
        regions = {fixtures.sterbenz_region(fixture, value) for value in fixtures.canonical_grid(fixture)}
        assert "sterbenz" in regions
        assert "regular" in regions


def test_cpk_definition_line_matches_theorem_source() -> None:
    source_line = "    C_{p,k}:=\\lim_{f\\to0^+}\\frac{R_{p,k}(f)}{f^{\\alpha-1}L(f)}."
    assert source_line in THEOREM_SOURCE.read_text(encoding="utf-8")
    assert source_line in (REPORT_DIR / "pre_registration.md").read_text(encoding="utf-8")


def test_pre_registration_records_platform_and_boundaries() -> None:
    text = (REPORT_DIR / "pre_registration.md").read_text(encoding="utf-8")
    assert "numpy.float128 / numpy.longdouble" in text
    for boundary in ("r >= 4", "beta <= 1 / sqrt(2)", "x <= 1/2"):
        assert boundary in text


def test_precision_aggregate_byte_stable_against_report() -> None:
    assert campaign.precision_aggregate_bytes() == (REPORT_DIR / "precision_aggregate.json").read_bytes()


def test_f5_supplementary_byte_stable_against_report() -> None:
    assert campaign.f5_supplementary_bytes() == (REPORT_DIR / "f5_plus_supplementary.json").read_bytes()


def test_headline_classification_byte_stable_against_report() -> None:
    assert campaign.headline_bytes() == (REPORT_DIR / "headline_classification.md").read_bytes()


def test_pre_registration_unchanged_since_pre_registration_commit() -> None:
    committed = subprocess.run(
        ["git", "show", f"{PRE_REG_COMMIT}:Build_Docs/Reports/task017c_multi_precision_theorem2/pre_registration.md"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    assert (REPORT_DIR / "pre_registration.md").read_bytes() == committed


def test_F3_sentinel_across_precisions() -> None:
    output = campaign.run_precision_campaign()
    for row in output["observation_table"]:
        if row["path"] == "F3":
            assert row["residual"] == 0.0


def test_no_manifest_changes() -> None:
    paths = ("Build_Docs/Architecture/layer_manifest.json", "Build_Docs/Architecture/LAYER_MANIFEST.md")
    subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=ROOT, check=True)


def test_no_physics_interpretive_language_in_task_files() -> None:
    paths = [ROOT / path for path in NEW_SOURCE_FILES]
    paths.extend(path for path in REPORT_DIR.glob("*") if path.is_file())
    summary = ROOT / "Build_Docs" / "Reports" / "task017c_summary.md"
    if summary.is_file():
        paths.append(summary)
    result = subprocess.run(
        ["rg", "Kerr|lightspeed|frame dragging|cosmology|relativistic", *[str(path.relative_to(ROOT)) for path in paths]],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_no_forbidden_imports_introduced() -> None:
    result = subprocess.run(
        ["rg", "scipy|sympy|mpmath|statsmodels|sklearn|numpy\\.special", *NEW_SOURCE_FILES],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_typed_finite_difference_source_unchanged() -> None:
    path = "src/lloyd_v4/primitives/typed_finite_difference.py"
    committed = subprocess.run(["git", "show", f"{PRE_REG_COMMIT}:{path}"], cwd=ROOT, capture_output=True, check=True).stdout
    assert (ROOT / path).read_bytes() == committed


def test_no_forbidden_cbrt_or_fractional_power_patterns() -> None:
    result = subprocess.run(
        ["rg", r"math\.cbrt|\*\*\s*\(\s*1\.0\s*/\s*3\.0\s*\)|\*\*\s*\(\s*1\s*/\s*3\s*\)|numpy\.special", *NEW_SOURCE_FILES],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_no_hardcoded_math_named_constants() -> None:
    result = subprocess.run(
        ["rg", r"math\.pi|math\.e|math\.tau", *NEW_SOURCE_FILES],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_no_numpy_random() -> None:
    result = subprocess.run(["rg", r"numpy\.random|np\.random", *NEW_SOURCE_FILES], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 1


def test_no_global_decimal_context_mutation() -> None:
    result = subprocess.run(
        ["rg", r"getcontext\(\)\.prec|decimal\.getcontext\(\)\.prec", *NEW_SOURCE_FILES],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_precision_distributions_distinguishable() -> None:
    output = campaign.run_precision_campaign()
    for fixture in fixtures.FIXTURES:
        summaries = output["fits"][fixture]["F1"]["regular_region"]["per_precision_summary"]
        assert len({row["rms_C"] for row in summaries}) > 1


def test_float32_regular_distribution_not_single_outlier_dominated() -> None:
    output = campaign.run_precision_campaign()
    for fixture in fixtures.FIXTURES:
        first = output["fits"][fixture]["F1"]["regular_region"]["per_precision_summary"][0]
        assert first["largest_u_outlier_fraction"] <= 0.75


def test_F3_fit_slope_ci_includes_zero_all_fixtures() -> None:
    output = campaign.run_precision_campaign()
    for fixture in fixtures.FIXTURES:
        assert output["fits"][fixture]["F3"]["regular_region"]["b_k_ci_includes_zero"] is True


def test_core_slopes_are_reported_and_not_identical() -> None:
    output = campaign.run_precision_campaign()
    for fixture in fixtures.FIXTURES:
        slopes = [output["fits"][fixture][path]["regular_region"]["fit"]["b_k"] for path in ("F1", "F2", "F4")]
        assert len(set(slopes)) > 1


def test_F2_sterbenz_and_regular_fits_reported() -> None:
    output = campaign.run_precision_campaign()
    for fixture in fixtures.FIXTURES:
        regular = output["fits"][fixture]["F2"]["regular_region"]["fit"]["b_k"]
        sterbenz = output["fits"][fixture]["F2"]["sterbenz_region"]["fit"]["b_k"]
        assert regular != sterbenz


def test_f5_supplementary_paths_reported() -> None:
    output = campaign.run_f5_supplementary_campaign()
    for fixture in fixtures.FIXTURES:
        assert set(output["fits"][fixture]) == {"P_compound_split", "P_sign_c"}


def test_headline_is_declared_value() -> None:
    output = campaign.run_precision_campaign()
    assert output["headline_classification"] in {"theorem2_validated", "theorem2_partial", "theorem2_refuted"}
