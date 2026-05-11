# Codex Task 009: TypedProjectionSolver MVP

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

Task 009 is not a V1 solver port. It is the first V4-native solver consumer.

## Current verified baseline

Task 000 is complete. The M0 substrate exists: statuses, validity, conditioning, provenance, typed results/refusals, protocol validation, conservative status calculus, strict serialization, core errors, and architecture docs.

Task 001 is complete. `ProjectiveRatio(n, d)` exists as the first primitive. It preserves raw projective coordinates `[n:d]`, classifies exact projective strata without dividing by `d`, and scalarizes only through an explicit protocol that may refuse.

Task 002 is complete. `StratifiedQuadraticRoots` exists. `stratified_quadratic_roots(a, b, c)` returns a typed root-state result with raw coefficients, discriminant evidence, branch-labeled projective root coordinates, validity, conditioning, and provenance. `select_quadratic_root(result, branch)` is explicit and protocol-validated.

Task 003 is complete. `ProjectionResultV4` and the exact quadratic projection protocol exist. `exact_quadratic_projection(root_state_result, branch)` consumes validated Task 002 root-state results, calls Task 002 selection for selectable branches, and emits structured projection evidence with separate `root_exists`, `projection_defined`, `selected_root_valid`, and `advance_valid` flags.

Task 004 is complete. The Layer 2 metrology foundation exists under `src/lloyd_v4/metrology`. It implements declared and estimated `b_k` noise-floor evidence, limit-of-detection classification with explicit `identity_evidence`, pointwise `K_q` proxy calibration through ProjectiveRatio plus explicit scalarization, `proxy_uncalibrated(...)`, and `require_valid_proxy_calibration(...)`.

Task 005 is complete. `TypedResult` is generic over value type and status enum family. Protocols infer or declare status families and reject wrong-family typed results explicitly. Named transition-rule machinery exists with canonical rules for ProjectiveRatio scalarization, quadratic root selection, quadratic projection, limit-of-detection classification, valid `K_q` calibration, and later layer composition.

Task 006 is complete. The branch package exists under `src/lloyd_v4/branch`. It implements `BranchFingerprintStatus`, slope-flow comparison with ProjectiveRatio-backed segment slopes, declared model residual comparison, `K_q` slope-stability checks using Task 004 calibration evidence, and BranchFingerprint composition through named transition rules. BranchFingerprint is evidence, not a domain classifier.

Task 007 is complete. The refinery package exists under `src/lloyd_v4/refinery`. It implements typed result snapshots, explicit slag vectors, scenario and candidate rewrite decisions, `RefineryStatus`, refinery protocols, named status-preservation transition rules, accepted-rewrite enforcement, and serialization. The refinery consumes supplied typed observations only. It does not parse, simplify, generate, or classify equations.

Task 008 is complete. The history package exists under `src/lloyd_v4/history`. It implements `HistoryStatus`, compact status-event recording, pairwise transition comparison with precedence, ordered trace construction, stable-trace protocol enforcement with typed refusals, history result aliases, protocols, transition rules, and serialization. History observes typed status evolution and does not decide downstream meaning.

Task 008 verification baseline:

```text
Full suite: 177 passed
Required source audits: no matches
```

## Task 009 goal

Implement the first V4-native solver consumer:

```text
TypedProjectionSolver MVP
```

Task 009 should create a small, honest solver/controller that consumes explicitly supplied local quadratic models and existing V4 typed evidence. It must not implement a new automatic differentiation engine, expression parser, symbolic solver, V1 Halley transport, multistart search, or domain consumer.

The solver should answer one narrow question:

```text
Given a sequence of caller-supplied local quadratic step models, can V4 advance by typed projection until it reaches an explicit metrology-backed termination condition, while preserving protocol evidence, branch evidence, optional refinement evidence, and projection-history coherence?
```

This task is the first consumer because it composes the existing V4 layers:

```text
ProjectiveRatio         -> via Task 002 root selection and Task 006 slopes
StratifiedQuadraticRoots -> local quadratic step model
ProjectionResultV4      -> explicit advance validity
Metrology               -> residual observability and convergence evidence
BranchFingerprint       -> optional branch-consistency gate
Refinery                -> optional candidate/rewrite acceptance gate
History                 -> projection-status trace evidence
Named transitions       -> no ad hoc mixed-status joins
```

