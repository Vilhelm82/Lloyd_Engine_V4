import math

import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import ConditioningStatus, QuadraticRootStatus
from lloyd_v4.primitives.projective_ratio import ProjectiveRatioValue
from lloyd_v4.primitives.stratified_quadratic_roots import (
    QuadraticCoefficients,
    QuadraticRootCoordinate,
    stratified_quadratic_roots,
)


def test_two_real_roots_classification_and_coordinates() -> None:
    result = stratified_quadratic_roots(1, -3, 2)

    assert result.status is QuadraticRootStatus.TWO_REAL_ROOTS
    assert result.value.coefficients == QuadraticCoefficients(a=1, b=-3, c=2)
    assert result.value.discriminant == 1
    assert set(result.value.coordinates) == {"minus", "plus"}
    assert result.value.coordinates["minus"] == QuadraticRootCoordinate(
        branch="minus",
        coordinate=ProjectiveRatioValue(numerator=2.0, denominator=2),
    )
    assert result.value.coordinates["plus"] == QuadraticRootCoordinate(
        branch="plus",
        coordinate=ProjectiveRatioValue(numerator=4.0, denominator=2),
    )
    assert result.validity.defined is True
    assert result.validity.selectable is True


def test_repeated_root_classification_and_coordinate_without_sqrt_branch() -> None:
    result = stratified_quadratic_roots(1, 2, 1)

    assert result.status is QuadraticRootStatus.REPEATED_ROOT
    assert result.value.discriminant == 0
    assert set(result.value.coordinates) == {"repeated"}
    assert result.value.coordinates["repeated"].coordinate == ProjectiveRatioValue(
        numerator=-2,
        denominator=2,
    )
    assert result.conditioning.status is ConditioningStatus.WARNING


def test_no_real_root_classification_has_no_coordinates() -> None:
    result = stratified_quadratic_roots(1, 0, 1)

    assert result.status is QuadraticRootStatus.NO_REAL_ROOT
    assert result.value.discriminant == -4
    assert result.value.coordinates == {}
    assert result.validity.finite is False


def test_linear_root_classification_and_coordinate() -> None:
    result = stratified_quadratic_roots(0, 2, -4)

    assert result.status is QuadraticRootStatus.LINEAR_ROOT
    assert result.value.discriminant is None
    assert set(result.value.coordinates) == {"linear"}
    assert result.value.coordinates["linear"].coordinate == ProjectiveRatioValue(
        numerator=4,
        denominator=2,
    )


def test_constant_identity_and_no_solution_have_no_selected_scalar_root() -> None:
    identity = stratified_quadratic_roots(0, 0, 0)
    no_solution = stratified_quadratic_roots(0, 0, 5)

    assert identity.status is QuadraticRootStatus.CONSTANT_IDENTITY
    assert identity.value.coordinates == {}
    assert identity.value.discriminant is None
    assert identity.validity.selectable is False

    assert no_solution.status is QuadraticRootStatus.CONSTANT_NO_SOLUTION
    assert no_solution.value.coordinates == {}
    assert no_solution.value.discriminant is None
    assert no_solution.validity.selectable is False


def test_very_small_nonzero_a_remains_quadratic() -> None:
    result = stratified_quadratic_roots(1e-300, 1.0, 1.0)

    assert result.status is QuadraticRootStatus.TWO_REAL_ROOTS


def test_very_small_nonzero_discriminant_is_not_repeated() -> None:
    result = stratified_quadratic_roots(1.0, 2.000000000000001, 1.0)

    assert result.status is QuadraticRootStatus.TWO_REAL_ROOTS
    assert result.value.discriminant > 0


def test_root_state_is_structured_not_bare_tuple() -> None:
    result = stratified_quadratic_roots(1, -3, 2)

    assert not isinstance(result.value, tuple)
    assert hasattr(result.value, "coordinates")


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_nonfinite_inputs_fail_explicitly(bad: float) -> None:
    with pytest.raises(ProtocolViolationError):
        stratified_quadratic_roots(bad, 1, 1)
