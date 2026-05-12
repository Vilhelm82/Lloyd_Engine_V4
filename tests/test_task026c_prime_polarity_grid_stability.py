import json
import subprocess
import sys
from pathlib import Path

from lloyd_v4.core import status as status_module
from lloyd_v4.evals.path_law_discovery import build_candidate_library
from lloyd_v4.evals.polarity_grid_stability import (
    GRID_ORDER,
    GRID_SEEDS,
    PAIR_ORDER,
    _binomial_p_values,
    campaign_bytes,
    compute_polarity_table,
    compute_precision_overlap_invariance,
    construct_grid,
    run_campaign,
)
from lloyd_v4.evals.schwarzschild_four_form import sweep_r_values
from lloyd_v4.evals.multi_precision_four_form import ulp_of_double


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "lloyd_v4" / "evals" / "polarity_grid_stability.py"


def _status_values() -> set[str]:
    values: set[str] = set()
    for enum_type in status_module.StatusCode.__args__:
        values.update(item.value for item in enum_type)
    return values


def test_grids_are_deterministic() -> None:
    for name in GRID_ORDER:
        first = construct_grid(name, GRID_SEEDS[name])
        second = construct_grid(name, GRID_SEEDS[name])
        assert first["r_values"] == second["r_values"]


def test_grids_preserve_ordering() -> None:
    for name in GRID_ORDER:
        values = construct_grid(name, GRID_SEEDS[name])["r_values"]
        assert all(left < right for left, right in zip(values, values[1:]))


def test_grids_deduplicate() -> None:
    for name in GRID_ORDER:
        values = construct_grid(name, GRID_SEEDS[name])["r_values"]
        for left, right in zip(values, values[1:]):
            assert abs(right - left) >= 2.0 * ulp_of_double(max(abs(left), abs(right)))


def test_grids_clamp_to_range() -> None:
    ref = sweep_r_values()
    for name in GRID_ORDER:
        values = construct_grid(name, GRID_SEEDS[name])["r_values"]
        assert all(ref[0] <= value <= ref[-1] for value in values)


def test_reference_grid_matches_sweep_r_values() -> None:
    assert construct_grid("reference", 0)["r_values"] == sweep_r_values()


def test_polarity_table_schema() -> None:
    for name in GRID_ORDER:
        grid = construct_grid(name, GRID_SEEDS[name])
        for precision in ("float32", "float64"):
            table = compute_polarity_table(grid, precision)
            assert {"grid_name", "precision", "n_after_dedup", "per_form_nonzero", "pairs"} <= set(table)
            for pair in PAIR_ORDER:
                pair_table = table["pairs"][pair]
                assert {
                    "cofire_count",
                    "same_sign_count",
                    "same_sign_fraction",
                    "p_one_tail_upper",
                    "p_one_tail_lower",
                    "p_two_tail",
                    "region_split",
                } <= set(pair_table)


def test_region_split_consistency() -> None:
    for name in GRID_ORDER:
        grid = construct_grid(name, GRID_SEEDS[name])
        for precision in ("float32", "float64"):
            table = compute_polarity_table(grid, precision)
            for pair in PAIR_ORDER:
                region_total = sum(region["cofire"] for region in table["pairs"][pair]["region_split"].values())
                assert region_total == table["pairs"][pair]["cofire_count"]


def test_negative_control_f1_f4() -> None:
    output = run_campaign()
    assert output["negative_control_passed"] is True
    assert output["aggregate_classifications"]["F1_F4"]["aggregate"] in {"depolarized_invariant", "open_underpowered"}


def test_f2_f4_underpromotion_guard() -> None:
    output = run_campaign()
    per_grid = output["aggregate_classifications"]["F2_F4"]["per_grid"]
    if any(status == "underpowered_grid" for status in per_grid.values()):
        assert output["aggregate_classifications"]["F2_F4"]["aggregate"] != "grid_stable_polarity_coupling"


def test_byte_stable_campaign_output() -> None:
    assert campaign_bytes() == campaign_bytes()
    assert json.dumps(run_campaign(), sort_keys=True, allow_nan=False) == json.dumps(run_campaign(), sort_keys=True, allow_nan=False)


def test_no_runtime_status_enum_additions() -> None:
    before = _status_values()
    import lloyd_v4.evals.polarity_grid_stability  # noqa: F401

    after = _status_values()
    assert after == before
    for report_status in ("grid_stable_supported", "depolarized_invariant", "negative_control_failed"):
        assert report_status not in after


def test_no_law_library_term_added() -> None:
    before = tuple(term.term_id for term in build_candidate_library())
    import lloyd_v4.evals.polarity_grid_stability  # noqa: F401

    after = tuple(term.term_id for term in build_candidate_library())
    assert after == before
    assert len(after) == 17


def test_p_value_computation_exact() -> None:
    assert _binomial_p_values(16, 16)["p_one_tail_upper"] == 2**-16


def test_f3_remains_zero() -> None:
    for name in GRID_ORDER:
        grid = construct_grid(name, GRID_SEEDS[name])
        for precision in ("float32", "float64"):
            table = compute_polarity_table(grid, precision)
            assert table["per_form_nonzero"]["F3"] == 0


def test_forbidden_import_grep_surface_is_clean() -> None:
    text = MODULE_PATH.read_text(encoding="utf-8")
    for token in ("numpy.random", "np.random", "scipy", "sympy", "mpmath", "math.pi", "math.e", "math.tau", "numpy.pi", "np.pi"):
        assert token not in text

    grid = construct_grid("reference", 0)
    overlap = compute_precision_overlap_invariance(grid)
    assert set(overlap["pairs"]) == set(PAIR_ORDER)
