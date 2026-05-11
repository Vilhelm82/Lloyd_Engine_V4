# Codex Task 009A: TypedProjectionSolver Scenario Battery

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

Task 009A is not a new solver feature task. It is a solver test-hardening and scenario-validation task.

## Current verified baseline

Task 000 is complete. The M0 substrate exists: statuses, validity, conditioning, provenance, typed results/refusals, protocol validation, conservative status calculus, strict serialization, core errors, and architecture docs.

Task 001 is complete. `ProjectiveRatio(n, d)` exists as the first primitive. It preserves raw projective coordinates `[n:d]`, classifies exact projective strata without dividing by `d`, and scalarizes only through an explicit protocol that may refuse.

Task 002 is complete. `StratifiedQuadraticRoots` exists. `stratified_quadratic_roots(a, b, c)` returns a typed root-state result with raw coefficients, discriminant evidence, branch-labeled projective root coordinates, validity, conditioning, and provenance. `select_quadratic_root(result, branch)` is explicit and protocol-validated.

Task 003 is complete. `ProjectionResultV4` and the exact quadratic projection protocol exist. `exact_quadratic_projection(root_state_result, branch)` consumes validated Task 002 root-state results, calls Task 002 selection for selectable branches, and emits structured projection evidence with separate `root_exists`, `projection_defined`, `selected_root_valid`, and `advance_valid` flags.

Task 004 is complete. The Layer 2 metrology foundation exists under `src/lloyd_v4/metrology`. It implements declared and estimated `b_k` noise-floor evidence, limit-of-detection classification with explicit `identity_evidence`, pointwise `K_q` proxy calibration through ProjectiveRatio plus explicit scalarization, `proxy_uncalibrated(...)`, and `require_valid_proxy_calibration(...)`.

Task 005 is complete. `TypedResult` is generic over value type and status enum family. Protocols infer or declare status families and reject wrong-family typed results explicitly. Named transition-rule machinery exists with canonical rules for ProjectiveRatio scalarization, quadratic root selection, quadratic projection, limit-of-detection classification, valid `K_q` calibration, branch/refinery/history composition, and solver decisions.

Task 006 is complete. The branch package exists under `src/lloyd_v4/branch`. It implements `BranchFingerprintStatus`, slope-flow comparison with ProjectiveRatio-backed segment slopes, declared model residual comparison, `K_q` slope-stability checks using Task 004 calibration evidence, and BranchFingerprint composition through named transition rules. BranchFingerprint is evidence, not a domain classifier.

Task 007 is complete. The refinery package exists under `src/lloyd_v4/refinery`. It implements typed result snapshots, explicit slag vectors, scenario and candidate rewrite decisions, `RefineryStatus`, refinery protocols, named status-preservation transition rules, accepted-rewrite enforcement, and serialization. The refinery consumes supplied typed observations only. It does not parse, simplify, generate, or classify equations.

Task 008 is complete. The history package exists under `src/lloyd_v4/history`. It implements `HistoryStatus`, compact status-event recording, pairwise transition comparison with precedence, ordered trace construction, stable-trace protocol enforcement with typed refusals, history result aliases, protocols, transition rules, and serialization. History observes typed status evolution and does not decide downstream meaning.

Task 009 is complete. The solver package exists under `src/lloyd_v4/solver`. It implements the TypedProjectionSolver MVP with:

```text
SolverStatus
LocalQuadraticStepModel
SolverPolicy
step evaluation via Task 002 roots and Task 003 projection
metrology-backed convergence via Task 004
optional BranchFingerprint and refinery gates
projection-history coherence via Task 008
solver run execution and converged-solver protocol
named Task 009 transition rules
serialization and reports
```

Task 009 verification baseline:

```text
Task 009 slice: 26 passed
Full suite: 203 passed
Required source audits: no matches
```

## Task 009A goal

Add a comprehensive solver scenario battery proving that the Task 009 solver behaves like a V4 typed consumer, not like a scalar residual solver with decorative metadata.

