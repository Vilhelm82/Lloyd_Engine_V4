# Codex Task 017c — Multi-Precision Execution and Empirical Validation of Theorem 2

## 0. Post-029c finalisation

This is the shippable version of the previously queued 017c draft. Task 029c landed on `origin/main` (commit `975a3fb`, headline `chain_property_universal`), and the four-fixture cross-comparison framework is in place. The six refinement points flagged in the queued draft are resolved as follows:

1. **Fixture scope** — 4 fixtures: Schwarzschild, SR, pure algebraic, cbrt. (`chain_property_universal` landed cleanly; cbrt is in.)
2. **Decimal cube root** — scope-reduction adopted. The cbrt fixture executes at binary precisions only (float32, float64, float128-if-applicable). The other three fixtures execute the full precision battery (binary + decimal-50/100/200). The paper documents the asymmetry honestly: `Decimal.sqrt()` is native and context-bound; `Decimal` has no native cube root, so introducing one would either bake `**(Decimal(1)/Decimal(3))` (different error structure than `numpy.cbrt`, breaks cross-fixture comparability) or a hand-rolled Newton iteration (introduces solver dynamics into a fixture definition). Asymmetric coverage with explicit documentation is more honest than dishonest symmetry.
3. **Sterbenz boundary location** — value-level boundary at `R^n ≥ 1/2` confirmed by 029c across radical degrees. Per-fixture boundaries: r = 4 (Schwarzschild), β = 1/√2 (SR), x = 1/2 (pure algebraic and cbrt).
4. **R² threshold** — finalised at R² ≥ 0.98 for paths in their regular (non-Sterbenz) region. The Sterbenz region is evaluated by a different test (see point 5).
5. **|a_k| threshold** — replaced with a statistical test. Intercept `a_k` is consistent with zero if the deterministic bootstrap 95% CI on `a_k` includes zero. This is more principled than a hard magnitude threshold and self-calibrating across precisions.
6. **F5+ inclusion** — `P_compound_split` and `P_sign_c` are included as additional non-load-bearing fits (029b + 029c confirmed universal across radical degree). `P_distrib_sqrt_mul` is excluded from 017c (029b/029c established sqrt-specificity; multi-precision fitting on it does not test Theorem 2 universally).

Additional structural refinement to the Sterbenz-region prediction: inside the Sterbenz-applicable region, F2's slope `b_k` is predicted to be **statistically indistinguishable from zero** (Sterbenz mechanism makes the subtraction *exact*, so the precision-scaling term vanishes). This is sharper than the queued draft's "weaker threshold inside Sterbenz region" language and matches the mechanism story in the paper. F3's slope is predicted indistinguishable from zero everywhere (calibration).

If any of these resolutions are wrong, override before this ships to Codex. The spec below is otherwise ready to execute.

---

## 1. Repository / Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4`

**Baseline HEAD:** post-029c on `origin/main` (commit `975a3fb` or its descendant). Codex starts from current `origin/main` at task execution time.

**Test baseline:** 582 passing (post-029c). Whatever the actual count is at task start, record it.

**Test count target:** previous baseline + ~35 new tests. Target ~617 against the 582 baseline.

**Sequencing dependency:** this task assumes Task 029c has landed. If `975a3fb` (or a descendant carrying its content) is not on `origin/main`, **halt and report**.

## 2. Task Goal

Empirically validate **Theorem 2 (precision-scaling separation)** from `transfer_function_exponent_family_v3.tex`. The theorem is currently asserted, not demonstrated. It is the load-bearing resolution to the self-reference problem in the paper. This task closes the gap by running `typed_finite_difference` at multiple precisions across the four chain-property fixtures and fitting the per-precision conditioning amplitudes against unit roundoff.

The form of the claim to be tested:

```
C_{p,k} = a_k + u_p · b_k
```

where `p` indexes precision (each with its own unit roundoff `u_p`), `k` indexes path (F1, F2, F3, F4), `a_k` is the path-invariant geometric amplitude, and `b_k` is the path-dependent arithmetic conditioning amplitude.

