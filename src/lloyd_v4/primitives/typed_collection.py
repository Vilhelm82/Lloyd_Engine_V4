from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import CollectionStatus, ConditioningStatus, ProtocolStatus
from lloyd_v4.core.validity import Validity


@dataclass(frozen=True, slots=True)
class TypedCollectionValue:
    items: tuple[Any, ...]
    count: int

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "items": to_json_safe(self.items),
            "count": self.count,
        }


TYPED_COLLECTION_PROTOCOL = ProducerProtocol(
    name="typed_collection",
    emitted_statuses=frozenset(
        {
            CollectionStatus.COLLECTION_EMPTY,
            CollectionStatus.COLLECTION_SINGLETON,
            CollectionStatus.COLLECTION_OBSERVED,
        }
    ),
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=CollectionStatus,
)

NON_EMPTY_TYPED_COLLECTION_PROTOCOL = ConsumerProtocol(
    name="non_empty_typed_collection",
    accepted_statuses=frozenset(
        {
            CollectionStatus.COLLECTION_SINGLETON,
            CollectionStatus.COLLECTION_OBSERVED,
        }
    ),
    required_validity_fields=frozenset({"defined", "selectable"}),
    scalarization_allowed=False,
    status_family=CollectionStatus,
    refused_statuses=frozenset({CollectionStatus.COLLECTION_EMPTY}),
)

TypedCollectionResult = TypedResult[TypedCollectionValue, CollectionStatus]


def typed_collection(items: Iterable[Any]) -> TypedCollectionResult:
    items_tuple = tuple(items)
    count = len(items_tuple)
    if count == 0:
        status = CollectionStatus.COLLECTION_EMPTY
    elif count == 1:
        status = CollectionStatus.COLLECTION_SINGLETON
    else:
        status = CollectionStatus.COLLECTION_OBSERVED

    value = TypedCollectionValue(items=items_tuple, count=count)
    return TypedResult(
        value=value,
        space="TypedCollection",
        status=status,
        validity=_validity_for_status(status),
        conditioning=Conditioning(status=ConditioningStatus.WELL_CONDITIONED),
        provenance=Provenance(
            operation_id="typed_collection",
            expression_path="typed_collection_construction",
            inputs=(items_tuple,),
            parents=(),
        ),
        protocol=ProtocolStatus.OK,
    )


def _validity_for_status(status: CollectionStatus) -> Validity:
    if status is CollectionStatus.COLLECTION_EMPTY:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