The existing Task 009 tests prove the solver APIs and primary protocol paths exist. Task 009A should prove the solver behavior across explicit scenarios:

```text
1. every SolverStatus can be intentionally produced;
2. every Task 009 named transition rule is exercised;
3. projection strata map correctly to solver statuses;
4. metrology-backed convergence obeys policy;
5. BranchFingerprint and refinery gates block only when enabled;
6. history coherence catches projection-geometry instability;
7. sequence inconsistency and budget exhaustion are explicit;
8. serialization remains stable;
9. no V1/V3/legacy/domain/parser/hidden-tolerance behavior leaks in.
```

Task 009A should prefer adding tests and reports. Source changes should be minimal and only made if the new tests expose a real Task 009 bug. Do not change existing solver semantics just to make tests easier.

## Non-goals

Do not implement Task 010 JetBundle.

Do not generate local quadratic models from expressions.

Do not add automatic differentiation.

Do not parse equations.

Do not port V1 Halley, geometry-aware transport, multistart routing, route scores, AST evaluators, HyperDual, or N-variable engines.

Do not add a domain consumer.

Do not add bearing, aerospace, betting, scanner, or application labels.

Do not add arrays, tensors, vectorized solver runs, surface meshes, centrifuge, implicit chart projection, shape operator, singularity, symmetry, or curvature decomposition.

Do not add internal residual tolerances, hidden epsilons, denominator floors, rescue constants, clamps, `isclose`, `allclose`, smoothing, hysteresis, interpolation, extrapolation, confidence scores, weighted scores, or fallback branches.

Do not rename or hide the existing Task 000 `measurement_resolution` provenance metadata.

## Required files

Add Task 009A tests under `tests/`. Recommended files:

```text
tests/test_task009a_solver_status_coverage.py
tests/test_task009a_projection_strata_scenarios.py
tests/test_task009a_metrology_policy_scenarios.py
tests/test_task009a_branch_refinery_gate_scenarios.py
tests/test_task009a_history_and_sequence_scenarios.py
tests/test_task009a_transition_rule_coverage.py
tests/test_task009a_solver_serialization_regression.py
tests/test_task009a_source_purity.py
```

Add reports under:

```text
Build_Docs/Reports/task009A/
```

Required reports:

```text
Build_Docs/Reports/task009A/task009A_summary.md
Build_Docs/Reports/task009A/solver_scenario_matrix.md
Build_Docs/Reports/task009A/design_decisions.md
```

Optional but useful:

```text
Build_Docs/Reports/task009A/status_coverage_matrix.md
Build_Docs/Reports/task009A/transition_rule_coverage.md
```

## Test construction guidance

Use the public Task 009 solver APIs and result aliases. Do not reach into private internals unless unavoidable. If helper fixtures are needed, define them inside test files or a narrow test helper module.

The solver consumes caller-supplied `LocalQuadraticStepModel` values. Build small deterministic models with finite Python floats.

Useful local quadratic coefficient fixtures:

```text
transverse two-real-root model:
    a = 1, b = 0, c = -1
    branches: minus, plus

linear model:
    a = 0, b = 1, c = -2
    branch: linear

repeated-root tangent model:
    a = 1, b = -2, c = 1
    branch: repeated

no-real-root model:
    a = 1, b = 0, c = 1

constant identity model:
    a = 0, b = 0, c = 0

constant no-solution model:
    a = 0, b = 0, c = 1

wrong-branch model:
    use a selectable model but request an incompatible branch
```

If the final Task 009 `LocalQuadraticStepModel` constructor uses different field names, adapt to the implementation while preserving these semantic cases.

Use Task 004 metrology APIs to produce convergence evidence. Do not fake convergence through raw residual comparisons.

Use Task 006 and Task 007 public APIs to create BranchFingerprint and refinery evidence where practical. If creating full evidence is too heavy for a specific negative gate, a minimal well-formed typed result is acceptable only if it preserves protocol identity, status family, validity, provenance, and serialization expectations.

