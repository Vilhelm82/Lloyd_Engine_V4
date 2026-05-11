import math

import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import MetrologyStatus
from lloyd_v4.metrology import (
    classify_against_noise_floor,
    declare_bk_noise_floor,
    estimate_bk_noise_floor,
)
from lloyd_v4.primitives.projective_ratio import projective_ratio


def test_declared_noise_floor_records_evidence() -> None:
    result = declare_bk_noise_floor(1e-6, unit="m", measurement_resolution=1e-9)

    assert result.status is MetrologyStatus.NOISE_FLOOR_DECLARED
    assert result.value.label == "b_k"
    assert result.value.noise_floor == 1e-6
    assert result.value.method == "declared"
    assert result.value.unit == "m"
    assert result.value.measurement_resolution == 1e-9
    assert result.value.sample_count == 0
    assert result.value.observations == ()
    assert result.validity.defined is True


def test_estimated_noise_floor_uses_max_abs_observed() -> None:
    result = estimate_bk_noise_floor([1e-7, -2e-7, 5e-8])

    assert result.status is MetrologyStatus.NOISE_FLOOR_ESTIMATED
    assert result.value.noise_floor == 2e-7
    assert result.value.method == "max_abs_observed"
    assert result.value.sample_count == 3
    assert result.value.observations == (1e-7, -2e-7, 5e-8)


def test_empty_observations_are_indeterminate() -> None:
    result = estimate_bk_noise_floor([])

    assert result.status is MetrologyStatus.NOISE_FLOOR_INDETERMINATE
    assert result.value.noise_floor is None
    assert result.value.sample_count == 0
    assert result.validity.defined is False


@pytest.mark.parametrize("bad_floor", [-1.0, math.nan, math.inf, -math.inf])
def test_invalid_declared_noise_floor_rejected(bad_floor: float) -> None:
    with pytest.raises(ProtocolViolationError):
        declare_bk_noise_floor(bad_floor)


def test_invalid_observation_or_method_rejected() -> None:
    with pytest.raises(ProtocolViolationError):
        estimate_bk_noise_floor([0.0, math.inf])

    with pytest.raises(ProtocolViolationError):
        estimate_bk_noise_floor([1.0], method="median")


def test_all_zero_observations_estimate_zero_but_do_not_certify_identity() -> None:
    floor = estimate_bk_noise_floor([0.0, 0.0])
    classified = classify_against_noise_floor(0.0, floor)

    assert floor.status is MetrologyStatus.NOISE_FLOOR_ESTIMATED
    assert floor.value.noise_floor == 0.0
    assert classified.status is MetrologyStatus.DETECTION_INDETERMINATE


def test_limit_of_detection_classification_semantics() -> None:
    floor = declare_bk_noise_floor(1e-6, unit="m")

    detected = classify_against_noise_floor(2e-6, floor, observable_label="x")
    below = classify_against_noise_floor(5e-7, floor)
    on_limit = classify_against_noise_floor(1e-6, floor)
    zero_without_identity = classify_against_noise_floor(0.0, floor)
    identity = classify_against_noise_floor(0.0, floor, identity_evidence=True)

    assert detected.status is MetrologyStatus.DETECTED
    assert detected.value.comparison == "above_limit"
    assert detected.value.noise_floor_trace_id == floor.provenance.trace_id
    assert detected.value.unit == "m"

    assert below.status is MetrologyStatus.BELOW_LIMIT_OF_DETECTION
    assert below.value.comparison == "below_limit"
    assert on_limit.status is MetrologyStatus.BELOW_LIMIT_OF_DETECTION
    assert on_limit.value.comparison == "on_limit"
    assert zero_without_identity.status is MetrologyStatus.BELOW_LIMIT_OF_DETECTION
    assert zero_without_identity.value.comparison == "below_limit"
    assert identity.status is MetrologyStatus.IDENTITY_ZERO
    assert identity.value.identity_evidence is True


def test_identity_evidence_requires_exact_zero() -> None:
    floor = declare_bk_noise_floor(1e-6)

    with pytest.raises(ProtocolViolationError):
        classify_against_noise_floor(2.0, floor, identity_evidence=True)


def test_zero_observable_with_zero_floor_is_indeterminate_without_identity() -> None:
    floor = declare_bk_noise_floor(0.0)
    result = classify_against_noise_floor(0.0, floor)

    assert result.status is MetrologyStatus.DETECTION_INDETERMINATE
    assert result.value.comparison == "exact_zero_without_identity_evidence"


def test_detection_rejects_raw_or_unrelated_floor_evidence() -> None:
    with pytest.raises(ProtocolViolationError):
        classify_against_noise_floor(1.0, 1e-6)

    with pytest.raises(ProtocolViolationError):
        classify_against_noise_floor(1.0, projective_ratio(1, 2))
