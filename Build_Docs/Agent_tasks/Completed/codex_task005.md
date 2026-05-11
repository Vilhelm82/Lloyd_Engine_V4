# Codex Task 005: Status-Family Typing and Named Transition Calculus

## Repository

Work in:

```text
/mnt/fast/Lloyd_Engine_V4
```

This is Lloyd Engine V4 clean-room work. V3 is reference evidence only. Do not import, call, bridge, compare against, adapt, or depend on V3 at runtime. Do not add legacy adapters, compatibility shims, downgrade modes, or cross-engine calls.

## Current verified baseline

Task 000 is complete. The M0 core substrate exists: statuses, validity, conditioning, provenance, typed results/refusals, protocol validation, conservative status calculus, strict serialization, and core errors.

Task 001 is complete. `ProjectiveRatio(n, d)` exists as the first primitive. It preserves raw projective coordinates `[n:d]`, classifies exact projective strata without dividing by `d`, and scalarizes only through an explicit protocol that may refuse.

Task 002 is complete. `StratifiedQuadraticRoots` exists as the second Layer 1 primitive. `stratified_quadratic_roots(a, b, c)` returns a typed root-state result with raw coefficients, discriminant evidence, branch-labeled projective root coordinates, validity, conditioning, and provenance. `select_quadratic_root(result, branch)` is explicit and protocol-validated.

Task 003 is complete. `ProjectionResultV4` and the exact quadratic projection protocol exist under `src/lloyd_v4/projection`. `exact_quadratic_projection(root_state_result, branch)` consumes validated Task 002 root-state results, rejects raw tuples/scalars/unrelated typed results, calls Task 002 selection for selectable branches, and emits structured projection results with separate `root_exists`, `projection_defined`, `selected_root_valid`, and `advance_valid` flags.

Task 004 is complete. The Layer 2 metrology foundation exists under `src/lloyd_v4/metrology`. It implements declared and estimated `b_k` noise-floor evidence, limit-of-detection classification with explicit `identity_evidence`, pointwise `K_q` calibration through ProjectiveRatio plus explicit scalarization, `proxy_uncalibrated(...)`, and `require_valid_proxy_calibration(...)`.

Task 004 verification baseline:

```text
Task 004 slice: 30 passed
Full suite: 95 passed
Clean-room, hidden-correction, dependency-direction, deferred-feature, and metrology leakage audits: no matches
```

Task 005 now implements:

```text
Status-family typing and named transition calculus
```

BranchFingerprint object and slope-flow model comparison are deferred to Task 006.

## Why Task 005 exists

M0 deliberately chose strict runtime protocol validation before static protocol checking. M0 also deliberately chose a conservative status calculus where empty joins, mixed joins, and unhandled statuses fail explicitly.

That was the correct substrate for Tasks 000 through 004. The first primitives have now exposed the stable contract surface:

```text
ProjectiveRatio scalarization
Quadratic root selection
Quadratic root-state to ProjectionResultV4 mapping
b_k noise-floor classification
K_q valid-calibration requirement
```

These are no longer hypothetical composition cases. They are real transition rules.

Task 005 hardens the core before BranchFingerprint begins mixing projection, metrology, calibration, and transfer-observable evidence.

## Goal

Implement status-family typing and named status-transition rules without changing existing semantics.

Task 005 should make the following more explicit:

```text
A ProjectiveRatio result carries a ProjectiveRatio status family.
A quadratic root-state result carries a QuadraticRoot status family.
A projection result carries a Projection status family.
A metrology result carries a Metrology status family.
A protocol declares the status family and status set it can consume.
A mixed-status composition is legal only through a named transition rule.
Generic mixed joins remain conservative and refuse.
```

Task 005 must preserve all behavior from Tasks 001 through 004. This is a hardening task, not a semantic rewrite.

## Design principles

- Geometry precedes scalarization.
- Degeneracy is a stratum, not failure.
- Typed results compose by protocols.
- Protocol contracts should be status-family aware.
- Runtime validation remains authoritative.
- Static typing support should improve, but must not replace runtime checks.
- Named transition rules should document and enforce known composition paths.
- Generic mixed-status joins must remain conservative.
- No universal status lattice in Task 005.
- No new mathematical primitive in Task 005.
- No metrology reclassification of exact algebraic strata.
- No BranchFingerprint, slope-flow comparison, finite-eta correction, equation refinery, or domain consumer in Task 005.
- No hidden epsilons, denominator floors, discriminant floors, clamps, rescue constants, default branch policies, or compatibility modes.

