import subprocess
from pathlib import Path

import numpy as np

from lloyd_v4.evals import cbrt_four_form as cbrt
from lloyd_v4.evals import cbrt_four_form_campaign as campaign
from lloyd_v4.evals import cbrt_lattice_campaign as lattice
from lloyd_v4.evals import cbrt_polarity_grid_stability as polarity
from lloyd_v4.evals import cross_fixture_comparison
from lloyd_v4.evals.multi_precision_four_form import ulp_of_double
from lloyd_v4.evals.polarity_grid_stability import GRID_ORDER
from lloyd_v4.evals.pure_algebraic_four_form import x_grid


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029c_cbrt_four_form_battery"
PRE_REG_COMMIT = "9ee06d7"
NEW_SOURCE_FILES = (
    "src/lloyd_v4/evals/cbrt_four_form.py",
    "src/lloyd_v4/evals/cbrt_lattice_campaign.py",
    "src/lloyd_v4/evals/cbrt_polarity_grid_stability.py",
    "src/lloyd_v4/evals/cbrt_four_form_campaign.py",
)


def test_numpy_cbrt_exact_integer_cube() -> None:
    assert np.cbrt(8.0) == 2.0


def test_numpy_cbrt_exact_fractional_cube() -> None:
    assert np.cbrt(np.float32(0.125)) == np.float32(0.5)


def test_cbrt_uses_canonical_x_grid() -> None:
    values = x_grid()
    assert len(values) == 137
    assert values[0] == 0.01
    assert values[-1] == 0.99
    assert 0.5 in values


def test_F3_cbrt_identically_zero() -> None:
    for x_value in x_grid():
        assert cbrt.four_form_float32(x_value)["F3"] == 0.0
        assert cbrt.four_form_float64(x_value)["F3"] == 0.0


def test_F1_and_F4_finite_on_grid() -> None:
    for x_value in x_grid():
        for form_id in ("F1", "F4"):
            value = cbrt.four_form_float64(x_value)[form_id]
            assert value == value
            assert value not in (float("inf"), float("-inf"))


def test_F2_finite_on_grid() -> None:
    for x_value in x_grid():
        value = cbrt.four_form_float64(x_value)["F2"]
        assert value == value
        assert value not in (float("inf"), float("-inf"))


def test_alt_routing_close_to_direct() -> None:
    for x_value in x_grid():
        direct = cbrt.f_direct(x_value)
        alternate = cbrt.f_alt_routing(x_value)
        unit = ulp_of_double(max(abs(direct), abs(alternate)))
        assert abs(direct - alternate) <= 16.0 * unit


def test_sterbenz_regions_populated() -> None:
    values = x_grid()
    assert any(value <= 0.5 for value in values)
    assert any(value > 0.5 for value in values)


def test_F3_silent_in_both_sterbenz_regions() -> None:
    for x_value in x_grid():
        assert cbrt.four_form_float64(x_value)["F3"] == 0.0
        if x_value <= 0.5:
            assert cbrt.four_form_float64(x_value)["F3"] == 0.0
        else:
            assert cbrt.four_form_float64(x_value)["F3"] == 0.0


def test_cbrt_lattice_campaign_schema() -> None:
    output = lattice.run_campaign()
    for form_id in cbrt.FORM_KEYS:
        by_precision = output["by_form"][form_id]["by_precision"]
        assert set(by_precision) == {"float32", "float64"}
        for item in by_precision.values():
            assert {"n_total", "n_nonzero", "level_integer_residual_max", "candidate_classification"} <= set(item)


def test_polarity_grids_deterministic() -> None:
    for name in GRID_ORDER:
        first = polarity.construct_grid(name, polarity.GRID_SEEDS[name])
        second = polarity.construct_grid(name, polarity.GRID_SEEDS[name])
        assert first["r_values"] == second["r_values"]


def test_polarity_grids_bounded_and_deduped() -> None:
    for name in GRID_ORDER:
        values = polarity.construct_grid(name, polarity.GRID_SEEDS[name])["r_values"]
        assert all(0.01 <= value <= 0.99 for value in values)
        for left, right in zip(values, values[1:]):
            assert abs(right - left) >= 2.0 * ulp_of_double(max(abs(left), abs(right)))


def test_campaign_results_byte_stable_against_report() -> None:
    assert campaign.campaign_bytes() == (REPORT_DIR / "campaign_results.json").read_bytes()


def test_campaign_results_byte_stable_across_runs() -> None:
    assert campaign.campaign_bytes() == campaign.campaign_bytes()


def test_headline_classification_byte_stable() -> None:
    assert campaign.headline_bytes() == (REPORT_DIR / "headline_classification.md").read_bytes()
    assert campaign.headline_bytes() == campaign.headline_bytes()


