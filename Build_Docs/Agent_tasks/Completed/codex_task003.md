# Codex Task 003: ProjectionResultV4 and Exact Projection Protocol

## Repository

Work in:

```text
/mnt/fast/Lloyd_Engine_V4
```

This is Lloyd Engine V4 clean-room work. V3 is reference evidence only. Do not import, call, bridge, compare against, or adapt V3 at runtime. Do not add legacy adapters, compatibility shims, downgrade modes, or cross-engine calls.

## Current State

Task 000 is complete. The M0 core substrate exists: statuses, validity, conditioning, provenance, typed results/refusals, protocol validation, conservative status calculus, strict serialization, and core errors.

Task 001 is complete. `ProjectiveRatio(n, d)` exists as the first primitive. It preserves raw projective coordinates `[n:d]`, classifies exact projective strata without dividing by `d`, and scalarizes only through an explicit protocol that may refuse.

Task 002 is complete. `StratifiedQuadraticRoots` exists as the second Layer 1 primitive. `stratified_quadratic_roots(a, b, c)` returns a typed root-state result with raw coefficients, discriminant evidence where applicable, branch-labeled projective root coordinates for selectable real-root strata, validity, conditioning, and provenance. `select_quadratic_root(result, branch)` is explicit and protocol-validated. The full test suite currently passes with 46 tests, and source-only audits over `src/` are clean.

Task 003 should now implement `ProjectionResultV4 and exact projection protocol`.

## Goal

Implement `ProjectionResultV4` as the first exact projection protocol over Task 002 root-state results.

Projection in Task 003 is not a domain consumer. It does not compute spatial geometry, bearing diagnostics, a flow integration, branch fingerprints, or metrology. It consumes a typed root-state result, an explicit branch request, and emits a typed projection result that separates:

```text
root_exists
projection_defined
selected_root_valid
advance_valid
conditioning_status
```

This task proves that V4 can compose typed root-state results into a projection decision without collapsing degeneracy into a boolean mask or scalar fallback.

## Design Principles

- Geometry precedes scalarization.
- Degeneracy is a stratum, not failure.
- Projection consumes typed root-state evidence through protocols.
- Branch selection is explicit. There is no default, nearest, principal, or policy-selected branch.
- A projection result is not a raw scalar root.
- `root_exists`, `projection_defined`, `selected_root_valid`, and `advance_valid` are distinct fields.
- Tangent contact is a projection stratum, not a generic success.
- No hidden tolerances, rescue constants, branch policies, clamps, fallback branches, or legacy modes.
- Typed results compose by protocols and preserve provenance through compact parent trace IDs.

## Required Public API

Add a new projection module. Prefer this package boundary because Task 003 is a protocol consumer of Layer 1 primitives rather than another root primitive:

```text
src/lloyd_v4/projection/__init__.py
src/lloyd_v4/projection/exact_projection.py
```

If the existing package shape strongly favors keeping all early operations under `primitives`, use:

```text
src/lloyd_v4/primitives/projection_result.py
```

but do not create both.

Required function:

```python
exact_quadratic_projection(root_state_result: TypedResult, branch: str) -> TypedResult
```

Recommended value objects, names may vary if the existing core style suggests better names:

```python
ProjectionFlags
ProjectionResultValue
ProjectionRefusalEvidence
```

The projection result value must be structured. Do not return a scalar root, tuple, boolean mask, or bare dictionary.

## Input Contract

`exact_quadratic_projection(...)` consumes a typed root-state result produced by `stratified_quadratic_roots(...)`, or a result that validates against the same Task 002 root-state protocol.

The function must validate the input protocol before projecting.

Invalid input types, non-root typed results, raw coefficient tuples, scalar roots, and arbitrary objects must fail explicitly through the existing protocol/error/refusal path. Do not silently re-run `stratified_quadratic_roots(...)` from raw coefficients in Task 003.

The branch argument is required and must be preserved in the output evidence, even when projection refuses.

## Projection Protocols

Add protocol declarations consistent with the existing M0 protocol machinery:

```text
EXACT_QUADRATIC_PROJECTION_PROTOCOL
PROJECTION_RESULT_V4_PROTOCOL
```

`EXACT_QUADRATIC_PROJECTION_PROTOCOL` consumes Task 002 root-state statuses:

```text
two_real_roots
repeated_root
no_real_root
linear_root
constant_identity
constant_no_solution
```

