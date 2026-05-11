import dataclasses
import json
import math

import pytest

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.status import AlphaProbeStatus, ScalarAlphaJetBundleStatus, SingularAlphaJetBundleStatus
from lloyd_v4.primitives import (
    ALPHA_PROBE_CONSUMER_PROTOCOL,
    ALPHA_NUMERIC_FLOOR,
    DEFAULT_ALPHA_MATERIALITY,
    K_BOUNDARY,
    K_DRIFT,
    MIN_WINDOW_COUNT,
    MIN_WINDOW_POINTS,
    AlphaProbeObservation,
    AlphaWindowFit,
    AlphaWindowStabilityStatus,
    directional_alpha_probe,
    scalar_alpha_jet_bundle,
    singular_alpha_jet_bundle,
)


H6 = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
E_H_GRID = [10.0 ** (-i) for i in range(1, 8)]


def sqrt_fixture(x: float) -> float:
    return math.sqrt(x)


def reciprocal_fixture(x: float) -> float:
    if x == 0.0:
        raise ZeroDivisionError("undefined at zero")
    return 1.0 / x


def slow_drift_fixture(x: float) -> float:
    return math.sqrt(x) * (1.0 + 0.1 * x**0.1)


def negative_log_fixture(x: float) -> float:
    if x <= 0.0:
        raise ValueError("undefined at zero")
    return -math.log(x)


def iterated_log_fixture(x: float) -> float:
    if x <= 0.0:
        raise ValueError("undefined at zero")
    return math.log(-math.log(x))


def essential_fixture(x: float) -> float:
    if x == 0.0:
        return 0.0
    return math.exp(-1.0 / (x * x))


def scalar_boundary_fixture(x: float) -> float:
    if x == 0.0:
        return 0.0
    return -math.log(x)


def scalar_unstable_fixture(x: float) -> float:
    if x == 0.0:
        return 0.0
    return math.log(-math.log(x))


def boundary_envelope(standard_error: float | None) -> float:
    return max(K_BOUNDARY * (0.0 if standard_error is None else standard_error), ALPHA_NUMERIC_FLOOR)


def test_alpha_window_fit_is_frozen_slotted_and_serializable() -> None:
    fit = AlphaWindowFit(
        h_start=1e-6,
        h_end=1e-2,
        h_count=5,
        observed_slope=-0.5,
        observed_alpha=0.5,
        slope_standard_error=1e-4,
        alpha_standard_error=1e-4,
        r_squared=0.99,
    )

    assert fit == dataclasses.replace(fit)
    assert not hasattr(fit, "__dict__")
    with pytest.raises(dataclasses.FrozenInstanceError):
        fit.h_count = 3
    assert to_json_safe(fit)["observed_alpha"] == 0.5


def test_alpha_window_stability_status_values() -> None:
    assert AlphaWindowStabilityStatus.STABLE.value == "stable"
    assert AlphaWindowStabilityStatus.UNSTABLE.value == "unstable"
    assert AlphaWindowStabilityStatus.NOT_TESTED.value == "not_tested"


def test_reliability_constants_are_exposed_and_calibrated() -> None:
    assert K_BOUNDARY == 2.0
    assert K_DRIFT == 2.0
    assert ALPHA_NUMERIC_FLOOR == 1e-9
    assert DEFAULT_ALPHA_MATERIALITY == 0.05
    assert MIN_WINDOW_POINTS == 3
    assert MIN_WINDOW_COUNT == 3


def test_new_alpha_probe_status_values() -> None:
    assert AlphaProbeStatus.ALPHA_ZERO_BOUNDARY.value == "alpha_zero_boundary"
    assert AlphaProbeStatus.ALPHA_UNSTABLE_WINDOW.value == "alpha_unstable_window"


