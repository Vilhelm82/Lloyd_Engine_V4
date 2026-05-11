import json

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.metrology import (
    calibrate_proxy_kq,
    classify_against_noise_floor,
    declare_bk_noise_floor,
    estimate_bk_noise_floor,
    proxy_uncalibrated,
)


def _encoded(value):
    payload = to_json_safe(value)
    return payload, json.dumps(payload, allow_nan=False)


def test_noise_floor_and_detection_serialization() -> None:
    declared = declare_bk_noise_floor(1e-6, measurement_resolution=1e-9)
    estimated = estimate_bk_noise_floor([1e-7, -2e-7])
    indeterminate = estimate_bk_noise_floor([])
    detected = classify_against_noise_floor(2e-6, declared)
    below = classify_against_noise_floor(0.0, declared)
    zero_floor = classify_against_noise_floor(0.0, declare_bk_noise_floor(0.0))
    identity = classify_against_noise_floor(0.0, declared, identity_evidence=True)

    declared_payload, declared_json = _encoded(declared)
    estimated_payload, estimated_json = _encoded(estimated)
    indeterminate_payload, _ = _encoded(indeterminate)
    detected_payload, _ = _encoded(detected)
    below_payload, _ = _encoded(below)
    zero_payload, _ = _encoded(zero_floor)
    identity_payload, _ = _encoded(identity)

    assert declared_payload["value"]["noise_floor"] == 1e-6
    assert declared_payload["value"]["measurement_resolution"] == 1e-9
    assert estimated_payload["value"]["method"] == "max_abs_observed"
    assert estimated_payload["value"]["sample_count"] == 2
    assert indeterminate_payload["status"] == "noise_floor_indeterminate"
    assert detected_payload["value"]["comparison"] == "above_limit"
    assert below_payload["value"]["comparison"] == "below_limit"
    assert zero_payload["value"]["comparison"] == "exact_zero_without_identity_evidence"
    assert identity_payload["value"]["identity_evidence"] is True
    assert "NaN" not in declared_json
    assert "Infinity" not in estimated_json


def test_kq_and_uncalibrated_serialization() -> None:
    valid = calibrate_proxy_kq(6.0, 3.0)
    invalid = calibrate_proxy_kq(6.0, 0.0)
    indeterminate = calibrate_proxy_kq(0.0, 0.0)
    missing = proxy_uncalibrated(reason="missing")

    valid_payload, valid_json = _encoded(valid)
    invalid_payload, invalid_json = _encoded(invalid)
    indeterminate_payload, indeterminate_json = _encoded(indeterminate)
    missing_payload, _ = _encoded(missing)

    assert valid_payload["value"]["kq_projective_coordinates"] == {"numerator": 6.0, "denominator": 3.0}
    assert valid_payload["value"]["kq_scalar_value"] == 2.0
    assert invalid_payload["value"]["kq_projective_status"] == "infinite_direction"
    assert invalid_payload["value"]["kq_scalar_value"] is None
    assert indeterminate_payload["value"]["refusal_evidence"] is not None
    assert missing_payload["value"]["reason"] == "missing"
    assert "Infinity" not in invalid_json
    assert "NaN" not in indeterminate_json
    assert "Infinity" not in valid_json


def test_strict_serialization_still_encodes_nonfinite_payloads() -> None:
    payload = to_json_safe({"bad": float("-inf")})
    encoded = json.dumps(payload, allow_nan=False)

    assert payload["bad"]["kind"] == "nonfinite_float"
    assert "Infinity" not in encoded