**The exact statement of Theorem 2 and the canonical definition of `C_{p,k}` are read from `transfer_function_exponent_family_v3.tex` and transcribed verbatim into the pre-registration.** Codex must not paraphrase; the test in §7.5 enforces that the pre-registration's definition matches the paper's line-for-line.

Four sub-claims to test per path per fixture:

1. **Linear-in-`u_p` fit quality (regular region).** R² of the linear fit `C_{p,k} ~ a_k + b_k · u_p` exceeds 0.98 for paths evaluated outside the Sterbenz-applicable region.
2. **Intercept consistent with zero.** `a_k`'s deterministic bootstrap 95% CI includes zero for all four paths in all four fixtures.
3. **Slope structure.** In the regular region, `b_k` for F1, F2, F4 are each distinguishable from zero (95% CI excludes zero) and distinguishable from each other (paths resolve). F3's slope is indistinguishable from zero in every region (calibration).
4. **Sterbenz-region b_k vanishing.** Inside the Sterbenz-applicable region of each fixture, F2's slope `b_k` is indistinguishable from zero (the Sterbenz mechanism makes the subtraction exact, so the precision-scaling term vanishes). This is the sharpest empirical prediction the mechanism story makes.

**Three possible headlines:**

- `theorem2_validated` — all four sub-claims hold across all fixtures in scope. Theorem 2 graduates from asserted to empirically validated. Paper revision can move the theorem from "proposed resolution" to "demonstrated resolution" of the self-reference problem.
- `theorem2_partial` — some sub-claims hold, some don't. The paper's claim scopes to what's empirically supported, with explicit per-claim language.
- `theorem2_refuted` — the linear-in-`u_p` model does not capture the precision-scaling behaviour. Paper requires a different resolution to the self-reference problem.

All three are legitimate outcomes. Codex does not pre-decide.

## 3. Source Labelling

- **V4-surface (load-bearing):** Layer 1 `typed_finite_difference` primitive (existing, no extension), typed result protocol, byte-stability discipline, axioms 1–12, all four chain-property fixtures, polarity-grid-stability framework, lattice framework.
- **Theorem-derived:** Theorem 2 statement and `C_{p,k}` definition (read from `transfer_function_exponent_family_v3.tex` verbatim, not paraphrased in this spec); the Sterbenz-region vanishing prediction (R^n ≥ 1/2 → exact subtraction → b_k for F2 → 0).
- **Proposal evidence:** the `theorem2_*` classification headlines; the R² ≥ 0.98 threshold; the bootstrap-CI-includes-zero criterion for intercept (pre-registered, subject to the campaign result).

## 4. Design Principles

1. **No extension to substrate primitives.** `typed_finite_difference` already exists and already carries precision metadata per Axiom 5. Multi-precision execution is feeding it inputs at different precisions, not extending its protocol. If at any point this task appears to require modifying `typed_finite_difference`, halt and report.
2. **No `layer_manifest.json` changes.**
3. **Precision-parameterised fixture wrappers.** The four fixtures are wrapped (not re-implemented) to accept a precision specification. The wrapper composes the existing fixture definition with precision selection. No fixture **logic** is duplicated; only the precision binding is new.
4. **Asymmetric precision coverage handled explicitly.** Three fixtures (Schwarzschild, SR, pure algebraic) execute at six precisions (float32 / float64 / float128-if-applicable / decimal-50 / decimal-100 / decimal-200). The cbrt fixture executes at three precisions (float32 / float64 / float128-if-applicable). The aggregate report represents the coverage asymmetry explicitly; cbrt rows for Decimal precisions are recorded as "out-of-scope-by-design", not as missing data.
5. **No scipy.** Linear fits use `numpy.linalg.lstsq` or hand-rolled normal-equation least squares. Both are admitted (numpy proper, not numpy.special). No `scipy.optimize`, no `scipy.stats`. No `statsmodels`.
6. **Bootstrap confidence intervals via `random.Random(seed)`.** Deterministic. No `numpy.random`.
7. **Pre-registration is mandatory.** Same protocol as 029c: dedicated commit before any campaign code runs; byte-identical at completion; commit message fixed.
8. **Platform reporting for `numpy.float128`.** `numpy.float128` is platform-dependent (80-bit extended on x86_64 Linux, may be float64 on Windows or ARM). At task start, record `numpy.finfo(numpy.float128)`. If `eps(float128) == eps(float64)` on the host, the float128 row is dropped from the analysis with an explicit note. Do not silently use float128 as if it were a separate precision when the platform doesn't support it.
9. **No physics-interpretive language.**
10. **One precision-axis variation per task.** This task adds the multi-precision execution axis. It does not add new fixtures, does not add new paths beyond F1–F4 and the two pre-confirmed F5+ paths, does not add new substrate primitives.

