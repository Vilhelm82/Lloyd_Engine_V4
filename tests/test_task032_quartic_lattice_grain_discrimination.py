import math
import subprocess
from pathlib import Path

import pytest

from lloyd_v4.evals import cbrt_four_form, pure_algebraic_four_form
from lloyd_v4.evals.pure_algebraic_quartic_campaign import (
    ADMISSIBLE_F2_GRAINS,
    battery_bytes,
    campaign_bytes,
    headline_bytes,
    headline_for_grain,
    lattice_bytes,
    run_campaign,
    sterbenz_boundary_observation,
)
from lloyd_v4.evals.pure_algebraic_quartic_four_form import (
    FORM_KEYS,
    F1_of_x,
    R_of_x,
    f_direct,
    four_form_float32,
    four_form_float64,
    quartic_four_form_battery,
    root_fourth_from_root,
)
from lloyd_v4.evals.pure_algebraic_quartic_lattice_campaign import run_campaign as run_lattice_campaign
from lloyd_v4.evals.pure_algebraic_quartic_polarity_grid_stability import GRID_ORDER, PAIR_ORDER, run_campaign as run_polarity_campaign


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task032_quartic_lattice_grain_discrimination"
SUMMARY = ROOT / "Build_Docs" / "Reports" / "task032_quartic_lattice_grain_discrimination_summary.md"
PRE_REG_COMMIT = "ea1c8d7"
BASELINE_HEAD = "0650a448e68a5498ceb272fbd73cf9afd4cf44ba"
BASELINE_TEST_COUNT = 686
NEW_SOURCE_FILES = (
    "src/lloyd_v4/evals/pure_algebraic_quartic_four_form.py",
    "src/lloyd_v4/evals/pure_algebraic_quartic_lattice_campaign.py",
    "src/lloyd_v4/evals/pure_algebraic_quartic_polarity_grid_stability.py",
    "src/lloyd_v4/evals/pure_algebraic_quartic_campaign.py",
)


def test_task031_commit_is_ancestor_of_head() -> None:
    subprocess.run(["git", "merge-base", "--is-ancestor", "0650a44", "HEAD"], cwd=ROOT, check=True)
    subprocess.run(["git", "merge-base", "--is-ancestor", "0650a44", "origin/main"], cwd=ROOT, check=True)


def test_prior_fixture_modules_importable() -> None:
    assert pure_algebraic_four_form.FORM_KEYS == FORM_KEYS
    assert cbrt_four_form.FORM_KEYS == FORM_KEYS


def test_pre_task_baseline_recorded_in_summary() -> None:
    text = SUMMARY.read_text(encoding="utf-8")
    assert BASELINE_HEAD in text
    assert f"{BASELINE_TEST_COUNT} passing" in text


@pytest.mark.parametrize("precision", ("float32", "float64"))
def test_quartic_root_values_are_finite(precision: str) -> None:
    for x_value in pure_algebraic_four_form.x_grid():
        values = four_form_float32(x_value) if precision == "float32" else four_form_float64(x_value)
        assert all(math.isfinite(value) for value in values.values())


@pytest.mark.parametrize("precision", ("float32", "float64"))
@pytest.mark.parametrize("form_id", ("F1", "F2", "F4"))
def test_non_calibration_forms_are_finite(form_id: str, precision: str) -> None:
    for x_value in pure_algebraic_four_form.x_grid():
        value = four_form_float32(x_value)[form_id] if precision == "float32" else four_form_float64(x_value)[form_id]
        assert math.isfinite(value)


def test_F3_calibration_zero_at_float64() -> None:
    for x_value in pure_algebraic_four_form.x_grid():
        assert four_form_float64(x_value)["F3"] == 0.0


def test_root_fourth_parenthesisations_match_fixture_at_float64() -> None:
    for x_value in pure_algebraic_four_form.x_grid():
        root = R_of_x(x_value)
        direct = f_direct(x_value)
        residual = root_fourth_from_root(root) - direct
        paired = (root * root) * (root * root) - direct
        assert residual == paired
        assert residual == F1_of_x(x_value)


def test_F1_identity_matches_root_fourth_minus_direct() -> None:
    for x_value in pure_algebraic_four_form.x_grid():
        root = R_of_x(x_value)
        assert F1_of_x(x_value) == root_fourth_from_root(root) - f_direct(x_value)


def test_orchestrator_four_form_values_match_direct_module() -> None:
    payload = run_campaign()["four_form_battery"]
    direct = quartic_four_form_battery()
    assert payload == direct


def test_F1_lattice_integer_at_float64() -> None:
    row = run_lattice_campaign()["by_form"]["F1"]["by_precision"]["float64"]
    assert row["candidate_classification"] == "lattice_integer"
    assert row["level_integer_residual_max"] == 0.0


