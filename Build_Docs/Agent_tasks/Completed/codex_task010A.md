# Codex Task 010A: Document the Principles

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

Task 010A is the first task in the 010-series. It is a documentation-only task. No source code changes are permitted.

## Current verified baseline

Tasks 000 through 009A are complete. The substrate has:

- M0 typed substrate with statuses, validity, conditioning, provenance, typed results, protocol contracts, status calculus, strict serialization, and core errors.
- Layer-1 primitives `ProjectiveRatio` and `StratifiedQuadraticRoots`.
- `ProjectionResultV4` and the exact quadratic projection protocol.
- Metrology layer with `b_k` noise floor and `K_q` proxy calibration.
- Generic `TypedResult` with status families, named transition rules, and protocol family rejection.
- `BranchFingerprint` with slope-flow comparison and K_q slope stability.
- Refinery with status-preservation transition rules and same-geometry-lower-slag gating.
- History layer with status-event recording and stable-trace protocol.
- `TypedProjectionSolver` with full scenario coverage from Task 009A.
- 213 passing tests. Source-purity audits clean.

## Task 010A goal

Get the design principles articulated during the V4 reality-check review onto disk so subsequent tasks (010B through 010G and beyond) can be written against them and future Codex / Claude / human sessions can be pushed back against them.

The principles to document:

1. **Discovery-mode primacy.** The engine is an agnostic workshop, not an assembly line. No consumer-shaped scoping. The engine is pointed at mathematical reality and observations are accumulated; domain use cases are inevitable consequences of substrate purity, not design targets.
2. **Epistemic-stance-only commitments.** No off-the-shelf maths or physics is imported as substrate content. Constants, named theorems, and standard formalisms are domain articulations, not building blocks.
3. **Self-derivation.** Every layer derives from its parent layers. A higher layer that requires a concept absent from its parents must halt; the parent layer is extended honestly, then the higher layer rebuilds. No upward smuggling.
4. **Vocabulary-failure detection.** The engine must have a typed way to report *"this structure is outside my current vocabulary"* rather than silently collapsing unfamiliar structure into the closest familiar stratum.
5. **Provenance fields measured, not declared.** Operation_id and similar provenance fields are read from the call tree at result construction, not assigned by the author.
6. **Synthesis as substrate-evolution oracle.** The engine may use existing mathematical objects as navigation targets. Synthesis attempts produce typed observations whose discovery-layer classification prescribes the appropriate kind of next substrate work.
7. **The engine has no failures, only structure-revealing observations of varying refinement.** Every artifact a synthesis attempt produces is informative.

Task 010A documents principles 1, 2, 3, and the framing that supports the rest. Principles 4 through 7 are documented in their own implementation tasks (010E for vocabulary failure, 010C′ for measured operation_id, 010G for synthesis and discovery layers).

## Design principles for Task 010A

- Documentation only. No source code changes. No new tests of source behaviour.
- Existing architecture documents are extended, not rewritten, except where explicitly noted.
- The new documents follow the structure of existing architecture documents in `Build_Docs/Architecture/` (statement, rationale, what V4 forbids, what V4 must represent instead — for axioms; structured prose for thesis-style docs).
- The layer manifest is machine-readable. Either embed structured sections parseable by regex or add a sibling `layer_manifest.json` file with the same content normatively.
- The full test suite must remain green at task completion. All existing tests pass without modification.

## Primitive-sufficiency gate

This task introduces no new substrate concepts. Every concept it documents (axioms, layer manifest, discovery philosophy, task template) is metadata about the existing substrate, not new substrate behaviour. The primitive-sufficiency gate is satisfied trivially: no parent-layer concepts are required because the task is doc-only.

## Required deliverables

### 1. Extend `Build_Docs/Architecture/AXIOMS.md`

Add Axiom 11 and Axiom 12 after the existing Axiom 10. Format follows the existing axioms (statement, rationale, V4 forbids, V4 must represent instead).

#### Axiom 11 — Epistemic Stance Only

**Statement.** V4 commits at the level of how observation works, not at the level of what is observed. Imported constants, named theorems, and off-the-shelf formalisms are domain articulations, not substrate.

