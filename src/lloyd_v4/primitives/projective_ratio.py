from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol, validate_protocol
from lloyd_v4.core.result import TypedRefusal, TypedResult
from lloyd_v4.core.status import ConditioningStatus, ProjectiveRatioStatus, ProtocolStatus
from lloyd_v4.core.transitions import StatusTransitionRule
from lloyd_v4.core.validity import Validity


PROJECTIVE_RATIO_SPACE = "ProjectiveRatio"
SCALAR_SPACE = "Scalar"

PROJECTIVE_RATIO_PROTOCOL = ProducerProtocol(
    name="projective_ratio",
    emitted_statuses=frozenset(
        {
            ProjectiveRatioStatus.FINITE_RATIO,
            ProjectiveRatioStatus.SIGNED_ZERO,
            ProjectiveRatioStatus.INFINITE_DIRECTION,
            ProjectiveRatioStatus.INDETERMINATE,
        }
    ),
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
)

PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL = ConsumerProtocol(
    name="projective_ratio_scalarization",
    accepted_statuses=frozenset(
        {
            ProjectiveRatioStatus.FINITE_RATIO,
            ProjectiveRatioStatus.SIGNED_ZERO,
        }
    ),
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=True,
)


@dataclass(frozen=True, slots=True)
class ProjectiveRatioValue:
    numerator: Any
    denominator: Any

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe

        return {
            "numerator": to_json_safe(self.numerator),
            "denominator": to_json_safe(self.denominator),
        }


ProjectiveRatioResult = TypedResult[ProjectiveRatioValue, ProjectiveRatioStatus]

PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE = StatusTransitionRule(
    rule_id="projective_ratio.scalarization",
    input_status_family=ProjectiveRatioStatus,
    output_status_family=None,
    input_protocol_id=PROJECTIVE_RATIO_PROTOCOL.name,
    output_protocol_id=PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL.name,
    accepted_input_statuses=frozenset(
        {ProjectiveRatioStatus.FINITE_RATIO, ProjectiveRatioStatus.SIGNED_ZERO}
    ),
    refused_input_statuses=frozenset(
        {ProjectiveRatioStatus.INFINITE_DIRECTION, ProjectiveRatioStatus.INDETERMINATE}
    ),
    mapped_statuses={},
    description="ProjectiveRatio scalarization accepts finite and signed-zero strata and refuses non-scalar projective strata.",
    emitted_input_statuses=PROJECTIVE_RATIO_PROTOCOL.emitted_statuses,
)


def projective_ratio(
    numerator: Any,
    denominator: Any,
    *,
    precision: str = "raw_python",
    backend: str = "python",
    device: str = "cpu",
    measurement_resolution: Any | None = None,
) -> TypedResult:
    raw_numerator, numerator_parent = _unwrap_input(numerator)
    raw_denominator, denominator_parent = _unwrap_input(denominator)
    status = _classify(raw_numerator, raw_denominator)
    validity = _validity_for_status(status)
    parents = tuple(
        trace_id
        for trace_id in (numerator_parent, denominator_parent)
        if trace_id is not None
    )

    return TypedResult(
        value=ProjectiveRatioValue(raw_numerator, raw_denominator),
        space=PROJECTIVE_RATIO_SPACE,
        status=status,
        validity=validity,
        conditioning=Conditioning(status=ConditioningStatus.WELL_CONDITIONED),
        provenance=Provenance(
            operation_id="projective_ratio",
            expression_path="canonical_projective_ratio",
            precision=precision,
            backend=backend,
            device=device,
            measurement_resolution=measurement_resolution,
            inputs=(raw_numerator, raw_denominator),
            parents=parents,
        ),
        protocol=ProtocolStatus.OK,
    )


def scalarize_projective_ratio(result: TypedResult) -> TypedResult:
    check = validate_protocol(result, PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL)
    scalar_provenance = Provenance(
        operation_id="projective_ratio.scalarize",
        expression_path="projective_ratio_scalarization",
        precision=result.provenance.precision,
        backend=result.provenance.backend,
        device=result.provenance.device,
        measurement_resolution=result.provenance.measurement_resolution,
        parents=(result.provenance.trace_id,),
    )

    if not check.ok:
        refusal = TypedRefusal(
            reason=f"scalarization refused for {result.status.value}: {check.reason}",
            status=ProtocolStatus.SCALARIZATION_REFUSED,
            details={"projective_status": result.status.value, "protocol_reason": check.reason},
        )
        return TypedResult(
            value=None,
            space=SCALAR_SPACE,
            status=result.status,
            validity=Validity(defined=False, finite=False, selectable=False),
            conditioning=result.conditioning,
            provenance=scalar_provenance,
            protocol=ProtocolStatus.SCALARIZATION_REFUSED,
            refusal=refusal,
        )

    value = _require_projective_value(result).numerator / _require_projective_value(result).denominator
    return TypedResult(
        value=value,
        space=SCALAR_SPACE,
        status=result.status,
        validity=Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True),
        conditioning=result.conditioning,
        provenance=scalar_provenance,
        protocol=ProtocolStatus.OK,
    )


def _unwrap_input(value: Any) -> tuple[Any, str | None]:
    if isinstance(value, TypedResult):
        return value.value, value.provenance.trace_id
    return value, None


def _classify(numerator: Any, denominator: Any) -> ProjectiveRatioStatus:
    numerator_is_zero = numerator == 0
    denominator_is_zero = denominator == 0

    if denominator_is_zero and numerator_is_zero:
        return ProjectiveRatioStatus.INDETERMINATE
    if denominator_is_zero:
        return ProjectiveRatioStatus.INFINITE_DIRECTION
    if numerator_is_zero:
        return ProjectiveRatioStatus.SIGNED_ZERO
    return ProjectiveRatioStatus.FINITE_RATIO


def _validity_for_status(status: ProjectiveRatioStatus) -> Validity:
    if status in {ProjectiveRatioStatus.FINITE_RATIO, ProjectiveRatioStatus.SIGNED_ZERO}:
        return Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True)
    if status is ProjectiveRatioStatus.INFINITE_DIRECTION:
        return Validity(defined=True, finite=False, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _require_projective_value(result: TypedResult) -> ProjectiveRatioValue:
    if not isinstance(result.value, ProjectiveRatioValue):
        raise TypeError("expected ProjectiveRatioValue")
    return result.value
