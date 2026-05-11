# Codex Task 010B: Layer Manifest Reconciliation and Closure Audits

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

Task 010B is the second task in the 010-series. It is an audit-and-documentation task. No source code changes are permitted in `src/lloyd_v4/`.

## Current verified baseline

Tasks 000 through 009A and 010A are complete.

010A added:

- Axioms 11 (Epistemic Stance Only) and 12 (Self-Derivation) in `Build_Docs/Architecture/AXIOMS.md`.
- `Build_Docs/Architecture/DISCOVERY_PHILOSOPHY.md`.
- `Build_Docs/Architecture/LAYER_MANIFEST.md` and `Build_Docs/Architecture/layer_manifest.json` declaring eight layers (`core`, `primitives`, `projection`, `metrology`, `branch`, `refinery`, `history`, `solver`) with parent relationships and provided concepts.
- `Build_Docs/Architecture/DESIGN_THESIS.md` extended with design commitments after the reality-check review.
- `Build_Docs/Agent_tasks/TASK_TEMPLATE.md`.
- 217 passing tests. Source-purity audits clean.

Inspection of 010A's deliverables surfaced the framing requirements for 010B:

- The Markdown manifest catalogues a richer "Provides" surface per layer than the JSON does. For `core` the Markdown lists status families, value/substrate types (`TypedResult`, `TypedRefusal`, `Validity`, `Conditioning`, `Provenance`), protocol types (`ProducerProtocol`, `ConsumerProtocol`, `ProtocolCheck`), transition types, and error/serialization utilities — plus the narrow `__all__` exports. The JSON only carries `status_families` and the narrow `__all__`. The JSON is declared normative; reconciling it to match the Markdown depth is a 010B prerequisite.
- Cross-layer imports in the substrate use submodule paths, not just `__init__.py` paths. Examples: `from lloyd_v4.core.result import TypedResult`, `from lloyd_v4.projection.exact_projection import ProjectionResultV4`. This is normal Python and respects the parent hierarchy, but it means the audit's primary structural check is **parent-relationship enforcement on full module paths**, not `__all__` membership.
- Status families are physically declared in `core/status.py` but semantically owned by different layers. `ProjectionStatus` is projection vocabulary; `BranchFingerprintStatus` is branch vocabulary. The current JSON manifest lists every family under `core`, which collapses semantic ownership into physical declaration site. The reconciled manifest should record semantic ownership so the layer-coherence audit has a meaningful source of truth.

## Task 010B goal

Make the layer manifest the normative, machine-readable, structurally-enforced source of truth for V4's layer architecture.

Three structural audits are added on top of the reconciled manifest:

1. **Cross-layer parent-relationship audit.** Every `from lloyd_v4....` import in `src/lloyd_v4/<layer>/` resolves to either `<layer>` itself (intra-layer) or a layer declared as a parent of `<layer>` in the manifest.
2. **Manifest export drift audit.** Every layer's manifest entry lists `all_exports` matching the layer's actual `__init__.py __all__`.
3. **Status-family-layer-coherence audit.** Each status family declared in the manifest as semantically owned by a particular layer is referenced (emitted, accepted, transitioned) only within that layer or its descendants.

Together these audits enforce Axiom 12 structurally rather than incidentally.

## Design principles for Task 010B

- Audit-and-documentation only. No source code changes in `src/lloyd_v4/`.
- The reconciled JSON manifest is the normative source of truth; the Markdown is updated only as needed to maintain parity.
- The audits are implemented as utilities under `tests/_audit_helpers/` and exercised by tests under `tests/test_task010b_*.py`.
- Audits work on the current codebase as-is. The codebase has been spot-checked: cross-layer parent relationships are honest, status families are referenced consistently with their semantic ownership, `__init__.py __all__` content matches what the manifest claims. The audits should pass without source changes.
- Existing tests must remain green. Full suite still passes.

## Primitive-sufficiency gate

This task introduces no new substrate concepts. It introduces:

- An audit-utilities module under `tests/_audit_helpers/`, which is test support, not substrate.
- An expanded JSON manifest schema, which is metadata about existing substrate, not new substrate behaviour.
- Three new test files exercising the audits.

Every concept the task uses (layers, status families, parent relationships, `__init__.py __all__`) is already provided by 010A's manifest or by the existing substrate. Gate satisfied.

## Required deliverables

### 1. Reconcile `Build_Docs/Architecture/layer_manifest.json`

Replace the current JSON manifest with a categorised structure that mirrors the Markdown's depth and adds explicit semantic ownership for status families.

