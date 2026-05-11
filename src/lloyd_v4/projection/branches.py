from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.status import ProtocolStatus, ValueStatus
from lloyd_v4.primitives import typed_value


class BranchSelection(StrEnum):
    MINUS = "minus"
    PLUS = "plus"
    REPEATED = "repeated"
    LINEAR = "linear"


@dataclass(frozen=True, slots=True)
class BranchSelectionValue:
    branch: BranchSelection

    def to_json_safe(self) -> dict[str, str]:
        return {"branch": self.branch.value}


BRANCH_SELECTION_PROTOCOL = ProducerProtocol(
    name="branch_selection",
    emitted_statuses=frozenset({ValueStatus.VALUE_OBSERVED}),
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=ValueStatus,
)

BRANCH_SELECTION_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="branch_selection_consumer",
    accepted_statuses=frozenset({ValueStatus.VALUE_OBSERVED}),
    required_validity_fields=frozenset({"defined", "selectable"}),
    scalarization_allowed=False,
    status_family=ValueStatus,
    refused_statuses=frozenset({ValueStatus.VALUE_ABSENT}),
)

BranchSelectionResult = TypedResult[BranchSelectionValue, ValueStatus]


def branch_selection(branch: BranchSelection) -> BranchSelectionResult:
    if not isinstance(branch, BranchSelection):
        raise ProtocolViolationError("branch must be a BranchSelection enum member")
    inner = typed_value(branch)
    value = BranchSelectionValue(branch=branch)
    return TypedResult(
        value=value,
        space="BranchSelection",
        status=inner.status,
        validity=inner.validity,
        conditioning=inner.conditioning,
        provenance=Provenance(
            operation_id="branch_selection",
            expression_path="branch_selection_construction",
            parents=(inner.provenance.trace_id,),
        ),
        protocol=ProtocolStatus.OK,
    )
