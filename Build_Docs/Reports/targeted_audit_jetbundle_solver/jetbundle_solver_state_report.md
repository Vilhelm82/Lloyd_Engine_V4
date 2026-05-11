# JetBundle and Alpha-Solver State Report

Repository: `/mnt/fast/Lloyd_Engine_V4`

Generated: 2026-05-11

Scope: targeted audit/report only. No runtime source was modified.

## 1. Executive summary

The current trustworthy JetBundle substrate is the core typed result/protocol/provenance/transition machinery plus the Layer 1 primitives: `ProjectiveRatio`, `StratifiedQuadraticRoots`, `typed_value`, `typed_collection`, `typed_finite_difference`, and the internal `typed_log_log_slope` estimator. `exact_quadratic_projection` is trustworthy as a typed projection consumer over quadratic roots, not as a general JetBundle provider.

The current trustworthy alpha-aware solver substrate is narrower: use core + primitives + exact projection where the local model is genuinely quadratic + typed finite-difference/log-log-slope evidence. Do not base the next alpha solver directly on current `branch`, `refinery`, `history`, or `solver` packages except as reference evidence and audit examples.

Safe dependencies:

- `src/lloyd_v4/core/*`
- `src/lloyd_v4/primitives/projective_ratio.py`
- `src/lloyd_v4/primitives/stratified_quadratic_roots.py`
- `src/lloyd_v4/primitives/typed_value.py`
- `src/lloyd_v4/primitives/typed_collection.py`
- `src/lloyd_v4/primitives/typed_finite_difference.py`, with its precision-floor caveat
- `src/lloyd_v4/primitives/typed_log_log_slope.py`, as internal slope evidence
- `src/lloyd_v4/projection/exact_projection.py`, for quadratic projection only

Candidate-only or reference-only:

- `metrology`: candidate substrate for explicit status floors and detection, but policy-sensitive.
- `branch`: reference-only for alpha/solver because declared model bands and fingerprint composition are not primitive alpha evidence.
- `refinery`: reference-only audit/consumer machinery.
- `history`: candidate substrate for later trace evidence, not minimal solver MVP.
- `solver`: reference-only because it consumes caller-supplied local quadratic models and residual evidence.

Recommended next task: **Task 018: Directional AlphaProbe primitive**. Build directional/probe-specific alpha evidence before JetBundle.

## 2. Current task ledger reconstruction

