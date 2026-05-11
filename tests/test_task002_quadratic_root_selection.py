from lloyd_v4.core.status import ProtocolStatus, QuadraticRootStatus
from lloyd_v4.primitives.stratified_quadratic_roots import (
    select_quadratic_root,
    stratified_quadratic_roots,
)


def test_select_two_real_roots_minus_and_plus() -> None:
    result = stratified_quadratic_roots(1, -3, 2)

    minus = select_quadratic_root(result, "minus")
    plus = select_quadratic_root(result, "plus")

    assert minus.value == 1.0
    assert minus.status is QuadraticRootStatus.TWO_REAL_ROOTS
    assert minus.protocol is ProtocolStatus.OK
    assert result.provenance.trace_id in minus.provenance.parents

    assert plus.value == 2.0
    assert plus.status is QuadraticRootStatus.TWO_REAL_ROOTS
    assert plus.protocol is ProtocolStatus.OK
    assert result.provenance.trace_id in plus.provenance.parents


def test_select_repeated_and_linear_roots() -> None:
    repeated = stratified_quadratic_roots(1, 2, 1)
    linear = stratified_quadratic_roots(0, 2, -4)

    repeated_scalar = select_quadratic_root(repeated, "repeated")
    linear_scalar = select_quadratic_root(linear, "linear")

    assert repeated_scalar.value == -1
    assert repeated_scalar.status is QuadraticRootStatus.REPEATED_ROOT
    assert repeated_scalar.protocol is ProtocolStatus.OK

    assert linear_scalar.value == 2
    assert linear_scalar.status is QuadraticRootStatus.LINEAR_ROOT
    assert linear_scalar.protocol is ProtocolStatus.OK


def test_refuses_statuses_without_selectable_scalar_roots() -> None:
    for result in [
        stratified_quadratic_roots(1, 0, 1),
        stratified_quadratic_roots(0, 0, 0),
        stratified_quadratic_roots(0, 0, 5),
    ]:
        selected = select_quadratic_root(result, "minus")

        assert selected.value is None
        assert selected.status is result.status
        assert selected.protocol is ProtocolStatus.SCALARIZATION_REFUSED
        assert selected.refusal is not None


def test_refuses_incompatible_branch_labels() -> None:
    cases = [
        (stratified_quadratic_roots(1, -3, 2), "linear"),
        (stratified_quadratic_roots(1, 2, 1), "plus"),
        (stratified_quadratic_roots(0, 2, -4), "minus"),
    ]

    for result, branch in cases:
        selected = select_quadratic_root(result, branch)

        assert selected.value is None
        assert selected.protocol is ProtocolStatus.SCALARIZATION_REFUSED
        assert selected.refusal is not None
        assert branch in selected.refusal.reason
