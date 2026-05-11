import json
import math

import pytest

from _audit_helpers.lineage import build_trace_id_index, walk_chain
from lloyd_v4.core.conditioning import ConditioningStatus
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import SlopeStatus
from lloyd_v4.primitives import (
    LOG_LOG_SLOPE_CONSUMER_PROTOCOL,
    projective_ratio,
    typed_collection,
    typed_finite_difference,
    typed_log_log_slope,
)


def _power_observations(alpha: float, f_values: list[float], delta_ratio: float = 1e-6):
    return [
        typed_finite_difference(lambda x, a=alpha: x**a, f, delta_ratio * f, function_label=f"power_{alpha}")
        for f in f_values
    ]


def test_observed_stratum_recovers_alpha_minus_one_for_quadratic() -> None:
    f_values = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3]
    slope_result = typed_log_log_slope(typed_collection(_power_observations(2.0, f_values)))

    assert slope_result.status is SlopeStatus.SLOPE_OBSERVED
    assert abs(slope_result.value.slope - 1.0) < 1e-3
    assert slope_result.value.r_squared > 0.999
    assert slope_result.value.n_used == len(f_values)
    assert slope_result.value.n_input_observations == len(f_values)
    assert slope_result.conditioning.status is ConditioningStatus.WELL_CONDITIONED


def test_observed_stratum_recovers_slope_for_alpha_one_half() -> None:
    f_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    slope_result = typed_log_log_slope(typed_collection(_power_observations(0.5, f_values)))

    assert slope_result.status is SlopeStatus.SLOPE_OBSERVED
    assert abs(slope_result.value.slope - (-0.5)) < 1e-3


def test_insufficient_data_stratum_empty_collection() -> None:
    slope_result = typed_log_log_slope(typed_collection([]))

    assert slope_result.status is SlopeStatus.SLOPE_INSUFFICIENT_DATA
    assert slope_result.value.slope is None
    assert slope_result.value.n_used == 0
    assert slope_result.value.n_input_observations == 0


def test_insufficient_data_stratum_too_few_observations() -> None:
    obs_results = _power_observations(2.0, [0.01, 0.1])
    slope_result = typed_log_log_slope(typed_collection(obs_results))

    assert slope_result.status is SlopeStatus.SLOPE_INSUFFICIENT_DATA
    assert slope_result.value.n_input_observations == 2
    assert slope_result.value.n_used == 2


def test_insufficient_data_stratum_filters_non_observed() -> None:
    obs_results = [
        typed_finite_difference(lambda x: x * x, 0.01, 1e-6, function_label="square"),
        typed_finite_difference(lambda x: x * x, 0.1, 0.0, function_label="square"),
        typed_finite_difference(lambda x: float("inf"), 0.5, 1e-6, function_label="inf"),
    ]
    slope_result = typed_log_log_slope(typed_collection(obs_results))

    assert slope_result.status is SlopeStatus.SLOPE_INSUFFICIENT_DATA
    assert slope_result.value.n_input_observations == 3
    assert slope_result.value.n_used == 1


def test_degenerate_input_stratum_all_same_f() -> None:
    obs_results = [
        typed_finite_difference(lambda x: x * x, 0.01, 1e-7, function_label="a"),
        typed_finite_difference(lambda x: x * x, 0.01, 2e-7, function_label="b"),
        typed_finite_difference(lambda x: x * x, 0.01, 3e-7, function_label="c"),
    ]
    slope_result = typed_log_log_slope(typed_collection(obs_results))

    assert slope_result.status is SlopeStatus.SLOPE_DEGENERATE_INPUT
    assert slope_result.value.n_used == 3
    assert slope_result.value.log_f_min == slope_result.value.log_f_max


def test_degenerate_input_stratum_all_same_transfer_magnitude() -> None:
    obs_results = [
        typed_finite_difference(lambda x: x, 1.0, 0.5, function_label="x"),
        typed_finite_difference(lambda x: x, 2.0, 0.5, function_label="x"),
        typed_finite_difference(lambda x: x, 4.0, 0.5, function_label="x"),
    ]
    slope_result = typed_log_log_slope(typed_collection(obs_results))

    assert slope_result.status is SlopeStatus.SLOPE_DEGENERATE_INPUT
    assert slope_result.value.n_used == 3


def test_mixed_collection_filters_to_observed_and_fits() -> None:
    obs_results = [
        typed_finite_difference(lambda x: x * x, 0.001, 1e-7, function_label="square"),
        typed_finite_difference(lambda x: x * x, 0.01, 1e-7, function_label="square"),
        typed_finite_difference(lambda x: x * x, 0.1, 0.0, function_label="square"),
        typed_finite_difference(lambda x: x * x, 0.05, 1e-7, function_label="square"),
        typed_finite_difference(lambda x: float("inf"), 0.2, 1e-7, function_label="inf"),
        typed_finite_difference(lambda x: x * x, 0.5, 1e-7, function_label="square"),
    ]
    slope_result = typed_log_log_slope(typed_collection(obs_results))

    assert slope_result.status is SlopeStatus.SLOPE_OBSERVED
    assert slope_result.value.n_input_observations == 6
    assert slope_result.value.n_used == 4
    assert abs(slope_result.value.slope - 1.0) < 1e-2


def test_non_typed_result_input_raises() -> None:
    with pytest.raises(ProtocolViolationError):
        typed_log_log_slope([1, 2, 3])


def test_collection_of_wrong_type_raises() -> None:
    bad_collection = typed_collection([projective_ratio(1, 2), projective_ratio(3, 4)])

    with pytest.raises(ProtocolViolationError):
        typed_log_log_slope(bad_collection)


