from lloyd_v4.core.calculus import join_statuses
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import MetrologyStatus, ProjectiveRatioStatus
from lloyd_v4.metrology import calibrate_proxy_kq, classify_against_noise_floor, declare_bk_noise_floor, require_valid_proxy_calibration
from lloyd_v4.primitives.projective_ratio import projective_ratio, scalarize_projective_ratio
from lloyd_v4.primitives.stratified_quadratic_roots import select_quadratic_root, stratified_quadratic_roots
from _projection_branch import project_with_branch


def test_existing_flows_preserve_semantics_and_serialization_shape() -> None:
    ratio = projective_ratio(6, 3)
    scalar = scalarize_projective_ratio(ratio)
    roots = stratified_quadratic_roots(1, -3, 2)
    selected = select_quadratic_root(roots, "minus")
    projection = project_with_branch(roots, "minus")
    floor = declare_bk_noise_floor(1.0)
    detection = classify_against_noise_floor(2.0, floor)
    calibration = calibrate_proxy_kq(6.0, 3.0)
    accepted_calibration = require_valid_proxy_calibration(calibration)

    assert scalar.value == 2
    assert selected.value == 1.0
    assert projection.status.value == "projection_transverse"
    assert detection.status is MetrologyStatus.DETECTED
    assert accepted_calibration.value.kq_scalar_value == 2.0
    assert "__orig_class__" not in to_json_safe(projection)


def test_generic_mixed_joins_remain_conservative() -> None:
    assert join_statuses("same", [ProjectiveRatioStatus.FINITE_RATIO, ProjectiveRatioStatus.FINITE_RATIO]) is ProjectiveRatioStatus.FINITE_RATIO

    for statuses in [[], [ProjectiveRatioStatus.FINITE_RATIO, MetrologyStatus.CALIBRATION_VALID]]:
        try:
            join_statuses("mixed", statuses)
        except ProtocolViolationError:
            pass
        else:
            raise AssertionError("join_statuses accepted an invalid mixed join")
