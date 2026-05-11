from lloyd_v4.core.status import ProjectionStatus
from lloyd_v4.primitives import stratified_quadratic_roots
from lloyd_v4.projection import BranchSelection, branch_selection, exact_quadratic_projection


def test_projection_result_has_no_flags_or_value_refusal_duplication() -> None:
    root = stratified_quadratic_roots(1, -3, 2)
    branch = branch_selection(BranchSelection.MINUS)

    projection = exact_quadratic_projection(root, branch)

    assert projection.status is ProjectionStatus.PROJECTION_TRANSVERSE
    assert not hasattr(projection.value, "flags")
    assert not hasattr(projection.value, "refusal")
    assert projection.value.source_trace_id == root.provenance.trace_id
    assert projection.value.source_operation_id == "stratified_quadratic_roots"
    assert projection.value.requested_branch == "minus"
    assert projection.value.selected_branch == "minus"
    assert root.provenance.trace_id in projection.provenance.parents
    assert branch.provenance.trace_id in projection.provenance.parents
    assert projection.value.selected_root_trace_id in projection.provenance.parents


def test_selection_refusal_uses_typed_result_refusal_only() -> None:
    root = stratified_quadratic_roots(1, -3, 2)
    branch = branch_selection(BranchSelection.LINEAR)

    projection = exact_quadratic_projection(root, branch)

    assert projection.status is ProjectionStatus.PROJECTION_SELECTION_REFUSED
    assert projection.refusal is not None
    assert projection.refusal.details["branch"] == "linear"
    assert projection.value.selected_branch is None
    assert projection.value.selected_root_trace_id is None
    assert not hasattr(projection.value, "refusal")
