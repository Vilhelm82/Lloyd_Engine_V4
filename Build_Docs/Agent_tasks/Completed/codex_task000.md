# Codex Task 000: Lloyd V4 Bootstrap - Axioms, Typed Geometry Kernel, and M0 Skeleton

## Target repository

```text
/mnt/fast/Lloyd_Engine_V4
```

Place this task file at:

```text
/mnt/fast/Lloyd_Engine_V4/Build_Docs/Agent_tasks/codex_task000.md
```

## Mission

Bootstrap Lloyd V4 as a clean, domain-agnostic typed numerical geometry engine.

This is not V3 cleanup.
This is not V3 compatibility work.
This is not a consumer rebuild.
This is not a branch-classifier implementation.

V4 starts from first principles:

> Lloyd V4 treats numerical computation as navigation through stratified geometric spaces under finite-precision observation.

Every computation is a partial map between typed geometric spaces. A computation may return a scalar, vector, projective state, subspace, root state, branch fingerprint, typed refusal, or protocol violation. A scalar is only valid when the domain, stratum, validity, conditioning, and protocol permit scalarization.

Task 000 exists to create the clean foundation: the axioms, the status calculus, the protocol contract design, the provenance model, the result-type skeleton, and the initial repo structure. Do not prematurely build consumers.

## Non-negotiable design rules

1. **No V3 runtime dependency.**
   V3 is reference-only evidence: frozen targets, known dirty equations, theorem notes, and historical reports. V4 must not import, call, bridge to, or adapt V3.

2. **No legacy compatibility layer.**
   Do not add `safe_mask`, `projection_mode="legacy"`, legacy adapters, downgrade shims, or compatibility wrappers.

3. **No domain-specific consumer.**
   Do not build bearing diagnostics, centrifuge tooling, betting scanners, V3 flow replicas, aerospace consumers, K_G preamps, or application-specific diagnostics in Task 000.

4. **No hidden guard rails.**
   No secret epsilons, clamp floors, denominator foam, discriminant laundering, or tolerance-as-rescue. Declared measurement resolution is allowed only as an instrument property that affects typed status resolution, not as a way to convert invalid geometry into valid scalar output.

5. **Typed refusal is first class.**
   If no honest scalar exists, V4 should be able to say so as a typed result, not as `NaN`, exception-only behavior, or boolean failure.

6. **Protocols are load-bearing.**
   A primitive emits typed statuses. A consumer declares which statuses it can consume. Unhandled strata are protocol violations, not numerical surprises.

7. **Status calculus belongs in M0.**
   Do not defer composition rules until after primitives are built. Even a minimal calculus is required before ProjectiveRatio or StratifiedQuadraticRoots are implemented.

8. **Provenance is structural.**
   Precision, backend, device, expression path, operation identity, measurement resolution, and parent provenance must be represented as part of the substrate design. Provenance must not explode combinatorially, and it must not be silently dropped.

9. **Zero means measured zero only when justified.**
   V4 must distinguish `identity_zero`, `below_limit_of_detection`, `indeterminate`, and `detected_nonzero`. This is design-only in Task 000, but the vocabulary must exist.

10. **Proxy observables are guilty until calibrated.**
    The design must include the principle that a proxy observable is not equivalent to a direct transfer observable unless its calibration factor is tested, for example via stability of `D log K_q(f)`.

## Core thesis to preserve

The Lloyd framework is not V3. V3 demonstrated pieces of the framework.

The framework is the typed geometric relation and its supporting calculus. V4 should implement it more honestly.

The relation:

```text
D ⊕ S = P
```

survives as an algebraic relation between typed geometric objects. D, S, and P become typed values with strata, validity, conditioning, and provenance. K_G is demoted from central identity to one observable or scalar projection among many. Branch fingerprints, path dependence, identifiability, and proxy calibration become first-class substrate concerns.

## Task 000 deliverables

Create the initial repository structure and design documents.

Suggested structure:

```text
/mnt/fast/Lloyd_Engine_V4/
  README.md
  pyproject.toml
  Build_Docs/
    Agent_tasks/
      codex_task000.md
    Architecture/
      AXIOMS.md
      DESIGN_THESIS.md
      STATUS_CALCULUS.md
      PROTOCOL_CONTRACTS.md
      PROVENANCE_MODEL.md
      RESULT_TYPES.md
      METROLOGY_PRINCIPLES.md
      V3_REFERENCE_LEDGER.md
      ROADMAP.md
    Reports/
      task000/
        task000_summary.md
        created_files_manifest.csv
        design_decisions.md
        task001_scope_projective_ratio.md
  src/
    lloyd_v4/
      __init__.py
      core/
        __init__.py
        status.py
        validity.py
        conditioning.py
        provenance.py
        result.py
        protocols.py
        calculus.py
        serialization.py
        errors.py
      primitives/
        __init__.py
      metrology/
        __init__.py
      refinery/
        __init__.py
  tests/
    test_task000_docs_exist.py
    test_task000_no_v3_dependency.py
    test_task000_core_smoke.py
    test_task000_strict_serialization.py
```

If the repo already has some of this structure, preserve existing clean work and extend it. Do not overwrite unknown user work without reporting it.

## Task 1: Repository bootstrap

Initialize a minimal Python package if missing.

Requirements:

- Python 3.11+ preferred.
- Keep dependencies minimal.
- Do not require torch in Task 000 unless it is already intentionally part of the environment. The core substrate should be backend-aware but not backend-owned.
- Create a minimal `pyproject.toml` with package metadata and pytest configuration.
- Add `README.md` describing V4 as a typed numerical geometry substrate, not a V3 fork.

The README must include:

```text
Lloyd V4 is a typed numerical geometry kernel.
It has no runtime dependency on Lloyd V3.
It does not preserve legacy V3 compatibility.
It treats computation as partial maps through stratified geometric spaces under finite-precision observation.
```

## Task 2: Write AXIOMS.md

Create `Build_Docs/Architecture/AXIOMS.md`.

It must include at least these axioms:

1. Geometry precedes scalarization.
2. Degeneracy is a stratum, not a failure.
3. Hidden guard rails are forbidden.
4. Validity is multi-field, never one universal boolean.
5. Numerical representation is a path, not the object.
6. Zero must be measured or proven, not assumed.
7. Proxy observables require calibration.
8. Typed results compose by protocols.
9. Type-system failures are real failure modes.
10. V3 is reference evidence only, never a runtime authority.

For each axiom, include:

- statement
- rationale
- what V4 forbids because of it
- what V4 must represent instead

## Task 3: Write DESIGN_THESIS.md

Create `Build_Docs/Architecture/DESIGN_THESIS.md`.

It must describe V4 as:

```text
A typed, stratified geometry kernel where every computation is a partial map between typed geometric spaces with explicit domain, stratum, validity, conditioning, provenance, and protocol contract.
```

Include the four-layer architecture:

```text
Layer 0: Core typed substrate
Layer 1: Primitive geometric operations
Layer 2: Metrology and transfer
Layer 3: Consumers
```

Make clear that Task 000 only builds Layer 0 scaffolding and architecture docs.

Also include the initial primitive order:

```text
M1: ProjectiveRatio
M2: StratifiedQuadraticRoots
M3: ProjectionResultV4
M4: Metrology and branch fingerprint foundation
M5: Protocol-aware refinery
```

## Task 4: Write STATUS_CALCULUS.md

Create `Build_Docs/Architecture/STATUS_CALCULUS.md`.

This is load-bearing. Do not leave it vague.

At minimum, define:

### Status categories

- domain status
- stratum status
- validity status
- conditioning status
- metrology status
- protocol status
- provenance status

### Minimal composition rules

Include first-pass rules such as:

- Undefined domain blocks scalarization.
- Domain strata must not be silently converted into numeric values.
- Invalid input status propagates unless a primitive explicitly handles that stratum.
- A consumer must declare accepted statuses.
- Unhandled status produces `ProtocolViolation`.
- Conditioning warnings propagate unless explicitly resolved.
- Measurement-resolution statuses are not the same as mathematical degeneracies.
- Status joins must be explicit and named.
- Unknown or mixed status is not silently accepted.

### Required early examples

Use abstract examples only:

- ratio `n/d` with finite, infinite-directional, indeterminate, and signed-zero strata.
- quadratic root strata: two-real-roots, repeated-root, no-real-root, linear-root, constant-identity, constant-no-solution.
- proxy observable with calibrated versus uncalibrated status.

Do not implement these primitives yet unless creating placeholder enums. This document defines the calculus for the upcoming tasks.

## Task 5: Write PROTOCOL_CONTRACTS.md

Create `Build_Docs/Architecture/PROTOCOL_CONTRACTS.md`.

Define what a protocol declaration is.

The design should aim toward static checkability, while allowing strict runtime validation in early Python implementation.

Include:

- producer protocol
- consumer protocol
- accepted status set
- required fields
- forbidden scalarizations
- exhaustive handling requirement
- protocol violation result
- protocol uncertainty result
- how tests should verify exhaustiveness

Provide pseudocode examples:

```python
class ConsumerProtocol:
    accepted_strata: set[StatusCode]
    required_validity_fields: set[str]
    scalarization_allowed: bool
```

and:

```python
def validate_protocol(result: TypedResult, consumer: ConsumerProtocol) -> ProtocolCheck:
    ...
```

Do not create adapters to V3.

## Task 6: Write PROVENANCE_MODEL.md

Create `Build_Docs/Architecture/PROVENANCE_MODEL.md`.

This must address the hard part: how provenance propagates without combinatorial explosion.

Required concepts:

- operation_id
- expression_path
- precision
- backend
- device
- measurement_resolution
- parent provenance references
- trace_id or hash
- provenance compaction
- provenance equivalence classes
- lost provenance as an explicit status, not silent omission

State that provenance supports later precision/path attribution:

```text
C_{p,k} = a + u_p b_k
```

but Task 000 does not implement that estimator.

## Task 7: Write RESULT_TYPES.md

Create `Build_Docs/Architecture/RESULT_TYPES.md`.

Define the intended base objects:

- `TypedResult`
- `StatusTensor` or equivalent status carrier
- `Validity`
- `Conditioning`
- `Provenance`
- `ProtocolCheck`
- `ScalarizationResult`
- `TypedRefusal`

Explain that `TypedResult.value` is not necessarily scalar and may be absent where no honest value exists.

## Task 8: Write METROLOGY_PRINCIPLES.md

Create `Build_Docs/Architecture/METROLOGY_PRINCIPLES.md`.

Include principles for:

- finite-precision observation
- declared measurement resolution
- precision/path attribution
- `b_k` noise floor and limit of detection
- identity zero versus below-noise zero
- proxy calibration via `K_q`
- finite-window and finite-step bias
- direct transfer versus proxy observable

This is design groundwork only. No full estimators in Task 000.

## Task 9: Write V3_REFERENCE_LEDGER.md

Create `Build_Docs/Architecture/V3_REFERENCE_LEDGER.md`.

This document must state:

- V3 is reference-only.
- V4 must not import or call V3.
- V3 targets may be copied as static fixtures.
- V3 known dirty equations are evidence, not architecture.
- V4 may deliberately diverge from V3 if the typed result is more honest.

Include initial known evidence from the prior V3 work:

- `stratified_quadratic_roots` was the first true ingot.
- `safe_mask` was retired as a source of truth in V3 Pass11.
- V3 Pass08 integrated stratified quadratic projection in legacy-compatible mode.
- V3 Pass09 introduced exact projection mode.
- V3 Pass10 validated CUDA performance and tensor-native cleanup.
- V3 Pass11 made exact projection mode default.
- V4 should not inherit V3 legacy modes.

Do not create live links or imports to V3.

## Task 10: Write ROADMAP.md

Create `Build_Docs/Architecture/ROADMAP.md`.

Proposed milestones:

```text
M0: Axioms, status calculus, protocols, provenance, result types
M1: ProjectiveRatio primitive and scalarization refusal
M2: StratifiedQuadraticRoots without legacy mode
M3: ProjectionResultV4 and exact projection protocol
M4: Metrology foundation: b_k noise floor and K_q calibration
M5: BranchFingerprint object and slope-flow model comparison
M6: Protocol-aware equation refinery
M7: History-aware status traces
M8: First domain consumer, chosen only after substrate stabilizes
```

Make M1 explicit: ProjectiveRatio is the first primitive because division is the smallest place where scalar numerics lies.

## Task 11: Create minimal core skeleton

Create minimal Python files under `src/lloyd_v4/core/`.

Keep them tiny. The goal is not full implementation yet.

Suggested minimum:

### `status.py`

Define basic enums or string enums for:

- `DomainStatus`
- `ValidityStatus`
- `ConditioningStatus`
- `MetrologyStatus`
- `ProtocolStatus`

Also define placeholder projective ratio and quadratic root status enums for documentation/test visibility, but do not implement primitives yet.

### `validity.py`

Define a small immutable `Validity` dataclass with optional fields:

- `defined`
- `finite`
- `selectable`
- `advanceable`
- `observable`

Use `Any` or a simple `ArrayLike` alias for now. Do not force torch dependency in Task 000.

### `provenance.py`

Define a small immutable `Provenance` dataclass with:

- `operation_id`
- `expression_path`
- `precision`
- `backend`
- `device`
- `measurement_resolution`
- `parents`
- `trace_id`

Include a helper to derive a stable trace id from fields if feasible.

### `result.py`

Define `TypedResult` with:

- `value`
- `space`
- `status`
- `validity`
- `conditioning`
- `provenance`
- `protocol`

Also define `TypedRefusal` or a refusal status object.

### `protocols.py`

Define minimal protocol declaration classes:

- `ProducerProtocol`
- `ConsumerProtocol`
- `ProtocolCheck`
- `validate_protocol(...)`

Runtime validation is acceptable for M0. Leave hooks for static checkability.

### `calculus.py`

Define minimal named status composition helpers:

- `join_statuses(...)`
- `propagate_invalid(...)`
- `require_handled_status(...)`

These can be conservative stubs, but they must not silently accept unknown statuses.

### `serialization.py`

Define strict JSON-safe serialization helpers. Non-finite floats must be encoded safely, not emitted raw.

### `errors.py`

Define:

- `ProtocolViolationError`
- `ScalarizationError`
- `HiddenGuardRailError`
- `UnhandledStratumError`

Do not overbuild. Tiny and clean.

## Task 12: Add tests

Add minimal tests under `tests/`.

Required tests:

1. Design docs exist.
2. No source file imports `lloyd_v3` or V3 paths.
3. No source file defines `safe_mask`.
4. `TypedResult` can be created with a refusal status.
5. `Provenance` can be created and serialized.
6. Protocol validation rejects unhandled statuses.
7. Strict JSON serialization does not emit raw NaN or Infinity.
8. Status enums include ProjectiveRatio and QuadraticRoot status names for upcoming tasks.

Do not write broad brittle tests. Task 000 tests should protect the birth constraints.

## Task 13: Report

Write:

```text
Build_Docs/Reports/task000/task000_summary.md
Build_Docs/Reports/task000/created_files_manifest.csv
Build_Docs/Reports/task000/design_decisions.md
Build_Docs/Reports/task000/task001_scope_projective_ratio.md
```

`task000_summary.md` must include:

- what was created
- tests run
- any deviations from this task
- unresolved design questions
- whether Task 001 is ready

`design_decisions.md` must include decisions on:

- static versus runtime protocol checking
- status calculus minimum viable rules
- provenance propagation strategy
- no V3 runtime dependency
- no legacy adapters

`task001_scope_projective_ratio.md` must scope the next task:

```text
Implement ProjectiveRatio as the first primitive.
Represent n/d as a projective state, not a scalar.
Statuses: finite_ratio, signed_zero, infinite_direction, indeterminate.
Scalarization must be explicit and may refuse.
No eps, no denominator floor, no hidden guard rail.
```

## Verification commands

Run from repo root:

```bash
python -m pytest tests -q
```

If no virtual environment exists, report the environment and run with the available Python interpreter. Do not create huge dependency stacks.

Also run a source audit:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|epsilon|eps" src tests Build_Docs -n
```

The audit may find these terms inside documentation as forbidden concepts. It must not find them as implementation mechanisms in `src/lloyd_v4`.

## Acceptance criteria

Task 000 succeeds if:

1. V4 repo has a clean package skeleton.
2. Architecture docs exist and clearly define the axioms, status calculus, protocols, provenance model, result types, metrology principles, V3 reference-only stance, and roadmap.
3. No V3 runtime imports or cross-engine calls exist.
4. No legacy compatibility layer exists.
5. No domain consumer is implemented.
6. Minimal core result/protocol/status skeleton exists.
7. Tests pass.
8. Task 001 scope for ProjectiveRatio is written.
9. Reports are written under `Build_Docs/Reports/task000/`.

## Forbidden in Task 000

Do not:

- import V3
- call V3
- create adapters
- create a legacy compatibility mode
- implement bearing diagnostics
- implement centrifuge tooling
- implement betting scanner logic
- implement V3 flow clone
- implement K_G as central scalar identity
- implement ProjectiveRatio fully unless explicitly required by tests as a stub
- implement StratifiedQuadraticRoots fully
- hide invalid geometry behind epsilons or clamps
- make `safe_mask` a V4 field
- make a scalar the default output of every computation

## Philosophical note

The smallest object that refuses to lie is a ratio.

Task 000 prepares the language.
Task 001 will build the first word:

```text
ProjectiveRatio(n, d)
```

A ratio is not always a scalar.
That is the first V4 truth.