**Rationale.** Each formalism is one specific articulation of underlying mathematical territory. Importing it brings its vocabulary, its operations, and its tacit claim to be the natural articulation. The room behind that articulation closes the moment the formalism is brought in as substrate. The Gamma Function is one extension of the factorial to the complex plane; Hadamard's gamma is another. Bohr–Mollerup uniqueness picks one. Building Γ into the substrate forecloses on every other extension that V4 might independently observe to fit a given territory better.

**V4 forbids.** Imports of named mathematical content (`math`, `cmath`, `numpy.special`, `scipy.constants`, `scipy.special`, `sympy`, `mpmath`); hardcoded mathematical constants (`π`, `τ`, `e`, `γ`, `ζ`, `golden_ratio`); use of named theorems, named functions, or named equations as substrate building blocks.

**V4 must represent instead.** Constants and named objects as observables — values the engine measures or synthesises through its own primitives, with full provenance lineage to substrate operations. Existing maths may serve as navigation targets through the synthesis protocol, never as substrate content.

#### Axiom 12 — Self-Derivation

**Statement.** Every layer derives from its parent layers. A higher layer that requires a concept absent from its parents must halt; the parent layer is extended honestly, then the higher layer rebuilds.

**Rationale.** Without enforced layered derivation, higher layers can mint novel concepts ad hoc, and the substrate becomes a collection of jumps and forced rearrangements rather than a coherent structure where each level is built from below. The discipline of "speaking the same language" across layers requires that every concept used at any layer trace back to a primitive through registered transitions.

**V4 forbids.** Concepts minted at consumer layers that do not exist in any parent layer; transition rules that compose primitives without registered lineage; cross-layer references that bypass declared parent relationships.

**V4 must represent instead.** Layer manifests declaring provided concepts and parent layers; structural lineage from primitives to consumers via registered transition rules; descend-extend-return procedure when a higher layer's needs exceed parent provisions.

### 2. New `Build_Docs/Architecture/DISCOVERY_PHILOSOPHY.md`

A new architecture document. Sections:

#### Purpose

Articulates the agnostic-workshop framing for V4: the engine is built for clean operation at the primitive level, with use cases falling out as inevitable consequences of substrate purity rather than as design targets.

#### The agnostic workshop

The shovel principle: a shovel is not designed for trench-digging or sand-shovelling specifically; it is designed for clean operation as a leverage tool with a flat blade and an angled handle, and the work it can do is a corollary of that geometry. Designing the shovel for trenches makes it worse at sand. The same principle applies to V4: every primitive that is bent toward a specific consumer is paid for silently by every other use that gets compromised in service of that bend.

#### The dark room

The Gamma Function metaphor. Walking into a dark room and discovering the Gamma Function does not mean the room has been explored; it means one object in the room has been identified. Closing the room behind that object — by building Γ into the substrate — forecloses on every other articulation of complex factorials the room might have contained. The discipline V4 requires is to keep the room open by refusing to import the artifacts found in it as substrate, and instead to derive them as observables through the engine's own primitives.

#### The engine as discovery instrument

V4's role is to produce typed observations about mathematical structure, not to deliver answers about specific domains. The synthesis protocol (formalised separately) is one workflow within this framing: the engine is pointed at landmarks and produces typed observations about its own ability to reach them. The harness is the broader infrastructure for free-roaming observation — pointing the engine at mathematical structures and accumulating what falls out.

#### No failures, only observations of varying refinement

The engine produces no failures. Every artifact a synthesis attempt or observation campaign produces is informative. A closed synthesis is a refined observation. A typed gap is a less refined observation that nevertheless characterizes the gap. A multi-solution gap is a still-less-refined observation that characterizes substrate over-generalization. An axiomatic conflict is rarer still and characterizes the substrate's own commitments. Each level prescribes a different kind of substrate work; none is a failure mode.

This principle is the recursive completion of every other principle in V4. The substrate measures rather than declares (operation_id-as-measurement, axioms 11–12). The discovery process is vertical and self-terminating (synthesis discovery layers). The planning process is incremental and assumption-tracking (commit one task, evaluate evidence, commit next). At every level, the same discipline: do not pre-load answers; let the work produce them and commit only what has been verified.

#### Relationship to consumers