Task 009 should implement:

```text
1. a SolverStatus family;
2. typed local quadratic step model evidence;
3. typed solver policy evidence with explicit gates;
4. one-step projection evaluation;
5. finite sequence solver execution over caller-supplied models;
6. metrology-backed termination classification;
7. optional BranchFingerprint gate;
8. optional refinery acceptance gate;
9. projection-history trace recording and stable-geometry enforcement;
10. named transition rules for solver decisions;
11. serialization and reports for all new evidence.
```

The MVP solver does not generate local models. The caller supplies local quadratic step models. Future tasks may add `JetBundle`, automatic differentiation, implicit chart projection, or V1-style surface transport as model providers, but Task 009 must not.

## Design principles

- Geometry precedes scalarization.
- Degeneracy is a stratum, not failure.
- Typed results compose by protocols.
- Mixed-status composition must use named transition rules.
- Solver steps are typed evidence transitions, not scalar residual guesses.
- A numerical step is only a candidate. Projection, metrology, branch evidence, refinery evidence, and history evidence decide whether it is acceptable.
- Convergence must be metrology-backed. Do not add an internal residual tolerance.
- `below_limit_of_detection` is not `identity_zero`. Below-detection acceptance requires an explicit solver policy field.
- Tangent contact is not advance-valid. Preserve Task 003 semantics.
- BranchFingerprint evidence is optional in the MVP, but if the policy requires it, incomplete, unidentified, unstable, or proxy-uncalibrated evidence must block advancement or termination through a typed status.
- Refinery evidence is optional in the MVP, but if the policy requires it, only accepted same-geometry lower-slag evidence may pass.
- History observes projection geometry stability. Do not use history as smoothing, hysteresis, forecasting, or a hidden convergence test.
- Existing Task 001 through Task 008 behavior and serialization must remain unchanged.
- No hidden epsilons, tolerance gates, denominator floors, clamps, safe division, rescue constants, log offsets, fallback branches, confidence scores, weighted scores, smoothing, hysteresis, interpolation, extrapolation, symbolic simplification, persistent stores, V1 imports, V3 imports, adapters, or compatibility modes.
- Existing Task 000 `measurement_resolution` provenance metadata remains legitimate substrate metadata. Do not rename or hide it.

## Required package boundary

Create a new package for solver work.

Recommended files:

```text
src/lloyd_v4/solver/__init__.py
src/lloyd_v4/solver/typed_projection_solver.py
```

If the repository has a clearly better naming convention, use it, but do not place solver implementation inside primitives, projection, metrology, branch, refinery, history, or core.

Expected core modification:

```text
src/lloyd_v4/core/status.py
```

Only add the new Solver status family there. Do not add solver algorithms to core.

Task 009 may import earlier layers in this direction:

```text
solver -> core
solver -> primitives
solver -> projection
solver -> metrology
solver -> branch
solver -> refinery
solver -> history
```

Earlier layers must not import solver:

```text
core must not import solver implementation modules
primitives must not import solver
projection must not import solver
metrology must not import solver
branch must not import solver
refinery must not import solver
history must not import solver
```

Task 009 may consume public APIs, result aliases, protocols, and named transition rules from earlier tasks. It must not patch earlier task behavior.

## Required status family

Add a new status enum family. Recommended name:

```python
SolverStatus
```

Required initial statuses:

```text
solver_step_advanced
solver_converged_identity
solver_converged_below_detection
solver_projection_blocked
solver_tangent_blocked
solver_selection_refused
solver_branch_unidentified
solver_proxy_uncalibrated
solver_refinery_rejected
solver_history_unstable
solver_sequence_inconsistent
solver_step_budget_exhausted
solver_protocol_refused
solver_indeterminate
```

These names may be adjusted only if the final report includes a status table proving the same semantic coverage.

### Status meanings

`solver_step_advanced`

