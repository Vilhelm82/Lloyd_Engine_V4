from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.protocols import ConsumerProtocol, validate_protocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedRefusal, TypedResult
from lloyd_v4.core.status import (
    ConditioningStatus,
    ProtocolStatus,
    ProjectiveRatioStatus,
    QuadraticRootStatus,
    ValidityStatus,
)
from lloyd_v4.core.validity import Validity


def test_typed_result_can_hold_typed_refusal() -> None:
    provenance = Provenance(
        operation_id="task000.refusal",
        expression_path="smoke",
        precision="float64",
        backend="python",
        device="cpu",
        measurement_resolution=None,
    )
    refusal = TypedRefusal(
        reason="No honest scalar exists for this status.",
        status=ProtocolStatus.SCALARIZATION_REFUSED,
    )

    result = TypedResult(
        value=None,
        space="Scalar",
        status=ValidityStatus.INVALID,
        validity=Validity(defined=False, finite=False),
        conditioning=Conditioning(status=ConditioningStatus.UNKNOWN),
        provenance=provenance,
        protocol=ProtocolStatus.SCALARIZATION_REFUSED,
        refusal=refusal,
    )

    assert result.refusal == refusal
    assert result.value is None
    assert result.protocol is ProtocolStatus.SCALARIZATION_REFUSED


def test_provenance_can_be_created_and_serialized() -> None:
    provenance = Provenance(
        operation_id="task000.provenance",
        expression_path="n/d",
        precision="float64",
        backend="python",
        device="cpu",
        measurement_resolution={"absolute": 1e-12},
        parents=("parent-trace",),
    )

    payload = provenance.to_json_safe()

    assert payload["trace_id"] == provenance.trace_id
    assert payload["parents"] == ["parent-trace"]
    assert payload["measurement_resolution"] == {"absolute": 1e-12}


def test_protocol_validation_rejects_unhandled_status() -> None:
    result = TypedResult(
        value=None,
        space="ProjectiveRatio",
        status=ProjectiveRatioStatus.INDETERMINATE,
        validity=Validity(defined=False, finite=False),
        conditioning=Conditioning(status=ConditioningStatus.UNKNOWN),
        provenance=Provenance(operation_id="ratio", expression_path="0/0"),
        protocol=ProtocolStatus.OK,
    )
    consumer = ConsumerProtocol(
        name="finite-ratio-consumer",
        accepted_statuses=frozenset({ProjectiveRatioStatus.FINITE_RATIO}),
        scalarization_allowed=True,
    )

    check = validate_protocol(result, consumer)

    assert check.status is ProtocolStatus.VIOLATION
    assert "unhandled status" in check.reason


def test_status_enums_include_upcoming_primitive_statuses() -> None:
    assert ProjectiveRatioStatus.FINITE_RATIO.value == "finite_ratio"
    assert ProjectiveRatioStatus.SIGNED_ZERO.value == "signed_zero"
    assert ProjectiveRatioStatus.INFINITE_DIRECTION.value == "infinite_direction"
    assert ProjectiveRatioStatus.INDETERMINATE.value == "indeterminate"

    assert QuadraticRootStatus.TWO_REAL_ROOTS.value == "two_real_roots"
    assert QuadraticRootStatus.REPEATED_ROOT.value == "repeated_root"
    assert QuadraticRootStatus.NO_REAL_ROOT.value == "no_real_root"
    assert QuadraticRootStatus.LINEAR_ROOT.value == "linear_root"
    assert QuadraticRootStatus.CONSTANT_IDENTITY.value == "constant_identity"
    assert QuadraticRootStatus.CONSTANT_NO_SOLUTION.value == "constant_no_solution"
