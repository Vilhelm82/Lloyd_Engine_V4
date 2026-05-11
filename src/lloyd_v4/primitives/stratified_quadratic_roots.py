from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol, validate_protocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedRefusal, TypedResult
from lloyd_v4.core.status import ConditioningStatus, ProtocolStatus, QuadraticRootStatus
from lloyd_v4.core.transitions import StatusTransitionRule
from lloyd_v4.core.validity import Validity
from lloyd_v4.primitives.projective_ratio import (
    ProjectiveRatioValue,
    projective_ratio,
    scalarize_projective_ratio,
)


QUADRATIC_ROOT_SPACE = "StratifiedQuadraticRoots"
SCALAR_SPACE = "Scalar"

STRATIFIED_QUADRATIC_ROOTS_PROTOCOL = ProducerProtocol(
    name="stratified_quadratic_roots",
    emitted_statuses=frozenset(
        {
            QuadraticRootStatus.TWO_REAL_ROOTS,
            QuadraticRootStatus.REPEATED_ROOT,
            QuadraticRootStatus.NO_REAL_ROOT,
            QuadraticRootStatus.LINEAR_ROOT,
            QuadraticRootStatus.CONSTANT_IDENTITY,
            QuadraticRootStatus.CONSTANT_NO_SOLUTION,
        }
    ),
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
)

QUADRATIC_ROOT_SELECTION_PROTOCOL = ConsumerProtocol(
    name="quadratic_root_selection",
    accepted_statuses=frozenset(
        {
            QuadraticRootStatus.TWO_REAL_ROOTS,
            QuadraticRootStatus.REPEATED_ROOT,
            QuadraticRootStatus.LINEAR_ROOT,
        }
    ),
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=True,
)

BRANCHES_BY_STATUS = {
    QuadraticRootStatus.TWO_REAL_ROOTS: frozenset({"minus", "plus"}),
    QuadraticRootStatus.REPEATED_ROOT: frozenset({"repeated"}),
    QuadraticRootStatus.LINEAR_ROOT: frozenset({"linear"}),
}


@dataclass(frozen=True, slots=True)
class QuadraticCoefficients:
    a: Any
    b: Any
    c: Any

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe

        return {"a": to_json_safe(self.a), "b": to_json_safe(self.b), "c": to_json_safe(self.c)}


@dataclass(frozen=True, slots=True)
class QuadraticRootCoordinate:
    branch: str
    coordinate: ProjectiveRatioValue

    def to_json_safe(self) -> dict[str, Any]:
        return {"branch": self.branch, "coordinate": self.coordinate.to_json_safe()}


@dataclass(frozen=True, slots=True)
class StratifiedQuadraticRootValue:
    coefficients: QuadraticCoefficients
    discriminant: Any | None
    coordinates: dict[str, QuadraticRootCoordinate]

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe

        return {
            "coefficients": self.coefficients.to_json_safe(),
            "discriminant": to_json_safe(self.discriminant),
            "coordinates": {
                branch: coordinate.to_json_safe()
                for branch, coordinate in self.coordinates.items()
            },
        }


QuadraticRootStateResult = TypedResult[StratifiedQuadraticRootValue, QuadraticRootStatus]

QUADRATIC_ROOT_SELECTION_TRANSITION_RULE = StatusTransitionRule(
    rule_id="quadratic_roots.selection",
    input_status_family=QuadraticRootStatus,
    output_status_family=None,
    input_protocol_id=STRATIFIED_QUADRATIC_ROOTS_PROTOCOL.name,
    output_protocol_id=QUADRATIC_ROOT_SELECTION_PROTOCOL.name,
    accepted_input_statuses=frozenset(
        {
            QuadraticRootStatus.TWO_REAL_ROOTS,
            QuadraticRootStatus.REPEATED_ROOT,
            QuadraticRootStatus.LINEAR_ROOT,
        }
    ),
    refused_input_statuses=frozenset(
        {
            QuadraticRootStatus.NO_REAL_ROOT,
            QuadraticRootStatus.CONSTANT_IDENTITY,
            QuadraticRootStatus.CONSTANT_NO_SOLUTION,
        }
    ),
    mapped_statuses={},
    context_keys=("branch",),
    description="Quadratic root selection accepts selectable root-state statuses; branch compatibility is contextual.",
    emitted_input_statuses=STRATIFIED_QUADRATIC_ROOTS_PROTOCOL.emitted_statuses,
)