A one-step local quadratic model produced a Task 002 root state and a Task 003 projection result whose projection status is advance-valid. The selected root scalar is used as a displacement and the solver records `state_after = state_before + selected_root_value`.

This status is step evidence, not final convergence.

`solver_converged_identity`

The residual observable is classified by Task 004 metrology as `identity_zero` using explicit `identity_evidence=True`. This is the strongest MVP convergence status.

`solver_converged_below_detection`

The residual observable is classified as `below_limit_of_detection`, and the explicit solver policy permits below-detection termination. This does not certify identity-zero.

`solver_projection_blocked`

The local quadratic model maps through Task 002 and Task 003 to a projection result that cannot define an advance. Examples include no real root, constant identity with no unique projection, and constant no-solution.

`solver_tangent_blocked`

The local quadratic model maps to `projection_tangent_contact`. The scalar root may be selected, but Task 003 says `advance_valid=False`, so the solver must not advance.

`solver_selection_refused`

The local model is selectable in principle, but the requested branch is incompatible and Task 002/Task 003 selection refuses.

`solver_branch_unidentified`

The solver policy requires BranchFingerprint evidence, but the supplied fingerprint evidence is missing, incomplete, unidentified, ambiguous/no-match, wrong-family, or otherwise not accepted as complete branch evidence.

`solver_proxy_uncalibrated`

The solver policy requires BranchFingerprint evidence and the relevant branch/proxy evidence is blocked because the proxy is uncalibrated, Kq flow is unstable, Kq flow is indeterminate, or proxy evidence is missing.

`solver_refinery_rejected`

The solver policy requires refinery acceptance and the supplied Task 007 refinery decision is not accepted by the accepted-rewrite protocol.

`solver_history_unstable`

The solver has enough projection events to build a history trace, and the policy requires stable projection geometry, but the resulting trace is transitioned, incomplete, unordered, or refused by the stable-trace protocol.

`solver_sequence_inconsistent`

The caller-supplied model sequence is internally inconsistent. Examples: step indices are not strictly increasing, repeated model identifiers, missing required state evidence, or a next model state that does not exactly equal the previous accepted `state_after` under host Python arithmetic.

`solver_step_budget_exhausted`

The supplied finite model budget was consumed without convergence, projection blocking, typed refusal, or another terminal status. Preserve all accepted step evidence and history evidence.

`solver_protocol_refused`

A required input typed result has the wrong status family, missing protocol identity, invalid protocol, or cannot be consumed by the relevant existing protocol. Preserve refusal evidence.

`solver_indeterminate`

The solver lacks enough honest evidence to advance, converge, or classify one of the more specific statuses. Examples: residual metrology is indeterminate and the solver cannot advance, required local model fields are finite but semantically incomplete, or an existing typed refusal does not map cleanly to a more specific solver status.

## Validity mapping

Use the M0 validity fields consistently.

Recommended mapping:

```text
solver_step_advanced:                defined, finite, selectable, advanceable, observable
solver_converged_identity:           defined, finite, selectable, not advanceable, observable
solver_converged_below_detection:    defined, finite, selectable, not advanceable, observable
solver_projection_blocked:           defined, not finite, not selectable, not advanceable, observable
solver_tangent_blocked:              defined, finite, selectable, not advanceable, observable
solver_selection_refused:            not defined, not finite, not selectable, not advanceable, observable
solver_branch_unidentified:          defined, finite, not selectable, not advanceable, observable
solver_proxy_uncalibrated:           not defined, not finite, not selectable, not advanceable, observable
solver_refinery_rejected:            defined, finite, not selectable, not advanceable, observable
solver_history_unstable:             defined, finite, not selectable, not advanceable, observable
solver_sequence_inconsistent:        not defined, not finite, not selectable, not advanceable, observable
solver_step_budget_exhausted:        defined, finite, not selectable, not advanceable, observable
solver_protocol_refused:             not defined, not finite, not selectable, not advanceable, observable
solver_indeterminate:                not defined, not finite, not selectable, not advanceable, observable
```

If the implementation chooses a different mapping, document the reason in `solver_status_table.md`.

## Required value objects