def test_alpha_probe_observation_rejects_partial_nested_fields() -> None:
    with pytest.raises(ValueError):
        AlphaProbeObservation(
            probe_id="p",
            function_label="f",
            f_values=(1e-3, 1e-2, 1e-1),
            delta_values=(1e-9, 1e-8, 1e-7),
            eta=1e-6,
            transfer_trace_ids=(),
            slope_trace_id=None,
            observed_slope=None,
            observed_alpha=None,
            r_squared=None,
            standard_error=None,
            log_f_min=None,
            log_f_max=None,
            nested_window_fits=(AlphaWindowFit(1e-3, 1e-1, 3, 0.0, 1.0, 0.0, 0.0, 1.0),),
            alpha_window_min=None,
            alpha_window_max=None,
            alpha_window_span=None,
            propagated_window_error=None,
            alpha_stability_status=AlphaWindowStabilityStatus.NOT_TESTED,
            n_input_observations=0,
            n_observed=0,
            n_cancellation_dominated=0,
            n_non_finite=0,
            n_domain_refused=0,
            n_delta_indeterminate=0,
            declared_alpha_models=(),
            declared_alpha_band=None,
            selected_alpha_model=None,
            matching_alpha_model_names=(),
            expression_path="x",
        )


def test_alpha_probe_observation_rejects_missing_fields_when_tested() -> None:
    fit = AlphaWindowFit(1e-3, 1e-1, 3, 0.0, 1.0, 0.0, 0.0, 1.0)

    with pytest.raises(ValueError):
        AlphaProbeObservation(
            probe_id="p",
            function_label="f",
            f_values=(1e-3, 1e-2, 1e-1),
            delta_values=(1e-9, 1e-8, 1e-7),
            eta=1e-6,
            transfer_trace_ids=(),
            slope_trace_id=None,
            observed_slope=0.0,
            observed_alpha=1.0,
            r_squared=1.0,
            standard_error=0.0,
            log_f_min=-1.0,
            log_f_max=1.0,
            nested_window_fits=(fit,),
            alpha_window_min=1.0,
            alpha_window_max=None,
            alpha_window_span=0.0,
            propagated_window_error=0.0,
            alpha_stability_status=AlphaWindowStabilityStatus.STABLE,
            n_input_observations=3,
            n_observed=3,
            n_cancellation_dominated=0,
            n_non_finite=0,
            n_domain_refused=0,
            n_delta_indeterminate=0,
            declared_alpha_models=(),
            declared_alpha_band=None,
            selected_alpha_model=None,
            matching_alpha_model_names=(),
            expression_path="x",
        )


def test_alpha_probe_observation_rejects_negative_window_span() -> None:
    fit = AlphaWindowFit(1e-3, 1e-1, 3, 0.0, 1.0, 0.0, 0.0, 1.0)

    with pytest.raises(ValueError):
        AlphaProbeObservation(
            probe_id="p",
            function_label="f",
            f_values=(1e-3, 1e-2, 1e-1),
            delta_values=(1e-9, 1e-8, 1e-7),
            eta=1e-6,
            transfer_trace_ids=(),
            slope_trace_id=None,
            observed_slope=0.0,
            observed_alpha=1.0,
            r_squared=1.0,
            standard_error=0.0,
            log_f_min=-1.0,
            log_f_max=1.0,
            nested_window_fits=(fit,),
            alpha_window_min=1.0,
            alpha_window_max=1.0,
            alpha_window_span=-1e-6,
            propagated_window_error=0.0,
            alpha_stability_status=AlphaWindowStabilityStatus.STABLE,
            n_input_observations=3,
            n_observed=3,
            n_cancellation_dominated=0,
            n_non_finite=0,
            n_domain_refused=0,
            n_delta_indeterminate=0,
            declared_alpha_models=(),
            declared_alpha_band=None,
            selected_alpha_model=None,
            matching_alpha_model_names=(),
            expression_path="x",
        )


def test_nested_window_sizes_for_seven_h_points() -> None:
    result = directional_alpha_probe(lambda h: h**0.5, [10.0 ** (-i) for i in range(2, 9)], probe_id="sizes7", function_label="sqrt")

    assert result.value.alpha_stability_status is AlphaWindowStabilityStatus.STABLE
    assert [fit.h_count for fit in result.value.nested_window_fits] == [7, 6, 5, 4, 3]


