# Source Inventory: JetBundle / Solver Targeted Audit

Repository: `/mnt/fast/Lloyd_Engine_V4`

Current verification: `python -m pytest tests -q` passed on 2026-05-11 with 296 collected tests.

## Core substrate

| Path | Main exports / behavior | Status-family awareness | Provenance / transition notes | JetBundle / solver risk |
|---|---|---|---|---|
| `src/lloyd_v4/core/result.py` | `TypedRefusal`, generic `TypedResult[ValueT, StatusT]`; JSON-safe serialization of value/status/validity/conditioning/provenance/protocol/refusal at lines 18-53. | Generic over enum status type; no local family policy. | Carries existing `Provenance`; no transition rules. | Safe substrate. Result envelope is clean and audit-preserving. |
| `src/lloyd_v4/core/status.py` | All status families, including `TransferStatus`, `SlopeStatus`, `ProjectionStatus`, `SolverStatus`; union `StatusCode` at lines 186-205. | Central enum registry; families are separate `StrEnum`s. | No provenance; no rule objects. | Safe, but new AlphaProbe/JetBundle statuses must be added here intentionally. |
| `src/lloyd_v4/core/protocols.py` | `ProducerProtocol`, `ConsumerProtocol`, `ProtocolCheck`, `validate_protocol`; family checks at lines 53-60 and accepted-status checks at lines 73-77. | Family-aware via `status_family`, inferred from emitted/accepted statuses. | No provenance; validates consumer compatibility. | Safe substrate. One small concern: `scalarization_allowed` naming reads backwards in the refusal check at lines 79-83, but current tests cover expected behavior. |
| `src/lloyd_v4/core/transitions.py` | `StatusTransitionRule`, `StatusTransitionOutcome`, `apply_status_transition`; transition callable has authority before static mappings at lines 94-96. | Explicit input/output status families. | Encodes named rule IDs, accepted/refused/mapped statuses, context keys. | Safe substrate, but contextual rules with static `mapped_statuses` can mislead readers unless documented or tested. |
| `src/lloyd_v4/core/provenance.py` | `Provenance` with operation/expression/precision/backend/device/measurement_resolution/inputs/parents/trace_id/status. | Uses `ProvenanceStatus`. | Derives content-addressed trace IDs from operation, expression, precision, backend, device, measurement_resolution, inputs, parents, status at lines 29-42. | Safe. JetBundle should populate `inputs` for primitive observations and `parents` for derived evidence. |
| `src/lloyd_v4/core/serialization.py` | `to_json_safe`; maps NaN/Inf into tagged dictionaries at lines 9-15. | Enum-aware serialization. | No transition/provenance logic. | Safe. Preserves non-finite audit evidence. |
| `src/lloyd_v4/core/validity.py` | `Validity(defined, finite, selectable, advanceable, observable)`. | Status-neutral, used by every result family. | No transitions. | Safe. JetBundle refusals should use validity honestly instead of smuggling tolerances into values. |
| `src/lloyd_v4/core/conditioning.py` | `Conditioning(status, notes)` using `ConditioningStatus`. | Simple typed conditioning status. | No transitions. | Safe. Good place to carry fit diagnostics, not to mutate computed values. |

## Certified primitive / projection inventory

| Path | Statuses emitted | Protocols / rules | Provenance behavior | Scalarization / division | Substrate rating |
|---|---|---|---|---|---|
| `src/lloyd_v4/primitives/projective_ratio.py` | `finite_ratio`, `signed_zero`, `infinite_direction`, `indeterminate`. | `PROJECTIVE_RATIO_PROTOCOL`, `PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL`, `PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE`. | Primitive result inputs are `(raw_numerator, raw_denominator)` and parent traces from typed inputs at lines 87-112. Scalarization parent is the ratio trace at lines 119-127. | Does not divide during classification. Division occurs only in `scalarize_projective_ratio` after protocol acceptance at line 146. | `certified_substrate`. |
| `src/lloyd_v4/primitives/stratified_quadratic_roots.py` | `two_real_roots`, `repeated_root`, `no_real_root`, `linear_root`, `constant_identity`, `constant_no_solution`. | `STRATIFIED_QUADRATIC_ROOTS_PROTOCOL`, `QUADRATIC_ROOT_SELECTION_PROTOCOL`, `QUADRATIC_ROOT_SELECTION_TRANSITION_RULE`. | Root construction records inputs `(a,b,c)` at lines 156-164. Selection parents include root-state, ratio, and scalar traces at lines 205-213. | Root coordinates are projective values; selection calls `projective_ratio` and explicit scalarization at lines 186-197. | `certified_substrate` for exact quadratic local models; too narrow for general JetBundle. |
| `src/lloyd_v4/projection/exact_projection.py` | `projection_transverse`, `projection_tangent_contact`, `projection_linear`, `projection_no_real_root`, `projection_identity`, `projection_no_solution`, `projection_selection_refused`. | `EXACT_QUADRATIC_PROJECTION_PROTOCOL`, `PROJECTION_RESULT_V4_PROTOCOL`, `QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE`. | Projection parents include root-state, branch-selection, and selected-root traces at lines 232-240 and 337-345. | Delegates scalar root selection to Task 002; no fallback branch or nearest-root scoring. | `certified_substrate` as projection consumer; transition-rule ambiguity should be clarified. |