Use frozen dataclasses or existing repository conventions.

Recommended value objects:

```python
@dataclass(frozen=True)
class LocalQuadraticStepModel:
    model_id: str
    step_index: int
    state_before: float
    a: float
    b: float
    c: float
    branch: str
    residual_observable: float
    identity_evidence: bool = False
    geometry_signature: str | None = None
    branch_fingerprint_result: TypedResult | None = None
    refinery_decision_result: TypedResult | None = None
```

Interpretation:

```text
q(delta) = a * delta**2 + b * delta + c = 0
```

The selected scalar root is interpreted as a displacement `delta`. The step advances by:

```text
state_after = state_before + delta
```

All numeric fields must be finite Python `int` or `float` values. Do not accept non-finite values. Do not coerce string numerics.

Branch labels must match the existing Task 002 branch vocabulary:

```text
minus
plus
repeated
linear
```

The solver must not invent default, nearest, principal, positive, nonzero, fallback, or automatic branch policies.

Recommended policy object:

```python
@dataclass(frozen=True)
class SolverPolicy:
    accept_below_detection: bool = False
    require_branch_fingerprint: bool = False
    require_refinery_acceptance: bool = False
    require_stable_projection_history: bool = True
```

Policy fields are explicit serialized evidence, not hidden defaults. The defaults above are acceptable for API ergonomics only if the policy object is serialized into solver evidence. If the implementation avoids defaults and requires a policy object, that is also acceptable.

Recommended step evidence:

```python
@dataclass(frozen=True)
class SolverStepValue:
    model_id: str
    step_index: int
    state_before: float
    state_after: float | None
    selected_displacement: float | None
    requested_branch: str
    residual_observable: float
    residual_detection_trace_id: str | None
    root_state_trace_id: str | None
    projection_trace_id: str | None
    branch_fingerprint_trace_id: str | None
    refinery_decision_trace_id: str | None
    refusal_trace_id: str | None
    geometry_signature: str | None
    policy: SolverPolicy
```

Recommended run evidence:

```python
@dataclass(frozen=True)
class SolverRunValue:
    initial_state: float | None
    final_state: float | None
    steps: tuple[SolverStepValue, ...]
    terminal_step_index: int | None
    terminal_status: SolverStatus
    projection_history_trace_id: str | None
    policy: SolverPolicy
```

If the repository has a better existing evidence style, use it, but preserve the same information content.

## Required protocols and result aliases

Recommended protocol names:

```text
TYPED_PROJECTION_SOLVER_STEP_PROTOCOL
TYPED_PROJECTION_SOLVER_RUN_PROTOCOL
CONVERGED_SOLVER_PROTOCOL
```

Recommended aliases:

```python
SolverStepResult = TypedResult[SolverStepValue, SolverStatus]
SolverRunResult = TypedResult[SolverRunValue, SolverStatus]
```

Recommended public APIs:

```python
evaluate_solver_step(
    model: LocalQuadraticStepModel,
    noise_floor_result: TypedResult,
    policy: SolverPolicy,
) -> SolverStepResult

run_typed_projection_solver(
    models: Sequence[LocalQuadraticStepModel],
    noise_floor_result: TypedResult,
    policy: SolverPolicy,
) -> SolverRunResult

require_converged_solver(result: SolverRunResult) -> SolverRunResult
```

If naming differs, keep the semantic surface equivalent and document it.

`require_converged_solver(...)` must accept only:

```text
solver_converged_identity
solver_converged_below_detection
```

It must return typed refusal for all other solver statuses.

## Step evaluation algorithm

`evaluate_solver_step(...)` should follow this order.

### 1. Validate the local model

Validate that:

```text
model_id is non-empty
step_index is an integer
state_before is finite
coefficients a, b, c are finite
residual_observable is finite
branch is one of minus, plus, repeated, linear
noise_floor_result is a Task 004 noise-floor typed result
policy is explicit
```

Invalid structural inputs may raise `ProtocolViolationError` if that matches existing core practice. Wrong-family typed results should produce `solver_protocol_refused` if the evidence can be preserved.

### 2. Classify residual observability through Task 004