`PROJECTION_RESULT_V4_PROTOCOL` emits only the Task 003 projection statuses listed below.

Protocol validation must be explicit. If the source result cannot validate as a Task 002 root-state result, fail through the existing core refusal/error path rather than trying to infer fields by duck typing.

## Projection Statuses

The projection result emitted by `exact_quadratic_projection(...)` must emit exactly these projection statuses when input protocol validation succeeds:

```text
projection_transverse
projection_tangent_contact
projection_linear
projection_no_real_root
projection_identity
projection_no_solution
projection_selection_refused
```

Core protocol validation failures may use the existing core refusal/status machinery. The seven-status limit applies to validated Task 003 projection results, not to unrelated input validation failures.

## Projection Classification Rules

Use the source root-state status from Task 002 and the explicit branch request.

Source root-state statuses map as follows:

```text
two_real_roots + branch "minus" or "plus"      -> projection_transverse
repeated_root  + branch "repeated"             -> projection_tangent_contact
linear_root    + branch "linear"               -> projection_linear
no_real_root                                  -> projection_no_real_root
constant_identity                            -> projection_identity
constant_no_solution                         -> projection_no_solution
selectable source status + incompatible branch -> projection_selection_refused
```

Important consequences:

- `two_real_roots` accepts only `minus` and `plus`.
- `repeated_root` accepts only `repeated`.
- `linear_root` accepts only `linear`.
- Nonselectable source statuses are classified by their source stratum, not by branch compatibility.
- `constant_identity` means the real solution set is nonempty but nonunique. It does not define a unique projection.
- `projection_tangent_contact` is defined and has a selected scalar root, but it is not advance-valid in Task 003.
- `advance_valid` is a stratum-level projection flag. It does not mean positive time, nearest root, nonzero displacement, or domain-preferred motion.

For float roots selected through Task 002, Task 003 inherits Task 002 host-arithmetic semantics. Task 003 does not attempt symbolic, arbitrary-precision, or tolerance-based reinterpretation of root-state classification.

## Use Task 002 Selection Explicitly

For source statuses that support compatible branch selection, call or otherwise use the Task 002 explicit selection path:

```python
select_quadratic_root(root_state_result, branch)
```

Do not recompute the quadratic formula inside Task 003.

Do not divide projective coordinates directly in Task 003.

Do not bypass ProjectiveRatio scalarization. Task 002 already routes selected roots through the explicit ProjectiveRatio path. Task 003 should consume that selected-root child result and wrap it in projection provenance.

If Task 002 selection returns a typed refusal for an incompatible selectable branch, Task 003 should return a projection result with status:

```text
projection_selection_refused
```

and preserve the Task 002 refusal evidence.

## Required Projection Flags

Every validated Task 003 projection result must include a structured flag object with at least:

```python
root_exists: bool
projection_defined: bool
selected_root_valid: bool
advance_valid: bool
```

Required flag semantics:

```text
projection_transverse:        root_exists=True,  projection_defined=True,  selected_root_valid=True,  advance_valid=True
projection_linear:            root_exists=True,  projection_defined=True,  selected_root_valid=True,  advance_valid=True
projection_tangent_contact:   root_exists=True,  projection_defined=True,  selected_root_valid=True,  advance_valid=False
projection_no_real_root:      root_exists=False, projection_defined=False, selected_root_valid=False, advance_valid=False
projection_identity:          root_exists=True,  projection_defined=False, selected_root_valid=False, advance_valid=False
projection_no_solution:       root_exists=False, projection_defined=False, selected_root_valid=False, advance_valid=False
projection_selection_refused: root_exists=<from source status>, projection_defined=False, selected_root_valid=False, advance_valid=False
```

For `projection_selection_refused`, compute `root_exists` from the source root-state status:

```text
two_real_roots        -> True
repeated_root         -> True
linear_root           -> True
constant_identity     -> True
no_real_root          -> False
constant_no_solution  -> False
```

`root_exists=True` for `constant_identity` means the real solution set is nonempty. It does not mean a unique selectable projection exists.

## Validity Mapping

Use the existing `Validity` fields conservatively. For Task 003, `Validity.defined` tracks whether a unique projection target is determined, not merely whether the source stratum is known.

