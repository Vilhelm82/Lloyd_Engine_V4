import pytest

from lloyd_v4.branch import SlopeFlowModel, SlopeFlowSample, build_branch_fingerprint, compare_slope_flow_to_models
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import BranchFingerprintStatus, HistoryStatus, MetrologyStatus, ProjectiveRatioStatus, ProjectionStatus, QuadraticRootStatus, RefineryStatus
from lloyd_v4.history import record_status_event
from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.primitives.projective_ratio import projective_ratio
from lloyd_v4.primitives.stratified_quadratic_roots import stratified_quadratic_roots
from _projection_branch import project_with_branch
from lloyd_v4.refinery import evaluate_rewrite_candidate, snapshot_typed_result


def _branch_fingerprint():
    projection = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")
    flow = compare_slope_flow_to_models(
        [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.0), SlopeFlowSample(4.0, 16.0)],
        [SlopeFlowModel("square", 2.0)],
        declared_model_band=0.1,
    )
    return build_branch_fingerprint(projection, flow)


def _refinery_decision():
    snapshot = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    return evaluate_rewrite_candidate([snapshot], [snapshot], candidate_name="candidate")


def test_records_existing_status_families_as_compact_events() -> None:
    cases = [
        (projective_ratio(1, 2), ProjectiveRatioStatus.FINITE_RATIO.value, "ProjectiveRatioStatus"),
        (stratified_quadratic_roots(1, -3, 2), QuadraticRootStatus.TWO_REAL_ROOTS.value, "QuadraticRootStatus"),
        (project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus"), ProjectionStatus.PROJECTION_TRANSVERSE.value, "ProjectionStatus"),
        (declare_bk_noise_floor(0.5), MetrologyStatus.NOISE_FLOOR_DECLARED.value, "MetrologyStatus"),
        (_branch_fingerprint(), BranchFingerprintStatus.FINGERPRINT_COMPLETE.value, "BranchFingerprintStatus"),
        (_refinery_decision(), RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT.value, "RefineryStatus"),
    ]

    for index, (source, status, family) in enumerate(cases):
        event = record_status_event(source, stream_id="stream", observation_key=f"obs-{index}", step_index=index, geometry_signature="shape")
        assert event.status is HistoryStatus.HISTORY_EVENT_RECORDED
        assert event.value.source_status == status
        assert event.value.source_status_family == family
        assert event.value.source_trace_id == source.provenance.trace_id
        assert event.value.geometry_signature == "shape"
        assert event.provenance.parents == (source.provenance.trace_id,)


def test_event_recording_preserves_protocol_validity_conditioning_and_source_metadata() -> None:
    source = projective_ratio(1, 2)
    event = record_status_event(source, stream_id="stream", observation_key="ratio", step_index=3, scenario_id="scenario")

    assert event.value.source_protocol == "projective_ratio"
    assert event.value.source_validity["defined"] is True
    assert event.value.source_conditioning == "well_conditioned"
    assert event.value.source_operation_id == source.provenance.operation_id
    assert event.value.source_expression_path == source.provenance.expression_path
    assert event.value.source_precision == source.provenance.precision
    assert event.value.source_backend == source.provenance.backend
    assert event.value.source_device == source.provenance.device


def test_record_status_event_rejects_invalid_inputs() -> None:
    source = projective_ratio(1, 2)
    invalid_calls = [
        dict(result=object(), stream_id="s", observation_key="o", step_index=0),
        dict(result=source, stream_id="", observation_key="o", step_index=0),
        dict(result=source, stream_id="s", observation_key="", step_index=0),
        dict(result=source, stream_id="s", observation_key="o", step_index=-1),
        dict(result=source, stream_id="s", observation_key="o", step_index=0, scenario_id=""),
        dict(result=source, stream_id="s", observation_key="o", step_index=0, geometry_signature=""),
    ]

    for kwargs in invalid_calls:
        with pytest.raises(ProtocolViolationError):
            record_status_event(**kwargs)
