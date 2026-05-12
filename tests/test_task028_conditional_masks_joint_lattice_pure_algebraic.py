import json
import subprocess
from pathlib import Path

from lloyd_v4.core import status as status_module
from lloyd_v4.evals import conditional_mask_analysis as masks
from lloyd_v4.evals import cross_fixture_comparison as comparison
from lloyd_v4.evals import joint_signed_lattice_analysis as joint
from lloyd_v4.evals import pure_algebraic_lattice_campaign as pure_lattice
from lloyd_v4.evals import pure_algebraic_polarity_grid_stability as pure_polarity
from lloyd_v4.evals.path_law_discovery import build_candidate_library
from lloyd_v4.evals.pure_algebraic_four_form import four_form_decimal_oracle, four_form_float32, four_form_float64, pure_algebraic_four_form_battery, x_grid
from lloyd_v4.evals.multi_precision_four_form import ulp_of_double


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task028_conditional_masks_joint_lattice_pure_algebraic"
SCHWARZSCHILD_POLARITY = ROOT / "Build_Docs" / "Reports" / "task026c_prime_polarity_grid_stability" / "campaign_output.json"
SR_POLARITY = ROOT / "Build_Docs" / "Reports" / "task027_sr_four_form_cross_fixture" / "sr_polarity_grid_stability.json"


def _status_values() -> set[str]:
    values: set[str] = set()
    for enum_type in status_module.StatusCode.__args__:
        values.update(item.value for item in enum_type)
    return values


def test_conditional_mask_schema() -> None:
    output = masks.run_conditional_mask_campaign()
    required = {
        "F1_fires",
        "F2_fires",
        "cofire",
        "F1_only",
        "F2_only",
        "neither",
        "p_F2_given_F1",
        "p_F1_given_F2",
        "asymmetry_ratio",
        "cofire_same_sign",
        "cofire_opposite_sign",
    }
    for entry in output["entries"]:
        assert {"fixture", "grid", "precision", "n_cells", "pairs"} <= set(entry)
        assert set(entry["pairs"]) == set(masks.PAIR_ORDER)
        for pair in masks.PAIR_ORDER:
            assert required <= set(entry["pairs"][pair])


def test_conditional_mask_counts_consistency() -> None:
    output = masks.run_conditional_mask_campaign()
    for entry in output["entries"]:
        for pair in masks.PAIR_ORDER:
            item = entry["pairs"][pair]
            assert item["F1_fires"] + item["F2_only"] == item["F2_fires"] + item["F1_only"]
            assert item["cofire"] + item["F1_only"] + item["F2_only"] + item["neither"] == entry["n_cells"]
            assert item["cofire_same_sign"] + item["cofire_opposite_sign"] == item["cofire"]


def test_conditional_mask_byte_stable() -> None:
    assert masks.campaign_bytes() == masks.campaign_bytes()


def test_joint_signed_lattice_schema() -> None:
    output = joint.run_joint_lattice_campaign()
    for entry in output["entries"]:
        assert {"fixture", "precision", "n_cells", "joint_states", "marginals", "conditional_summaries"} <= set(entry)
        assert {"by_F1_level", "by_F2_level", "by_F4_level", "by_polarity_state"} <= set(entry["marginals"])
        assert {"F2_level_given_F1_plus1", "F2_level_given_F1_minus1", "F1F2_polarity_given_F4_level_band"} <= set(entry["conditional_summaries"])
        for state in entry["joint_states"]:
            assert {"state_key", "count", "fraction", "example_indices"} <= set(state)


def test_joint_signed_lattice_marginals_sum_to_total() -> None:
    output = joint.run_joint_lattice_campaign()
    for entry in output["entries"]:
        assert sum(entry["marginals"]["by_F1_level"].values()) == entry["n_cells"]
        assert sum(entry["marginals"]["by_F2_level"].values()) == entry["n_cells"]
        assert sum(entry["marginals"]["by_F4_level"].values()) == entry["n_cells"]


def test_joint_signed_lattice_byte_stable() -> None:
    assert joint.campaign_bytes() == joint.campaign_bytes()


def test_x_grid_deterministic_and_bounded() -> None:
    first = x_grid()
    second = x_grid()
    assert first == second
    assert len(first) == 137
    assert all(left < right for left, right in zip(first, first[1:]))
    assert first[0] == 0.01
    assert first[-1] == 0.99
    assert all(0.01 <= value <= 0.99 for value in first)


def test_F3_pure_algebraic_identically_zero() -> None:
    for value in x_grid():
        assert four_form_float32(value)["F3"] == 0.0
        assert four_form_float64(value)["F3"] == 0.0
        assert four_form_decimal_oracle(value, 50)["F3"] == 0.0


def test_pure_algebraic_four_form_byte_stable() -> None:
    first = json.dumps(pure_algebraic_four_form_battery(), sort_keys=True, allow_nan=False)
    second = json.dumps(pure_algebraic_four_form_battery(), sort_keys=True, allow_nan=False)
    assert first == second


