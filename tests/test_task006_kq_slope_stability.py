import pytest

from lloyd_v4.branch import compare_kq_slope_stability
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import BranchFingerprintStatus
from lloyd_v4.metrology import calibrate_proxy_kq, proxy_uncalibrated
from lloyd_v4.primitives.projective_ratio import projective_ratio


def test_kq_flow_stable_and_unstable() -> None:
    stable = compare_kq_slope_stability(
        [1.0, 2.0, 4.0],
        [calibrate_proxy_kq(2.0, 1.0), calibrate_proxy_kq(4.0, 2.0), calibrate_proxy_kq(8.0, 4.0)],
        declared_stability_band=0.01,
    )
    unstable = compare_kq_slope_stability(
        [1.0, 2.0, 4.0],
        [calibrate_proxy_kq(2.0, 1.0), calibrate_proxy_kq(8.0, 2.0), calibrate_proxy_kq(8.0, 4.0)],
        declared_stability_band=0.01,
    )

    assert stable.status is BranchFingerprintStatus.KQ_FLOW_STABLE
    assert stable.value.stable is True
    assert stable.value.slope_flow_trace_id is not None
    assert unstable.status is BranchFingerprintStatus.KQ_FLOW_UNSTABLE
    assert unstable.value.stable is False


def test_kq_flow_indeterminate_without_declared_band_or_samples() -> None:
    missing_band = compare_kq_slope_stability(
        [1.0, 2.0],
        [calibrate_proxy_kq(2.0, 1.0), calibrate_proxy_kq(4.0, 2.0)],
        declared_stability_band=None,
    )
    insufficient = compare_kq_slope_stability([1.0], [calibrate_proxy_kq(2.0, 1.0)], declared_stability_band=0.1)

    assert missing_band.status is BranchFingerprintStatus.KQ_FLOW_INDETERMINATE
    assert insufficient.status is BranchFingerprintStatus.KQ_FLOW_INDETERMINATE


def test_kq_flow_uncalibrated_and_wrong_family_rejection() -> None:
    invalid = compare_kq_slope_stability(
        [1.0, 2.0],
        [calibrate_proxy_kq(2.0, 1.0), proxy_uncalibrated()],
        declared_stability_band=0.1,
    )

    assert invalid.status is BranchFingerprintStatus.KQ_FLOW_UNCALIBRATED
    assert invalid.value.refusal_reasons
    with pytest.raises(ProtocolViolationError):
        compare_kq_slope_stability([1.0, 2.0], [calibrate_proxy_kq(2.0, 1.0), projective_ratio(1, 2)], declared_stability_band=0.1)