def stratified_quadratic_roots(
    a: int | float,
    b: int | float,
    c: int | float,
    *,
    precision: str = "raw_python",
    backend: str = "python",
    device: str = "cpu",
    measurement_resolution: Any | None = None,
) -> TypedResult:
    _require_real_finite(a, "a")
    _require_real_finite(b, "b")
    _require_real_finite(c, "c")

    status, discriminant = _classify(a, b, c)
    coordinates = _coordinates_for_status(status, a, b, c, discriminant)

    return TypedResult(
        value=StratifiedQuadraticRootValue(
            coefficients=QuadraticCoefficients(a=a, b=b, c=c),
            discriminant=discriminant,
            coordinates=coordinates,
        ),
        space=QUADRATIC_ROOT_SPACE,
        status=status,
        validity=_validity_for_status(status),
        conditioning=_conditioning_for_status(status),
        provenance=Provenance(
            operation_id="stratified_quadratic_roots",
            expression_path="direct_quadratic_formula",
            precision=precision,
            backend=backend,
            device=device,
            measurement_resolution=measurement_resolution,
            inputs=(a, b, c),
        ),
        protocol=ProtocolStatus.OK,
    )


def select_quadratic_root(result: TypedResult, branch: str) -> TypedResult:
    if not isinstance(result, TypedResult):
        raise ProtocolViolationError("quadratic root selection requires a TypedResult")
    if not isinstance(result.value, StratifiedQuadraticRootValue):
        raise ProtocolViolationError("quadratic root selection requires a quadratic root-state result")
    check = validate_protocol(result, QUADRATIC_ROOT_SELECTION_PROTOCOL)
    selected_provenance = _selection_provenance(result)

    if not check.ok:
        return _selection_refusal(result, branch, check.reason, selected_provenance)

    value = _require_quadratic_value(result)
    expected = BRANCHES_BY_STATUS.get(result.status, frozenset())
    if branch not in expected or branch not in value.coordinates:
        reason = f"branch {branch!r} is not compatible with {result.status.value}"
        return _selection_refusal(result, branch, reason, selected_provenance)

    coordinate = value.coordinates[branch].coordinate
    ratio = projective_ratio(
        coordinate.numerator,
        coordinate.denominator,
        precision=result.provenance.precision,
        backend=result.provenance.backend,
        device=result.provenance.device,
        measurement_resolution=result.provenance.measurement_resolution,
    )
    scalar = scalarize_projective_ratio(ratio)
    if scalar.refusal is not None:
        return _selection_refusal(result, branch, scalar.refusal.reason, selected_provenance)

    return TypedResult(
        value=scalar.value,
        space=SCALAR_SPACE,
        status=result.status,
        validity=Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True),
        conditioning=result.conditioning,
        provenance=Provenance(
            operation_id="stratified_quadratic_roots.select",
            expression_path=f"select_{branch}_root",
            precision=result.provenance.precision,
            backend=result.provenance.backend,
            device=result.provenance.device,
            measurement_resolution=result.provenance.measurement_resolution,
            parents=(result.provenance.trace_id, ratio.provenance.trace_id, scalar.provenance.trace_id),
        ),
        protocol=ProtocolStatus.OK,
    )


