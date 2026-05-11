# Codex Task 002: StratifiedQuadraticRoots

## Repository

Work in:

```text
/mnt/fast/Lloyd_Engine_V4
```

This is Lloyd Engine V4 clean-room work. V3 is reference evidence only. Do not import, call, bridge, compare against, or adapt V3 at runtime. Do not add legacy adapters, compatibility shims, downgrade modes, or cross-engine calls.

## Current State

Task 000 is complete. The M0 core substrate exists: statuses, validity, conditioning, provenance, typed results/refusals, protocol validation, conservative status calculus, strict serialization, and core errors.

Task 001 is complete. `ProjectiveRatio(n, d)` exists as the first primitive. It preserves raw projective coordinates `[n:d]`, classifies the exact projective stratum without dividing by `d`, and scalarizes only through an explicit protocol that may refuse. The full test suite currently passes with 23 tests, and source-only audits over `src/` are clean.

## Goal

Implement `StratifiedQuadraticRoots` as the second Layer 1 primitive.

The primitive must treat the real quadratic equation

```text
a*x^2 + b*x + c = 0
```

as a typed stratified root state before any scalar root output is requested.

This task is not a V3 refactor. It is a clean V4 primitive.

## Design Principles

- Geometry precedes scalarization.
- Degeneracy is a stratum, not failure.
- Exact classification comes before numeric root selection.
- No hidden tolerances, denominator floors, discriminant clamps, rescue constants, or fallback modes.
- Scalar/root selection must be explicit and may refuse.
- Typed results compose by protocols.
- Preserve raw coefficients, discriminant evidence, root-coordinate evidence, and provenance.

## Required Public API

Add a new module:

```text
src/lloyd_v4/primitives/stratified_quadratic_roots.py
```

Export the APIs from:

```text
src/lloyd_v4/primitives/__init__.py
```

Required functions:

```python
stratified_quadratic_roots(a, b, c) -> TypedResult
select_quadratic_root(result, branch: str) -> TypedResult
```

Recommended value objects, names may vary if the existing core style suggests better names:

```python
QuadraticCoefficients
QuadraticRootCoordinate
StratifiedQuadraticRootValue
```

The primitive result value must be structured. Do not return a bare tuple of scalar roots.

## Statuses

The primitive must emit exactly these initial statuses:

```text
two_real_roots
repeated_root
no_real_root
linear_root
constant_identity
constant_no_solution
```

Use existing M0 status definitions if they already exist. If they do not, extend the primitive status definitions minimally and consistently with the M0 status/protocol style.

## Exact Classification Rules

Use exact equality and exact sign tests on the computed discriminant. Do not use approximate-zero logic.

Let:

```text
discriminant = b*b - 4*a*c
```

Classification:

```text
if a != 0:
    if discriminant > 0:
        status = two_real_roots
    elif discriminant == 0:
        status = repeated_root
    else:
        status = no_real_root
else:
    if b != 0:
        status = linear_root
    elif c == 0:
        status = constant_identity
    else:
        status = constant_no_solution
```

Important consequences:

- A very small nonzero `a` is still quadratic.
- A very small nonzero discriminant is not repeated.
- A negative discriminant is `no_real_root`; do not return complex roots in Task 002.
- `constant_identity` means every real `x` satisfies the equation; it is not a selected scalar root.
- `constant_no_solution` means no real `x` satisfies the equation.

## Root Coordinate Representation

`stratified_quadratic_roots(a, b, c)` must preserve raw coefficients and the discriminant. It should also preserve selectable real root coordinates as projective coordinate evidence, not as already-selected scalar roots.

Use branch labels that are algebraic, not policy-driven:

```text
minus     -> (-b - sqrt(discriminant)) / (2*a)
plus      -> (-b + sqrt(discriminant)) / (2*a)
repeated  -> (-b) / (2*a)
linear    -> (-c) / b
```

Suggested coordinate records:

```text
minus:    [ -b - sqrt(discriminant) : 2*a ]
plus:     [ -b + sqrt(discriminant) : 2*a ]
repeated: [ -b : 2*a ]
linear:   [ -c : b ]
```

Only compute `sqrt(discriminant)` after the stratum has established `discriminant > 0`. For `repeated_root`, no square-root path is needed; use `[ -b : 2*a ]` directly.

Do not implement a numerically-stable alternate quadratic formula in this task. That would introduce a second expression path. Task 002 should use the direct algebraic path and record it honestly in provenance. Future path-aware primitives may add alternative formulas as separately named paths.

## Selection Protocol

Add protocol declarations consistent with the existing M0 protocol machinery:

