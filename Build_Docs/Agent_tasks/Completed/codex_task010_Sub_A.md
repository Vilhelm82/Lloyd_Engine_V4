# Codex Task 010-Sub-A: typed_collection Primitive at primitives Layer

## Repository

Work in:

```text
/mnt/fast/Lloyd_Engine_V4
```

This is Lloyd Engine V4 clean-room work. V3 is reference evidence only. Do not import, call, bridge, compare against, adapt, or depend on V3 at runtime. Do not add legacy adapters, compatibility shims, downgrade modes, or cross-engine calls.

V1 files may be used only as static design evidence for what the old engine attempted. Do not import, copy, or depend on:

```text
lloyd_core.py
lloyd_core_nvar.py
lloyd_decomposition.py
```

Task 010-Sub-A is the first task in the substrate-extension sequence inserted between Task 010C and Task 010C′. It is a **substrate-modifying task** — unlike 010A/B/C which were audit-and-documentation only, this task adds new source code at the `primitives` layer.

## Current verified baseline

Tasks 000 through 009A, 010A, 010B, and 010C are complete.

010C surfaced that the substrate has nine operations across five layers that produce `TypedResult` instances without consuming any. Inspection of those nine revealed two structural categories:

- **Genuinely axiomatic** (4 operations): `projective_ratio`, `stratified_quadratic_roots`, `declare_bk_noise_floor`, `proxy_uncalibrated`. These take raw scalars or are operator declarations; no typed precursor is meaningfully possible.
- **Composite-with-edge-case** (5 operations): `compare_slope_flow_to_models`, `build_status_trace`, `evaluate_solver_step`, `run_typed_projection_solver`, `estimate_bk_noise_floor`. These take sequences or dataclasses as inputs that should themselves be typed observations. They appear as primitives because their input collections aren't typed; in normal operation they have non-empty parents from internal typed work, but edge cases (empty inputs, early refusal) cause empty parents.

The substrate-extension series corrects this by introducing typed-input wrapping primitives, then refactoring the five composite-with-edge-case operations to consume them. After the series completes, the calibrated primitive set shrinks from nine to six and every member is genuinely primitive.

010-Sub-A is the first task: add `typed_collection` as an axiomatic wrapping primitive at the `primitives` layer. This primitive is the keystone for all subsequent layer-specific wrapper composites in tasks 010-Sub-C through 010-Sub-F. No consumer operations are refactored in this task; the primitive is added in isolation so that subsequent tasks have a stable foundation to build on.

## Task 010-Sub-A goal

Add a new axiomatic wrapping primitive `typed_collection(items)` to the `primitives` layer that wraps any iterable as a typed observation. This primitive introduces typed lineage from a raw sequence at the substrate's input boundary. It has empty parent provenance (it is a calibrated primitive) and emits a new `CollectionStatus` family describing the cardinality of the wrapped collection.

The primitive is generic — it accepts any iterable and stores items as a tuple. It does not validate item types or content. Validation and layer-specific value-type wrapping happen in the composite primitives that consume `typed_collection` in subsequent tasks.

This task does not refactor any existing operations. The substrate after this task contains the new primitive *plus* the existing nine calibrated operations unchanged. The 010C audit re-runs and reports ten calibrated primitives total (the existing nine plus the new `typed_collection`). This is expected and correct; the calibrated set shrinks only after the consumer-refactor tasks.

## Design principles for Task 010-Sub-A

- **Substrate addition only.** The task adds new source files and adds new entries to `core/status.py`, `primitives/__init__.py`, and the layer manifest. No existing operations are modified. No existing tests are broken.
- **Primitive purity.** `typed_collection` constructs a `TypedResult` with `parents=()`. It is a true calibrated primitive.
- **Generic, layer-foundational.** The primitive is at the `primitives` layer because collections are foundational across all higher layers. It does not encode any layer-specific semantics.
- **Cardinality-based status.** The primitive emits one of three statuses based purely on the cardinality of the wrapped collection: `COLLECTION_EMPTY`, `COLLECTION_SINGLETON`, `COLLECTION_OBSERVED`. No content-based status determination — that's the consumer's job.
- **Iteration order preserved.** Items are materialised as a tuple, preserving the order of iteration. Consumers depend on this for chains where positional meaning matters (segment sequences, event ordering).
- **No item validation.** The primitive accepts `Iterable[Any]`. Item validation is the consumer composite's responsibility. The primitive is intentionally generic so it can wrap heterogeneous content.

## Primitive-sufficiency gate

This task introduces:

- A new status family `CollectionStatus` (3 members). Status families are an existing core concept; adding a new one extends `core/status.py` without altering existing families.
- A new value type `TypedCollectionValue` (a frozen-slots dataclass with `items: tuple[Any, ...]` and `count: int`). Value types are an existing core concept.
- A new producer protocol `TYPED_COLLECTION_PROTOCOL`. Producer protocols are an existing core concept.
- A new consumer protocol `NON_EMPTY_TYPED_COLLECTION_PROTOCOL` for downstream consumers that require non-empty collections. Consumer protocols are an existing core concept.
- A new operation `typed_collection(items)` at the `primitives` layer. Operations are an existing core concept.

Every concept this task uses (status families, value types, producer/consumer protocols, operations, the `Iterable` type from the standard library) is already provided by the existing substrate. Nothing new is required from below. Gate satisfied.

## Required deliverables

### 1. Add `CollectionStatus` family to `src/lloyd_v4/core/status.py`

A new `StrEnum` with three members:

```python
class CollectionStatus(StrEnum):
    COLLECTION_EMPTY = "collection_empty"
    COLLECTION_SINGLETON = "collection_singleton"
    COLLECTION_OBSERVED = "collection_observed"
```

Add `CollectionStatus` to the closed `StatusCode` union if such a union exists in `core/status.py`. Follow the existing pattern of the file exactly.

### 2. Create `src/lloyd_v4/primitives/typed_collection.py`

This file contains:

- The `TypedCollectionValue` frozen-slots dataclass:

```python
@dataclass(frozen=True, slots=True)
class TypedCollectionValue:
    items: tuple[Any, ...]
    count: int

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "items": to_json_safe(self.items),
            "count": self.count,
        }
```

- The producer protocol:

```python
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
```

- The non-empty consumer protocol (for downstream consumers that require a non-empty collection):

```python
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
```

- The result-type alias:

```python
TypedCollectionResult = TypedResult[TypedCollectionValue, CollectionStatus]
```

- The primitive operation:

```python
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
            parents=(),
        ),
        protocol=ProtocolStatus.OK,
    )
```

- Validity helper:

```python
def _validity_for_status(status: CollectionStatus) -> Validity:
    if status is CollectionStatus.COLLECTION_EMPTY:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
```

The conditioning is `WELL_CONDITIONED` for all three statuses. Empty is a factual observation about cardinality, not an indeterminate condition; downstream consumers decide whether they accept an empty input. The `selectable` field distinguishes empty (cannot select an item) from singleton/observed (can select).

### 3. Update `src/lloyd_v4/primitives/__init__.py`

Add the new public exports to the layer's `__all__` and import them from the new module. The new exports are:

- `CollectionStatus` (re-exported from core for convenience, if other primitives in `__init__.py` follow this pattern; otherwise leave `CollectionStatus` as a core-only export)
- `TYPED_COLLECTION_PROTOCOL`
- `NON_EMPTY_TYPED_COLLECTION_PROTOCOL`
- `TypedCollectionResult`
- `TypedCollectionValue`
- `typed_collection`

Verify the existing imports/re-exports pattern in `primitives/__init__.py` first and follow it consistently. Do not change the existing exports; only add the new ones in alphabetical position.

### 4. Update `Build_Docs/Architecture/layer_manifest.json`

Update the `primitives` layer entry as follows:

- `status_families`: append `CollectionStatus`.
- `value_types`: append `TypedCollectionValue`.
- `protocol_types`: append `TYPED_COLLECTION_PROTOCOL`, `NON_EMPTY_TYPED_COLLECTION_PROTOCOL`.
- `operations`: append `typed_collection`.
- `calibrated_primitive_operations`: append `typed_collection`.
- `all_exports`: insert the new exports in alphabetical position to match the actual `primitives/__init__.py __all__` content after deliverable 3.

### 5. Update `Build_Docs/Architecture/LAYER_MANIFEST.md`

Maintain Markdown parity with the JSON. Add the new entries to the `primitives` section in the same order and style as the existing content.

## Required tests

Create `tests/test_task010_sub_a_typed_collection.py` covering:

### Cardinality-based status emission

- `typed_collection([])` returns a TypedResult with status `COLLECTION_EMPTY`, count 0, items `()`, parents `()`, space `"TypedCollection"`, operation_id `"typed_collection"`.
- `typed_collection([42])` returns status `COLLECTION_SINGLETON`, count 1, items `(42,)`, parents `()`.
- `typed_collection([1, 2, 3])` returns status `COLLECTION_OBSERVED`, count 3, items `(1, 2, 3)`, parents `()`.

