import json
from pathlib import Path

from lloyd_v4.core.conditioning import ConditioningStatus
from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.status import CollectionStatus
from lloyd_v4.primitives import (
    NON_EMPTY_TYPED_COLLECTION_PROTOCOL,
    TYPED_COLLECTION_PROTOCOL,
    TypedCollectionValue,
    typed_collection,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "Build_Docs" / "Architecture" / "layer_manifest.json"


def test_cardinality_based_status_emission() -> None:
    empty = typed_collection([])
    singleton = typed_collection([42])
    observed = typed_collection([1, 2, 3])

    assert empty.status is CollectionStatus.COLLECTION_EMPTY
    assert empty.value == TypedCollectionValue(items=(), count=0)
    assert empty.space == "TypedCollection"
    assert empty.provenance.operation_id == "typed_collection"
    assert empty.provenance.parents == ()

    assert singleton.status is CollectionStatus.COLLECTION_SINGLETON
    assert singleton.value.items == (42,)
    assert singleton.value.count == 1
    assert singleton.provenance.parents == ()

    assert observed.status is CollectionStatus.COLLECTION_OBSERVED
    assert observed.value.items == (1, 2, 3)
    assert observed.value.count == 3
    assert observed.provenance.parents == ()


def test_iterables_are_materialized_without_reordering_or_type_validation() -> None:
    assert typed_collection(iter([1, 2])).value.items == (1, 2)
    assert typed_collection((1, 2, 3)).value.items == (1, 2, 3)
    assert typed_collection(range(5)).value.items == (0, 1, 2, 3, 4)
    assert typed_collection([3, 1, 2]).value.items == (3, 1, 2)
    assert typed_collection([1, "two", 3.0, None]).value.items == (1, "two", 3.0, None)


def test_validity_and_conditioning_are_cardinality_only() -> None:
    empty = typed_collection([])
    singleton = typed_collection([1])
    observed = typed_collection([1, 2])

    assert empty.validity.defined is True
    assert empty.validity.finite is True
    assert empty.validity.observable is True
    assert empty.validity.advanceable is False
    assert empty.validity.selectable is False

    for result in (singleton, observed):
        assert result.validity.defined is True
        assert result.validity.finite is True
        assert result.validity.observable is True
        assert result.validity.advanceable is False
        assert result.validity.selectable is True

    for result in (empty, singleton, observed):
        assert result.conditioning.status is ConditioningStatus.WELL_CONDITIONED


def test_provenance_is_primitive_and_deterministic() -> None:
    first = typed_collection([1, 2, 3])
    second = typed_collection([1, 2, 3])

    assert first.provenance.operation_id == "typed_collection"
    assert first.provenance.expression_path == "typed_collection_construction"
    assert first.provenance.parents == ()
    assert first.provenance.trace_id == second.provenance.trace_id


def test_protocol_validation_accepts_only_non_empty_collections() -> None:
    accepted = validate_protocol(typed_collection([1, 2]), NON_EMPTY_TYPED_COLLECTION_PROTOCOL)
    refused = validate_protocol(typed_collection([]), NON_EMPTY_TYPED_COLLECTION_PROTOCOL)

    assert TYPED_COLLECTION_PROTOCOL.status_family is CollectionStatus
    assert NON_EMPTY_TYPED_COLLECTION_PROTOCOL.status_family is CollectionStatus
    assert accepted.ok is True
    assert refused.ok is False
    assert "collection_empty" in refused.reason or "COLLECTION_EMPTY" in refused.reason


def test_manifest_registers_typed_collection_and_exports_match_source() -> None:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    primitives = next(layer for layer in payload["layers"] if layer["name"] == "primitives")
    provides = primitives["provides"]

    assert "CollectionStatus" in provides["status_families"]
    assert "TypedCollectionValue" in provides["value_types"]
    assert "TYPED_COLLECTION_PROTOCOL" in provides["protocol_types"]
    assert "NON_EMPTY_TYPED_COLLECTION_PROTOCOL" in provides["protocol_types"]
    assert "typed_collection" in provides["operations"]
    assert "typed_collection" in provides["calibrated_primitive_operations"]

    import lloyd_v4.primitives as primitives_module

    assert set(provides["all_exports"]) == set(primitives_module.__all__)