```text
projection_transverse:        defined=True,  finite=True,  selectable=True,  advanceable=True,  observable=True
projection_linear:            defined=True,  finite=True,  selectable=True,  advanceable=True,  observable=True
projection_tangent_contact:   defined=True,  finite=True,  selectable=True,  advanceable=False, observable=True
projection_no_real_root:      defined=False, finite=False, selectable=False, advanceable=False, observable=True
projection_identity:          defined=False, finite=False, selectable=False, advanceable=False, observable=True
projection_no_solution:       defined=False, finite=False, selectable=False, advanceable=False, observable=True
projection_selection_refused: defined=False, finite=False, selectable=False, advanceable=False, observable=True
```

The source root-state status remains observable even when projection is not defined.

## Conditioning

Preserve source conditioning from the root-state result.

Additional Task 003 conditioning rules:

```text
projection_tangent_contact -> warning or equivalent conservative conditioning state
projection_transverse      -> preserve source conditioning
projection_linear          -> preserve source conditioning
projection_no_real_root    -> preserve source conditioning
projection_identity        -> warning or equivalent nonunique/underdetermined conditioning state
projection_no_solution     -> preserve source conditioning
projection_selection_refused -> warning or refusal-appropriate conditioning state
```

Do not invent numeric condition estimates in Task 003.

Repeated roots are structurally degenerate for projection even though Task 002 allowed root selection. This is the point of the Task 003 distinction between `selected_root_valid` and `advance_valid`.

## Projection Result Value Shape

A successful or refused projection result should preserve at least:

- source root-state status
- requested branch
- selected branch, if selection succeeds
- selected scalar root value, if selection succeeds
- selected-root child result trace ID, if selection succeeds
- Task 002 selection refusal evidence, if branch selection refuses
- projection status
- projection flags
- source root-state trace ID
- source root-state operation ID or protocol name when available

Suggested value object shape:

```python
@dataclass(frozen=True)
class ProjectionFlags:
    root_exists: bool
    projection_defined: bool
    selected_root_valid: bool
    advance_valid: bool

@dataclass(frozen=True)
class ProjectionResultValue:
    source_status: str
    requested_branch: str
    selected_branch: str | None
    selected_root_value: object | None
    selected_root_trace_id: str | None
    flags: ProjectionFlags
    refusal: object | None
```

Names may vary. The structure must not be replaced by an untyped dictionary unless that is already the strict serialization style of the core.

## Provenance

Projection provenance must include:

```text
operation_id = exact_quadratic_projection
expression_path = projection_from_stratified_quadratic_roots
parent trace reference to the Task 002 root-state result
parent trace reference to the selected-root child result when selection succeeds
parent trace reference or refusal evidence when Task 002 selection refuses
source root-state status
projection status
requested branch
selected branch when applicable
```

Use compact parent trace IDs, not recursive parent result objects.

Do not erase the ProjectiveRatio trace chain created by Task 002 selection. Task 003 should add projection provenance on top of it.

## Serialization

Strict serialization must preserve:

- projection status
- projection flags
- source root-state status
- requested branch
- selected branch when applicable
- selected scalar root value when applicable
- selection child trace ID when selection is attempted and available
- refusal evidence when applicable
- validity fields
- conditioning field
- provenance fields
- source root-state trace reference

Serialization must distinguish:

```text
projection_tangent_contact
projection_transverse
projection_selection_refused
projection_no_real_root
projection_identity
projection_no_solution
```

Do not serialize a projection result as only a boolean or scalar root.

## Files to Add or Modify

Expected source changes:

```text
src/lloyd_v4/projection/__init__.py
src/lloyd_v4/projection/exact_projection.py
src/lloyd_v4/core/status.py        # only if projection statuses must be registered centrally
src/lloyd_v4/core/protocol.py      # only if protocol declarations live centrally
src/lloyd_v4/__init__.py           # only if existing package exports require it
```

Alternative source path only if package layout demands it:

```text
src/lloyd_v4/primitives/projection_result.py
src/lloyd_v4/primitives/__init__.py
```

Expected tests:

```text
tests/test_task003_projection_result.py
tests/test_task003_projection_protocol.py
tests/test_task003_projection_serialization.py
tests/test_task003_source_purity.py
```

Expected reports:

```text
Build_Docs/Reports/task003/task003_summary.md
Build_Docs/Reports/task003/projection_result_status_table.md
Build_Docs/Reports/task003/design_decisions.md
```

