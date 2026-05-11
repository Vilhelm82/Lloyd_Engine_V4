import json
import math

import pytest

from lloyd_v4.core.conditioning import ConditioningStatus
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import TransferStatus
from lloyd_v4.primitives import (
    TRANSFER_OBSERVATION_CONSUMER_PROTOCOL,
    typed_finite_difference,
)


def test_observed_stratum_clean_linear_function() -> None:
    result = typed_finite_difference(lambda x: 2.0 * x, 1.0, 0.5, function_label="linear_2x")

    assert result.status is TransferStatus.TRANSFER_OBSERVED
    assert result.value.transfer == 2.0
    assert result.validity.finite is True
    assert result.validity.selectable is True
    assert result.conditioning.status is ConditioningStatus.WELL_CONDITIONED


def test_observed_stratum_quadratic() -> None:
    result = typed_finite_difference(lambda x: x * x, 1.0, 0.001, function_label="square")

    assert result.status is TransferStatus.TRANSFER_OBSERVED
    assert abs(result.value.transfer - 2.001) < 1e-12


def test_observed_stratum_both_endpoints_zero() -> None:
    result = typed_finite_difference(lambda x: 0.0, 1.0, 0.01, function_label="zero")

    assert result.status is TransferStatus.TRANSFER_OBSERVED
    assert result.value.transfer == 0.0
    assert result.value.cancellation_ratio is None


def test_cancellation_dominated_stratum() -> None:
    result = typed_finite_difference(lambda x: 1.0 + 1e-20 * x, 1.0, 0.01, function_label="cancel")

    assert result.status is TransferStatus.TRANSFER_CANCELLATION_DOMINATED
    assert result.validity.finite is True
    assert result.validity.selectable is False
    assert any("cancellation_ratio" in note for note in result.conditioning.notes)


def test_non_finite_stratum_overflow() -> None:
    def g(x: float) -> float:
        return x * 1e308 if x < 2 else float("inf")

    result = typed_finite_difference(g, 1.5, 1.0, function_label="overflow_at_2")

    assert result.status is TransferStatus.TRANSFER_NON_FINITE
    assert result.validity.finite is False


def test_non_finite_stratum_nan() -> None:
    result = typed_finite_difference(lambda x: math.nan, 1.0, 0.01, function_label="nan_function")

    assert result.status is TransferStatus.TRANSFER_NON_FINITE


def test_domain_refused_stratum_exception() -> None:
    def g(x: float) -> float:
        raise ValueError("not defined here")

    result = typed_finite_difference(g, 1.0, 0.01, function_label="raises")

    assert result.status is TransferStatus.TRANSFER_DOMAIN_REFUSED
    assert result.validity.defined is False


def test_domain_refused_stratum_non_numeric() -> None:
    result = typed_finite_difference(lambda x: "not a number", 1.0, 0.01, function_label="returns_string")

    assert result.status is TransferStatus.TRANSFER_DOMAIN_REFUSED


def test_delta_indeterminate_stratum() -> None:
    result = typed_finite_difference(lambda x: x * x, 1.0, 0.0, function_label="delta_zero")

    assert result.status is TransferStatus.TRANSFER_DELTA_INDETERMINATE
    assert result.value.transfer is None
    assert result.validity.defined is False


def test_non_finite_f_raises() -> None:
    with pytest.raises(ProtocolViolationError):
        typed_finite_difference(lambda x: x, float("inf"), 0.01, function_label="x")


def test_nan_delta_f_raises() -> None:
    with pytest.raises(ProtocolViolationError):
        typed_finite_difference(lambda x: x, 1.0, math.nan, function_label="x")


def test_non_callable_raises() -> None:
    with pytest.raises(ProtocolViolationError):
        typed_finite_difference(42, 1.0, 0.01, function_label="x")


def test_empty_function_label_raises() -> None:
    with pytest.raises(ProtocolViolationError):
        typed_finite_difference(lambda x: x, 1.0, 0.01, function_label="")


def test_inputs_field_carries_f_delta_label() -> None:
    result = typed_finite_difference(lambda x: x, 1.0, 0.01, function_label="identity")

    assert result.provenance.inputs == (1.0, 0.01, "identity")


