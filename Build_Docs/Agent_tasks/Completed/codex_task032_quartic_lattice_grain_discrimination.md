# Codex Task 032 — Quartic-Root Identity-Operand Fixture Battery (F2 Lattice Grain Discrimination)

## 0. Context

This task probes a sharp open hypothesis about the F2 lattice grain across radical degree. Current substrate observations across four fixtures show:

| Fixture | Radical degree n | Operand | F2 grain |
|---|---:|---|---:|
| Schwarzschild | 2 | transformed (r → 1−2/r) | 0.5 |
| SR | 2 | transformed (β → 1−β²) | 0.5 |
| Pure-algebraic | 2 | identity (x → 1−x) | 0.25 |
| Cube-root | 3 | identity (x → 1−x) | 0.25 |

Two competing hypotheses fit subsets of the data:

**H1 (algebraic-degree law):** F2 grain = $2^{1-n}$ where $n$ is the algebraic skeleton degree of $R^n = 1-x$. Predicts: n=2 → 0.5, n=3 → 0.25, n=4 → 0.125. Fits Schwarzschild, SR, and cube-root, but predicts 0.5 for pure-algebraic where 0.25 is observed.

**H2 (operand-transformation law):** F2 grain is 0.5 for transformed-operand fixtures, 0.25 for identity-operand fixtures, independent of n. Fits all four current data points but makes no prediction about scaling with n.

The disconfirming data point for H1 is pure-algebraic — the substrate's cleanest control. The hypotheses are confounded in the current battery because n and operand-transformation status co-vary.

**The depth question this task settles:** does the F2 lattice grain depend on the algebraic skeleton degree $n$, or only on operand-transformation status? Adding a quartic-root identity-operand fixture (n=4, identity operand) discriminates:
- If F2 grain = 0.125 → H1 supported (with pure-algebraic flagged as an anomaly worth understanding)
- If F2 grain = 0.25 → H2 supported (H1 refuted)
- If F2 grain is some other value → both hypotheses refuted, new mechanism

**Significance if H1 holds:** branch radical degree becomes inferable directly from ULP-lattice quantisation. The substrate produces a degree-discriminating diagnostic from float64 residual structure alone, without operand-specific knowledge.

**Task renumbering note.** Previous Task 032 candidate allocations (operation-level Sterbenz annotation; diagnostic-policy variant of Sterbenz audit) are rebanked to later slots. The quartic-root probe is a higher-priority depth move because it discriminates a sharp empirical question on the existing fixture-battery framework with minimal new substrate work.

---

## 1. Repository / Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4`

**Baseline HEAD:** post-031 on `origin/main` (commit `0650a44` or descendant).

**Test baseline:** 686 passing (post-031).

**Test count target:** previous baseline + ~25 new tests. Target ~711 against the 686 baseline.

**Sequencing dependency:** Task 031 (`0650a44` or descendant) must be on `origin/main`. The pure-algebraic and cbrt fixture modules (`src/lloyd_v4/evals/pure_algebraic_four_form.py`, `cbrt_four_form.py`) are imported by this task. If 031 is not landed, **halt and report**.

## 2. Task Goal

Build a quartic-root (n=4) identity-operand fixture parallel in structure to `pure_algebraic_four_form` and `cbrt_four_form`, run it through the four-form battery + lattice campaign + Sterbenz boundary check, and classify the observed F2 lattice grain against the three pre-registered outcomes (H1, H2, indeterminate).

The fixture computes the quartic root via composed square roots:
$$R(x) = \sqrt{\sqrt{1-x}}$$

This composition is the Axiom-11-admissible way to compute a quartic root in V4 substrate (each `np.sqrt` is an admitted operation, fractional-power patterns are not). The composition produces two rounding events rather than the single-rounding event that a native quartic-root primitive would produce. The spec acknowledges this explicitly; the interpretation of the result must account for it.

## 3. Source Labelling