def test_F3_lattice_empty_at_float64() -> None:
    row = run_lattice_campaign()["by_form"]["F3"]["by_precision"]["float64"]
    assert row["candidate_classification"] == "lattice_empty"
    assert row["n_nonzero"] == 0


def test_F4_lattice_integer_at_float64() -> None:
    row = run_lattice_campaign()["by_form"]["F4"]["by_precision"]["float64"]
    assert row["candidate_classification"] == "lattice_integer"
    assert row["level_integer_residual_max"] == 0.0


def test_F2_lattice_non_integer_at_float64() -> None:
    row = run_lattice_campaign()["by_form"]["F2"]["by_precision"]["float64"]
    assert row["candidate_classification"] == "non_integer_lattice"


def test_F2_float64_grain_is_declared_dyadic() -> None:
    row = run_lattice_campaign()["by_form"]["F2"]["by_precision"]["float64"]
    assert row["level_integer_residual_max"] in ADMISSIBLE_F2_GRAINS


def test_F2_float32_grain_reported() -> None:
    row = run_lattice_campaign()["by_form"]["F2"]["by_precision"]["float32"]
    assert isinstance(row["level_integer_residual_max"], float)
    assert row["candidate_classification"] in {"lattice_integer", "non_integer_lattice", "single_level", "lattice_empty"}


def test_polarity_grid_stability_reports_all_pairs_and_grids() -> None:
    output = run_polarity_campaign()
    assert set(output["aggregate_classifications"]) == set(PAIR_ORDER)
    assert {grid["name"] for grid in output["grids"]} == set(GRID_ORDER)
    assert len(output["polarity_tables"]) == len(GRID_ORDER) * 2


def test_sterbenz_boundary_counts_and_densities_populated() -> None:
    row = sterbenz_boundary_observation()
    assert row["observed_boundary_location"] == 0.5
    assert row["n_below_boundary"] > 0
    assert row["n_above_boundary"] > 0
    assert row["below_density"] > row["above_density"]


def test_F3_nonzero_count_zero_across_polarity_grids() -> None:
    output = run_polarity_campaign()
    for table in output["polarity_tables"]:
        assert table["per_form_nonzero"]["F3"] == 0


def test_F1_F2_polarity_coupling_cross_fixture_invariance() -> None:
    output = run_polarity_campaign()
    reference64 = next(table for table in output["polarity_tables"] if table["grid_name"] == "reference" and table["precision"] == "float64")
    fraction = reference64["pairs"]["F1_F2"]["same_sign_fraction"]
    assert fraction == 1.0 or output["aggregate_classifications"]["F1_F2"]["aggregate"] == "grid_stable_polarity_coupling"


@pytest.mark.parametrize(
    ("grain", "headline"),
    (
        (0.125, "lattice_grain_h1_quartic"),
        (0.25, "lattice_grain_h2_operand"),
        (0.0, "lattice_grain_indeterminate"),
        (0.5, "lattice_grain_indeterminate"),
        (0.375, "lattice_grain_indeterminate"),
    ),
)
def test_headline_mapping_branch_by_branch(grain: float, headline: str) -> None:
    assert headline_for_grain(grain) == headline


def test_observed_f2_grain_maps_to_registered_outcome() -> None:
    payload = run_campaign()
    grain = payload["hypothesis_discrimination"]["observed_f2_float64_grain"]
    assert grain in ADMISSIBLE_F2_GRAINS
    assert payload["headline_classification"] == headline_for_grain(grain)


def test_campaign_results_byte_stable() -> None:
    assert campaign_bytes() == (REPORT_DIR / "campaign_results.json").read_bytes()
    assert campaign_bytes() == campaign_bytes()


def test_output_component_bytes_stable() -> None:
    assert battery_bytes() == (REPORT_DIR / "quartic_four_form_battery.json").read_bytes()
    assert lattice_bytes() == (REPORT_DIR / "quartic_lattice_campaign_output.json").read_bytes()
    assert headline_bytes() == (REPORT_DIR / "headline_classification.md").read_bytes()


def test_pre_registration_unchanged_since_pre_registration_commit() -> None:
    committed = subprocess.run(
        ["git", "show", f"{PRE_REG_COMMIT}:Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/pre_registration.md"],
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


def test_no_forbidden_imports_or_power_patterns() -> None:
    result = subprocess.run(
        [
            "rg",
            r"math\.fma|math\.pow|math\.sqrt|cmath|scipy|sympy|mpmath|statsmodels|numpy\.special|numpy\.random|np\.power|numpy\.power|\*\*\s*0\.25|\*\*\s*0\.5",
            *NEW_SOURCE_FILES,
        ],
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