Use Task 008 history APIs indirectly through solver runs where possible. Direct history tests may be used to assert that the solver-supplied projection events are compatible with stable-trace enforcement.

## Required scenario matrix

Create a scenario matrix in tests and in `solver_scenario_matrix.md` covering at least these rows.

### A. Clean transverse advance

Input:

```text
projection: two-real-root local model
branch: compatible minus or plus
residual detection: detected
policy: no branch gate, no refinery gate, stable history optional
```

Expected:

```text
one-step result: solver_step_advanced
advanceable: true
not terminal convergence
selected projection trace preserved
```

### B. Clean linear advance

Input:

```text
projection: linear local model
branch: linear
residual detection: detected
```

Expected:

```text
one-step result: solver_step_advanced
uses Task 003 projection_linear semantics
```

### C. Identity convergence

Input:

```text
residual observable: exact zero
identity_evidence: true
noise-floor evidence: valid declared or estimated floor
```

Expected:

```text
solver_converged_identity
accepted by require_converged_solver
not confused with below-detection convergence
```

### D. Below-detection convergence policy split

Run the same below-limit residual evidence twice:

```text
policy.accept_below_detection = true
policy.accept_below_detection = false
```

Expected:

```text
true  -> solver_converged_below_detection, accepted by require_converged_solver
false -> not solver_converged_below_detection; solver continues if model budget remains, otherwise solver_step_budget_exhausted or another explicit non-converged status
```

This test must prove that below-detection termination is policy-controlled.

### E. Detection indeterminate

Input:

```text
noise-floor evidence: indeterminate
residual observable: finite
```

Expected:

```text
solver_indeterminate
not converged
typed refusal when require_converged_solver is called
```

### F. Tangent contact block

Input:

```text
projection: repeated-root local model
branch: repeated
```

Expected:

```text
solver_tangent_blocked
selected scalar root may exist, but advance_valid is false
solver must not advance state
```

### G. Projection blocked cases

Test all non-advance-defining projection source strata:

```text
no real root
constant identity
constant no solution
```

Expected:

```text
solver_projection_blocked
projection evidence preserved
no fake scalar step
```

### H. Selection refused

Input:

```text
selectable source model
incompatible branch request
```

Expected:

```text
solver_selection_refused
Task 002/003 refusal evidence preserved
```

### I. Branch gate disabled

Input:

```text
policy.requires_branch_fingerprint = false
branch evidence missing
otherwise valid advance/convergence evidence
```

Expected:

```text
branch evidence absence does not block
```

### J. Branch gate complete

Input:

```text
policy.requires_branch_fingerprint = true
BranchFingerprint evidence: fingerprint_complete
```

Expected:

```text
branch gate passes
```

### K. Branch gate unidentified or incomplete

Input:

```text
policy.requires_branch_fingerprint = true
BranchFingerprint evidence: fingerprint_unidentified or fingerprint_incomplete
```

Expected:

```text
solver_branch_unidentified
```

### L. Branch gate proxy uncalibrated

Input:

```text
policy.requires_branch_fingerprint = true
BranchFingerprint evidence: fingerprint_proxy_uncalibrated or proxy/Kq evidence blocked by uncalibrated/unstable/indeterminate proxy flow
```

Expected:

```text
solver_proxy_uncalibrated
```

### M. Refinery gate disabled

Input:

```text
policy.requires_refinery_acceptance = false
refinery evidence missing or non-accepted
otherwise valid advance/convergence evidence
```

Expected:

```text
refinery evidence absence or rejection does not block
```

### N. Refinery gate accepted

Input:

```text
policy.requires_refinery_acceptance = true
RefineryStatus: rewrite_accepted_same_geometry_lower_slag
```

Expected:

```text
refinery gate passes
```

### O. Refinery gate rejected

Input:

```text
policy.requires_refinery_acceptance = true
any non-accepted RefineryStatus
```

Expected:

```text
solver_refinery_rejected
```

