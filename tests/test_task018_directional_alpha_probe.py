import json
import math

import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import AlphaProbeStatus, ProjectionStatus, QuadraticRootStatus
from lloyd_v4.core.transitions import apply_status_transition
from lloyd_v4.primitives import (
    ALPHA_PROBE_CONSUMER_PROTOCOL,
    DeclaredAlphaModel,
    directional_alpha_probe,
    typed_finite_difference,
)
from lloyd_v4.projection.branches import BranchSelection
from lloyd_v4.projection.exact_projection import QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE


F_VALUES = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]


def test_regular_integer_stratum_alpha_2() -> None:
    result = directional_alpha_probe(lambda f: f * f, F_VALUES, probe_id="quadratic_probe", function_label="square", declared_alpha_band=0.01)

    assert result.status is AlphaProbeStatus.ALPHA_REGULAR_INTEGER
    assert abs(result.value.observed_alpha - 2.0) < 1e-3
    assert result.value.r_squared > 0.999
    assert result.value.n_observed == 6


def test_fractional_branch_stratum_alpha_half() -> None:
    result = directional_alpha_probe(lambda f: math.sqrt(f), F_VALUES[:-1], probe_id="sqrt_probe", function_label="sqrt", declared_alpha_band=0.01)

    assert result.status is AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH
    assert abs(result.value.observed_alpha - 0.5) < 1e-3


def test_negative_singularity_stratum() -> None:
    result = directional_alpha_probe(lambda f: 1.0 / f, [1e-4, 1e-3, 1e-2, 1e-1], probe_id="reciprocal_probe", function_label="reciprocal", declared_alpha_band=0.01)

    assert result.status is AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY
    assert result.value.observed_alpha < 0
    assert abs(result.value.observed_alpha - (-1.0)) < 1e-2


def test_model_unique_match_emits_regime_stratum() -> None:
    models = (DeclaredAlphaModel(name="quadratic", alpha=2.0, band=0.05),)

    result = directional_alpha_probe(lambda f: f * f, F_VALUES, probe_id="quadratic_with_model", function_label="square", declared_alpha_models=models)

    assert result.status is AlphaProbeStatus.ALPHA_REGULAR_INTEGER
    assert result.value.selected_alpha_model == "quadratic"
    assert result.value.matching_alpha_model_names == ("quadratic",)


def test_model_ambiguous_stratum() -> None:
    models = (
        DeclaredAlphaModel(name="quadratic", alpha=2.0, band=0.5),
        DeclaredAlphaModel(name="near_quadratic", alpha=2.4, band=0.5),
    )

    result = directional_alpha_probe(lambda f: f * f, F_VALUES, probe_id="ambiguous", function_label="square", declared_alpha_models=models)

    assert result.status is AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS
    assert set(result.value.matching_alpha_model_names) == {"quadratic", "near_quadratic"}
    assert result.value.selected_alpha_model is None


def test_model_no_match_stratum() -> None:
    models = (
        DeclaredAlphaModel(name="cubic", alpha=3.0, band=0.05),
        DeclaredAlphaModel(name="sqrt", alpha=0.5, band=0.05),
    )

    result = directional_alpha_probe(lambda f: f * f, F_VALUES, probe_id="no_match", function_label="square", declared_alpha_models=models)

    assert result.status is AlphaProbeStatus.ALPHA_MODEL_NO_MATCH
    assert result.value.matching_alpha_model_names == ()


def test_insufficient_data_stratum_too_few_f_values() -> None:
    result = directional_alpha_probe(lambda f: f * f, [1e-3, 1e-2], probe_id="too_few", function_label="square")

    assert result.status is AlphaProbeStatus.ALPHA_INSUFFICIENT_DATA
    assert result.value.observed_alpha is None
    assert result.value.n_observed == 2


def test_cancellation_dominated_stratum() -> None:
    result = directional_alpha_probe(lambda f: 1.0 + 1e-20 * f, [1e-4, 1e-3, 1e-2, 1e-1], probe_id="cancel", function_label="near_constant")

    assert result.status is AlphaProbeStatus.ALPHA_CANCELLATION_DOMINATED
    assert result.value.n_cancellation_dominated >= 3
    assert result.value.observed_alpha is None


def test_domain_refused_stratum() -> None:
    def g(f):
        raise ValueError("not defined")

    result = directional_alpha_probe(g, [1e-4, 1e-3, 1e-2, 1e-1], probe_id="bad", function_label="raises")

    assert result.status is AlphaProbeStatus.ALPHA_DOMAIN_REFUSED


def test_nonfinite_stratum_majority_nonfinite() -> None:
    result = directional_alpha_probe(lambda f: float("inf"), [1e-4, 1e-3, 1e-2, 1e-1], probe_id="inf", function_label="inf")

    assert result.status is AlphaProbeStatus.ALPHA_NONFINITE


def test_indeterminate_stratum_via_degenerate_input() -> None:
    result = directional_alpha_probe(lambda f: f * f, [1e-3, 1e-3, 1e-3, 1e-3], probe_id="degen", function_label="square")

    assert result.status is AlphaProbeStatus.ALPHA_INDETERMINATE


def test_input_validation_raises() -> None:
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [-1e-3, 1e-3, 1e-2], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [0.0, 1e-3, 1e-2], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [1e-3, math.inf, 1e-2], probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [1e-3, 1e-2], eta=0.0, probe_id="x", function_label="x")
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [1e-3, 1e-2], probe_id="", function_label="x")
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(42, [1e-3, 1e-2], probe_id="x", function_label="x")


