from lloyd_v4.core.status import ProjectionStatus
from lloyd_v4.primitives import stratified_quadratic_roots
from lloyd_v4.projection import BranchSelection, branch_selection, exact_quadratic_projection


def _project(a, b, c, branch: BranchSelection):
    return exact_quadratic_projection(stratified_quadratic_roots(a, b, c), branch_selection(branch))


def test_selectable_strata_project_to_expected_statuses() -> None:
    minus = _project(1, -3, 2, BranchSelection.MINUS)
    plus = _project(1, -3, 2, BranchSelection.PLUS)
    repeated = _project(1, 2, 1, BranchSelection.REPEATED)
    linear = _project(0, 2, -4, BranchSelection.LINEAR)

    assert minus.status is ProjectionStatus.PROJECTION_TRANSVERSE
    assert minus.value.selected_root_value == 1.0
    assert plus.status is ProjectionStatus.PROJECTION_TRANSVERSE
    assert plus.value.selected_root_value == 2.0
    assert repeated.status is ProjectionStatus.PROJECTION_TANGENT_CONTACT
    assert repeated.validity.advanceable is False
    assert linear.status is ProjectionStatus.PROJECTION_LINEAR
    assert linear.value.selected_root_value == 2


def test_nonselectable_strata_project_without_selection() -> None:
    no_real = _project(1, 0, 1, BranchSelection.MINUS)
    identity = _project(0, 0, 0, BranchSelection.LINEAR)
    no_solution = _project(0, 0, 5, BranchSelection.LINEAR)

    assert no_real.status is ProjectionStatus.PROJECTION_NO_REAL_ROOT
    assert no_real.value.selected_root_trace_id is None
    assert identity.status is ProjectionStatus.PROJECTION_IDENTITY
    assert identity.value.selected_root_trace_id is None
    assert no_solution.status is ProjectionStatus.PROJECTION_NO_SOLUTION
    assert no_solution.value.selected_root_trace_id is None


def test_incompatible_branch_projects_to_selection_refused() -> None:
    cases = [
        (stratified_quadratic_roots(1, -3, 2), BranchSelection.LINEAR),
        (stratified_quadratic_roots(1, 2, 1), BranchSelection.PLUS),
        (stratified_quadratic_roots(0, 2, -4), BranchSelection.MINUS),
    ]

    for root, branch in cases:
        projection = exact_quadratic_projection(root, branch_selection(branch))
        assert projection.status is ProjectionStatus.PROJECTION_SELECTION_REFUSED
        assert projection.refusal is not None
        assert projection.value.selected_root_trace_id is None
