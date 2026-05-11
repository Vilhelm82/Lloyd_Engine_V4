import math

import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import MetrologyStatus
from lloyd_v4.metrology import calibrate_proxy_kq, proxy_uncalibrated


def test_valid_kq_calibration_uses_projective_ratio_and_scalarizes() -> None:
    result = calibrate_proxy_kq(6.0, 3.0, frequency_label="10Hz")

    assert result.status is MetrologyStatus.CALIBRATION_VALID
    assert result.value.proxy_observable == 6.0
    assert result.value.transfer_observable == 3.0
    assert result.value.frequency_label == "10Hz"
    assert result.value.kq_projective_coordinates == {"numerator": 6.0, "denominator": 3.0}
    assert result.value.kq_projective_status == "finite_ratio"
    assert result.value.kq_scalar_value == 2.0
    assert result.value.kq_projective_trace_id in result.provenance.parents
    assert result.value.kq_scalar_trace_id in result.provenance.parents


def test_invalid_kq_calibration_preserves_projective_statuses_without_numeric_sentinel() -> None:
    zero_proxy = calibrate_proxy_kq(0.0, 3.0)
    zero_transfer = calibrate_proxy_kq(6.0, 0.0)

    assert zero_proxy.status is MetrologyStatus.CALIBRATION_INVALID
    assert zero_proxy.value.kq_projective_status == "signed_zero"
    assert zero_proxy.value.kq_scalar_value is None
    assert zero_proxy.value.kq_scalar_trace_id is not None

    assert zero_transfer.status is MetrologyStatus.CALIBRATION_INVALID
    assert zero_transfer.value.kq_projective_status == "infinite_direction"
    assert zero_transfer.value.kq_scalar_value is None
    assert zero_transfer.value.refusal_evidence is not None


def test_indeterminate_kq_calibration_preserves_refusal_evidence() -> None:
    result = calibrate_proxy_kq(0.0, 0.0)

    assert result.status is MetrologyStatus.CALIBRATION_INDETERMINATE
    assert result.value.kq_projective_status == "indeterminate"
    assert result.value.kq_scalar_value is None
    assert result.value.refusal_evidence is not None


def test_proxy_uncalibrated_is_typed_missing_evidence() -> None:
    result = proxy_uncalibrated(proxy_label="Y_sensor", reason="not_measured")

    assert result.status is MetrologyStatus.PROXY_UNCALIBRATED
    assert result.value.proxy_label == "Y_sensor"
    assert result.value.reason == "not_measured"
    assert result.validity.defined is False
    assert result.validity.observable is True


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_nonfinite_proxy_or_transfer_rejected(bad: float) -> None:
    with pytest.raises(ProtocolViolationError):
        calibrate_proxy_kq(bad, 1.0)

    with pytest.raises(ProtocolViolationError):
        calibrate_proxy_kq(1.0, bad)
