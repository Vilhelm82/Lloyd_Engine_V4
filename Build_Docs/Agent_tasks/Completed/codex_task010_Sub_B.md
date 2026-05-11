# Codex Task 010-Sub-B: typed_value Primitive at primitives Layer

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

Task 010-Sub-B is the second task in the substrate-extension sequence. Like 010-Sub-A, this is a substrate-modifying task — it adds new source code at the `primitives` layer.

## Current verified baseline

Tasks 000 through 009A, 010A, 010B, 010C, and 010-Sub-A are complete.

010-Sub-A added `primitives.typed_collection` as the foundational raw-sequence wrapping primitive. The substrate now has 25 distinct operation_ids and 10 calibrated primitives. The 010B and 010C audits all pass cleanly with `typed_collection` registered. The consumer-refactor pattern documented in `Build_Docs/Reports/task010_sub_a/typed_collection_design.md` is the template for all subsequent layer-specific wrapper composites in tasks 010-Sub-C through 010-Sub-F.

010-Sub-B adds the parallel single-value wrapping primitive `typed_value`. Together with `typed_collection`, these are the two foundational substrate-input wrapping primitives that every layer-specific wrapper composite in the remaining substrate-extension series will derive from. After 010-Sub-B lands, `typed_collection` covers raw-sequence inputs and `typed_value` covers raw single-value inputs (such as solver step models, solver policies, and any other dataclass or scalar that needs to be wrapped at a substrate boundary).

## Task 010-Sub-B goal

Add a new axiomatic wrapping primitive `typed_value(value)` at the `primitives` layer that wraps any single value as a typed observation. The primitive parallels `typed_collection` in structure: it has empty parent provenance, emits a new `ValueStatus` family describing whether the value is present or absent, and does not perform content validation.

The primitive is generic — it accepts any value and stores it as-is. It does not validate the value's type, structure, or content. Validation and layer-specific value-type wrapping happen in the composite primitives that consume `typed_value` in subsequent tasks (specifically 010-Sub-F for `solver.step_model` and `solver.solver_policy`).

This task does not refactor any existing operations. After this task the substrate contains 11 calibrated primitives (the 10 from 010-Sub-A plus `typed_value`) and 26 distinct operation_ids. The calibrated set begins shrinking only after the consumer-refactor tasks (010-Sub-C through F).

## Design principles for Task 010-Sub-B

- **Substrate addition only.** The task adds new source files and adds new entries to `core/status.py`, `primitives/__init__.py`, and the layer manifest. No existing operations are modified. No existing tests are broken.
- **Primitive purity.** `typed_value` constructs a `TypedResult` with `parents=()`. It is a true calibrated primitive.
- **Generic, layer-foundational.** The primitive is at the `primitives` layer because single-value wrapping is layer-foundational. It does not encode any layer-specific semantics.
- **Presence-based status.** The primitive emits one of two statuses based purely on whether the value is `None`: `VALUE_ABSENT` (value is `None`) or `VALUE_OBSERVED` (value is not `None`). Mirrors `typed_collection`'s empty/non-empty distinction at the single-value level.
- **`None` is the sentinel for absence.** Falsy non-None values (`0`, `False`, `""`, `[]`, `{}`) are observations of present values, not absent values. The check is `value is None`, not `not value`.
- **No content validation.** The primitive accepts `Any`. Type validation and structural validation are the consumer composite's responsibility. Same intentional genericity as `typed_collection`.

## Primitive-sufficiency gate

Same gate as 010-Sub-A. This task introduces:

- A new status family `ValueStatus` (2 members). Status families are an existing core concept.
- A new value type `TypedValueValue` (a frozen-slots dataclass). Value types are an existing core concept.
- A new producer protocol `TYPED_VALUE_PROTOCOL`. Existing core concept.
- A new consumer protocol `NON_NULL_TYPED_VALUE_PROTOCOL`. Existing core concept.
- A new operation `typed_value(value)` at the `primitives` layer. Existing core concept.

Every concept this task uses is already provided by the existing substrate. Gate satisfied.

## Required deliverables

### 1. Add `ValueStatus` family to `src/lloyd_v4/core/status.py`

A new `StrEnum` with two members:

```python
class ValueStatus(StrEnum):
    VALUE_ABSENT = "value_absent"
    VALUE_OBSERVED = "value_observed"
```

Add `ValueStatus` to the closed `StatusCode` union if such a union exists in `core/status.py`. Follow the existing pattern of the file exactly, including the position relative to `CollectionStatus` (added in 010-Sub-A).

