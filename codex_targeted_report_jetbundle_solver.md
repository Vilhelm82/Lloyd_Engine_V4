# Codex Task: Targeted V4 State Report for JetBundle and Alpha-Solver Design

## Purpose

Generate a targeted, source-grounded report that lets ChatGPT/Claire design the next V4 JetBundle and solver tasks from first-hand repository evidence, without uploading the full repo.

This is a reporting/audit task only. Do not modify runtime source unless explicitly noted under "allowed documentation outputs." Do not implement JetBundle, AlphaProbe, solver changes, or refactors.

## Repository

```text
/mnt/fast/Lloyd_Engine_V4
```

## Context

Lloyd V4 is a clean-room typed, stratified geometry kernel. V3/V1 are reference evidence only. There must be no adapters, no runtime dependency, no cross-engine calls, and no compatibility shims.

The current design question is:

> How should V4 design an alpha-aware JetBundle and a genuinely Lloyd-native solver that uses geometric measurement and typed status transitions, rather than becoming another Newton/Halley residual-descent solver?

Specific concern:

Existing Layer 2+ modules may be V3-shaped deferred-consumers unless they can be decomposed back into certified Layer 1 primitives and named transition rules. We need a source-grounded report that identifies what is safe substrate, what is candidate substrate, and what should be reference-only for the next solver design.

## Required Output

Create this report:

```text
Build_Docs/Reports/targeted_audit_jetbundle_solver/jetbundle_solver_state_report.md
```

Also create:

```text
Build_Docs/Reports/targeted_audit_jetbundle_solver/source_inventory.md
Build_Docs/Reports/targeted_audit_jetbundle_solver/audit_commands.md
```

If the report directory already exists, overwrite only files in that directory.

## Report Structure

The main report must have these sections.

### 1. Executive summary

Answer directly:

- What is the current trustworthy substrate for designing JetBundle?
- What is the current trustworthy substrate for designing an alpha-aware solver?
- Which existing modules are safe to depend on?
- Which modules should be treated as reference-only or candidate-only until certified?
- What is the recommended next task: ledger/certification, AlphaProbe, JetBundle, or solver?

### 2. Current task ledger reconstruction

Reconstruct the actual completed task sequence from available docs and source.

Include:

- canonical task ID
- task title
- report path
- created/modified source packages
- test count at completion, if available
- notes about 010 fan-out or numbering gaps, if present

Call out any ambiguous or missing task numbers.

### 3. Core substrate inventory

Inspect and summarize:

```text
src/lloyd_v4/core/result.py
src/lloyd_v4/core/status.py
src/lloyd_v4/core/protocols.py
src/lloyd_v4/core/transitions.py
src/lloyd_v4/core/provenance.py
src/lloyd_v4/core/serialization.py
src/lloyd_v4/core/validity.py
src/lloyd_v4/core/conditioning.py
```

For each file, report:

- main classes/enums/functions
- whether it is generic/status-family aware
- how provenance inputs/trace IDs are handled
- how named transition rules are represented
- any risks for JetBundle/solver design

### 4. Certified primitive/projection inventory

Inspect and summarize:

```text
src/lloyd_v4/primitives/projective_ratio.py
src/lloyd_v4/primitives/stratified_quadratic_roots.py
src/lloyd_v4/projection/exact_projection.py
```

For each:

- statuses emitted
- protocols declared
- transition rules exported
- provenance/parent trace behavior
- scalarization/division behavior
- whether it is safe substrate for JetBundle/solver design

### 5. Transfer and alpha measurement inventory

Find the current files that implement or test:

```text
typed_finite_difference
typed_log_log_slope
precision_floor
TRANSFER_CANCELLATION_DOMINATED
alpha minus one recovery
alpha-1 recovery
```

Use `rg` to locate them if paths are uncertain.

Report:

- exact source files
- exact tests
- status families involved
- how slope and alpha are computed
- whether ratios use ProjectiveRatio
- where `precision_floor` appears
- whether precision_floor changes computed values or only statuses
- how cancellation dominance is detected
- whether alpha is directional/probe-specific or treated as scalar global evidence
- whether nested-window alpha stability exists

### 6. Current solver inventory

Inspect and summarize:

```text
src/lloyd_v4/solver/
tests/test_task009_*.py
tests/test_task009A_*.py
```

If Task 009A tests do not exist, say so.

Report:

- SolverStatus values
- LocalQuadraticStepModel shape
- SolverPolicy fields
- how projection/root/metrology/branch/refinery/history gates are consumed
- which dependencies are hard dependencies versus optional gates
- whether the solver currently generates local models or only consumes supplied models
- where residual evidence enters
- whether any hidden tolerance/score exists
- whether it is suitable as substrate for an alpha-aware solver or should be treated as a reference consumer

### 7. Layer 2+ certification assessment

Inspect:

```text
src/lloyd_v4/metrology/
src/lloyd_v4/branch/
src/lloyd_v4/refinery/
src/lloyd_v4/history/
src/lloyd_v4/solver/
```

