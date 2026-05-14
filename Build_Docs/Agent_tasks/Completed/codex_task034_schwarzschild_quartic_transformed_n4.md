# Codex Task 034 — Schwarzschild-Shape Quartic Transformed-Operand Fixture (Compound Hypothesis Test at n=4)

## 0. Context

Task 033 produced a substrate-native discovery: the Schwarzschild-shape cube-root fixture (transformed operand, n=3) gives F2 lattice grain = `0.25`, not `0.5`. Under the pre-registered binary mapping this refuted H2 (n-independent transformed-operand law) and supported H2-refined (transformed effect n=2-specific).

But the observed pattern across the six current fixtures is more structured than either H2 framing captured. The transformed-operand sequence reads:

| Fixture | n | F2 grain |
|---|---:|---:|
| Schwarzschild | 2 | 0.5 |
| SR | 2 | 0.5 |
| Schwarzschild-cbrt (Task 033) | 3 | 0.25 |

That sequence is $2^{1-n}$ — the same algebraic-degree law (H1) that Task 032 refuted in the identity-operand row. H1 didn't die at Task 032; it re-emerges constrained to the transformed-operand row.

The compound hypothesis (H3) that fits all six existing data points:

| Operand | n=2 | n=3 | n=4 |
|---|---:|---:|---:|
| Identity | 0.25 | 0.25 | 0.25 |
| Transformed | 0.5 | 0.25 | **predicted 0.125** |

- **Identity operand:** F2 grain = `0.25` invariant across n (Tasks 028, 029c, 032 evidence).
- **Transformed operand:** F2 grain = $2^{1-n}$ (Schwarzschild and SR at n=2 give 0.5; Schwarzschild-cbrt at n=3 gives 0.25; predicted 0.125 at n=4).

H3 makes a sharp prediction for the unfilled (n=4, transformed) cell. If observed, the compound hypothesis is empirically supported across the full 2×3 grid. If not, the substrate has more structure than H3 captures.

**The depth question this task settles:** does the transformed-operand F2 grain continue to follow $2^{1-n}$ at n=4, converge to the identity-operand floor at 0.25, or display some third behaviour?

**Two-rounding-events caveat is now load-bearing.** The quartic radical via composed `sqrt(sqrt(·))` introduces two rounding events (Task 032 §13). If the observed grain is `0.0625` rather than `0.125`, the rounding-event-count hypothesis (rather than algebraic-skeleton-degree hypothesis) is at play. The pre-registration accommodates this as a distinct outcome.

---

## 1. Repository / Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4`

**Baseline HEAD:** post-033 on `origin/main` (commit at or after Task 033 completion).