```text
STRATIFIED_QUADRATIC_ROOTS_PROTOCOL
QUADRATIC_ROOT_SELECTION_PROTOCOL
```

`STRATIFIED_QUADRATIC_ROOTS_PROTOCOL` emits:

```text
two_real_roots
repeated_root
no_real_root
linear_root
constant_identity
constant_no_solution
```

`QUADRATIC_ROOT_SELECTION_PROTOCOL` accepts only:

```text
two_real_roots
repeated_root
linear_root
```

It refuses:

```text
no_real_root
constant_identity
constant_no_solution
```

Branch compatibility must also be explicit:

```text
two_real_roots -> accepts branch "minus" or "plus"
repeated_root  -> accepts branch "repeated"
linear_root    -> accepts branch "linear"
```

There must be no default branch, no principal root, no larger/smaller policy, and no domain-specific root selection.

`select_quadratic_root(result, branch)` must validate the root-state result against `QUADRATIC_ROOT_SELECTION_PROTOCOL`. Unsupported statuses or incompatible branch labels must return a typed refusal, not `nan`, `inf`, `None` as a scalar answer, or a silent fallback.

When division is needed for a selected root, use the Task 001 `ProjectiveRatio` path or an equivalent explicit protocol path. The selection result must preserve the root-state trace ID in provenance, directly or through the selected projective-ratio child result.

## Validity Mapping

Use the existing `Validity` fields conservatively:

```text
two_real_roots:        defined=True, finite=True,  selectable=True,  advanceable=True,  observable=True
repeated_root:         defined=True, finite=True,  selectable=True,  advanceable=True,  observable=True
linear_root:           defined=True, finite=True,  selectable=True,  advanceable=True,  observable=True
no_real_root:          defined=True, finite=False, selectable=False, advanceable=False, observable=True
constant_identity:     defined=True, finite=False, selectable=False, advanceable=False, observable=True
constant_no_solution:  defined=True, finite=False, selectable=False, advanceable=False, observable=True
```

Here `defined=True` means the root-state stratum is determined. It does not mean a unique scalar root exists.

For `repeated_root`, mark conditioning conservatively using the existing conditioning carrier. Do not invent a numeric condition estimate or tolerance in this task.

## Input Rules

Task 002 is scalar-only.

Accept finite real scalar coefficients supported by the existing core style, expected initially as `int` and `float`.

Non-finite inputs such as `nan`, `inf`, and `-inf` must fail explicitly through the existing error/refusal path. Do not classify non-finite inputs as mathematical strata.

Do not implement arrays, tensors, complex coefficients, symbolic coefficients, Decimal/Fraction special cases, or metrology-resolution behavior in this task.

## Serialization

Strict serialization must preserve:

- raw coefficients `a`, `b`, `c`
- computed discriminant where applicable
- emitted status
- validity fields
- conditioning field
- provenance, including operation ID, expression path, parent trace references, backend/device/precision if available
- root coordinate records and branch labels for selectable real-root strata
- typed refusal information for unsupported selection requests

No serialized scalar root should appear from `stratified_quadratic_roots(...)` itself. Scalar root output may appear only from `select_quadratic_root(...)` after protocol validation.

## Files to Add or Modify

Expected source changes:

```text
src/lloyd_v4/primitives/stratified_quadratic_roots.py
src/lloyd_v4/primitives/__init__.py
src/lloyd_v4/core/status.py          # only if the six statuses are not already present
src/lloyd_v4/core/protocols.py       # only if protocol declarations live centrally
```

Expected tests:

```text
tests/test_task002_stratified_quadratic_roots.py
tests/test_task002_quadratic_root_selection.py
tests/test_task002_quadratic_root_serialization.py
tests/test_task002_source_purity.py
```

Expected reports:

```text
Build_Docs/Reports/task002/task002_summary.md
Build_Docs/Reports/task002/stratified_quadratic_roots_status_table.md
Build_Docs/Reports/task002/design_decisions.md
```

Do not modify Task 001 behavior except as needed for imports/exports. Existing Task 000 and Task 001 tests must remain green.

## Required Tests

Write tests before implementation and run the Task 002 test slice once to confirm the expected red state.

Minimum classification tests:

```text
stratified_quadratic_roots(1, -3, 2) -> two_real_roots
stratified_quadratic_roots(1, 2, 1) -> repeated_root
stratified_quadratic_roots(1, 0, 1) -> no_real_root
stratified_quadratic_roots(0, 2, -4) -> linear_root
stratified_quadratic_roots(0, 0, 0) -> constant_identity
stratified_quadratic_roots(0, 0, 5) -> constant_no_solution
```

