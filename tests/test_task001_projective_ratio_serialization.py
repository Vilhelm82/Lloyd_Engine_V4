import json

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import ProtocolStatus
from lloyd_v4.primitives.projective_ratio import projective_ratio, scalarize_projective_ratio


def test_projective_ratio_result_serializes_strictly() -> None:
    result = projective_ratio(1, 0)

    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)

    assert payload["value"] == {"numerator": 1, "denominator": 0}
    assert payload["status"] == "infinite_direction"
    assert "NaN" not in encoded
    assert "Infinity" not in encoded


def test_refused_scalarization_is_typed_and_serializable() -> None:
    ratio = projective_ratio(0, 0)

    scalar = scalarize_projective_ratio(ratio)
    payload = to_json_safe(scalar)
    encoded = json.dumps(payload, allow_nan=False)

    assert payload["protocol"] == ProtocolStatus.SCALARIZATION_REFUSED.value
    assert payload["refusal"]["status"] == ProtocolStatus.SCALARIZATION_REFUSED.value
    assert payload["refusal"]["details"]["projective_status"] == "indeterminate"
    assert "NaN" not in encoded
    assert "Infinity" not in encoded
