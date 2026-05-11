import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import MetrologyStatus, ProtocolStatus
from lloyd_v4.metrology import (
    calibrate_proxy_kq,
    proxy_uncalibrated,
    require_valid_proxy_calibration,
)
from lloyd_v4.primitives.projective_ratio import projective_ratio


def test_require_valid_proxy_calibration_accepts_valid_child() -> None:
    calibration = calibrate_proxy_kq(6.0, 3.0)

    accepted = require_valid_proxy_calibration(calibration)

    assert accepted.status is MetrologyStatus.CALIBRATION_VALID
    assert accepted.protocol is ProtocolStatus.OK
    assert accepted.value.parent_calibration_trace_id == calibration.provenance.trace_id
    assert calibration.provenance.trace_id in accepted.provenance.parents


def test_require_valid_proxy_calibration_refuses_invalid_indeterminate_and_uncalibrated() -> None:
    cases = [
        calibrate_proxy_kq(0.0, 3.0),
        calibrate_proxy_kq(0.0, 0.0),
        proxy_uncalibrated(),
    ]

    for calibration in cases:
        result = require_valid_proxy_calibration(calibration)

        assert result.value is None
        assert result.protocol is ProtocolStatus.SCALARIZATION_REFUSED
        assert result.refusal is not None
        assert result.refusal.details["calibration_status"] == calibration.status.value


def test_require_valid_proxy_calibration_rejects_raw_or_unrelated_result() -> None:
    with pytest.raises(ProtocolViolationError):
        require_valid_proxy_calibration(2.0)

    with pytest.raises(ProtocolViolationError):
        require_valid_proxy_calibration(projective_ratio(1, 2))
