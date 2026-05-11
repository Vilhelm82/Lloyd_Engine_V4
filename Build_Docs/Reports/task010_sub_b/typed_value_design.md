# typed_value Design

## Contract

`typed_value(value)` accepts `Any` and stores the value as-is in `TypedValueValue`.

The result value is:

- `value`: the original object.
- `is_present`: `True` when `value is not None`, otherwise `False`.

Status emission is presence-only:

- `VALUE_ABSENT` when `value is None`.
- `VALUE_OBSERVED` when `value is not None`.

Falsy non-None values such as `0`, `False`, `""`, `[]`, and `{}` are observed values, not absence.

Validity is factual:

- Both statuses are `defined=True`, `finite=True`, `observable=True`, `advanceable=False`.
- `VALUE_ABSENT` has `selectable=False`.
- `VALUE_OBSERVED` has `selectable=True`.

Conditioning is always `WELL_CONDITIONED`.

Provenance is primitive:

- `operation_id="typed_value"`
- `expression_path="typed_value_construction"`
- `parents=()`

## Layer Placement

`typed_value` belongs beside `typed_collection` in `primitives` because single-value wrapping is layer-foundational. It covers raw substrate input boundaries where a single dataclass, scalar, policy, or object must become a typed observation before a higher layer interprets it.

## Deliberate Non-Behavior

`typed_value` does not validate type, inspect content, assign layer-specific meaning, reject falsey values, or create cross-family transitions. It only records presence or absence.

## Relationship To typed_collection

`typed_collection` covers raw sequence inputs. `typed_value` covers raw single-value inputs. Together they provide the generic substrate boundary wrappers needed by the consumer-refactor tasks 010-Sub-C through 010-Sub-F.

The consumer pattern mirrors `Build_Docs/Reports/task010_sub_a/typed_collection_design.md`:

1. Call `typed_value(raw)`.
2. Validate with `NON_NULL_TYPED_VALUE_PROTOCOL` when the downstream composite requires a present value.
3. Construct the layer-specific typed value.
4. Use the `typed_value` trace ID as a provenance parent.

## is_present Rationale

`is_present` is stored explicitly to mirror `TypedCollectionValue.count`. Downstream consumers can read presence directly without repeating the sentinel check against `None`.
