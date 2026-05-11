import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.metrology import classify_against_noise_floor, declare_bk_noise_floor, require_valid_proxy_calibration
from lloyd_v4.primitives.projective_ratio import PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL, projective_ratio
from lloyd_v4.primitives.stratified_quadratic_roots import (
    QUADRATIC_ROOT_SELECTION_PROTOCOL,
    select_quadratic_root,
    stratified_quadratic_roots,
)
from _projection_branch import project_with_branch


def test_projective_ratio_protocol_rejects_wrong_status_family_explicitly() -> None:
    projection = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")

    check = validate_protocol(projection, PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL)

    assert not check.ok
    assert "status family" in check.reason


def test_quadratic_selection_rejects_projective_and_projection_inputs() -> None:
    ratio = projective_ratio(1, 2)
    projection = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")

    ratio_check = validate_protocol(ratio, QUADRATIC_ROOT_SELECTION_PROTOCOL)
    projection_check = validate_protocol(projection, QUADRATIC_ROOT_SELECTION_PROTOCOL)

    assert "status family" in ratio_check.reason
    assert "status family" in projection_check.reason
    with pytest.raises(ProtocolViolationError):
        select_quadratic_root(ratio, "minus")


def test_projection_and_metrology_consumers_still_reject_unrelated_inputs() -> None:
    with pytest.raises(ProtocolViolationError):
        project_with_branch((1, -3, 2), "minus")

    with pytest.raises(ProtocolViolationError):
        classify_against_noise_floor(1.0, projective_ratio(1, 2))

    with pytest.raises(ProtocolViolationError):
        require_valid_proxy_calibration(projective_ratio(1, 2))

    with pytest.raises(ProtocolViolationError):
        require_valid_proxy_calibration(1.0)


def test_metrology_protocol_rejects_projection_result_where_noise_floor_required() -> None:
    projection = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")

    with pytest.raises(ProtocolViolationError, match="noise-floor"):
        classify_against_noise_floor(1.0, projection)

    floor = declare_bk_noise_floor(1.0)
    classified = classify_against_noise_floor(2.0, floor)
    assert classified.status.value == "detected"