def _require_real_finite(value: Any, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ProtocolViolationError(f"{name} must be a finite real scalar")
    if not math.isfinite(value):
        raise ProtocolViolationError(f"{name} must be a finite real scalar")


def _classify(a: int | float, b: int | float, c: int | float) -> tuple[QuadraticRootStatus, int | float | None]:
    if a != 0:
        discriminant = b * b - 4 * a * c
        if discriminant > 0:
            return QuadraticRootStatus.TWO_REAL_ROOTS, discriminant
        if discriminant == 0:
            return QuadraticRootStatus.REPEATED_ROOT, discriminant
        return QuadraticRootStatus.NO_REAL_ROOT, discriminant
    if b != 0:
        return QuadraticRootStatus.LINEAR_ROOT, None
    if c == 0:
        return QuadraticRootStatus.CONSTANT_IDENTITY, None
    return QuadraticRootStatus.CONSTANT_NO_SOLUTION, None


def _coordinates_for_status(
    status: QuadraticRootStatus,
    a: int | float,
    b: int | float,
    c: int | float,
    discriminant: int | float | None,
) -> dict[str, QuadraticRootCoordinate]:
    if status is QuadraticRootStatus.TWO_REAL_ROOTS:
        root_span = math.sqrt(discriminant)
        return {
            "minus": QuadraticRootCoordinate(
                branch="minus",
                coordinate=ProjectiveRatioValue(numerator=-b - root_span, denominator=2 * a),
            ),
            "plus": QuadraticRootCoordinate(
                branch="plus",
                coordinate=ProjectiveRatioValue(numerator=-b + root_span, denominator=2 * a),
            ),
        }
    if status is QuadraticRootStatus.REPEATED_ROOT:
        return {
            "repeated": QuadraticRootCoordinate(
                branch="repeated",
                coordinate=ProjectiveRatioValue(numerator=-b, denominator=2 * a),
            )
        }
    if status is QuadraticRootStatus.LINEAR_ROOT:
        return {
            "linear": QuadraticRootCoordinate(
                branch="linear",
                coordinate=ProjectiveRatioValue(numerator=-c, denominator=b),
            )
        }
    return {}


def _validity_for_status(status: QuadraticRootStatus) -> Validity:
    if status in {
        QuadraticRootStatus.TWO_REAL_ROOTS,
        QuadraticRootStatus.REPEATED_ROOT,
        QuadraticRootStatus.LINEAR_ROOT,
    }:
        return Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True)
    return Validity(defined=True, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning_for_status(status: QuadraticRootStatus) -> Conditioning:
    if status is QuadraticRootStatus.REPEATED_ROOT:
        return Conditioning(status=ConditioningStatus.WARNING, notes=("repeated_root",))
    return Conditioning(status=ConditioningStatus.WELL_CONDITIONED)


def _selection_provenance(result: TypedResult) -> Provenance:
    return Provenance(
        operation_id="stratified_quadratic_roots.select",
        expression_path="quadratic_root_selection_refusal",
        precision=result.provenance.precision,
        backend=result.provenance.backend,
        device=result.provenance.device,
        measurement_resolution=result.provenance.measurement_resolution,
        parents=(result.provenance.trace_id,),
    )


def _selection_refusal(
    result: TypedResult,
    branch: str,
    reason: str,
    provenance: Provenance,
) -> TypedResult:
    refusal = TypedRefusal(
        reason=f"root selection refused for branch {branch!r}: {reason}",
        status=ProtocolStatus.SCALARIZATION_REFUSED,
        details={"quadratic_status": result.status.value, "branch": branch, "protocol_reason": reason},
    )
    return TypedResult(
        value=None,
        space=SCALAR_SPACE,
        status=result.status,
        validity=Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True),
        conditioning=result.conditioning,
        provenance=provenance,
        protocol=ProtocolStatus.SCALARIZATION_REFUSED,
        refusal=refusal,
    )


def _require_quadratic_value(result: TypedResult) -> StratifiedQuadraticRootValue:
    if not isinstance(result.value, StratifiedQuadraticRootValue):
        raise TypeError("expected StratifiedQuadraticRootValue")
    return result.value