## 5. Primitive-Sufficiency Gate

| Concept used | Source layer | Status |
|---|---|---|
| `typed_finite_difference` | Layer 1 (existing) | Re-used, unmodified |
| Four chain-property fixtures | Evals layer (existing) | Re-used, wrapped for precision |
| Canonical 137-point grid | Evals layer (existing) | Re-used at each precision |
| `numpy.float32`, `numpy.float64`, `numpy.float128` | numpy (admitted as type containers) | New use of float32 and float128 |
| `decimal.Decimal` with varying `getcontext().prec` | Standard library (admitted) | Already used at decimal-50 |
| `Decimal.sqrt()` | Standard library, context-bound | Already used in pure-algebraic fixture |
| `numpy.linalg.lstsq` or hand-rolled normal equations | numpy proper | Admitted |
| `random.Random(seed)` | Standard library, admitted for deterministic bootstrap | New use for fit CIs |
| `math.comb` for any binomial p-value reporting | Existing admitted exception | Re-used |
| `numpy.finfo` for u_p computation | numpy (type introspection, not named mathematical content) | New use |

**Decimal cube root: out-of-scope-by-design.** The cbrt fixture is not executed at Decimal precisions. The aggregate report represents this as an explicit out-of-scope-by-design marker, not as missing data. No `Decimal`-context-aware cube root is introduced.

**Axiom 11 disposition.** All precisions used (numpy floats, Decimal contexts) are type-container admissions, not named mathematical content. `numpy.finfo` returns type-introspection data, not named mathematical content. None of these touch substrate; they live at the evals layer.

**Axiom 12 disposition.** Every concept used traces to existing parent-layer provisions plus the new evals-layer utilities (unit-roundoff calculator, precision-parameterised fixture wrappers, linear-fit utility, bootstrap CI utility). No new substrate concepts.

## 6. Required Deliverables

### 6.1 Pre-registration document

`Build_Docs/Reports/task017c_multi_precision_theorem2/pre_registration.md`

Committed in a dedicated commit before any campaign code runs. Contains:

1. The Theorem 2 statement and `C_{p,k}` definition transcribed **verbatim** from `transfer_function_exponent_family_v3.tex`.
2. The four sub-claim thresholds (R² ≥ 0.98 in regular region; intercept CI includes zero; slope structure; Sterbenz-region b_k vanishing).
3. The precision battery per fixture (six precisions for Schw/SR/pure-algebraic; three precisions for cbrt — out-of-scope-by-design for Decimal).
4. The platform's `numpy.finfo(numpy.float128)` output at task start.
5. The Sterbenz-applicable region per fixture (r ≥ 4, β ≤ 1/√2, x ≤ 1/2 for pure algebraic and cbrt).
6. Statement that predictions are not to be edited after this commit.

Pre-registration commit message:

```
Task 017c pre-registration: Theorem 2 multi-precision validation predictions

Predictions registered before campaign execution. Predictions are not to
be edited after this commit. Subsequent commits carry the campaign run
and observed results.
```

### 6.2 Precision-parameterised fixture wrappers

`src/lloyd_v4/evals/precision/precision_bound_fixtures.py` (or whatever directory mirrors existing conventions).

Per fixture, a precision-parameterised callable producing four-form values at a specified precision. For binary precisions: cast inputs via `numpy.float32(value)`, `numpy.float64(value)`, `numpy.float128(value)`. For Decimal precisions: `decimal.localcontext(decimal.Context(prec=N))` block wrapping the four-form evaluation. The context is local; it does not leak.

