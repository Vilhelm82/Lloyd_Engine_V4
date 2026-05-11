from dataclasses import replace

from lloyd_v4.branch import SlopeFlowModel, SlopeFlowSample, build_branch_fingerprint, compare_slope_flow_to_models
from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.protocols import ProducerProtocol
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.status import ConditioningStatus, MetrologyStatus, ProjectiveRatioStatus, RefineryStatus
from lloyd_v4.core.validity import Validity
from lloyd_v4.metrology import declare_bk_noise_floor
from lloyd_v4.primitives.projective_ratio import ProjectiveRatioValue, projective_ratio
from lloyd_v4.primitives.stratified_quadratic_roots import stratified_quadratic_roots
from _projection_branch import project_with_branch
from lloyd_v4.refinery import compare_refinery_scenario, snapshot_typed_result


def _projection_observation(branch: str, scenario_id: str = "projection"):
    return snapshot_typed_result(
        project_with_branch(stratified_quadratic_roots(1, -3, 2), branch),
        label=branch,
        scenario_id=scenario_id,
    )


def _fingerprint(model_name: str):
    projection = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")
    flow = compare_slope_flow_to_models(
        [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.0), SlopeFlowSample(4.0, 16.0)],
        [SlopeFlowModel(model_name, 2.0)],
        declared_model_band=0.1,
    )
    return snapshot_typed_result(build_branch_fingerprint(projection, flow), label=model_name, scenario_id="fingerprint")


def test_identical_protocol_status_validity_and_geometry_passes() -> None:
    reference = _projection_observation("minus")
    candidate = _projection_observation("minus")

    comparison = compare_refinery_scenario(reference, candidate)

    assert comparison.status is RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT
    assert comparison.geometry_match is True


def test_different_protocol_is_rejected() -> None:
    reference = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    candidate = replace(reference, label="candidate", protocol_identity="different_protocol")

    comparison = compare_refinery_scenario(reference, candidate)

    assert comparison.status is RefineryStatus.REWRITE_REJECTED_PROTOCOL_MISMATCH


def test_wrong_status_family_is_rejected() -> None:
    reference = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    candidate = snapshot_typed_result(declare_bk_noise_floor(1.0), label="candidate", scenario_id="s")

    comparison = compare_refinery_scenario(reference, candidate)

    assert comparison.status is RefineryStatus.REWRITE_REJECTED_STATUS_FAMILY_MISMATCH


def test_same_family_different_status_is_rejected() -> None:
    reference = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    candidate = snapshot_typed_result(projective_ratio(1, 0), label="candidate", scenario_id="s")

    comparison = compare_refinery_scenario(reference, candidate)

    assert comparison.status is RefineryStatus.REWRITE_REJECTED_STATUS_MISMATCH


def test_same_status_different_validity_is_rejected() -> None:
    reference = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    candidate = replace(reference, label="candidate", validity={**reference.validity, "finite": False})

    comparison = compare_refinery_scenario(reference, candidate)

    assert comparison.status is RefineryStatus.REWRITE_REJECTED_VALIDITY_MISMATCH


def test_projection_selected_branch_change_is_geometry_mismatch() -> None:
    reference = _projection_observation("minus")
    candidate = _projection_observation("plus")

    comparison = compare_refinery_scenario(reference, candidate)

    assert comparison.status is RefineryStatus.REWRITE_REJECTED_GEOMETRY_MISMATCH


def test_projection_value_status_change_is_geometry_mismatch() -> None:
    reference = _projection_observation("minus")
    altered = {
        **reference.value_fingerprint,
        "projection_status": "projection_tangent_contact",
    }
    candidate = replace(reference, label="candidate", value_fingerprint=altered)

    comparison = compare_refinery_scenario(reference, candidate)

    assert comparison.status is RefineryStatus.REWRITE_REJECTED_GEOMETRY_MISMATCH


def test_branch_fingerprint_selected_model_change_is_geometry_mismatch() -> None:
    comparison = compare_refinery_scenario(_fingerprint("square"), _fingerprint("other"))

    assert comparison.status is RefineryStatus.REWRITE_REJECTED_GEOMETRY_MISMATCH


def test_branch_fingerprint_preserved_model_remains_slag_eligible() -> None:
    reference = _fingerprint("square")
    candidate = replace(
        reference,
        label="candidate",
        value_fingerprint={**reference.value_fingerprint, "max_model_residual": 0.0},
    )

    comparison = compare_refinery_scenario(reference, candidate, declared_slag_dimensions=["max_model_residual"])

    assert comparison.status is RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT
    assert comparison.geometry_match is True


def test_unknown_family_snapshot_is_indeterminate_unhandled() -> None:
    protocol = ProducerProtocol(
        name="synthetic_projective",
        emitted_statuses=frozenset({ProjectiveRatioStatus.FINITE_RATIO}),
    )
    result = TypedResult(
        value=ProjectiveRatioValue(1, 2),
        space="Synthetic",
        status=ProjectiveRatioStatus.FINITE_RATIO,
        validity=Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True),
        conditioning=Conditioning(status=ConditioningStatus.WELL_CONDITIONED),
        provenance=projective_ratio(1, 2).provenance,
    )
    reference = snapshot_typed_result(result, label="reference", scenario_id="s")
    candidate = replace(reference, label="candidate", protocol_identity=protocol.name)

    comparison = compare_refinery_scenario(reference, candidate)

    assert comparison.status is RefineryStatus.REWRITE_REJECTED_PROTOCOL_MISMATCH