def test_collection_with_mixed_types_raises() -> None:
    bad_collection = typed_collection(
        [
            typed_finite_difference(lambda x: x, 0.01, 1e-6, function_label="x"),
            projective_ratio(1, 2),
        ]
    )

    with pytest.raises(ProtocolViolationError):
        typed_log_log_slope(bad_collection)


def test_inputs_field_is_empty_for_internal_operation() -> None:
    obs = _power_observations(2.0, [10**i * 1e-3 for i in range(4)])
    result = typed_log_log_slope(typed_collection(obs))

    assert result.provenance.inputs == ()


def test_parents_includes_collection_and_each_observation() -> None:
    obs = _power_observations(2.0, [10**i * 1e-3 for i in range(4)])
    collection = typed_collection(obs)
    result = typed_log_log_slope(collection)

    parents_set = set(result.provenance.parents)
    assert collection.provenance.trace_id in parents_set
    for observation in obs:
        assert observation.provenance.trace_id in parents_set
    assert len(result.provenance.parents) == 1 + len(obs)


def test_distinct_input_collections_distinct_trace_ids() -> None:
    obs_a = _power_observations(2.0, [0.01, 0.02, 0.03])
    obs_b = _power_observations(2.0, [0.02, 0.03, 0.04])

    slope_a = typed_log_log_slope(typed_collection(obs_a))
    slope_b = typed_log_log_slope(typed_collection(obs_b))

    assert slope_a.provenance.trace_id != slope_b.provenance.trace_id


def test_same_input_collection_identical_trace_ids() -> None:
    obs = _power_observations(2.0, [10**i * 1e-3 for i in range(4)])
    c1 = typed_collection(obs)
    c2 = typed_collection(obs)

    s1 = typed_log_log_slope(c1)
    s2 = typed_log_log_slope(c2)

    assert s1.provenance.trace_id == s2.provenance.trace_id


def test_provenance_records_path_metadata() -> None:
    obs = _power_observations(2.0, [10**i * 1e-3 for i in range(4)])
    result = typed_log_log_slope(typed_collection(obs))

    assert result.provenance.operation_id == "typed_log_log_slope"
    assert result.provenance.expression_path == "ordinary_least_squares"
    assert result.provenance.precision == "raw_python"


def test_lineage_walks_through_collection_to_observations() -> None:
    obs = _power_observations(2.0, [10**i * 1e-3 for i in range(4)])
    collection = typed_collection(obs)
    slope = typed_log_log_slope(collection)

    instances = (slope, collection) + tuple(obs)
    index = build_trace_id_index(instances)
    walked = list(walk_chain(slope, index))
    walked_ids = {item.provenance.trace_id for item in walked}

    assert slope.provenance.trace_id in walked_ids
    assert collection.provenance.trace_id in walked_ids
    for observation in obs:
        assert observation.provenance.trace_id in walked_ids


def test_serialization_round_trip_observed() -> None:
    obs = _power_observations(2.0, [10**i * 1e-3 for i in range(4)])
    result = typed_log_log_slope(typed_collection(obs))
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    decoded = json.loads(encoded)

    assert decoded["status"] == "slope_observed"
    assert decoded["value"]["slope"] is not None
    assert decoded["value"]["r_squared"] is not None


def test_serialization_round_trip_insufficient() -> None:
    result = typed_log_log_slope(typed_collection([]))
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)

    assert "Infinity" not in encoded
    assert "NaN" not in encoded


def test_serialization_round_trip_degenerate() -> None:
    obs = [
        typed_finite_difference(lambda x: x * x, 0.01, 1e-7, function_label="a"),
        typed_finite_difference(lambda x: x * x, 0.01, 2e-7, function_label="b"),
        typed_finite_difference(lambda x: x * x, 0.01, 3e-7, function_label="c"),
    ]
    encoded = json.dumps(to_json_safe(typed_log_log_slope(typed_collection(obs))), allow_nan=False)

    assert "Infinity" not in encoded
    assert "NaN" not in encoded


def test_consumer_protocol_accepts_observed() -> None:
    obs = _power_observations(2.0, [10**i * 1e-3 for i in range(4)])
    result = typed_log_log_slope(typed_collection(obs))

    check = validate_protocol(result, LOG_LOG_SLOPE_CONSUMER_PROTOCOL)

    assert check.ok


def test_consumer_protocol_refuses_insufficient_data() -> None:
    result = typed_log_log_slope(typed_collection([]))

    check = validate_protocol(result, LOG_LOG_SLOPE_CONSUMER_PROTOCOL)

    assert not check.ok


def test_alpha_minus_one_law_recovers_slope_for_known_alphas() -> None:
    test_cases = [
        (2.0, 1.0),
        (0.5, -0.5),
        (3.0, 2.0),
        (1.5, 0.5),
    ]
    f_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]

    for alpha, expected_slope in test_cases:
        obs = _power_observations(alpha, f_values)
        result = typed_log_log_slope(typed_collection(obs))

        assert result.status is SlopeStatus.SLOPE_OBSERVED, (
            f"alpha={alpha}: expected SLOPE_OBSERVED, got {result.status.value}"
        )
        assert abs(result.value.slope - expected_slope) < 1e-2, (
            f"alpha={alpha}: expected slope {expected_slope}, got {result.value.slope}"
        )
        assert result.value.r_squared > 0.999, (
            f"alpha={alpha}: expected R^2 > 0.999, got {result.value.r_squared}"
        )


def test_slope_result_reports_fit_diagnostics() -> None:
    obs = _power_observations(2.0, [1e-4, 1e-3, 1e-2, 1e-1])
    result = typed_log_log_slope(typed_collection(obs))

    assert result.value.intercept is not None
    assert result.value.standard_error is not None
    assert result.value.log_f_min < result.value.log_f_max
    assert any(note.startswith("r_squared=") for note in result.conditioning.notes)
