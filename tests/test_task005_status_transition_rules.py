import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import MetrologyStatus, ProjectionStatus, ProjectiveRatioStatus, QuadraticRootStatus
from lloyd_v4.core.transitions import apply_status_transition
from lloyd_v4.metrology.noise_floor import LIMIT_OF_DETECTION_TRANSITION_RULE
from lloyd_v4.metrology.proxy_calibration import VALID_PROXY_CALIBRATION_TRANSITION_RULE
from lloyd_v4.primitives.projective_ratio import PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE
from lloyd_v4.primitives.stratified_quadratic_roots import QUADRATIC_ROOT_SELECTION_TRANSITION_RULE
from lloyd_v4.projection import BranchSelection
from lloyd_v4.projection.exact_projection import QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE


def test_projective_ratio_scalarization_transition_rule() -> None:
    accepted = apply_status_transition(
        PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE,
        ProjectiveRatioStatus.FINITE_RATIO,
    )
    refused = apply_status_transition(
        PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE,
        ProjectiveRatioStatus.INDETERMINATE,
    )

    assert accepted.disposition.value == "accepted"
    assert refused.disposition.value == "refused"
    with pytest.raises(ProtocolViolationError, match="status family"):
        apply_status_transition(PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE, ProjectionStatus.PROJECTION_TRANSVERSE)


def test_projection_contextual_transition_rule() -> None:
    cases = [
        (QuadraticRootStatus.TWO_REAL_ROOTS, BranchSelection.MINUS, ProjectionStatus.PROJECTION_TRANSVERSE),
        (QuadraticRootStatus.TWO_REAL_ROOTS, BranchSelection.PLUS, ProjectionStatus.PROJECTION_TRANSVERSE),
        (QuadraticRootStatus.TWO_REAL_ROOTS, BranchSelection.REPEATED, ProjectionStatus.PROJECTION_SELECTION_REFUSED),
        (QuadraticRootStatus.REPEATED_ROOT, BranchSelection.REPEATED, ProjectionStatus.PROJECTION_TANGENT_CONTACT),
        (QuadraticRootStatus.REPEATED_ROOT, BranchSelection.MINUS, ProjectionStatus.PROJECTION_SELECTION_REFUSED),
        (QuadraticRootStatus.LINEAR_ROOT, BranchSelection.LINEAR, ProjectionStatus.PROJECTION_LINEAR),
        (QuadraticRootStatus.NO_REAL_ROOT, BranchSelection.MINUS, ProjectionStatus.PROJECTION_NO_REAL_ROOT),
        (QuadraticRootStatus.CONSTANT_IDENTITY, BranchSelection.MINUS, ProjectionStatus.PROJECTION_IDENTITY),
        (QuadraticRootStatus.CONSTANT_NO_SOLUTION, BranchSelection.MINUS, ProjectionStatus.PROJECTION_NO_SOLUTION),
    ]

    for status, branch, expected in cases:
        outcome = apply_status_transition(
            QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE,
            status,
            branch=branch,
        )
        assert outcome.output_status is expected

    with pytest.raises(ProtocolViolationError, match="status family"):
        apply_status_transition(
            QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE,
            MetrologyStatus.CALIBRATION_VALID,
            branch=BranchSelection.MINUS,
        )


def test_metrology_transition_rules() -> None:
    detected = apply_status_transition(
        LIMIT_OF_DETECTION_TRANSITION_RULE,
        MetrologyStatus.NOISE_FLOOR_DECLARED,
        observable=2.0,
        noise_floor=1.0,
        identity_evidence=False,
    )
    identity = apply_status_transition(
        LIMIT_OF_DETECTION_TRANSITION_RULE,
        MetrologyStatus.NOISE_FLOOR_DECLARED,
        observable=0.0,
        noise_floor=1.0,
        identity_evidence=True,
    )
    refused = apply_status_transition(
        VALID_PROXY_CALIBRATION_TRANSITION_RULE,
        MetrologyStatus.CALIBRATION_INVALID,
    )

    assert detected.output_status is MetrologyStatus.DETECTED
    assert identity.output_status is MetrologyStatus.IDENTITY_ZERO
    assert refused.disposition.value == "refused"
    with pytest.raises(ProtocolViolationError):
        apply_status_transition(
            LIMIT_OF_DETECTION_TRANSITION_RULE,
            MetrologyStatus.NOISE_FLOOR_DECLARED,
            observable=2.0,
            noise_floor=1.0,
            identity_evidence=True,
        )