def test_pre_registration_unchanged_since_pre_registration_commit() -> None:
    committed = subprocess.run(
        ["git", "show", f"{PRE_REG_COMMIT}:Build_Docs/Reports/task029c_cbrt_four_form_battery/pre_registration.md"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    current = (REPORT_DIR / "pre_registration.md").read_bytes()
    assert current == committed


def test_F3_sentinel_every_grid() -> None:
    output = polarity.run_campaign()
    for table in output["polarity_tables"]:
        assert table["per_form_nonzero"]["F3"] == 0


def test_negative_control_F1_F4_not_promoted() -> None:
    output = polarity.run_campaign()
    assert output["negative_control_passed"] is True
    assert output["aggregate_classifications"]["F1_F4"]["aggregate"] in {"depolarized_invariant", "open_underpowered"}


def test_F2_F4_bottle_cap_not_bypassed() -> None:
    output = polarity.run_campaign()
    per_grid = output["aggregate_classifications"]["F2_F4"]["per_grid"]
    if any(status == "underpowered_grid" for status in per_grid.values()):
        assert output["aggregate_classifications"]["F2_F4"]["aggregate"] != "grid_stable_polarity_coupling"


def test_no_manifest_changes() -> None:
    paths = ("Build_Docs/Architecture/layer_manifest.json", "Build_Docs/Architecture/LAYER_MANIFEST.md")
    subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=ROOT, check=True)


def test_no_physics_interpretive_language_in_task_files() -> None:
    report_files = tuple(sorted(REPORT_DIR.glob("*"))) + (ROOT / "Build_Docs" / "Reports" / "task029c_summary.md",)
    paths = [ROOT / path for path in NEW_SOURCE_FILES] + [path for path in report_files if path.is_file()]
    result = subprocess.run(
        ["rg", "Kerr|lightspeed|frame dragging|cosmology|relativistic", *[str(path.relative_to(ROOT)) for path in paths]],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_no_forbidden_cbrt_imports_or_patterns() -> None:
    result = subprocess.run(
        [
            "rg",
            r"math\.cbrt|cmath|scipy|sympy|mpmath|math\.pi|math\.e|math\.tau|\*\*\s*\(\s*1\.0\s*/\s*3\.0\s*\)|\*\*\s*\(\s*1\s*/\s*3\s*\)",
            *NEW_SOURCE_FILES,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1


def test_scale_invariant_rank_computed_for_cbrt() -> None:
    output = campaign.run_campaign()["cbrt_fixture"]["scale_invariant_rank_cut_0_10"]
    assert output["cut_threshold"] == 0.10
    assert isinstance(output["rank"], int)
    assert {"F1", "F2", "F3", "F4"} <= set(output["cluster_membership"])


def test_canonical_anchors_self_consistent_under_cbrt_rank() -> None:
    output = campaign.run_campaign()["cbrt_fixture"]["scale_invariant_rank_cut_0_10"]
    clusters = {output["cluster_membership"][label] for label in ("F1", "F2", "F3", "F4")}
    assert len(clusters) == 4
    assert output["f1_f4_self_consistent"] is True


def test_sterbenz_boundary_matches_pre_registration() -> None:
    row = campaign.sterbenz_boundary_observation()
    assert row["observed_boundary_location"] == 0.5
    assert row["observed_direction"] == "below_boundary_higher"
    assert row["supports_prediction"] is True


def test_F5_positive_predictions_recorded() -> None:
    section = campaign.run_campaign()["section_B_prediction_matches"]
    for label in ("P_compound_split", "P_sign_c"):
        assert section[label]["observed_status"] in {"present", "absent", "attenuated"}
        assert section[label]["cofire_rate"] is not None


def test_P_distrib_sqrt_mul_prediction_recorded() -> None:
    section = campaign.run_campaign()["section_B_prediction_matches"]
    assert section["P_distrib_sqrt_mul"]["observed_status"] in {"present", "absent", "attenuated"}
    assert section["P_distrib_sqrt_mul"]["cofire_rate"] is not None


def test_section_A_drives_headline() -> None:
    output = campaign.run_campaign()
    assert all(row["match"] for row in output["section_A_prediction_matches"])
    assert output["headline_classification"] == "chain_property_universal"


def test_cross_fixture_comparison_accepts_cbrt_fixture() -> None:
    output = cross_fixture_comparison.compare_fixtures(("schwarzschild", "sr", "pure_algebraic", "cbrt_chain"))
    assert output["fixtures"] == ["schwarzschild", "sr", "pure_algebraic", "cbrt_chain"]
    rows = {row["fixture"]: row for row in output["sterbenz_boundary_comparison"]}
    assert rows["cbrt_chain"]["supports_prediction"] is True