For the cbrt fixture: only binary precision wrappers are implemented. An attempt to call a Decimal wrapper raises a `NotImplementedError` with an explicit message: `"cbrt fixture is out-of-scope-by-design at Decimal precisions (see Task 017c §4 point 4)"`. The aggregate report consumes this exception as out-of-scope-by-design metadata.

### 6.3 Unit-roundoff utility

`src/lloyd_v4/evals/precision/unit_roundoff.py`

Exposes `u_p(precision_spec)` returning the unit roundoff:

- For binary float: `numpy.finfo(dtype).eps / 2` (round-to-nearest convention).
- For Decimal at precision N: `Decimal(5) * Decimal(10) ** (-N)` (half-ulp at the least significant digit, round-half-even default).

The utility records which convention it used in its return.

### 6.4 Linear-fit and bootstrap CI utilities

`src/lloyd_v4/evals/precision/linear_fit.py`

Per fixture per path: fit `C_{p,k} = a_k + b_k · u_p` across the precision battery. Reports:

- `a_k`, `b_k` point estimates
- `a_k`, `b_k` deterministic bootstrap 95% CIs (`random.Random(seed=hash(fixture_name+path))`)
- `R²` of fit
- Per-precision residuals
- Sterbenz-region restricted fit (re-fit on Sterbenz-applicable cells only) for F2 specifically

### 6.5 Multi-precision campaign module

`src/lloyd_v4/evals/precision/multi_precision_campaign.py`

For each (fixture, precision) pair in scope, for each path in {F1, F2, F3, F4}, for each cell in the canonical 137-point grid: evaluate the four-form; compute `C_{p,k}` per the paper's definition; record.

Output: a long-format observation table with columns `(fixture, precision_label, u_p, path, cell_index, residual, C_p_k_summary, region)` where `region ∈ {regular, sterbenz, boundary}` per fixture-specific Sterbenz boundary.

### 6.6 Cross-precision aggregate report

`Build_Docs/Reports/task017c_multi_precision_theorem2/precision_aggregate.json`

Byte-stable across repeat runs. Per (fixture, path):

- Fit parameters (a_k, b_k, R²) with CIs, for regular region and full grid
- Sterbenz-region restricted fit results
- Per-precision residual distributions
- Sub-claim match/mismatch
- Out-of-scope-by-design markers for cbrt × Decimal cells

### 6.7 F5+ supplementary fits

`Build_Docs/Reports/task017c_multi_precision_theorem2/f5_plus_supplementary.json`

Same fit machinery applied to `P_compound_split` and `P_sign_c` paths across all four fixtures. Reported as supplementary, non-load-bearing for the headline. If their fits also satisfy the four sub-claims, that's additional substrate-universality evidence. If they don't, the divergence is recorded as a forward observation.

### 6.8 Headline classification record

`Build_Docs/Reports/task017c_multi_precision_theorem2/headline_classification.md`

One of `theorem2_validated` / `theorem2_partial` / `theorem2_refuted` with per-sub-claim justification. Grounded in §6.6 results only (F5+ supplementary is reported, not headline-determining).

### 6.9 Task summary

`Build_Docs/Reports/task017c_summary.md`

Standard structure (mirror 029c). Must include:

- Pre-registration commit hash and date.
- Platform report (`numpy.finfo(numpy.float128)`, whether float128 is meaningfully distinct from float64 on the host).
- Precision battery actually executed per fixture.
- Per-fixture per-path fit results table.
- Sterbenz-region restricted fit results for F2 across all four fixtures.
- Sub-claim match/mismatch table (load-bearing).
- F5+ supplementary results table (non-load-bearing).
- Headline classification with one-paragraph justification grounded in load-bearing sub-claims only.
- Byte-stability confirmation.
- Discipline gates explicit confirmation.
- Forward observations. No next-task drafts.

## 7. Required Tests

Approximately **35 new tests**. Target ~617 total against post-029c baseline.