Do not modify Task 001 or Task 002 behavior except as needed for imports/exports. Existing Task 000, Task 001, and Task 002 tests must remain green.

## Required Tests

Write tests before implementation and run the Task 003 test slice once to confirm the expected red state.

Minimum projection classification tests:

```text
stratified_quadratic_roots(1, -3, 2), branch "minus" -> projection_transverse
stratified_quadratic_roots(1, -3, 2), branch "plus" -> projection_transverse
stratified_quadratic_roots(1, 2, 1), branch "repeated" -> projection_tangent_contact
stratified_quadratic_roots(0, 2, -4), branch "linear" -> projection_linear
stratified_quadratic_roots(1, 0, 1), any branch -> projection_no_real_root
stratified_quadratic_roots(0, 0, 0), any branch -> projection_identity
stratified_quadratic_roots(0, 0, 5), any branch -> projection_no_solution
```

Minimum branch compatibility tests:

```text
two_real_roots with branch "linear" -> projection_selection_refused
repeated_root with branch "plus" -> projection_selection_refused
linear_root with branch "minus" -> projection_selection_refused
projection_selection_refused preserves requested branch
projection_selection_refused preserves source root-state status
projection_selection_refused preserves Task 002 selection refusal evidence
```

Minimum flag tests:

```text
projection_transverse has root_exists=True, projection_defined=True, selected_root_valid=True, advance_valid=True
projection_linear has root_exists=True, projection_defined=True, selected_root_valid=True, advance_valid=True
projection_tangent_contact has root_exists=True, projection_defined=True, selected_root_valid=True, advance_valid=False
projection_no_real_root has root_exists=False, projection_defined=False, selected_root_valid=False, advance_valid=False
projection_identity has root_exists=True, projection_defined=False, selected_root_valid=False, advance_valid=False
projection_no_solution has root_exists=False, projection_defined=False, selected_root_valid=False, advance_valid=False
projection_selection_refused from two_real_roots has root_exists=True but selected_root_valid=False
```

Minimum validity tests:

```text
projection_transverse validity is defined, finite, selectable, advanceable, observable
projection_linear validity is defined, finite, selectable, advanceable, observable
projection_tangent_contact validity is defined, finite, selectable, not advanceable, observable
projection_no_real_root validity is not defined, not finite, not selectable, not advanceable, observable
projection_identity validity is not defined, not finite, not selectable, not advanceable, observable
projection_no_solution validity is not defined, not finite, not selectable, not advanceable, observable
projection_selection_refused validity is not defined, not finite, not selectable, not advanceable, observable
```

Minimum protocol tests:

```text
exact_quadratic_projection refuses or errors on raw coefficient tuples
exact_quadratic_projection refuses or errors on scalar roots
exact_quadratic_projection refuses or errors on ProjectiveRatio results that are not quadratic root states
exact_quadratic_projection validates root-state protocol before reading root-state fields
exact_quadratic_projection does not silently re-run quadratic classification from raw coefficients
```

Minimum provenance tests:

```text
projection result provenance parent includes root-state trace ID
projection result provenance includes selection child trace ID when selection succeeds
projection result provenance preserves requested branch
projection result provenance preserves selected branch when selection succeeds
projection_selection_refused preserves refusal evidence and source root-state trace ID
```

Minimum serialization tests:

```text
projection result serializes projection status, flags, source status, requested branch, validity, conditioning, provenance, and parent trace IDs
successful projection serializes selected branch and selected scalar root value
projection_tangent_contact serializes advance_valid=False distinctly from selection failure
projection_identity serializes root_exists=True and projection_defined=False
projection_selection_refused serializes refusal evidence and requested branch
strict serialization rejects non-finite scalar payloads as in M0
```

Minimum source-purity tests:

```text
No V3, legacy, adapter, safe-mask, hidden-correction, branch-policy, or projection fallback terms appear in src/.
Task 003 source does not recompute the quadratic formula.
Task 003 source does not directly divide projective root coordinates.
Task 003 source does not introduce nearest/principal/default branch selection.
Task 003 source does not introduce metrology, branch fingerprints, K_q calibration, or b_k noise-floor estimation.
```

## Required Commands

Run the Task 003 red slice before implementation:

```bash
python -m pytest tests/test_task003_projection_result.py tests/test_task003_projection_protocol.py tests/test_task003_projection_serialization.py tests/test_task003_source_purity.py -q
```

