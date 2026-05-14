# Codex Task 033 — Schwarzschild-Shape Cube-Root Transformed-Operand Fixture (F2 Lattice Grain H2 Discrimination at n=3)

## 0. Context

Task 032 confirmed H2 (operand-transformation law: F2 grain = 0.5 for transformed-operand fixtures, 0.25 for identity-operand fixtures) in the identity-operand case at n=4, refuting H1 (algebraic-degree law: F2 grain = $2^{1-n}$). The five-fixture table now reads:

| Fixture | n | Operand | F2 grain |
|---|---:|---|---:|
| Schwarzschild | 2 | transformed (r → 1−2/r) | 0.5 |
| SR | 2 | transformed (β → 1−β²) | 0.5 |
| Pure-algebraic | 2 | identity (x → 1−x) | 0.25 |
| Cube-root | 3 | identity (x → 1−x) | 0.25 |
| Quartic-root | 4 | identity (x → 1−x) | 0.25 |

The pattern is unambiguous in three of four cells: identity-operand at n=2, n=3, n=4 all give 0.25, and transformed-operand at n=2 gives 0.5 across two independent fixtures. The (n≥3, transformed) cell is unfilled.

H2 predicts 0.5 for any transformed-operand fixture regardless of n. If observed, H2 holds across the full tested range. If the (n≥3, transformed) cell gives 0.25, the operand-transformation effect is n=2-specific and H2 needs refinement. If it gives some other value (e.g., 0.125, 0.0625), a more complex mechanism is in play.

**The depth question this task settles:** is the operand-transformation effect on F2 lattice grain invariant across radical degree, or specific to n=2?

The fixture uses Schwarzschild's operand transformation $r \to 1 - 2/r$ paired with a cube-root radical $R = \mathrm{cbrt}(f)$. This combines an already-characterized transformed-operand structure (Schwarzschild at n=2 gives 0.5) with an already-characterized cube-root radical (cbrt identity-operand at n=3 gives 0.25). Both component pieces are V4-admitted single-rounding operations; the composition introduces no new arithmetic structure.

**Why Schwarzschild operand specifically over SR.** Schwarzschild's r → 1−2/r involves division, structurally more complex than SR's β → 1−β² squaring. Both produced 0.5 at n=2, suggesting the operand-transformation effect is not specific to a particular operand structure. Schwarzschild is the sharper first probe because its operand map is more arithmetically complex; if the effect is real, it should show through the more complex transformation.

**Why n=3 specifically over n=4.** Native single-rounding `numpy.cbrt` versus composed-sqrt $\sqrt{\sqrt{\cdot}}$. Removes the two-rounding-events caveat from 032's interpretation. A clean n=3 result is structurally cleaner than a clean n=4 result through the composed form.

A parallel (n=4, transformed) fixture is the natural follow-up if this task's result supports H2.

---

## 1. Repository / Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4`

**Baseline HEAD:** post-032 on `origin/main` (commit at or after Task 032 completion).

**Test baseline:** 723 passing (post-032).

**Test count target:** previous baseline + ~25 new tests. Target ~748 against the 723 baseline.

**Sequencing dependency:** Task 032 must be on `origin/main`. The Schwarzschild fixture and cbrt fixture modules (`src/lloyd_v4/evals/schwarzschild_four_form.py`, `cbrt_four_form.py`) are imported by this task. If 032 is not landed, **halt and report**.

## 2. Task Goal

Build a Schwarzschild-shape cube-root fixture that pairs the Schwarzschild operand transformation $r \to 1 - 2/r$ with a cube-root radical $R = \mathrm{cbrt}(f)$. Run it through the four-form battery + lattice campaign + Sterbenz boundary check, and classify the observed F2 lattice grain against the three pre-registered outcomes.

The fixture combines two already-characterized substrate elements:
- The Schwarzschild operand transformation from `schwarzschild_four_form.py` (operand grid $r \in [2.005, 10.0]$, transformation $f = 1 - 2/r$).
- The cube-root radical from `cbrt_four_form.py` ($R = \mathrm{np.cbrt}(f)$, single-rounding native operation).

Neither component is novel; their composition is what this task tests.

## 3. Source Labelling