Use the existing Task 004 limit-of-detection classifier. Do not compare `abs(residual)` directly in solver code.

Required behavior:

```text
identity_zero -> solver_converged_identity
below_limit_of_detection + policy.accept_below_detection=True -> solver_converged_below_detection
below_limit_of_detection + policy.accept_below_detection=False -> continue only if projection evidence can advance; otherwise solver_indeterminate
detected -> continue to projection
detection_indeterminate -> continue only if projection evidence can advance; otherwise solver_indeterminate
wrong-family/noise-floor refusal -> solver_protocol_refused
```

The residual detection result trace ID must be preserved in the solver evidence.

### 3. Apply optional BranchFingerprint gate

If `policy.require_branch_fingerprint` is true:

```text
fingerprint_complete -> continue
fingerprint_proxy_uncalibrated or Kq/proxy refusal evidence -> solver_proxy_uncalibrated
fingerprint_unidentified -> solver_branch_unidentified
fingerprint_incomplete -> solver_branch_unidentified
missing/wrong-family fingerprint evidence -> solver_branch_unidentified or solver_protocol_refused, depending on existing protocol validation style
```

Do not infer a domain branch identity.

If `policy.require_branch_fingerprint` is false, preserve supplied branch fingerprint trace evidence if present, but do not require it.

### 4. Apply optional refinery gate

If `policy.require_refinery_acceptance` is true, validate the supplied Task 007 refinery decision using the accepted-rewrite protocol.

```text
rewrite_accepted_same_geometry_lower_slag -> continue
all other refinery statuses -> solver_refinery_rejected
missing/wrong-family refinery evidence -> solver_refinery_rejected or solver_protocol_refused, depending on existing protocol validation style
```

If `policy.require_refinery_acceptance` is false, preserve supplied refinery trace evidence if present, but do not require it.

### 5. Build and project the local quadratic step

Use the existing Task 002 and Task 003 path:

```python
root_state = stratified_quadratic_roots(model.a, model.b, model.c)
projection = exact_quadratic_projection(root_state, model.branch)
```

Do not recompute quadratic roots in solver code. Do not divide projective root coordinates in solver code. Do not implement an alternate formula.

### 6. Map projection status to solver status

Use a named transition rule.

Required mapping:

```text
projection_transverse      -> solver_step_advanced
projection_linear          -> solver_step_advanced
projection_tangent_contact -> solver_tangent_blocked
projection_no_real_root    -> solver_projection_blocked
projection_identity        -> solver_projection_blocked
projection_no_solution     -> solver_projection_blocked
projection_selection_refused -> solver_selection_refused
```

For `solver_step_advanced`, `state_after` must be:

```text
state_before + selected scalar root value from the projection evidence
```

If a projection status claims advance validity but selected scalar evidence is missing, emit `solver_protocol_refused` or `solver_indeterminate` with preserved evidence. Do not silently recompute the root.

## Run algorithm

`run_typed_projection_solver(...)` consumes a finite sequence of caller-supplied local models.

Required behavior:

```text
1. Empty model sequence -> solver_indeterminate.
2. Models must have strictly increasing step_index in caller order.
3. Evaluate each model with evaluate_solver_step(...).
4. If a terminal convergence/block/refusal status is emitted, stop and return a SolverRunResult.
5. For solver_step_advanced, carry forward state_after.
6. If a next model is supplied, its state_before must exactly equal the previous accepted state_after under host Python arithmetic. Do not use approximate closeness.
7. Preserve all step evidence.
8. Build projection-history events from projection results for accepted projection steps when two or more such events exist.
9. If policy.require_stable_projection_history is true and the projection-history trace is transitioned, incomplete, unordered, or refused, return solver_history_unstable.
10. If all supplied models are consumed and no convergence/block/refusal occurred, return solver_step_budget_exhausted.
```

The exact-equality rule above means exact equality of the provided finite Python values after the solver's own `state_before + displacement` computation. It does not mean symbolic real equality.

History should track projection geometry, not ordinary terminal solver-status changes. A terminal transition from `solver_step_advanced` to `solver_converged_identity` is not itself a projection-geometry instability.

