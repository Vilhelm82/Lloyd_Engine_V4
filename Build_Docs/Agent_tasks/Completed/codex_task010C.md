# Codex Task 010C: Provenance-Based Lineage Audit

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

Task 010C is the third task in the 010-series. It is an audit-and-documentation task. No source code changes are permitted in `src/lloyd_v4/`.

## Current verified baseline

Tasks 000 through 009A, 010A, and 010B are complete.

010B reconciled `Build_Docs/Architecture/layer_manifest.json` to a categorised schema with seven `provides` categories per layer (`status_families`, `value_types`, `protocol_types`, `transition_types`, `errors_and_utilities`, `operations`, `all_exports`). Status-family ownership was distributed across layers semantically. Three structural audits established and passing:

- Cross-layer parent-relationship check: 113 cross-layer imports inspected, 0 violations.
- Manifest export drift check: 0 mismatches across all 8 layers.
- Status-family layer-coherence check: 0 non-allowed references across all 14 families.

`tests/_audit_helpers/manifest.py` is established and provides manifest loading, layer walking, and AST-based `lloyd_v4` import extraction utilities. The full test suite passes (numbers per the 010B summary).

010B's findings simplify 010C in three ways and add one nuance:

- `_audit_helpers/manifest.py` provides reusable infrastructure for layer walking and AST inspection. 010C extends it with a sibling `lineage.py` rather than duplicating the import-extraction logic.
- The categorised manifest is the natural place to declare which operation_ids legitimately terminate provenance chains. 010C adds `calibrated_primitive_operations` per layer and (if needed) `internal_operations`.
- Cross-layer parent integrity is verified honest. 010C's lineage walk should produce clean cross-family transitions in the existing codebase modulo any minor manifest-completeness findings.
- Tests import audit helpers as `_audit_helpers.manifest` rather than `tests._audit_helpers.manifest` because `tests/` is not a package during pytest collection. 010C's new tests follow the same convention.

## Task 010C goal

Walk every typed result the test suite produces, follow `provenance.parents`, and verify three structural properties of every chain:

1. **Termination.** Every chain terminates in an operation declared as a calibrated primitive in the manifest.
2. **Operation registry.** Every `operation_id` encountered in any chain is declared somewhere in source — either as a public operation in a layer's manifest entry, as an internal operation, or as a calibrated primitive.
3. **Transition justification.** Every cross-family status transition between a parent and child node has a registered `StatusTransitionRule`.

The audits run on a runtime corpus of `TypedResult` instances captured during a pytest session via an autouse session-scoped fixture. The corpus is everything the test suite produces; the audits walk it.

This task introduces no new substrate behaviour. The substrate's existing `Provenance.parents` mechanism, existing `StatusTransitionRule` registry, and existing layer-manifest infrastructure are all the audit needs.

## Design principles for Task 010C

- Audit-and-documentation only. No source code changes in `src/lloyd_v4/`.
- The audit operates on runtime-collected `TypedResult` instances, not on synthetic test fixtures. The corpus is whatever the test suite produces.
- Operation_ids encountered in chains but not in the manifest are *manifest-completeness findings*, not violations. The task adds them to the manifest's `internal_operations` category for their declaring layer. Genuine violations (operation_ids that appear in chains but cannot be found anywhere in source) are reported as audit failures.
- Existing tests must remain green. The autouse collector fixture must not perturb the behaviour of any existing test.
- The audit's character is bounded by the current substrate: `operation_id` is a declared string, not a measured fingerprint. Task 010C′ will replace declarative operation_ids with structural measurements; at that point this audit's correctness becomes structural rather than registry-based. 010C verifies the substrate at its current state.

## Primitive-sufficiency gate

010C uses only existing substrate concepts. The runtime collector reads the substrate's existing `TypedResult` and `Provenance` types. The lineage walker uses existing `Provenance.parents` traceability. The transition-justification audit uses existing `StatusTransitionRule` registry exposed via each layer's `__init__.py`.

The two new manifest categories (`calibrated_primitive_operations`, `internal_operations`) are metadata about existing substrate operations, not new operations. The runtime collector mechanism uses Python's standard library only (no external dependencies).

Gate satisfied. No prior task is required.

## Required deliverables

### 1. Extend `Build_Docs/Architecture/layer_manifest.json`

Add two new categories to each layer's `provides`:

- `calibrated_primitive_operations` — operation_ids that legitimately terminate a provenance chain. A calibrated primitive is an operation that constructs a `TypedResult` without consuming any `TypedResult` as input (its provenance has empty `parents`). Currently this set is small: `projective_ratio` and `stratified_quadratic_roots` from `primitives`. Other layers' `calibrated_primitive_operations` are likely empty arrays at task start; populate during the audit if discovery finds otherwise.
- `internal_operations` — operation_ids declared in source within the layer that are not part of the layer's public `__all__`. These are operations used by the layer internally that may emit `TypedResult` instances visible in provenance chains. Populated during the audit based on findings; likely empty at task start for most layers.