- **V4-surface (load-bearing):** Layer 1 primitives, existing four-form battery infrastructure (`pure_algebraic_four_form`, `cbrt_four_form`), lattice campaign infrastructure (`pure_algebraic_lattice_campaign`, `cbrt_lattice_campaign`), polarity grid stability infrastructure, byte-stability discipline, axioms 1-12.
- **Theorem-derived:** the algebraic identity $R^4 = 1-x$ on the identity-operand sweep; the Sterbenz-applicable region $x \le 1/2$ for the first subtraction $R^4 - 1$.
- **Proposal evidence:** the H1 vs H2 hypotheses themselves (subject to MVP validation), the quartic-via-composed-sqrts implementation, the three-outcome pre-registration structure.
- **V3 reference (concept only):** none. This task is V4-substrate-native end to end.

## 4. Design Principles

1. **No new substrate primitives.** All measurement reuses existing four-form, lattice, and polarity machinery applied to a new fixture.
2. **No multi-precision battery this task.** Float32 and float64 only (matching cbrt's primary battery). Multi-precision extension to quartic is a forward task conditional on this task's outcome.
3. **No V3-shape import.** Grep test enforces.
4. **Identity-operand only.** A transformed-operand quartic fixture would be a parallel future task. The current discrimination is best done with identity-operand to isolate the radical-degree effect.
5. **Quartic via composed sqrts is the admitted form.** Pre-registration declares this explicitly and notes the two-rounding-events consequence.
6. **F2 max_integer_residual at float64 is the load-bearing measurement.** Other observations (polarity, Sterbenz boundary) are reported but do not determine the headline.
7. **Pre-registration locks the three possible outcomes and the discrimination rule, not the predicted outcome.**
8. **No physics-interpretive language.**

## 5. Primitive-Sufficiency Gate

| Concept used | Source | Status |
|---|---|---|
| Quartic root via $\sqrt{\sqrt{1-x}}$ at float32, float64 | New fixture module using `np.sqrt` composition | Admitted (numpy.sqrt is admitted as cbrt is) |
| Canonical 137-point grid on $x \in [0.01, 0.99]$ | Existing `pure_algebraic_four_form.x_grid` | Re-used |
| Four-form battery (F1, F2, F3, F4) | Same shape as `cbrt_four_form` adapted to n=4 | New module; mirrors existing pattern |
| Lattice campaign at float64 | Existing `pure_algebraic_lattice_campaign` / `cbrt_lattice_campaign` machinery | Re-used; new fixture wiring |
| Polarity grid stability at float64 | Existing machinery | Re-used |
| Sterbenz boundary check at $x = 1/2$ | Same logic as 029c | Re-used |

**Axiom 11 disposition.** `numpy.sqrt` is admitted under the same standard as `numpy.cbrt` (basic numpy operations, not named mathematical content from `numpy.special` / `math` / `scipy.special`). Quartic root via $\sqrt{\sqrt{x}}$ composition is two basic-operation invocations, no fractional-power pattern, no named-radical import.

**Axiom 12 disposition.** Every observation traces to Layer 1 primitives via existing campaign measurement provenance. No new substrate concept is minted.

## 6. The Four-Form Battery for n=4

The fixture defines forms parallel to the cbrt four-form battery with the radical $R(x) = \sqrt{\sqrt{1-x}}$ replacing the cube root:

- $F_1(x) := R^4 - f_{\mathrm{direct}}(x)$ where $f_{\mathrm{direct}}(x) = 1 - x$
- $F_2(x) := R^4 - 1 + x$
- $F_3(x) := R - \sqrt{\sqrt{f_{\mathrm{direct}}(x)}}$ (calibration zero; same path twice)
- $F_4(x) := R - \sqrt{\sqrt{f_{\mathrm{alt}}(x)}}$ where $f_{\mathrm{alt}}(x) = (1 - x/2) - x/2$

$R^4$ is computed as `root * root * root * root` (four multiplications, parallel to cbrt's `root * root * root`).

The float32 fixture casts inputs and intermediate values to `numpy.float32`, computes the radical and forms at float32, then casts to float for output. The float64 fixture uses Python floats and `numpy.sqrt` at float64.

## 7. Required Deliverables

### 7.1 Pre-registration document

`Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/pre_registration.md`

Committed in a dedicated commit before any measurement code runs. Structured in three sections:

**Section A — Fixture construction (locked before measurement)**

- Operand: $x \in [0.01, 0.99]$, canonical 137-point grid (re-uses `pure_algebraic_four_form.x_grid`).
- Identity operand transformation: $f_{\mathrm{direct}}(x) = 1 - x$.
- Quartic root: $R(x) = \sqrt{\sqrt{1-x}}$ via two `numpy.sqrt` invocations.
- Four-form definitions per Section 6 above.
- Float32 fixture casts inputs and intermediate values to `numpy.float32`.

**Section B — Hypotheses and pre-registered outcomes (locked before measurement)**

| Hypothesis | Predicted F2 grain at n=4 | Source |
|---|---:|---|
| H1 (algebraic-degree law: grain = $2^{1-n}$) | 0.125 | Two-of-three fit on physical fixtures + cbrt |
| H2 (operand-transformation law) | 0.25 | Four-of-four fit on existing data |
| Indeterminate | other value | Neither hypothesis predicts |

The headline classification logic:

- `lattice_grain_h1_quartic` if observed F2 `max_integer_residual` at float64 equals 0.125 exactly.
- `lattice_grain_h2_operand` if observed F2 `max_integer_residual` at float64 equals 0.25 exactly.
- `lattice_grain_indeterminate` if observed F2 `max_integer_residual` at float64 is any other value (including 0.5, 0.0, or fractional values not matching either hypothesis).

Strict equality is appropriate because lattice grain values in V4 are typed dyadic rationals derived from float64 ulp structure; CI-style fuzziness does not apply to the discretized lattice classification.

**Section C — Supplementary observations (reported but not load-bearing)**

- F1, F3, F4 lattice classifications (F3 should be `lattice_empty`; F1 and F4 should be `lattice_integer`).
- Polarity grid stability for the $(F_1, F_2)$ pair at float64 (predicted: `grid_stable_polarity_coupling` to match the cross-fixture invariance).
- Sterbenz boundary directional bias at $x = 1/2$ (predicted: below-density higher, matching pure-algebraic and cube-root).
- The two-rounding-events consequence of the $\sqrt{\sqrt{\cdot}}$ composition: noted as a caveat. A native single-rounding quartic-root primitive would be a different fixture and could give a different result. The current spec deliberately uses the admitted form.

Pre-registration commit message:

```
Task 032 pre-registration: quartic-root identity-operand fixture for F2 lattice grain discrimination

H1 (grain = 2^(1-n)) predicts F2 grain = 0.125 at n=4.
H2 (operand-transformation law) predicts F2 grain = 0.25 at n=4.
Both hypotheses pre-registered; outcome observed via existing lattice
campaign machinery on a quartic-via-sqrt-of-sqrt identity-operand fixture.
```

### 7.2 Fixture module

`src/lloyd_v4/evals/pure_algebraic_quartic_four_form.py`

Defines the four forms at float32 and float64. Structure mirrors `cbrt_four_form.py` exactly: `R_of_x`, `F1_of_x`, `F2_of_x`, `F3_of_x`, `F4_of_x`, `four_form_float32`, `four_form_float64`, `quartic_four_form_battery`.

The fixture imports `x_grid` from `pure_algebraic_four_form` (same canonical grid).

### 7.3 Lattice campaign module

`src/lloyd_v4/evals/pure_algebraic_quartic_lattice_campaign.py`

Mirrors `pure_algebraic_lattice_campaign.py` structure. Computes lattice classification, level histogram, level integer residual max/median, level jump distribution, and regional distinct level counts for each form at float32 and float64.

### 7.4 Polarity grid stability module

`src/lloyd_v4/evals/pure_algebraic_quartic_polarity_grid_stability.py`

Mirrors the existing polarity grid stability machinery. Runs the four-grid set (reference, coarse_perturbation, fine_perturbation, independent_uniform) at float32 and float64, reports F1_F2, F1_F4, F2_F4 pair classifications.

### 7.5 Sterbenz boundary analysis

Re-uses the existing Sterbenz boundary analysis utility (whatever Task 029c used internally to produce the boundary report). Applies to the quartic fixture at float64, reports below/above counts and densities at the predicted boundary $x = 0.5$.

### 7.6 Campaign orchestrator

`src/lloyd_v4/evals/pure_algebraic_quartic_campaign.py`

Top-level orchestrator that runs the four-form battery, lattice campaign, polarity grid stability, and Sterbenz boundary check, then writes the aggregated output JSON.

### 7.7 Output JSONs

`Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/campaign_results.json`

Byte-stable. Contains per-form per-precision lattice classifications, polarity tables, Sterbenz boundary observation, and the hypothesis-discrimination summary.

`Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/quartic_four_form_battery.json`

Byte-stable. Four-form values at every grid point at float32 and float64.

`Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/quartic_lattice_campaign_output.json`

Byte-stable. Detailed lattice classification with histograms, level distributions, regional counts.

### 7.8 Headline classification record

`Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/headline_classification.md`

One of the three headlines per Section 7.1 with table grounding:

| Hypothesis | Predicted | Observed | Match? |
|---|---:|---:|---|
| H1: grain = $2^{1-n}$ | 0.125 | [observed value] | Y/N |
| H2: operand-transformation law | 0.25 | [observed value] | Y/N |

### 7.9 Task summary

`Build_Docs/Reports/task032_quartic_lattice_grain_discrimination_summary.md`

Standard structure (mirror 029c / 030 / 031). Must include:

- Pre-registration commit hash.
- Four-form values per fixture point (or reference to the byte-stable JSON).
- Lattice classification table (F1, F2, F3, F4 at float32 and float64).
- F2 lattice grain comparison across the existing fixtures and the new quartic fixture:

| Fixture | n | Operand | F2 grain |
|---|---:|---|---:|
| Schwarzschild | 2 | transformed | 0.5 |
| SR | 2 | transformed | 0.5 |
| Pure-algebraic | 2 | identity | 0.25 |
| Cube-root | 3 | identity | 0.25 |
| Quartic-root (this task) | 4 | identity | [observed] |

- Headline classification with justification.
- Sterbenz boundary observation table.
- Polarity grid stability summary.
- Tests, byte-stability, discipline gates.
- Forward observations including the two-rounding-events caveat and what follow-up tasks (e.g., quintic, native-rounding quartic primitive if Axiom 11 is amended) the outcome would suggest. **No next-task drafts.**

## 8. Required Tests

Approximately **25 new tests** in `tests/test_task032_quartic_lattice_grain_discrimination.py`.

### 8.1 Pre-task evidence (~3 tests)

- Confirm Task 031 commit `0650a44` (or descendant) on `origin/main`.
- Confirm pure-algebraic and cbrt fixture modules importable.
- Record HEAD hash and pre-existing test count.

### 8.2 Fixture correctness tests (~6 tests)

- Quartic root via $\sqrt{\sqrt{1-x}}$ produces finite non-NaN values at every grid point at float32 and float64.
- F1, F2, F4 produce finite non-NaN values at every grid point at float32 and float64.
- F3 produces exactly 0.0 at every grid point at float64 (calibration zero invariant).
- $R^4$ (computed as `root * root * root * root`) and $(R^2)^2$ produce bit-identical residuals at float64 (sanity: parenthesisation of repeated multiplication doesn't matter for 4 identical operands).
- The algebraic identity $R^4 - (1-x) = F_1(x)$ holds at every grid point within float64 tolerance.
- The four-form values match between the orchestrator output and direct module invocation (no orchestrator-induced drift).

### 8.3 Lattice classification tests (~6 tests)

- F1 classification at float64 is `lattice_integer` with `level_integer_residual_max = 0.0`.
- F3 classification at float64 is `lattice_empty`.
- F4 classification at float64 is `lattice_integer` with `level_integer_residual_max = 0.0`.
- F2 classification at float64 is `non_integer_lattice` (some grain value is observed).
- F2 `level_integer_residual_max` at float64 is a typed dyadic rational from `{0.0, 0.125, 0.25, 0.5}` (declared admissible set; anything outside this triggers `lattice_grain_indeterminate`).
- F2 `level_integer_residual_max` at float32 is also reported and noted in the summary (float32 may show different grain due to wider rounding).

### 8.4 Polarity / Sterbenz tests (~4 tests)

- Polarity grid stability machine produces aggregate classifications for $F_1\_F_2$, $F_1\_F_4$, $F_2\_F_4$ pairs at float32 and float64 over four grids.
- Sterbenz boundary check at $x = 0.5$ produces below count, above count, below density, above density at float64.
- F3 nonzero count is 0 across all polarity grids (cross-fixture invariance).
- Polarity coupling for $F_1\_F_2$ pair at float64 reference grid: same-sign fraction = 1.0 OR aggregate classification is `grid_stable_polarity_coupling` (cross-fixture invariance).

### 8.5 Hypothesis discrimination test (~2 tests)

- The headline classification matches the pre-registered logic: observed F2 grain → expected headline string. Test this branch by branch (parameterized over the three possible outcomes).
- The observed F2 grain at float64 maps to one of the three pre-registered outcomes (no off-list value sneaks through).

### 8.6 Byte-stability tests (~2 tests)

- `campaign_results.json` byte-identical between two consecutive runs.
- `pre_registration.md` byte-identical to committed file at task close.

### 8.7 Discipline gate tests (~2 tests)

- No imports from `src/lloyd_v4/refinery/` (V3-shape) in any new file. Grep test.
- No `math.fma`, `math.pow`, `math.sqrt`, `cmath`, `scipy`, `sympy`, `mpmath`, `statsmodels`, `numpy.special`, `numpy.random` introduced. No fractional-power pattern (e.g., `** 0.25`, `** 0.5`, `numpy.power(..., 0.25)`).

## 9. Required Commands

1. `git status` — clean.
2. `git log -1 --oneline` — record HEAD.
3. Confirm Task 031 commit on `origin/main`.
4. `pytest -q tests/` — baseline.
5. Create `pre_registration.md` per §7.1.
6. `git add Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/pre_registration.md`
7. `git commit -m "Task 032 pre-registration: quartic-root identity-operand fixture for F2 lattice grain discrimination..."` (full message per §7.1)
8. Record pre-registration commit hash.
9. Implement modules and tests.
10. `pytest -q tests/` — confirm all pass.
11. Run campaign; write all output JSONs and `headline_classification.md`.
12. Run campaign a second time; diff against repository copies; byte-identical.
13. Write `task032_quartic_lattice_grain_discrimination_summary.md`.
14. `pytest -q tests/` — final.
15. `git add -A && git commit -m "Task 032: quartic-root lattice grain discrimination — <headline>" && git push origin main`.
16. `git status` — clean.
17. `git log -2 --oneline` — both commits visible on `origin/main`.

## 10. Non-Goals (Loud and Explicit)

- **NOT** modifying any substrate primitive.
- **NOT** modifying `layer_manifest.json`.
- **NOT** building a Layer 2 module.
- **NOT** importing from `src/lloyd_v4/refinery/`.
- **NOT** building a transformed-operand quartic fixture (deferred).
- **NOT** running multi-precision battery for quartic (deferred to a conditional follow-up).
- **NOT** building a native-rounding quartic-root primitive (would require Axiom 11 amendment or substrate work outside this task's scope).
- **NOT** running the campaign at quintic, sextic, or higher radical degrees (conditional follow-up only).
- **NOT** drafting follow-up tasks in the summary.
- **NOT** promoting any new concept to substrate.
- **NOT** using `math.pow`, `numpy.power` with fractional exponent, or any other fractional-power pattern (Axiom 11).

## 11. Completion Report

`Build_Docs/Reports/task032_quartic_lattice_grain_discrimination_summary.md`, in this order:

1. **Scope.**
2. **Pre-registration commit hash and date.**
3. **Quartic fixture construction** — radical via composed sqrts, four-form definitions, grid.
4. **Lattice classification table** — F1, F2, F3, F4 at float32 and float64, with `lattice_class`, `n_nonzero`, `level_integer_residual_max`.
5. **F2 lattice grain cross-fixture comparison** — five-row table including the new quartic fixture.
6. **Sterbenz boundary observation** — below/above counts and densities at $x = 0.5$.
7. **Polarity grid stability summary** — pair classifications for $F_1\_F_2$, $F_1\_F_4$, $F_2\_F_4$ at float32 and float64.
8. **Hypothesis discrimination table** — H1 prediction, H2 prediction, observed value, headline.
9. **Headline classification** with one-paragraph justification grounded in §6's lattice classification.
10. **Two-rounding-events caveat** — explicit note that the quartic-via-sqrt-of-sqrt composition produces two rounding events, and that a native single-rounding quartic primitive would be a different fixture; the outcome of this task is for the admitted form.
11. **Tests** — total count, new tests added, pytest result.
12. **Byte-stability confirmation.**
13. **Discipline gates** explicit confirmation, including V3-shape no-import grep result.
14. **Files changed.**
15. **Forward observations** — four required categories: (a) which hypothesis was supported and how strongly, (b) what the cross-fixture pattern now looks like with five data points, (c) whether the two-rounding-events caveat materially changes interpretation, (d) what fixtures or substrate work would be needed to discriminate further (e.g., higher radical degrees, transformed-operand quartic, native-rounding quartic primitive). **No next-task drafts.**

## 12. Acceptance Criteria

1. Pre-registration committed as its own commit before any measurement code ran.
2. All pre-existing tests pass.
3. All new tests pass (~25 new).
4. Quartic fixture produces finite non-NaN values at every grid point at float32 and float64.
5. F3 produces calibration zero at every grid point at float64.
6. F2 `level_integer_residual_max` at float64 is one of `{0.0, 0.125, 0.25, 0.5}`; if observed value is outside this set, headline is forced to `lattice_grain_indeterminate` and the observed value is documented.
7. Sterbenz boundary check produces a populated below/above table at $x = 0.5$.
8. Polarity grid stability for $F_1\_F_2$ pair at float64 is `grid_stable_polarity_coupling` OR is documented in the summary as the first cross-fixture invariance violation.
9. All output JSONs byte-stable.
10. `pre_registration.md` byte-identical to committed file.
11. `layer_manifest.json` byte-identical to start.
12. No imports from `src/lloyd_v4/refinery/`.
13. No forbidden imports or patterns (especially no fractional-power pattern).
14. Headline classification recorded.
15. Two-rounding-events caveat explicitly stated in the summary.
16. Forward observations recorded without drafting next task.
17. Final commit pushed to `origin/main`. `git status` clean. Both commits on `origin/main` in order.

## 13. Discipline Notes

### Axiom 10 — V3 reference-only

This task is V4-substrate-native end to end. No V3 reference is consulted. The four-form battery infrastructure, lattice campaign, and polarity grid stability machinery are all existing V4 substrate modules.

### Axiom 11 — Epistemic stance only

`numpy.sqrt` is admitted at the same level as `numpy.cbrt` — a basic numpy operation, not named mathematical content. The quartic root is computed as $\sqrt{\sqrt{\cdot}}$ via two `numpy.sqrt` invocations. No fractional-power pattern, no `math.pow`, no named mathematical content imports.

The two-rounding-events consequence of this composition is acknowledged in the pre-registration as a structural property of the admitted form, not a defect. If the substrate observation shows the grain depends on rounding-event count rather than on algebraic skeleton degree, this is itself a substantive finding that the spec must accommodate (via the `lattice_grain_indeterminate` outcome category).

### Axiom 12 — Self-derivation

Every observation traces to Layer 1 primitives via existing campaign measurement provenance. No new substrate concept is minted.

### Pre-registration is non-negotiable

The three outcomes are locked. The headline classification logic is locked. The fixture construction (quartic via composed sqrts) is locked. Post-hoc adjustment of any of these is forbidden. If observation diverges from both H1 and H2 (i.e., grain is some value other than 0.125 or 0.25), the headline is `lattice_grain_indeterminate` and the observed value is documented honestly.

### What the result discriminates and what it does not

A clean H1 result (F2 grain = 0.125) discriminates the algebraic-degree hypothesis against the operand-transformation hypothesis on this single new data point, but leaves pure-algebraic as an unexplained anomaly under H1. The summary should flag this honestly: H1 supported with one outstanding anomaly.

A clean H2 result (F2 grain = 0.25) refutes H1 outright; the F2 grain depends on operand-transformation status alone, not on algebraic skeleton degree. The "branch degree inferable from ULP-lattice quantisation" diagnostic capability is not supported by the substrate.

An indeterminate result (any other grain value) refutes both hypotheses and indicates a more complex mechanism. The summary should document the observed value precisely and propose what alternative hypotheses fit the now-five-fixture pattern.

### Byte-stability across measurement

All measurement runs are deterministic. No `numpy.random`. Repeat runs produce byte-identical output. Diff verifies.

### Git discipline non-negotiable

Pre-registration commit lands on `origin/main` before measurement code runs. Main task commit lands before the task is considered closed.

---

## Appendix A — Why pure-algebraic is the anomaly under H1, not cube-root

Under H1 ($\text{grain} = 2^{1-n}$):
- Schwarzschild n=2 → 0.5 ✓
- SR n=2 → 0.5 ✓
- Cube-root n=3 → 0.25 ✓
- Pure-algebraic n=2 → predicted 0.5, observed 0.25 ✗

Three of four data points match H1 exactly. The anomaly is pure-algebraic, which is the substrate's cleanest control. Two possible readings:

**Reading 1:** Pure-algebraic's 0.25 grain is a real exception to the $2^{1-n}$ pattern, and the operand-transformation status (identity versus transformed) has a secondary effect that depresses grain in some identity-operand cases. Under this reading, H1 is approximately right but has an operand-transformation correction term. The quartic-root identity-operand fixture should produce 0.125 (since it follows the cube-root's identity-operand behaviour rather than pure-algebraic's), but might produce 0.0625 or another value if the operand-transformation correction is multiplicative.

**Reading 2:** The $2^{1-n}$ pattern is an artefact of co-variation between n and operand-transformation in the three physical/cbrt fixtures, and H2 (operand-transformation rule, grain independent of n) is the correct hypothesis. The quartic-root identity-operand fixture should produce 0.25.

Reading 1 and Reading 2 make different predictions for the quartic. Task 032 discriminates.

## Appendix B — Why the two-rounding-events caveat matters

A native single-rounding quartic primitive (e.g., `math.pow(x, 0.25)`, if Axiom 11 admitted it) and the composed $\sqrt{\sqrt{x}}$ form are algebraically equivalent but float-arithmetically different. The composed form rounds twice (once per `sqrt` call); the native form rounds once. This structural difference could affect the residual lattice independently of the algebraic skeleton degree.

If H1 holds for native single-rounding quartic (giving 0.125) but the composed form gives a different value (e.g., 0.25), the substrate distinguishes between "algebraic skeleton degree" and "rounding-event count" — both real properties of the implementation, but only the former is the framework's intended observable.

Resolving this would require either:
- Admitting fractional-power patterns under Axiom 11 (a substantive substrate decision)
- Building a Newton-iteration quartic-root primitive (substantial work; trades the rounding-event-count question for a Newton-convergence-residual question)
- Accepting that the quartic-via-composed-sqrts is the substrate-admissible answer and interpreting all results under that admission

The current task takes the third option. The two-rounding-events caveat is recorded; the result is interpreted under the admission; if the discrimination is clean (H1 or H2), the framework's diagnostic capability is established for the admitted form. If the result is indeterminate, the rounding-event-count hypothesis becomes a serious alternative that the next task should address.