Minimum coordinate tests:

```text
two_real_roots preserves branches "minus" and "plus"
repeated_root preserves branch "repeated"
linear_root preserves branch "linear"
no_real_root has no real-root coordinate records
constant_identity has no selected scalar root
constant_no_solution has no selected scalar root
```

Minimum selection tests:

```text
select two_real_roots branch "minus" succeeds
select two_real_roots branch "plus" succeeds
select repeated_root branch "repeated" succeeds
select linear_root branch "linear" succeeds
select no_real_root refuses
select constant_identity refuses
select constant_no_solution refuses
select two_real_roots with branch "linear" refuses
select repeated_root with branch "plus" refuses
select linear_root with branch "minus" refuses
```

Minimum exactness tests:

```text
a very small nonzero a remains quadratic, not linear
a very small nonzero discriminant is not repeated
no_real_root does not return complex roots
stratified_quadratic_roots itself does not return a bare tuple of scalar roots
selection refusal does not return inf, nan, or a numeric sentinel
```

Minimum serialization tests:

```text
classification result serializes with coefficients, discriminant, status, validity, conditioning, provenance, and root coordinate evidence
selection success serializes as a child typed result with parent trace provenance
selection refusal serializes with TypedRefusal and original root-state status preserved
strict serialization rejects non-finite scalar payloads as in M0
```

Minimum source-purity tests:

```text
No V3, legacy, adapter, safe-mask, hidden-correction, or denominator/discriminant rescue terms appear in src/.
No discriminant clamp, square-root rescue, denominator floor, or hidden tolerance appears in the new primitive.
No cmath/complex-root path appears in Task 002 source.
```

## Required Commands

Run the Task 002 red slice before implementation:

```bash
python -m pytest tests/test_task002_stratified_quadratic_roots.py tests/test_task002_quadratic_root_selection.py tests/test_task002_quadratic_root_serialization.py tests/test_task002_source_purity.py -q
```

After implementation, run:

```bash
python -m pytest tests/test_task002_stratified_quadratic_roots.py tests/test_task002_quadratic_root_selection.py tests/test_task002_quadratic_root_serialization.py tests/test_task002_source_purity.py -q
python -m pytest tests -q
```

Run source-only audits:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|epsilon|eps" src -n
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard" src/lloyd_v4/primitives src/lloyd_v4/core -n
rg "disc_floor|discriminant_floor|clamp_discriminant|safe_sqrt|sqrt_guard|small_discriminant|tolerance|threshold" src/lloyd_v4/primitives src/lloyd_v4/core -n
rg "import cmath|from cmath|complex\(" src/lloyd_v4/primitives/stratified_quadratic_roots.py -n
```

The expected result for each source-only audit is no matches.

## Non-Goals

Do not implement:

- ProjectionResultV4
- branch fingerprints
- metrology or measurement-resolution thresholds
- b_k noise-floor estimation
- K_q calibration
- domain consumers
- V3 fixtures or V3 comparison tests
- adapters, bridges, shims, or compatibility modes
- arrays/tensors/status tensors
- complex roots
- symbolic roots
- alternate numerically stable quadratic formula paths
- root ordering by magnitude or policy
- principal-root defaults

## Completion Report

Create `Build_Docs/Reports/task002/task002_summary.md` with:

- files created
- files modified
- behavior summary
- red test result
- Task 002 test-slice result
- full-suite result
- source-audit results
- deviations, if any
- readiness note for Task 003: `ProjectionResultV4 and exact projection protocol`

Also create `stratified_quadratic_roots_status_table.md` documenting each status, exact condition, value shape, validity mapping, selection behavior, and refusal behavior.

## Acceptance Criteria

Task 002 is complete only when:

1. `stratified_quadratic_roots(a, b, c)` returns a typed root-state result, not scalar roots.
2. The six required statuses classify exactly as specified.
3. Raw coefficients and discriminant evidence are preserved.
4. Selectable root coordinates are represented as branch-labeled projective coordinates.
5. Root selection is explicit and protocol-validated.
6. Unsupported root selection returns typed refusal.
7. No hidden tolerance, clamp, rescue, denominator floor, square-root guard, or legacy pathway exists.
8. No complex-root path is implemented.
9. No V3 runtime dependency, fixture comparison, adapter, bridge, or compatibility mode is added.
10. Task 000 and Task 001 behavior remains green.
11. Task 002 reports are written under `Build_Docs/Reports/task002/`.
12. Task-specific tests, full-suite tests, and source-only audits all pass.