The schema becomes nine `provides` categories: `status_families`, `value_types`, `protocol_types`, `transition_types`, `errors_and_utilities`, `operations`, `calibrated_primitive_operations`, `internal_operations`, `all_exports`. Empty arrays are permitted; structure remains uniform.

`Build_Docs/Architecture/LAYER_MANIFEST.md` is updated to maintain parity.

### 2. Implement `tests/_audit_helpers/lineage.py`

A new test-support module that provides the runtime collector and lineage-walking utilities. Required functions and infrastructure:

- A module-level list `_collected_instances: list[TypedResult]` that accumulates every `TypedResult` constructed during a pytest session.
- `install_collector()` — monkey-patches `TypedResult.__post_init__` (or equivalent construction hook for the frozen-slots dataclass) to append `self` to `_collected_instances` after the original `__post_init__` runs. Idempotent: calling it twice is safe and does not double-collect. The patch must preserve the original `__post_init__` semantics exactly.
- `collected_instances() -> tuple[TypedResult, ...]` — returns a snapshot of the collected list.
- `build_trace_id_index(instances) -> dict[str, TypedResult]` — builds an index mapping `provenance.trace_id` to the instance.
- `walk_chain(instance, index) -> Iterable[TypedResult]` — yields the instance, then its parents in topological order via `provenance.parents` trace_id resolution. Detects cycles and raises if any chain has one (cycles are themselves a structural violation).
- `chain_terminals(instance, index) -> tuple[TypedResult, ...]` — returns the terminal nodes of `instance`'s chain (nodes whose `provenance.parents` is empty). A chain may have multiple terminals if the consumer fanned across multiple primitives.
- `family_of(instance) -> type[StrEnum]` — returns the status family enum class of the instance's status.
- `operation_id_of(instance) -> str` — returns the instance's `provenance.operation_id`.
- `all_operation_ids_in_corpus(instances) -> frozenset[str]` — every operation_id appearing in any chain across the corpus.
- `static_operation_id_registry() -> Mapping[str, str]` — by AST-scanning every Python file in `src/lloyd_v4/`, finds every literal string passed as `operation_id=` to a `Provenance(...)` constructor (or equivalent construction). Returns a mapping from operation_id literal to the layer that declares it. Use existing `_audit_helpers/manifest.py` utilities for layer walking.
- `manifest_operation_id_registry(manifest) -> Mapping[str, str]` — every operation_id declared in any layer's `operations`, `calibrated_primitive_operations`, or `internal_operations`. Returns mapping from operation_id to declaring layer.
- `transition_rule_registry() -> dict[tuple[type, type], list[StatusTransitionRule]]` — by walking each layer's `__init__.py` exports, collects every `StatusTransitionRule` and indexes them by `(input_status_family, output_status_family)`. The same family pair may have multiple rules; the audit accepts any matching rule.

### 3. Create or extend `tests/conftest.py`

If `tests/conftest.py` does not exist, create it. If it does, extend it.

Required: a session-scoped autouse fixture that installs the collector before any tests run:

```python
import pytest
from _audit_helpers.lineage import install_collector

@pytest.fixture(scope="session", autouse=True)
def _audit_lineage_collector():
    install_collector()
    yield
```

The collector remains installed for the duration of the session and the collected list is read by the audit tests at session-end.

The fixture must not affect any existing test. The collector's only effect on `TypedResult` construction is to append the new instance to a list — the constructed instance and its behaviour are unchanged.

### 4. Implement `tests/test_task010c_lineage_terminates_in_primitive.py`

Verifies every chain in the captured corpus terminates in a calibrated primitive operation:

- Loads the manifest. Builds the union set of `calibrated_primitive_operations` across all layers.
- Reads the captured corpus via `collected_instances()`.
- Builds the trace_id index.
- For each captured instance, computes its `chain_terminals()`.
- For each terminal, verifies its `operation_id` is in the calibrated-primitives set.
- Collects violations and asserts empty.
- Failure message lists each violation as `<terminal trace_id>: operation_id <id> is not a calibrated primitive`.

The test must be collected after the rest of the suite has run so the corpus is populated. Either via pytest's `pytest_collection_modifyitems` to ensure ordering, or by placing the audit in a separate test file that pytest naturally collects last alphabetically (010C tests sort after the rest of the 010 series; further tests in this file should be named to land last in the session).

### 5. Implement `tests/test_task010c_no_unregistered_operations.py`

Verifies every operation_id in the corpus is declared somewhere:

- Loads the manifest. Builds the union of declared operation_ids from `operations`, `calibrated_primitive_operations`, and `internal_operations` across all layers.
- Loads the static AST registry via `static_operation_id_registry()`. Every operation_id that appears as a literal in source.
- Builds the runtime corpus's set of operation_ids via `all_operation_ids_in_corpus()`.
- Computes the set of operation_ids in the corpus that are not in the manifest.
- For each such operation_id, checks the AST registry. If found there, this is a *manifest-completeness finding*: the operation_id is declared in source but missing from the manifest. Add it to the manifest's `internal_operations` for the declaring layer.
- After the manifest is updated (during task work, not during test execution), the test re-runs and asserts all operation_ids in the corpus are in the manifest.
- Operation_ids in the corpus that are *not* in the AST registry are genuine violations: operation_id used at runtime but not declared anywhere in source. The test asserts this list is empty. (This should not occur in a healthy substrate.)

### 6. Implement `tests/test_task010c_cross_family_transitions_justified.py`

Verifies cross-family transitions in chains have registered rules:

- Loads the transition rule registry via `transition_rule_registry()`.
- For each captured instance, walks its chain.
- For each parent-child edge in the chain, computes `family_of(parent)` and `family_of(child)`.
- If the families differ, looks up the `(parent_family, child_family)` pair in the registry. The lookup must return at least one rule.
- If no rule exists for the family pair, this is a violation. Collects all violations and asserts empty.
- Failure message lists each violation as `<parent trace_id> (<parent_family>) → <child trace_id> (<child_family>): no registered StatusTransitionRule`.

### 7. Implement `tests/test_task010c_no_chain_cycles.py`

Verifies no chain in the corpus has a cycle:

- For each captured instance, attempts `walk_chain()`.
- `walk_chain` is implemented to raise on cycle detection.
- The test catches any cycle exception and reports the trace_id at which the cycle was detected.
- Asserts no cycles are found across the entire corpus.

This test would normally be implicit (the substrate's design forbids cycles), but explicitly testing it catches any future regression where parent trace_ids are accidentally set in a way that forms a loop.

## Required tests

- `tests/test_task010c_lineage_terminates_in_primitive.py`
- `tests/test_task010c_no_unregistered_operations.py`
- `tests/test_task010c_cross_family_transitions_justified.py`
- `tests/test_task010c_no_chain_cycles.py`

Each test imports from `_audit_helpers.lineage` and `_audit_helpers.manifest`.

## Required commands

Run from repo root.

Red test slice (expected to fail before deliverables are written):

```bash
python -m pytest tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_cross_family_transitions_justified.py tests/test_task010c_no_chain_cycles.py -q
```

Green test slice (expected to pass after deliverables and any necessary manifest-completeness updates):

```bash
python -m pytest tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_cross_family_transitions_justified.py tests/test_task010c_no_chain_cycles.py -q
```

Full suite:

```bash
python -m pytest tests -q
```

Source audits (expected to remain clean since no source changes are made):

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance|confidence_score|weighted_score|smoothing|hysteresis|interpolate|extrapolate" src/lloyd_v4 -n
rg -i "lloyd_core|lloyd_core_nvar|lloyd_decomposition|hyperdual|halley|multi_start|route_score" src/lloyd_v4 -n
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

Each audit must return no matches.

## Non-Goals

Do not implement:

- Any source code changes in `src/lloyd_v4/`.
- Operation_id-as-measurement (the substrate refactor that converts declared operation_id strings into measured call-tree fingerprints). That is Task 010C′. 010C operates on declared operation_ids as they currently exist.
- The off-the-shelf maths import audit. That is Task 010D.
- The `VocabularyStatus` family. That is Task 010E.
- The discovery harness scaffold. That is Task 010F.
- The synthesis protocol. That is Task 010G.
- A reorganisation of `core/status.py` or any substrate file.

Do not modify:

- Any source files in `src/lloyd_v4/`.
- `Build_Docs/Architecture/AXIOMS.md`.
- `Build_Docs/Architecture/DISCOVERY_PHILOSOPHY.md`.
- `Build_Docs/Architecture/DESIGN_THESIS.md`.
- `Build_Docs/Agent_tasks/TASK_TEMPLATE.md`.
- `tests/_audit_helpers/manifest.py` beyond minor additions or compatibility tweaks if needed by the lineage utilities. The 010B manifest functions remain unchanged in behaviour.

Do not introduce:

- New status families.
- New protocols.
- New transition rules.
- New runtime dependencies (standard library only).
- A second collector mechanism. The single autouse session fixture in `tests/conftest.py` is the only collection path.

## Note on audit character after 010C′

010C verifies operation_id integrity in the current substrate, where `operation_id` is a string the author assigns to `Provenance` at construction. The audit's check is: every declared operation_id is registered in source (manifest or AST scan) and every chain terminates in a declared calibrated primitive.

After Task 010C′ lands, `operation_id` becomes a measurement of the actual call tree, not an author-assigned string. At that point:

- The manifest's `calibrated_primitive_operations` becomes the authoritative set of axiomatic operation_ids (the substrate's calibration constants).
- The AST registry of declared operation_id strings becomes obsolete — operation_ids are no longer literals authors write; they are derived from call trees.
- The lineage audit's correctness becomes structural rather than registry-based. Non-substrate call trees physically cannot construct `TypedResult` instances; the audit's "every chain terminates in a primitive" check becomes a tautology because the substrate enforces it at construction time.

