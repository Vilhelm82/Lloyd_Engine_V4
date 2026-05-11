import dataclasses
import json
import math

import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import AlphaProbeStatus, SingularAlphaJetBundleStatus
from lloyd_v4.primitives import (
    SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL,
    DeclaredAlphaModel,
    scalar_alpha_jet_bundle,
    singular_alpha_jet_bundle,
)


H_VALUES = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]


def test_negative_alpha_singularity_stratum_reciprocal_at_origin() -> None:
    result = singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, H_VALUES, probe_id="reciprocal_jet", function_label="reciprocal", declared_alpha_band=0.01)

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert abs(result.value.observed_alpha - (-1.0)) < 1e-3
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY


def test_negative_alpha_singularity_inverse_square() -> None:
    result = singular_alpha_jet_bundle(lambda x: 1.0 / (x * x), 0.0, H_VALUES, probe_id="inv_sq_jet", function_label="inverse_square", declared_alpha_band=0.01)

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert abs(result.value.observed_alpha - (-2.0)) < 1e-2


def test_negative_alpha_singularity_inverse_sqrt() -> None:
    result = singular_alpha_jet_bundle(lambda x: 1.0 / math.sqrt(x), 0.0, H_VALUES, probe_id="inv_sqrt_jet", function_label="inverse_sqrt", declared_alpha_band=0.01)

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert abs(result.value.observed_alpha - (-0.5)) < 1e-3


def test_regular_integer_alpha_strata() -> None:
    linear = singular_alpha_jet_bundle(lambda x: x, 0.0, H_VALUES, probe_id="linear_jet", function_label="identity", declared_alpha_band=0.01)
    quadratic = singular_alpha_jet_bundle(lambda x: x * x, 0.0, H_VALUES, probe_id="quad_jet", function_label="square", declared_alpha_band=0.01)

    assert linear.status is SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA
    assert abs(linear.value.observed_alpha - 1.0) < 1e-3
    assert quadratic.status is SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA
    assert abs(quadratic.value.observed_alpha - 2.0) < 1e-3


def test_fractional_alpha_branch_stratum_sqrt() -> None:
    result = singular_alpha_jet_bundle(lambda x: math.sqrt(x), 0.0, H_VALUES[:-1], probe_id="sqrt_jet", function_label="sqrt", declared_alpha_band=0.01)

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH
    assert abs(result.value.observed_alpha - 0.5) < 1e-3


def test_alpha_model_refused_ambiguous() -> None:
    models = (
        DeclaredAlphaModel("inverse", -1.0, 0.5),
        DeclaredAlphaModel("near_inverse", -1.2, 0.5),
    )

    result = singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, H_VALUES, probe_id="ambig_jet", function_label="reciprocal", declared_alpha_models=models)

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_MODEL_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS
    assert set(result.value.matching_alpha_model_names) == {"inverse", "near_inverse"}


def test_alpha_model_refused_no_match() -> None:
    models = (DeclaredAlphaModel("sqrt", 0.5, 0.05),)

    result = singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, H_VALUES, probe_id="no_match_jet", function_label="reciprocal", declared_alpha_models=models)

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_MODEL_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_MODEL_NO_MATCH


def test_cancellation_dominated_stratum_near_constant() -> None:
    result = singular_alpha_jet_bundle(lambda x: 1.0 + 1e-20 * x, 1.0, [1e-4, 1e-3, 1e-2, 1e-1], probe_id="cancel_jet", function_label="near_constant")

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_CANCELLATION_DOMINATED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_CANCELLATION_DOMINATED


def test_domain_refused_stratum_f_raises_at_x0_plus_h() -> None:
    def f(_x):
        raise ValueError("never defined")

    result = singular_alpha_jet_bundle(f, 0.0, [1e-4, 1e-3, 1e-2], probe_id="raises", function_label="undefined")

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_DOMAIN_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_DOMAIN_REFUSED


def test_f_raises_at_x0_but_singular_observable_passes() -> None:
    def f(x):
        if x == 0.0:
            raise ZeroDivisionError("undefined at zero")
        return 1.0 / x

    result = singular_alpha_jet_bundle(f, 0.0, H_VALUES, probe_id="x0_raises_h_works", function_label="reciprocal_with_zero_refusal", declared_alpha_band=0.01)

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert abs(result.value.observed_alpha - (-1.0)) < 1e-3


def test_nonfinite_stratum_f_returns_inf() -> None:
    result = singular_alpha_jet_bundle(lambda _x: float("inf"), 0.0, [1e-4, 1e-3, 1e-2], probe_id="inf_jet", function_label="constant_inf")

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NONFINITE
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_NONFINITE


def test_indeterminate_strata() -> None:
    insufficient = singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [1e-3, 1e-2], probe_id="few", function_label="reciprocal")
    degenerate = singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [1e-3, 1e-3, 1e-3, 1e-3], probe_id="degen", function_label="reciprocal")

    assert insufficient.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_INDETERMINATE
    assert insufficient.value.alpha_status is AlphaProbeStatus.ALPHA_INSUFFICIENT_DATA
    assert degenerate.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_INDETERMINATE
    assert degenerate.value.alpha_status is AlphaProbeStatus.ALPHA_INDETERMINATE


def test_negative_alpha_recovery_across_exponents() -> None:
    cases = [
        (lambda x: 1.0 / x, -1.0, "reciprocal"),
        (lambda x: 1.0 / (x * x), -2.0, "inverse_square"),
        (lambda x: 1.0 / (x**3), -3.0, "inverse_cube"),
        (lambda x: 1.0 / math.sqrt(x), -0.5, "inverse_sqrt"),
    ]

    for func, expected_alpha, label in cases:
        result = singular_alpha_jet_bundle(func, 0.0, H_VALUES, probe_id=f"validate_{label}", function_label=label, declared_alpha_band=0.05)

        assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY, f"{label}: got {result.status.value}"
        assert abs(result.value.observed_alpha - expected_alpha) < 1e-2