- **V4-surface (load-bearing):** Layer 1 primitives, existing Schwarzschild fixture infrastructure (operand grid, transformation map), existing cbrt fixture infrastructure (`np.cbrt` invocation, four-form battery pattern), lattice campaign machinery, polarity grid stability machinery, Sterbenz boundary analysis, byte-stability discipline, axioms 1-12.
- **Theorem-derived:** the algebraic identity $R^3 = 1 - 2/r$ on the Schwarzschild operand sweep; the Sterbenz-applicable region for the first subtraction $R^3 - 1$.
- **Proposal evidence:** the H2-discrimination question itself, the three-outcome pre-registration structure.
- **V3 reference (concept only):** none. V4-substrate-native end to end.

## 4. Design Principles

1. **No new substrate primitives.** All measurement reuses existing four-form, lattice, polarity, and Sterbenz boundary machinery applied to a new fixture composition.
2. **No multi-precision battery this task.** Float32 and float64 only (matching cbrt's primary battery and Task 032's scope). Multi-precision is a forward task conditional on outcome.
3. **No V3-shape import.** Grep test enforces.
4. **Schwarzschild operand grid is the existing canonical grid.** Re-use, do not reconstruct.
5. **Cube-root via `numpy.cbrt` is the radical.** Single-rounding native operation, no composed-radical caveat.
6. **F2 max_integer_residual at float64 is the load-bearing measurement.** Other observations (polarity, Sterbenz boundary at the appropriately-shifted location) are reported but do not determine the headline.
7. **Pre-registration locks the three possible outcomes and the discrimination rule, not the predicted outcome.**
8. **No physics-interpretive language.** The Schwarzschild operand map is used as a *structural* transformed-operand pattern, not as a physical referent. The fixture is named for structural lineage, not physics.

## 5. Primitive-Sufficiency Gate

| Concept used | Source | Status |
|---|---|---|
| Schwarzschild operand grid $r \in [2.005, 10.0]$ on 137 points | Existing `schwarzschild_four_form.r_grid` (or equivalent) | Re-used |
| Schwarzschild operand transformation $f = 1 - 2/r$ | Existing `schwarzschild_four_form.f_direct` | Re-used |
| Schwarzschild alt routing $f_{\mathrm{alt}}$ | Existing | Re-used |
| Cube-root via `numpy.cbrt` at float32 and float64 | Existing `cbrt_four_form` pattern | Re-used |
| Four-form battery (F1, F2, F3, F4) | Same shape as Schwarzschild and cbrt fixtures, adapted | New module; mirrors existing pattern |
| Lattice campaign at float64 | Existing machinery | Re-used; new fixture wiring |
| Polarity grid stability at float64 | Existing machinery | Re-used |
| Sterbenz boundary check | Existing logic, with boundary at the appropriate r-value | Re-used |

**Sterbenz boundary location for this fixture.** The first subtraction in the F2 chain is $R^3 - 1$, which is Sterbenz-exact when $R^3 \ge 1/2$. Substituting $R^3 = 1 - 2/r$: Sterbenz-exact when $1 - 2/r \ge 1/2$, i.e., $r \ge 4$. Same boundary as the existing Schwarzschild fixture at n=2 (since the operand transformation is the same), confirming that the boundary location is operand-determined, not radical-determined.

**Axiom 11 disposition.** `numpy.cbrt` and the basic arithmetic of $f = 1 - 2/r$ are admitted. No named mathematical content imports. No fractional-power patterns.

**Axiom 12 disposition.** Every observation traces to Layer 1 primitives via existing campaign measurement provenance. No new substrate concept is minted.

## 6. The Four-Form Battery for Schwarzschild-cbrt

Parallel to the existing Schwarzschild four-form and cbrt four-form, with the cube-root radical applied to the Schwarzschild operand:

- $R(r) := \mathrm{cbrt}(1 - 2/r)$
- $F_1(r) := R^3 - f_{\mathrm{direct}}(r)$ where $f_{\mathrm{direct}}(r) = 1 - 2/r$
- $F_2(r) := R^3 - 1 + 2/r$
- $F_3(r) := R - \mathrm{cbrt}(f_{\mathrm{direct}}(r))$ (calibration zero; same path twice)
- $F_4(r) := R - \mathrm{cbrt}(f_{\mathrm{alt}}(r))$ where $f_{\mathrm{alt}}(r)$ is the Schwarzschild alternative routing of $1 - 2/r$

