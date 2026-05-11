# Codex Task 001 — ProjectiveRatio: the first honest primitive

## Repository

Work in:

```text
/mnt/fast/Lloyd_Engine_V4
```

Place this task file at:

```text
/mnt/fast/Lloyd_Engine_V4/Build_Docs/Agent_tasks/codex_task001.md
```

## Context

Task 000 created the Lloyd V4 bootstrap substrate under `src/lloyd_v4` and the architecture/report documents under `Build_Docs`. The source-only forbidden-concept audit over `src/` passed, and the initial tests passed.

V4 is not a V3 fork. It has no runtime dependency on V3, no adapters, no legacy modes, no `safe_mask`, no hidden guard rails, and no scalar-first result model.

The architectural thesis is:

> Lloyd V4 is a typed, stratified geometry kernel where every computation is a partial map between typed geometric spaces with explicit domain, stratum, validity, conditioning, provenance, and protocol contract.

Task 001 implements the first true primitive:

```text
ProjectiveRatio(n, d)
```

The primitive represents `n / d` as a projective state `[n:d]`, not as an automatic scalar.

Division is the smallest operation where scalar numerics starts lying. This task exists to make that lie impossible in V4.

## Read before changing code

Read these first:

```text
Build_Docs/Architecture/AXIOMS.md
Build_Docs/Architecture/DESIGN_THESIS.md
Build_Docs/Architecture/STATUS_CALCULUS.md
Build_Docs/Architecture/PROTOCOL_CONTRACTS.md
Build_Docs/Architecture/PROVENANCE_MODEL.md
Build_Docs/Architecture/RESULT_TYPES.md
Build_Docs/Architecture/METROLOGY_PRINCIPLES.md
Build_Docs/Architecture/ROADMAP.md
Build_Docs/Reports/task000/task000_summary.md
Build_Docs/Reports/task000/design_decisions.md
Build_Docs/Reports/task000/task001_scope_projective_ratio.md
```

Then inspect the actual core package:

```text
src/lloyd_v4/core/
tests/
```

Use the repo-native structures created in Task 000. Do not invent parallel versions of `TypedResult`, provenance, validity, protocol, serialization, or errors unless the existing ones truly cannot support this primitive. If the existing surface is too small, extend it minimally and document why.

## Goal

Implement `ProjectiveRatio` as a typed projective primitive with explicit scalarization.

The primitive must emit a typed result whose value is the projective representation `[n:d]` or an equivalent structured value. It must not divide by `d` during construction.

Scalarization is a separate operation. Scalarization may return a scalar only for strata whose protocol permits scalar output. Otherwise it must return a typed refusal or raise the repo-native protocol/refusal error, depending on the Task 000 design.

## Required strata

Implement exactly these ProjectiveRatio statuses unless an existing Task 000 status registry requires a namespaced spelling:

```text
finite_ratio         d != 0 and n != 0
signed_zero          d != 0 and n == 0
infinite_direction   d == 0 and n != 0
indeterminate        d == 0 and n == 0
```

Use exact zero tests only. Do not add tolerances. Do not add denominator floors. Do not reinterpret small nonzero denominators.

## Required semantics

### `finite_ratio`

Input stratum:

```text
d != 0 and n != 0
```

Projective state exists.

Scalarization is permitted and returns `n / d`.

### `signed_zero`

Input stratum:

```text
d != 0 and n == 0
```

Projective state exists.

Scalarization is permitted and returns the scalar zero implied by the raw representation. Preserve the raw numerator and denominator in the projective value so sign/orientation information is not destroyed.

### `infinite_direction`

Input stratum:

```text
d == 0 and n != 0
```

Projective direction exists.

Scalarization is refused. Do not return `inf`. Do not return a huge finite number. Do not throw away the projective value.

### `indeterminate`

Input stratum:

```text
d == 0 and n == 0
```

The projective point is not determined by the coordinates.

Scalarization is refused. The typed result should still carry the raw `[0:0]` evidence and an explicit indeterminate status.

## API shape

Prefer a small, explicit API. Adapt names to the Task 000 core conventions, but keep the conceptual shape:

```python
from lloyd_v4.primitives.projective_ratio import projective_ratio, scalarize_projective_ratio

ratio = projective_ratio(n, d)
scalar = scalarize_projective_ratio(ratio)
```

Suggested structured value:

```python
@dataclass(frozen=True)
class ProjectiveRatioValue:
    numerator: Any
    denominator: Any
```

Suggested primitive result:

```python
TypedResult(
    value=ProjectiveRatioValue(n, d),
    status=<one of finite_ratio/signed_zero/infinite_direction/indeterminate>,
    validity=<multi-field validity object>,
    conditioning=<conditioning object>,
    provenance=<provenance object>,
    protocol=<projective_ratio protocol if the substrate supports this>,
)
```

Do not force this exact constructor if the Task 000 objects differ. Use the substrate that exists.

## Validity guidance

V4 has no universal safe boolean.

Represent validity with the richest Task 000 object available. Conceptually:

```text
finite_ratio:
  projective_defined = true
  scalarizable = true
  scalar_finite = true

signed_zero:
  projective_defined = true
  scalarizable = true
  scalar_finite = true

infinite_direction:
  projective_defined = true
  scalarizable = false
  scalar_finite = false

indeterminate:
  projective_defined = false or undetermined
  scalarizable = false
  scalar_finite = false
```

If Task 000 validity fields are named differently, map these concepts into the existing fields and document the mapping.

## Protocol requirements

Add or extend a protocol declaration for ProjectiveRatio if the substrate supports protocol objects.

The protocol should declare:

```text
emitted statuses:
  finite_ratio
  signed_zero
  infinite_direction
  indeterminate

scalarization-accepted statuses:
  finite_ratio
  signed_zero

scalarization-refused statuses:
  infinite_direction
  indeterminate
```

Unhandled statuses must fail explicitly.

No consumer should be able to treat `ProjectiveRatio` as a plain scalar without requesting scalarization.

## Status calculus requirements

Task 000 created a conservative status calculus. Extend it minimally only if needed.

For Task 001, do not invent broad algebraic composition rules yet. Add only the rules necessary to:

1. represent the four ProjectiveRatio strata;
2. validate scalarization acceptance/refusal;
3. serialize/report the result safely;
4. avoid ad hoc scalar escape paths.

If the calculus cannot express a needed operation, produce a design note rather than adding a loose rule.

## Provenance requirements

Every ProjectiveRatio result should carry provenance through the repo-native provenance model.

At minimum, provenance should identify:

```text
operation_id: projective_ratio
expression_path: canonical_projective_ratio
parents or parent_trace_ids if n/d came from typed inputs
precision/backend/device/measurement_resolution if available from the substrate
```

Scalarization should create a child provenance entry, not overwrite the primitive provenance.

If inputs are raw Python values and no precision/backend/device exists, represent that explicitly rather than inventing fake metadata.

## Serialization requirements

ProjectiveRatio results must be strictly serializable using the Task 000 strict serialization path.

Rules:

- `infinite_direction` must not serialize as raw JSON `Infinity`.
- `indeterminate` must not serialize as raw JSON `NaN`.
- refused scalarization must serialize as a refusal/status object, not as a numeric sentinel.
- no output JSON may contain non-standard `NaN`, `Infinity`, or `-Infinity`.

## Source purity rules

Do not introduce these into `src/`:

```text
lloyd_v3
safe_mask
legacy
legacy_compat
projection_mode="legacy"
clamp_min
epsilon
eps
```

Also avoid denominator-rescue names such as:

```text
safe_divide
safe_denominator
denominator_floor
small_denominator_fix
```

This primitive is not a safe divide. It is a typed projective state.

Documentation may mention forbidden terms only when explaining what V4 refuses to do.

## Implementation tasks

### 1. Create primitive package

Add a primitive package if it does not exist:

```text
src/lloyd_v4/primitives/__init__.py
src/lloyd_v4/primitives/projective_ratio.py
```

Export the primitive cleanly from package `__init__` files if appropriate.

### 2. Implement ProjectiveRatio value and statuses

Add the value object and status constants/enum entries according to the Task 000 status conventions.

The constructor must classify the exact stratum without scalar division.

### 3. Implement explicit scalarization

Add:

```python
scalarize_projective_ratio(result)
```

or the repo-native equivalent.

Scalarization succeeds for `finite_ratio` and `signed_zero` only.

Scalarization refuses `infinite_direction` and `indeterminate`.

The refusal should use Task 000's typed refusal/protocol violation machinery. Do not return `None` silently.

### 4. Add strict serialization support

Ensure ProjectiveRatio typed results, scalarization successes, and scalarization refusals can be serialized by the strict serializer.

### 5. Add documentation/report files

Write:

```text
Build_Docs/Reports/task001/task001_summary.md
Build_Docs/Reports/task001/projective_ratio_status_table.md
Build_Docs/Reports/task001/scalarization_protocol.md
Build_Docs/Reports/task001/unresolved_questions.md
```

The summary should include commands run and test results.

The status table should include each stratum, condition, projective-defined status, scalarization permission, and refusal behavior.

### 6. Add tests

Add tests under `tests/`, for example:

```text
tests/test_task001_projective_ratio.py
tests/test_task001_projective_ratio_scalarization.py
tests/test_task001_projective_ratio_serialization.py
tests/test_task001_source_purity.py
```

Required tests:

1. finite denominator and nonzero numerator produces `finite_ratio`;
2. zero numerator with finite denominator produces `signed_zero`;
3. zero denominator with nonzero numerator produces `infinite_direction`;
4. zero numerator and zero denominator produces `indeterminate`;
5. construction preserves raw numerator and denominator;
6. construction does not divide by denominator;
7. scalarization succeeds for `finite_ratio`;
8. scalarization succeeds for `signed_zero`;
9. scalarization refuses `infinite_direction`;
10. scalarization refuses `indeterminate`;
11. refused scalarization is typed and serializable;
12. strict JSON output contains no non-finite JSON tokens;
13. source-only audit over `src/` contains no forbidden V3/legacy/guardrail terms;
14. no hidden denominator rescue appears in implementation.

Optional but valuable tests:

- negative denominator with zero numerator preserves raw sign/orientation evidence;
- integer inputs remain valid;
- float inputs remain valid;
- nested typed provenance parent trace IDs are preserved if the substrate supports them.

## Suggested verification commands

Run:

```bash
cd /mnt/fast/Lloyd_Engine_V4
python -m pytest tests -q
```

Run source-only forbidden-term audit:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|epsilon|eps" src -n
```

Run denominator-rescue audit:

```bash
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard" src/lloyd_v4/primitives src/lloyd_v4/core -n
```

If documentation intentionally discusses forbidden concepts, keep those references outside `src/` and clearly label them as refusals.

## Acceptance criteria

Task 001 is complete when:

1. `ProjectiveRatio` exists as a typed primitive.
2. It represents `[n:d]` without automatic division.
3. The four required strata are emitted correctly.
4. Scalarization is explicit.
5. Scalarization refuses non-scalarizable strata.
6. Results and refusals serialize strictly.
7. Provenance is preserved according to the Task 000 model.
8. Protocol validation rejects unhandled statuses.
9. Tests pass.
10. Source-only forbidden-term audit over `src/` passes.
11. No hidden denominator rescue exists.
12. Task 001 reports are written.

## What not to do

Do not implement StratifiedQuadraticRoots yet.

Do not implement branch fingerprints yet.

Do not implement V3 comparison fixtures yet.

Do not add torch/CUDA/performance dependencies unless the Task 000 substrate already requires them.

Do not add domain consumers.

Do not add adapters.

Do not create a scalar-first convenience API.

Do not name this primitive `safe_divide`.

## Expected Task 002 preparation

At the end of Task 001, produce a short scope note for Task 002:

```text
Build_Docs/Reports/task001/task002_scope_stratified_quadratic_roots.md
```

Task 002 should likely implement `StratifiedQuadraticRoots` without legacy mode, using the ProjectiveRatio/status/protocol lessons from Task 001.

Do not start Task 002 in this pass.

## Final report format

At completion, report:

```text
Task 001 status: completed / blocked
Files added
Files modified
Tests run
Audit results
ProjectiveRatio status table location
Scalarization behavior summary
Unresolved design questions
Task 002 readiness
```