The new schema has, per layer:

```json
{
  "name": "<layer>",
  "description": "<brief description>",
  "parents": ["<parent layer>", ...],
  "provides": {
    "status_families": [...],
    "value_types": [...],
    "protocol_types": [...],
    "transition_types": [...],
    "errors_and_utilities": [...],
    "operations": [...],
    "all_exports": [...]
  }
}
```

Categories are layer-appropriate. Not every layer has entries in every category. `core` has entries in every category. Most consumer layers have `value_types`, `protocol_types`, `transition_types`, `operations`, `all_exports` plus their owned `status_families` if any. Empty arrays are permitted; the structure is uniform across layers.

**Status family semantic ownership.** The current JSON lists all status families under `core`. The reconciled manifest distributes them as follows:

- `core`: `DomainStatus`, `StratumStatus`, `ValidityStatus`, `ConditioningStatus`, `ProtocolStatus`, `ProvenanceStatus` — substrate-cross-cutting families.
- `primitives`: `ProjectiveRatioStatus`, `QuadraticRootStatus`.
- `projection`: `ProjectionStatus`.
- `metrology`: `MetrologyStatus`.
- `branch`: `BranchFingerprintStatus`.
- `refinery`: `RefineryStatus`.
- `history`: `HistoryStatus`.
- `solver`: `SolverStatus`.

Status families are physically declared in `core/status.py`. The manifest captures *semantic* ownership distinct from physical declaration site. The status-family-layer-coherence audit uses semantic ownership as the source of truth.

**`all_exports`.** Each layer's `all_exports` list matches the layer's actual `__init__.py __all__` content exactly. The export drift audit verifies this.

**Other categories.** Populate by walking each layer's submodules and listing publicly importable names by category. The Markdown manifest already enumerates these for `core`; extend to all layers in the same style.

### 2. Update `Build_Docs/Architecture/LAYER_MANIFEST.md` if needed

Maintain Markdown parity with the reconciled JSON. The Markdown remains the human-readable rendering. Per-layer Markdown sections list the same categories the JSON declares, in the same order, with the same content.

### 3. Implement `tests/_audit_helpers/manifest.py`

A new test-support module providing the audit utilities. Required functions:

- `load_manifest() -> Manifest` — loads `Build_Docs/Architecture/layer_manifest.json` and returns a structured representation. The `Manifest` type is a dataclass or TypedDict carrying per-layer entries.
- `parents_for_layer(manifest, layer_name) -> tuple[str, ...]` — declared parents.
- `all_exports_for_layer(manifest, layer_name) -> tuple[str, ...]` — declared `all_exports`.
- `status_families_for_layer(manifest, layer_name) -> tuple[str, ...]` — declared semantic ownership of status families.
- `owning_layer_for_status_family(manifest, family_name) -> str` — reverse lookup; returns the layer name that semantically owns the family. Raises if the family is not declared.
- `descendants_of_layer(manifest, layer_name) -> frozenset[str]` — transitive set of layers that declare `layer_name` (transitively) as a parent. Used for the family-coherence audit.
- `extract_lloyd_v4_imports(source_path) -> tuple[str, ...]` — for a Python file, returns the list of `lloyd_v4.X.Y...` module paths imported via `from lloyd_v4.X.Y... import ...` or `import lloyd_v4.X.Y...`. The first segment after `lloyd_v4.` is the targeted layer. Submodule paths are preserved (e.g. `core.result`, not just `core`).
- `actual_all_exports(layer_name) -> tuple[str, ...]` — reads `src/lloyd_v4/<layer_name>/__init__.py`, parses `__all__`, returns the list as declared in source.
- `iter_layer_source_files(layer_name) -> Iterable[Path]` — yields every `.py` file under `src/lloyd_v4/<layer_name>/`, excluding `__pycache__`.
- `find_status_family_references(layer_name) -> Mapping[str, list[Path]]` — scans every Python file under `src/lloyd_v4/<layer_name>/` and finds references to status family names (e.g. `ProjectionStatus.PROJECTION_TRANSVERSE` or bare `ProjectionStatus`). Returns a mapping from family name to the list of files in `<layer_name>` that reference it.

Use Python's `ast` module for import extraction and `__all__` parsing. Do not use textual regex parsing for these — `ast` is the correct tool. Status-family references can be found via combined `ast` walking and string matching against the family name, since family names are unique identifiers in the codebase.

### 4. Implement `tests/test_task010b_manifest_completeness.py`

Verifies the JSON manifest has the expected structure:

- Loads `layer_manifest.json` successfully.
- Asserts the manifest has an entry for each of the eight layers (`core`, `primitives`, `projection`, `metrology`, `branch`, `refinery`, `history`, `solver`).
- For each entry, asserts the presence of `name`, `description`, `parents`, `provides`.
- Asserts each entry's `provides` has the categorised keys: `status_families`, `value_types`, `protocol_types`, `transition_types`, `errors_and_utilities`, `operations`, `all_exports`. Each is an array; empty arrays permitted.
- Asserts `core` has empty `parents` and every other layer has at least one parent.
- Asserts the parent graph is acyclic and each layer's declared parents form a subset of the previously-declared layers (the manifest is in topological order).

### 5. Implement `tests/test_task010b_export_drift.py`

For each layer, verifies the manifest's `all_exports` matches the layer's actual `__init__.py __all__`:

- For each of the eight layers, calls `actual_all_exports(layer_name)` and `all_exports_for_layer(manifest, layer_name)`.
- Asserts the two sets are equal.
- On mismatch, the failure message lists names declared in the manifest but missing from `__all__`, and names in `__all__` but missing from the manifest.

### 6. Implement `tests/test_task010b_cross_layer_parent_check.py`

Walks every Python file in `src/lloyd_v4/<layer>/` for each layer and verifies cross-layer imports respect the declared parent hierarchy:

- For each layer, iterate over every `.py` file via `iter_layer_source_files(layer_name)`.
- For each file, call `extract_lloyd_v4_imports(source_path)` to get the list of `lloyd_v4.X...` import paths.
- For each import path, extract the targeted-layer segment (the first identifier after `lloyd_v4.`).
- Assert the targeted-layer is either the importing file's own layer (intra-layer) or a layer in `parents_for_layer(manifest, importing_layer)` (cross-layer to parent).
- A cross-layer import to a non-parent layer is a violation. Collect all violations and assert the list is empty.
- The failure message lists each violation as `<file>:<line>: imports from <targeted_layer> but <importing_layer>'s parents are <parent_list>`.

The audit excludes `src/lloyd_v4/__init__.py` itself from per-layer processing — it is the package root, not a layer.

### 7. Implement `tests/test_task010b_status_family_layer_coherence.py`

Verifies status-family references respect semantic ownership:

- Loads the manifest.
- Builds the status-family ownership map: each declared status family → its owning layer.
- For each status family:
  - Determine the owning layer.
  - Compute the set of allowed layers: `{owning_layer} ∪ descendants_of_layer(manifest, owning_layer)`.
  - Walk every layer in the substrate. For each non-allowed layer, scan source files for references to the family name.
  - A reference in a non-allowed layer is a violation. Note: references in `core/status.py` itself are permitted because the family is physically declared there.
- Collect all violations and assert the list is empty.
- The failure message lists each violation as `<file>: references <family_name> but <referring_layer> is not <owning_layer> nor a descendant`.

The audit treats `core/status.py` as a special case: physical declaration of a status family there is not a reference for the purposes of this audit. Only references *outside* `core/status.py` count.

## Required tests

- `tests/test_task010b_manifest_completeness.py`
- `tests/test_task010b_export_drift.py`
- `tests/test_task010b_cross_layer_parent_check.py`
- `tests/test_task010b_status_family_layer_coherence.py`

Each test imports utilities from `tests/_audit_helpers/manifest.py`. The utilities are themselves not directly tested by 010B; their correctness is established by the four audit tests passing on the existing (known-coherent) codebase.

## Required commands

Run from repo root.

