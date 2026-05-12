import inspect
import os
import subprocess
import sys
from pathlib import Path

import lloyd_v4.primitives as primitives
from lloyd_v4.evals import multi_precision_four_form as multi_precision
from lloyd_v4.evals import path_law_campaign as campaign
from lloyd_v4.evals import path_law_discovery as discovery
from lloyd_v4.evals.schwarzschild_four_form import R_of_r, delta_f_of_r, f_of_r, sweep_r_values


ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_MODULE = ROOT / "src" / "lloyd_v4" / "evals" / "path_law_discovery.py"
CAMPAIGN_MODULE = ROOT / "src" / "lloyd_v4" / "evals" / "path_law_campaign.py"


def test_module_symbols_are_available_with_documented_call_surface() -> None:
    for name in (
        "build_candidate_library",
        "evaluate_terms",
        "fit_sparse_ols",
        "rank_fits",
        "validate_fit_axis_A",
        "validate_fit_axis_B",
        "validate_fit_axis_C",
        "validate_fit_axis_D",
        "validate_fit_axis_E",
        "validate_fit_axis_F",
        "classify_law",
        "discover_path_law_for_form",
    ):
        assert callable(getattr(discovery, name))

    assert "parsimony_tolerance" in inspect.signature(discovery.rank_fits).parameters


def test_candidate_library_has_exact_task025_terms() -> None:
    library = discovery.build_candidate_library()
    assert len(library) == 17
    assert tuple(term.term_id for term in library) == tuple(f"T_{index}" for index in range(1, 18))
    assert tuple(term.name for term in library) == (
        "one",
        "f",
        "R",
        "sqrt_f_alias",
        "inv_sqrt_f",
        "inv_r",
        "r_minus_2",
        "factored_f",
        "ulp_f",
        "ulp_R",
        "ulp_2_over_r",
        "delta_f",
        "delta_R",
        "delta_f_over_sqrt_f",
        "delta_f_over_2_sqrt_f",
        "delta_f_times_sqrt_f",
        "chain_envelope",
    )


def test_term_evaluation_correctness_at_r_four() -> None:
    r_value = 4.0
    f_value = 0.5
    r_sqrt = f_value**0.5
    expected = (
        1.0,
        f_value,
        r_sqrt,
        r_sqrt,
        1.0 / r_sqrt,
        0.25,
        2.0,
        0.5,
        multi_precision.ulp_of_double(f_value),
        multi_precision.ulp_of_double(r_sqrt),
        multi_precision.ulp_of_double(0.5),
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        multi_precision.predicted_chain_envelope(r_value),
    )
    actual = discovery.evaluate_terms(discovery.build_candidate_library(), (r_value,))[0]

    for observed, wanted in zip(actual, expected, strict=True):
        if wanted == 0.0:
            assert observed == 0.0
        else:
            assert abs(observed - wanted) <= multi_precision.ulp_of_double(wanted)


def test_sparse_ols_recovers_synthetic_t15_law() -> None:
    r_values = tuple(value for value in sweep_r_values() if delta_f_of_r(value) != 0.0)
    library = discovery.build_candidate_library()
    matrix = discovery.evaluate_terms(library, r_values)
    term_ids = tuple(term.term_id for term in library)
    t15_index = term_ids.index("T_15")
    y = tuple(2.0 * row[t15_index] for row in matrix)

    ranked = discovery.rank_fits(discovery.fit_sparse_ols(matrix, y, max_terms=1, term_ids=term_ids))
    top = ranked[0]

    assert top.terms == ("T_15",)
    assert 1.98 <= top.coefficients[0] <= 2.02


def test_f3_classifies_as_exact_zero() -> None:
    value = discovery.discover_path_law_for_form("F3", sweep_r_values())

    assert value.status == "path_law_exact_zero"
    assert value.selected_law == {"terms": [], "coefficients": [], "r_squared": 1.0, "law": "0"}


def test_f4_rediscovery_gate_selects_t15() -> None:
    value = discovery.discover_path_law_for_form("F4", sweep_r_values())

    assert value.top_ranked_1_term_fit["terms"] == ["T_15"]
    assert value.rediscovery_gate["winning_term"] == "T_15"
    assert value.rediscovery_gate["passed"] is True


def test_f4_t15_coefficient_is_in_expected_range() -> None:
    value = discovery.discover_path_law_for_form("F4", sweep_r_values())
    coefficient = value.top_ranked_1_term_fit["coefficients"][0]

    assert 0.5 <= coefficient <= 2.0
    assert value.top_ranked_1_term_fit["r_squared"] >= 0.95


def test_precision_scaling_axis_runs_for_all_nonzero_forms() -> None:
    output = campaign.run_campaign()

    for form_id in ("F1", "F2", "F4"):
        axis_b = output["forms"][form_id]["validation_results"]["B"]
        assert axis_b["status"] in {"precision_scaling_supported", "precision_scaling_failed"}
        assert isinstance(axis_b["passed"], bool)
        assert "ratio_count" in axis_b["metrics"]


def test_campaign_output_is_deterministic_across_processes(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

    for path in (first, second):
        subprocess.run(
            [sys.executable, "-m", "lloyd_v4.evals.path_law_campaign", "--output", str(path)],
            cwd=ROOT,
            env=env,
            check=True,
        )

    assert first.read_bytes() == second.read_bytes()


def test_path_law_sources_obey_task025_import_discipline() -> None:
    forbidden = (
        "import math",
        "from math",
        "numpy.sqrt",
        "numpy.linalg",
        "scipy",
        "sympy",
        "sklearn",
        "mpmath",
        "lloyd_v3",
    )
    for path in (DISCOVERY_MODULE, CAMPAIGN_MODULE):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text

    discovery_text = DISCOVERY_MODULE.read_text(encoding="utf-8")
    assert "np.linalg.lstsq" in discovery_text
    assert "from decimal import" not in discovery_text


def test_primitives_exports_unchanged_by_path_law_campaign() -> None:
    assert len(primitives.__all__) == 65
    assert "path_law_discovery" not in primitives.__all__
    assert "path_law_campaign" not in primitives.__all__


def test_f4_known_term_matches_fixture_to_first_order() -> None:
    ratios = []
    for r_value in sweep_r_values():
        observed = multi_precision.four_form_float64(r_value)["F4"]
        predicted = delta_f_of_r(r_value) / (2.0 * R_of_r(r_value))
        if observed != 0.0 and predicted != 0.0:
            ratios.append(observed / predicted)

    assert len(ratios) >= 80
    assert 0.8 <= sorted(ratios)[len(ratios) // 2] <= 1.2