For each package, assign one of:

```text
certified_substrate
candidate_substrate
reference_only
quarantine_until_rebuilt
```

Use these criteria:

- lineage terminates in registered primitives or certified substrate
- named transition rules exist and are complete
- no hidden tolerance/rescue behavior
- declared floors/bands affect status only, not computed value
- result serialization preserves audit evidence
- no V1/V3 runtime dependency
- no domain-consumer assumptions
- no ad hoc mixed-family status joins

Explain the rating.

### 8. Projection transition rule ambiguity check

Inspect the transition rule for quadratic roots to exact projection.

Specifically determine whether it has both:

- static `mapped_statuses`
- contextual transition callable

If yes, answer:

- does static mapped_statuses imply unconditional mappings that the callable can override?
- can an incompatible branch produce `projection_selection_refused` even when the static dict says otherwise?
- recommend one of:
  - remove static mapped_statuses for contextual rules
  - mark static mappings as branch-compatible defaults only
  - add tests/comments clarifying callable authority

### 9. Precision floor audit

Find every occurrence of:

```text
precision_floor
roundoff_floor
unit_roundoff
machine_epsilon
cancellation_ratio
2.0**-52
2.0 ** -52
sys.float_info.epsilon
np.finfo
```

For each occurrence:

- path and line number
- purpose
- whether it changes value or only status
- whether it should be allowed, documented, renamed, or audited harder

Recommend a source audit pattern that catches future unauthorized precision floors without banning legitimate `noise_floor` or mathematical `Floors`.

### 10. JetBundle design implications

Based only on source evidence, recommend the minimal next JetBundle-related primitive.

Answer:

- Should `AlphaProbe` be separate from JetBundle?
- Should alpha evidence be directional/probe-specific?
- What statuses are needed?
- Which existing source functions can be reused safely?
- Which existing source functions should only be reference evidence?
- What must JetBundle refuse explicitly?
- Should JetBundle be callable-based first, parser-based, or both?

### 11. Solver design implications

Based only on source evidence, recommend the minimal next solver task.

Answer:

- Should the next solver depend on current metrology/branch/refinery/history modules?
- Or should it depend only on Layer 1/projection plus alpha-aware JetBundle?
- What is the smallest acceptance law that proves it is not Newton/Halley residual descent?
- What are the two or three killer tests?
- How should tied candidates be handled without hidden scoring?

### 12. Recommended next Codex ticket

Draft a recommended next ticket title and one-paragraph scope.

Choose one:

```text
Task 017: Layer/Axiom-12 certification and audit hardening
Task 018: Directional AlphaProbe primitive
Task 019: Alpha-aware JetBundle primitive
Task 020: AlphaProjectionSolver MVP
```

or propose a better order if source evidence demands it.

## Required Commands

Run and include outputs in `audit_commands.md`.

### Full tests

```bash
python -m pytest tests -q
```

### Source purity

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance|confidence_score|weighted_score|smoothing|hysteresis|interpolate|extrapolate" src/lloyd_v4 -n
rg -i "lloyd_core|lloyd_core_nvar|lloyd_decomposition|hyperdual|halley|multi_start|route_score" src/lloyd_v4 -n
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

### Alpha/transfer search

```bash
rg "typed_finite_difference|typed_log_log_slope|TRANSFER_CANCELLATION_DOMINATED|precision_floor|cancellation_ratio|alpha|α|log_log|slope" src tests Build_Docs -n
```

### Precision floor search

```bash
rg "precision_floor|roundoff_floor|unit_roundoff|machine_epsilon|cancellation_ratio|2\.0\s*\*\*\s*-52|sys\.float_info\.epsilon|np\.finfo" src tests Build_Docs -n
```

### Transition rule search

```bash
rg "StatusTransitionRule|mapped_statuses|transition_fn|apply_status_transition|quadratic_roots.to_exact_projection|projection" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection tests -n
```

### Layer dependency search

```bash
rg "from lloyd_v4\.metrology|import .*metrology" src/lloyd_v4/primitives src/lloyd_v4/projection -n
rg "from lloyd_v4\.branch|import .*branch" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology -n
rg "from lloyd_v4\.refinery|import .*refinery" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch -n
rg "from lloyd_v4\.history|import .*history" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery -n
rg "from lloyd_v4\.solver|import .*solver" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery src/lloyd_v4/history -n
```

## Important Constraints

- Do not alter runtime source.
- Do not implement JetBundle.
- Do not implement AlphaProbe.
- Do not modify solver behavior.
- Do not rename task files unless explicitly asked.
- Reports must cite exact source paths and, where helpful, line numbers.
- Be honest about uncertainty. If a task/report file is missing, say so.
- Treat V1/V3 as reference evidence only.
- Do not add adapters, bridges, compatibility shims, or cross-engine calls.

## Desired Final Reply From Codex

When done, reply with:

- path to the generated report
- test result summary
- top 5 findings
- recommended next task title