Red test slice (expected to fail before deliverables are written, since the JSON manifest is incomplete and the audit utilities don't exist):

```bash
python -m pytest tests/test_task010b_manifest_completeness.py tests/test_task010b_export_drift.py tests/test_task010b_cross_layer_parent_check.py tests/test_task010b_status_family_layer_coherence.py -q
```

Green test slice (expected to pass after deliverables):

```bash
python -m pytest tests/test_task010b_manifest_completeness.py tests/test_task010b_export_drift.py tests/test_task010b_cross_layer_parent_check.py tests/test_task010b_status_family_layer_coherence.py -q
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
- The off-the-shelf maths import audit. That is Task 010D.
- Operation_id-as-measurement. That is Task 010C′.
- The lineage audit (provenance tree walk). That is Task 010C.
- The `VocabularyStatus` family. That is Task 010E.
- The discovery harness scaffold. That is Task 010F.
- The synthesis protocol. That is Task 010G.
- A reorganisation of `core/status.py` to physically distribute status families across layers. The reconciled manifest captures semantic ownership; the source remains as-is.

Do not modify:

- Any source files in `src/lloyd_v4/`.
- `Build_Docs/Architecture/AXIOMS.md` (010A is the source of truth for axioms).
- `Build_Docs/Architecture/DISCOVERY_PHILOSOPHY.md`.
- `Build_Docs/Architecture/DESIGN_THESIS.md` (other than potential minor parity adjustments if the manifest reconciliation requires it; minimise these).
- `Build_Docs/Agent_tasks/TASK_TEMPLATE.md`.

Do not introduce:

- New status families.
- New protocols.
- New transition rules.
- New runtime dependencies.
- Manifest fields beyond those specified in deliverable 1.

## Heads-up for downstream tasks

During inspection of 010A's output, an `import math` was found in `src/lloyd_v4/branch/fingerprint.py:4`. This predates 010A and is not 010B's concern, but it is a violation of Axiom 11 that Task 010D's off-the-shelf-maths-import audit will surface. Whoever drafts 010D should expect a small cleanup pass to either justify the import as instrument-allowlisted (with a justification comment per Axiom 11's allowlist mechanism) or replace the math operations with substrate-derived equivalents. There may be other instances; 010D's full audit will identify all of them. 010B explicitly does not address this.

## Completion report

Create the following at task end:

```text
Build_Docs/Reports/task010B/task010B_summary.md
Build_Docs/Reports/task010B/manifest_reconciliation.md
Build_Docs/Reports/task010B/audit_results.md
```

`task010B_summary.md` must include:

- Files created
- Files modified
- Red test slice command and result
- Green test slice command and result
- Full-suite command and result
- Source audit commands and results
- Deviations, if any
- Readiness note for Task 010C

`manifest_reconciliation.md` must include:

- A summary of the manifest changes from 010A's version: which categories were added per layer, how status family semantic ownership was distributed, any discrepancies discovered between Markdown and JSON during reconciliation.
- For each of the eight layers, a brief summary of what each `provides` category contains.
- A note confirming `all_exports` per layer matches `__init__.py __all__` exactly.

`audit_results.md` must include:

- The result of each of the four audits on the current codebase.
- For the cross-layer parent check: total imports inspected, total cross-layer imports, total violations (expected zero).
- For the export drift check: per-layer `all_exports` match status (expected all match).
- For the status-family-coherence check: per-family number of references found in non-allowed layers (expected zero across all families).
- If any audit finds an unexpected violation that requires a one-time manifest correction (rather than a source change), document the correction here.

## Acceptance criteria

Task 010B is complete only when:

1. `Build_Docs/Architecture/layer_manifest.json` is reconciled to the categorised schema with per-layer entries for all eight layers and the seven `provides` categories.
2. Status-family semantic ownership in the JSON manifest is distributed across layers as specified in deliverable 1.
3. Each layer's `all_exports` in the manifest matches the layer's actual `__init__.py __all__`.
4. `Build_Docs/Architecture/LAYER_MANIFEST.md` retains parity with the reconciled JSON.
5. `tests/_audit_helpers/manifest.py` exists and provides the required functions.
6. `tests/_audit_helpers/__init__.py` exists (package marker).
7. All four required test files exist and pass on the current codebase.
8. The cross-layer parent check finds zero violations.
9. The export drift check finds zero per-layer mismatches.
10. The status-family-coherence check finds zero non-allowed references.
11. Full test suite passes (no existing tests broken).
12. Source audits remain clean.
13. No source code in `src/lloyd_v4/` has been modified.
14. Reports are written under `Build_Docs/Reports/task010B/`.
15. Readiness note for Task 010C is present in the summary report.

## Task 010C readiness

When this task is complete and committed, the next task is **Task 010C — Provenance-based lineage audit**. Before drafting `codex_task010C.md`, re-evaluate the planned 010C scope against what 010B actually surfaced. Specifically:

- 010B's audit utilities under `tests/_audit_helpers/` may provide useful infrastructure for 010C's lineage walk (the `ast`-based import extraction in particular). 010C's spec should reference these utilities and extend them rather than duplicating effort.
- If 010B's status-family-coherence audit found any unexpected references that required manifest corrections, 010C's lineage audit should be aware of those corrections so the provenance walk doesn't re-surface them as orphan operations.
- The reconciled manifest from 010B is the source of truth for 010C's "is this `operation_id` registered" check (operation registration is the manifest's `operations` category per layer).
- Inspection during 010B may have surfaced findings that affect 010C's scope. Note these in the `task010B_summary.md` readiness section before drafting `codex_task010C.md`.