$R^3$ is computed as `root * root * root` (three multiplications, matching cbrt's existing pattern).

The float32 fixture casts inputs and intermediate values to `numpy.float32`. The float64 fixture uses Python floats and `numpy.cbrt` at float64.

## 7. Required Deliverables

### 7.1 Pre-registration document

`Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/pre_registration.md`

Committed in a dedicated commit before any measurement code runs.

**Section A — Fixture construction (locked)**

- Operand grid: $r \in [2.005, 10.0]$, 137 points (re-uses existing Schwarzschild grid).
- Operand transformation: $f_{\mathrm{direct}}(r) = 1 - 2/r$ (re-uses existing).
- Radical: $R(r) = \mathrm{cbrt}(1 - 2/r)$ via `numpy.cbrt` (single rounding event).
- Four-form definitions per Section 6.
- Float32 fixture casts inputs and intermediates to `numpy.float32`.

**Section B — Hypotheses and pre-registered outcomes (locked)**

| Hypothesis | Predicted F2 grain | Source |
|---|---:|---|
| H2 (transformed → 0.5, independent of n) | 0.5 | Three existing transformed-operand cases at n=2 all give 0.5 |
| H2-refined (transformed effect specific to n=2) | 0.25 | If observed, the operand-transformation effect on grain is n=2-specific |
| Indeterminate | other value | Neither hypothesis predicts |

Headline classification:

- `transformed_operand_law_supported_at_n3` if observed F2 `max_integer_residual` at float64 equals 0.5 exactly.
- `transformed_operand_law_refuted_at_n3` if observed F2 `max_integer_residual` at float64 equals 0.25 exactly.
- `lattice_grain_indeterminate_at_n3` if observed F2 `max_integer_residual` at float64 is any other value.

Strict equality applies (lattice grain is a typed dyadic rational from float64 ulp structure).

**Section C — Supplementary observations (reported but not load-bearing)**

- F1, F3, F4 lattice classifications (predicted: F3 lattice_empty, F1 and F4 lattice_integer).
- Polarity grid stability for the $(F_1, F_2)$ pair at float64 (predicted: `grid_stable_polarity_coupling` per cross-fixture invariance).
- Sterbenz boundary directional bias at $r = 4.0$ (predicted: above-density higher, matching existing Schwarzschild at n=2; the boundary is operand-determined, so it should sit at the same r-value as the n=2 Schwarzschild fixture).
- Value-level comparison: does the Sterbenz boundary location depend on radical degree, or only on the operand transformation? This is a secondary question the fixture addresses.

Pre-registration commit message:

```
Task 033 pre-registration: Schwarzschild-cbrt transformed-operand n=3 fixture

H2 predicts F2 grain = 0.5 at (n=3, transformed). H2-refined predicts
0.25 if the operand-transformation effect is n=2-specific. Both
hypotheses pre-registered; outcome observed via existing lattice
campaign machinery on a Schwarzschild-operand cube-root fixture.
```

### 7.2 Fixture module

`src/lloyd_v4/evals/schwarzschild_cbrt_four_form.py`

Defines the four forms at float32 and float64. Structure mirrors `cbrt_four_form.py` and `schwarzschild_four_form.py`. Imports the operand grid from the existing Schwarzschild fixture; imports the `np.cbrt` pattern from the existing cbrt fixture.

Key functions: `R_of_r`, `F1_of_r`, `F2_of_r`, `F3_of_r`, `F4_of_r`, `four_form_float32`, `four_form_float64`, `schwarzschild_cbrt_four_form_battery`.

### 7.3 Lattice campaign module

`src/lloyd_v4/evals/schwarzschild_cbrt_lattice_campaign.py`

Mirrors `cbrt_lattice_campaign.py` structure. Computes lattice classification, level histogram, level integer residual max/median, level jump distribution, and regional distinct level counts for each form at float32 and float64.

### 7.4 Polarity grid stability module

`src/lloyd_v4/evals/schwarzschild_cbrt_polarity_grid_stability.py`

Mirrors existing polarity grid stability machinery. Four-grid set (reference, coarse_perturbation, fine_perturbation, independent_uniform) at float32 and float64.

### 7.5 Sterbenz boundary analysis

Re-uses the existing Sterbenz boundary analysis utility. Applies to the Schwarzschild-cbrt fixture at float64 with boundary at $r = 4.0$. Reports below/above counts and densities. Records confirmation that the boundary location is operand-determined (same r-value as Schwarzschild n=2) and that the radical degree change to n=3 does not shift it.

### 7.6 Campaign orchestrator

`src/lloyd_v4/evals/schwarzschild_cbrt_campaign.py`

Top-level orchestrator that runs the four-form battery, lattice campaign, polarity grid stability, and Sterbenz boundary check, then writes the aggregated output JSON.

### 7.7 Output JSONs

`Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/campaign_results.json`

Byte-stable. Per-form per-precision lattice classifications, polarity tables, Sterbenz boundary observation, hypothesis-discrimination summary.

`Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/schwarzschild_cbrt_four_form_battery.json`

Byte-stable. Four-form values at every grid point at float32 and float64.

`Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/schwarzschild_cbrt_lattice_campaign_output.json`

Byte-stable. Detailed lattice classification with histograms, level distributions, regional counts.

### 7.8 Headline classification record

`Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/headline_classification.md`

One of the three headlines per Section 7.1 with table grounding:

| Hypothesis | Predicted | Observed | Match? |
|---|---:|---:|---|
| H2: transformed → 0.5 | 0.5 | [observed value] | Y/N |
| H2-refined: transformed-effect n=2-specific | 0.25 | [observed value] | Y/N |

### 7.9 Task summary

`Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3_summary.md`

Standard structure. Must include:

- Pre-registration commit hash.
- Lattice classification table (F1, F2, F3, F4 at float32 and float64).
- F2 lattice grain six-fixture table:

| Fixture | n | Operand | F2 grain |
|---|---:|---|---:|
| Schwarzschild | 2 | transformed | 0.5 |
| SR | 2 | transformed | 0.5 |
| Pure-algebraic | 2 | identity | 0.25 |
| Cube-root | 3 | identity | 0.25 |
| Quartic-root | 4 | identity | 0.25 |
| Schwarzschild-cbrt (this task) | 3 | transformed | [observed] |

- Sterbenz boundary observation table at $r = 4.0$, with comparison to Schwarzschild n=2 boundary.
- Polarity grid stability summary.
- Hypothesis discrimination table.
- Headline classification with justification.
- Tests, byte-stability, discipline gates.
- Forward observations — three required: (a) whether H2 is supported, refined, or refuted by this data point, (b) whether the Sterbenz boundary is operand-determined (sitting at the same r-value as n=2 Schwarzschild) or radical-determined, (c) what fixtures would further discriminate (e.g., parallel Schwarzschild-quartic at n=4, SR-cbrt at n=3 for operand-structure invariance). **No next-task drafts.**

## 8. Required Tests

Approximately **25 new tests** in `tests/test_task033_schwarzschild_cbrt_transformed_n3.py`.

### 8.1 Pre-task evidence (~3 tests)

- Confirm Task 032 commit on `origin/main`.
- Confirm Schwarzschild and cbrt fixture modules importable.
- Record HEAD hash and pre-existing test count.

### 8.2 Fixture correctness tests (~6 tests)

- $R = \mathrm{cbrt}(1 - 2/r)$ produces finite non-NaN values at every grid point at float32 and float64.
- F1, F2, F4 produce finite non-NaN values at every grid point at float32 and float64.
- F3 produces exactly 0.0 at every grid point at float64 (calibration zero invariant).
- $R^3 - (1 - 2/r) = F_1(r)$ holds at every grid point within float64 tolerance.
- The operand grid is byte-identical to the existing Schwarzschild grid.
- The four-form values match between orchestrator output and direct module invocation.

### 8.3 Lattice classification tests (~6 tests)

- F1 classification at float64 is `lattice_integer` with `level_integer_residual_max = 0.0`.
- F3 classification at float64 is `lattice_empty`.
- F4 classification at float64 is `lattice_integer` with `level_integer_residual_max = 0.0`.
- F2 classification at float64 is `non_integer_lattice` (some grain value is observed).
- F2 `level_integer_residual_max` at float64 is one of `{0.0, 0.125, 0.25, 0.5}` (declared admissible set).
- F2 `level_integer_residual_max` at float32 is reported and noted in the summary.

### 8.4 Polarity / Sterbenz tests (~4 tests)

- Polarity grid stability produces aggregate classifications for $F_1\_F_2$, $F_1\_F_4$, $F_2\_F_4$ pairs at float32 and float64 over four grids.
- Sterbenz boundary check at $r = 4.0$ produces below/above counts and densities at float64.
- F3 nonzero count is 0 across all polarity grids (cross-fixture invariance).
- Polarity coupling for $F_1\_F_2$ pair at float64 reference grid is `grid_stable_polarity_coupling` OR documented as a cross-fixture invariance violation.

### 8.5 Hypothesis discrimination test (~3 tests)

- The headline classification matches the pre-registered logic: observed F2 grain → expected headline string. Parameterized over the three outcomes.
- The observed F2 grain at float64 maps to one of the three pre-registered outcomes.
- The Sterbenz boundary location at $r = 4.0$ in this fixture is byte-identical to the boundary location used for the existing Schwarzschild fixture at n=2.

### 8.6 Byte-stability tests (~2 tests)

- `campaign_results.json` byte-identical between two consecutive runs.
- `pre_registration.md` byte-identical to committed file at task close.

### 8.7 Discipline gate tests (~2 tests)

- No imports from `src/lloyd_v4/refinery/` in any new file. Grep test.
- No `math.fma`, `math.pow`, `cmath`, `scipy`, `sympy`, `mpmath`, `statsmodels`, `numpy.special`, `numpy.random` introduced. No fractional-power pattern.

## 9. Required Commands

1. `git status` — clean.
2. `git log -1 --oneline` — record HEAD.
3. Confirm Task 032 commit on `origin/main`.
4. `pytest -q tests/` — baseline.
5. Create `pre_registration.md` per §7.1.
6. `git add Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/pre_registration.md`
7. `git commit -m "Task 033 pre-registration: Schwarzschild-cbrt transformed-operand n=3 fixture..."` (full message per §7.1)
8. Record pre-registration commit hash.
9. Implement modules and tests.
10. `pytest -q tests/` — confirm all pass.
11. Run campaign; write all output JSONs and `headline_classification.md`.
12. Run campaign a second time; diff against repository copies; byte-identical.
13. Write `task033_schwarzschild_cbrt_transformed_n3_summary.md`.
14. `pytest -q tests/` — final.
15. `git add -A && git commit -m "Task 033: Schwarzschild-cbrt n=3 transformed-operand — <headline>" && git push origin main`.
16. `git status` — clean.
17. `git log -2 --oneline` — both commits visible on `origin/main`.

## 10. Non-Goals

- **NOT** modifying any substrate primitive.
- **NOT** modifying `layer_manifest.json`.
- **NOT** building a Layer 2 module.
- **NOT** importing from `src/lloyd_v4/refinery/`.
- **NOT** building a parallel SR-cbrt fixture (operand-structure invariance is a forward task).
- **NOT** building a parallel Schwarzschild-quartic fixture (n=4 transformed is the natural follow-up).
- **NOT** running multi-precision battery (deferred).
- **NOT** drafting follow-up tasks in the summary.
- **NOT** promoting any new concept to substrate.
- **NOT** using `math.pow`, `numpy.power` with fractional exponent, or any fractional-power pattern.
- **NOT** treating this as a physics fixture. The Schwarzschild operand map is used here as a *structural* transformed-operand pattern, not for any physical content.

## 11. Acceptance Criteria

1. Pre-registration committed as its own commit before any measurement code ran.
2. All pre-existing tests pass.
3. All new tests pass (~25 new).
4. Fixture produces finite non-NaN values at every grid point at float32 and float64.
5. F3 produces calibration zero at every grid point at float64.
6. F2 `level_integer_residual_max` at float64 is one of `{0.0, 0.125, 0.25, 0.5}`; if observed value is outside this set, headline forced to `lattice_grain_indeterminate_at_n3` and observed value documented.
7. Sterbenz boundary check produces a populated below/above table at $r = 4.0$.
8. Polarity grid stability for $F_1\_F_2$ pair at float64 is `grid_stable_polarity_coupling` OR documented as a cross-fixture invariance violation.
9. All output JSONs byte-stable.
10. `pre_registration.md` byte-identical to committed file.
11. `layer_manifest.json` byte-identical to start.
12. No imports from `src/lloyd_v4/refinery/`.
13. No forbidden imports or fractional-power patterns.
14. Headline classification recorded.
15. Forward observations recorded without drafting next task.
16. Final commit pushed to `origin/main`. `git status` clean. Both commits on `origin/main` in order.

## 12. Discipline Notes

### Axiom 10 — V3 reference-only

V4-substrate-native end to end. The Schwarzschild operand map and cbrt radical are both existing V4 substrate elements; their composition is what's new.

### Axiom 11 — Epistemic stance only

`numpy.cbrt` and basic arithmetic of $1 - 2/r$ are admitted. No named mathematical content, no fractional-power patterns. The fixture is named for structural lineage from the Schwarzschild operand pattern; "Schwarzschild" here is a structural label for the operand-transformation type, not a physics reference.

### Axiom 12 — Self-derivation

Every observation traces to Layer 1 primitives via existing campaign provenance. No new substrate concept is minted.

### Pre-registration is non-negotiable

The three outcomes are locked. The headline classification logic is locked. The fixture construction is locked. Post-hoc adjustment is forbidden. Observation that diverges from both H2 outcomes is honestly reported.

### What this result discriminates and what it does not

A clean 0.5 result confirms H2 across n=2 and n=3 transformed cases, supporting an n-independent operand-transformation rule. The (n=4, transformed) cell remains unfilled but the operand-transformation pattern is now characterized at two radical degrees.

A clean 0.25 result refutes H2's n-independence: the operand-transformation effect would be n=2-specific. This is a substantive substrate finding that would reshape the lattice-grain map.

An indeterminate result (any other grain value) indicates a more complex mechanism — possibly an interaction effect between operand structure and radical degree that neither hypothesis captures.

### What this does NOT settle

- The operand-structure invariance question. Schwarzschild's operand map involves division; SR's involves squaring. Both produce 0.5 at n=2. Whether *any* transformed-operand fixture produces 0.5 at higher n, or only Schwarzschild-style transformations do, is a parallel question. A future SR-cbrt fixture would address it.
- The native-rounding versus composed-rounding question for higher radical degrees. This fixture uses native cbrt (single rounding event); a parallel Schwarzschild-quartic fixture using composed sqrt-of-sqrt is the natural next step if the n=4 transformed cell is needed.

### Byte-stability across measurement

All measurement runs are deterministic. No `numpy.random`. Repeat runs produce byte-identical output.

### Git discipline non-negotiable

Pre-registration commit lands on `origin/main` before measurement code runs. Main task commit lands before the task is considered closed.

---

## Appendix A — The grid completion after this task

After Task 033, the fixture grid will be:

| | Transformed operand | Identity operand |
|---|---|---|
| n=2 | Schwarzschild 0.5, SR 0.5 | Pure-algebraic 0.25 |
| n=3 | **Schwarzschild-cbrt [observed]** | Cube-root 0.25 |
| n=4 | (unfilled) | Quartic-root 0.25 |

If Schwarzschild-cbrt gives 0.5, the transformed-operand row is consistent across n=2 and n=3. The (n=4, transformed) cell is then the natural next probe.

If Schwarzschild-cbrt gives 0.25, the transformed-operand effect is n=2-specific, the grid pattern is more complex than H2 captures, and the cleanest next probe is probably SR-cbrt at n=3 to test whether the result is Schwarzschild-operand-specific or operand-structure-general.

## Appendix B — The Sterbenz boundary as a secondary observable

The Sterbenz-applicable region for the F2 chain's first subtraction $R^n - 1$ depends on the operand transformation, not on $n$:

- Schwarzschild operand: $R^n \ge 1/2 \iff 1 - 2/r \ge 1/2 \iff r \ge 4$.

The boundary at $r = 4$ should hold for both the existing Schwarzschild (n=2) fixture and this Schwarzschild-cbrt (n=3) fixture. If the boundary shifts or fails to appear at $r = 4$ in the n=3 fixture, the operand-determined-boundary claim of Section 8 of the transfer-function paper would need revisiting.

The pre-registered prediction: the boundary is at $r = 4$ exactly, with above-density higher (matching Schwarzschild n=2). The secondary observation gives a second data point on the radical-degree invariance of the Sterbenz boundary location.
