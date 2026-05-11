from lloyd_v4.branch import SlopeFlowModel, SlopeFlowSample, build_branch_fingerprint, compare_kq_slope_stability, compare_slope_flow_to_models
from lloyd_v4.core.status import BranchFingerprintStatus, ProjectionStatus
from lloyd_v4.metrology import calibrate_proxy_kq
from lloyd_v4.primitives.stratified_quadratic_roots import stratified_quadratic_roots
from _projection_branch import project_with_branch


def _flow(status="unique"):
    samples = [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.0), SlopeFlowSample(4.0, 16.0)]
    if status == "observed":
        return compare_slope_flow_to_models(samples)
    if status == "ambiguous":
        return compare_slope_flow_to_models(samples, [SlopeFlowModel("a", 2.0), SlopeFlowModel("b", 2.0)], declared_model_band=0.1)
    return compare_slope_flow_to_models(samples, [SlopeFlowModel("square", 2.0)], declared_model_band=0.1)


def test_direct_transfer_fingerprint_complete_for_transverse_linear_and_tangent() -> None:
    transverse = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")
    linear = project_with_branch(stratified_quadratic_roots(0, 2, -4), "linear")
    tangent = project_with_branch(stratified_quadratic_roots(1, 2, 1), "repeated")

    for projection in [transverse, linear, tangent]:
        fingerprint = build_branch_fingerprint(projection, _flow())
        assert fingerprint.status is BranchFingerprintStatus.FINGERPRINT_COMPLETE
        assert fingerprint.value.projection_trace_id == projection.provenance.trace_id
        assert fingerprint.value.requested_branch == projection.value.requested_branch

    tangent_fingerprint = build_branch_fingerprint(tangent, _flow())
    assert tangent.status is ProjectionStatus.PROJECTION_TANGENT_CONTACT
    assert tangent_fingerprint.value.projection_status == ProjectionStatus.PROJECTION_TANGENT_CONTACT.value


def test_incomplete_unidentified_and_proxy_fingerprints() -> None:
    no_real = project_with_branch(stratified_quadratic_roots(1, 0, 1), "minus")
    incomplete = build_branch_fingerprint(no_real, _flow())
    unidentified = build_branch_fingerprint(project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus"), _flow("ambiguous"))
    missing_proxy = build_branch_fingerprint(
        project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus"),
        _flow(),
        observable_kind="proxy",
    )
    stable_kq = compare_kq_slope_stability(
        [1.0, 2.0],
        [calibrate_proxy_kq(2.0, 1.0), calibrate_proxy_kq(4.0, 2.0)],
        declared_stability_band=0.01,
    )
    proxy_complete = build_branch_fingerprint(
        project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus"),
        _flow(),
        observable_kind="proxy",
        kq_flow_result=stable_kq,
    )

    assert incomplete.status is BranchFingerprintStatus.FINGERPRINT_INCOMPLETE
    assert unidentified.status is BranchFingerprintStatus.FINGERPRINT_UNIDENTIFIED
    assert missing_proxy.status is BranchFingerprintStatus.FINGERPRINT_PROXY_UNCALIBRATED
    assert proxy_complete.status is BranchFingerprintStatus.FINGERPRINT_COMPLETE