| ID | Title | Report path | Source packages created/modified | Completion tests |
|---|---|---|---|---|
| 000 | Bootstrap substrate | `Build_Docs/Reports/task000/task000_summary.md` | Created `core`, package markers | 9 passed |
| 001 | ProjectiveRatio | `Build_Docs/Reports/task001/task001_summary.md` | Created `primitives/projective_ratio.py`; modified primitives exports/core error docstring | 23 passed |
| 002 | StratifiedQuadraticRoots | `Build_Docs/Reports/task002/task002_summary.md` | Created `primitives/stratified_quadratic_roots.py`; modified primitives exports | 46 passed |
| 003 | ProjectionResultV4 / exact projection | `Build_Docs/Reports/task003/task003_summary.md` | Created `projection`; modified `core/status.py` | 65 passed |
| 004 | Metrology foundation | `Build_Docs/Reports/task004/task004_summary.md` | Created `metrology/noise_floor.py`, `metrology/proxy_calibration.py`; modified status/metrology exports | 95 passed, inferred from full-suite dots |
| 005 | Status-family typing and transitions | `Build_Docs/Reports/task005/task005_summary.md` | Created `core/transitions.py`; modified core/primitives/projection/metrology | 110 passed, inferred from full-suite dots |
| 006 | BranchFingerprint / slope-flow | `Build_Docs/Reports/task006/task006_summary.md` | Created `branch`; modified status and Task 005 audit | 123 passed, inferred from full-suite dots |
| 007 | Protocol-aware refinery | `Build_Docs/Reports/task007/task007_summary.md` | Created `refinery/observations.py`, `slag.py`, `decision.py`; modified status/refinery exports | 156 passed |
| 008 | History-aware status traces | `Build_Docs/Reports/task008/task008_summary.md` | Created `history`; modified status and prior source-purity tests | 177 passed |
| 009 | Typed projection solver | `Build_Docs/Reports/task009/task009_summary.md` | Created `solver`; modified status | 203 passed |
| 009A | Solver scenario hardening | `Build_Docs/Reports/task009A/task009A_summary.md` | Modified `solver/typed_projection_solver.py` | 213 passed |
| 010A | Principle documentation | `Build_Docs/Reports/task010A/task010A_summary.md` | Documentation/manifest only | 217 passed, inferred from baseline plus 4 tests |
| 010B | Layer manifest and closure audit | `Build_Docs/Reports/task010B/task010B_summary.md` | Created audit helpers/tests; modified manifest docs | 222 passed, inferred from full-suite dots |
| 010C | Lineage/provenance audit | `Build_Docs/Reports/task010C/task010C_summary.md` | Created lineage audit helpers/tests; modified manifest docs/tests | 226 passed, inferred from full-suite dots |
| 010-Rebuild-Projection | Typed branch selection / projection rebuild | `Build_Docs/Reports/task010_rebuild_projection/task010_rebuild_projection_summary.md` | Created `projection/branches.py`; modified projection/solver/branch/refinery manifests/tests | 236 passed |
| 010-Sub-A | `typed_collection` | `Build_Docs/Reports/task010_sub_a/task010_sub_a_summary.md` | Created `primitives/typed_collection.py`; modified status/primitives/manifest | Not explicitly stated |
| 010-Sub-B | `typed_value` | `Build_Docs/Reports/task010_sub_b/task010_sub_b_summary.md` | Created `primitives/typed_value.py`; modified status/primitives/manifest | Not explicitly stated |
| 011 | Provenance inputs / content-addressed trace identity | `Build_Docs/Agent_tasks/Completed/codex_task011_provenance_inputs.md` | Modified provenance and primitive inputs; no `Reports/task011` summary found | Not available in report |
| 012-014 | Ambiguous / missing | No matching task report found | No evidence found | Missing |
| 015 | `typed_finite_difference` | `Build_Docs/Reports/task015_summary.md` | Created `primitives/typed_finite_difference.py`; modified status/primitives/manifest/status calculus | 272 passed |
| 016 | `typed_log_log_slope` | `Build_Docs/Reports/task016_summary.md` | Created `primitives/typed_log_log_slope.py`; modified status/primitives/manifest/status calculus | 296 passed |

Notes:

- The 010 sequence fans out into 010A/010B/010C, 010-Rebuild-Projection, and 010-Sub-A/B. The numbering is not linear.
- Task 011 is present as a completed agent task but lacks a `Build_Docs/Reports/task011/` summary.
- Tasks 012, 013, and 014 have no located reports or completed task files.

## 3. Core substrate inventory

`src/lloyd_v4/core/result.py` defines the typed result envelope and typed refusal. It is generic/status-family capable through `TypedResult[ValueT, StatusT]`, stores provenance directly, and serializes status/protocol/refusal evidence. It is safe for JetBundle and solver use.

`src/lloyd_v4/core/status.py` owns every status family. It already has `TransferStatus`, `SlopeStatus`, `ProjectionStatus`, and `SolverStatus`, but no alpha/JetBundle family. New alpha statuses should be added here, not hidden in condition notes.

`src/lloyd_v4/core/protocols.py` provides producer/consumer declarations and family-aware validation. It rejects wrong status families before checking accepted statuses. This is safe substrate for AlphaProbe/JetBundle consumer contracts.

`src/lloyd_v4/core/transitions.py` provides named transition rules. Important detail: `apply_status_transition` uses `rule.transition` before static `mapped_statuses`, so callable authority overrides static maps.

`src/lloyd_v4/core/provenance.py` derives trace IDs from operation identity, expression path, precision/backend/device, measurement resolution, inputs, parents, and provenance status. JetBundle should use `inputs` for raw callable/sample identities and `parents` for derived evidence.

`src/lloyd_v4/core/serialization.py`, `validity.py`, and `conditioning.py` are safe: non-finite values serialize explicitly; validity and conditioning are small typed carriers.

## 4. Certified primitive/projection inventory

`projective_ratio.py` emits exact projective strata and refuses scalarization for infinite/indeterminate cases. It classifies without division and scalarizes only after protocol acceptance. This is certified substrate.

`stratified_quadratic_roots.py` emits quadratic root-state strata, preserves coefficient/discriminant/branch evidence, and routes root selection through ProjectiveRatio scalarization. This is certified for quadratic local models, not for general singularity geometry.