### 2. Create `src/lloyd_v4/primitives/typed_value.py`

This file mirrors `src/lloyd_v4/primitives/typed_collection.py` in structure. Required contents:

- The `TypedValueValue` frozen-slots dataclass:

```python
@dataclass(frozen=True, slots=True)
class TypedValueValue:
    value: Any
    is_present: bool

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "value": to_json_safe(self.value),
            "is_present": self.is_present,
        }
```

The `is_present` field is `True` when `value is not None` and `False` when `value is None`. Stored explicitly to mirror `TypedCollectionValue.count`'s explicit storage; downstream consumers can read either field directly without re-computing.

- The producer protocol:

```python
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
```

- The non-null consumer protocol:

```python
NON_NULL_TYPED_VALUE_PROTOCOL = ConsumerProtocol(
    name="non_null_typed_value",
    accepted_statuses=frozenset({ValueStatus.VALUE_OBSERVED}),
    required_validity_fields=frozenset({"defined", "selectable"}),
    scalarization_allowed=False,
    status_family=ValueStatus,
    refused_statuses=frozenset({ValueStatus.VALUE_ABSENT}),
)
```

- The result-type alias:

```python
TypedValueResult = TypedResult[TypedValueValue, ValueStatus]
```

- The primitive operation:

```python
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
            parents=(),
        ),
        protocol=ProtocolStatus.OK,
    )
```

- Validity helper:

```python
def _validity_for_status(status: ValueStatus) -> Validity:
    if status is ValueStatus.VALUE_ABSENT:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
```

