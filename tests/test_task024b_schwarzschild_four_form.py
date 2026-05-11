import csv
from pathlib import Path

import lloyd_v4.primitives as primitives
from lloyd_v4.core.status import SlopeStatus, TransferStatus
from lloyd_v4.evals import schwarzschild_four_form as fixture
from lloyd_v4.evals import schwarzschild_four_form_campaign as campaign
from lloyd_v4.primitives import AlphaWindowStabilityStatus


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task024b_schwarzschild_four_form"
CSV_PATH = REPORT_DIR / "v3_reference_overlay.csv"


def test_task024b_modules_exist_after_landing() -> None:
    assert (ROOT / "src" / "lloyd_v4" / "evals" / "schwarzschild_four_form.py").is_file()
    assert (ROOT / "src" / "lloyd_v4" / "evals" / "schwarzschild_four_form_campaign.py").is_file()


def test_fixture_module_symbols_and_sweep() -> None:
    for name in ("f_of_r", "R_of_r", "F1_of_r", "F2_of_r", "F3_of_r", "F4_of_r", "delta_f_of_r", "sweep_r_values"):
        assert callable(getattr(fixture, name))

    r_values = fixture.sweep_r_values()
    assert len(r_values) == 137
    assert r_values == tuple(sorted(r_values))
    assert r_values[0] == 2.005
    assert r_values[-1] == 10.0


def test_v3_reference_overlay_agrees_with_fixture_within_one_ulp_column() -> None:
    columns = {
        "f_re": fixture.f_of_r,
        "R": fixture.R_of_r,
        "F1": fixture.F1_of_r,
        "F2": fixture.F2_of_r,
        "F3": fixture.F3_of_r,
        "F4": fixture.F4_of_r,
        "delta_f": fixture.delta_f_of_r,
    }

    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = tuple(csv.DictReader(handle))

    assert len(rows) == 137
    for row_index, row in enumerate(rows):
        r_value = float(row["re"])
        ulp = float(row["ulp_f"])
        for column, function in columns.items():
            expected = float(row[column])
            actual = function(r_value)
            if expected == 0.0:
                assert actual == 0.0, (row_index, column, expected, actual)
            else:
                assert abs(actual - expected) <= ulp, (row_index, column, expected, actual, abs(actual - expected) / ulp)


def test_stratum_pattern_across_four_forms() -> None:
    output = campaign.run_campaign()
    forms = output["forms"]

    f3_transfers = forms["F3"]["transfers"]
    assert len(f3_transfers) == 136
    assert all(item["status"] == TransferStatus.TRANSFER_OBSERVED.value for item in f3_transfers)
    assert all(item["transfer"] == 0.0 for item in f3_transfers)

    allowed = {TransferStatus.TRANSFER_OBSERVED.value, TransferStatus.TRANSFER_CANCELLATION_DOMINATED.value}
    for name in ("F1", "F2", "F4"):
        assert set(forms[name]["transfer_counts"]).issubset(allowed)
        assert sum(forms[name]["transfer_counts"].values()) == 136


def test_slope_fit_non_crash_for_non_degenerate_forms() -> None:
    output = campaign.run_campaign()
    forms = output["forms"]

    assert forms["F4"]["slope"]["status"] in {
        SlopeStatus.SLOPE_OBSERVED.value,
        SlopeStatus.SLOPE_INSUFFICIENT_DATA.value,
    }
    assert forms["F4"]["slope"]["value"]["slope"] is None or isinstance(forms["F4"]["slope"]["value"]["slope"], float)
    assert forms["F3"]["slope"]["status"] in {
        SlopeStatus.SLOPE_INSUFFICIENT_DATA.value,
        SlopeStatus.SLOPE_DEGENERATE_INPUT.value,
    }
    assert forms["F3"]["slope"]["value"]["slope"] is None


def test_alpha_probe_reliability_fields_are_self_consistent() -> None:
    output = campaign.run_campaign()
    for form in output["forms"].values():
        alpha = form["alpha_probe"]
        if alpha["alpha_stability_status"] == AlphaWindowStabilityStatus.NOT_TESTED.value:
            assert alpha["alpha_window_min"] is None
            assert alpha["alpha_window_max"] is None
            assert alpha["alpha_window_span"] is None
            assert alpha["propagated_window_error"] is None
            continue

        assert alpha["alpha_window_min"] is not None
        assert alpha["alpha_window_max"] is not None
        assert alpha["alpha_window_span"] is not None
        assert alpha["propagated_window_error"] is not None
        assert alpha["alpha_window_min"] <= alpha["alpha_window_max"]
        assert alpha["alpha_window_span"] >= 0.0
        assert alpha["nested_window_fit_count"] >= 3


def test_campaign_output_is_deterministic(tmp_path: Path) -> None:
    first = campaign.campaign_bytes()
    second = campaign.campaign_bytes()
    assert first == second

    output_path = tmp_path / "campaign_output.json"
    campaign.write_campaign_output(output_path)
    assert output_path.read_bytes() == first


def test_evals_modules_have_no_legacy_or_external_math_imports() -> None:
    forbidden = (
        "import math",
        "from math",
        "numpy.linalg",
        "scipy",
        "sympy",
        "mpmath",
        "lloyd_v3",
    )
    for path in (
        ROOT / "src" / "lloyd_v4" / "evals" / "schwarzschild_four_form.py",
        ROOT / "src" / "lloyd_v4" / "evals" / "schwarzschild_four_form_campaign.py",
    ):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text


def test_primitives_exports_unchanged_by_campaign() -> None:
    assert len(primitives.__all__) == 65
    assert "schwarzschild_four_form" not in primitives.__all__
    assert "schwarzschild_four_form_campaign" not in primitives.__all__
