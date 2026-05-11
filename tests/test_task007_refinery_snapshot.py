import pytest

from lloyd_v4.branch import SlopeFlowModel, SlopeFlowSample, build_branch_fingerprint, compare_slope_flow_to_models
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import BranchFingerprintStatus, MetrologyStatus, ProjectiveRatioStatus, ProjectionStatus, QuadraticRootStatus
from lloyd_v4.metrology import calibrate_proxy_kq, declare_bk_noise_floor
from lloyd_v4.primitives.projective_ratio import projective_ratio
from lloyd_v4.primitives.stratified_quadratic_roots import stratified_quadratic_roots
from _projection_branch import project_with_branch
from lloyd_v4.refinery import snapshot_typed_result


def _fingerprint():
    roots = stratified_quadratic_roots(1, -3, 2)
    projection = project_with_branch(roots, "minus")
    flow = compare_slope_flow_to_models(
        [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.0), SlopeFlowSample(4.0, 16.0)],
        [SlopeFlowModel("square", 2.0)],
        declared_model_band=0.1,
    )
    return build_branch_fingerprint(projection, flow)


def test_snapshot_typed_result_rejects_raw_inputs() -> None:
    for raw in [1, (1, 2), {"value": 1}, lambda: 1, object(), "typed"]:
        with pytest.raises(ProtocolViolationError):
            snapshot_typed_result(raw, label="raw", scenario_id="s0")


def test_projective_ratio_snapshot_preserves_shape_protocol_and_trace() -> None:
    result = projective_ratio(3, 4)
    snapshot = snapshot_typed_result(result, label="reference", scenario_id="ratio")

    assert snapshot.status_family == "ProjectiveRatioStatus"
    assert snapshot.status == ProjectiveRatioStatus.FINITE_RATIO.value
    assert snapshot.protocol_identity == "projective_ratio"
    assert snapshot.trace_id == result.provenance.trace_id
    assert snapshot.validity["finite"] is True
    assert snapshot.value_fingerprint["coordinate_shape"] == "finite"


def test_quadratic_root_snapshot_preserves_branch_labels_and_trace() -> None:
    result = stratified_quadratic_roots(1, -3, 2)
    snapshot = snapshot_typed_result(result, label="reference", scenario_id="roots")

    assert snapshot.status_family == "QuadraticRootStatus"
    assert snapshot.status == QuadraticRootStatus.TWO_REAL_ROOTS.value
    assert snapshot.protocol_identity == "stratified_quadratic_roots"
    assert snapshot.value_fingerprint["branch_labels"] == ["minus", "plus"]
    assert snapshot.source_trace_ids == ()


def test_projection_snapshot_preserves_branch_status_and_sources() -> None:
    roots = stratified_quadratic_roots(1, -3, 2)
    projection = project_with_branch(roots, "minus")
    snapshot = snapshot_typed_result(projection, label="reference", scenario_id="projection")

    assert snapshot.status_family == "ProjectionStatus"
    assert snapshot.status == ProjectionStatus.PROJECTION_TRANSVERSE.value
    assert snapshot.protocol_identity == "projection_result_v4"
    assert snapshot.value_fingerprint["requested_branch"] == "minus"
    assert snapshot.value_fingerprint["selected_branch"] == "minus"
    assert "projection_flags" not in snapshot.value_fingerprint
    assert roots.provenance.trace_id in snapshot.source_trace_ids


def test_metrology_snapshot_preserves_role_and_status() -> None:
    noise = declare_bk_noise_floor(0.5)
    calibration = calibrate_proxy_kq(2.0, 1.0)

    noise_snapshot = snapshot_typed_result(noise, label="reference", scenario_id="noise")
    calibration_snapshot = snapshot_typed_result(calibration, label="reference", scenario_id="calibration")

    assert noise_snapshot.status == MetrologyStatus.NOISE_FLOOR_DECLARED.value
    assert noise_snapshot.value_fingerprint["metrology_role"] == "noise_floor"
    assert calibration_snapshot.status == MetrologyStatus.CALIBRATION_VALID.value
    assert calibration_snapshot.value_fingerprint["metrology_role"] == "proxy_calibration"


def test_branch_fingerprint_snapshot_preserves_model_proxy_and_projection_evidence() -> None:
    fingerprint = _fingerprint()
    snapshot = snapshot_typed_result(fingerprint, label="reference", scenario_id="fingerprint")

    assert snapshot.status_family == "BranchFingerprintStatus"
    assert snapshot.status == BranchFingerprintStatus.FINGERPRINT_COMPLETE.value
    assert snapshot.protocol_identity == "branch_fingerprint"
    assert snapshot.value_fingerprint["observable_kind"] == "direct_transfer"
    assert snapshot.value_fingerprint["selected_model_name"] == "square"
    assert snapshot.value_fingerprint["selected_branch"] == "minus"
    assert snapshot.value_fingerprint["proxy_mode"] == "direct"
    assert set(fingerprint.value.source_trace_ids).issubset(set(snapshot.source_trace_ids))
