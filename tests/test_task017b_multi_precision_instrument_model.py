from pathlib import Path

import lloyd_v4.primitives as primitives
from lloyd_v4.evals import multi_precision_campaign as campaign
from lloyd_v4.evals import multi_precision_four_form as multi_precision
from lloyd_v4.evals.schwarzschild_four_form import sweep_r_values


ROOT = Path(__file__).resolve().parents[1]
MULTI_PRECISION_MODULE = ROOT / "src" / "lloyd_v4" / "evals" / "multi_precision_four_form.py"
CAMPAIGN_MODULE = ROOT / "src" / "lloyd_v4" / "evals" / "multi_precision_campaign.py"


def test_multi_precision_module_symbols_are_available() -> None:
    for name in (
        "four_form_float32",
        "four_form_float64",
        "four_form_decimal_oracle",
        "ulp_of_double",
        "predicted_chain_envelope",
    ):
        assert callable(getattr(multi_precision, name))


def test_float32_has_larger_f4_residuals_than_float64_on_many_points() -> None:
    larger_count = 0
    for r_value in sweep_r_values():
        f32 = abs(multi_precision.four_form_float32(r_value)["F4"])
        f64 = abs(multi_precision.four_form_float64(r_value)["F4"])
        if f32 > f64:
            larger_count += 1

    assert larger_count >= 10


def test_phase_a_records_result_ulp_bound_failure_pattern() -> None:
    output = campaign.run_campaign()
    phase_a = output["phase_a"]
    f4 = phase_a["forms"]["F4"]

    assert output["model_supported"] is False
    assert phase_a["pass"] is False
    assert f4["pass"] is False
    assert f4["float64_nonzero_count"] == 92
    assert f4["result_bound_exceed_count"] == f4["float64_nonzero_count"]
    assert f4["median_ratio_to_result_bound"] > 1e14
    assert 0.99 <= f4["median_residual_over_abs_float64"] <= 1.01
    assert f4["near_field_nonzero_count"] > f4["middle_field_nonzero_count"] > f4["far_field_nonzero_count"]
    assert f4["near_field_median_residual"] > f4["middle_field_median_residual"]

    assert f4["chain_diagnostic_pass"] is True
    assert f4["exceed_allowed_chain_count"] == 0


def test_phase_b_scaling_ratio_matches_float_unit_ratio_order() -> None:
    phase_b = campaign.run_campaign()["phase_b"]

    assert phase_b["both_nonzero_count"] >= 10
    assert phase_b["float32_strictly_larger_count"] >= 10
    assert phase_b["pass"] is True
    assert phase_b["expected_ratio"] == multi_precision.FLOAT32_TO_FLOAT64_UNIT_RATIO
    assert 0.2 <= phase_b["observed_over_expected"] <= 5.0


def test_phase_c_f3_is_exact_zero_at_all_precisions() -> None:
    for r_value in sweep_r_values():
        assert multi_precision.four_form_float32(r_value)["F3"] == 0.0
        assert multi_precision.four_form_float64(r_value)["F3"] == 0.0
        assert multi_precision.four_form_decimal_oracle(r_value, 50)["F3"] == 0.0

    phase_c = campaign.run_campaign()["phase_c"]
    assert phase_c["pass"] is True
    assert phase_c["nonzero_count"] == 0


def test_multi_precision_campaign_output_is_deterministic(tmp_path: Path) -> None:
    first = campaign.campaign_bytes()
    second = campaign.campaign_bytes()
    assert first == second

    output_path = tmp_path / "multi_precision.json"
    campaign.write_campaign_output(output_path)
    assert output_path.read_bytes() == first


def test_multi_precision_sources_obey_import_discipline() -> None:
    forbidden = (
        "import math",
        "from math",
        "numpy.sqrt",
        "numpy.linalg",
        "scipy",
        "sympy",
        "mpmath",
        "lloyd_v3",
    )
    for path in (MULTI_PRECISION_MODULE, CAMPAIGN_MODULE):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text

    utility_text = MULTI_PRECISION_MODULE.read_text(encoding="utf-8")
    decimal_import = utility_text.index("from decimal import")
    oracle_start = utility_text.index("def four_form_decimal_oracle")
    assert decimal_import > oracle_start
    assert "Decimal" not in CAMPAIGN_MODULE.read_text(encoding="utf-8")


def test_primitives_exports_unchanged_by_multi_precision_campaign() -> None:
    assert len(primitives.__all__) == 65
    assert "multi_precision_four_form" not in primitives.__all__
    assert "multi_precision_campaign" not in primitives.__all__