`exact_projection.py` consumes typed root-state and typed branch-selection evidence and emits projection statuses. It preserves root, branch, and selected-root parents. It is certified for exact quadratic projection. It should not be treated as a general solver or JetBundle primitive.

## 5. Transfer and alpha measurement inventory

Located files:

- `src/lloyd_v4/primitives/typed_finite_difference.py`
- `src/lloyd_v4/primitives/typed_log_log_slope.py`
- `tests/test_task015_typed_finite_difference.py`
- `tests/test_task016_typed_log_log_slope.py`

`typed_finite_difference` uses `TransferStatus`. It computes a direct forward difference and records `transfer`, endpoint values, `delta_g`, and `cancellation_ratio`. It does not use `ProjectiveRatio`; it checks `delta_f == 0` before direct division.

`precision_floor` appears in `typed_finite_difference.py` and related docs/tests. In source it is `_precision_floor("raw_python") -> 2.0**-52`. It changes status from observed to `TRANSFER_CANCELLATION_DOMINATED`; it does not clamp or alter `transfer`.

`typed_log_log_slope` uses `SlopeStatus`. It filters only `TRANSFER_OBSERVED` observations and fits ordinary least squares on `log(f)` vs `log(abs(transfer))`. Tests demonstrate alpha-minus-one recovery for `alpha` values 0.5, 1.5, 2.0, and 3.0.

Current alpha evidence is scalar over the supplied observation set. It is not first-class directional evidence, and nested-window alpha stability does not exist.

## 6. Current solver inventory

`SolverStatus` values are defined in `core/status.py`: step advanced, converged identity, converged below detection, projection blocked, tangent blocked, selection refused, branch unidentified, proxy uncalibrated, refinery rejected, history unstable, sequence inconsistent, step budget exhausted, protocol refused, indeterminate.

`LocalQuadraticStepModel` is a supplied data model containing quadratic coefficients, branch, residual observable, optional identity evidence, optional geometry signature, and optional branch/refinery evidence. The solver does not construct this model.

`SolverPolicy` controls below-detection convergence, branch fingerprint gate, refinery gate, and projection-history stability.

Dependency consumption:

- Hard: metrology noise-floor classification, quadratic roots, branch selection, exact projection.
- Optional: branch fingerprint, refinery accepted rewrite, history stable trace.

Residual evidence enters before projection through `classify_against_noise_floor`. Identity evidence and accepted below-detection can stop the step before projection. Otherwise, projection supplies the displacement. There is no hidden score or tie-breaker; branch choice is supplied externally.

Task 009A tests exist as lowercase `tests/test_task009a_*.py`, not uppercase `test_task009A_*.py`.

Suitability: the solver is a reference consumer. It is useful for typed statuses and transition examples, but not suitable as substrate for an alpha-aware solver because it is residual-gated, caller-model-driven, and not alpha-aware.

## 7. Layer 2+ certification assessment

`metrology`: `candidate_substrate`. It is typed and named-rule-driven. However, floors and detection policy influence statuses, so solver use must keep policies explicit.

`branch`: `reference_only`. It has ProjectiveRatio-backed segment slopes, but declared model bands and fingerprint composition make it too consumer-shaped for alpha substrate.

`refinery`: `reference_only`. It is an audit consumer over supplied snapshots and declared slag dimensions. It should not sit inside the alpha solver MVP.

`history`: `candidate_substrate`. It provides useful status trace evidence, but depends on refinery snapshots and is unnecessary for minimal alpha projection.

`solver`: `reference_only`. It demonstrates typed solver status flow, but it is not a native alpha/geometric solver.

No V1/V3 runtime dependency, adapter, bridge, compatibility shim, or cross-engine call was found in the required source-purity searches.

## 8. Projection transition rule ambiguity check

`QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE` has both static `mapped_statuses` and contextual `transition=_projection_transition`.

Because `apply_status_transition` calls `rule.transition` before reading `mapped_statuses`, static mappings do not imply unconditional runtime mappings when a contextual callable exists. The callable can emit `projection_selection_refused` for branch incompatibility even when the static dict maps `two_real_roots` to `projection_transverse`.

Recommendation: **add tests/comments clarifying callable authority**, and preferably mark static mappings as branch-compatible defaults only. Removing static mappings would make coverage audits less direct unless a replacement coverage mechanism is added.

## 9. Precision floor audit

Occurrences found:

| Path | Purpose | Value impact | Recommendation |
|---|---|---|---|
| `src/lloyd_v4/primitives/typed_finite_difference.py:50,60` | Stores/serializes `cancellation_ratio`. | Audit evidence only. | Allowed. |
| `src/lloyd_v4/primitives/typed_finite_difference.py:80,172-185` | Computes cancellation ratio and compares with precision floor. | Status-only; transfer preserved. | Allowed, document as status-only. |
| `src/lloyd_v4/primitives/typed_finite_difference.py:214-217` | Defines raw-python floor as `2.0**-52`. | Status-only. | Allowed but should be named `raw_python_unit_roundoff_floor` or documented harder. |
| `tests/test_task015_typed_finite_difference.py:39,48` | Verifies cancellation-ratio reporting. | Test only. | Allowed. |
| `Build_Docs/Reports/task015_summary.md` and `Build_Docs/Agent_tasks/Completed/codex_task015_typed_finite_difference.md` | Design/report documentation. | Documentation only. | Keep; note source uses `2.0**-52` while task prose mentions `sys.float_info.epsilon`. |
| `Build_Docs/Agent_tasks/codex_task016_typed_log_log_slope.md` | Future multi-precision reference. | Documentation only. | Allowed. |

Recommended audit pattern:

```bash
rg "precision_floor|roundoff_floor|unit_roundoff|machine_epsilon|cancellation_ratio|2\.0\s*\*\*\s*-52|sys\.float_info\.epsilon|np\.finfo" src tests Build_Docs -n
```

Then manually classify hits as machine-precision floors versus legitimate metrology `noise_floor` or mathematical `Floors`. Do not ban `noise_floor`; it is a typed metrology concept.

## 10. JetBundle design implications

`AlphaProbe` should be separate from JetBundle. The current source evidence says alpha measurement is not yet a local state bundle; it is a directional/probe observation derived from callable samples and transfer slopes.

Alpha evidence should be directional/probe-specific. Current `typed_log_log_slope` can recover alpha-minus-one only for a supplied observation family; collapsing that into global scalar evidence would lose the probe path.

Minimal statuses needed:

- `alpha_observed`
- `alpha_insufficient_data`
- `alpha_unstable_window`
- `alpha_cancellation_dominated`
- `alpha_domain_refused`
- `alpha_non_finite`

Safely reusable functions:

- `typed_finite_difference`
- `typed_collection`
- `typed_log_log_slope` as internal slope evidence
- `to_json_safe`, `Provenance`, `TypedResult`, `Validity`, `Conditioning`

Reference-only functions:

- `compare_slope_flow_to_models`
- `build_branch_fingerprint`
- current `evaluate_solver_step` / `run_typed_projection_solver`

JetBundle must explicitly refuse non-callable inputs, non-finite sample coordinates, zero/invalid probe deltas, insufficient observed transfers, cancellation-dominated transfer sets, non-finite slope fits, and mixed probe directions.

JetBundle should be callable-based first. Parser-based input can come later only after callable behavior and provenance identity are certified.

## 11. Solver design implications

The next solver should depend only on core, Layer 1 primitives, exact projection where applicable, and the new directional AlphaProbe. It should not depend on current metrology/branch/refinery/history modules for the MVP.

Smallest acceptance law proving it is not Newton/Halley residual descent:

> Candidate advancement is accepted only when a typed directional AlphaProbe supplies stable alpha evidence and a named projection transition selects an admissible geometric branch; residual magnitude alone cannot advance or rank a candidate.

Killer tests:

- Two candidates have identical residual decrease but different alpha stability; the stable alpha candidate is accepted and the other is refused.
- A cancellation-dominated transfer set preserves computed transfer evidence but refuses solver advancement.
- Tied candidates with equal alpha/projection evidence return an explicit `selection_refused_tie` status, not a hidden score.

Tie handling should be typed and explicit: return a refusal carrying candidate trace IDs and the equality reason. No weighted score, confidence score, residual nudge, or branch-order default.

## 12. Recommended next Codex ticket

**Task 018: Directional AlphaProbe primitive**

Scope: Add a Layer 1 directional AlphaProbe primitive that samples a callable along an explicit probe direction, uses typed finite-difference observations plus typed log-log slope evidence, preserves every sample/transfer/slope parent trace, emits first-class alpha statuses, and refuses insufficient, non-finite, cancellation-dominated, or unstable nested-window evidence without changing computed values. Do not implement JetBundle or solver behavior in this task; produce the certified alpha evidence object the next JetBundle and solver can safely consume.