## Transfer and alpha measurement

Exact source files:

- `src/lloyd_v4/primitives/typed_finite_difference.py`
- `src/lloyd_v4/primitives/typed_log_log_slope.py`
- Tests: `tests/test_task015_typed_finite_difference.py`, `tests/test_task016_typed_log_log_slope.py`
- Reports/spec evidence: `Build_Docs/Reports/task015_summary.md`, `Build_Docs/Reports/task016_summary.md`, `Build_Docs/Agent_tasks/codex_task016_typed_log_log_slope.md`

Findings:

- `typed_finite_difference` emits `TransferStatus`: observed, cancellation dominated, non-finite, domain refused, delta indeterminate (`core/status.py` lines 96-102).
- It computes `g(f)`, `g(f+delta_f)`, `delta_g`, and `transfer = delta_g / delta_f` at lines 97-148. It currently does not use `ProjectiveRatio`; division is direct after checking `delta_f != 0`.
- Cancellation dominance is `abs(delta_g) / max(abs(g_f), abs(g_f_plus)) < precision_floor` at lines 156-185.
- `precision_floor` currently returns `2.0**-52` for `raw_python` at lines 214-217. It changes only status/validity/conditioning; the computed `transfer` remains stored in the `TransferObservation` for cancellation-dominated cases.
- `typed_log_log_slope` consumes a typed collection of transfer observations, filters to `TRANSFER_OBSERVED`, derives pairs from `observation.provenance.inputs[0]` and `observation.value.transfer`, and fits `log(abs(transfer))` against `log(f)` at lines 84-115.
- Alpha recovery is alpha-minus-one: tests at `tests/test_task016_typed_log_log_slope.py` lines 28-46 and 260-281 recover slopes for synthetic `g(f)=f**alpha`.
- Alpha evidence is currently only a fitted scalar over a provided observation set. Direction/probe identity can be inferred from callable labels and inputs, but no first-class directional `AlphaProbe` object exists.
- Nested-window alpha stability does not exist; `Build_Docs/Reports/task016_summary.md` lists it as a current limit.

## Solver inventory

Source:

- `src/lloyd_v4/solver/typed_projection_solver.py`
- Tests: `tests/test_task009_*.py` and lowercase `tests/test_task009a_*.py` exist. There are no uppercase `test_task009A_*.py` files.

Key structures:

- `SolverStatus`: lines 169-183 in `core/status.py`.
- `SolverPolicy`: `accept_below_detection`, `require_branch_fingerprint`, `require_refinery_acceptance`, `require_stable_projection_history` at `typed_projection_solver.py` lines 194-207.
- `LocalQuadraticStepModel`: caller-supplied `model_id`, `step_index`, `state_before`, `a`, `b`, `c`, `branch`, `residual_observable`, optional identity, geometry signature, branch/refinery evidence at lines 210-249.
- The solver does not generate local models. It consumes supplied coefficients and supplied residual evidence.
- Hard dependencies: core, metrology noise-floor classification, stratified quadratic roots, branch selection, exact projection.
- Optional policy gates: branch fingerprint, refinery acceptance, stable projection history.
- Residual evidence enters first through `classify_against_noise_floor(model.residual_observable, ...)` at lines 332-337. Identity and below-detection convergence are decided before projection at lines 348-353.
- Step advancement maps projection status to solver status at lines 359-381. There is no hidden score; branch choice is the caller-supplied branch string.
- Current solver should be treated as `reference_only` for the alpha-aware solver. It is a useful typed consumer and transition/status example, but it is still local quadratic projection plus residual gate, not a Lloyd-native alpha/geometric measurement solver.

## Layer 2+ package assessment

| Package | Rating | Reason |
|---|---|---|
| `metrology` | `candidate_substrate` | Typed, protocolized, no reverse imports into lower layers. Noise-floor/limit-of-detection is useful but declared/estimated floors affect status decisions, so use with explicit policy. |
| `branch` | `reference_only` | Uses ProjectiveRatio for segment slopes and named rules, but compares against declared model/stability bands and composes branch fingerprints from higher-level assumptions. Useful evidence, not a certified alpha substrate. |
| `refinery` | `reference_only` | Protocol-preserving snapshot and slag gate are useful audit machinery, but it is a consumer over supplied scenarios and declared dimensions. Not a primitive solver substrate. |
| `history` | `candidate_substrate` | Compact typed event/trace evidence with stable-trace protocol. It depends on refinery snapshots and should not be required for the minimal alpha solver MVP. |
| `solver` | `reference_only` | Good status-transition consumer, but depends on caller-supplied local quadratic models and residual metrology; not alpha-aware and not model-generating. |

## Recommended source audit pattern for precision floors

Keep the broad floor search, but split legitimate metrology/noise floors from machine precision floors:

```bash
rg "precision_floor|roundoff_floor|unit_roundoff|machine_epsilon|cancellation_ratio|2\.0\s*\*\*\s*-52|sys\.float_info\.epsilon|np\.finfo" src tests Build_Docs -n
rg "noise_floor|Floors|floor" src/lloyd_v4 -n
```

Then require any machine-precision floor to satisfy all of:

- named status family covers the refusal/degradation stratum;
- computed numerical value is preserved, not clamped;
- conditioning notes preserve floor and ratio evidence;
- source comment or report states that the floor is status-only.
