from dataclasses import replace

from lloyd_v4.branch import SlopeFlowModel, SlopeFlowSample, build_branch_fingerprint, compare_slope_flow_to_models
from lloyd_v4.core.status import RefineryStatus
from lloyd_v4.primitives.stratified_quadratic_roots import stratified_quadratic_roots
from _projection_branch import project_with_branch
from lloyd_v4.refinery import compute_slag_vector, evaluate_rewrite_candidate, snapshot_typed_result


def _fingerprint_snapshot(scenario_id: str = "fp", *, residual: float | None = None):
    projection = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")
    flow = compare_slope_flow_to_models(
        [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.2), SlopeFlowSample(4.0, 16.0)],
        [SlopeFlowModel("square", 2.0)],
        declared_model_band=0.3,
    )
    snapshot = snapshot_typed_result(build_branch_fingerprint(projection, flow), label="reference", scenario_id=scenario_id)
    if residual is None:
        return snapshot
    return replace(snapshot, value_fingerprint={**snapshot.value_fingerprint, "max_model_residual": residual})


def test_same_geometry_componentwise_lower_slag_is_accepted() -> None:
    reference = _fingerprint_snapshot(residual=0.1)
    candidate = replace(_fingerprint_snapshot(residual=0.0), label="candidate")

    result = evaluate_rewrite_candidate(
        [reference],
        [candidate],
        candidate_name="candidate",
        declared_slag_dimensions=["max_model_residual"],
    )

    assert result.status is RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG
    assert result.value.accepted is True
    assert "weighted_score" not in result.to_json_safe()["value"]


def test_same_geometry_equal_slag_is_equivalent_no_improvement() -> None:
    reference = _fingerprint_snapshot(residual=0.1)
    candidate = replace(_fingerprint_snapshot(residual=0.1), label="candidate")

    result = evaluate_rewrite_candidate(
        [reference],
        [candidate],
        candidate_name="candidate",
        declared_slag_dimensions=["max_model_residual"],
    )

    assert result.status is RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT


def test_one_worse_declared_dimension_rejects_slag_regression() -> None:
    reference = _fingerprint_snapshot(residual=0.1)
    candidate = replace(_fingerprint_snapshot(residual=0.2), label="candidate")

    result = evaluate_rewrite_candidate(
        [reference],
        [candidate],
        candidate_name="candidate",
        declared_slag_dimensions=["max_model_residual"],
    )

    assert result.status is RefineryStatus.REWRITE_REJECTED_SLAG_REGRESSION


def test_lower_warning_count_requires_preserved_geometry() -> None:
    reference = snapshot_typed_result(
        project_with_branch(stratified_quadratic_roots(1, 2, 1), "repeated"),
        label="reference",
        scenario_id="projection",
    )
    candidate = replace(reference, label="candidate", conditioning={"status": "well_conditioned", "notes": []})

    result = evaluate_rewrite_candidate(
        [reference],
        [candidate],
        candidate_name="candidate",
        declared_slag_dimensions=["warning_count"],
    )

    assert result.status is RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG


def test_absent_dimensions_are_not_replaced_with_numeric_sentinels() -> None:
    snapshot = snapshot_typed_result(
        project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus"),
        label="reference",
        scenario_id="projection",
    )

    slag = compute_slag_vector(snapshot, declared_dimensions=["max_model_residual"])

    assert slag.components == {}
    assert "max_model_residual" in slag.unavailable_dimensions
