from lloyd_v4.branch import SlopeFlowModel, SlopeFlowSample, compare_slope_flow_to_models
from lloyd_v4.core.status import BranchFingerprintStatus, MetrologyStatus
from lloyd_v4.metrology import classify_against_noise_floor, declare_bk_noise_floor


def test_direct_slope_flow_observed_without_models() -> None:
    result = compare_slope_flow_to_models(
        [SlopeFlowSample(1.0, 2.0), SlopeFlowSample(2.0, 4.0), SlopeFlowSample(4.0, 8.0)]
    )

    assert result.status is BranchFingerprintStatus.SLOPE_FLOW_OBSERVED
    assert len(result.value.segment_evidence) == 2
    assert result.value.segment_evidence[0].slope == 1.0
    assert result.value.selected_model_name is None
    assert result.validity.defined is True


def test_model_residual_unique_ambiguous_and_no_match() -> None:
    samples = [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.0), SlopeFlowSample(4.0, 16.0)]
    models = [SlopeFlowModel("square", 2.0), SlopeFlowModel("linear", 1.0)]
    residuals = compare_slope_flow_to_models(samples, models)
    unique = compare_slope_flow_to_models(samples, models, declared_model_band=0.1)
    ambiguous = compare_slope_flow_to_models(
        samples,
        [SlopeFlowModel("square_a", 2.0), SlopeFlowModel("square_b", 2.0)],
        declared_model_band=0.1,
    )
    no_match = compare_slope_flow_to_models(samples, [SlopeFlowModel("flat", 0.0)], declared_model_band=0.1)

    assert residuals.status is BranchFingerprintStatus.SLOPE_MODEL_RESIDUALS
    assert residuals.value.selected_model_name is None
    assert unique.status is BranchFingerprintStatus.SLOPE_MODEL_UNIQUE_MATCH
    assert unique.value.selected_model_name == "square"
    assert ambiguous.status is BranchFingerprintStatus.SLOPE_MODEL_AMBIGUOUS
    assert no_match.status is BranchFingerprintStatus.SLOPE_MODEL_NO_MATCH


def test_insufficient_and_indeterminate_samples() -> None:
    floor = declare_bk_noise_floor(1.0)
    below = classify_against_noise_floor(0.5, floor)
    detected = classify_against_noise_floor(2.0, floor)

    insufficient = compare_slope_flow_to_models(
        [
            SlopeFlowSample(1.0, 0.5, detection_trace_id=below.provenance.trace_id, detection_status=below.status.value),
            SlopeFlowSample(2.0, 2.0, detection_trace_id=detected.provenance.trace_id, detection_status=detected.status.value),
        ]
    )
    repeated_control = compare_slope_flow_to_models([SlopeFlowSample(1.0, 1.0), SlopeFlowSample(1.0, 2.0)])
    zero_observable = compare_slope_flow_to_models([SlopeFlowSample(1.0, 0.0), SlopeFlowSample(2.0, 2.0)])

    assert insufficient.status is BranchFingerprintStatus.SLOPE_FLOW_INSUFFICIENT_SAMPLES
    assert insufficient.value.samples[0].detection_status == MetrologyStatus.BELOW_LIMIT_OF_DETECTION.value
    assert repeated_control.status is BranchFingerprintStatus.SLOPE_FLOW_INDETERMINATE
    assert repeated_control.value.segment_evidence[0].refusal_reason is not None
    assert zero_observable.status is BranchFingerprintStatus.SLOPE_FLOW_INSUFFICIENT_SAMPLES