def test_distinct_function_labels_distinct_trace_ids() -> None:
    r1 = typed_finite_difference(lambda x: x, 1.0, 0.01, function_label="identity")
    r2 = typed_finite_difference(lambda x: x * x, 1.0, 0.01, function_label="square")

    assert r1.provenance.trace_id != r2.provenance.trace_id


def test_same_inputs_identical_trace_ids() -> None:
    g = lambda x: x
    r1 = typed_finite_difference(g, 1.0, 0.01, function_label="identity")
    r2 = typed_finite_difference(g, 1.0, 0.01, function_label="identity")

    assert r1.provenance.trace_id == r2.provenance.trace_id


def test_distinct_f_distinct_trace_ids() -> None:
    r1 = typed_finite_difference(lambda x: x, 1.0, 0.01, function_label="x")
    r2 = typed_finite_difference(lambda x: x, 2.0, 0.01, function_label="x")

    assert r1.provenance.trace_id != r2.provenance.trace_id


def test_distinct_delta_distinct_trace_ids() -> None:
    r1 = typed_finite_difference(lambda x: x, 1.0, 0.01, function_label="x")
    r2 = typed_finite_difference(lambda x: x, 1.0, 0.001, function_label="x")

    assert r1.provenance.trace_id != r2.provenance.trace_id


def test_provenance_records_path_metadata() -> None:
    result = typed_finite_difference(lambda x: x, 1.0, 0.01, function_label="x")

    assert result.provenance.operation_id == "typed_finite_difference"
    assert result.provenance.expression_path == "forward_difference"
    assert result.provenance.precision == "raw_python"
    assert result.provenance.backend == "python"
    assert result.provenance.parents == ()


def test_serialization_round_trip_observed() -> None:
    result = typed_finite_difference(lambda x: x * x, 1.0, 0.001, function_label="square")
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    decoded = json.loads(encoded)

    assert decoded["status"] == "transfer_observed"
    assert decoded["value"]["transfer"] is not None
    assert decoded["provenance"]["inputs"] == [1.0, 0.001, "square"]


def test_serialization_round_trip_non_finite() -> None:
    result = typed_finite_difference(lambda x: float("inf"), 1.0, 0.01, function_label="inf_fn")
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)

    assert "Infinity" not in encoded
    assert "NaN" not in encoded


def test_all_strata_serialize_without_naked_nonfinite_values() -> None:
    cases = [
        typed_finite_difference(lambda x: x, 1.0, 0.01, function_label="observed"),
        typed_finite_difference(lambda x: 1.0 + 1e-20 * x, 1.0, 0.01, function_label="cancel"),
        typed_finite_difference(lambda x: math.nan, 1.0, 0.01, function_label="nan"),
        typed_finite_difference(lambda x: "bad", 1.0, 0.01, function_label="bad"),
        typed_finite_difference(lambda x: x, 1.0, 0.0, function_label="zero_delta"),
    ]

    assert {result.status for result in cases} == set(TransferStatus)
    for result in cases:
        encoded = json.dumps(to_json_safe(result), allow_nan=False)
        assert "Infinity" not in encoded
        assert "NaN" not in encoded


def test_consumer_protocol_accepts_observed() -> None:
    result = typed_finite_difference(lambda x: x, 1.0, 0.01, function_label="x")

    check = validate_protocol(result, TRANSFER_OBSERVATION_CONSUMER_PROTOCOL)

    assert check.ok


def test_consumer_protocol_refuses_cancellation_dominated() -> None:
    result = typed_finite_difference(lambda x: 1.0 + 1e-20 * x, 1.0, 0.01, function_label="cancel")

    check = validate_protocol(result, TRANSFER_OBSERVATION_CONSUMER_PROTOCOL)

    assert not check.ok
    assert "cancellation_dominated" in check.reason or "unhandled" in check.reason


def test_unsupported_precision_raises() -> None:
    with pytest.raises(ProtocolViolationError):
        typed_finite_difference(lambda x: x, 1.0, 0.01, function_label="x", precision="float32")