### P. Stable projection history

Input:

```text
multi-step run
accepted projection events preserve protocol, status family, status, validity, and geometry signature
policy.requires_stable_projection_history = true
```

Expected:

```text
history gate passes
run terminates by convergence or budget, not by solver_history_unstable
history trace evidence serialized
```

### Q. Projection history status transition

Input:

```text
multi-step run
accepted projection event changes projection status or branch geometry signature
policy.requires_stable_projection_history = true
```

Expected:

```text
solver_history_unstable
```

### R. Projection history geometry transition

Input:

```text
projection status remains same
caller-supplied projection geometry signature changes
policy.requires_stable_projection_history = true
```

Expected:

```text
solver_history_unstable
```

### S. Unordered or repeated sequence

Input:

```text
model step indices non-increasing or repeated
```

Expected:

```text
solver_sequence_inconsistent
```

### T. State continuity mismatch

Input:

```text
next model's state_before does not exactly equal previous accepted state_after under host Python arithmetic
```

Expected:

```text
solver_sequence_inconsistent
```

Do not use approximate equality here. Task 009 sequence consistency is exact host-arithmetic equality.

### U. Budget exhausted

Input:

```text
finite sequence of valid advance steps
no metrology-backed convergence before supplied model budget ends
```

Expected:

```text
solver_step_budget_exhausted
```

### V. Protocol refused / wrong-family evidence

Input:

```text
wrong-family typed evidence supplied to a required gate
or malformed required typed evidence supplied through public API
```

Expected:

```text
solver_protocol_refused
or a clear ProtocolViolationError if the public API contract rejects before producing a solver result
```

Document which behavior the implementation uses. The behavior must be explicit and covered.

## Required status coverage

Every `SolverStatus` must be intentionally produced by at least one test unless the implementation makes a status impossible to produce through public APIs. If a status is impossible through public APIs, that is a design smell and must be documented in `design_decisions.md` with a proposed follow-up.

Required coverage list:

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

Add a test helper or assertion that compares produced statuses against this required set.

## Required transition-rule coverage

Every Task 009 named transition rule must be exercised by at least one test.

Required rules:

```text
solver.residual_detection.to_solver
solver.projection.to_solver_step
solver.branch_fingerprint.require_complete
solver.refinery.require_accepted
solver.projection_history.require_stable
solver.run.require_converged
```

Coverage should include both passing and blocking paths where applicable.

At minimum:

```text
residual detection -> identity convergence
residual detection -> below-detection convergence
residual detection -> indeterminate
projection -> advance
projection -> tangent block
projection -> projection block
projection -> selection refusal
branch fingerprint -> complete pass
branch fingerprint -> unidentified block
branch fingerprint -> proxy uncalibrated block
refinery -> accepted pass
refinery -> rejected block
history -> stable pass
history -> unstable block
run -> require converged accepted
run -> require converged refusal
```

## Required serialization checks

Add or extend serialization tests to prove:

```text
SolverStepValue serialization preserves:
- model identity / step index evidence
- state_before
- state_after when advanced
- requested branch
- projection trace evidence
- residual/metrology trace evidence
- optional branch/refinery gate evidence when present
- solver status

SolverRunValue serialization preserves:
- run ID or equivalent sequence evidence
- final status
- final state when present
- all step trace references or compact step evidence
- history trace evidence when constructed
- terminal refusal evidence where applicable
```

Serialization shape must remain JSON-safe and must not add non-finite sentinels.

Generic typing metadata must not become serialized evidence unless Task 009 already did so. Preserve existing Task 009 serialization decisions.

## Required source-purity tests

Add a Task 009A source-purity test file. Keep the existing Task 009 audits and add scenario-battery specific protection.