010C is the audit at the current substrate level. It will need light revision after 010C′ to reflect the structural shift, but the runtime collection mechanism and the lineage-walking utilities remain useful.

## Completion report

Create the following at task end:

```text
Build_Docs/Reports/task010C/task010C_summary.md
Build_Docs/Reports/task010C/lineage_corpus.md
Build_Docs/Reports/task010C/manifest_completeness_findings.md
```

`task010C_summary.md` must include:

- Files created
- Files modified
- Red test slice command and result
- Green test slice command and result
- Full-suite command and result
- Source audit commands and results
- Deviations, if any
- Readiness note for Task 010C′

`lineage_corpus.md` must include:

- Total number of `TypedResult` instances captured during the test session.
- Total number of distinct operation_ids encountered.
- Total number of distinct status families encountered.
- Per-layer breakdown of how many captured instances had `operation_id` declared by that layer.
- A summary of the longest chain depth observed and a representative example chain.
- Cycle audit result (expected: zero cycles).

`manifest_completeness_findings.md` must include:

- The list of operation_ids found in the runtime corpus that were not in the 010A/010B manifest.
- For each, the declaring layer (from AST scan).
- The corresponding manifest update made: which operation_ids were added to which layer's `internal_operations` or `calibrated_primitive_operations`.
- A statement confirming all operation_ids in the corpus are now in the manifest after the updates.
- A statement confirming no operation_ids in the corpus were untraceable in source (which would be a genuine violation rather than a manifest-completeness finding).

## Acceptance criteria

Task 010C is complete only when:

1. `Build_Docs/Architecture/layer_manifest.json` has `calibrated_primitive_operations` and `internal_operations` categories populated for every layer (empty arrays where appropriate).
2. `Build_Docs/Architecture/LAYER_MANIFEST.md` retains parity with the JSON.
3. `tests/_audit_helpers/lineage.py` exists with the required functions and the runtime collector mechanism.
4. `tests/conftest.py` exists or is extended with the session-scoped autouse `_audit_lineage_collector` fixture.
5. The collector preserves `TypedResult.__post_init__` semantics exactly; existing tests pass without modification.
6. All four required test files exist and pass on the current codebase, possibly after manifest-completeness updates.
7. The lineage-termination audit confirms every chain terminates in a calibrated primitive operation.
8. The operation-registry audit confirms every operation_id in the corpus is in the manifest after any necessary manifest-completeness updates.
9. The cross-family transition audit confirms every cross-family transition has a registered `StatusTransitionRule`.
10. The cycle audit confirms no chains contain cycles.
11. Full test suite passes (no existing tests broken).
12. Source audits remain clean.
13. No source code in `src/lloyd_v4/` has been modified.
14. Reports are written under `Build_Docs/Reports/task010C/`.
15. Readiness note for Task 010C′ is present in the summary report.

## Task 010C′ readiness

When this task is complete and committed, the next task is **Task 010C′ — Operation_id as measured trace**. This is a substrate refactor that converts `operation_id` from an author-assigned string into a structural fingerprint of the actual call tree. Before drafting `codex_task010C_prime.md`, re-evaluate the planned 010C′ scope against what 010C surfaced:

- The list of operation_ids encountered in the runtime corpus (from `lineage_corpus.md`) is the empirical set of operations the substrate currently emits. 010C′'s call-tree measurement must produce equivalent operation_ids for at least the calibrated primitives, and consistent fingerprints for composite operations across runs.
- The set of `calibrated_primitive_operations` in the manifest after 010C completes is the candidate set for 010C′'s axiomatic-primitive operation_id constants. Any operation_ids in `internal_operations` will become composite fingerprints derived from call trees.
- `tests/_audit_helpers/lineage.py`'s runtime collector mechanism is reusable in 010C′ for verifying that the structural fingerprints produced by the new substrate match the operation_ids the audit currently sees (transition validation across the refactor).
- 010C′'s test for "non-terminating call tree refused" can use the same collector to verify that synthetic non-substrate call trees produce no `TypedResult` instances at all (the structural impossibility of covert import).

Note these in `task010C_summary.md` before drafting `codex_task010C_prime.md`.