## Required package boundary

Core generic typing and transition machinery belongs in core.

Expected core files to modify or add:

```text
src/lloyd_v4/core/result.py
src/lloyd_v4/core/protocol.py
src/lloyd_v4/core/calculus.py
src/lloyd_v4/core/transitions.py
src/lloyd_v4/core/__init__.py
```

Use existing filenames if the repository already has equivalent modules. Do not create duplicate concepts under new names if an existing core module is the right home.

Family-specific aliases and transition-rule constants may live near the family they describe:

```text
src/lloyd_v4/primitives/projective_ratio.py
src/lloyd_v4/primitives/stratified_quadratic_roots.py
src/lloyd_v4/projection/exact_projection.py
src/lloyd_v4/metrology/noise_floor.py
src/lloyd_v4/metrology/proxy_calibration.py
```

Core may define the generic machinery. Core must not import primitive, projection, or metrology implementation modules to register their rules. Dependency direction must stay clean.

Earlier layers must not import later layers:

```text
primitives must not import projection
primitives must not import metrology
projection must not import metrology
core must not import implementation modules from primitives/projection/metrology
```

It is acceptable for tests to import all public APIs to verify registration and behavior.

## Part A: TypedResult generic status-family support

Update `TypedResult` so it can be parameterized by value type and status enum family.

Recommended shape:

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

ValueT = TypeVar("ValueT")
StatusT = TypeVar("StatusT", bound=Enum)

@dataclass(frozen=True)
class TypedResult(Generic[ValueT, StatusT]):
    value: ValueT
    status: StatusT
    ...