def test_full_window_fit_matches_primary_alpha_observation() -> None:
    result = directional_alpha_probe(lambda h: h**0.5, [10.0 ** (-i) for i in range(2, 9)], probe_id="full", function_label="sqrt")

    assert result.value.nested_window_fits[0].observed_alpha == pytest.approx(result.value.observed_alpha)
    assert result.value.nested_window_fits[0].observed_slope == pytest.approx(result.value.observed_slope)


def test_sequential_from_top_drops_largest_h_each_window() -> None:
    h_grid = [10.0 ** (-i) for i in range(2, 9)]
    result = directional_alpha_probe(lambda h: h**0.5, h_grid, probe_id="drop", function_label="sqrt")
    h_ends = [fit.h_end for fit in result.value.nested_window_fits]

    assert h_ends == [1e-2, 1e-3, 1e-4, 1e-5, 1e-6]


def test_nested_window_skips_when_only_two_windows_possible() -> None:
    result = directional_alpha_probe(lambda h: h * h, [1e-4, 1e-3, 1e-2, 1e-1], probe_id="sizes4", function_label="square", declared_alpha_band=0.05)

    assert result.status is AlphaProbeStatus.ALPHA_REGULAR_INTEGER
    assert result.value.nested_window_fits is None
    assert result.value.alpha_stability_status is AlphaWindowStabilityStatus.NOT_TESTED
    assert "nested_window_skipped: h_grid_too_short" in result.conditioning.notes


def test_nested_window_exactly_five_points_produces_three_windows() -> None:
    result = directional_alpha_probe(lambda h: h**0.5, [1e-5, 1e-4, 1e-3, 1e-2, 1e-1], probe_id="sizes5", function_label="sqrt")

    assert [fit.h_count for fit in result.value.nested_window_fits] == [5, 4, 3]


def test_propagated_window_error_uses_min_and_max_alpha_fits() -> None:
    result = directional_alpha_probe(iterated_log_fixture, E_H_GRID, probe_id="prop", function_label="iter")
    fits = result.value.nested_window_fits
    min_fit = min(fits, key=lambda fit: fit.observed_alpha)
    max_fit = max(fits, key=lambda fit: fit.observed_alpha)
    expected = math.sqrt(min_fit.alpha_standard_error**2 + max_fit.alpha_standard_error**2)

    assert result.value.propagated_window_error == pytest.approx(expected)


def test_zero_boundary_envelope_uses_standard_error_and_numeric_floor() -> None:
    assert max(K_BOUNDARY * 0.01, ALPHA_NUMERIC_FLOOR) == pytest.approx(0.02)
    assert max(K_BOUNDARY * 1e-15, ALPHA_NUMERIC_FLOOR) == ALPHA_NUMERIC_FLOOR


def test_fixture_a_preserves_fractional_branch_and_stable_evidence() -> None:
    scalar = scalar_alpha_jet_bundle(sqrt_fixture, 0.0, H6, probe_id="A_scalar", function_label="sqrt")
    singular = singular_alpha_jet_bundle(sqrt_fixture, 0.0, H6, probe_id="A_singular", function_label="sqrt")

    assert scalar.status is ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH
    assert singular.status is SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH
    assert scalar.value.alpha_probe_observation.alpha_stability_status is AlphaWindowStabilityStatus.STABLE
    assert singular.value.alpha_probe_observation.alpha_stability_status is AlphaWindowStabilityStatus.STABLE


def test_fixture_b_preserves_informative_scalar_refusal_and_singular_negative() -> None:
    scalar = scalar_alpha_jet_bundle(reciprocal_fixture, 0.0, H6, probe_id="B_scalar", function_label="recip")
    singular = singular_alpha_jet_bundle(reciprocal_fixture, 0.0, H6, probe_id="B_singular", function_label="recip")

    assert scalar.status is ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED
    assert scalar.value.alpha_probe_observation is None
    assert singular.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert singular.value.alpha_probe_observation.alpha_stability_status is AlphaWindowStabilityStatus.STABLE


