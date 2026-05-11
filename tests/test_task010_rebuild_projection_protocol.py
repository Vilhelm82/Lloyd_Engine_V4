import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import (
    ProjectiveRatioStatus,
    ProjectionStatus,
    ValueStatus,
)
from lloyd_v4.primitives import projective_ratio, stratified_quadratic_roots
from lloyd_v4.projection import BranchSelection, branch_selection, exact_quadratic_projection


def test_wrong_python_types_raise_programmer_error() -> None:
    branch = branch_selection(BranchSelection.MINUS)
    root = stratified_quadratic_roots(1, -3, 2)

    with pytest.raises(ProtocolViolationError):
        exact_quadratic_projection((1, -3, 2), branch)
    with pytest.raises(ProtocolViolationError):
        exact_quadratic_projection(root, "minus")
    with pytest.raises(ProtocolViolationError):
        exact_quadratic_projection(projective_ratio(1, 2), branch)


def test_wrong_status_on_root_typed_result_returns_typed_refusal() -> None:
    wrong_status_root = stratified_quadratic_roots(1, -3, 2)
    original_status = wrong_status_root.status
    object.__setattr__(wrong_status_root, "status", ProjectiveRatioStatus.FINITE_RATIO)
    branch = branch_selection(BranchSelection.MINUS)

    try:
        projection = exact_quadratic_projection(wrong_status_root, branch)
    finally:
        object.__setattr__(wrong_status_root, "status", original_status)

    assert projection.status is ProjectionStatus.PROJECTION_SELECTION_REFUSED
    assert projection.refusal is not None
    assert "status family mismatch" in projection.refusal.reason
    assert wrong_status_root.provenance.trace_id in projection.provenance.parents
    assert branch.provenance.trace_id in projection.provenance.parents


def test_wrong_status_on_branch_typed_result_returns_typed_refusal() -> None:
    root = stratified_quadratic_roots(1, -3, 2)
    bad_branch = branch_selection(BranchSelection.MINUS)
    original_status = bad_branch.status
    object.__setattr__(bad_branch, "status", ValueStatus.VALUE_ABSENT)

    try:
        projection = exact_quadratic_projection(root, bad_branch)
    finally:
        object.__setattr__(bad_branch, "status", original_status)

    assert projection.status is ProjectionStatus.PROJECTION_SELECTION_REFUSED
    assert projection.refusal is not None
    assert "unhandled status" in projection.refusal.reason
    assert root.provenance.trace_id in projection.provenance.parents
    assert bad_branch.provenance.trace_id in projection.provenance.parents