**Test baseline:** post-033 (~752 passing, accounting for Task 033's added tests).

**Test count target:** previous baseline + ~25 new tests.

**Sequencing dependency:** Task 033 must be on `origin/main`. The Schwarzschild operand grid (from `schwarzschild_four_form.py` or `schwarzschild_cbrt_four_form.py`) and the quartic-via-composed-sqrt pattern (from `pure_algebraic_quartic_four_form.py`) are imported by this task. If 033 is not landed, **halt and report**.

## 2. Task Goal

Build a Schwarzschild-shape quartic fixture that pairs the Schwarzschild operand transformation $r \to 1 - 2/r$ with a quartic radical $R = \sqrt{\sqrt{f}}$. Run it through the four-form battery + lattice campaign + Sterbenz boundary check, and classify the observed F2 lattice grain against three pre-registered outcomes.

The fixture combines two already-characterised substrate elements:
- The Schwarzschild operand transformation from `schwarzschild_four_form.py` / `schwarzschild_cbrt_four_form.py` (operand grid $r \in [2.005, 10.0]$, transformation $f = 1 - 2/r$, alternate routing $f_{\mathrm{alt}} = (r-2)/r$).
- The composed-sqrt quartic radical from `pure_algebraic_quartic_four_form.py` ($R = \mathrm{np.sqrt}(\mathrm{np.sqrt}(f))$, two rounding events).

Neither component is novel. Their composition is what this task tests.

## 3. Source Labelling

- **V4-surface (load-bearing):** Layer 1 primitives, existing Schwarzschild fixture infrastructure (operand grid, transformation map, alternate routing), existing pure-algebraic quartic fixture infrastructure (composed-sqrt pattern, four-form battery shape), lattice campaign machinery, polarity grid stability machinery, Sterbenz boundary analysis, byte-stability discipline, axioms 1-12.
- **Theorem-derived:** the algebraic identity $R^4 = 1 - 2/r$ on the Schwarzschild operand sweep; the Sterbenz-applicable region $r \ge 4$ for the first subtraction $R^4 - 1$ (operand-determined, same as n=2 and n=3 cases).
- **Proposal evidence:** the compound hypothesis H3 itself (subject to MVP validation), the rounding-event-count alternative hypothesis as a distinct outcome category.
- **V3 reference (concept only):** none. V4-substrate-native end to end.

## 4. Design Principles

1. **No new substrate primitives.** All measurement reuses existing four-form, lattice, polarity, and Sterbenz boundary machinery applied to a new fixture composition.
2. **No multi-precision battery this task.** Float32 and float64 only.
3. **No V3-shape import.** Grep test enforces.
4. **Schwarzschild operand grid is the existing canonical grid.** Re-use, do not reconstruct.
5. **Quartic via $\sqrt{\sqrt{\cdot}}$ composition is the admitted radical form.** Pre-registration acknowledges the two-rounding-events consequence and admits a `0.0625` outcome as the rounding-event-count discriminator.
6. **F2 max_integer_residual at float64 is the load-bearing measurement.**
7. **Pre-registration locks the three possible outcomes and the discrimination rule, not the predicted outcome.**
8. **No physics-interpretive language.** "Schwarzschild" labels the operand-transformation structure, not a physics referent.

## 5. Primitive-Sufficiency Gate

| Concept used | Source | Status |
|---|---|---|
| Schwarzschild operand grid $r \in [2.005, 10.0]$, 137 points | Existing `schwarzschild_four_form` / `schwarzschild_cbrt_four_form` | Re-used |
| Schwarzschild direct operand $f = 1 - 2/r$ | Existing | Re-used |
| Schwarzschild alt routing $f_{\mathrm{alt}} = (r-2)/r$ | Existing | Re-used |
| Quartic radical via $\sqrt{\sqrt{f}}$ at float32, float64 | Existing `pure_algebraic_quartic_four_form` pattern | Re-used |
| Four-form battery (F1, F2, F3, F4) | Mirrors existing Schwarzschild-cbrt and pure-algebraic-quartic patterns | New module |
| Lattice campaign at float64 | Existing machinery | Re-used; new fixture wiring |
| Polarity grid stability at float64 | Existing machinery | Re-used |
| Sterbenz boundary check at $r = 4.0$ | Existing logic, operand-determined boundary | Re-used |

**Sterbenz boundary location.** The first subtraction in the F2 chain is $R^4 - 1$, Sterbenz-exact when $R^4 \ge 1/2$. Substituting $R^4 = 1 - 2/r$: Sterbenz-exact when $r \ge 4$. Same as Schwarzschild n=2 and Schwarzschild-cbrt n=3 cases. This is the third data point on the operand-determined-boundary observation.

**Axiom 11 disposition.** `numpy.sqrt` is admitted under the same standard as `numpy.cbrt`. The composed $\sqrt{\sqrt{\cdot}}$ form is two basic-operation invocations, no fractional-power pattern, no named-radical import. The two-rounding-events structural property is acknowledged explicitly in the pre-registration as a distinct discriminator (via the `0.0625` outcome).

**Axiom 12 disposition.** Every observation traces to Layer 1 primitives via existing campaign provenance. No new substrate concept is minted.

## 6. The Four-Form Battery for Schwarzschild-Quartic

Parallel to Schwarzschild-cbrt (Task 033) and pure-algebraic-quartic (Task 032):

- $R(r) := \sqrt{\sqrt{1 - 2/r}}$
- $F_1(r) := R^4 - f_{\mathrm{direct}}(r)$ where $f_{\mathrm{direct}}(r) = 1 - 2/r$
- $F_2(r) := R^4 - 1 + 2/r$
- $F_3(r) := R - \sqrt{\sqrt{f_{\mathrm{direct}}(r)}}$ (calibration zero; same path twice)
- $F_4(r) := R - \sqrt{\sqrt{f_{\mathrm{alt}}(r)}}$ where $f_{\mathrm{alt}}(r) = (r - 2)/r$

$R^4$ is computed as `(root * root) * (root * root)` (parallel to pure-algebraic-quartic's grouping).

The float32 fixture casts inputs and intermediate values to `numpy.float32`. The float64 fixture uses Python floats and `numpy.sqrt` at float64.

## 7. Required Deliverables

### 7.1 Pre-registration document

`Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/pre_registration.md`

**Section A — Fixture construction (locked)**

- Operand grid: $r \in [2.005, 10.0]$, 137 points (existing Schwarzschild grid).
- Direct operand: $f_{\mathrm{direct}}(r) = 1 - 2/r$.
- Alt operand: $f_{\mathrm{alt}}(r) = (r-2)/r$.
- Radical: $R(r) = \sqrt{\sqrt{1 - 2/r}}$ via two `numpy.sqrt` invocations.
- Four-form definitions per Section 6.

**Section B — Hypotheses and pre-registered outcomes (locked)**

| Hypothesis | Predicted F2 grain | Source |
|---|---:|---|
| H3 (compound: transformed → $2^{1-n}$, identity → 0.25) | 0.125 | Fits all six existing data points; algebraic-skeleton-degree law for transformed row |
| H3-converges (transformed decays toward identity floor of 0.25) | 0.25 | Alternative: transformed-operand effect floors at 0.25 by n=4 |
| H_rounding (grain depends on rounding-event count) | 0.0625 | The two-rounding-events caveat: composed-sqrt may produce $2^{-(2 \cdot \text{rounding events})}$ rather than $2^{1-n}$ |
| Indeterminate | other value | None of the above |

Headline classification:

- `compound_law_h3_supported_at_n4` if observed F2 `max_integer_residual` at float64 equals `0.125` exactly.
- `transformed_decay_converges_to_identity_floor` if observed equals `0.25` exactly.
- `rounding_event_count_dominates` if observed equals `0.0625` exactly.
- `lattice_grain_indeterminate_at_n4_transformed` for any other value.

Strict equality (lattice grain is a typed dyadic rational from float64 ulp structure).

**Section C — Supplementary observations (reported but not load-bearing)**

- F1, F3, F4 lattice classifications (predicted: F3 lattice_empty, F1 and F4 lattice_integer).
- Polarity grid stability for the $(F_1, F_2)$ pair at float64 (predicted: `grid_stable_polarity_coupling`).
- Sterbenz boundary directional bias at $r = 4.0$ (predicted: above-density higher, matching Schwarzschild n=2 and Schwarzschild-cbrt n=3 — the boundary is operand-determined and should sit at the same r-value).
- Comparison against Task 032's pure-algebraic-quartic at n=4 identity (which gave 0.25): does the operand-transformation flip the grain, or does it stay at 0.25?

Pre-registration commit message:

```
Task 034 pre-registration: Schwarzschild-quartic transformed-operand n=4 fixture

H3 (compound: transformed → 2^(1-n)) predicts F2 grain = 0.125 at n=4.
H3-converges predicts 0.25 if transformed decay floors at identity baseline.
H_rounding predicts 0.0625 if rounding-event count dominates over algebraic
skeleton degree (two-rounding caveat from composed sqrt-of-sqrt). All three
hypotheses pre-registered with strict-equality classification.
```

### 7.2 Fixture module

`src/lloyd_v4/evals/schwarzschild_quartic_four_form.py`

Defines the four forms at float32 and float64. Structure mirrors `schwarzschild_cbrt_four_form.py` (Task 033) and `pure_algebraic_quartic_four_form.py` (Task 032). Imports the operand grid from existing Schwarzschild infrastructure; imports the composed-sqrt pattern from existing pure-algebraic-quartic.

Key functions: `R_of_r`, `F1_of_r`, `F2_of_r`, `F3_of_r`, `F4_of_r`, `four_form_float32`, `four_form_float64`, `schwarzschild_quartic_four_form_battery`.

### 7.3 Lattice campaign module

`src/lloyd_v4/evals/schwarzschild_quartic_lattice_campaign.py`

Mirrors existing lattice campaign structure. Computes lattice classification, level histogram, level integer residual max/median, level jump distribution, regional distinct level counts at float32 and float64.

### 7.4 Polarity grid stability module

`src/lloyd_v4/evals/schwarzschild_quartic_polarity_grid_stability.py`

Mirrors existing polarity grid stability machinery. Four-grid set at float32 and float64.

### 7.5 Sterbenz boundary analysis

Re-uses existing utility, applied to Schwarzschild-quartic at float64 with boundary at $r = 4.0$. Records the third data point on operand-determined-boundary invariance.

### 7.6 Campaign orchestrator

`src/lloyd_v4/evals/schwarzschild_quartic_campaign.py`

Top-level orchestrator.

### 7.7 Output JSONs

- `Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/campaign_results.json`
- `Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/schwarzschild_quartic_four_form_battery.json`
- `Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/schwarzschild_quartic_lattice_campaign_output.json`

All byte-stable.

### 7.8 Headline classification record

`Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/headline_classification.md`

One of the four headlines per Section 7.1 with table grounding:

| Hypothesis | Predicted | Observed | Match? |
|---|---:|---:|---|
| H3: compound law | 0.125 | [observed] | Y/N |
| H3-converges: transformed floors at identity baseline | 0.25 | [observed] | Y/N |
| H_rounding: rounding-event count dominates | 0.0625 | [observed] | Y/N |

### 7.9 Task summary

`Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4_summary.md`

Standard structure. Must include:

- Pre-registration commit hash.
- Lattice classification table (F1, F2, F3, F4 at float32 and float64).
- F2 lattice grain seven-fixture table:

| Fixture | n | Operand | F2 grain |
|---|---:|---|---:|
| Schwarzschild | 2 | transformed | 0.5 |
| SR | 2 | transformed | 0.5 |
| Pure-algebraic | 2 | identity | 0.25 |
| Cube-root | 3 | identity | 0.25 |
| Quartic-root | 4 | identity | 0.25 |
| Schwarzschild-cbrt | 3 | transformed | 0.25 |
| Schwarzschild-quartic (this task) | 4 | transformed | [observed] |

- The fully-populated 2×3 grid (identity vs transformed) × (n=2, n=3, n=4) after this task.
- Sterbenz boundary observation at $r = 4.0$, with comparison to Schwarzschild n=2 and Schwarzschild-cbrt n=3 boundaries.
- Polarity grid stability summary.
- Hypothesis discrimination table.
- Headline classification with one-paragraph justification.
- Tests, byte-stability, discipline gates.
- Forward observations — three required: (a) which hypothesis was supported and how the grid pattern reads, (b) what the rounding-event-count outcome (if observed) would imply for the framework's claim that lattice grain reflects algebraic skeleton degree, (c) what fixture or substrate work would discriminate further if the result is `0.25` or indeterminate (e.g., SR-cbrt for operand-structure invariance, native-rounding quartic primitive if Axiom 11 is amended). **No next-task drafts.**

## 8. Required Tests

Approximately **25 new tests** in `tests/test_task034_schwarzschild_quartic_transformed_n4.py`.

### 8.1 Pre-task evidence (~3 tests)

- Confirm Task 033 commit on `origin/main`.
- Confirm Schwarzschild and pure-algebraic-quartic fixture modules importable.
- Record HEAD hash and pre-existing test count.

### 8.2 Fixture correctness tests (~6 tests)

- $R = \sqrt{\sqrt{1 - 2/r}}$ produces finite non-NaN values at every grid point at float32 and float64.
- F1, F2, F4 produce finite non-NaN values at every grid point at float32 and float64.
- F3 produces exactly 0.0 at every grid point at float64 (calibration zero invariant).
- $(R \cdot R) \cdot (R \cdot R)$ and $((R \cdot R) \cdot R) \cdot R$ produce bit-identical residuals at float64 (sanity: parenthesisation invariance for four identical operands).
- The operand grid is byte-identical to the existing Schwarzschild grid.
- The four-form values match between orchestrator output and direct module invocation.

### 8.3 Lattice classification tests (~6 tests)

- F1 classification at float64 is `lattice_integer` with `level_integer_residual_max = 0.0`.
- F3 classification at float64 is `lattice_empty`.
- F4 classification at float64 is `lattice_integer` with `level_integer_residual_max = 0.0`.
- F2 classification at float64 is `non_integer_lattice`.
- F2 `level_integer_residual_max` at float64 is one of `{0.0, 0.0625, 0.125, 0.25, 0.5}` (declared admissible set; expanded from prior tasks to include `0.0625` for the rounding-event-count outcome).
- F2 `level_integer_residual_max` at float32 is reported.

### 8.4 Polarity / Sterbenz tests (~4 tests)

- Polarity grid stability produces aggregate classifications for $F_1\_F_2$, $F_1\_F_4$, $F_2\_F_4$ pairs at float32 and float64 over four grids.
- Sterbenz boundary check at $r = 4.0$ produces below/above counts and densities at float64.
- F3 nonzero count is 0 across all polarity grids.
- Polarity coupling for $F_1\_F_2$ pair at float64 reference grid is `grid_stable_polarity_coupling` OR documented as a cross-fixture invariance violation.

### 8.5 Hypothesis discrimination test (~3 tests)

- The headline classification matches the pre-registered logic over all four outcomes (parameterised).
- The observed F2 grain at float64 maps to one of the four pre-registered outcomes.
- The Sterbenz boundary location at $r = 4.0$ in this fixture matches the boundary location in Schwarzschild n=2 and Schwarzschild-cbrt n=3.

### 8.6 Byte-stability tests (~2 tests)

- `campaign_results.json` byte-identical between two consecutive runs.
- `pre_registration.md` byte-identical to committed file at task close.

### 8.7 Discipline gate tests (~2 tests)

- No imports from `src/lloyd_v4/refinery/` in any new file. Grep test.
- No `math.fma`, `math.pow`, `cmath`, `scipy`, `sympy`, `mpmath`, `statsmodels`, `numpy.special`, `numpy.random` introduced. No fractional-power pattern (e.g., `** 0.25`, `numpy.power(..., 0.25)`).

## 9. Required Commands

1. `git status` — clean.
2. `git log -1 --oneline` — record HEAD.
3. Confirm Task 033 commit on `origin/main`.
4. `pytest -q tests/` — baseline.
5. Create `pre_registration.md` per §7.1.
6. `git add Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/pre_registration.md`
7. `git commit -m "Task 034 pre-registration: Schwarzschild-quartic transformed-operand n=4 fixture..."` (full message per §7.1)
8. Record pre-registration commit hash.
9. Implement modules and tests.
10. `pytest -q tests/` — confirm all pass.
11. Run campaign; write all output JSONs and `headline_classification.md`.
12. Run campaign a second time; diff against repository copies; byte-identical.
13. Write `task034_schwarzschild_quartic_transformed_n4_summary.md`.
14. `pytest -q tests/` — final.
15. `git add -A && git commit -m "Task 034: Schwarzschild-quartic n=4 transformed-operand — <headline>" && git push origin main`.
16. `git status` — clean.
17. `git log -2 --oneline` — both commits visible on `origin/main`.

## 10. Non-Goals

- **NOT** modifying any substrate primitive.
- **NOT** modifying `layer_manifest.json`.
- **NOT** building a Layer 2 module.
- **NOT** importing from `src/lloyd_v4/refinery/`.
- **NOT** building a parallel SR-quartic fixture (operand-structure invariance is a forward task).
- **NOT** running multi-precision battery (deferred).
- **NOT** building a native-rounding quartic primitive (Axiom 11 amendment or substantial Newton-iteration substrate work; outside this task).
- **NOT** running n=5 or higher radicals.
- **NOT** drafting follow-up tasks in the summary.
- **NOT** promoting any new concept to substrate.
- **NOT** using `math.pow`, `numpy.power` with fractional exponent, or any fractional-power pattern.

## 11. Acceptance Criteria

1. Pre-registration committed as its own commit before any measurement code ran.
2. All pre-existing tests pass.
3. All new tests pass (~25 new).
4. Fixture produces finite non-NaN values at every grid point at float32 and float64.
5. F3 produces calibration zero at every grid point at float64.
6. F2 `level_integer_residual_max` at float64 is one of `{0.0, 0.0625, 0.125, 0.25, 0.5}`; outside-set values force `lattice_grain_indeterminate_at_n4_transformed` with the value documented.
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

V4-substrate-native end to end. Both component pieces (Schwarzschild operand, composed-sqrt quartic radical) are existing V4 substrate elements; their composition is new.

### Axiom 11 — Epistemic stance only

`numpy.sqrt` is admitted as a basic numpy operation. The quartic radical is computed as $\sqrt{\sqrt{\cdot}}$ via two invocations. No fractional-power pattern, no named mathematical content. The two-rounding-events consequence of this composition is treated as a substantive structural property of the admitted form, accommodated explicitly in the pre-registration via the `0.0625` outcome category.

### Axiom 12 — Self-derivation

Every observation traces to Layer 1 primitives via existing campaign provenance. No new substrate concept is minted.

### Pre-registration is non-negotiable

The four outcomes are locked. The headline classification logic is locked. The fixture construction (Schwarzschild operand + composed-sqrt quartic) is locked. Post-hoc adjustment is forbidden. Observation diverging from all four named outcomes triggers `lattice_grain_indeterminate_at_n4_transformed` and the observed value is documented.

### What each outcome means

**`compound_law_h3_supported_at_n4` (0.125):** The compound hypothesis holds. F2 grain follows $2^{1-n}$ for transformed operands and stays at 0.25 for identity operands. The framework's claim that ULP-lattice quantisation reflects algebraic skeleton degree is supported in the transformed-operand row across n=2, n=3, n=4. Branch radical degree becomes inferable from substrate observation alone *for transformed-operand fixtures*.

**`transformed_decay_converges_to_identity_floor` (0.25):** The transformed-operand grain decays from 0.5 at n=2 through 0.25 at n=3 and remains at 0.25 at n=4. The transformed and identity grains converge at higher n. This is a substantive substrate finding with a more complex underlying mechanism than either H2 or H3 captures; further task work needed to characterise.

**`rounding_event_count_dominates` (0.0625):** The grain depends on rounding-event count rather than algebraic skeleton degree. The composed-sqrt's two rounding events produce $2^{-(2k)}$ where $k$ is the rounding event count, distinct from $2^{1-n}$. This outcome would refute the compound hypothesis as articulated and reframe the question: what V4 reads is rounding-event signature, not radical degree. The native-rounding quartic primitive would be the discriminating follow-up.

**`lattice_grain_indeterminate_at_n4_transformed` (other):** A more complex mechanism than any pre-registered hypothesis. Observed value documented; framework needs new theoretical work before further fixture exploration.

### What this does NOT settle

- The operand-structure invariance question. Schwarzschild operand involves division; SR operand involves squaring. Both produce 0.5 at n=2. A future SR-cbrt or SR-quartic would test whether the transformed-operand law is Schwarzschild-specific or holds across operand structures.
- The native-rounding versus composed-rounding question for n=4. If H_rounding is observed (0.0625), the rounding-event-count alternative becomes load-bearing and a native single-rounding quartic primitive is needed to discriminate.
- The behaviour at n=5 or higher. Whatever the n=4 result, n=5 transformed adds one more data point and either confirms the pattern or reveals additional structure.

### Byte-stability across measurement

All measurement runs are deterministic. No `numpy.random`. Repeat runs produce byte-identical output.

### Git discipline non-negotiable

Pre-registration commit lands on `origin/main` before measurement code runs. Main task commit lands before the task is considered closed.

---

## Appendix A — The grid after this task

The full 2×3 grid will read:

| | n=2 | n=3 | n=4 |
|---|---:|---:|---:|
| Identity operand | 0.25 | 0.25 | 0.25 |
| Transformed operand | 0.5 (×2) | 0.25 | **[observed]** |

If observed = 0.125: clean 2×3 confirmation of the compound hypothesis. The framework reads algebraic skeleton degree in the transformed-operand row.

If observed = 0.25: the transformed-operand row converges to the identity-operand floor at n=4. Two interpretations are equally consistent with the data: (a) the operand-transformation effect attenuates with n and floors at 0.25; (b) some interaction between radical-composition mechanism and operand transformation gives this specific result. Discriminating between them needs more fixtures.

If observed = 0.0625: rounding-event count dominates. The framework's diagnostic capability is for rounding signature, not algebraic degree, and the original "branch degree inferable from ULP-lattice quantisation" claim needs reframing.

## Appendix B — Why the rounding-event-count outcome is now load-bearing

Task 032 acknowledged the two-rounding-events caveat for the pure-algebraic-quartic fixture but did not treat it as a load-bearing prediction. The result there (0.25) was consistent with both H2 (operand-transformation rule, predicts 0.25 for identity) and a rounding-event-independent identity-operand floor. The two readings could not be distinguished.

At n=4 transformed, the compound hypothesis H3 makes a sharp algebraic-skeleton-degree prediction (0.125). The rounding-event-count alternative makes a sharp distinct prediction (0.0625). Pure-algebraic-quartic at n=4 identity gave 0.25, not 0.0625, so the rounding-event-count hypothesis would have to take a more specific form: rounding-event count matters *only when the operand is transformed*. That is itself a structural claim worth testing.

The pre-registered `0.0625` outcome is therefore not a guess at an unlikely value — it is the discriminating prediction for the rounding-event-count alternative under the constraint that pure-algebraic-quartic (n=4 identity, two roundings) gave 0.25. If observed, the substrate is telling us that rounding-event count interacts with operand-transformation status; if not, the simpler compound hypothesis or its convergence variant is in play.

## Appendix C — Sterbenz boundary as a tertiary invariance check

The Sterbenz-applicable region for $R^n - 1$ depends on the operand transformation, not on $n$, when the operand transformation is Schwarzschild's:

- Schwarzschild n=2: $R^2 \ge 1/2 \iff r \ge 4$.
- Schwarzschild-cbrt n=3 (Task 033): $R^3 \ge 1/2 \iff r \ge 4$.
- Schwarzschild-quartic n=4 (this task): $R^4 \ge 1/2 \iff r \ge 4$.

All three boundaries sit at the same $r$-value. If this fixture's observed boundary is also at $r = 4.0$ with above-density higher, the operand-determined-boundary observation is confirmed at a third radical degree. If the boundary shifts in this fixture, the operand-determined claim is more nuanced than the n=2 and n=3 evidence suggested.