```

Exact syntax may vary to match the existing codebase. The important requirements are:

```text
TypedResult is generic over value type.
TypedResult is generic over status enum family.
Existing construction call sites keep working.
Existing runtime attributes keep the same names.
Existing serialization stays unchanged.
No generic metadata is serialized.
```

Keep the existing runtime `StatusCode` union or equivalent if it is useful for validation, serialization, or compatibility with existing code. Do not remove runtime validation simply because type hints now exist.

### Required public result aliases

Add concrete aliases or lightweight exported type aliases for the existing result families.

Names may vary if the codebase style requires, but the public typing surface must exist.

Recommended aliases:

```python
ProjectiveRatioResult = TypedResult[ProjectiveRatioValue, ProjectiveRatioStatus]
QuadraticRootStateResult = TypedResult[QuadraticRootStateValue, QuadraticRootStatus]
ProjectionResultV4 = TypedResult[ProjectionResultValue, ProjectionStatus]
NoiseFloorResult = TypedResult[NoiseFloorValue, MetrologyStatus]
LimitOfDetectionResult = TypedResult[LimitOfDetectionValue, MetrologyStatus]
ProxyCalibrationResult = TypedResult[ProxyCalibrationValue, MetrologyStatus]
```

If existing value class names differ, use the actual names and document them in the Task 005 report.

If an operation currently returns a refusal result with `value=None` or a core refusal value, preserve the existing behavior. Do not invent new refusal status families unless existing core machinery already requires it.

### Static typing expectation

Task 005 should improve static type readability and future static checkability. It does not need to make Python prove every accepted status subset.

Do not add a new external dependency solely for static checking. If `mypy`, `pyright`, or another checker is already configured in the project, add a small smoke test or documented command. If no checker is configured, add import/introspection tests that verify aliases are parameterized and importable.

Runtime validation remains mandatory either way.

## Part B: Status-family-aware protocol contracts

Enhance protocol contracts so they declare the status family they consume or emit.

Recommended protocol fields:

```python
status_family: type[Enum]
emitted_statuses: frozenset[Enum] | None
accepted_statuses: frozenset[Enum]
refused_statuses: frozenset[Enum] | None
```

Exact names may vary. Preserve existing protocol behavior and public API where possible.

Protocol validation must reject:

```text
raw values that are not TypedResult objects
TypedResult objects with a status from the wrong enum family
TypedResult objects with a status in the correct family but outside the accepted set
TypedResult objects from an incompatible producer protocol when producer identity is already checked by the existing code
```

Wrong-family rejection should happen before or alongside accepted-set rejection. The error/refusal reason should make the mismatch clear enough for tests to assert it is a family/protocol mismatch, not a scalar failure.

Do not weaken existing protocol validation. Do not make protocols accept multiple unrelated status families unless a current core protocol already does so for a documented reason.

## Part C: Named status-transition rules

Add named status-transition rule machinery.

This is not a universal status lattice. It is a registry or set of explicit contracts for known composition paths.

Recommended core value objects:

```python
TransitionDisposition
StatusTransitionRule
StatusTransitionOutcome
```

Recommended dispositions:

```text
mapped
accepted
refused
not_applicable
```

Use an enum or frozen literals according to the existing style.

Recommended `StatusTransitionRule` fields:

```python
rule_id: str
input_status_family: type[Enum]
output_status_family: type[Enum] | None
input_protocol_id: str | None
output_protocol_id: str | None
accepted_input_statuses: frozenset[Enum]
refused_input_statuses: frozenset[Enum]
mapped_statuses: Mapping[Enum, Enum]
context_keys: tuple[str, ...]
description: str
```

Exact implementation may vary, but the rule object must be immutable and serializable or at least introspectable for tests.

A rule is complete when every status emitted by its declared input protocol is either:

```text
accepted
mapped
explicitly refused
explicitly marked not applicable for that protocol
```

Do not require a rule to cover every status in a broad enum family when the producer protocol emits only a subset. This matters for `MetrologyStatus`, where noise-floor evidence, limit-of-detection evidence, and proxy-calibration evidence share a family but are distinct producer protocols.

### Required transition-rule functions

Add core helpers equivalent to:

```python
assert_transition_rule_complete(rule: StatusTransitionRule) -> None
apply_status_transition(rule: StatusTransitionRule, status: Enum, **context) -> StatusTransitionOutcome
```

Optional registry helpers are allowed:

```python
register_status_transition_rule(rule: StatusTransitionRule) -> StatusTransitionRule
get_status_transition_rule(rule_id: str) -> StatusTransitionRule
```

If a registry is added, avoid import-time cycles. Family-specific modules may expose their own rule constants instead of relying on global auto-registration.

`apply_status_transition(...)` must reject statuses from the wrong family. It must not silently coerce by name string.

For context-dependent transitions, such as branch-specific projection, the transition rule may declare required context keys rather than encoding every branch case as a flat status map.

## Required canonical transition rules

Backfill named transition rules for the real protocol transitions from Tasks 001 through 004.

### 1. ProjectiveRatio scalarization

Rule ID recommendation:

```text
projective_ratio.scalarization
```

Input protocol:

```text
PROJECTIVE_RATIO_PROTOCOL
```

Consumer protocol:

```text
PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL
```

Accepted inputs:

```text
finite_ratio
signed_zero
```

Refused inputs:

```text
infinite_direction
indeterminate
```

Behavior must remain unchanged:

```text
finite_ratio and signed_zero scalarize explicitly
infinite_direction refuses with no scalar infinity
indeterminate refuses with no NaN or numeric sentinel
```

### 2. Quadratic root selection

Rule ID recommendation:

```text
quadratic_roots.selection
```

Input protocol:

```text
STRATIFIED_QUADRATIC_ROOTS_PROTOCOL
```

Consumer protocol:

```text
QUADRATIC_ROOT_SELECTION_PROTOCOL
```

Selectable statuses:

```text
two_real_roots
repeated_root
linear_root
```

Nonselectable/refused statuses:

```text
no_real_root
constant_identity
constant_no_solution
```

Branch compatibility remains contextual:

```text
two_real_roots accepts minus and plus
repeated_root accepts repeated
linear_root accepts linear
incompatible branch labels refuse through existing typed refusal behavior
```

The rule should document that branch compatibility is part of context and not a generic status join.

### 3. Quadratic root-state to ProjectionResultV4

Rule ID recommendation:

```text
quadratic_roots.to_exact_projection
```

Input protocol:

```text
STRATIFIED_QUADRATIC_ROOTS_PROTOCOL
```

Output protocol:

```text
EXACT_QUADRATIC_PROJECTION_PROTOCOL
```

Required status mapping:

```text
two_real_roots + compatible minus/plus branch -> projection_transverse
repeated_root + compatible repeated branch -> projection_tangent_contact
linear_root + compatible linear branch -> projection_linear
no_real_root -> projection_no_real_root
constant_identity -> projection_identity
constant_no_solution -> projection_no_solution
selectable source with incompatible branch -> projection_selection_refused
```

Preserve Task 003 semantics:

```text
projection_tangent_contact has selected_root_valid=True and advance_valid=False
projection_identity has root_exists=True and projection_defined=False
```

Do not add principal-root, nearest-root, positive-time, default-branch, or auto-branch policies.

### 4. b_k noise-floor to limit-of-detection classification

Rule ID recommendation:

```text
metrology.noise_floor.limit_of_detection
```

Input producer protocols:

```text
B_K_NOISE_FLOOR_PROTOCOL
```

Output protocol:

```text
LIMIT_OF_DETECTION_PROTOCOL
```

Applicable input statuses:

```text
noise_floor_declared
noise_floor_estimated
noise_floor_indeterminate
```

Contextual output statuses:

```text
detected
below_limit_of_detection
detection_indeterminate
identity_zero
```

Preserve Task 004 semantics:

```text
abs(observable) > L -> detected
abs(observable) <= L and L > 0 -> below_limit_of_detection
indeterminate floor -> detection_indeterminate
zero observable with zero floor and no identity evidence -> detection_indeterminate
exact zero observable with identity_evidence=True -> identity_zero
nonzero observable with identity_evidence=True -> protocol error
```

Metrology must not reclassify exact ProjectiveRatio, quadratic-root, or projection strata.

### 5. K_q valid proxy calibration requirement

Rule ID recommendation:

```text
metrology.proxy_calibration.require_valid
```

Input producer protocols:

```text
K_Q_PROXY_CALIBRATION_PROTOCOL
PROXY_UNCALIBRATED_PROTOCOL
```

Consumer protocol:

```text
VALID_PROXY_CALIBRATION_PROTOCOL
```

Accepted inputs:

```text
calibration_valid
```

Refused inputs:

```text
calibration_invalid
calibration_indeterminate
proxy_uncalibrated
```

Preserve Task 004 semantics:

```text
calibration_valid means finite nonzero pointwise K_q only
calibration_invalid refuses without scalar infinity
calibration_indeterminate refuses without NaN or numeric sentinel
proxy_uncalibrated refuses as missing typed evidence, not an exception
```

Do not add slope-flow stability or branch-fingerprint inference.

## Conservative calculus requirement

Keep `join_statuses(...)` conservative.

The following must remain true:

```text
empty joins fail explicitly
mixed families fail explicitly
unhandled mixed statuses fail explicitly
same-status joins may pass only if current M0 behavior already permits them
```

Task 005 may add named transition helpers, but it must not make `join_statuses(...)` magically combine arbitrary statuses.

Good:

```text
apply named transition rule quadratic_roots.to_exact_projection
```

Bad:

```text
join_statuses(two_real_roots, calibration_valid) -> some inferred mixed status
```

The calculus goblin is allowed to carry a clipboard. It is not allowed to invent mathematics.

## Serialization requirements

Existing serialized results from Tasks 001 through 004 must remain backward-compatible.

Do not serialize:

```text
TypeVar objects
Generic aliases
__orig_class__
Python typing internals
private registry memory addresses
```

If transition rules are serialized for reports or tests, use plain data:

```text
rule_id
input_status_family name
output_status_family name
accepted status names
refused status names
mapped status names
context keys
description
```

Do not alter existing result JSON shape unless strictly necessary. Any unavoidable serialization change must be documented in `Build_Docs/Reports/task005/design_decisions.md` and covered by tests.

## Tests to add

Add a Task 005 test slice under `tests/`.

Recommended files:

```text
tests/test_task005_typed_result_generics.py
tests/test_task005_protocol_status_families.py
tests/test_task005_status_transition_rules.py
tests/test_task005_transition_rule_coverage.py
tests/test_task005_existing_flows_still_pass.py
tests/test_task005_source_purity.py
```

Use actual filenames if repository style suggests alternatives.

### Required red tests before implementation

The first run of the Task 005 slice should fail before implementation because status-family generic aliases and/or transition-rule machinery do not exist.

Record that red result in the Task 005 summary.

### TypedResult generic tests

Verify:

```text
TypedResult can be parameterized by value type and status family
existing unparameterized construction still works
family-specific result aliases import successfully
ProjectiveRatioResult alias points to ProjectiveRatioValue and ProjectiveRatioStatus
QuadraticRootStateResult alias points to root-state value and QuadraticRootStatus
ProjectionResultV4 alias points to ProjectionResultValue and ProjectionStatus
metrology aliases point to their value types and MetrologyStatus
serialization does not emit generic typing internals
```

If static type checker tooling is already configured, add a smoke command. If not configured, do not install new static-check dependencies for Task 005.

### Protocol family tests

Verify:

```text
ProjectiveRatio protocols reject statuses from ProjectionStatus and MetrologyStatus
Quadratic root selection rejects ProjectiveRatioResult and ProjectionResultV4 inputs
exact_quadratic_projection still rejects raw tuples, scalar roots, and unrelated typed results
metrology protocols reject projection/root/projective results where typed metrology evidence is required
family mismatch errors/refusals are explicit and not silent accepted-set failures
```

Do not weaken existing runtime protocol validation.

### Transition rule tests

Verify the canonical transition rules exist and are complete against their producer protocols:

```text
projective_ratio.scalarization covers all ProjectiveRatio producer statuses
quadratic_roots.selection covers all quadratic root-state producer statuses
quadratic_roots.to_exact_projection covers all quadratic root-state producer statuses
metrology.noise_floor.limit_of_detection covers noise-floor producer statuses
metrology.proxy_calibration.require_valid covers proxy-calibration/uncalibrated producer statuses
```

Verify wrong-family status application fails:

```text
apply projective_ratio.scalarization to projection_transverse -> protocol/family violation
apply quadratic_roots.to_exact_projection to calibration_valid -> protocol/family violation
```

Verify contextual mappings preserve existing behavior:

```text
two_real_roots + minus -> projection_transverse
two_real_roots + plus -> projection_transverse
two_real_roots + repeated -> projection_selection_refused
repeated_root + repeated -> projection_tangent_contact
repeated_root + minus -> projection_selection_refused
linear_root + linear -> projection_linear
no_real_root -> projection_no_real_root
constant_identity -> projection_identity
constant_no_solution -> projection_no_solution
```

Verify metrology contextual transitions preserve Task 004 behavior:

```text
positive observable above declared floor -> detected
observable on or below declared floor -> below_limit_of_detection
empty estimated floor -> detection_indeterminate
zero observable with zero floor and no identity evidence -> detection_indeterminate
zero observable with identity_evidence=True -> identity_zero
nonzero observable with identity_evidence=True -> protocol error
calibration_valid passes require_valid_proxy_calibration
calibration_invalid refuses
calibration_indeterminate refuses
proxy_uncalibrated refuses
```

### Existing flow tests

Re-run representative flows from Tasks 001 through 004:

```text
projective_ratio -> scalarize_projective_ratio
stratified_quadratic_roots -> select_quadratic_root
stratified_quadratic_roots -> exact_quadratic_projection
calibrate_proxy_kq -> require_valid_proxy_calibration
classify_against_noise_floor with declared and estimated floors
```

The behavior and serialized results should remain semantically unchanged.

## Required reports

Add:

```text
Build_Docs/Reports/task005/task005_summary.md
Build_Docs/Reports/task005/status_transition_rules.md
Build_Docs/Reports/task005/design_decisions.md
```

`task005_summary.md` must include:

```text
files created
files modified
red test result
Task 005 slice result
full suite result
source audit results
deviations
Task 006 readiness
```

`status_transition_rules.md` must list each canonical rule with:

```text
rule_id
input protocol
output/consumer protocol
input status family
output status family, if applicable
accepted statuses
refused statuses
mapped statuses
context keys
notes on contextual behavior
```

`design_decisions.md` must include at least:

```text
why TypedResult became generic but runtime validation remains mandatory
why StatusCode runtime union was preserved or changed
why generic mixed joins remain conservative
why named transition rules are not a universal status lattice
how contextual transitions are represented
how serialization compatibility was preserved
why BranchFingerprint moved to Task 006
```

## Source audits

Run the full suite:

```bash
python -m pytest tests -q
```

Run the Task 005 slice:

```bash
python -m pytest tests/test_task005_typed_result_generics.py tests/test_task005_protocol_status_families.py tests/test_task005_status_transition_rules.py tests/test_task005_transition_rule_coverage.py tests/test_task005_existing_flows_still_pass.py tests/test_task005_source_purity.py -q
```

If filenames differ, document the exact command in the summary.

Run clean-room audit:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
```

