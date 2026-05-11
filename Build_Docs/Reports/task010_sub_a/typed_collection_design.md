# typed_collection Design

## Contract

`typed_collection(items)` accepts `Iterable[Any]`, materializes it once as a tuple, preserves iteration order, and returns `TypedCollectionResult`.

The result value is `TypedCollectionValue`:

- `items`: the materialized tuple
- `count`: the tuple length

Status emission is cardinality-only:

- `COLLECTION_EMPTY` when `count == 0`
- `COLLECTION_SINGLETON` when `count == 1`
- `COLLECTION_OBSERVED` when `count > 1`

Validity is factual and simple:

- All statuses are `defined=True`, `finite=True`, `observable=True`, `advanceable=False`.
- `COLLECTION_EMPTY` has `selectable=False`.
- Singleton and observed collections have `selectable=True`.

Conditioning is always `WELL_CONDITIONED`. Empty collection is an observed cardinality, not an indeterminate state.

Provenance is primitive:

- `operation_id="typed_collection"`
- `expression_path="typed_collection_construction"`
- `parents=()`

## Layer Placement

The primitive belongs in `primitives` because typed collections are layer-foundational. They introduce typed lineage from raw sequences at the substrate input boundary without encoding metrology, branch, history, solver, or refinery semantics.

## Deliberate Non-Behavior

`typed_collection` does not validate item types, inspect item contents, assign layer-specific meanings, perform scalarization, or create cross-family transitions. It only records that an iterable was observed as an ordered collection.

## Consumer-Refactor Pattern

Later wrapper composites should consume `typed_collection` and re-wrap with layer-specific value types. Examples include observation sample sets, slope-flow sample sets, history event sets, and solver step-model sets.

The expected pattern is:

1. Call `typed_collection(raw_items)`.
2. Validate cardinality with `NON_EMPTY_TYPED_COLLECTION_PROTOCOL` if the downstream operation requires non-empty input.
3. Construct the layer-specific typed value.
4. Use the `typed_collection` trace ID as a provenance parent.

This keeps raw sequence boundaries typed while leaving domain-specific validation in the consuming layer.