Required audits:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
```

```bash
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance|confidence_score|weighted_score|smoothing|hysteresis|interpolate|extrapolate" src/lloyd_v4 -n
```

```bash
rg -i "lloyd_core|lloyd_core_nvar|lloyd_decomposition|hyperdual|halley|multi_start|route_score" src/lloyd_v4 -n
```

```bash
rg "lloyd_v4\.solver|from lloyd_v4\.solver|import .*solver" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery src/lloyd_v4/history -n
```

```bash
rg "TypedProjectionSolver|SolverStatus|solver_step|solver_converged|solver_projection|solver_branch|solver_refinery|solver_history" src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery src/lloyd_v4/history -n
```

```bash
rg "JetBundle|shape_operator|singularity|symmetry|centrifuge|surface_mesh|implicit_chart|finite_eta|domain_consumer|domain_classifier|bearing|aerospace|betting|scanner|parser|cas|symbolic_simplifier" src/lloyd_v4/solver -n
```

```bash
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

If legitimate Task 009A report files contain audit terms, do not audit `Build_Docs` for these terms. Source-only audits should run over `src` unless a specific test intentionally checks docs.

## Required run commands

Run the new Task 009A slice:

```bash
python -m pytest tests/test_task009a_*.py -q
```

Run the full suite:

```bash
python -m pytest tests -q
```

Also run with standard pytest output if useful:

```bash
pytest
```

Run all required source audits and record exact commands/results in `task009A_summary.md`.

## Acceptance criteria

Task 009A is complete when:

1. The Task 009A scenario tests exist and pass.
2. Every required `SolverStatus` is intentionally produced or explicitly documented as unreachable through public APIs with a follow-up recommendation.
3. Every Task 009 named transition rule is exercised.
4. Projection-stratum mapping tests cover transverse, linear, tangent, no-real-root, constant identity, constant no-solution, and incompatible branch cases.
5. Metrology policy tests prove identity convergence, below-detection policy split, detected continuation, and indeterminate detection behavior.
6. BranchFingerprint gate tests prove disabled, complete, unidentified/incomplete, and proxy-uncalibrated behavior.
7. Refinery gate tests prove disabled, accepted, and rejected behavior.
8. History tests prove stable, status-transitioned, geometry-transitioned, unordered/repeated, and state-continuity-mismatch behavior.
9. Budget exhaustion is tested as explicit terminal evidence.
10. Converged-solver protocol tests prove accepted convergence and typed refusal for non-converged statuses.
11. Serialization tests prove solver step/run evidence remains JSON-safe and preserves relevant traces.
12. No new hidden numeric correction path appears.
13. No V1/V3 runtime dependency appears.
14. No parser, symbolic simplifier, JetBundle, implicit chart, shape operator, domain consumer, or solver-port behavior appears.
15. Existing Task 001 through Task 009 behavior and serialization remain unchanged unless a real Task 009 bug is found and documented.
16. Full suite passes.
17. All required source audits return no matches.
18. Task 009A reports are added under `Build_Docs/Reports/task009A/`.

## Reports

### `task009A_summary.md`

Include:

```text
Files created
Files modified
Scenario slice command and result
Full suite command and result
Source audit commands and results
Any solver source fixes made
Any unreachable status coverage and why
Deviations
Task 010 readiness
```

### `solver_scenario_matrix.md`

Include a table with:

```text
scenario id
scenario name
input projection/metrology/branch/refinery/history condition
policy settings
expected SolverStatus
actual SolverStatus
notes
```

### `design_decisions.md`

Include decisions about:

```text
public API versus internal fixture construction
whether wrong-family evidence returns solver_protocol_refused or ProtocolViolationError
how branch/refinery evidence was constructed for tests
how history geometry signatures were chosen
any minimal source bug fixes
why no Task 010 behavior was added
```

### Optional `transition_rule_coverage.md`

Include a table with:

```text
rule id
positive cases tested
blocking/mapped cases tested
test file names
notes
```

## Task 010 readiness

Task 010 remains ready to scope as:

```text
JetBundle primitive and typed second-order local model extraction
```

Task 009A should not change that readiness. The solver still consumes supplied local models. Task 010 should give it a V4-native model provider.
