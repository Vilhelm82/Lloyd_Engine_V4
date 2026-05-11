from lloyd_v4.core.status import ProjectiveRatioStatus
from lloyd_v4.primitives.projective_ratio import ProjectiveRatioValue, projective_ratio


class NoDivideDenominator:
    def __eq__(self, other: object) -> bool:
        return other == 0

    def __rtruediv__(self, numerator: object) -> object:
        raise AssertionError("construction attempted scalar division")


def test_finite_denominator_and_nonzero_numerator_produces_finite_ratio() -> None:
    result = projective_ratio(6, 3)

    assert result.status is ProjectiveRatioStatus.FINITE_RATIO
    assert result.value == ProjectiveRatioValue(numerator=6, denominator=3)
    assert result.validity.defined is True
    assert result.validity.finite is True
    assert result.validity.selectable is True


def test_zero_numerator_with_finite_denominator_produces_signed_zero() -> None:
    result = projective_ratio(0, -4)

    assert result.status is ProjectiveRatioStatus.SIGNED_ZERO
    assert result.value == ProjectiveRatioValue(numerator=0, denominator=-4)
    assert result.validity.defined is True
    assert result.validity.finite is True
    assert result.validity.selectable is True


def test_zero_denominator_with_nonzero_numerator_produces_infinite_direction() -> None:
    result = projective_ratio(-5, 0)

    assert result.status is ProjectiveRatioStatus.INFINITE_DIRECTION
    assert result.value == ProjectiveRatioValue(numerator=-5, denominator=0)
    assert result.validity.defined is True
    assert result.validity.finite is False
    assert result.validity.selectable is False


def test_zero_numerator_and_zero_denominator_produces_indeterminate() -> None:
    result = projective_ratio(0, 0)

    assert result.status is ProjectiveRatioStatus.INDETERMINATE
    assert result.value == ProjectiveRatioValue(numerator=0, denominator=0)
    assert result.validity.defined is False
    assert result.validity.finite is False
    assert result.validity.selectable is False


def test_construction_preserves_raw_values_and_does_not_divide() -> None:
    denominator = NoDivideDenominator()

    result = projective_ratio(7, denominator)

    assert result.status is ProjectiveRatioStatus.INFINITE_DIRECTION
    assert result.value == ProjectiveRatioValue(numerator=7, denominator=denominator)


def test_projective_ratio_provenance_records_operation_and_path() -> None:
    result = projective_ratio(1, 2)

    assert result.provenance.operation_id == "projective_ratio"
    assert result.provenance.expression_path == "canonical_projective_ratio"
    assert result.provenance.precision == "raw_python"
