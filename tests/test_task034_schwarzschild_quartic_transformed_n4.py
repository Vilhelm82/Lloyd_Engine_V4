import math
import subprocess
from pathlib import Path

import numpy as np
import pytest

from lloyd_v4.evals import pure_algebraic_quartic_four_form, schwarzschild_four_form
from lloyd_v4.evals.schwarzschild_quartic_campaign import (
    ADMISSIBLE_F2_GRAINS,
    battery_bytes,
    campaign_bytes,
    headline_bytes,
    headline_for_grain,
    lattice_bytes,
    parenthesization_observation,
    run_campaign,
    sterbenz_boundary_observation,
)
from lloyd_v4.evals.schwarzschild_quartic_four_form import (
    FORM_KEYS,
    F1_of_r,
    R_of_r,
    f_direct,
    four_form_float32,
    four_form_float64,
    root_fourth_from_root,
    schwarzschild_quartic_four_form_battery,
)
from lloyd_v4.evals.schwarzschild_quartic_lattice_campaign import run_campaign as run_lattice_campaign
from lloyd_v4.evals.schwarzschild_quartic_polarity_grid_stability import GRID_ORDER, PAIR_ORDER, run_campaign as run_polarity_campaign


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task034_schwarzschild_quartic_transformed_n4"
SUMMARY = ROOT / "Build_Docs" / "Reports" / "task034_schwarzschild_quartic_transformed_n4_summary.md"
PRE_REG_COMMIT = "6a81d9d"
TASK033_COMMIT = "42ff428957054e3079839ff142aa22795dd16f83"
BASELINE_TEST_COUNT = 762
NEW_SOURCE_FILES = (
    "src/lloyd_v4/evals/schwarzschild_quartic_four_form.py",
    "src/lloyd_v4/evals/schwarzschild_quartic_lattice_campaign.py",
    "src/lloyd_v4/evals/schwarzschild_quartic_polarity_grid_stability.py",
    "src/lloyd_v4/evals/schwarzschild_quartic_campaign.py",
)


def test_task033_commit_is_ancestor_of_head() -> None:
    subprocess.run(["git", "merge-base", "--is-ancestor", TASK033_COMMIT, "HEAD"], cwd=ROOT, check=True)
    subprocess.run(["git", "merge-base", "--is-ancestor", TASK033_COMMIT, "origin/main"], cwd=ROOT, check=True)


def test_prior_fixture_modules_importable() -> None:
    assert tuple(schwarzschild_four_form.sweep_r_values())
    assert pure_algebraic_quartic_four_form.FORM_KEYS == FORM_KEYS


def test_pre_task_baseline_recorded_in_summary() -> None:
    text = SUMMARY.read_text(encoding="utf-8")
    assert TASK033_COMMIT in text
    assert f"{BASELINE_TEST_COUNT} passing" in text
    assert PRE_REG_COMMIT in text


@pytest.mark.parametrize("precision", ("float32", "float64"))
def test_root_values_are_finite(precision: str) -> None:
    for r_value in schwarzschild_four_form.sweep_r_values():
        values = four_form_float32(r_value) if precision == "float32" else four_form_float64(r_value)
        root = np.sqrt(np.sqrt(np.float32(schwarzschild_four_form.f_of_r(r_value)))) if precision == "float32" else R_of_r(r_value)
        assert math.isfinite(float(root))
        assert all(math.isfinite(value) for value in values.values())


@pytest.mark.parametrize("precision", ("float32", "float64"))
@pytest.mark.parametrize("form_id", ("F1", "F2", "F4"))
def test_non_calibration_forms_are_finite(form_id: str, precision: str) -> None:
    for r_value in schwarzschild_four_form.sweep_r_values():
        value = four_form_float32(r_value)[form_id] if precision == "float32" else four_form_float64(r_value)[form_id]
        assert math.isfinite(value)


def test_F3_calibration_zero_at_float64() -> None:
    for r_value in schwarzschild_four_form.sweep_r_values():
        assert four_form_float64(r_value)["F3"] == 0.0


def test_F1_identity_matches_root_fourth_minus_direct() -> None:
    for r_value in schwarzschild_four_form.sweep_r_values():
        root = R_of_r(r_value)
        assert F1_of_r(r_value) == root_fourth_from_root(root) - f_direct(r_value)


def test_parenthesization_observation_records_empirical_mismatch() -> None:
    row = parenthesization_observation()
    assert row["paired_grouping"] == "(R * R) * (R * R)"
    assert row["left_fold_grouping"] == "((R * R) * R) * R"
    assert row["mismatch_count"] == 50
    assert row["bit_identical_all_points"] is False


