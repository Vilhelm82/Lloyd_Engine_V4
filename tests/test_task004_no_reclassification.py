from lloyd_v4.core.status import ProjectionStatus, ProjectiveRatioStatus, QuadraticRootStatus
from lloyd_v4.metrology import (
    calibrate_proxy_kq,
    classify_against_noise_floor,
    declare_bk_noise_floor,
    estimate_bk_noise_floor,
)
from lloyd_v4.primitives.projective_ratio import projective_ratio
from lloyd_v4.primitives.stratified_quadratic_roots import stratified_quadratic_roots
from _projection_branch import project_with_branch


def test_metrology_does_not_reclassify_prior_exact_strata() -> None:
    ratio_inf = projective_ratio(1.0, 0.0)
    ratio_indeterminate = projective_ratio(0.0, 0.0)
    no_real = stratified_quadratic_roots(1.0, 0.0, 1.0)
    repeated = stratified_quadratic_roots(1.0, 2.0, 1.0)
    tangent = project_with_branch(repeated, "repeated")

    floor = declare_bk_noise_floor(1.0)
    estimate_bk_noise_floor([0.0, 1.0])
    classify_against_noise_floor(0.5, floor)
    calibrate_proxy_kq(6.0, 3.0)

    assert ratio_inf.status is ProjectiveRatioStatus.INFINITE_DIRECTION
    assert ratio_indeterminate.status is ProjectiveRatioStatus.INDETERMINATE
    assert no_real.status is QuadraticRootStatus.NO_REAL_ROOT
    assert repeated.status is QuadraticRootStatus.REPEATED_ROOT
    assert tangent.status is ProjectionStatus.PROJECTION_TANGENT_CONTACT
