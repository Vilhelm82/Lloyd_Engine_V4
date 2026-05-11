import inspect
import json
import math

import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import AlphaProbeStatus, ScalarAlphaJetBundleStatus, TransferStatus
from lloyd_v4.primitives import (
    SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL,
    DeclaredAlphaModel,
    scalar_alpha_jet_bundle,
    typed_finite_difference,
)


H_VALUES = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]


def test_regular_integer_stratum_quadratic_at_origin() -> None:
    result = scalar_alpha_jet_bundle(lambda x: x * x, 0.0, H_VALUES, probe_id="quad_jet", function_label="square", declared_alpha_band=0.01)

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA
    assert abs(result.value.observed_alpha - 2.0) < 1e-3
    assert result.value.point == 0.0
    assert result.value.f_value == 0.0
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_REGULAR_INTEGER


def test_fractional_branch_stratum_sqrt_at_origin() -> None:
    result = scalar_alpha_jet_bundle(lambda x: math.sqrt(x), 0.0, H_VALUES[:-1], probe_id="sqrt_jet", function_label="sqrt", declared_alpha_band=0.01)

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH
    assert abs(result.value.observed_alpha - 0.5) < 1e-3


def test_inherited_negative_alpha_mapping_via_declared_model() -> None:
    models = (DeclaredAlphaModel("declared_singular", -1.0, 2.5),)

    result = scalar_alpha_jet_bundle(lambda x: x, 0.0, H_VALUES, probe_id="declared_negative", function_label="identity", declared_alpha_models=models)

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY
    assert result.value.observed_alpha > 0.0
    assert result.value.selected_alpha_model == "declared_singular"


def test_reciprocal_regular_away_from_singularity() -> None:
    result = scalar_alpha_jet_bundle(lambda x: 1.0 + 1.0 / x, 1.0, [1e-6, 1e-5, 1e-4, 1e-3], probe_id="reciprocal_jet", function_label="one_plus_inverse", declared_alpha_band=0.01)

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_REGULAR_INTEGER
    assert abs(result.value.observed_alpha - 1.0) < 1e-2


def test_alpha_model_refused_ambiguous() -> None:
    models = (
        DeclaredAlphaModel("quadratic", 2.0, 0.5),
        DeclaredAlphaModel("near_quadratic", 2.4, 0.5),
    )

    result = scalar_alpha_jet_bundle(lambda x: x * x, 0.0, H_VALUES, probe_id="ambig_jet", function_label="square", declared_alpha_models=models)

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_MODEL_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS
    assert set(result.value.matching_alpha_model_names) == {"quadratic", "near_quadratic"}


def test_alpha_model_refused_no_match() -> None:
    models = (DeclaredAlphaModel("sqrt", 0.5, 0.05),)

    result = scalar_alpha_jet_bundle(lambda x: x * x, 0.0, H_VALUES, probe_id="no_match_jet", function_label="square", declared_alpha_models=models)

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_MODEL_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_MODEL_NO_MATCH


def test_cancellation_dominated_stratum_near_constant() -> None:
    result = scalar_alpha_jet_bundle(lambda x: x, 1.0, [1e-4, 1e-3, 1e-2, 1e-1], probe_id="cancel_jet", function_label="identity", eta=1e-18)

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_CANCELLATION_DOMINATED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_CANCELLATION_DOMINATED


def test_domain_refused_stratum_at_x0() -> None:
    def f(x):
        if x == 0:
            raise ValueError("undefined at 0")
        return 1.0 / x

    result = scalar_alpha_jet_bundle(f, 0.0, [1e-4, 1e-3, 1e-2], probe_id="x0_raises", function_label="reciprocal")

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED
    assert result.value.f_value is None
    assert result.value.alpha_probe_trace_id is None
    assert result.value.transfer_trace_ids == ()


def test_domain_refused_stratum_at_x0_plus_h() -> None:
    def f(x):
        if x == 0.0:
            return 1.0
        raise ValueError("only defined at 0")

    result = scalar_alpha_jet_bundle(f, 0.0, [1e-4, 1e-3, 1e-2], probe_id="h_raises", function_label="point_only")

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED
    assert result.value.f_value == 1.0
    assert result.value.alpha_probe_trace_id is not None
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_DOMAIN_REFUSED