def test_operand_grid_is_byte_identical_to_existing_sweep() -> None:
    payload = schwarzschild_quartic_four_form_battery()
    assert tuple(point["r"] for point in payload["points"]) == schwarzschild_four_form.sweep_r_values()


def test_orchestrator_four_form_values_match_direct_module() -> None:
    payload = run_campaign()["four_form_battery"]
    direct = schwarzschild_quartic_four_form_battery()
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
    assert row["observed_boundary_location"] == 4.0
    assert row["nearest_grid_point_to_boundary"] == 3.9655172413793105
    assert row["n_below_boundary"] > 0
    assert row["n_above_boundary"] > 0
    assert row["above_density"] > row["below_density"]
    assert row["supports_prediction"] is True


def test_F3_nonzero_count_zero_across_polarity_grids() -> None:
    output = run_polarity_campaign()
    for table in output["polarity_tables"]:
        assert table["per_form_nonzero"]["F3"] == 0


def test_F1_F2_polarity_coupling_grid_stable() -> None:
    output = run_polarity_campaign()
    reference64 = next(table for table in output["polarity_tables"] if table["grid_name"] == "reference" and table["precision"] == "float64")
    assert reference64["pairs"]["F1_F2"]["same_sign_fraction"] == 1.0
    assert output["aggregate_classifications"]["F1_F2"]["aggregate"] == "grid_stable_polarity_coupling"


@pytest.mark.parametrize(
    ("grain", "headline"),
    (
        (0.125, "compound_law_h3_supported_at_n4"),
        (0.25, "transformed_decay_converges_to_identity_floor"),
        (0.0625, "rounding_event_count_dominates"),
        (0.0, "lattice_grain_indeterminate_at_n4_transformed"),
        (0.5, "lattice_grain_indeterminate_at_n4_transformed"),
        (0.375, "lattice_grain_indeterminate_at_n4_transformed"),
    ),
)
def test_headline_mapping_branch_by_branch(grain: float, headline: str) -> None:
    assert headline_for_grain(grain) == headline


def test_observed_f2_grain_maps_to_registered_outcome() -> None:
    payload = run_campaign()
    grain = payload["hypothesis_discrimination"]["observed_f2_float64_grain"]
    assert grain in ADMISSIBLE_F2_GRAINS
    assert payload["headline_classification"] == headline_for_grain(grain)


def test_sterbenz_boundary_location_matches_prior_schwarzschild_fixtures() -> None:
    row = sterbenz_boundary_observation()
    assert row["observed_boundary_location"] == row["existing_schwarzschild_n2_boundary"] == 4.0
    assert row["observed_boundary_location"] == row["existing_schwarzschild_cbrt_n3_boundary"] == 4.0
    assert row["boundary_location_match_to_prior_schwarzschild_fixtures"] is True


def test_campaign_results_byte_stable() -> None:
    assert campaign_bytes() == (REPORT_DIR / "campaign_results.json").read_bytes()
    assert campaign_bytes() == campaign_bytes()


def test_output_component_bytes_stable() -> None:
    assert battery_bytes() == (REPORT_DIR / "schwarzschild_quartic_four_form_battery.json").read_bytes()
    assert lattice_bytes() == (REPORT_DIR / "schwarzschild_quartic_lattice_campaign_output.json").read_bytes()
    assert headline_bytes() == (REPORT_DIR / "headline_classification.md").read_bytes()


def test_pre_registration_unchanged_since_pre_registration_commit() -> None:
    committed = subprocess.run(
        ["git", "show", f"{PRE_REG_COMMIT}:Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/pre_registration.md"],
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
            r"math\.fma|math\.pow|cmath|scipy|sympy|mpmath|statsmodels|numpy\.special|numpy\.random|np\.power|numpy\.power|\*\*\s*0\.25|\*\*\s*0\.5|\*\*\s*\(\s*1",
            *NEW_SOURCE_FILES,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_no_physics_interpretive_language_in_task034_files() -> None:
    paths = [ROOT / path for path in NEW_SOURCE_FILES]
    paths += [path for path in REPORT_DIR.glob("*") if path.is_file()]
    paths.append(SUMMARY)
    result = subprocess.run(
        ["rg", "Kerr|lightspeed|frame dragging|cosmology|relativistic", *[str(path.relative_to(ROOT)) for path in paths]],
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
