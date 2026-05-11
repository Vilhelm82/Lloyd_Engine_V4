import json

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import ProtocolStatus
from lloyd_v4.primitives.stratified_quadratic_roots import (
    select_quadratic_root,
    stratified_quadratic_roots,
)


def test_classification_result_serializes_with_evidence() -> None:
    result = stratified_quadratic_roots(1, -3, 2)

    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)

    assert payload["status"] == "two_real_roots"
    assert payload["value"]["coefficients"] == {"a": 1, "b": -3, "c": 2}
    assert payload["value"]["discriminant"] == 1
    assert payload["value"]["coordinates"]["minus"]["coordinate"] == {
        "numerator": 2.0,
        "denominator": 2,
    }
    assert payload["validity"]["defined"] is True
    assert payload["conditioning"]["status"] == "well_conditioned"
    assert payload["provenance"]["operation_id"] == "stratified_quadratic_roots"
    assert "NaN" not in encoded
    assert "Infinity" not in encoded


def test_selection_success_serializes_as_child_result() -> None:
    result = stratified_quadratic_roots(1, -3, 2)

    selected = select_quadratic_root(result, "minus")
    payload = to_json_safe(selected)
    encoded = json.dumps(payload, allow_nan=False)

    assert payload["value"] == 1.0
    assert payload["status"] == "two_real_roots"
    assert result.provenance.trace_id in payload["provenance"]["parents"]
    assert "NaN" not in encoded
    assert "Infinity" not in encoded


def test_selection_refusal_serializes_with_original_status() -> None:
    result = stratified_quadratic_roots(1, 0, 1)

    selected = select_quadratic_root(result, "minus")
    payload = to_json_safe(selected)
    encoded = json.dumps(payload, allow_nan=False)

    assert payload["value"] is None
    assert payload["status"] == "no_real_root"
    assert payload["protocol"] == ProtocolStatus.SCALARIZATION_REFUSED.value
    assert payload["refusal"]["details"]["quadratic_status"] == "no_real_root"
    assert "NaN" not in encoded
    assert "Infinity" not in encoded


def test_strict_serialization_encodes_nonfinite_scalar_payloads() -> None:
    payload = to_json_safe({"bad": float("inf")})
    encoded = json.dumps(payload, allow_nan=False)

    assert payload["bad"]["kind"] == "nonfinite_float"
    assert "Infinity" not in encoded