def test_duplicate_model_names_raise() -> None:
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(
            lambda f: f,
            [1e-3, 1e-2, 1e-1],
            probe_id="x",
            function_label="x",
            declared_alpha_models=(
                DeclaredAlphaModel("dup", 0.5, 0.05),
                DeclaredAlphaModel("dup", 1.5, 0.05),
            ),
        )


def test_inputs_carry_probe_and_function_labels() -> None:
    f_values = (1e-3, 1e-2, 1e-1)

    result = directional_alpha_probe(lambda f: f * f, list(f_values), probe_id="quad_probe", function_label="square", eta=1e-6)

    assert result.provenance.inputs == ("quad_probe", "square", f_values, 1e-6)


def test_parents_include_all_transfers_and_slope() -> None:
    result = directional_alpha_probe(lambda f: f * f, [10 ** (-i) for i in range(2, 8)], probe_id="x", function_label="square")

    assert len(result.provenance.parents) == 7


def test_distinct_probe_ids_distinct_trace_ids() -> None:
    f_values = [1e-3, 1e-2, 1e-1]
    r1 = directional_alpha_probe(lambda f: f * f, f_values, probe_id="A", function_label="square")
    r2 = directional_alpha_probe(lambda f: f * f, f_values, probe_id="B", function_label="square")

    assert r1.provenance.trace_id != r2.provenance.trace_id


def test_identical_inputs_identical_trace_ids() -> None:
    f_values = [1e-3, 1e-2, 1e-1]
    r1 = directional_alpha_probe(lambda f: f * f, f_values, probe_id="x", function_label="square")
    r2 = directional_alpha_probe(lambda f: f * f, f_values, probe_id="x", function_label="square")

    assert r1.provenance.trace_id == r2.provenance.trace_id


def test_alpha_probe_never_alters_transfer_values() -> None:
    f_values = [1e-3, 1e-2, 1e-1]
    direct_transfers = [typed_finite_difference(lambda f: f * f, f, 1e-6 * f, function_label="square") for f in f_values]

    probe_result = directional_alpha_probe(lambda f: f * f, f_values, probe_id="x", function_label="square", eta=1e-6)

    assert probe_result.value.transfer_trace_ids == tuple(t.provenance.trace_id for t in direct_transfers)


def test_alpha_minus_one_law_via_alpha_probe() -> None:
    test_cases = [
        (0.5, AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH),
        (1.5, AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH),
        (2.0, AlphaProbeStatus.ALPHA_REGULAR_INTEGER),
        (3.0, AlphaProbeStatus.ALPHA_REGULAR_INTEGER),
    ]
    f_values = [10 ** (-i) for i in range(1, 7)]

    for alpha, expected_status in test_cases:
        result = directional_alpha_probe(
            lambda f, a=alpha: f**a,
            f_values,
            probe_id=f"alpha_{alpha}",
            function_label=f"power_{alpha}",
            declared_alpha_band=0.05,
        )

        assert result.status is expected_status, f"alpha={alpha}: expected {expected_status.value}, got {result.status.value}"
        assert abs(result.value.observed_alpha - alpha) < 1e-2
        assert result.value.r_squared > 0.999


def test_projection_transition_rule_callable_authoritative() -> None:
    rule = QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE
    assert rule.mapped_statuses[QuadraticRootStatus.TWO_REAL_ROOTS] is ProjectionStatus.PROJECTION_TRANSVERSE

    outcome = apply_status_transition(rule, QuadraticRootStatus.TWO_REAL_ROOTS, branch=BranchSelection.LINEAR)

    assert outcome.output_status is ProjectionStatus.PROJECTION_SELECTION_REFUSED


def test_serialization_round_trip_observed_and_refusal() -> None:
    observed = directional_alpha_probe(lambda f: f * f, [1e-3, 1e-2, 1e-1, 1.0], probe_id="x", function_label="square", declared_alpha_band=0.05)
    observed_payload = to_json_safe(observed)
    observed_decoded = json.loads(json.dumps(observed_payload, allow_nan=False))
    assert observed_decoded["status"] == "alpha_regular_integer"
    assert observed_decoded["value"]["observed_alpha"] is not None

    refusal = directional_alpha_probe(lambda f: f, [1e-3, 1e-2], probe_id="x", function_label="x")
    encoded = json.dumps(to_json_safe(refusal), allow_nan=False)
    assert "Infinity" not in encoded
    assert "NaN" not in encoded


def test_consumer_protocol_accepts_observed_and_refuses_model_no_match() -> None:
    observed = directional_alpha_probe(lambda f: f * f, [1e-3, 1e-2, 1e-1, 1.0], probe_id="x", function_label="square", declared_alpha_band=0.05)
    assert validate_protocol(observed, ALPHA_PROBE_CONSUMER_PROTOCOL).ok

    no_match = directional_alpha_probe(
        lambda f: f * f,
        [1e-3, 1e-2, 1e-1, 1.0],
        probe_id="x",
        function_label="square",
        declared_alpha_models=(DeclaredAlphaModel("sqrt", 0.5, 0.05),),
    )
    assert not validate_protocol(no_match, ALPHA_PROBE_CONSUMER_PROTOCOL).ok