If only one accepted projection event exists, preserve the singleton history evidence if useful, but do not block solely because Task 008 stable-trace protocol refuses singleton traces. Stable projection history is meaningful only when two or more comparable projection events exist.

## Named transition rules

Add Task 009 transition rules using `src/lloyd_v4/core/transitions.py`.

Required rules:

```text
solver.residual_detection.to_solver
solver.projection.to_solver_step
solver.branch_fingerprint.require_complete
solver.refinery.require_accepted
solver.projection_history.require_stable
solver.run.require_converged
```

### solver.residual_detection.to_solver

Input protocol:

```text
limit_of_detection
```

Output protocol:

```text
typed_projection_solver_step
```

Input family:

```text
MetrologyStatus
```

Output family:

```text
SolverStatus
```

Mapped statuses:

```text
identity_zero -> solver_converged_identity
below_limit_of_detection -> contextual solver_converged_below_detection or solver_indeterminate, depending on policy.accept_below_detection
detected -> contextual continue/no terminal solver status
detection_indeterminate -> contextual continue/no terminal solver status or solver_indeterminate
```

### solver.projection.to_solver_step

Input protocol:

```text
projection_result_v4
```

Output protocol:

```text
typed_projection_solver_step
```

Input family:

```text
ProjectionStatus
```

Output family:

```text
SolverStatus
```

Mapped statuses:

```text
projection_transverse -> solver_step_advanced
projection_linear -> solver_step_advanced
projection_tangent_contact -> solver_tangent_blocked
projection_no_real_root -> solver_projection_blocked
projection_identity -> solver_projection_blocked
projection_no_solution -> solver_projection_blocked
projection_selection_refused -> solver_selection_refused
```

### solver.branch_fingerprint.require_complete

Input protocol:

```text
branch_fingerprint
```

Output protocol:

```text
typed_projection_solver_step
```

Input family:

```text
BranchFingerprintStatus
```

Output family:

```text
SolverStatus
```

Accepted statuses:

```text
fingerprint_complete
```

Mapped/refused statuses:

```text
fingerprint_unidentified -> solver_branch_unidentified
fingerprint_incomplete -> solver_branch_unidentified
fingerprint_proxy_uncalibrated -> solver_proxy_uncalibrated
```

If the implementation has more precise BranchFingerprint statuses from Task 006, include them in the rule report. Do not leave a producer status unaccounted for.

### solver.refinery.require_accepted

Input protocol:

```text
refinery.decision
```

Output protocol:

```text
typed_projection_solver_step
```

Input family:

```text
RefineryStatus
```

Output family:

```text
SolverStatus
```

Accepted statuses:

```text
rewrite_accepted_same_geometry_lower_slag
```

All other refinery statuses map to or refuse as:

```text
solver_refinery_rejected
```

### solver.projection_history.require_stable

Input protocol:

```text
history_trace
```

Output protocol:

```text
typed_projection_solver_run
```

Input family:

```text
HistoryStatus
```

Output family:

```text
SolverStatus
```

Accepted statuses:

```text
history_trace_stable
```

Mapped/refused statuses:

```text
history_trace_transitioned -> solver_history_unstable
history_trace_incomplete -> solver_history_unstable
history_trace_unordered -> solver_history_unstable
history_trace_empty -> solver_indeterminate
history_trace_singleton -> contextual non-blocking evidence unless stable trace is explicitly demanded for singleton traces
```

### solver.run.require_converged

Input protocol:

```text
typed_projection_solver_run
```

Output protocol:

```text
converged_solver
```

Input family:

```text
SolverStatus
```

Output family:

```text
none
```

Accepted statuses:

```text
solver_converged_identity
solver_converged_below_detection
```

Refused statuses:

```text
all other SolverStatus values
```

## Serialization requirements

All new values and results must serialize through the existing strict serialization path.

Serialized evidence must include:

```text
solver status
solver protocol
policy fields
model IDs
step indices
state_before/state_after
selected displacement when present
requested branch
residual observable
trace IDs for residual detection, root state, projection, branch fingerprint, refinery, and history when present
terminal status
validity
conditioning
provenance
```