def test_fixture_c_remains_fractional_branch_under_default_materiality() -> None:
    h_grid = [10.0 ** (-i) for i in range(2, 9)]
    scalar = scalar_alpha_jet_bundle(slow_drift_fixture, 0.0, h_grid, probe_id="C_scalar", function_label="slow")
    singular = singular_alpha_jet_bundle(slow_drift_fixture, 0.0, h_grid, probe_id="C_singular", function_label="slow")

    assert scalar.status is ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH
    assert singular.status is SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH
    assert scalar.value.alpha_probe_observation.alpha_stability_status is AlphaWindowStabilityStatus.STABLE
    assert scalar.value.alpha_probe_observation.alpha_window_span < DEFAULT_ALPHA_MATERIALITY


def test_fixture_d_classifies_singular_log_as_zero_boundary() -> None:
    result = singular_alpha_jet_bundle(negative_log_fixture, 0.0, [10.0 ** (-i) for i in range(2, 10)], probe_id="D", function_label="neg_log")
    alpha = result.value.alpha_probe_observation

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_ZERO_BOUNDARY
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_ZERO_BOUNDARY
    assert abs(alpha.observed_alpha) <= boundary_envelope(alpha.standard_error)
    assert alpha.alpha_stability_status is AlphaWindowStabilityStatus.STABLE


def test_zero_boundary_precedes_declared_model_matching() -> None:
    from lloyd_v4.primitives import DeclaredAlphaModel

    result = directional_alpha_probe(
        negative_log_fixture,
        [10.0 ** (-i) for i in range(2, 10)],
        probe_id="D_model",
        function_label="neg_log",
        declared_alpha_models=(DeclaredAlphaModel("ordinary_negative", -1.0, 0.2),),
    )

    assert result.status is AlphaProbeStatus.ALPHA_ZERO_BOUNDARY
    assert result.value.selected_alpha_model is None


def test_fixture_e_classifies_singular_iterated_log_as_unstable_window() -> None:
    result = singular_alpha_jet_bundle(iterated_log_fixture, 0.0, E_H_GRID, probe_id="E", function_label="iter")
    alpha = result.value.alpha_probe_observation

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_UNSTABLE_WINDOW
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_UNSTABLE_WINDOW
    assert alpha.alpha_stability_status is AlphaWindowStabilityStatus.UNSTABLE
    assert alpha.alpha_window_span > DEFAULT_ALPHA_MATERIALITY
    assert alpha.alpha_window_span > K_DRIFT * alpha.propagated_window_error
    assert alpha.nested_window_fits[0].observed_alpha > alpha.nested_window_fits[-1].observed_alpha


def test_unstable_window_precedes_declared_model_matching() -> None:
    from lloyd_v4.primitives import DeclaredAlphaModel

    result = directional_alpha_probe(
        iterated_log_fixture,
        E_H_GRID,
        probe_id="E_model",
        function_label="iter",
        declared_alpha_models=(DeclaredAlphaModel("small_fractional", 0.08, 0.1),),
    )

    assert result.status is AlphaProbeStatus.ALPHA_UNSTABLE_WINDOW
    assert result.value.selected_alpha_model is None


def test_large_declared_alpha_band_suppresses_unstable_window_materiality() -> None:
    result = directional_alpha_probe(iterated_log_fixture, E_H_GRID, probe_id="E_large_band", function_label="iter", declared_alpha_band=0.1)

    assert result.status is AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH
    assert result.value.alpha_stability_status is AlphaWindowStabilityStatus.STABLE
    assert result.value.alpha_window_span < 0.1


def test_declared_model_matching_still_runs_for_stable_algebraic_cases() -> None:
    from lloyd_v4.primitives import DeclaredAlphaModel

    result = directional_alpha_probe(
        lambda h: h * h,
        H6,
        probe_id="model_no_match_stable",
        function_label="square",
        declared_alpha_models=(DeclaredAlphaModel("sqrt", 0.5, 0.05),),
    )

    assert result.status is AlphaProbeStatus.ALPHA_MODEL_NO_MATCH
    assert result.value.alpha_stability_status is AlphaWindowStabilityStatus.STABLE


