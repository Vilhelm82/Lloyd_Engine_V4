# Codex Task 031 — Sterbenz Audit via Refinery MVP (Pure Algebraic, Six Rewrite Candidates)

## 0. Context

This is the depth probe of the V4-native refinery. It uses the Task 030 MVP infrastructure (geometry admissibility gate, burden vector extractor, Pareto comparison) to audit whether Sterbenz's lemma identifies the *minimum-burden* form of `R² − 1 + x` in its applicable region of the pure_algebraic fixture, or whether V4 has found something else.

**The depth question this task settles:** can V4 substrate, on the empirical floor built through the chain-property campaigns and 017c, produce a typed refinery adjudication of an external numerical-analysis mechanism? Task 030 validated that the substrate floor is sufficient for a single-pair, single-fixture decision. Task 031 validates whether the same floor is sufficient for a multi-candidate audit of a named mechanism. Success here unlocks the breadth conversation (multi-fixture audits, audits of other named results — Kahan, Wilkinson, Goldberg). Failure here reveals a substrate gap that must close before breadth is justified.

**Task renumbering note.** The operation-level Sterbenz annotation work previously banked at Task 030 was moved to Task 031 in the Task 030 spec. Task 031 is now reassigned to this Sterbenz audit. The operation-level annotation work is pushed to **Task 032** and may be partially superseded by the audit findings here — that decision is deferred until after this task lands.

**Four possible headlines:**

- `sterbenz_minimum_burden_form_confirmed` — the Sterbenz-blessed reference form is the sole element of the Pareto frontier in the Sterbenz-applicable region. V4 confirms Sterbenz selects the minimum-burden form. Empirical validation of a named numerical-analysis result on V4-native terms.
- `sterbenz_dominated_by_alternative` — the Sterbenz-blessed reference is *not* on the Pareto frontier (strictly dominated by at least one alternative candidate). V4 has improved on a named result. The dominating candidate becomes the V4-native "purest form" for `R² − 1 + x` in this region.
- `sterbenz_tied_with_alternatives` — the Sterbenz-blessed reference is on the Pareto frontier but not alone (tied with or Pareto-incomparable to at least one other candidate). The frontier is a tie-equivalence class. Sterbenz is in it but not unique.
- `sterbenz_audit_indeterminate` — the N-way Pareto comparison does not resolve cleanly. Substrate-floor gap revealed.

All four are legitimate. The pre-registration locks the candidate set and burden dimensions, not the outcome. I genuinely do not know which way this lands.

---

## 1. Repository / Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4`

**Baseline HEAD:** post-030 on `origin/main` (commit `d7a8466` or descendant). Codex starts from current `origin/main`.

**Test baseline:** 644 passing (post-030).

**Test count target:** previous baseline + ~30 new tests. Target ~674 against the 644 baseline.

**Sequencing dependency:** Task 030 (`d7a8466` or descendant) must be on `origin/main`. The Task 030 modules at `src/lloyd_v4/evals/refinery_mvp/` are imported by this task. If 030 is not landed, **halt and report**.

## 2. Task Goal

Audit whether the Sterbenz-blessed form `(R * R) - 1.0 + x` is the minimum-burden representation of the algebraic identity `R² − 1 + x ≡ 0 (when R² = 1 − x)` in the Sterbenz-applicable region `x ≤ 1/2` of the pure_algebraic fixture, across a hand-curated set of six rewrite candidates.

The audit produces one of the four headlines in Section 0, grounded in:

1. A geometry admissibility check on each candidate (all should pass — they're declared algebraic equivalents).
2. Burden vector extraction per candidate in the Sterbenz-applicable region.
3. N-way Pareto frontier identification across the burden vectors.
4. Classification of the Sterbenz-blessed reference's position relative to the frontier.

Full-grid burden vectors are also computed and reported as supplementary evidence (the reassociated form's region-swapped Sterbenz protection is most visible in the full-grid comparison).

## 3. Source Labelling

- **V4-surface (load-bearing):** Layer 1 primitives, Task 030 refinery MVP modules (`geometry_admissibility`, `burden_vector`, `pareto_decision`), the pure_algebraic fixture, the canonical 137-point grid, 017c multi-precision execution machinery, 029-series lattice and polarity campaigns, byte-stability discipline, axioms 1–12.
- **Theorem-derived:** the Sterbenz-applicable region for pure_algebraic (`x ≤ 1/2`), pre-registered from 029c's value-level boundary confirmation; the linear-in-`u_p` model for `b_k` extraction, pre-registered from 017c's R² = 1.0 validation.
- **Proposal evidence:** the six-candidate rewrite set itself (subject to MVP validation); the N-way Pareto frontier algorithm; the four typed outcome categories.
- **V3 reference (concept only):** the V3 refinery's audit purpose informs this task's framing. V3 implementation, status enums, data structures do not transfer. The V3-shape Layer 2 module at `src/lloyd_v4/refinery/` is not imported, called, or referenced.

## 4. Design Principles

1. **No new substrate primitives.** All measurement reuses existing 017c precision battery and 029-series lattice/polarity machinery, applied to new rewrite paths.
2. **No Layer 2 module.** This task extends the evals-layer Task 030 framework. The Layer 2 substrate rebuild remains a separate future task.
3. **No V3-shape import.** Grep test enforces.
4. **Pure_algebraic only.** Non-linear operand transformations (Schwarzschild's `r → 2/r`, SR's `β → β²`) warp the lattice grid spacing before the subtraction occurs, which would confound the audit by entangling operand-path effects with subtraction-topology effects. Pure_algebraic isolates the arithmetic mechanism — operand `x` enters `1 − x` directly, lattice grain is already characterized at 0.25 from 029-series, geometry is linear.
5. **Hand-curated candidate set, not enumerated.** Six rewrites, each declaring which structural property of floating-point propagation it tests. Algorithmic enumeration would produce variants of unclear individual purpose; hand curation lets each candidate carry an explicit hypothesis.
6. **Region-restricted analysis for the audit headline; full-grid for supplementary.** The Sterbenz audit is meaningful only in the Sterbenz-applicable region. Full-grid measurements are recorded for forward observations but do not enter the headline classification.
7. **Pre-registration locks candidates and burden dimensions, not outcome.**
8. **No physics-interpretive language.**

## 5. Primitive-Sufficiency Gate

| Concept used | Source | Status |
|---|---|---|
| Six rewrite candidates as callables on pure_algebraic | New evals-layer module | Hand-curated |
| Multi-precision execution at float32 / float64 / float128 | 017c precision-bound fixture wrappers | Re-used, extended to new paths |
| Lattice campaign output (class + integer residual) | 029-series lattice machinery | Re-used, extended |
| Polarity grid stability (paired with reference) | 026c-prime machinery | Re-used, extended pairwise |
| Burden vector extraction | Task 030 `burden_vector.py` | Re-used, extended to N candidates |
| Geometry admissibility gate | Task 030 `geometry_admissibility.py` | Re-used, applied per candidate |
| N-way Pareto frontier | New evals-layer module | Generalises Task 030's pairwise comparison |
| Decimal-emulated exact intermediate | `decimal.Decimal` arithmetic at fixed Decimal-100 context, cast to float64 for final addition | Admitted as Decimal type-container, same admission as in pure_algebraic fixture's Decimal-50 work |

**Axiom 11 disposition.** No named mathematical content imports. No `math.fma` (which would violate Axiom 11). The Decimal-emulated candidate uses `decimal.Decimal` as a type container at fixed precision, then casts back — the same admission already granted in the pure_algebraic fixture's decimal-50 work. This tests the *substrate property* of infinite-precision intermediate before final rounding, not the named mechanism FMA per se.

**Axiom 12 disposition.** Every burden dimension traces to a Layer 1 primitive via existing campaign measurement provenance. The N-way Pareto frontier is a generalisation of the pairwise Pareto comparison from Task 030, with full lineage to its parent operation. No new substrate concept is minted.

## 6. Required Deliverables

### 6.1 Pre-registration document

`Build_Docs/Reports/task031_sterbenz_audit/pre_registration.md`

Committed in a dedicated commit before any measurement code runs. Structured in three sections:

**Section A — Rewrite candidate set (locked before measurement)**

The six candidates with their declared hypotheses. Each candidate carries:
- `candidate_id` (e.g., `c1_reference`, `c2_reassociated`, etc.)
- `expression` (Python callable definition as committed source)
- `declared_algebraic_identity` (must match `pure_algebraic_zero_constraint`)
- `tested_property` (one-line statement of which structural property this candidate probes)
- `expected_burden_relation_to_reference` (one of: `predicted_tied`, `predicted_better`, `predicted_worse`, `genuine_uncertainty`)

The six candidates:

| ID | Expression | Tested property | Expected relation |
|---|---|---|---|
| `c1_reference` | `(R * R) - 1.0 + x` | Sterbenz-blessed explicit subtraction | reference (baseline) |
| `c2_reassociated` | `(R * R) + (x - 1.0)` | Reassociation; swaps Sterbenz protection from x ≤ 1/2 to x ≥ 1/2 | predicted_worse in Sterbenz region |
| `c3_factored` | `(R - 1.0) * (R + 1.0) + x` | Catastrophic cancellation negative control (`R - 1` cancels when R ≈ 1) | predicted_worse (cleanly Pareto-dominated) |
| `c4_power_operator` | `(R ** 2) - 1.0 + x` | Operator-shift (`R ** 2` vs `R * R`) | predicted_tied with reference |
| `c5_identity_padded` | `((R * R) - 1.0) / 1.0 + x` | Identity-padding (`/ 1.0` no-op); tests whether `operation_chain_depth` differentiates while other dimensions tie | predicted_worse on `operation_chain_depth` only |
| `c6_decimal_emulated` | `float(Decimal(R) * Decimal(R) - Decimal(1)) + x` (intermediate at Decimal-100 context, cast to float64) | Infinite-precision intermediate before final rounding; tests whether substrate-level intermediate exactness beats operation-level Sterbenz exact subtraction | genuine_uncertainty |

**Section B — Burden vector dimensions and Pareto rule (locked before measurement)**

Same dimensions as Task 030 (`b_k_point_estimate`, `b_k_ci_lower`, `b_k_ci_upper`, `lattice_class`, `max_integer_residual`, `polarity_class`, `calibration_zero_preserved`, `operation_chain_depth`). Same "better" directions. Same equality-required and paired-equal constraints. N-way Pareto frontier: a candidate is on the frontier if no other candidate strictly dominates it.

**Section C — Sterbenz-applicable region and headline classification logic (locked before measurement)**

- Sterbenz-applicable region: `x ≤ 1/2` for pure_algebraic.
- Audit headline determined by:
  - `sterbenz_minimum_burden_form_confirmed` if `c1_reference` is the sole Pareto-frontier element.
  - `sterbenz_dominated_by_alternative` if `c1_reference` is not on the Pareto frontier (strictly dominated).
  - `sterbenz_tied_with_alternatives` if `c1_reference` is on the frontier but not alone.
  - `sterbenz_audit_indeterminate` if the comparison produces inconsistent orderings or three or more required dimensions return unavailable-data sentinels.
- The factored form `c3_factored` is expected to be off the frontier. If `c3_factored` lands on the frontier, the audit headline is `sterbenz_audit_indeterminate` regardless of other results — this is the calibration: if the refinery cannot detect catastrophic cancellation, the audit is not trustworthy on this dataset.

Pre-registration commit message:

```
Task 031 pre-registration: Sterbenz audit candidates, burden dimensions, headline logic

Predictions registered before measurement code execution. Predictions are
not to be edited after this commit. Subsequent commits carry measurement
runs and observed results.
```

### 6.2 Rewrite candidates module

`src/lloyd_v4/evals/sterbenz_audit/rewrite_candidates.py`

Defines the six candidates as precision-parameterised callables (using Task 017c's `precision_bound_fixtures` pattern). Each candidate is a function `(x_value, precision_spec) -> typed_residual` consuming the canonical 137-point grid value at the declared precision.

The Decimal-emulated candidate `c6_decimal_emulated` uses `decimal.localcontext(decimal.Context(prec=100))` for the intermediate `Decimal(R) * Decimal(R) - Decimal(1)` computation, then casts to the target output precision before the final `+ x`. The Decimal context is local; it does not leak. The Decimal precision (100) is fixed regardless of the target output precision.

For `c6_decimal_emulated`: only binary output precisions are supported (float32, float64, float128 if available). Calling with a Decimal output precision raises `NotImplementedError` with the exact message `"c6_decimal_emulated only supports binary output precisions (intermediate is always Decimal-100)"`.

### 6.3 Measurement extension

`src/lloyd_v4/evals/sterbenz_audit/measurement_extension.py`

For each new candidate (c2 through c6), drives:

- Multi-precision execution at float32, float64, float128-if-applicable (using 017c machinery)
- Lattice campaign (using 029-series machinery) at float64
- Polarity grid stability paired against `c1_reference` (using 026c-prime machinery) at float64

The reference candidate `c1_reference` is identical to F2 of pure_algebraic; its measurements are read from existing campaign reports (no fresh measurement).

### 6.4 N-way Pareto frontier module

`src/lloyd_v4/evals/sterbenz_audit/n_way_pareto.py`

Exposes `compute_pareto_frontier(burden_vectors: list[BurdenVector], burden_policy) -> ParetoFrontierResult`.

A candidate is on the frontier if no other candidate strictly Pareto-dominates it (per the same rule as Task 030's pairwise comparison, applied across all pairs). The result records:

- `frontier_members` — list of candidate IDs on the frontier
- `pairwise_dominance` — N×N matrix of pairwise `compare_burden_vectors` results
- `dominated_candidates` — candidates strictly dominated, with the identifying dominator
- `incomparable_pairs` — pairs that are mutually non-dominating but not tied

### 6.5 Sterbenz audit orchestrator

`src/lloyd_v4/evals/sterbenz_audit/audit_run.py`

Top-level `run_sterbenz_audit(fixture_name, region_predicate, candidate_ids) -> SterbenzAuditResult`.

Sequences: load candidate definitions → run admissibility on each → extract burden vectors (region-restricted and full-grid) → compute Pareto frontier (region-restricted) → classify headline. Returns a typed audit result.

### 6.6 Measurement output JSONs

`Build_Docs/Reports/task031_sterbenz_audit/measurement_aggregate.json`

Byte-stable. Contains per-candidate per-precision per-region observations, lattice classifications, polarity classifications paired against reference.

### 6.7 Region-restricted burden vectors

`Build_Docs/Reports/task031_sterbenz_audit/sterbenz_region_burden_vectors.json`

Byte-stable. Six burden vectors restricted to the Sterbenz-applicable region (`x ≤ 1/2`).

### 6.8 Full-grid burden vectors (supplementary)

`Build_Docs/Reports/task031_sterbenz_audit/full_grid_burden_vectors.json`

Byte-stable. Six burden vectors over the full canonical 137-point grid. Supplementary; does not enter headline classification.

### 6.9 Pareto frontier record

`Build_Docs/Reports/task031_sterbenz_audit/pareto_frontier.json`

Byte-stable. The full N×N pairwise dominance matrix, frontier membership, dominated candidates with their dominators, and incomparable pairs. Computed on the Sterbenz-region burden vectors.

### 6.10 Headline classification record

`Build_Docs/Reports/task031_sterbenz_audit/headline_classification.md`

One of the four headlines with one-paragraph justification grounded in §6.9.

### 6.11 Task summary

`Build_Docs/Reports/task031_sterbenz_audit_summary.md`

Standard structure (mirror Task 030 / 017c). Must include:

- Pre-registration commit hash.
- Six candidates with their hypotheses and pre-registered expected relations.
- Per-candidate burden vector tables, Sterbenz-region and full-grid.
- Pareto frontier composition.
- Headline classification with justification.
- **Region comparison** for `c2_reassociated`: explicit comparison of its burden in the Sterbenz region (`x ≤ 1/2`) vs the Sterbenz-inapplicable region (`x > 1/2`). The pre-registered prediction is that `c2_reassociated` is *worse* than `c1_reference` in the Sterbenz region (where x − 1 is not Sterbenz-protected) but *equivalent or better* in the inapplicable region (where x − 1 IS Sterbenz-protected). This is the region-swap prediction.
- **Calibration check**: confirmation that `c3_factored` is off the Pareto frontier. If this fails, the headline is forced to `sterbenz_audit_indeterminate`.
- **The interesting answer**: position of `c6_decimal_emulated` on the frontier. If it dominates the reference, V4 has empirically shown that substrate-level intermediate exactness beats operation-level Sterbenz exact subtraction in this region. If it doesn't, Sterbenz's protection is robust against the strongest alternative.
- Tests, byte-stability, discipline gates.
- Forward observations (no next-task drafts).

## 7. Required Tests

Approximately **30 new tests** in `tests/test_task031_sterbenz_audit.py`.

### 7.1 Pre-task evidence (~3 tests)

- Confirm Task 030 commit `d7a8466` (or descendant) on `origin/main`.
- Confirm 017c, 029a/c, 026c-prime, 030 report JSONs exist at expected paths.
- Record HEAD hash and pre-existing test count.

### 7.2 Rewrite candidate tests (~6 tests)

- Each of six candidates produces a finite non-NaN value at every cell of the canonical grid at float64.
- `c1_reference` value equals F2 of pure_algebraic to within machine epsilon (sanity: reference IS F2).
- `c4_power_operator` (`R ** 2`) and `c1_reference` (`R * R`) produce bit-identical residuals at every cell at float64 (in CPython, `R ** 2` for float `R` routes to FMUL).
- `c5_identity_padded` and `c1_reference` produce bit-identical residuals at every cell at float64 (`/ 1.0` is an IEEE identity).
- `c3_factored` produces residuals that are at least one order of magnitude larger than `c1_reference` somewhere in the canonical grid (catastrophic cancellation signal).
- `c6_decimal_emulated` raises `NotImplementedError` with the exact message from §6.2 when called with a Decimal output precision.

### 7.3 Measurement extension tests (~4 tests)

- 017c precision battery applied to c2 through c6 produces b_k fits at float32, float64, float128-if-applicable.
- 029-series lattice campaign applied to c2 through c6 produces lattice_class and max_integer_residual at float64.
- 026c-prime polarity grid stability paired (reference, candidate) for c2 through c6 produces polarity classifications.
- The reference c1's measurements are read from existing campaign reports, not re-measured.

### 7.4 N-way Pareto tests (~5 tests)

- Frontier on a synthetic three-candidate input with one strictly dominated candidate returns the two non-dominated as frontier members.
- Frontier on synthetic all-tied input returns all members.
- Frontier on synthetic all-incomparable input returns all members.
- Pairwise dominance matrix is symmetric in the appropriate sense (A dominates B iff B is dominated by A).
- The result records each pair's outcome explicitly.

### 7.5 Region-restriction tests (~3 tests)

- Sterbenz-applicable region predicate `x ≤ 0.5` correctly subsets the canonical grid.
- Burden vectors restricted to the Sterbenz region differ from full-grid burden vectors for at least one candidate (the restriction is non-trivial).
- The grid contains x = 0.5 exactly for boundary inclusion.

### 7.6 Byte-stability tests (~3 tests)

- `measurement_aggregate.json` byte-identical between two consecutive runs.
- `sterbenz_region_burden_vectors.json` byte-identical between two consecutive runs.
- `pre_registration.md` byte-identical to committed file at task close.

### 7.7 Discipline gate tests (~6 tests)

- No imports from `src/lloyd_v4/refinery/` in any new file. Grep test.
- No `math.fma`, `math.cbrt`, `cmath`, `scipy`, `sympy`, `mpmath`, `statsmodels`, `numpy.special`, `numpy.random` introduced.
- No hardcoded mathematical constants.
- `layer_manifest.json` byte-identical to start.
- No physics-interpretive language (grep).
- `typed_finite_difference` source byte-identical to start.

## 8. Required Commands

1. `git status` — clean.
2. `git log -1 --oneline` — record HEAD.
3. Confirm Task 030 commit `d7a8466` (or descendant) and all required prior-task reports on `origin/main`.
4. `pytest -q tests/` — baseline.
5. Create `pre_registration.md` per §6.1.
6. `git add Build_Docs/Reports/task031_sterbenz_audit/pre_registration.md`
7. `git commit -m "Task 031 pre-registration: Sterbenz audit candidates, burden dimensions, headline logic..."` (full message per §6.1)
8. Record pre-registration commit hash.
9. Implement modules and tests.
10. `pytest -q tests/` — confirm all pass.
11. Run audit; write all output JSONs and `headline_classification.md`.
12. Run audit a second time; diff against repository copies; byte-identical.
13. Write `task031_sterbenz_audit_summary.md`.
14. `pytest -q tests/` — final.
15. `git add -A && git commit -m "Task 031: Sterbenz audit — <headline>" && git push origin main`.
16. `git status` — clean.
17. `git log -2 --oneline` — both commits visible on `origin/main`.

## 9. Non-Goals (Loud and Explicit)

- **NOT** modifying any substrate primitive.
- **NOT** modifying `layer_manifest.json`.
- **NOT** building a Layer 2 module.
- **NOT** importing from `src/lloyd_v4/refinery/`.
- **NOT** auditing fixtures other than pure_algebraic.
- **NOT** auditing named mechanisms other than Sterbenz.
- **NOT** extending the candidate set beyond the six declared in pre-registration.
- **NOT** using `math.fma` (Axiom 11). `c6_decimal_emulated` uses Decimal as the V4-admitted substitute.
- **NOT** algorithmically enumerating rewrites. The candidate set is hand-curated and locked.
- **NOT** running the audit at multiple Decimal precisions on c6. The Decimal intermediate is fixed at prec=100; output is cast to binary precisions only.
- **NOT** promoting any new concept to substrate.
- **NOT** drafting Task 032 (operation-level Sterbenz annotation), the Layer 2 refinery rebuild task, or any forward task in the summary.
- **NOT** using weighted aggregation. Decision is N-way Pareto on the burden vector.

## 10. Completion Report

`Build_Docs/Reports/task031_sterbenz_audit_summary.md`, in this order:

1. **Scope.**
2. **Pre-registration commit hash and date.**
3. **Six candidates table** — IDs, expressions, declared hypotheses, pre-registered expected relations, observed relations to reference.
4. **Sterbenz-region burden vector table** — all six candidates, all eight dimensions, with provenance.
5. **Full-grid burden vector table** — supplementary, all six candidates.
6. **Pareto frontier composition** — frontier members, dominated candidates, incomparable pairs.
7. **Region-swap finding for c2_reassociated** — burden comparison in Sterbenz region vs Sterbenz-inapplicable region, with mechanism statement.
8. **Calibration check** — c3_factored Pareto-dominated status, confirming the audit can detect catastrophic cancellation.
9. **Decimal-intermediate finding for c6** — position relative to reference, with mechanism interpretation.
10. **Headline classification** with one-paragraph justification grounded in the Pareto frontier composition.
11. **Tests** — total count, new tests added, pytest result.
12. **Byte-stability confirmation.**
13. **Discipline gates** explicit confirmation, including V3-shape no-import grep result.
14. **Files changed.**
15. **Forward observations** — five categories required: (a) whether substrate-level intermediate exactness dominated Sterbenz operation-level exactness, (b) whether the reassociation region-swap prediction held, (c) what the audit reveals about the refinery's ability to discriminate operationally-different but mathematically-equivalent rewrites, (d) whether any candidate produced an unexpected burden profile inviting further investigation, (e) what extensions would be needed to audit non-Sterbenz mechanisms (Kahan summation, Wilkinson bounds, etc.). **No next-task drafts.**

## 11. Acceptance Criteria

1. Pre-registration committed as its own commit before any measurement code ran.
2. All pre-existing tests pass.
3. All new tests pass (~30 new).
4. All six candidates admissible under the geometry gate (none should fail admissibility — all declare the same algebraic identity).
5. All six candidates produce populated burden vectors in the Sterbenz region (no all-sentinel rows).
6. `c3_factored` is off the Pareto frontier (calibration check). If this fails, the headline is forced to `sterbenz_audit_indeterminate`.
7. `c4_power_operator` and `c5_identity_padded` produce bit-identical residuals to `c1_reference` at float64 (these are operational sanity checks).
8. All output JSONs byte-stable.
9. `pre_registration.md` byte-identical to committed file.
10. `layer_manifest.json` byte-identical to start.
11. No imports from `src/lloyd_v4/refinery/`.
12. No forbidden imports or patterns.
13. Headline classification recorded.
14. Forward observations recorded without drafting next task.
15. Final commit pushed to `origin/main`. `git status` clean. Both commits on `origin/main` in order.

## 12. Discipline Notes

### Axiom 10 — V3 reference-only (with non-reflexive interpretation)

The V3 refinery's audit purpose is reference for *what* this task does. V3 implementation, status enums, parent set, data structures do not transfer. The Task 030 framework that this task extends is V4-native, built from V4 substrate. The audit shape — geometry admissibility, burden vector, Pareto comparison — is V4-native through Task 030. This task adds N-way comparison and region restriction, both of which are V4-clean extensions.

### Axiom 11 — Epistemic stance only

No named numerical-analysis content imported as substrate. Sterbenz is the audit *subject*, not a substrate building block. `math.fma` is not imported; the Decimal-emulated candidate uses Decimal as a V4-admitted type container at fixed precision. The Decimal-100 intermediate context tests the substrate property of infinite-precision intermediate rounding, accessed through Decimal arithmetic, not the named function FMA.

### Axiom 12 — Self-derivation

Every concept used traces to existing parent-layer provisions. Task 030's refinery MVP modules are the parent layer for this task's audit machinery. The N-way Pareto frontier generalises Task 030's pairwise comparison with explicit provenance. No new substrate concept is minted.

### Pre-registration is non-negotiable

The six candidates are locked. Burden dimensions are locked. The headline classification logic is locked. The calibration requirement (c3_factored must be off the frontier) is locked. Post-hoc adjustment of any of these is forbidden. If observation diverges from pre-registration, the divergence is reported honestly and the summary records the actual headline.

### Calibration before audit

The c3_factored candidate is included specifically as a deliberately-pathological control. The refinery's ability to detect and reject catastrophic cancellation is a precondition for the audit being trustworthy. If c3_factored lands on the Pareto frontier, the audit is not trustworthy on this dataset and the headline reflects this honestly.

### Discovery and promotion separated

If the audit reveals a substrate-level finding (e.g., the Decimal-intermediate property dominates Sterbenz exact-subtraction), that is a forward observation. Promotion of any concept to substrate happens in a separate task with separate gates. This task does not promote.

### Byte-stability across measurement

All measurement runs are deterministic. No `numpy.random`. No global Decimal context mutation. Repeat runs produce byte-identical output. Diff verifies.

### Git discipline non-negotiable

Pre-registration commit lands on `origin/main` before measurement code runs. Main task commit lands before the task is considered closed.

---

## Appendix A — Candidate hypotheses in detail

**c1_reference: `(R * R) - 1.0 + x`** — the Sterbenz-blessed explicit subtraction. For `x ≤ 1/2`, `R² ≥ 1/2`, and Sterbenz's lemma guarantees `R² − 1` is computed exactly. This is the form the lemma identifies as exact-arithmetic in this region. The audit asks: is this form *also* the minimum-burden representation, or does another form match or beat it?

**c2_reassociated: `(R * R) + (x - 1.0)`** — Sterbenz exactness moves from the `R² − 1` subtraction (protected for `x ≤ 1/2`) to the `x − 1` subtraction (which has different protection conditions). Specifically: Sterbenz's lemma protects `a − b` when `a/2 ≤ b ≤ 2a`. For `x − 1` with `x ≤ 1/2`, we'd need `x/2 ≤ 1 ≤ 2x`, which fails at the upper bound (1 > 2x when x ≤ 1/2). So `x − 1` is *not* Sterbenz-protected in the Sterbenz-applicable region of the original form. This candidate moves Sterbenz protection out of the region where the audit operates. Pre-registered prediction: c2 is *worse* than c1 in the Sterbenz region, *better* than c1 in the inapplicable region. This region-swap is the substantive test.

**c3_factored: `(R - 1.0) * (R + 1.0) + x`** — algebraically equivalent (`R² − 1 = (R−1)(R+1)`), but the `R − 1` subtraction is catastrophic when `R ≈ 1` (which is exactly the regime near the branch point). Pre-registered prediction: `b_k` for this candidate is at least one order of magnitude larger than `c1_reference` in the Sterbenz region, and c3 is strictly Pareto-dominated by c1. This is the calibration: the refinery must detect and reject this candidate. If it doesn't, the audit is untrustworthy.

**c4_power_operator: `(R ** 2) - 1.0 + x`** — in CPython, `R ** 2` for a float `R` typically routes through `BINARY_POWER` which optimizes to `FMUL` for integer exponent 2. The residual should be bit-identical to `c1_reference`. Pre-registered prediction: tied with reference on every dimension. This is a sanity test: if c4 differs measurably from c1, something unexpected is happening in the interpreter's power-operator handling.

**c5_identity_padded: `((R * R) - 1.0) / 1.0 + x`** — `/ 1.0` is an IEEE 754 identity; the residual is bit-identical to `c1_reference`. Pre-registered prediction: tied on b_k, lattice_class, max_integer_residual, polarity_class, calibration_zero_preserved; worse only on `operation_chain_depth` (one additional operation). This tests whether the refinery correctly identifies "more operations producing identical results" as pure bloat — strictly Pareto-dominated by c1 on the single discriminating dimension. If c5 *isn't* Pareto-dominated, the operation_chain_depth dimension isn't doing the work it should be doing.

**c6_decimal_emulated: `float(Decimal(R) * Decimal(R) - Decimal(1)) + x`** — the intermediate `R² − 1` is computed at Decimal-100 precision (effectively infinite for this purpose), then cast to float64 with a single final rounding, then added to `x`. This is the Axiom-11-admissible analog of hardware FMA: a single final rounding instead of two. Pre-registered prediction: genuine uncertainty. If c6 dominates c1, the V4-native finding is that substrate-level intermediate exactness is at least as strong as operation-level exact subtraction. If c6 doesn't dominate, Sterbenz's protection is shown robust against the strongest alternative. Either direction is a result.

## Appendix B — Why this set audits Sterbenz cleanly

Sterbenz's lemma is a claim about *one specific arithmetic form* (explicit subtraction) being exact in a specific region. The audit asks whether that form is the *minimum-burden* representation of the same algebraic identity in the same region. The six candidates span:

- The Sterbenz-blessed form itself (c1)
- A reassociation that moves Sterbenz protection out of the audit region (c2)
- A deliberately pathological alternative (c3, calibration)
- Two operationally-different but numerically-identical forms (c4, c5 — refinery discrimination tests)
- A substrate-property alternative that bypasses Sterbenz's operation-level protection entirely (c6)

If c1 is on the frontier alone, Sterbenz is empirically validated on V4-native terms. If c6 ties or dominates, V4 has empirically discovered that substrate-level intermediate exactness is at least as protective as operation-level exact subtraction — a substantive finding that opens new territory for the refinery to audit other named results. If c2 lands as predicted (worse in Sterbenz region, better in inapplicable region), the region-dependent burden profile is itself a publishable observation.

The audit is informative regardless of which way it lands.