### 7.1 Pre-task evidence

- Confirm Task 029c is on `origin/main` (commit `975a3fb` or descendant); halt if not.
- Confirm `transfer_function_exponent_family_v3.tex` is accessible and contains Theorem 2.
- Record HEAD hash and pre-existing test count.

### 7.2 Precision-binding tests (~7 tests)

- `numpy.float32(1.0).dtype == numpy.float32` (sanity).
- `numpy.float128` available; record `finfo` and report whether distinct from float64.
- `Decimal` context at prec=50/100/200 produces results with expected precision in a simple known computation.
- Precision-parameterised wrappers for Schwarzschild/SR/pure-algebraic return values at each requested binary and Decimal precision.
- Precision-parameterised wrappers for cbrt return values at each requested binary precision.
- cbrt wrapper at Decimal precision raises `NotImplementedError` with the exact out-of-scope-by-design message from §6.2.
- Decimal context does not leak: a `localcontext()` block at prec=50 inside a prec=28 outer context leaves the outer context unchanged on exit.

### 7.3 Unit-roundoff utility tests (~4 tests)

- `u_p(float32) ≈ 5.96e-8` to four sig figs.
- `u_p(float64) ≈ 1.11e-16` to four sig figs.
- `u_p(decimal_prec=50) == Decimal(5) * Decimal(10) ** -50`.
- The utility records which convention it used in its return.

### 7.4 Fit-utility tests (~5 tests)

- Hand-rolled or `numpy.linalg.lstsq` linear fit matches reference computation on a synthetic linear dataset to within machine precision.
- R² for a perfect linear dataset is 1.0 (within machine epsilon).
- Bootstrap 95% CI is deterministic across runs given a fixed seed.
- Bootstrap CI includes the true parameter on a synthetic dataset where the true parameter is known.
- Sterbenz-region restriction correctly subsets the grid by predicate per fixture.

### 7.5 Theorem-2 transcription tests (~2 tests)

- The `C_{p,k}` definition in `pre_registration.md` matches Theorem 2 as it appears in `transfer_function_exponent_family_v3.tex` (string-match check on the canonical definition line).
- The pre-registration includes the platform's float128 report and the per-fixture Sterbenz-boundary definitions.

### 7.6 Byte-stability tests (~3 tests)

- `precision_aggregate.json` byte-identical between two consecutive runs.
- `pre_registration.md` byte-identical at task close (no post-hoc edits).
- `headline_classification.md` byte-identical between two consecutive runs.

### 7.7 Discipline gate tests (~6 tests)

- F3 sentinel: F3 ≡ 0 (or below detection) at every cell, every precision, every fixture. If F3 fires non-trivially, halt loudly.
- No `layer_manifest.json` changes.
- No physics-interpretive language (grep test, mirrors existing pattern).
- No `scipy`, `sympy`, `mpmath` introduced (grep test).
- `typed_finite_difference` source byte-identical to start (file-hash check).
- No `math.cbrt`, `f ** (1.0/3.0)`, `f ** (1/3)`, `numpy.special` introduced.

### 7.8 Source-purity tests (~3 tests)

- No new hardcoded mathematical constants (no `math.pi`, `math.e`, etc.).
- No `numpy.random` (only `random.Random(seed)`).
- No global Decimal context mutation (only `decimal.localcontext()` blocks).

### 7.9 Methodology gate tests (~5 tests)

- Each precision in the battery produces a distinguishable residual distribution from each other precision (negative control on the multi-precision setup).
- Fit residuals at the largest u_p (float32) are not dominated by single outlier cells.
- F3 fit slope CI includes zero in all fixtures (calibration check).
- F1, F2, F4 slope CIs do not all collapse to identical values in any fixture (paths genuinely resolve).
- The Sterbenz-region restricted fit and full-grid fit produce statistically distinguishable b_k for F2 in fixtures where Sterbenz applies.

## 8. Required Commands