The agnostic workshop produces no consumers as design targets. Domain consumers — bearing diagnostics, aerospace tooling, betting scanners, anything else — are downstream applications of substrate purity, not requirements that shape the substrate. A V4 build that has been shaped by a particular consumer's needs has compromised its agnosticism; a V4 build whose substrate has been kept pure produces consumers as inevitable corollaries. The first domain consumer is deferred indefinitely until discovery-mode observation campaigns produce evidence about which consumer benefits most directly from V4 typed inputs.

### 3. New `Build_Docs/Architecture/LAYER_MANIFEST.md`

Machine-readable layer manifest. Each layer entry includes:

- Layer name
- Brief description
- Parent layers (declared explicitly)
- Provided concepts: status families, protocols, value types, transition rules, public operations

Required entries (one per layer currently in `src/lloyd_v4/`):

- `core` — substrate. No parent layers. Provides: status families (`DomainStatus`, `StratumStatus`, `ValidityStatus`, `ConditioningStatus`, `MetrologyStatus`, `ProtocolStatus`, `ProvenanceStatus`, plus all primitive-and-consumer-layer status families enumerated in `core/status.py`), `TypedResult`, `Provenance`, `ProducerProtocol`, `ConsumerProtocol`, `StatusTransitionRule`, `TransitionDisposition`, `StatusTransitionOutcome`, error classes, serialization utilities.
- `primitives` — Layer 1. Parent: `core`. Provides: `ProjectiveRatio` (with statuses, protocols, transition rules, value/result types, and operations), `StratifiedQuadraticRoots` (with statuses, protocols, transition rules, value/result types, and operations).
- `projection` — Layer 1.5 (consumer of primitives). Parents: `core`, `primitives`. Provides: `ProjectionResultV4`, `exact_quadratic_projection`, `ProjectionFlags`, `ProjectionResultValue`, projection protocols and transition rules.
- `metrology` — Layer 2. Parents: `core`, `primitives`. Provides: `b_k` noise floor evidence, limit-of-detection classification, `K_q` proxy calibration, calibration validity protocols and transition rules, all metrology value/result types.
- `branch` — Layer 2 (depends on metrology and projection). Parents: `core`, `primitives`, `projection`, `metrology`. Provides: `BranchFingerprint`, slope-flow comparison, `K_q` slope stability, branch-fingerprint composition rules and transition rules, all branch value/result types.
- `refinery` — Layer 2 (depends on branch). Parents: `core`, `primitives`, `projection`, `metrology`, `branch`. Provides: typed result snapshots, slag vectors, refinery decisions, status-preservation transition rules, refinery protocols.
- `history` — Layer 2 (depends on refinery). Parents: `core`, `primitives`, `projection`, `metrology`, `branch`, `refinery`. Provides: status events, status traces, history transitions, stable-trace protocols and transition rules.
- `solver` — Layer 3 (consumer). Parents: `core`, `primitives`, `projection`, `metrology`, `branch`, `refinery`, `history`. Provides: `TypedProjectionSolver`, solver step and run protocols, solver transition rules, solver value/result types.

Each layer entry must list the names that the layer's `__init__.py` exports via `__all__`. The list is normative — Task 010B's audits will verify the manifest against the actual exports.

The manifest may be authored as structured Markdown (with predictable headings parseable by regex) or as Markdown plus a sibling `layer_manifest.json` file. If JSON is included, it is the normative source and the Markdown is a human-readable rendering.

### 4. Update `Build_Docs/Architecture/DESIGN_THESIS.md`

Extend the existing thesis to reference the new principles. Add a new section near the end (after "Initial Primitive Order"), titled "Design Commitments After the Reality-Check Review". The section should:

- Cite Axioms 11 and 12 by reference and include one-sentence summaries of each.
- Cite the agnostic-workshop framing from `DISCOVERY_PHILOSOPHY.md`.
- Cite the structural-measurement principle for provenance fields (which will be implemented in Task 010C′).
- Note that the discovery-layer hierarchy and synthesis protocol are formalised in `SYNTHESIS_PROTOCOL.md` (which will be created in Task 010G; for now, mark it as "to be created in Task 010G").
- Note that the engine produces no failures — only structure-revealing observations of varying refinement — and reference `DISCOVERY_PHILOSOPHY.md` for the elaboration.