Do not serialize callbacks, functions, lambdas, AST nodes, parser state, or raw exception objects.

## Required reports

Create Task 009 reports under:

```text
Build_Docs/Reports/task009/
```

Required files:

```text
Build_Docs/Reports/task009/task009_summary.md
Build_Docs/Reports/task009/solver_status_table.md
Build_Docs/Reports/task009/status_transition_rules.md
Build_Docs/Reports/task009/design_decisions.md
```

`task009_summary.md` should include:

```text
files created
files modified
behavior summary
red test result
Task 009 test slice result
full suite result
source audit results
any deviations
Task 010 readiness
```

`solver_status_table.md` should include each SolverStatus with:

```text
input condition
value shape
validity mapping
conditioning behavior
protocol behavior
refusal/indeterminate behavior
```

`status_transition_rules.md` should include all Task 009 named transition rules with:

```text
rule id
input protocol
output protocol
input family
output family
accepted statuses
refused statuses
mapped statuses
context keys
notes
```

`design_decisions.md` should explicitly record:

```text
local model generation is caller-supplied in Task 009
no V1 Halley/transport/multistart port
convergence is metrology-backed, not tolerance-backed
below-detection is not identity-zero
projection semantics are inherited from Task 003
history tracks projection geometry, not ordinary terminal solver-status changes
BranchFingerprint and refinery gates are explicit policy choices
no domain consumer or domain classifier is introduced
```

## Tests

Add focused Task 009 tests. Recommended files:

```text
tests/test_task009_solver_step_projection.py
tests/test_task009_solver_convergence_metrology.py
tests/test_task009_solver_branch_and_refinery_gates.py
tests/test_task009_solver_run_history.py
tests/test_task009_transition_rules.py
tests/test_task009_solver_serialization.py
tests/test_task009_source_purity.py
```

### Required red tests

Before implementation, the Task 009 test slice should fail because the solver package and `SolverStatus` do not exist.

### Required behavior tests

At minimum, test:

```text
1. A transverse local quadratic projection advances by selected displacement.
2. A linear local quadratic projection advances by selected displacement.
3. Tangent contact returns solver_tangent_blocked and does not advance.
4. No-real-root local model returns solver_projection_blocked.
5. Incompatible branch returns solver_selection_refused.
6. identity_zero residual metrology returns solver_converged_identity before projection.
7. below_limit_of_detection returns solver_converged_below_detection only when policy.accept_below_detection is true.
8. below_limit_of_detection without acceptance policy does not certify identity convergence.
9. detected residual proceeds to projection.
10. wrong-family noise-floor evidence is refused clearly.
11. required BranchFingerprint complete evidence passes.
12. required BranchFingerprint unidentified/incomplete evidence returns solver_branch_unidentified.
13. required proxy-uncalibrated fingerprint evidence returns solver_proxy_uncalibrated.
14. required refinery accepted evidence passes.
15. required refinery rejected/equivalent/indeterminate evidence returns solver_refinery_rejected.
16. run_typed_projection_solver enforces strictly increasing step_index.
17. run_typed_projection_solver enforces exact state continuity between accepted state_after and next state_before.
18. projection-history trace stable evidence passes when two or more accepted projection events preserve projection geometry.
19. projection-history transition returns solver_history_unstable when stable projection history is required.
20. exhausted supplied model budget returns solver_step_budget_exhausted.
21. require_converged_solver accepts only solver_converged_identity and solver_converged_below_detection.
22. serialization preserves policy, traces, statuses, and selected displacement.
23. Existing Task 001 through Task 008 flows still pass unchanged.
```

### Negative tests

Test that solver code does not:

```text
- divide projective root coordinates directly;
- implement an alternate quadratic formula;
- compare residuals to an internal numeric tolerance;
- silently accept below-detection as identity-zero;
- choose a default/principal/nearest/positive branch;
- use approximate equality for state continuity;
- sort caller-supplied solver models;
- import or reference V1 modules;
- import or call V3/legacy code;
- modify primitive, projection, metrology, branch, refinery, or history behavior.
```

## Source purity and dependency audits