1. `git status` — clean.
2. `git log -1 --oneline` — record HEAD.
3. Confirm 029c commit `975a3fb` (or descendant) on `origin/main`. Halt if not.
4. `pytest -q tests/` — baseline.
5. Read Theorem 2 definition from `transfer_function_exponent_family_v3.tex`. Transcribe verbatim into `pre_registration.md`.
6. Record platform's `numpy.finfo(numpy.float128)` in pre-registration.
7. Create `pre_registration.md` per §6.1.
8. `git add Build_Docs/Reports/task017c_multi_precision_theorem2/pre_registration.md`
9. `git commit -m "Task 017c pre-registration: ..."` (see §6.1 for exact message)
10. Record the pre-registration commit hash.
11. Implement modules and tests.
12. `pytest -q tests/` — confirm all pass.
13. Run the campaign; write `precision_aggregate.json` and `f5_plus_supplementary.json`.
14. Run the campaign a second time, write to `/tmp/`, diff. Byte-identical.
15. Run the fits per fixture per path. Write `headline_classification.md`.
16. Write `task017c_summary.md`.
17. `pytest -q tests/` — final.
18. `git add -A && git commit -m "Task 017c: multi-precision Theorem 2 validation — <headline>" && git push origin main`
19. `git status` — clean.
20. `git log -2 --oneline` — both commits visible on `origin/main`.

## 9. Non-Goals (Loud and Explicit)

- **NOT** modifying `typed_finite_difference` or any other substrate primitive.
- **NOT** modifying `layer_manifest.json`.
- **NOT** adding new fixtures. The four chain-property fixtures are exactly the scope.
- **NOT** introducing a Decimal-context-aware cube root. The cbrt × Decimal cells are explicitly out-of-scope-by-design.
- **NOT** validating α-1 recovery at branch points. Separate task.
- **NOT** running operation-level Sterbenz annotation. That is Task 030.
- **NOT** drafting Task 030 (or any forward task) in the summary.
- **NOT** drafting a paper revision incorporating these results. Separate post-task action by William.
- **NOT** using `scipy`, `sympy`, `mpmath`, `numpy.special`, `scipy.optimize`, `scipy.stats`, `statsmodels`, or any clustering library.
- **NOT** using `math.cbrt`, `**(1/3)`, `numpy.random`, or hardcoded math-named constants.
- **NOT** using global `decimal.getcontext()` mutation. All context changes are `localcontext()` blocks.
- **NOT** silently using `numpy.float128` as if it were distinct from float64 on platforms where it isn't.
- **NOT** pre-deciding the headline.
- **NOT** including `P_distrib_sqrt_mul` in the fit campaign. Established sqrt-specific by 029b/029c; not a Theorem 2 universality test.

## 10. Completion Report

`Build_Docs/Reports/task017c_summary.md`, in this order:

1. **Scope.**
2. **Pre-registration commit hash and date.**
3. **Platform report.**
4. **Precision battery actually executed per fixture** (asymmetric — cbrt at binary only).
5. **Per-fixture per-path fit table:**

   | Fixture | Path | a_k (CI) | b_k (CI) | R² | a_k CI includes 0? |
   |---|---|---|---|---|---|
   | Schwarzschild | F1 | (fill) | (fill) | (fill) | (Y/N) |
   | ... (rows for every fixture × path combination) | | | | | |

6. **Sterbenz-region restricted F2 fit table:**

   | Fixture | F2 b_k (CI) regular region | F2 b_k (CI) Sterbenz region | Vanishing match? |
   |---|---|---|---|

7. **Sub-claim match/mismatch table (load-bearing):**

   | Sub-claim | Pre-registered threshold | Observed | Match? |
   |---|---|---|---|
   | Regular-region R² | R² ≥ 0.98 | (fill) | (Y/N) |
   | Intercept CI includes zero | All a_k CIs include 0 | (fill) | (Y/N) |
   | Slope structure | F1,F2,F4 b_k distinguishable; F3 b_k indistinguishable from 0 | (fill) | (Y/N) |
   | Sterbenz-region F2 b_k vanishing | F2 b_k CI in Sterbenz region includes 0 | (fill) | (Y/N) |

