import os
import subprocess
import sys
from pathlib import Path

import lloyd_v4.primitives as primitives
from lloyd_v4.evals import lattice_anomaly_campaign as campaign


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_MODULE = ROOT / "src" / "lloyd_v4" / "evals" / "lattice_anomaly_campaign.py"


def test_module_symbols_are_available() -> None:
    for name in (
        "run_submodule_A_lattice",
        "run_submodule_B_f2_anomaly",
        "run_submodule_C_phase_b_spread",
        "run_submodule_D_cross_form",
        "run_submodule_E_sign_pattern",
        "run_campaign",
        "write_campaign_output",
        "campaign_bytes",
        "extract_double_bits",
        "integer_level_or_none",
        "bootstrap_median_ratios",
        "correlation_with_bit_pattern",
    ):
        assert callable(getattr(campaign, name))


def test_campaign_bytes_are_deterministic_in_process() -> None:
    assert campaign.campaign_bytes() == campaign.campaign_bytes()


def test_submodule_a_f3_lattice_is_empty_at_all_precisions() -> None:
    output = campaign.run_campaign()["submodules"]["A_lattice_structure"]
    by_precision = output["by_form"]["F3"]["by_precision"]

    for precision in ("float32", "float64", "decimal_50"):
        assert by_precision[precision]["candidate_classification"] == "lattice_empty"
        assert by_precision[precision]["n_nonzero"] == 0


def test_submodule_a_f4_float64_is_integer_lattice() -> None:
    output = campaign.run_campaign()["submodules"]["A_lattice_structure"]
    f4 = output["by_form"]["F4"]["by_precision"]["float64"]

    assert f4["candidate_classification"] == "lattice_integer"
    assert 20 <= f4["n_distinct_levels"] <= 50
    assert f4["level_integer_residual_max"] < 1e-3


def test_submodule_b_f2_anomaly_record_count_and_hypotheses() -> None:
    output = campaign.run_campaign()["submodules"]["B_f2_anomaly"]

    assert output["n_nonzero_float64"] == 28
    assert len(output["per_point_records"]) == 28
    for key in (
        "hypothesis_1_small_sample",
        "hypothesis_2_float32_mostly_zero",
        "hypothesis_3_sign_disagreement",
        "hypothesis_4_lattice_mismatch",
    ):
        assert isinstance(output[key]["supported"], bool)


def test_submodule_c_overlap_count_and_prediction_test() -> None:
    output = campaign.run_campaign()["submodules"]["C_phase_b_spread"]
    prediction = output["quantisation_prediction_test"]

    assert 60 <= output["n_overlap_points"] <= 80
    assert isinstance(prediction["supported"], bool)
    assert isinstance(prediction["n_predicted_within_factor_2"], int)
    assert isinstance(prediction["n_predicted_within_factor_4"], int)


def test_submodule_d_sum_cancellation_scale() -> None:
    output = campaign.run_campaign()["submodules"]["D_cross_form"]

    assert output["sum_F1_F2_F3_F4"]["max_abs"] < 1e-14


def test_submodule_d_correlation_matrix_structure() -> None:
    matrix = campaign.run_campaign()["submodules"]["D_cross_form"]["correlation_matrix_pearson"]

    assert len(matrix) == 4
    assert all(len(row) == 4 for row in matrix)
    for index in range(4):
        assert matrix[index][index] == 1.0
    for index in range(4):
        assert matrix[2][index] == (1.0 if index == 2 else 0.0)
        assert matrix[index][2] == (1.0 if index == 2 else 0.0)
    for left in range(4):
        for right in range(4):
            assert matrix[left][right] == matrix[right][left]
            assert -1.0 <= matrix[left][right] <= 1.0


def test_submodule_e_sign_counts_add_to_sweep_size() -> None:
    output = campaign.run_campaign()["submodules"]["E_sign_pattern"]

    for form_id, form in output["per_form"].items():
        assert form["n_pos"] + form["n_neg"] + form["n_zero"] == 137
        if form_id == "F3":
            assert form["n_pos"] == 0
            assert form["n_neg"] == 0
            assert form["n_zero"] == 137


def test_cross_validation_against_prior_task_counts() -> None:
    output = campaign.run_campaign()["submodules"]

    assert output["A_lattice_structure"]["by_form"]["F4"]["by_precision"]["float64"]["n_nonzero"] == 92
    assert output["B_f2_anomaly"]["n_nonzero_float64"] == 28
    assert output["E_sign_pattern"]["per_form"]["F3"]["n_zero"] == 137


def test_campaign_output_is_deterministic_across_processes(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

    for path in (first, second):
        subprocess.run(
            [sys.executable, "-m", "lloyd_v4.evals.lattice_anomaly_campaign", "--output", str(path)],
            cwd=ROOT,
            env=env,
            check=True,
        )

    assert first.read_bytes() == second.read_bytes()


def test_lattice_anomaly_source_purity() -> None:
    text = CAMPAIGN_MODULE.read_text(encoding="utf-8")
    forbidden = (
        "import math",
        "from math",
        "import scipy",
        "import sympy",
        "import sklearn",
        "import mpmath",
        "numpy.sqrt",
        "np.sqrt",
        "numpy.cos",
        "np.cos",
        "numpy.exp",
        "np.exp",
    )
    for token in forbidden:
        assert token not in text

    decimal_import = text.index("from decimal import")
    oracle_start = text.index("def _factored_sqrt_round_dir")
    assert decimal_import > oracle_start


def test_primitives_exports_unchanged_by_lattice_campaign() -> None:
    assert len(primitives.__all__) == 65
    assert "lattice_anomaly_campaign" not in primitives.__all__