Run hidden-correction audits:

```bash
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard" src/lloyd_v4 -n
```

```bash
rg "disc_floor|discriminant_floor|clamp_discriminant|safe_sqrt|sqrt_guard|small_discriminant|threshold|tolerance" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Run dependency-direction audits:

```bash
rg "lloyd_v4\.metrology|from lloyd_v4\.metrology|import .*metrology" src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

```bash
rg "lloyd_v4\.projection|from lloyd_v4\.projection|import .*projection" src/lloyd_v4/primitives -n
```

Run deferred-feature audit:

```bash
rg "branch_fingerprint|fingerprint|slope_flow|flow_model|finite_eta|domain_consumer|equation_refinery|refinery" src/lloyd_v4 -n
```

This audit should produce no source matches. If a transition-rule report or doc mentions deferred features, that is fine outside `src/`.

Run compatibility/adapters audit:

```bash
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

If the codebase already contains harmless words in comments/docstrings that trip this audit, tighten the regex rather than deleting meaningful core fields or behavior.

## Non-goals

Do not implement:

```text
BranchFingerprint
slope-flow model comparison
finite-eta correction
history-aware status traces
protocol-aware equation refinery
domain consumers
arrays or tensors
symbolic math
arbitrary-precision math
complex roots
new quadratic formulas
new projection branch policies
nearest-root policy
principal-root policy
positive-time flow policy
metrology-based reclassification of exact strata
V3 fixtures
V3 runtime comparison
adapters
compatibility layers
```

Do not change the meaning of:

```text
finite_ratio
signed_zero
infinite_direction
indeterminate
two_real_roots
repeated_root
no_real_root
linear_root
constant_identity
constant_no_solution
projection_transverse
projection_tangent_contact
projection_linear
projection_no_real_root
projection_identity
projection_no_solution
projection_selection_refused
noise_floor_declared
noise_floor_estimated
noise_floor_indeterminate
detected
below_limit_of_detection
detection_indeterminate
identity_zero
calibration_valid
calibration_invalid
calibration_indeterminate
proxy_uncalibrated
```

Task 005 is allowed to make these statuses better typed and better composed. It is not allowed to reinterpret them.

## Acceptance criteria

Task 005 is complete when:

```text
1. TypedResult is generic over value type and status enum family.
2. Existing TypedResult construction and serialization remain backward-compatible.
3. Public result aliases exist for ProjectiveRatio, quadratic root-state, ProjectionResultV4, and metrology result families.
4. Protocol contracts are status-family aware.
5. Runtime protocol validation rejects wrong-family TypedResult inputs explicitly.
6. Core named transition-rule machinery exists.
7. Generic mixed-status joins remain conservative.
8. Canonical transition rules exist for ProjectiveRatio scalarization, quadratic root selection, quadratic root-state projection, b_k limit-of-detection classification, and K_q valid-calibration requirement.
9. Transition-rule completeness tests prove producer statuses are accepted, mapped, refused, or explicitly not applicable.
10. Existing Task 001 through Task 004 behavior remains unchanged.
11. Existing serialization remains semantically unchanged and does not expose typing internals.
12. Task 005 reports are written under Build_Docs/Reports/task005.
13. Task 005 test slice passes.
14. Full test suite passes.
15. Source audits pass with no V3, legacy, hidden correction, dependency-direction, or deferred-feature leakage.
```

## Task 006 readiness

After Task 005, Task 006 should return to the roadmap item:

```text
BranchFingerprint object and slope-flow model comparison
```

Task 006 should consume the new named transition rules instead of inventing local composition maps. It should treat projection, metrology, calibration, and transfer-observable statuses as typed families composed only through declared protocols.