### Iterable acceptance

- `typed_collection(iter([1, 2]))` (a generator) works and produces a singleton or observed result correctly.
- `typed_collection((1, 2, 3))` (a tuple) works.
- `typed_collection(range(5))` works.
- Iteration order is preserved: `typed_collection([3, 1, 2]).value.items == (3, 1, 2)`.

### Heterogeneous content

- `typed_collection([1, "two", 3.0, None])` works without raising. Items are stored as-is. The primitive does not validate item types.

### Validity

- `COLLECTION_EMPTY` validity has `selectable=False`.
- `COLLECTION_SINGLETON` and `COLLECTION_OBSERVED` validity have `selectable=True`.
- All three have `defined=True`, `finite=True`, `observable=True`, `advanceable=False`.

### Conditioning

- All three statuses produce `WELL_CONDITIONED` conditioning.

### Provenance

- `provenance.operation_id == "typed_collection"`.
- `provenance.expression_path == "typed_collection_construction"`.
- `provenance.parents == ()`.
- The trace_id is deterministic (same inputs produce same trace_id).

### Protocol validation

- `validate_protocol(typed_collection([1, 2]), NON_EMPTY_TYPED_COLLECTION_PROTOCOL).ok` is `True`.
- `validate_protocol(typed_collection([]), NON_EMPTY_TYPED_COLLECTION_PROTOCOL).ok` is `False`.
- The refusal reason for an empty collection mentions `COLLECTION_EMPTY` or refers to the refused-status set.

### Manifest registration

- `typed_collection` appears in the `primitives.calibrated_primitive_operations` list in the JSON manifest.
- `typed_collection` appears in `primitives.operations` in the JSON manifest.
- `CollectionStatus` appears in `primitives.status_families` in the JSON manifest.
- The `primitives` layer's `all_exports` in the JSON manifest matches the actual `primitives/__init__.py __all__`.

### Audit re-runs

The existing 010C audits must continue to pass:

- `tests/test_task010c_lineage_terminates_in_primitive.py` passes. Any new TypedResults produced during the test session by `typed_collection` calls have empty parents and operation_id `"typed_collection"`, which is now in `calibrated_primitive_operations`.
- `tests/test_task010c_no_unregistered_operations.py` passes. `typed_collection` is registered.
- `tests/test_task010c_cross_family_transitions_justified.py` passes. The new primitive does not introduce any cross-family transitions on its own.
- `tests/test_task010c_no_chain_cycles.py` passes.
- `tests/test_task010b_*.py` audits pass with the manifest updates.

## Required commands

Run from repo root.