def test_nonfinite_stratum_f_at_x0() -> None:
    result = scalar_alpha_jet_bundle(lambda x: float("inf"), 0.0, [1e-4, 1e-3, 1e-2], probe_id="inf_jet", function_label="constant_inf")

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_NONFINITE
    assert result.value.f_value is not None
    assert not math.isfinite(result.value.f_value)


def test_indeterminate_stratum_insufficient_h_values() -> None:
    result = scalar_alpha_jet_bundle(lambda x: x * x, 0.0, [1e-3, 1e-2], probe_id="few", function_label="square")

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_INDETERMINATE
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_INSUFFICIENT_DATA


def test_indeterminate_stratum_repeated_h() -> None:
    result = scalar_alpha_jet_bundle(lambda x: x * x, 0.0, [1e-3, 1e-3, 1e-3, 1e-3], probe_id="degen", function_label="square")

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_INDETERMINATE
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_INDETERMINATE


def test_input_validation_raises() -> None:
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(lambda x: x, 0.0, [], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(lambda x: x, 0.0, [-1e-3, 1e-3, 1e-2], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(lambda x: x, math.inf, [1e-3, 1e-2], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(lambda x: x, 0.0, [1e-3, 1e-2, 1e-1], probe_id="", function_label="x")
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(42, 0.0, [1e-3, 1e-2], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(lambda x: x, 0.0, [1e-3, 1e-2], eta=0.0, probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(
            lambda x: x,
            0.0,
            [1e-3, 1e-2],
            probe_id="x",
            function_label="x",
            declared_alpha_models=(DeclaredAlphaModel("dup", 1.0, 0.1), DeclaredAlphaModel("dup", 2.0, 0.1)),
        )


def test_derivative_pulled_from_smallest_observed_h() -> None:
    result = scalar_alpha_jet_bundle(lambda x: x * x, 1.0, [1e-3, 2e-3, 3e-3, 4e-3], probe_id="deriv_check", function_label="square", declared_alpha_band=0.01)

    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA
    assert result.value.derivative_h == 1e-3
    assert abs(result.value.derivative_at_point - 2.002001) < 1e-5


def test_derivative_none_when_no_h_observed() -> None:
    result = scalar_alpha_jet_bundle(lambda x: x, 1.0, [1e-4, 1e-3, 1e-2], probe_id="no_deriv", function_label="identity", eta=1e-18)

    assert result.value.derivative_at_point is None
    assert result.value.derivative_h is None
    assert result.value.derivative_transfer_trace_id is None


def test_inputs_carry_probe_function_label_x0_h_eta() -> None:
    h_values = (1e-3, 1e-2, 1e-1)

    result = scalar_alpha_jet_bundle(lambda x: x * x, 0.5, list(h_values), probe_id="quad", function_label="square", eta=1e-6)

    assert result.provenance.inputs == ("quad", "square", 0.5, h_values, 1e-6)


def test_parents_contains_only_alpha_probe_trace() -> None:
    result = scalar_alpha_jet_bundle(lambda x: x * x, 0.0, [10 ** (-i) for i in range(2, 8)], probe_id="x", function_label="square", declared_alpha_band=0.01)

    assert result.provenance.parents == (result.value.alpha_probe_trace_id,)
    assert result.value.slope_trace_id is not None
    assert result.value.slope_trace_id != result.value.alpha_probe_trace_id
    assert len(result.value.transfer_trace_ids) == 6


def test_trace_identity_rules() -> None:
    h_values = [1e-3, 1e-2, 1e-1]

    r1 = scalar_alpha_jet_bundle(lambda x: x * x, 0.0, h_values, probe_id="x", function_label="square")
    r2 = scalar_alpha_jet_bundle(lambda x: x * x, 1.0, h_values, probe_id="x", function_label="square")
    r3 = scalar_alpha_jet_bundle(lambda x: x * x, 0.0, h_values, probe_id="x", function_label="square")

    assert r1.provenance.trace_id != r2.provenance.trace_id
    assert r1.value.alpha_probe_trace_id != r2.value.alpha_probe_trace_id
    assert r1.provenance.trace_id == r3.provenance.trace_id
    assert r1.value.alpha_probe_trace_id == r3.value.alpha_probe_trace_id


def test_derivative_trace_matches_independent_typed_finite_difference() -> None:
    x0 = 1.0
    eta = 1e-6
    h_values = [1e-3, 1e-2, 1e-1]
    f = lambda x: x * x
    f_at_x0 = f(x0)
    g_local = lambda h: f(x0 + h) - f_at_x0

    result = scalar_alpha_jet_bundle(f, x0, h_values, probe_id="deriv_trace", function_label="square", eta=eta, declared_alpha_band=0.01)
    direct = typed_finite_difference(g_local, 1e-3, eta * 1e-3, function_label="square__local_at_1.0")

    assert direct.status is TransferStatus.TRANSFER_OBSERVED
    assert result.value.derivative_transfer_trace_id == direct.provenance.trace_id
    assert result.value.derivative_at_point == direct.value.transfer


def test_alpha_minus_one_law_via_scalar_alpha_jet_bundle() -> None:
    test_cases = [
        (0.5, ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH),
        (1.5, ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH),
        (2.0, ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA),
        (3.0, ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA),
    ]

    for alpha, expected_status in test_cases:
        result = scalar_alpha_jet_bundle(
            lambda x, a=alpha: x**a,
            0.0,
            [10 ** (-i) for i in range(1, 7)],
            probe_id=f"alpha_{alpha}",
            function_label=f"power_{alpha}",
            declared_alpha_band=0.05,
        )

        assert result.status is expected_status
        assert abs(result.value.observed_alpha - alpha) < 1e-2


def test_alpha_probe_refusal_propagates_as_typed_result_not_exception() -> None:
    call_count = [0]

    def f(x):
        call_count[0] += 1
        if call_count[0] > 1:
            raise ValueError("only first call allowed")
        return 0.0

    result = scalar_alpha_jet_bundle(f, 0.0, [1e-3, 1e-2, 1e-1], probe_id="x", function_label="restricted")

    assert isinstance(result, TypedResult)
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED


def test_no_default_h_grid() -> None:
    sig = inspect.signature(scalar_alpha_jet_bundle)

    assert sig.parameters["h_values"].default is inspect.Parameter.empty


def test_serialization_round_trip_observed() -> None:
    result = scalar_alpha_jet_bundle(lambda x: x * x, 0.0, [1e-3, 1e-2, 1e-1, 1.0], probe_id="x", function_label="square", declared_alpha_band=0.05)

    decoded = json.loads(json.dumps(to_json_safe(result), allow_nan=False))

    assert decoded["status"] == "scalar_jet_regular_integer_alpha"
    assert decoded["value"]["observed_alpha"] is not None
    assert decoded["value"]["alpha_status"] == "alpha_regular_integer"


def test_serialization_round_trip_refusal() -> None:
    result = scalar_alpha_jet_bundle(lambda x: 1.0 + 1e-20 * x, 1.0, [1e-3, 1e-2, 1e-1], probe_id="x", function_label="near_constant")

    encoded = json.dumps(to_json_safe(result), allow_nan=False)

    assert "Infinity" not in encoded
    assert "NaN" not in encoded


def test_consumer_protocol_accepts_observed_strata_and_refuses_refusals() -> None:
    observed = scalar_alpha_jet_bundle(lambda x: x * x, 0.0, [1e-3, 1e-2, 1e-1, 1.0], probe_id="x", function_label="square", declared_alpha_band=0.05)
    refusal = scalar_alpha_jet_bundle(lambda x: x, 1.0, [1e-3, 1e-2, 1e-1], probe_id="x", function_label="identity", eta=1e-18)

    assert validate_protocol(observed, SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL).ok
    assert not validate_protocol(refusal, SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL).ok
