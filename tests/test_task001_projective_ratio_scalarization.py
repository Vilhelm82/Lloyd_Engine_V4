from lloyd_v4.core.status import ProjectiveRatioStatus, ProtocolStatus
from lloyd_v4.primitives.projective_ratio import projective_ratio, scalarize_projective_ratio


def test_scalarization_succeeds_for_finite_ratio() -> None:
    ratio = projective_ratio(9, 3)

    scalar = scalarize_projective_ratio(ratio)

    assert scalar.value == 3
    assert scalar.status is ProjectiveRatioStatus.FINITE_RATIO
    assert scalar.protocol is ProtocolStatus.OK
    assert scalar.refusal is None
    assert scalar.provenance.parents == (ratio.provenance.trace_id,)


def test_scalarization_succeeds_for_signed_zero() -> None:
    ratio = projective_ratio(0, -3)

    scalar = scalarize_projective_ratio(ratio)

    assert scalar.value == 0
    assert scalar.status is ProjectiveRatioStatus.SIGNED_ZERO
    assert scalar.protocol is ProtocolStatus.OK
    assert scalar.refusal is None
    assert scalar.provenance.parents == (ratio.provenance.trace_id,)


def test_scalarization_refuses_infinite_direction() -> None:
    ratio = projective_ratio(5, 0)

    scalar = scalarize_projective_ratio(ratio)

    assert scalar.value is None
    assert scalar.status is ProjectiveRatioStatus.INFINITE_DIRECTION
    assert scalar.protocol is ProtocolStatus.SCALARIZATION_REFUSED
    assert scalar.refusal is not None
    assert "infinite_direction" in scalar.refusal.reason


def test_scalarization_refuses_indeterminate() -> None:
    ratio = projective_ratio(0, 0)

    scalar = scalarize_projective_ratio(ratio)

    assert scalar.value is None
    assert scalar.status is ProjectiveRatioStatus.INDETERMINATE
    assert scalar.protocol is ProtocolStatus.SCALARIZATION_REFUSED
    assert scalar.refusal is not None
    assert "indeterminate" in scalar.refusal.reason