After implementation, run:

```bash
python -m pytest tests/test_task003_projection_result.py tests/test_task003_projection_protocol.py tests/test_task003_projection_serialization.py tests/test_task003_source_purity.py -q
python -m pytest tests -q
```

Run source-only audits:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard" src/lloyd_v4 -n
rg "disc_floor|discriminant_floor|clamp_discriminant|safe_sqrt|sqrt_guard|small_discriminant|tolerance|threshold" src/lloyd_v4 -n
rg "principal_root|nearest_root|default_branch|auto_branch|root_policy|advance_policy|projection_fallback|fallback_branch" src/lloyd_v4 -n
rg "b_k|K_q|branch_fingerprint|fingerprint|noise_floor|measurement_resolution|calibration" src/lloyd_v4/projection src/lloyd_v4/primitives -n
```

The expected result for each source-only audit is no matches.

If Task 003 is implemented under `src/lloyd_v4/primitives/projection_result.py` instead of `src/lloyd_v4/projection`, adjust the last command path accordingly.

## Non-Goals

Do not implement:

- domain consumers
- spatial point/vector projection
- flow integration
- positive-time or nearest-root policy
- principal-root defaults
- branch ordering by magnitude or sign
- projection mode flags
- projection mode legacy behavior
- V3 fixtures or V3 comparison tests
- adapters, bridges, shims, or compatibility modes
- branch fingerprints
- metrology or measurement-resolution thresholds
- b_k noise-floor estimation
- K_q calibration
- finite-eta correction
- path-aware alternate quadratic formulas
- arrays/tensors/status tensors
- complex projection paths
- symbolic or arbitrary-precision projection classification
- numeric condition estimates

## Completion Report

Create `Build_Docs/Reports/task003/task003_summary.md` with:

- files created
- files modified
- behavior summary
- red test result
- Task 003 test-slice result
- full-suite result
- source-audit results
- deviations, if any
- readiness note for Task 004: `Metrology foundation: b_k noise floor and K_q calibration`

Also create `projection_result_status_table.md` documenting each projection status, source condition, branch compatibility, projection flags, validity mapping, selection behavior, advance behavior, and refusal behavior.

Also create `design_decisions.md` documenting:

- why Task 003 consumes root-state results instead of raw coefficients
- why repeated roots become `projection_tangent_contact` with `advance_valid=False`
- why `constant_identity` has `root_exists=True` but `projection_defined=False`
- why Task 003 does not impose positive, nearest, nonzero, or principal-root policy
- why selected roots are obtained through Task 002 selection rather than recomputing formulas

## Acceptance Criteria

Task 003 is complete only when:

1. `exact_quadratic_projection(root_state_result, branch)` consumes a validated Task 002 root-state result.
2. Raw coefficients, scalar roots, and unrelated typed results are rejected through the existing protocol/error/refusal path.
3. The projection result emits only the seven required projection statuses after input protocol validation.
4. Branch compatibility is explicit and branch requests are preserved in output evidence.
5. Successful projection uses Task 002 `select_quadratic_root(...)` or an equivalent explicit selection protocol path.
6. Task 003 does not recompute the quadratic formula or divide projective coordinates directly.
7. Projection flags distinguish `root_exists`, `projection_defined`, `selected_root_valid`, and `advance_valid`.
8. `projection_tangent_contact` has `selected_root_valid=True` and `advance_valid=False`.
9. `projection_identity` has `root_exists=True` and `projection_defined=False`.
10. Incompatible branches produce typed projection refusal behavior with source status and requested branch preserved.
11. Provenance preserves root-state parent trace ID and selected-root child trace ID when selection succeeds.
12. Serialization preserves projection flags, branch evidence, validity, conditioning, provenance, and refusal evidence.
13. No hidden tolerance, clamp, rescue, branch policy, fallback branch, or legacy pathway exists.
14. No V3 runtime dependency, fixture comparison, adapter, bridge, or compatibility mode is added.
15. No domain consumer, metrology estimator, branch fingerprint, or K_q calibration is added.
16. Existing Task 000, Task 001, and Task 002 behavior remains green.
17. Task 003 reports are written under `Build_Docs/Reports/task003/`.
18. Task-specific tests, full-suite tests, and source-only audits all pass.