def test_pure_algebraic_polarity_grids_deterministic() -> None:
    for name in pure_polarity.GRID_ORDER:
        first = pure_polarity.construct_grid(name, pure_polarity.GRID_SEEDS[name])
        second = pure_polarity.construct_grid(name, pure_polarity.GRID_SEEDS[name])
        assert first["r_values"] == second["r_values"]


def test_pure_algebraic_polarity_grids_clamped_and_deduped() -> None:
    for name in pure_polarity.GRID_ORDER:
        values = pure_polarity.construct_grid(name, pure_polarity.GRID_SEEDS[name])["r_values"]
        assert all(0.01 <= value <= 0.99 for value in values)
        for left, right in zip(values, values[1:]):
            assert abs(right - left) >= 2.0 * ulp_of_double(max(abs(left), abs(right)))


def test_pure_algebraic_negative_control_F1_F4() -> None:
    output = pure_polarity.run_campaign()
    assert output["negative_control_passed"] is True
    assert output["aggregate_classifications"]["F1_F4"]["aggregate"] in {"depolarized_invariant", "open_underpowered"}


def test_pure_algebraic_F2_F4_bottle_cap_guard() -> None:
    output = pure_polarity.run_campaign()
    per_grid = output["aggregate_classifications"]["F2_F4"]["per_grid"]
    if any(status == "underpowered_grid" for status in per_grid.values()):
        assert output["aggregate_classifications"]["F2_F4"]["aggregate"] != "grid_stable_polarity_coupling"


def test_pure_algebraic_polarity_byte_stable() -> None:
    assert pure_polarity.campaign_bytes() == pure_polarity.campaign_bytes()


def test_three_fixture_comparison_byte_stable() -> None:
    assert comparison.campaign_bytes() == comparison.campaign_bytes()


def test_three_fixture_comparison_schema() -> None:
    output = comparison.compare_fixtures()
    assert {
        "fixtures",
        "per_pair_aggregate_comparison",
        "per_grid_per_precision_comparison",
        "lattice_grain_comparison",
        "sterbenz_boundary_comparison",
        "headline_finding",
    } <= set(output)
    assert "pure_algebraic" in output["fixtures"]
    assert output["headline_finding"] in {"chain_property_supported", "chain_property_partial", "chain_property_rejected"}
    for row in output["per_pair_aggregate_comparison"]:
        assert {"schwarzschild_aggregate", "sr_aggregate", "pure_algebraic_aggregate"} <= set(row)


def test_sterbenz_boundary_three_fixtures() -> None:
    rows = {row["fixture"]: row for row in comparison.compare_fixtures()["sterbenz_boundary_comparison"]}
    assert set(rows) == {"schwarzschild", "sr", "pure_algebraic"}
    assert rows["schwarzschild"]["boundary"] == 4.0
    assert rows["sr"]["boundary"] == 2.0 ** -0.5
    assert rows["pure_algebraic"]["boundary"] == 0.5
    for row in rows.values():
        assert {"f2_count_below_boundary", "f2_count_above_boundary", "supports_prediction"} <= set(row)
        assert isinstance(row["supports_prediction"], bool)


def test_no_runtime_status_enum_additions() -> None:
    before = _status_values()
    import lloyd_v4.evals.conditional_mask_analysis  # noqa: F401
    import lloyd_v4.evals.joint_signed_lattice_analysis  # noqa: F401
    import lloyd_v4.evals.pure_algebraic_four_form  # noqa: F401
    import lloyd_v4.evals.pure_algebraic_lattice_campaign  # noqa: F401
    import lloyd_v4.evals.pure_algebraic_polarity_grid_stability  # noqa: F401

    after = _status_values()
    assert after == before


def test_no_law_library_term_added() -> None:
    before = tuple(term.term_id for term in build_candidate_library())
    import lloyd_v4.evals.pure_algebraic_polarity_grid_stability  # noqa: F401

    after = tuple(term.term_id for term in build_candidate_library())
    assert after == before
    assert len(after) == 17


def test_no_manifest_changes() -> None:
    paths = ("Build_Docs/Architecture/layer_manifest.json", "Build_Docs/Architecture/LAYER_MANIFEST.md")
    subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=ROOT, check=True)


def test_existing_campaign_outputs_unchanged() -> None:
    before = {path: path.read_bytes() for path in (SCHWARZSCHILD_POLARITY, SR_POLARITY)}
    masks.write_conditional_mask_output(REPORT_DIR / "conditional_mask_output.json")
    joint.write_joint_lattice_output(REPORT_DIR / "joint_signed_lattice_output.json")
    pure_lattice.write_campaign_output(REPORT_DIR / "pure_algebraic_lattice_campaign_output.json")
    pure_polarity.write_campaign_output(REPORT_DIR / "pure_algebraic_polarity_grid_stability.json")
    comparison.write_comparison_output(REPORT_DIR / "three_fixture_comparison.json")
    after = {path: path.read_bytes() for path in before}
    assert after == before