def test_fixture_f_preserves_indeterminate_refusal_and_skips_windows() -> None:
    scalar = scalar_alpha_jet_bundle(essential_fixture, 0.0, [1e-3, 1e-2, 1e-1, 0.5], probe_id="F_scalar", function_label="essential")
    singular = singular_alpha_jet_bundle(essential_fixture, 0.0, [1e-3, 1e-2, 1e-1, 0.5], probe_id="F_singular", function_label="essential")

    assert scalar.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_INDETERMINATE
    assert singular.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_INDETERMINATE
    assert scalar.value.alpha_probe_observation.alpha_stability_status is AlphaWindowStabilityStatus.NOT_TESTED
    assert singular.value.alpha_probe_observation.alpha_stability_status is AlphaWindowStabilityStatus.NOT_TESTED


def test_guard_g1_tiny_positive_alpha_remains_fractional_branch() -> None:
    result = singular_alpha_jet_bundle(lambda x: x**0.01, 0.0, H6, probe_id="G1", function_label="tiny_positive")
    alpha = result.value.alpha_probe_observation

    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH
    assert alpha.observed_alpha == pytest.approx(0.01, abs=1e-6)
    assert abs(alpha.observed_alpha) > boundary_envelope(alpha.standard_error)


def test_guard_g2_tiny_negative_alpha_remains_negative_singularity() -> None:
    def tiny_negative(x: float) -> float:
        if x == 0.0:
            raise ZeroDivisionError("undefined at zero")
        return x**-0.05

    scalar = scalar_alpha_jet_bundle(tiny_negative, 0.0, H6, probe_id="G2_scalar", function_label="tiny_negative")
    singular = singular_alpha_jet_bundle(tiny_negative, 0.0, H6, probe_id="G2_singular", function_label="tiny_negative")
    alpha = singular.value.alpha_probe_observation

    assert scalar.status is ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED
    assert singular.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert alpha.observed_alpha == pytest.approx(-0.05, abs=1e-6)
    assert abs(alpha.observed_alpha) > boundary_envelope(alpha.standard_error)


def test_declared_alpha_band_overrides_default_materiality() -> None:
    result = directional_alpha_probe(slow_drift_fixture, [10.0 ** (-i) for i in range(2, 9)], probe_id="band", function_label="slow", declared_alpha_band=0.001)

    assert result.status is AlphaProbeStatus.ALPHA_UNSTABLE_WINDOW
    assert result.value.alpha_window_span > 0.001


def test_declared_alpha_band_validation() -> None:
    directional_alpha_probe(lambda h: h, [1e-3, 1e-2, 1e-1], probe_id="ok", function_label="ok", declared_alpha_band=None)
    directional_alpha_probe(lambda h: h, [1e-3, 1e-2, 1e-1], probe_id="ok2", function_label="ok", declared_alpha_band=0.1)

    with pytest.raises(ValueError):
        directional_alpha_probe(lambda h: h, [1e-3, 1e-2, 1e-1], probe_id="bad", function_label="bad", declared_alpha_band=0.0)
    with pytest.raises(ValueError):
        directional_alpha_probe(lambda h: h, [1e-3, 1e-2, 1e-1], probe_id="bad2", function_label="bad", declared_alpha_band=-0.1)


def test_alpha_consumer_protocol_refuses_new_non_algebraic_statuses() -> None:
    boundary = directional_alpha_probe(negative_log_fixture, [10.0 ** (-i) for i in range(2, 10)], probe_id="protocolD", function_label="neg_log")
    unstable = directional_alpha_probe(iterated_log_fixture, E_H_GRID, probe_id="protocolE", function_label="iter")

    assert not validate_protocol(boundary, ALPHA_PROBE_CONSUMER_PROTOCOL).ok
    assert not validate_protocol(unstable, ALPHA_PROBE_CONSUMER_PROTOCOL).ok


