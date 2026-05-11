# Codex Task 010-Rebuild-Projection: Clean Rebuild of the projection Layer

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

This is a substrate-modifying task. It replaces the entire `projection` layer source against the V4 substrate principles, rebuilds the projection tests as specification tests, and updates the call sites in any other layer that calls `exact_quadratic_projection`.

## Current verified baseline

Tasks 000 through 009A, 010A, 010B, 010C, 010-Sub-A, and 010-Sub-B are complete.

The substrate now has:

- `core` with status families, TypedResult/TypedRefusal, Provenance, Validity, Conditioning, ProducerProtocol/ConsumerProtocol, StatusTransitionRule machinery.
- `primitives` layer with `projective_ratio`, `stratified_quadratic_roots`, `typed_collection`, `typed_value` — four axiomatic primitives covering geometric algebra and substrate-input wrapping.

The 010B and 010C audits all pass. Lineage corpus stats from 010-Sub-B: 26 distinct operation_ids, 11 calibrated primitives.

The substrate-extension series (010-Sub-A through F) was reframed: instead of refactoring existing operations to consume typed inputs while preserving signatures, the consumer layers are being rebuilt cleanly against the typed primitive substrate. The "preserve existing signatures" constraint that motivated the refactor framing exists to protect production consumers, and V4 has none. Removing the constraint produces cleaner code.

This task is the first rebuild. The projection layer is the lowest consumer layer (depends only on core + primitives). Subsequent rebuilds will follow a similar pattern, layer by layer up the dependency graph, each evaluated independently before commit.

## Task 010-Rebuild-Projection goal

Replace the projection layer's source against V4 substrate principles, addressing five concrete issues that 010C-style auditing has surfaced or that direct inspection identified:

1. **Branch selection is a raw string at the operation boundary.** `exact_quadratic_projection(root_state, branch: str)` accepts a Python string with a documented closed set `{"minus", "plus", "repeated", "linear"}`. This is an un-typed substrate-input boundary. Branch selection is a geometric choice (which root, which direction) and should be a typed input.

2. **Wrong-status input raises `ProtocolViolationError`.** The operation conflates wrong-Python-type errors (programmer error, exception is appropriate) with right-Python-type-but-wrong-status conditions (substrate observation, should be typed refusal). The two paths should be separated.

3. **`ProjectionResultValue.refusal: dict[str, Any] | None` duplicates `TypedResult.refusal`.** Two representations of the same fact. The TypedResult-level refusal is canonical.

4. **`ProjectionFlags` denormalizes status into four booleans.** `root_exists`, `projection_defined`, `selected_root_valid`, `advance_valid` are uniquely determined by the projection status. The redundant denormalization adds maintenance burden without buying anything the geometry actually needs at this layer.

5. **The transition rule is declarative metadata only.** `QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE` defines a `transition` callable, but `exact_quadratic_projection` does the mapping directly via two module-level dicts (`_SELECTABLE_PROJECTION_STATUS`, `_NONSELECTABLE_PROJECTION_STATUS`). The rule registration is for audit machinery only. The rebuild makes the transition rule active machinery; the dispatch dicts go away.

The rebuild replaces the projection source. It does NOT rebuild any other layer; it only updates the call sites in other layers that invoke `exact_quadratic_projection`.

## Design principles for Task 010-Rebuild-Projection

- **Spec-driven, not behavior-preserving.** The rebuild's behavior is derived from substrate principles applied to what the projection layer needs to do. Where the rebuild's behavior differs from the current implementation, the difference is justified by a substrate principle. Existing test assertions that were testing artifacts of the un-typed interface get rewritten against the new specification; assertions that were testing genuine geometric behavior survive in the rewritten tests.
- **Typed inputs at every boundary.** The operation consumes typed observations only. Branch selection becomes a typed BranchSelection observation produced by a layer-local composite that wraps via `typed_value`.
- **Typed refusal for substrate observations; exceptions for programmer errors.** Wrong Python type → `ProtocolViolationError`. Wrong-status-on-right-type → typed refusal returned as a TypedResult.
- **Transition rule is active.** `apply_status_transition` is invoked at runtime to determine the projection status. The rule's `transition` callable is the authoritative dispatch.
- **Single source of truth for refusal.** The TypedResult-level `refusal` field is canonical. No redundant dict copy in the value type.
- **Status family taxonomy unchanged.** `ProjectionStatus`'s seven members capture the actual cases the geometry produces. No reason to redesign.
- **No anticipatory additions.** The rebuild does only what the projection layer's geometry surfaces. No tolerance contracts, no flag-derivation utilities, no consumer-ergonomic helpers. If a consumer later needs flags or any other derived view, they get added when that need surfaces.

