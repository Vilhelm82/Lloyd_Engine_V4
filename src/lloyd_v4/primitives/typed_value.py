from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import ConditioningStatus, ProtocolStatus, ValueStatus
from lloyd_v4.core.validity import Validity


@dataclass(frozen=True, slots=True)
class TypedValueValue:
    value: Any
    is_present: bool

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "value": to_json_safe(self.value),
            "is_present": self.is_present,
        }


TYPED_VALUE_PROTOCOL = ProducerProtocol(
    name="typed_value",
    emitted_statuses=frozenset(
        {
            ValueStatus.VALUE_ABSENT,
            ValueStatus.VALUE_OBSERVED,
        }
    ),
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=ValueStatus,
)

NON_NULL_TYPED_VALUE_PROTOCOL = ConsumerProtocol(
    name="non_null_typed_value",
    accepted_statuses=frozenset({ValueStatus.VALUE_OBSERVED}),
    required_validity_fields=frozenset({"defined", "selectable"}),
    scalarization_allowed=False,
    status_family=ValueStatus,
    refused_statuses=frozenset({ValueStatus.VALUE_ABSENT}),
)

TypedValueResult = TypedResult[TypedValueValue, ValueStatus]


def typed_value(value: Any) -> TypedValueResult:
    is_present = value is not None
    status = ValueStatus.VALUE_OBSERVED if is_present else ValueStatus.VALUE_ABSENT
    payload = TypedValueValue(value=value, is_present=is_present)
    return TypedResult(
        value=payload,
        space="TypedValue",
        status=status,
        validity=_validity_for_status(status),
        conditioning=Conditioning(status=ConditioningStatus.WELL_CONDITIONED),
        provenance=Provenance(
            operation_id="typed_value",
            expression_path="typed_value_construction",
            inputs=(value,),
            parents=(),
        ),
        protocol=ProtocolStatus.OK,
    )


def _validity_for_status(status: ValueStatus) -> Validity:
    if status is ValueStatus.VALUE_ABSENT:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
