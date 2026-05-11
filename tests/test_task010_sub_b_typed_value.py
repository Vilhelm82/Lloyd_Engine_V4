import json
from dataclasses import dataclass
from pathlib import Path

from lloyd_v4.core.conditioning import ConditioningStatus
from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.status import ValueStatus
from lloyd_v4.primitives import (
    NON_NULL_TYPED_VALUE_PROTOCOL,
    TYPED_VALUE_PROTOCOL,
    TypedValueValue,
    typed_collection,
    typed_value,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "Build_Docs" / "Architecture" / "layer_manifest.json"


@dataclass(frozen=True, slots=True)
class ExamplePayload:
    name: str
    amount: int


def test_presence_based_status_emission() -> None:
    observed = typed_value(42)
    absent = typed_value(None)
    text = typed_value("hello")

    assert observed.status is ValueStatus.VALUE_OBSERVED
    assert observed.value == TypedValueValue(value=42, is_present=True)
    assert observed.space == "TypedValue"
    assert observed.provenance.operation_id == "typed_value"
    assert observed.provenance.parents == ()

    assert absent.status is ValueStatus.VALUE_ABSENT
    assert absent.value == TypedValueValue(value=None, is_present=False)
    assert absent.provenance.parents == ()

    assert text.status is ValueStatus.VALUE_OBSERVED
    assert text.value.value == "hello"
    assert text.value.is_present is True


def test_falsy_non_none_values_are_observed() -> None:
    for raw in (0, False, "", [], {}):
        result = typed_value(raw)
        assert result.status is ValueStatus.VALUE_OBSERVED
        assert result.value.value == raw
        assert result.value.is_present is True


def test_heterogeneous_content_is_stored_without_validation() -> None:
    payload = ExamplePayload(name="sample", amount=3)
    nested_result = typed_collection([1, 2, 3])

    assert typed_value(payload).value.value is payload
    assert typed_value(nested_result).value.value is nested_result
    assert typed_value(0.0).value.value == 0.0
    assert typed_value(complex(1, 2)).value.value == complex(1, 2)


def test_validity_and_conditioning_are_presence_only() -> None:
    observed = typed_value("present")
    absent = typed_value(None)

    assert observed.validity.defined is True
    assert observed.validity.finite is True
    assert observed.validity.observable is True
    assert observed.validity.advanceable is False
    assert observed.validity.selectable is True

    assert absent.validity.defined is True
    assert absent.validity.finite is True
    assert absent.validity.observable is True
    assert absent.validity.advanceable is False
    assert absent.validity.selectable is False

    assert observed.conditioning.status is ConditioningStatus.WELL_CONDITIONED
    assert absent.conditioning.status is ConditioningStatus.WELL_CONDITIONED


def test_provenance_is_primitive_and_deterministic_for_same_hashable_value() -> None:
    first = typed_value("stable")
    second = typed_value("stable")

    assert first.provenance.operation_id == "typed_value"
    assert first.provenance.expression_path == "typed_value_construction"
    assert first.provenance.parents == ()
    assert first.provenance.trace_id == second.provenance.trace_id


def test_protocol_validation_accepts_only_non_null_values() -> None:
    accepted = validate_protocol(typed_value(42), NON_NULL_TYPED_VALUE_PROTOCOL)
    refused = validate_protocol(typed_value(None), NON_NULL_TYPED_VALUE_PROTOCOL)

    assert TYPED_VALUE_PROTOCOL.status_family is ValueStatus
    assert NON_NULL_TYPED_VALUE_PROTOCOL.status_family is ValueStatus
    assert accepted.ok is True
    assert refused.ok is False
    assert "value_absent" in refused.reason or "VALUE_ABSENT" in refused.reason


def test_manifest_registers_typed_value_and_exports_match_source() -> None:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    primitives = next(layer for layer in payload["layers"] if layer["name"] == "primitives")
    provides = primitives["provides"]

    assert "ValueStatus" in provides["status_families"]
    assert "TypedValueValue" in provides["value_types"]
    assert "TYPED_VALUE_PROTOCOL" in provides["protocol_types"]
    assert "NON_NULL_TYPED_VALUE_PROTOCOL" in provides["protocol_types"]
    assert "typed_value" in provides["operations"]
    assert "typed_value" in provides["calibrated_primitive_operations"]

    import lloyd_v4.primitives as primitives_module

    assert set(provides["all_exports"]) == set(primitives_module.__all__)