8. **F5+ supplementary fits table** (P_compound_split, P_sign_c) — same columns as table 5, marked supplementary.
9. **Headline classification** with justification grounded in §7 only.
10. **Tests** — total count, new tests added, pytest result.
11. **Byte-stability confirmation.**
12. **Discipline gates** explicit confirmation.
13. **Files changed.**
14. **Forward observations** — what did the multi-precision data reveal about (a) linear-in-u_p model adequacy across the precision range, (b) whether the Sterbenz mechanism explanation extends cleanly across precisions, (c) any structure observable in b_k that suggests further mechanism decomposition, (d) F5+ supplementary behaviour. **No next-task drafts.**

## 11. Acceptance Criteria

1. Pre-registration committed as its own commit before any campaign code ran.
2. All pre-existing tests pass.
3. All new tests pass (~35 new).
4. F3 sentinel held at every precision in every fixture.
5. `precision_aggregate.json` byte-stable.
6. `f5_plus_supplementary.json` byte-stable.
7. `pre_registration.md` byte-identical to committed file.
8. `layer_manifest.json` byte-identical to start.
9. `typed_finite_difference` source byte-identical to start.
10. No physics-interpretive language.
11. No forbidden imports or patterns.
12. Platform float128 report present in pre-registration and summary.
13. Headline classification recorded, grounded in load-bearing sub-claims only.
14. F5+ supplementary reported regardless of outcome.
15. Forward observations recorded without drafting next task.
16. Final commit pushed to `origin/main`. `git status` clean. Both commits on `origin/main` in order.

## 12. Discipline Notes

### Axiom 5 — Numerical representation is a path

This task is the empirical test of Axiom 5's claim. The whole point of Theorem 2 is that the *path* (precision) is separable from the *object* (geometric structure). If the empirical fit confirms linear-in-u_p separation, Axiom 5 has its strongest empirical support to date. If it doesn't, Axiom 5's claim narrows in scope.

### Axiom 10 — V3 reference-only

V3 has multi-precision execution machinery (different shape from V4). Reference-only stance applies: V4's multi-precision execution derives from V4's typed substrate, not adapted from V3's implementation. The smell to watch: "V3 did multi-precision this way, so V4 does multi-precision this way." Pull up. V4's multi-precision binding is the precision-parameterised fixture wrapper consuming the unchanged `typed_finite_difference` primitive. Nothing else.

### Axiom 11 — Epistemic stance only

`numpy.float32`, `numpy.float64`, `numpy.float128` admitted as type containers. `decimal.Decimal` admitted. `Decimal.sqrt()` admitted at fixture layer (already used). `numpy.finfo` admitted as type-introspection.

Forbidden: `math.cbrt`, `**(1.0/3.0)`, hand-rolled Newton cube root in the fixture module, hardcoded math-named constants. The cbrt × Decimal cell is the explicit boundary: not implemented, not approximated, not silently substituted.

### Axiom 12 — Self-derivation

Every concept used traces to existing parent-layer provisions. No new substrate concepts. If a concept appears to be required that does not exist in a parent layer, halt and report as forward observation; do not extend substrate ad hoc.

### F3 sentinel across precisions

F3 calibration silence must hold at every precision, every cell, every fixture. If F3 fires non-trivially at any precision, either the fixture-precision binding is wrong at that precision, or the calibration assumption fails at that precision. Halt loudly either way.

### Pre-registration is non-negotiable

R² ≥ 0.98 in regular region; bootstrap CI inclusion criterion for intercepts; Sterbenz-region vanishing prediction for F2 — all locked before the campaign runs. Post-hoc threshold-tuning is forbidden. If a sub-claim narrowly misses, it misses; the summary reports the miss honestly; the paper accommodates.

### Byte-stability across multi-precision

Decimal arithmetic is deterministic given fixed context. Numpy float arithmetic is IEEE-deterministic. Bootstrap CIs are deterministic given fixed seeds. All campaign outputs must byte-diff to zero across repeat runs.

### Platform reporting is part of the task

`numpy.float128` is platform-dependent. The platform report goes in the pre-registration. If float128 collapses to float64 on the host, the float128 row is dropped from the analysis with an explicit note. The paper revision incorporating these results must include the platform under which the campaign ran.