`VALUE_ABSENT` has `defined=True` because the absence is itself a defined observation (mirrors `COLLECTION_EMPTY`'s `defined=True`). It has `selectable=False` because there is no value to select. `VALUE_OBSERVED` has `selectable=True`. Conditioning is `WELL_CONDITIONED` for both — value presence/absence is a factual observation, not an indeterminate state.

### 3. Update `src/lloyd_v4/primitives/__init__.py`

Add the new public exports to the layer's `__all__` and import them from the new module. The new exports are:

- `TYPED_VALUE_PROTOCOL`
- `NON_NULL_TYPED_VALUE_PROTOCOL`
- `TypedValueResult`
- `TypedValueValue`
- `typed_value`

Insert them in alphabetical position to match the existing convention. Do not change any existing exports.

### 4. Update `Build_Docs/Architecture/layer_manifest.json`

Update the `primitives` layer entry as follows:

- `status_families`: append `ValueStatus`.
- `value_types`: append `TypedValueValue`.
- `protocol_types`: append `TYPED_VALUE_PROTOCOL`, `NON_NULL_TYPED_VALUE_PROTOCOL`.
- `operations`: append `typed_value`.
- `calibrated_primitive_operations`: append `typed_value`.
- `all_exports`: insert the new exports in alphabetical position to match the actual `primitives/__init__.py __all__` content after deliverable 3.

### 5. Update `Build_Docs/Architecture/LAYER_MANIFEST.md`

Maintain Markdown parity with the JSON. Add the new entries to the `primitives` section in the same order and style as the existing content.

## Required tests

Create `tests/test_task010_sub_b_typed_value.py` covering:

### Presence-based status emission

- `typed_value(42)` returns a TypedResult with status `VALUE_OBSERVED`, `is_present=True`, `value=42`, parents `()`, space `"TypedValue"`, operation_id `"typed_value"`.
- `typed_value(None)` returns status `VALUE_ABSENT`, `is_present=False`, `value=None`, parents `()`.
- `typed_value("hello")` returns `VALUE_OBSERVED`, `value="hello"`.

### Falsy non-None values are present

- `typed_value(0)` returns `VALUE_OBSERVED` with `value=0` and `is_present=True`. Zero is a value, not absence.
- `typed_value(False)` returns `VALUE_OBSERVED` with `value=False` and `is_present=True`.
- `typed_value("")` returns `VALUE_OBSERVED` with `value=""` and `is_present=True`.
- `typed_value([])` returns `VALUE_OBSERVED` with `value=[]` and `is_present=True`. The primitive does not unwrap the empty list as absent.
- `typed_value({})` returns `VALUE_OBSERVED` with `value={}` and `is_present=True`.

### Heterogeneous content

- `typed_value(some_frozen_dataclass)` works without raising. The dataclass is stored as-is in `value`.
- `typed_value(some_typed_result)` works without raising. (A nested TypedResult as a value is permitted; this primitive does not interpret the contents.)
- `typed_value(0.0)` works.
- `typed_value(complex(1, 2))` works.

### Validity

- `VALUE_OBSERVED` validity has `selectable=True`, `defined=True`, `finite=True`, `observable=True`, `advanceable=False`.
- `VALUE_ABSENT` validity has `selectable=False`, `defined=True`, `finite=True`, `observable=True`, `advanceable=False`.

### Conditioning

- Both statuses produce `WELL_CONDITIONED` conditioning.

### Provenance

- `provenance.operation_id == "typed_value"`.
- `provenance.expression_path == "typed_value_construction"`.
- `provenance.parents == ()`.
- The trace_id is deterministic (same inputs produce same trace_id for hashable values; for unhashable values, each call may produce a fresh trace_id, which is acceptable — note this in the test file with a comment).

### Protocol validation

- `validate_protocol(typed_value(42), NON_NULL_TYPED_VALUE_PROTOCOL).ok` is `True`.
- `validate_protocol(typed_value(None), NON_NULL_TYPED_VALUE_PROTOCOL).ok` is `False`.
- The refusal reason for an absent value mentions `VALUE_ABSENT` or refers to the refused-status set.

### Manifest registration

- `typed_value` appears in the `primitives.calibrated_primitive_operations` list in the JSON manifest.
- `typed_value` appears in `primitives.operations`.
- `ValueStatus` appears in `primitives.status_families`.
- The `primitives` layer's `all_exports` in the JSON manifest matches the actual `primitives/__init__.py __all__`.

### Audit re-runs

The existing 010B and 010C audits must continue to pass:

- `tests/test_task010c_lineage_terminates_in_primitive.py`: `typed_value` instances produced during the test session have empty parents and operation_id `"typed_value"`, which is now in `calibrated_primitive_operations`.
- `tests/test_task010c_no_unregistered_operations.py`: `typed_value` is registered.
- `tests/test_task010c_cross_family_transitions_justified.py`: the new primitive does not introduce any cross-family transitions.
- `tests/test_task010c_no_chain_cycles.py`.
- `tests/test_task010b_*.py` audits pass with the manifest updates.

## Required commands

Run from repo root.

Red test slice (expected to fail before deliverables):

```bash
python -m pytest tests/test_task010_sub_b_typed_value.py -q
```

Green test slice:

```bash
python -m pytest tests/test_task010_sub_b_typed_value.py -q
```

Full suite:

```bash
python -m pytest tests -q
```

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

- Any layer-specific wrapper composites. Tasks 010-Sub-C through 010-Sub-F own those.
- Refactoring of any existing operations to consume `typed_value`. Operations like `evaluate_solver_step` and `run_typed_projection_solver` remain unchanged in this task; their refactor happens in 010-Sub-F.
- Operation_id-as-measurement (Task 010C′).
- The off-the-shelf maths import audit (Task 010D).
- The discovery harness scaffold (Task 010F).
- The synthesis protocol (Task 010G).

Do not modify:

- Any source file under `src/lloyd_v4/` other than:
  - Adding the new `ValueStatus` family to `core/status.py`
  - Adding the new file `primitives/typed_value.py`
  - Adding the new exports to `primitives/__init__.py`
- Any architecture document other than `layer_manifest.json` and `LAYER_MANIFEST.md` (for the `primitives` entry only).
- `Build_Docs/Reports/task010_sub_a/typed_collection_design.md`. The 010-Sub-A design doc remains the consumer-refactor pattern reference; 010-Sub-B's design doc complements it for single-value wrapping.
- `tests/_audit_helpers/manifest.py` or `tests/_audit_helpers/lineage.py`.
- Any existing test file. Existing tests must continue to pass without modification.
- `src/lloyd_v4/primitives/typed_collection.py`. The 010-Sub-A primitive remains unchanged.

Do not introduce:

- New transition rules. Transitions connecting `ValueStatus` to consumer status families belong in the consumer-refactor tasks.
- Type validation in `typed_value`. The primitive is intentionally generic.
- A `VALUE_INVALID` or similar status. Validity of content is the consumer's concern, not the primitive's.
- New runtime dependencies.

## Completion report

Create the following at task end:

```text
Build_Docs/Reports/task010_sub_b/task010_sub_b_summary.md
Build_Docs/Reports/task010_sub_b/typed_value_design.md
```

`task010_sub_b_summary.md` must include:

- Files created
- Files modified
- Red test slice command and result
- Green test slice command and result
- Full-suite command and result
- Source audit commands and results
- Updated 010C lineage corpus stats: number of distinct operation_ids (now expected to be 26 = 25 + typed_value), number of calibrated primitives in the manifest (now 11 = 10 + typed_value), confirmation that all four 010C audits and all four 010B audits re-run cleanly.
- Deviations, if any.
- Readiness note for Task 010-Sub-C.

`typed_value_design.md` must include:

- The primitive's contract: input type, output type, status emission rules (presence-based on `value is None`), validity rules, parent provenance behaviour.
- The rationale for layer placement (single-value wrapping is layer-foundational; the primitive sits alongside `typed_collection` at `primitives` to cover the second class of substrate input boundaries).
- Deliberate non-behaviour: no type validation, no content inspection, no semantic interpretation, no cross-family transitions.
- The relationship to `typed_collection`: `typed_collection` covers raw-sequence inputs; `typed_value` covers raw single-value inputs. Together they cover the substrate's input boundary completely for the consumer-refactor tasks 010-Sub-C through 010-Sub-F.
- Reference to `typed_collection_design.md` for the canonical consumer-refactor pattern. The pattern for `typed_value` consumers is identical: call `typed_value(raw)` → validate non-null with `NON_NULL_TYPED_VALUE_PROTOCOL` if needed → construct layer-specific typed value → use `typed_value` trace_id as provenance parent.
- The `is_present` field rationale: stored explicitly to mirror `TypedCollectionValue.count` and to let downstream consumers read presence without re-comparing against `None`.

## Acceptance criteria

Task 010-Sub-B is complete only when:

1. `ValueStatus` is added to `src/lloyd_v4/core/status.py` with two members.
2. `src/lloyd_v4/primitives/typed_value.py` exists with the value type, two protocols, result alias, primitive function, and validity helper.
3. `src/lloyd_v4/primitives/__init__.py` exports the new public names in `__all__`.
4. `Build_Docs/Architecture/layer_manifest.json` is updated with the new status family, value type, protocols, operation, and calibrated primitive entries in the `primitives` layer.
5. `Build_Docs/Architecture/LAYER_MANIFEST.md` retains parity with the JSON.
6. `tests/test_task010_sub_b_typed_value.py` exists and exercises every behavioural property listed in the Required tests section.
7. All new tests pass.
8. All four 010C audits continue to pass with `typed_value` registered as a calibrated primitive.
9. All four 010B audits continue to pass with the manifest updates.
10. Full test suite passes (no existing tests broken).
11. Source audits remain clean.
12. The primitive's parents tuple is `()` in every test that exercises it.
13. `typed_value(0)`, `typed_value(False)`, `typed_value("")`, `typed_value([])`, and `typed_value({})` all produce `VALUE_OBSERVED`. Only `typed_value(None)` produces `VALUE_ABSENT`.
14. Reports are written under `Build_Docs/Reports/task010_sub_b/`.
15. Readiness note for Task 010-Sub-C is present in the summary report.

## Task 010-Sub-C readiness

When this task is complete and committed, the next task is **Task 010-Sub-C — metrology.observation_sample_set composite + estimate_bk_noise_floor refactor**. This is the first task in the substrate-extension series that exercises the consumer-refactor pattern on a real existing operation. It will reveal whether the pattern documented in `typed_collection_design.md` generalises cleanly or whether the first concrete application surfaces something we hadn't anticipated.

Before drafting `codex_task010_Sub_C.md`, re-evaluate against any findings 010-Sub-B surfaces:

- If the `typed_value` implementation revealed any frictions specific to single-value wrapping (e.g. unhashable-value trace_id behaviour, frozen-dataclass storage subtleties, `is_present` field interactions with Pydantic-style serialization), 010-Sub-C's spec should anticipate them where they would also affect collection wrapping.
- If the manifest update or audit re-run surfaced any drift from 010-Sub-A's state (similar to 010-Sub-A's calibrated-primitive-ownership correction), document it explicitly so 010-Sub-C starts from a clean baseline.
- 010-Sub-C is the first task that *modifies* an existing operation rather than purely adding new code. The non-goals constraint structure changes accordingly. The substrate extension series's risk profile shifts from 010-Sub-C onward; the spec should reflect this with a more careful before/after behavioural comparison section.

Note these in `task010_sub_b_summary.md` before drafting `codex_task010_Sub_C.md`.
