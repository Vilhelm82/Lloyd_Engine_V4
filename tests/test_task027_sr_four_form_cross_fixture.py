import json
import subprocess
from pathlib import Path

from lloyd_v4.core import status as status_module
from lloyd_v4.evals import cross_fixture_comparison as comparison
from lloyd_v4.evals import sr_lattice_campaign as sr_lattice
from lloyd_v4.evals import sr_polarity_grid_stability as sr_polarity
from lloyd_v4.evals.path_law_discovery import build_candidate_library
from lloyd_v4.evals.sr_four_form import beta_grid, four_form_decimal_oracle, four_form_float32, four_form_float64, sr_four_form_battery
from lloyd_v4.evals.multi_precision_four_form import ulp_of_double


ROOT = Path(__file__).resolve().parents[1]


def _status_values() -> set[str]:
    values: set[str] = set()
    for enum_type in status_module.StatusCode.__args__:
        values.update(item.value for item in enum_type)
    return values


def test_beta_grid_deterministic_and_bounded() -> None:
    first = beta_grid()
    second = beta_grid()

    assert first == second
    assert len(first) == 137
    assert all(left < right for left, right in zip(first, first[1:]))
    assert first[0] == 0.01
    assert first[-1] == 0.9999
    assert all(0.01 <= value <= 0.9999 for value in first)


def test_F3_sr_is_identically_zero() -> None:
    for beta_value in beta_grid():
        assert four_form_float32(beta_value)["F3"] == 0.0
        assert four_form_float64(beta_value)["F3"] == 0.0
        assert four_form_decimal_oracle(beta_value, 50)["F3"] == 0.0


def test_sr_four_form_byte_stable() -> None:
    first = json.dumps(sr_four_form_battery(), sort_keys=True, allow_nan=False)
    second = json.dumps(sr_four_form_battery(), sort_keys=True, allow_nan=False)
    assert first == second


def test_sr_lattice_campaign_schema() -> None:
    output = sr_lattice.run_campaign()
    assert {"campaign", "beta_count", "beta_min", "beta_max", "by_form"} <= set(output)
    for form_id in ("F1", "F2", "F3", "F4"):
        by_precision = output["by_form"][form_id]["by_precision"]
        for precision in ("float32", "float64", "decimal_50"):
            item = by_precision[precision]
            assert {"n_total", "n_nonzero", "n_distinct_levels", "level_histogram", "regional_distinct_level_counts", "candidate_classification"} <= set(item)


def test_sr_polarity_grids_deterministic() -> None:
    for name in sr_polarity.GRID_ORDER:
        first = sr_polarity.construct_grid(name, sr_polarity.GRID_SEEDS[name])
        second = sr_polarity.construct_grid(name, sr_polarity.GRID_SEEDS[name])
        assert first["r_values"] == second["r_values"]


def test_sr_polarity_grids_clamped_and_deduped() -> None:
    for name in sr_polarity.GRID_ORDER:
        values = sr_polarity.construct_grid(name, sr_polarity.GRID_SEEDS[name])["r_values"]
        assert all(0.01 <= value <= 0.9999 for value in values)
        for left, right in zip(values, values[1:]):
            assert abs(right - left) >= 2.0 * ulp_of_double(max(abs(left), abs(right)))


def test_sr_negative_control_f1_f4() -> None:
    output = sr_polarity.run_campaign()
    assert output["negative_control_passed"] is True
    assert output["aggregate_classifications"]["F1_F4"]["aggregate"] in {"depolarized_invariant", "open_underpowered"}


def test_sr_f2_f4_bottle_cap_guard() -> None:
    output = sr_polarity.run_campaign()
    per_grid = output["aggregate_classifications"]["F2_F4"]["per_grid"]
    if any(status == "underpowered_grid" for status in per_grid.values()):
        assert output["aggregate_classifications"]["F2_F4"]["aggregate"] != "grid_stable_polarity_coupling"


def test_sr_polarity_byte_stable() -> None:
    assert sr_polarity.campaign_bytes() == sr_polarity.campaign_bytes()


def test_cross_fixture_comparison_byte_stable() -> None:
    assert comparison.campaign_bytes() == comparison.campaign_bytes()


def test_cross_fixture_comparison_schema() -> None:
    output = comparison.compare_fixtures()
    assert {
        "per_pair_aggregate_comparison",
        "per_grid_per_precision_comparison",
        "lattice_grain_comparison",
        "sterbenz_boundary_comparison",
        "headline_finding",
    } <= set(output)
    assert output["headline_finding"] in {"chain_property_supported", "chain_property_partial", "chain_property_rejected"}


def test_sterbenz_boundary_table_schema() -> None:
    rows = comparison.compare_fixtures()["sterbenz_boundary_comparison"]
    assert len(rows) == 2
    for row in rows:
        assert {
            "f2_count_above_boundary",
            "f2_count_below_boundary",
            "predicted_direction",
            "observed_direction",
            "supports_prediction",
        } <= set(row)
        assert isinstance(row["supports_prediction"], bool)


def test_no_runtime_status_enum_additions() -> None:
    before = _status_values()
    import lloyd_v4.evals.sr_four_form  # noqa: F401
    import lloyd_v4.evals.sr_lattice_campaign  # noqa: F401
    import lloyd_v4.evals.sr_polarity_grid_stability  # noqa: F401
    import lloyd_v4.evals.cross_fixture_comparison  # noqa: F401

    after = _status_values()
    assert after == before


def test_no_law_library_term_added() -> None:
    before = tuple(term.term_id for term in build_candidate_library())
    import lloyd_v4.evals.sr_polarity_grid_stability  # noqa: F401

    after = tuple(term.term_id for term in build_candidate_library())
    assert after == before
    assert len(after) == 17


def test_no_manifest_changes() -> None:
    paths = ("Build_Docs/Architecture/layer_manifest.json", "Build_Docs/Architecture/LAYER_MANIFEST.md")
    subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=ROOT, check=True)


def test_sr_p_value_exact_check() -> None:
    assert sr_polarity._binomial_p_values(20, 20)["p_one_tail_upper"] == 2**-20