## Primitive-sufficiency gate

This task uses:

- `BranchSelection` enum (new, projection-layer-local). Enum is a Python language feature; not new substrate.
- `BranchSelectionValue` value type (new, projection-layer-local). Value types are an existing core concept.
- `branch_selection(branch: BranchSelection) → TypedResult` composite (new, projection-layer-local). Consumes `typed_value` from primitives. Composites are an existing core concept.
- Existing `apply_status_transition` machinery from core.
- Existing `select_quadratic_root` from primitives.
- Existing `STRATIFIED_QUADRATIC_ROOTS_PROTOCOL` and `QUADRATIC_ROOT_SELECTION_PROTOCOL` from primitives.
- Existing `ProjectionStatus` from core.

Every concept is already provided by the current substrate. Gate satisfied.

## Required deliverables

### 1. Replace `src/lloyd_v4/projection/branches.py` (new file)

Contains:

- The `BranchSelection` `StrEnum` with four members:

```python
class BranchSelection(StrEnum):
    MINUS = "minus"
    PLUS = "plus"
    REPEATED = "repeated"
    LINEAR = "linear"
```

- The `BranchSelectionValue` frozen-slots dataclass:

```python
@dataclass(frozen=True, slots=True)
class BranchSelectionValue:
    branch: BranchSelection

    def to_json_safe(self) -> dict[str, str]:
        return {"branch": self.branch.value}
```

- The producer protocol `BRANCH_SELECTION_PROTOCOL` and consumer protocol `BRANCH_SELECTION_CONSUMER_PROTOCOL` over `ValueStatus` (since the underlying typed_value carries `ValueStatus`).

- The result-type alias `BranchSelectionResult = TypedResult[BranchSelectionValue, ValueStatus]`.

- The composite operation:

```python
def branch_selection(branch: BranchSelection) -> BranchSelectionResult:
    if not isinstance(branch, BranchSelection):
        raise ProtocolViolationError("branch must be a BranchSelection enum member")
    inner = typed_value(branch)
    value = BranchSelectionValue(branch=branch)
    return TypedResult(
        value=value,
        space="BranchSelection",
        status=inner.status,  # VALUE_OBSERVED, since branch is non-None by Python type
        validity=inner.validity,
        conditioning=inner.conditioning,
        provenance=Provenance(
            operation_id="branch_selection",
            expression_path="branch_selection_construction",
            parents=(inner.provenance.trace_id,),
        ),
        protocol=ProtocolStatus.OK,
    )
```

This is a composite (parents non-empty). It is *not* a calibrated primitive.

The wrong-Python-type check raises `ProtocolViolationError` because passing something that isn't a `BranchSelection` is a programmer error. The composite has no other failure mode at this layer; the `typed_value` primitive cannot fail on a non-None enum member.

### 2. Replace `src/lloyd_v4/projection/exact_projection.py`

The new file contains:

- `EXACT_QUADRATIC_PROJECTION_PROTOCOL` (consumer protocol, accepts the existing root-state statuses) — same as current.
- `PROJECTION_RESULT_V4_PROTOCOL` (producer protocol, emits the seven `ProjectionStatus` members) — same as current.
- `ProjectionResultValue` value type, **without** the `refusal` field and **without** any reference to `ProjectionFlags`. Fields:
  - `source_status: str`
  - `requested_branch: str` (the branch enum's string value, for serialization clarity)
  - `selected_branch: str | None`
  - `selected_root_value: Any | None`
  - `selected_root_trace_id: str | None`
  - `source_trace_id: str`
  - `source_operation_id: str`
  - `projection_status: str`

  `to_json_safe` updated accordingly.

- `ProjectionResultV4 = TypedResult[ProjectionResultValue, ProjectionStatus]`.
- `QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE` — same `StatusTransitionRule` definition, but the `transition` callable is invoked at runtime.
- `exact_quadratic_projection(root_state_result, branch_selection_result)` — new signature.

The operation's logic:

```python
def exact_quadratic_projection(
    root_state_result: TypedResult,
    branch_selection_result: TypedResult,
) -> ProjectionResultV4:
    # Wrong Python type → programmer error → exception
    _require_typed_result(root_state_result, "root_state_result")
    _require_typed_result(branch_selection_result, "branch_selection_result")
    _require_value_type(root_state_result, StratifiedQuadraticRootValue, "root_state_result")
    _require_value_type(branch_selection_result, BranchSelectionValue, "branch_selection_result")

    # Wrong-status root state → typed refusal returned as a TypedResult
    root_check = validate_protocol(root_state_result, EXACT_QUADRATIC_PROJECTION_PROTOCOL)
    if not root_check.ok:
        return _projection_input_refusal(
            root_state_result=root_state_result,
            branch_selection_result=branch_selection_result,
            reason=root_check.reason,
        )

    # Wrong-status branch selection → typed refusal
    branch_check = validate_protocol(branch_selection_result, BRANCH_SELECTION_CONSUMER_PROTOCOL)
    if not branch_check.ok:
        return _projection_input_refusal(
            root_state_result=root_state_result,
            branch_selection_result=branch_selection_result,
            reason=branch_check.reason,
        )

    # Apply transition rule actively
    branch = branch_selection_result.value.branch
    transition_outcome = apply_status_transition(
        QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE,
        root_state_result.status,
        context={"branch": branch},
    )
    projection_status = transition_outcome.output_status

    # Dispatch based on the transition outcome
    if projection_status is ProjectionStatus.PROJECTION_SELECTION_REFUSED:
        return _projection_result(
            root_state_result=root_state_result,
            branch_selection_result=branch_selection_result,
            projection_status=projection_status,
            selected_root=None,
            refusal=_branch_incompatibility_refusal(root_state_result, branch),
        )

    if _is_nonselectable_projection_status(projection_status):
        return _projection_result(
            root_state_result=root_state_result,
            branch_selection_result=branch_selection_result,
            projection_status=projection_status,
            selected_root=None,
            refusal=None,
        )

    selected_root = select_quadratic_root(root_state_result, branch.value)
    if selected_root.refusal is not None:
        return _projection_result(
            root_state_result=root_state_result,
            branch_selection_result=branch_selection_result,
            projection_status=ProjectionStatus.PROJECTION_SELECTION_REFUSED,
            selected_root=selected_root,
            refusal=selected_root.refusal,
        )

    return _projection_result(
        root_state_result=root_state_result,
        branch_selection_result=branch_selection_result,
        projection_status=projection_status,
        selected_root=selected_root,
        refusal=None,
    )
```

The `_projection_result` helper constructs the final `TypedResult` with the new `ProjectionResultValue` (no refusal dict, no flags), the canonical TypedResult-level refusal, full provenance carrying parents from both the root_state_result and branch_selection_result trace_ids (and the selected_root trace_id when present), validity, and conditioning.

The two dicts `_SELECTABLE_PROJECTION_STATUS` and `_NONSELECTABLE_PROJECTION_STATUS` go away. Their content is now expressed inside the `transition` callable on the rule. The helper `_is_nonselectable_projection_status` is a small predicate against the three nonselectable members.

### 3. Update `src/lloyd_v4/projection/__init__.py`

Replace the exports list to match the new module surface:

- `BRANCH_SELECTION_PROTOCOL`, `BRANCH_SELECTION_CONSUMER_PROTOCOL`, `BranchSelection`, `BranchSelectionResult`, `BranchSelectionValue`, `branch_selection` (from the new `branches.py`)
- `EXACT_QUADRATIC_PROJECTION_PROTOCOL`, `QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE`, `PROJECTION_RESULT_V4_PROTOCOL`, `ProjectionResultV4`, `ProjectionResultValue`, `exact_quadratic_projection` (from the rebuilt `exact_projection.py`)

Note `ProjectionFlags` is removed from `__all__`.

### 4. Update call sites in other layers

Search the substrate for callers of `exact_quadratic_projection`:

```bash
rg "exact_quadratic_projection\(" src/lloyd_v4 -n
```

Each caller receives a string-based branch and passes it directly. Update each call site to:

1. Import `BranchSelection` and `branch_selection` from `lloyd_v4.projection`.
2. Construct `branch_enum = BranchSelection(model.branch)` from the existing string field.
3. Call `branch_selection(branch_enum)` to produce a typed branch selection.
4. Pass the typed branch selection result to `exact_quadratic_projection`.

The known caller is `src/lloyd_v4/solver/typed_projection_solver.py:evaluate_solver_step`. There may be others; the grep finds all of them. The internal data structures of those layers are NOT rebuilt here; only their call site to projection changes. Their `branch: str` fields stay strings until those layers' own rebuild tasks.

### 5. Rewrite projection tests

Replace the existing five test files with specification tests for the new design:

- `tests/test_task010_rebuild_projection_branch_selection.py` — new, tests the `branch_selection` composite and `BranchSelection` enum.
- `tests/test_task010_rebuild_projection_protocol.py` — replaces `tests/test_task003_projection_protocol.py`. Tests the new typed-input contract, including: wrong Python type raises, wrong-status returns typed refusal (does NOT raise), missing branch input handling.
- `tests/test_task010_rebuild_projection_result.py` — replaces `tests/test_task003_projection_result.py`. Tests the value-type structure (no `refusal` dict, no `ProjectionFlags`), provenance with parents from both inputs, source-trace preservation.
- `tests/test_task010_rebuild_projection_serialization.py` — replaces `tests/test_task003_projection_serialization.py`. Tests `to_json_safe` on the new `ProjectionResultValue` (no flags field, no refusal dict).
- `tests/test_task010_rebuild_projection_strata_scenarios.py` — replaces `tests/test_task009a_projection_strata_scenarios.py`. Tests each of the seven projection statuses across the appropriate root-state strata.

Update `tests/test_task009_solver_step_projection.py` to use the new call-site pattern (construct typed branch input before calling). The test's intent is preserved — it tests that the solver's projection call produces correct results — but the call expression changes.

The five replaced files are deleted. The `_solver_step_projection` test is updated in place.

### 6. Update manifest entries

In `Build_Docs/Architecture/layer_manifest.json`, update the `projection` layer:

- `status_families`: unchanged (still owns `ProjectionStatus`).
- `value_types`: replace `ProjectionFlags` and old `ProjectionResultValue` listing with `BranchSelectionValue`, `ProjectionResultValue`. (`ProjectionFlags` is removed.)
- `protocol_types`: append `BRANCH_SELECTION_PROTOCOL`, `BRANCH_SELECTION_CONSUMER_PROTOCOL` alongside the existing two.
- `transition_types`: unchanged (still has `QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE`).
- `errors_and_utilities`: unchanged.
- `operations`: append `branch_selection` alongside `exact_quadratic_projection`.
- `calibrated_primitive_operations`: should be empty for `projection` after the rebuild. The current manifest had `exact_quadratic_projection` listed there; it shouldn't have been (the operation has parents). Verify and correct if so.
- `internal_operations`: unchanged.
- `all_exports`: regenerate to match the rebuilt `__init__.py __all__`.

### 7. Update Markdown manifest parity

`Build_Docs/Architecture/LAYER_MANIFEST.md` — keep the projection section's structure consistent with the JSON.

## Required tests

- `tests/test_task010_rebuild_projection_branch_selection.py`
- `tests/test_task010_rebuild_projection_protocol.py`
- `tests/test_task010_rebuild_projection_result.py`
- `tests/test_task010_rebuild_projection_serialization.py`
- `tests/test_task010_rebuild_projection_strata_scenarios.py`
- Updated: `tests/test_task009_solver_step_projection.py` (call site updated, test intent preserved)

Deleted:

- `tests/test_task003_projection_protocol.py`
- `tests/test_task003_projection_result.py`
- `tests/test_task003_projection_serialization.py`
- `tests/test_task009a_projection_strata_scenarios.py`

## Required commands

Run from repo root.

Red test slice (expected to fail before deliverables; failure modes will include both missing new test files and old test files that now fail against the new source):

```bash
python -m pytest tests/test_task010_rebuild_projection_branch_selection.py tests/test_task010_rebuild_projection_protocol.py tests/test_task010_rebuild_projection_result.py tests/test_task010_rebuild_projection_serialization.py tests/test_task010_rebuild_projection_strata_scenarios.py -q
```

Green test slice:

```bash
python -m pytest tests/test_task010_rebuild_projection_branch_selection.py tests/test_task010_rebuild_projection_protocol.py tests/test_task010_rebuild_projection_result.py tests/test_task010_rebuild_projection_serialization.py tests/test_task010_rebuild_projection_strata_scenarios.py -q
```

Full suite (must pass with the rebuilt projection, updated solver call site, and new/updated tests):

```bash
python -m pytest tests -q
```

010B and 010C audits explicitly:

```bash
python -m pytest tests/test_task010b_manifest_completeness.py tests/test_task010b_export_drift.py tests/test_task010b_cross_layer_parent_check.py tests/test_task010b_status_family_layer_coherence.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_cross_family_transitions_justified.py tests/test_task010c_no_chain_cycles.py -q
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

- Rebuild of any other layer. Metrology, branch, refinery, history, solver remain as-is. Only their call sites to `exact_quadratic_projection` get updated.
- Operation_id-as-measurement (Task 010C′).
- The off-the-shelf maths import audit (Task 010D).
- Any new status family beyond what the projection layer already had.
- Any flag-derivation utility for downstream consumers. If a later consumer rebuild needs flag-style ergonomics, that consumer derives them from status at its consumption site.
- Any tolerance-contract documentation or per-operation precision specification.
- A `PROJECTION_PROTOCOL_REFUSED` status (or any new ProjectionStatus member). Wrong-status input produces a typed refusal carrying the existing input's status; no new status family member is needed.
- Behavior preservation for the sake of preservation. Test assertions that test artifacts of the un-typed interface get rewritten against the new spec.

Do not modify:

- Any source file under `src/lloyd_v4/` other than:
  - `src/lloyd_v4/projection/branches.py` (new)
  - `src/lloyd_v4/projection/exact_projection.py` (rebuilt)
  - `src/lloyd_v4/projection/__init__.py` (export list updated)
  - The call sites in other layers identified by the `exact_quadratic_projection(` grep — only the call expressions, not the surrounding logic.
- `core/status.py`. No new status family members are needed.
- `Build_Docs/Architecture/AXIOMS.md`, `DISCOVERY_PHILOSOPHY.md`, `DESIGN_THESIS.md`, `TASK_TEMPLATE.md`.
- `tests/_audit_helpers/`.
- Any existing test file other than `tests/test_task009_solver_step_projection.py` (call site updated).

Do not introduce:

- Backward-compatibility shims accepting both old and new signatures.
- Deprecation warnings on the old signature. The old signature is gone.
- Item validation in `branch_selection` beyond `isinstance(branch, BranchSelection)`. The enum constraint is the validation.

## Completion report

Create:

```text
Build_Docs/Reports/task010_rebuild_projection/task010_rebuild_projection_summary.md
Build_Docs/Reports/task010_rebuild_projection/projection_rebuild_design.md
Build_Docs/Reports/task010_rebuild_projection/behavioral_deltas.md
```

`task010_rebuild_projection_summary.md` must include:

- Files created
- Files modified
- Files deleted (the four replaced test files)
- Red test slice command and result
- Green test slice command and result
- Full-suite command and result
- 010B and 010C audit re-run results
- Source audit results
- Updated 010C lineage corpus stats: number of distinct operation_ids, number of calibrated primitives, confirmation that `exact_quadratic_projection` is no longer in `calibrated_primitive_operations` (it's a composite now, with parents from typed inputs), and `branch_selection` is registered as a composite operation.
- Deviations, if any.
- Readiness note for the next rebuild task (whichever layer comes next in dependency order).

`projection_rebuild_design.md` must include:

- The contract of `branch_selection`: input type, output type, status semantics, validity, parents.
- The contract of `exact_quadratic_projection`: input types (both typed), output type, the active transition rule's role, the dispatch logic between selectable and nonselectable cases, the wrong-Python-type vs wrong-status separation.
- Justification for each behavioral delta from the prior implementation, against substrate principles.

`behavioral_deltas.md` must enumerate each behavior change between the old and new projection layer:

- Old: `exact_quadratic_projection(root_state, branch: str)`. New: `exact_quadratic_projection(root_state_result, branch_selection_result)`.
- Old: wrong status raises ProtocolViolationError. New: wrong status returns typed refusal.
- Old: `ProjectionResultValue.refusal: dict`. New: removed.
- Old: `ProjectionResultValue.flags: ProjectionFlags`. New: removed.
- Old: status mapping via `_SELECTABLE_PROJECTION_STATUS` / `_NONSELECTABLE_PROJECTION_STATUS` dicts. New: active `apply_status_transition(QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE, ...)`.
- Old: solver call `exact_quadratic_projection(root_state, model.branch)`. New: solver call wraps `model.branch` via `branch_selection(BranchSelection(model.branch))`.

Each delta gets a one-line principle justification.

## Acceptance criteria

Task 010-Rebuild-Projection is complete only when:

1. `src/lloyd_v4/projection/branches.py` exists with `BranchSelection`, `BranchSelectionValue`, the two protocols, the result alias, and the `branch_selection` composite.
2. `src/lloyd_v4/projection/exact_projection.py` is rebuilt with the new signature, no `ProjectionFlags`, no `refusal` dict on `ProjectionResultValue`, active transition rule dispatch, and typed-refusal handling for wrong-status inputs.
3. `src/lloyd_v4/projection/__init__.py` exports the new public names; `ProjectionFlags` is removed.
4. All call sites of `exact_quadratic_projection` in other layers are updated to use the new typed-branch signature. The grep `rg "exact_quadratic_projection\(" src/lloyd_v4 -n` shows every match using the new typed-input form.
5. The four old test files are deleted. The five new test files exist and exercise the rebuild's specification.
6. `tests/test_task009_solver_step_projection.py` is updated to use the new call form and passes.
7. All five new tests pass.
8. All four 010C audits and all four 010B audits pass.
9. Full test suite passes.
10. Source audits remain clean.
11. `exact_quadratic_projection` no longer appears in any `calibrated_primitive_operations` list in the manifest.
12. `branch_selection` appears in `projection.operations` in the manifest.
13. The lineage corpus shows `exact_quadratic_projection` instances with non-empty parents in every test that exercises it.
14. Reports are written under `Build_Docs/Reports/task010_rebuild_projection/`.
15. Readiness note for the next rebuild task is present in the summary report.

## Next-task readiness

When this task is complete and committed, evaluate which layer to rebuild next. The dependency graph determines candidates: anything whose only consumer-layer dependency is now `projection` (rebuilt) plus core + primitives is eligible. Likely candidates:

- `metrology`: parents are `core` and `primitives` only — no projection dependency. Could be next.
- Any layer that depends only on core + primitives + projection.

Before drafting the next rebuild task spec, do a fresh inspection of the candidate layer's source. Don't assume the issues will mirror the projection layer's. Each layer's geometry surfaces its own concerns.

Note any findings from this rebuild that should inform the next one — especially anything about how the active transition rule machinery worked in practice, any frictions with the wrong-Python-type vs wrong-status separation, and whether the "delete old tests, write new specification tests" pattern produced cleanly auditable behavioral deltas. Document these in `task010_rebuild_projection_summary.md` before drafting the next rebuild task.