def test_new_alpha_probe_statuses_are_not_selectable() -> None:
    boundary = directional_alpha_probe(negative_log_fixture, [10.0 ** (-i) for i in range(2, 10)], probe_id="validityD", function_label="neg_log")
    unstable = directional_alpha_probe(iterated_log_fixture, E_H_GRID, probe_id="validityE", function_label="iter")

    assert not boundary.validity.selectable
    assert not unstable.validity.selectable
    assert boundary.validity.finite
    assert unstable.validity.finite


def test_conditioning_notes_record_boundary_and_unstable_evidence() -> None:
    boundary = directional_alpha_probe(negative_log_fixture, [10.0 ** (-i) for i in range(2, 10)], probe_id="notesD", function_label="neg_log")
    unstable = directional_alpha_probe(iterated_log_fixture, E_H_GRID, probe_id="notesE", function_label="iter")

    assert any(note.startswith("alpha_boundary_envelope=") for note in boundary.conditioning.notes)
    assert any(note.startswith("materiality_limit=") for note in unstable.conditioning.notes)
    assert "alpha_stability_status=unstable" in unstable.conditioning.notes


def test_scalar_bundle_maps_zero_boundary_and_unstable_window() -> None:
    boundary = scalar_alpha_jet_bundle(scalar_boundary_fixture, 0.0, [10.0 ** (-i) for i in range(2, 10)], probe_id="scalarD", function_label="log")
    unstable = scalar_alpha_jet_bundle(scalar_unstable_fixture, 0.0, E_H_GRID, probe_id="scalarE", function_label="iter")

    assert boundary.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_ZERO_BOUNDARY
    assert boundary.value.alpha_status is AlphaProbeStatus.ALPHA_ZERO_BOUNDARY
    assert unstable.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_UNSTABLE_WINDOW
    assert unstable.value.alpha_status is AlphaProbeStatus.ALPHA_UNSTABLE_WINDOW


def test_singular_bundle_maps_zero_boundary_and_unstable_window() -> None:
    boundary = singular_alpha_jet_bundle(negative_log_fixture, 0.0, [10.0 ** (-i) for i in range(2, 10)], probe_id="singularD", function_label="log")
    unstable = singular_alpha_jet_bundle(iterated_log_fixture, 0.0, E_H_GRID, probe_id="singularE", function_label="iter")

    assert boundary.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_ZERO_BOUNDARY
    assert boundary.value.alpha_status is AlphaProbeStatus.ALPHA_ZERO_BOUNDARY
    assert unstable.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_UNSTABLE_WINDOW
    assert unstable.value.alpha_status is AlphaProbeStatus.ALPHA_UNSTABLE_WINDOW


def test_to_json_safe_serializes_new_fields_for_tested_and_skipped_cases() -> None:
    tested = directional_alpha_probe(iterated_log_fixture, E_H_GRID, probe_id="json1", function_label="iter")
    skipped = directional_alpha_probe(lambda h: h * h, [1e-3, 1e-2], probe_id="json2", function_label="square")

    tested_payload = json.loads(json.dumps(to_json_safe(tested), allow_nan=False))
    skipped_payload = json.loads(json.dumps(to_json_safe(skipped), allow_nan=False))

    assert tested_payload["value"]["nested_window_fits"]
    assert tested_payload["value"]["alpha_stability_status"] == "unstable"
    assert skipped_payload["value"]["nested_window_fits"] is None
    assert skipped_payload["value"]["alpha_stability_status"] == "not_tested"


def test_bundle_serialization_exposes_full_alpha_probe_observation() -> None:
    result = singular_alpha_jet_bundle(iterated_log_fixture, 0.0, E_H_GRID, probe_id="bundle_json", function_label="iter")
    payload = json.loads(json.dumps(to_json_safe(result), allow_nan=False))

    alpha_payload = payload["value"]["alpha_probe_observation"]
    assert alpha_payload["status"] if "status" in alpha_payload else True
    assert alpha_payload["alpha_stability_status"] == "unstable"
    assert alpha_payload["nested_window_fits"]