### Asymmetric precision coverage is a feature, not a bug

The cbrt fixture's restriction to binary precisions is a deliberate scope choice grounded in the Decimal cube-root question. The aggregate report represents this explicitly: cbrt × Decimal cells are marked `out_of_scope_by_design`, not `missing` or `error`. The paper documents the asymmetry. Honest scope is better than dishonest symmetry.

### Git discipline non-negotiable

Pre-registration commit lands on `origin/main` before campaign code runs. Main task commit lands before task is considered closed. `git status` clean. Summary references both commit hashes.

---

## Appendix A — Theorem 2 statement and the linear-in-u_p model

Codex reads the canonical Theorem 2 statement and the `C_{p,k}` definition from `transfer_function_exponent_family_v3.tex` and transcribes them verbatim into `pre_registration.md`. The transcription test in §7.5 enforces line-for-line match. This is to prevent paraphrase drift between what the paper claims and what the campaign tests.

The linear-in-u_p model `C_{p,k} = a_k + u_p · b_k` is interpreted as follows:

- `a_k` (intercept): the path-invariant geometric amplitude. For algebraically-zero constraints (F1, F2, F3, F4 — all evaluate to 0 in exact arithmetic), the geometric content is zero. Prediction: `a_k` is consistent with zero (CI includes zero).
- `b_k` (slope): the path-dependent arithmetic conditioning amplitude. Different paths route the same exact-arithmetic zero through different floating-point operations and accumulate different rounding-induced residuals. Prediction: `b_k` differs across paths in the regular region; F3's `b_k` is zero (calibration); F2's `b_k` is zero in the Sterbenz region (exact subtraction).

The test of Theorem 2 is whether this linear-in-u_p decomposition holds empirically across the precision battery for each path in each fixture.

## Appendix B — Sterbenz region as a substructure prediction

The Sterbenz mechanism (established by 029c at value-level across radical degrees) predicts that inside the Sterbenz-applicable region, F2's subtraction `R^n − 1` is *exact*. An exact subtraction has no rounding-induced residual, so its conditioning amplitude `b_k` should vanish — not just decrease, vanish.

This is the sharpest single empirical prediction the mechanism story makes, and 017c tests it directly. If F2's `b_k` in the Sterbenz region is statistically indistinguishable from zero across all four fixtures, the Sterbenz mechanism is empirically pinned at multi-precision level. If it's not, the mechanism story is partial.

Per-fixture Sterbenz-applicable regions (from 029c results):

| Fixture | Sterbenz-applicable region |
|---|---|
| Schwarzschild | r ≥ 4 |
| SR | β ≤ 1/√2 |
| Pure algebraic | x ≤ 1/2 |
| cbrt | x ≤ 1/2 |

## Appendix C — Scope-reduction on cbrt at Decimal precisions

`Decimal.sqrt()` exists in the Python standard library and is context-bound. `Decimal` has no native cube root. The three candidates for filling this gap each carry significant costs:

| Candidate | Cost |
|---|---|
| Newton iteration to context precision | Solver dynamics inside a fixture; iteration count and termination criterion become fixture parameters; the fixture is no longer "pure expression" |
| `value ** (Decimal(1)/Decimal(3))` | Routes through Decimal's internal ln/exp; not correctly-rounded for perfect cubes; introduces a *different* error structure than `numpy.cbrt`, which breaks the cross-precision comparability that the entire campaign depends on |
| Scope-reduction (adopted) | The cbrt fixture is evaluated at binary precisions only; the paper documents the asymmetry explicitly |

The scope-reduction is the honest answer. The paper can document this: "Cross-precision validation extends to all six precisions for the sqrt-based fixtures, and to binary precisions only for the cbrt-based fixture, due to the absence of an IEEE-correctly-rounded cube root operation in the Python Decimal module. The asymmetry does not affect the load-bearing Theorem 2 claim, which is validated across all six precisions for three fixtures."

This is one of those engineering choices where the right answer is to be explicit about the limitation rather than paper over it.