Red test slice (expected to fail before deliverables, since the new test file doesn't exist):

```bash
python -m pytest tests/test_task010_sub_a_typed_collection.py -q
```

Green test slice (expected to pass after deliverables):

```bash
python -m pytest tests/test_task010_sub_a_typed_collection.py -q
```

Full suite:

```bash
python -m pytest tests -q
```

The full suite must pass. The corpus reported by 010C grows by some number of `typed_collection` calls (one per test that exercises the primitive); the lineage audit re-runs cleanly because `typed_collection` is registered in the manifest.

Source audits (must remain clean):

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance|confidence_score|weighted_score|smoothing|hysteresis|interpolate|extrapolate" src/lloyd_v4 -n
rg -i "lloyd_core|lloyd_core_nvar|lloyd_decomposition|hyperdual|halley|multi_start|route_score" src/lloyd_v4 -n
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

Each audit must return no matches.

## Non-Goals

Do not implement:

- `typed_value` primitive. That is Task 010-Sub-B.
- Any layer-specific wrapper composites (`observation_sample_set`, `slope_flow_sample_set`, `event_set`, `step_model_set`, `solver_policy`, etc.). Those are Tasks 010-Sub-C through 010-Sub-F.
- Refactoring of any existing operations to consume `typed_collection`. The five composite-with-edge-case operations (`estimate_bk_noise_floor`, `compare_slope_flow_to_models`, `build_status_trace`, `evaluate_solver_step`, `run_typed_projection_solver`) remain unchanged in this task.
- Operation_id-as-measurement. That is Task 010C′.
- The off-the-shelf maths import audit. That is Task 010D.
- The discovery harness scaffold. That is Task 010F.
- The synthesis protocol. That is Task 010G.

Do not modify:

- Any source file under `src/lloyd_v4/` other than:
  - Adding the new `CollectionStatus` family to `core/status.py`
  - Adding the new file `primitives/typed_collection.py`
  - Adding the new exports to `primitives/__init__.py`
- `Build_Docs/Architecture/AXIOMS.md`
- `Build_Docs/Architecture/DISCOVERY_PHILOSOPHY.md`
- `Build_Docs/Architecture/DESIGN_THESIS.md`
- `Build_Docs/Agent_tasks/TASK_TEMPLATE.md`
- `tests/_audit_helpers/manifest.py` or `tests/_audit_helpers/lineage.py`
- Any existing test files. The existing tests must continue to pass without modification.

Do not introduce:

- New transition rules in this task. The transition rules connecting `CollectionStatus` to consumer status families belong in the consumer-refactor tasks.
- A second wrapping primitive (`typed_value`). That is the next task.
- Item validation in `typed_collection`. The primitive is intentionally generic.
- New runtime dependencies.

## Completion report

Create the following at task end:

```text
Build_Docs/Reports/task010_sub_a/task010_sub_a_summary.md
Build_Docs/Reports/task010_sub_a/typed_collection_design.md
```

`task010_sub_a_summary.md` must include:

- Files created
- Files modified
- Red test slice command and result
- Green test slice command and result
- Full-suite command and result
- Source audit commands and results
- Updated 010C lineage corpus stats: number of distinct operation_ids (now expected to be one greater than 010C's 24), number of calibrated primitives in the manifest (now 10 = 9 + typed_collection), confirmation that all four 010C audits re-run cleanly.
- Deviations, if any
- Readiness note for Task 010-Sub-B

`typed_collection_design.md` must include:

- A summary of the primitive's contract: input type, output type, status emission rules, validity rules, parent provenance behaviour.
- A statement of why the primitive is at the `primitives` layer (collections are layer-foundational; the primitive introduces typed lineage from raw sequences at the substrate's input boundary).
- A statement of what the primitive deliberately does NOT do (no item validation, no layer-specific semantics, no cross-family transitions).
- A note on the planned consumer-refactor pattern: each layer's wrapper composite (`observation_sample_set`, `slope_flow_sample_set`, etc.) will consume `typed_collection` and re-wrap with layer-specific value types, using `typed_collection.provenance.trace_id` as a parent. This pattern is documented here so subsequent tasks have a consistent reference.

## Acceptance criteria

Task 010-Sub-A is complete only when:

1. `CollectionStatus` is added to `src/lloyd_v4/core/status.py` with three members.
2. `src/lloyd_v4/primitives/typed_collection.py` exists with the value type, two protocols, result alias, primitive function, and validity helper.
3. `src/lloyd_v4/primitives/__init__.py` exports the new public names in `__all__`.
4. `Build_Docs/Architecture/layer_manifest.json` is updated with the new status family, value type, protocols, operation, and calibrated primitive entries in the `primitives` layer.
5. `Build_Docs/Architecture/LAYER_MANIFEST.md` retains parity with the JSON.
6. `tests/test_task010_sub_a_typed_collection.py` exists and exercises every behavioural property listed in the Required tests section.
7. All new tests pass.
8. All four 010C audits continue to pass with `typed_collection` registered as a calibrated primitive.
9. All four 010B audits continue to pass with the manifest updates.
10. Full test suite passes (no existing tests broken).
11. Source audits remain clean.
12. The primitive's parents tuple is `()` in every test that exercises it.
13. Reports are written under `Build_Docs/Reports/task010_sub_a/`.
14. Readiness note for Task 010-Sub-B is present in the summary report.

## Task 010-Sub-B readiness

When this task is complete and committed, the next task is **Task 010-Sub-B — typed_value primitive at primitives layer**. It introduces a parallel single-value wrapping primitive for cases where a single dataclass or scalar needs to be wrapped as typed input (used by the solver-refactor tasks for `LocalQuadraticStepModel` and `SolverPolicy`).

Before drafting `codex_task010_Sub_B.md`, re-evaluate against any findings 010-Sub-A surfaces:

- If the `typed_collection` implementation revealed any unexpected substrate frictions (status family registration patterns, manifest update mechanics, test-collection interactions), 010-Sub-B's spec should be adjusted to anticipate them.
- 010-Sub-B follows the same structural pattern as 010-Sub-A (new value type, producer protocol, consumer protocol, primitive function). The spec should reuse 010-Sub-A's pattern explicitly, including the same conditioning conventions and validity logic style.
- If the cross-test-suite operation_id corpus growth from `typed_collection` is more than expected (i.e., many tests construct typed collections), the lineage corpus stats in 010-Sub-B's planning should account for further growth.

Note these in `task010_sub_a_summary.md` before drafting `codex_task010_Sub_B.md`.
