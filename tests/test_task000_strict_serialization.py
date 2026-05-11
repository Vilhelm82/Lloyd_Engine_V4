import json
import math

from lloyd_v4.core.serialization import to_json_safe


def test_strict_json_serialization_encodes_nonfinite_floats() -> None:
    payload = to_json_safe(
        {
            "nan": math.nan,
            "pos_inf": math.inf,
            "neg_inf": -math.inf,
            "finite": 1.25,
        }
    )
    encoded = json.dumps(payload, allow_nan=False)

    assert '"nonfinite_float"' in encoded
    assert "NaN" not in encoded
    assert "Infinity" not in encoded
    assert payload["finite"] == 1.25