def test_input_validation_raises() -> None:
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [-1e-3, 1e-3, 1e-2], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [0.0, 1e-3, 1e-2], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, math.inf, [1e-3, 1e-2], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [1e-3, 1e-2, 1e-1], probe_id="", function_label="x")
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(42, 0.0, [1e-3, 1e-2], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [1e-3, 1e-2], eta=0.0, probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(
            lambda x: 1.0 / x,
            0.0,
            [1e-3, 1e-2],
            probe_id="x",
            function_label="x",
            declared_alpha_models=(DeclaredAlphaModel("dup", -1.0, 0.1), DeclaredAlphaModel("dup", -2.0, 0.1)),
        )


def test_bundle_never_evaluates_f_at_x0() -> None:
    calls = []

    def f(x):
        calls.append(x)
        if x == 0.0:
            raise AssertionError("bundle must not evaluate f at x0")
        return 1.0 / x

    result = singular_alpha_jet_bundle(f, 0.0, H_VALUES, probe_id="audit", function_label="reciprocal_audited", declared_alpha_band=0.01)

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert 0.0 not in calls


def test_observation_has_no_f_value_or_derivative_fields() -> None:
    result = singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [1e-3, 1e-2, 1e-1], probe_id="x", function_label="x")
    field_names = {field.name for field in dataclasses.fields(result.value)}

    assert field_names.isdisjoint({"f_value", "derivative_at_point", "derivative_h", "derivative_transfer_trace_id"})


def test_inputs_and_parents_record_lineage() -> None:
    h_values = (1e-3, 1e-2, 1e-1)

    result = singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, list(h_values), probe_id="recip", function_label="reciprocal", eta=1e-6)

    assert result.provenance.inputs == ("recip", "reciprocal", 0.0, h_values, 1e-6)
    assert result.provenance.parents == (result.value.alpha_probe_trace_id,)
    assert result.value.transfer_trace_ids


def test_trace_identity_rules() -> None:
    h_values = [1e-3, 1e-2, 1e-1]
    f = lambda x: 1.0 / x if x != 0 else 0.0

    r1 = singular_alpha_jet_bundle(f, 0.5, h_values, probe_id="x", function_label="rec")
    r2 = singular_alpha_jet_bundle(f, 1.0, h_values, probe_id="x", function_label="rec")
    r3 = singular_alpha_jet_bundle(f, 0.5, h_values, probe_id="x", function_label="rec")

    assert r1.provenance.trace_id != r2.provenance.trace_id
    assert r1.value.alpha_probe_trace_id != r2.value.alpha_probe_trace_id
    assert r1.provenance.trace_id == r3.provenance.trace_id
    assert r1.value.alpha_probe_trace_id == r3.value.alpha_probe_trace_id


def test_sibling_bundles_at_same_x0_distinct_alpha_probe_trace_ids() -> None:
    h_values = [1e-3, 1e-2, 1e-1]
    f = lambda x: x * x

    singular = singular_alpha_jet_bundle(f, 1.0, h_values, probe_id="shared", function_label="square")
    scalar = scalar_alpha_jet_bundle(f, 1.0, h_values, probe_id="shared", function_label="square")

    assert singular.value.alpha_probe_trace_id != scalar.value.alpha_probe_trace_id
    assert singular.provenance.trace_id != scalar.provenance.trace_id


def test_provenance_records_path_metadata() -> None:
    result = singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [1e-3, 1e-2, 1e-1], probe_id="x", function_label="rec")

    assert result.provenance.operation_id == "singular_alpha_jet_bundle"
    assert result.provenance.expression_path == "singular_alpha_jet_singular_probe"
    assert result.provenance.precision == "raw_python"


def test_serialization_round_trip_negative_alpha() -> None:
    result = singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, H_VALUES, probe_id="x", function_label="rec", declared_alpha_band=0.05)
    encoded = json.dumps(to_json_safe(result), allow_nan=False)
    decoded = json.loads(encoded)

    assert decoded["status"] == "singular_jet_negative_alpha_singularity"
    assert decoded["value"]["observed_alpha"] is not None
    assert decoded["value"]["alpha_status"] == "alpha_negative_singularity"
    assert "Infinity" not in encoded
    assert "NaN" not in encoded


def test_serialization_round_trip_refusal() -> None:
    result = singular_alpha_jet_bundle(lambda x: 1.0 + 1e-20 * x, 1.0, [1e-3, 1e-2, 1e-1], probe_id="x", function_label="near_constant")
    encoded = json.dumps(to_json_safe(result), allow_nan=False)

    assert "Infinity" not in encoded
    assert "NaN" not in encoded


def test_consumer_protocol_accepts_observed_strata_and_refuses_refusals() -> None:
    negative = singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, H_VALUES, probe_id="x", function_label="rec", declared_alpha_band=0.05)
    regular = singular_alpha_jet_bundle(lambda x: x * x, 0.0, H_VALUES, probe_id="x", function_label="sq", declared_alpha_band=0.05)
    refusal = singular_alpha_jet_bundle(lambda x: 1.0 + 1e-20 * x, 1.0, [1e-3, 1e-2, 1e-1], probe_id="x", function_label="nc")

    assert validate_protocol(negative, SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL).ok
    assert validate_protocol(regular, SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL).ok
    assert not validate_protocol(refusal, SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL).ok