Keep existing audits green. Add Task 009 audits as appropriate.

Required clean-room audit:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
```

Required hidden-correction audit:

```bash
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance|confidence_score|weighted_score|smoothing|hysteresis|interpolate|extrapolate" src/lloyd_v4 -n
```

Required V1-reference audit:

```bash
rg -i "lloyd_core|lloyd_core_nvar|lloyd_decomposition|hyperdual|halley|multi_start|route_score" src/lloyd_v4 -n
```

Result must be no matches. Task 009 is allowed to be inspired by the old geometry-aware solver idea, but source must not import, name, copy, or depend on the V1 implementation.

Required dependency-direction audit:

```bash
rg "lloyd_v4\.solver|from lloyd_v4\.solver|import .*solver" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery src/lloyd_v4/history -n
```

Result must be no matches.

Required earlier-layer leakage audit:

```bash
rg "TypedProjectionSolver|SolverStatus|solver_step|solver_converged|solver_projection|solver_branch|solver_refinery|solver_history" src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery src/lloyd_v4/history -n
```

Result must be no matches.

Required deferred-feature audit:

```bash
rg "JetBundle|shape_operator|singularity|symmetry|centrifuge|surface_mesh|implicit_chart|finite_eta|domain_consumer|domain_classifier|bearing|aerospace|betting|scanner|parser|cas|symbolic_simplifier" src/lloyd_v4/solver -n
```

Result must be no matches.

Required compatibility audit:

```bash
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

Result must be no matches.

If an audit term appears only in a Task 009 report under `Build_Docs/Reports/task009`, that is acceptable. Source audits are over `src` unless explicitly stated otherwise.

## Non-goals

Do not implement:

```text
V1 Halley solver
Newton solver
multistart root search
automatic differentiation
HyperDual or HyperDualN
JetBundle
expression parser
safe AST evaluator
surface mesh
sweep
closure
centrifuge
curvature decomposition
shape operator
singularity classifier
symmetry detector
implicit chart projection
n-variable hypersurface engine
finite-eta correction
precision-path separation
new BranchFingerprint models
domain consumer
domain classifier
bearing/aerospace/betting/scanner logic
symbolic equation generation
CAS simplification
persistent history store
runtime V1 or V3 comparison fixtures
adapters or compatibility modes
```

These are future V4-native tasks. Task 009 is only the first solver consumer over supplied local quadratic model evidence.

## Acceptance criteria

Task 009 is complete when:

```text
1. src/lloyd_v4/solver exists with a typed projection solver MVP.
2. SolverStatus is added to core status definitions.
3. evaluate_solver_step(...) consumes a local quadratic model, Task 004 noise-floor evidence, and explicit policy evidence.
4. evaluate_solver_step(...) uses Task 002 and Task 003 for root/projection evidence and never recomputes roots directly.
5. run_typed_projection_solver(...) consumes a finite caller-supplied model sequence and returns a typed solver run result.
6. Convergence is determined only through Task 004 metrology evidence and explicit policy.
7. Tangent contact blocks advancement.
8. BranchFingerprint and refinery gates are policy-controlled and protocol-validated.
9. Projection-history stability uses Task 008 history evidence and does not treat ordinary terminal solver-status changes as instability.
10. Named Task 009 transition rules are exported and covered by tests.
11. Serialization preserves solver evidence, trace IDs, policy, statuses, validity, conditioning, and provenance.
12. Task 009 reports are created under Build_Docs/Reports/task009.
13. Task 009 test slice passes.
14. Full test suite passes.
15. Source audits return no matches.
16. Existing Task 001 through Task 008 behavior remains unchanged.
```

## Task 010 readiness

After Task 009, Task 010 should be ready to scope as one of:

```text
JetBundle primitive and typed second-order local model extraction
```

or:

```text
Precision-path separation: C_{p,k} = a + u_p b_k
```

Do not implement either in Task 009. The recommended next step is `JetBundle`, because the solver MVP deliberately depends on caller-supplied local quadratic models. A V4-native JetBundle can later become the local-model provider without polluting the solver with parser or automatic-differentiation machinery.