The existing content of `DESIGN_THESIS.md` (Layer Architecture, Initial Primitive Order, the D⊕S=P relation) is preserved verbatim. The new section is additive.

### 5. New `Build_Docs/Agent_tasks/TASK_TEMPLATE.md`

A new document that codifies the structure every future codex_task spec must follow. Sections:

- **Repository** — where to work; warnings about V3, V1 files.
- **Current Verified Baseline** — what is in place when this task starts.
- **Task Goal** — what this task accomplishes.
- **Design Principles** — task-specific constraints.
- **Primitive-Sufficiency Gate** — the explicit demonstration that every concept the task requires is provided by parent layers, or a list of separate prior tasks needed to extend the parents first.
- **Required Deliverables** — specific files, modules, statuses, protocols, transition rules.
- **Required Tests** — specific test files, with one-sentence descriptions of what each verifies.
- **Required Commands** — bash commands for running the task's test slice, the full suite, and source audits.
- **Non-Goals** — things this task explicitly does not do.
- **Completion Report** — what to write at end of task in `Build_Docs/Reports/taskNNN/`.
- **Acceptance Criteria** — numbered list of conditions for task completion.

The document also includes a short prose preamble explaining that:

- Tasks are committed one at a time.
- After each task is complete, the next task's spec is re-evaluated against the evidence the completed task produced.
- The task series plan in `Build_Docs/Agent_tasks/Task_010_Series_Plan.md` is a target trajectory, not a commitment sequence.
- The primitive-sufficiency gate is the structural enforcement of Axiom 12 at task-commit time.

The TASK_TEMPLATE.md does not replace the existing codex_taskNNN.md files. It applies to tasks created from this point onward.

## Required tests

All tests are documentation-presence tests. No source behaviour is being tested.

### `tests/test_task010a_axioms_present.py`

Verifies that `Build_Docs/Architecture/AXIOMS.md` contains:

- A section header for "Axiom 11" with the substring "Epistemic Stance Only" in or near the header.
- Within the Axiom 11 section, the four required subsections: a Statement, a Rationale, a "V4 forbids" subsection, and a "V4 must represent instead" subsection.
- A section header for "Axiom 12" with the substring "Self-Derivation" in or near the header.
- Within the Axiom 12 section, the same four subsections.

Test by reading the file as text and asserting the presence of the expected headings and subsections.

### `tests/test_task010a_principle_docs_present.py`

Verifies that the new architecture documents exist and contain their required structure:

- `Build_Docs/Architecture/DISCOVERY_PHILOSOPHY.md` exists and contains section headers for: agnostic workshop, dark room, engine as discovery instrument, no failures only observations, relationship to consumers.
- `Build_Docs/Architecture/LAYER_MANIFEST.md` exists and contains an entry for each of the eight current layers (`core`, `primitives`, `projection`, `metrology`, `branch`, `refinery`, `history`, `solver`).
- `Build_Docs/Agent_tasks/TASK_TEMPLATE.md` exists and contains section headers for the eleven required template sections (Repository, Current Verified Baseline, Task Goal, Design Principles, Primitive-Sufficiency Gate, Required Deliverables, Required Tests, Required Commands, Non-Goals, Completion Report, Acceptance Criteria).

### `tests/test_task010a_design_thesis_references.py`

Verifies that `Build_Docs/Architecture/DESIGN_THESIS.md` has been extended:

- Contains a new section titled "Design Commitments After the Reality-Check Review" (or close variant — the assertion can be relaxed to match the section's first heading).
- The new section references "Axiom 11" and "Axiom 12" by name.
- The new section references the agnostic-workshop framing from `DISCOVERY_PHILOSOPHY.md`.
- The existing thesis content (Layer Architecture, Initial Primitive Order, the D⊕S=P discussion) is preserved.

### `tests/test_task010a_layer_manifest_machine_readable.py`

Verifies that the layer manifest is parseable:

- Either `Build_Docs/Architecture/LAYER_MANIFEST.md` contains structured sections recognisable by regex (e.g. each layer entry has a heading matching `^## (core|primitives|projection|metrology|branch|refinery|history|solver)` and subheadings for "Parents" and "Provides"), OR
- `Build_Docs/Architecture/layer_manifest.json` exists and validates against a small declared schema (each layer has `name`, `description`, `parents`, `provides`).

The test does not yet enforce that the manifest matches the actual `__init__.py` exports — that audit is Task 010B's deliverable. Task 010A only verifies the manifest is structurally well-formed.

## Required commands

Run from repo root.

Red test slice (expected to fail before deliverables are written):

```bash
python -m pytest tests/test_task010a_axioms_present.py tests/test_task010a_principle_docs_present.py tests/test_task010a_design_thesis_references.py tests/test_task010a_layer_manifest_machine_readable.py -q
```

Green test slice (expected to pass after deliverables are written):

```bash
python -m pytest tests/test_task010a_axioms_present.py tests/test_task010a_principle_docs_present.py tests/test_task010a_design_thesis_references.py tests/test_task010a_layer_manifest_machine_readable.py -q
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
- The actual layer-manifest closure audit. That is Task 010B's deliverable; this task only authors the manifest.
- The lineage audit. That is Task 010C.
- Operation_id-as-measurement. That is Task 010C′.
- The off-the-shelf maths import audit. That is Task 010D.
- The `VocabularyStatus` family. That is Task 010E.
- The discovery harness scaffold. That is Task 010F.
- The synthesis protocol. That is Task 010G.
- `SYNTHESIS_PROTOCOL.md`. The reference to it in `DESIGN_THESIS.md` is a forward reference noting it will be created in Task 010G.

Do not modify:

- Any existing source files.
- Any existing tests.
- Any existing architecture documents other than `DESIGN_THESIS.md`.

Do not introduce:

- New status families.
- New protocols.
- New transition rules.
- New runtime dependencies.

## Completion report

Create the following at task end:

```text
Build_Docs/Reports/task010A/task010A_summary.md
Build_Docs/Reports/task010A/principles_documented.md
```

`task010A_summary.md` must include:

- Files created
- Files modified
- Red test slice command and result
- Green test slice command and result
- Full-suite command and result
- Source audit commands and results
- Deviations, if any
- Readiness note for Task 010B

`principles_documented.md` must include:

- A summary of Axiom 11 (Epistemic Stance Only) — one paragraph
- A summary of Axiom 12 (Self-Derivation) — one paragraph
- A summary of the agnostic-workshop / discovery-philosophy framing — one paragraph
- A summary of what `LAYER_MANIFEST.md` declares — one paragraph
- A summary of the task template structure — one paragraph
- A note explaining that further principles (vocabulary failure, measured operation_id, synthesis protocol) are documented in their own implementation tasks and not in 010A

## Acceptance criteria

Task 010A is complete only when:

1. `Build_Docs/Architecture/AXIOMS.md` contains Axioms 11 and 12 with the four-subsection format matching existing axioms.
2. `Build_Docs/Architecture/DISCOVERY_PHILOSOPHY.md` exists with the five required sections.
3. `Build_Docs/Architecture/LAYER_MANIFEST.md` exists with entries for all eight current layers including parent declarations and provided concepts.
4. The layer manifest is machine-readable: either by structured Markdown or by a sibling `layer_manifest.json` file.
5. `Build_Docs/Architecture/DESIGN_THESIS.md` has been extended with the new section referencing Axioms 11 and 12 and the discovery-philosophy framing, without removing existing content.
6. `Build_Docs/Agent_tasks/TASK_TEMPLATE.md` exists with all eleven required sections and the prose preamble explaining incremental task commitment.
7. All four required test files exist and the green test slice passes.
8. Full test suite passes (no existing tests broken).
9. Source audits remain clean.
10. No source code in `src/lloyd_v4/` has been modified.
11. Reports are written under `Build_Docs/Reports/task010A/`.
12. Readiness note for Task 010B is present in the summary report.

## Task 010B readiness

When this task is complete and committed, the next task in the series is **Task 010B — Layer manifest and closure audit**. Before drafting `codex_task010B.md`, the layer manifest authored in this task should be reviewed against the actual `__init__.py` exports in each layer to confirm the manifest is correct. If the review surfaces any discrepancies, the manifest is updated as part of 010A's completion (since the manifest is 010A's deliverable). 010B's spec is then written against the verified manifest.
