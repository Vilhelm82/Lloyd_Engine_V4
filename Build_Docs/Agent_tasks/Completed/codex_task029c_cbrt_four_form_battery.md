# Codex Task 029c — Structurally-Different Chain Fixture (Cube-Root Four-Form Battery)

## 0. Post-029b amendment

This spec was amended after Task 029b landed on `origin/main` (commit `7777bf5`, headline `mixed_resolution`). The amendment adds three F5+ predictions to the pre-registration as a **secondary, non-load-bearing** section. The five strong-cluster invariants remain load-bearing for the headline classification. The F5+ predictions inform the campaign's evidence weight but do not determine the headline.

Changes from the pre-amendment draft:

- Baseline test count updated to 553 (post-029b).
- Pre-registration deliverable (§6.1) now requires both a Section A (five strong-cluster invariants, load-bearing) and a Section B (three F5+ predictions, secondary).
- Campaign output JSON (§6.6) includes scale-invariant rank data and F5+ path classifications.
- New tests subsection (§7.10) covers the F5+ predictions.
- Completion report (§10) gains a secondary F5+ table.
- New Appendix B documents the derivation of the F5+ predictions from 029b.
- Test count target raised from ~22 to ~25 new tests.

The amendment is additive. The five-invariants framework, the Sterbenz prediction, and the headline classification are unchanged.

## 1. Repository / Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4`

**Baseline HEAD:** post-029b on `origin/main` (commit `7777bf5` or later). Codex starts from current `origin/main` at task execution time.

**Test baseline:** 553 passing (post-029b). Whatever the actual count is at task start, record it.

**Test count target:** previous baseline + ~25 new tests. Target ~578 against the 553 baseline.

## 2. Task Goal

Add a **cube-root four-form battery** as the fourth fixture in the cross-fixture chain-property campaign. The existing three fixtures (Schwarzschild, SR, pure algebraic) all share the same radical-degree-2 algebraic skeleton `R = sqrt(1 − x)`. This task tests whether the five preserved substrate invariants survive a **structural** variation of the algebraic skeleton: `R = cbrt(1 − x)`.

The four-form battery becomes:

- `F1 = R³ − f_direct` (cube the radical, subtract operand directly)
- `F2 = R³ − 1 + x` (cube the radical, expand `1 − x` form)
- `F3 = R − cbrt(f_direct)` (calibration identity, must be silent)
- `F4 = R − cbrt(f_alt_routing)` (calibration with operand-path variation)

with `f_direct = 1.0 − x` and `f_alt_routing` constructed by the **same operand-path variation pattern** the existing three fixtures use for F4 (i.e., a second algebraically-equivalent expression of `1 − x` that follows a different floating-point rounding path). The cbrt fixture must mirror the existing fixture pattern exactly except for the radical degree.

**Pre-registration is part of the task.** Predictions are committed to the repository **before** the campaign runs. The campaign is then run and observations are recorded. Match/mismatch is reported per prediction. This is the strongest available form of evidence for the universality claim and the primary defense against the "you tuned the framework to the data" attack.

**Three possible headlines:**

- `chain_property_universal` — all five invariants survive in cbrt fixture; universality claim genuinely strengthens from "sqrt-of-near-1 chains" to "controlled-branch radical chains."
- `chain_property_radical_specific` — one or more invariants diverge cleanly under cbrt; paper scopes honestly to radical-degree-2 family.
- `chain_property_partial` — mixed result with specific divergences; the divergences inform downstream task design (likely Task 030 operation-level annotation).

All three are legitimate outcomes. Codex must not pre-decide. The campaign reports what it observes.

## 3. Source Labelling

Each claim in this spec is labelled by source. Codex must honour the labels and not silently upgrade a proposal-evidence claim to V4-surface authority.

- **V4-surface (load-bearing):** typed substrate primitives, four-form battery infrastructure, polarity-grid-stability framework, lattice campaign framework, cross-fixture comparison framework, byte-stability discipline, all 12 axioms.
- **Theorem-derived:** Sterbenz boundary location prediction (R³ ≥ 1/2 → x ≤ 1/2 under `f = 1 − x`), F3 identity silence (cbrt(f) − cbrt(f) = 0 in IEEE 754 when both invocations are bit-identical).
- **Proposal evidence:** the `chain_property_*` classification headlines, the five-invariants framing, the predictions in Section 7.

## 4. Design Principles

1. **One structural variation per task.** This task adds exactly the cbrt fixture. No log/rational/Bell-strain fixtures. No α-1 recovery on the constraint surface. No multi-precision execution. Those are separate tasks.
2. **Mirror Task 028 structure.** Task 028 added pure algebraic as the third fixture; Task 029c adds cbrt as the fourth. The infrastructure changes are minimal and parameterized over fixture definitions.
3. **No substrate primitive additions.** The cbrt fixture lives in the evals layer. No new typed primitives. No new status families. No new protocols. No `layer_manifest.json` changes.
4. **Pre-registration is non-negotiable.** Predictions are committed to a `pre_registration.md` file in the task's report directory **in its own commit** before any campaign code is executed. The pre-registration commit hash is recorded in the task summary. If the prediction file is touched after the campaign runs, the task is invalid.
5. **Same canonical 137-point x-grid as the existing fixtures.** The grid is operand-dependent in interpretation (β² for SR, 2/r for Schwarzschild, x for pure algebraic and cbrt) but the numerical x-values are the same set. Do not reinvent the grid.
6. **Four-grid polarity stability battery applies unchanged.** Same four perturbation grids. Same cofire and sign-agreement metrics. Same bottle-cap thresholds.
7. **Lattice campaign applies unchanged.** Same per-path lattice grain extraction. Same classification (integer-lattice / non-integer-lattice / continuous). Same residual reporting.
8. **No physics-interpretive language anywhere.** Not in the fixture module, not in the report, not in the pre-registration. The cbrt fixture is a **mathematical structural variation**, not a domain model. No "cubic cosmology" or "cubic relativity" or any equivalent.

## 5. Primitive-Sufficiency Gate

| Concept used | Source layer | Status |
|---|---|---|
| Four-form battery | Evals layer (existing) | Re-used |
| Polarity-grid-stability | Evals layer (existing) | Re-used |
| Lattice campaign | Evals layer (existing) | Re-used |
| Cross-fixture comparison | Evals layer (existing) | Re-used, extended to 4 fixtures |
| Bottle-cap discipline | Evals layer (existing) | Re-used |
| Byte-stability verification | Evals layer (existing) | Re-used |
| `numpy.cbrt` for R computation | `numpy` (admitted as type/arithmetic container per Axiom 11) | New fixture-level operation |
| `numpy.sqrt` reference | `numpy` (already used by existing fixtures) | Unchanged |

**Axiom 11 disposition for `numpy.cbrt`.** `numpy.cbrt` is an IEEE-correctly-rounded arithmetic operation, conceptually at the same level as `numpy.sqrt`. It is not a named mathematical function in the Axiom 11 sense (`math`, `cmath`, `numpy.special`, `scipy.special`, `sympy`, `mpmath` content). The existing fixtures already use `numpy.sqrt` at the fixture-definition layer; `numpy.cbrt` enters by the same admission, at the same layer, for the same purpose (computing R from f in the fixture definition). This admission applies **only at the evals/fixture layer**. No substrate primitive is permitted to import `numpy.cbrt` as a result of this task.

**Forbidden alternatives** (Codex must reject if encountered):
- `math.cbrt` — `math` is forbidden under Axiom 11
- `f ** (1.0/3.0)` — not IEEE-correctly-rounded for cubes; rounds through log/exp; introduces a different error structure than `numpy.cbrt` and would compromise the cross-fixture comparability
- Hand-rolled Newton iteration for cube root — introduces solver dynamics into the fixture definition; not the same kind of operation as `numpy.sqrt`

**No new substrate concepts are minted.** Axiom 12 self-derivation: every concept used at this task traces to existing parent-layer provisions. The cbrt fixture is a new instance of an existing pattern, not a new pattern.

## 6. Required Deliverables

### 6.1 Pre-registration document

`Build_Docs/Reports/task029c_cbrt_four_form_battery/pre_registration.md`

Committed in a **dedicated commit before any campaign code is executed**. The document is structured in two sections:

**Section A — Strong-cluster invariants (load-bearing for headline)**

1. The five-invariants table with explicit per-invariant prediction (Section 7 of this spec is the source).
2. The Sterbenz boundary prediction (location and directional bias).
3. The fixture definition (operand domain, grid, f_direct, f_alt_routing, four-form expressions).

**Section B — Refined F5+ predictions (secondary, informative, non-load-bearing)**

Derived from Task 029b's `mixed_resolution` headline (see Appendix B for the derivation). The three predictions are:

1. **P_compound_split — predict PRESENT in cbrt strong cluster.** P_compound_split survived scale-invariant refinement in all three sqrt-fixtures (029b universal refined F5+ set). If the path is genuinely universal at the substrate level, it should appear in cbrt at the same strong-cluster threshold.
2. **P_sign_c — predict PRESENT in cbrt strong cluster.** Same rationale as P_compound_split.
3. **P_distrib_sqrt_mul — predict ABSENT or significantly attenuated in cbrt strong cluster.** In 029b, P_distrib_sqrt_mul aligned with sparse sqrt-specific route-residual cells in Schwarzschild and SR. The name itself encodes the sqrt assumption. The prediction is that this path either does not appear in the cbrt strong cluster at all, or appears with cofire rates substantially below the strong-cluster threshold. The negative prediction is the cleanest test of operation-specificity vs. substrate-universality.

**Status of Section B in the headline.** Section B predictions are reported with match/mismatch in the summary but do **not** determine the `chain_property_*` headline. The headline rides on Section A. Section B informs the cross-fixture evidence weight and is part of the paper's argument that the framework can distinguish substrate-universal from operation-specific structure.

**Document closing items:**

4. A statement that the predictions in both sections are not to be edited after this commit.
5. The commit hash of this commit (filled in retroactively in the task summary).

The pre-registration commit message must be exactly:

```
Task 029c pre-registration: cbrt four-form battery predictions

Predictions registered before campaign execution. Predictions are not to
be edited after this commit. Subsequent commits carry the campaign run
and observed results.
```

### 6.2 New fixture module

`src/lloyd_v4/evals/fixtures/cbrt_chain.py` (or whatever directory mirrors the existing fixture pattern — Codex should follow the existing convention; do not invent a new convention).

The module exposes:

- The operand-to-x conversion (operand is x directly; trivial here).
- `f_direct(x)`: `1.0 − x` (or whatever existing fixtures' convention names this).
- `f_alt_routing(x)`: the same alt-routing pattern existing fixtures use, applied to `1 − x` rather than to any sqrt-specific form. (Codex must read the existing pure-algebraic fixture and mirror its f_alt construction with the cbrt-appropriate substitution.)
- `R(x)`: `numpy.cbrt(f_direct(x))`.
- Four-form battery: `F1`, `F2`, `F3`, `F4` per Section 2.
- The canonical 137-point x-grid (same grid the existing fixtures use; this is shared, not duplicated).

### 6.3 Cross-fixture campaign extension

The existing cross-fixture comparison module (which currently runs over Schwarzschild + SR + pure algebraic) is parameterized to accept the cbrt fixture as a fourth entry. **No structural change** to the comparison framework — just register the cbrt fixture and let the existing framework consume it.

If the existing comparison framework hardcodes "three fixtures" anywhere, that hardcoding must be lifted to a list-driven parameterization. Lifting the hardcoding is in scope; redesigning the comparison logic is not.

### 6.4 Lattice campaign extension

Same disposition as 6.3. The existing lattice campaign accepts the cbrt fixture as input. Per-path lattice grain extraction and classification run unchanged.

### 6.5 Polarity-grid-stability campaign extension

Same disposition. Four grids, same bottle-cap thresholds, same sign-agreement metric.

### 6.6 Campaign output JSON

`Build_Docs/Reports/task029c_cbrt_four_form_battery/campaign_results.json`

Byte-stable across repeat runs (verified per Section 7.4). Contains:

- Per-fixture (now 4 fixtures) per-path (F1, F2, F3, F4) per-grid observations.
- Sign-agreement rates with binomial p-values (via `math.comb`).
- Lattice grain residuals and classifications.
- Sterbenz boundary observed location and below/above density ratios.
- Cross-fixture comparison table (5 invariants × 4 fixtures).
- **Scale-invariant rank data for the cbrt fixture** (mirrors Task 029b's methodology). The rank cut at 0.10 is reported with cluster membership.
- **F5+ path classification for the cbrt fixture** at the strong-cluster threshold, specifically the status of P_compound_split, P_sign_c, and P_distrib_sqrt_mul (present / absent / attenuated). This populates the Section B match/mismatch table in the summary.

### 6.7 Headline classification record

`Build_Docs/Reports/task029c_cbrt_four_form_battery/headline_classification.md`

One of: `chain_property_universal`, `chain_property_radical_specific`, `chain_property_partial`. With explicit per-invariant match/mismatch against the pre-registration.

### 6.8 Task summary

`Build_Docs/Reports/task029c_summary.md`

Standard task-summary structure (mirror `task028_summary.md` and `task029_summary.md`). Must include:

- Pre-registration commit hash.
- Five-invariants table with prediction, observation, and match/mismatch.
- Sterbenz boundary observed location and bias direction.
- Lattice grain residual for cbrt fixture (specific value, e.g. 0.5, 0.25, or other).
- F1∥F2 grid-stable sign-agreement rate for cbrt (with p-value).
- Headline classification with one-paragraph justification.
- Byte-stability diff result (must be "no diff").
- Forward observations (not next-task drafts). What did the cross-fixture comparison reveal that informs Task 030 design? Do not draft Task 030.

## 7. Required Tests

Approx **25 new tests**, all under `tests/test_task029c_cbrt_four_form_battery.py` unless a logical separation is cleaner. Target total: ~578 (against the 553 post-029b baseline).

### 7.1 Pre-task evidence

- Baseline test count matches `origin/main` at task start. Record HEAD hash.
- All pre-existing tests pass before any new code is added.
- Confirm Task 029b is on `origin/main` (commit `7777bf5` or its descendant); halt if not.

### 7.2 Fixture-definition tests (~6 tests)

- `numpy.cbrt(8.0) == 2.0` exactly (sanity check on the chosen primitive — IEEE-correct cube root).
- `numpy.cbrt(0.125) == 0.5` exactly.
- F3 calibration silence: F3 evaluates to exactly 0.0 at every cell of the canonical grid (this is the calibration zero; non-zero F3 means the fixture is wrong).
- F1 and F4 produce finite non-NaN values at every cell of the canonical grid.
- F2 produces finite non-NaN values at every cell.
- `f_alt_routing` differs from `f_direct` by at most a few ulps at every cell, never by more.

### 7.3 Stratum coverage tests (~4 tests)

- Sterbenz-applicable region (x ≤ 1/2) and Sterbenz-inapplicable region (x > 1/2) are both populated in the canonical grid.
- F3 silence holds across both regions.
- The grid contains x = 1/2 exactly (or as close as the grid construction permits) for boundary-location verification.

### 7.4 Byte-stability tests (~3 tests)

- `campaign_results.json` byte-identical between two consecutive runs (write to /tmp/, diff against repository copy).
- `pre_registration.md` byte-identical to the committed file at task completion (no post-hoc edits).
- `headline_classification.md` byte-identical between two consecutive runs.

### 7.5 Discipline gate tests (~5 tests)

- F3 sentinel: F3 ≡ 0 at every cell, every grid. If F3 ever fires, the test halts loudly.
- Negative control: F1/F4 do not aggregate to `grid_stable_polarity_coupling` (F1/F4 should still classify as `depolarized_invariant` or `open_underpowered` in cbrt as in existing fixtures).
- Bottle-cap: F2/F4 do not promote to `grid_stable_polarity_coupling` unless all four grids have cofire ≥ 10.
- No manifest changes: `layer_manifest.json` byte-identical to its state at task start.
- No physics-interpretive language: source-grep test rejects "Kerr", "lightspeed", "frame dragging", "cosmology", "relativistic" appearing in any new file from this task. (Mirror the existing source-grep discipline test pattern.)

### 7.6 Source-purity tests (~2 tests)

- No `math.cbrt`, no `cmath`, no `scipy`, no `sympy`, no `mpmath`, no `math.pi`/`math.e` introduced.
- No `f ** (1.0/3.0)` or `f ** (1/3)` patterns introduced for cube root.

### 7.7 Methodology gate tests (~2 tests)

- The four paths F1, F2, F3, F4 cluster into four distinct signature groups in the cbrt fixture (same gate the existing fixtures pass).
- Sterbenz boundary observed location matches the pre-registered location (x = 1/2 ± grid resolution).

### 7.8 Refined F5+ prediction tests (~3 tests)

These tests verify that the campaign infrastructure produces the data needed to evaluate Section B of the pre-registration. They do not enforce the prediction outcome — that's the campaign's job — they enforce that the data exists and is reported correctly.

- **Scale-invariant rank computed for cbrt fixture.** The `campaign_results.json` contains a `scale_invariant_rank_cut_0_10` field for the cbrt fixture with cluster membership recorded per path. The rank is reported even if it differs from the existing three fixtures.
- **P_compound_split and P_sign_c classification recorded.** The campaign output reports the strong-cluster status of P_compound_split and P_sign_c in the cbrt fixture as one of `{present, absent, attenuated}` with the cofire rate that drove the classification.
- **P_distrib_sqrt_mul classification recorded.** Same as above for P_distrib_sqrt_mul. The classification field is populated regardless of whether the path is present or absent — `absent` is a first-class outcome and must be recorded explicitly, not as a missing key.

## 8. Required Commands

Codex executes these in order:

1. `git status` — confirm clean working tree.
2. `git log -1 --oneline` — record current HEAD.
3. `pytest -q tests/` — confirm baseline.
4. Create `Build_Docs/Reports/task029c_cbrt_four_form_battery/pre_registration.md` with predictions per Section 7.
5. `git add Build_Docs/Reports/task029c_cbrt_four_form_battery/pre_registration.md`
6. `git commit -m "Task 029c pre-registration: cbrt four-form battery predictions

Predictions registered before campaign execution. Predictions are not to
be edited after this commit. Subsequent commits carry the campaign run
and observed results."`
7. Record the pre-registration commit hash. This is referenced in the final summary.
8. Implement the fixture module, campaign extension, and tests.
9. `pytest -q tests/` — confirm new test count and all pass.
10. Run the campaign; write `campaign_results.json`.
11. Run the campaign a second time, write to `/tmp/campaign_results_repeat.json`, `diff` against repository copy. Verify byte-identical.
12. Write `headline_classification.md` based on observed-vs-predicted.
13. Write `task029c_summary.md`.
14. `pytest -q tests/` — final confirmation.
15. `git add -A && git commit -m "Task 029c: cbrt four-form battery — <headline>" && git push origin main`
16. `git status` — confirm clean working tree post-push.
17. `git log -2 --oneline` — confirm both pre-registration and main task commits are on origin/main.

## 9. Non-Goals (Loud and Explicit)

- **NOT** extending substrate primitives. No new typed primitives. No new status families. No new protocols.
- **NOT** modifying `layer_manifest.json`. Byte-identical to its state at task start.
- **NOT** promoting any observable to substrate. Promotion criteria are unchanged from the substrate handoff: chain-property fully supported (✓ at strong-cluster level if 029c lands `chain_property_universal`) AND joint-state reveals derivable law (NOT yet — that's Task 030 territory).
- **NOT** adding log/rational/Bell-strain fixtures. One structural variation per task.
- **NOT** running multi-precision execution. That's Task 017b territory.
- **NOT** running α-1 recovery on cbrt branch point. That's Attack 6 / a future α-validation task.
- **NOT** using `math.cbrt` or `**(1.0/3.0)` for cube root.
- **NOT** using `numpy.random`, `scipy`, `sympy`, `mpmath`, math-named constants, or clustering libraries.
- **NOT** introducing physics-interpretive language for the cbrt fixture.
- **NOT** pre-deciding the outcome. `chain_property_universal` is one of three possible headlines, not the target.
- **NOT** drafting Task 030 (or any forward task) in the task summary. Forward observations only.
- **NOT** drafting the paper revision incorporating cbrt results. That's a separate, post-029c action by the user.

## 10. Completion Report

`Build_Docs/Reports/task029c_summary.md` must contain, in this order:

1. **Scope** — one paragraph describing what was added (cbrt fixture as fourth chain-property fixture) and what was not added.
2. **Pre-registration** — commit hash and date.
3. **Section A — Five-invariants table (load-bearing for headline):**

   | Invariant | Prediction | Observed | Match? |
   |---|---|---|---|
   | F1∥F2 grid-stable polarity coupling | 100% sign agreement, p < 0.01, all 4 grids cofire ≥ 10 | (fill in) | (Y/N) |
   | F3 identity silence | F3 ≡ 0 at every cell | (fill in) | (Y/N) |
   | F2 non-integer lattice grain | non-integer character, grain TBD | (fill in) | (Y/N) |
   | F4 integer lattice character | integer-lattice classification | (fill in) | (Y/N) |
   | Sterbenz boundary at x = 1/2, below density > above | location at x = 1/2, below higher | (fill in) | (Y/N) |

4. **Section B — Refined F5+ predictions table (secondary, non-load-bearing):**

   | Path | Prediction | Observed status | Cofire rate | Match? |
   |---|---|---|---|---|
   | P_compound_split | PRESENT in cbrt strong cluster | (fill in) | (fill in) | (Y/N) |
   | P_sign_c | PRESENT in cbrt strong cluster | (fill in) | (fill in) | (Y/N) |
   | P_distrib_sqrt_mul | ABSENT or attenuated in cbrt strong cluster | (fill in) | (fill in) | (Y/N) |

5. **Sterbenz boundary section** — observed location, below/above densities, comparison to pure algebraic.
6. **Headline classification** — one of `chain_property_universal` / `chain_property_radical_specific` / `chain_property_partial`, with one paragraph of justification grounded in **Section A only**. Section B match/mismatch is reported but does not enter the headline.
7. **F5+ interpretation paragraph** — what does Section B tell us about substrate-universality vs operation-specificity? Specifically, if P_distrib_sqrt_mul was predicted absent and is observed absent, that is mechanism-specificity evidence. If it is observed present in cbrt, the sqrt-specific characterisation from 029b needs revisiting. Either direction is informative.
8. **Tests** — total count, new tests added, pytest result.
9. **Byte-stability** — confirmation of no-diff on both campaign and pre-registration files.
10. **Discipline gates** — explicit confirmation that F3 sentinel held, negative control held, bottle-cap held, no manifest changes, no physics-interpretive language, no `math.cbrt`/`**(1/3)` patterns introduced.
11. **Files changed** — full list.
12. **Forward observations** — what did the cross-fixture comparison reveal about (a) chain-property generality across radical degree, (b) whether the Sterbenz mechanism explanation needs refinement, (c) whether the lattice-grain operand-dependence has more structure than currently described, (d) whether Section B's F5+ results suggest further mechanism-specificity work. **No next-task drafts.**

## 11. Acceptance Criteria

The task is complete when all of the following hold:

1. Pre-registration committed as its own commit before any campaign code was executed, containing both Section A (five-invariants) and Section B (F5+ predictions).
2. All pre-existing tests pass.
3. All new tests pass (target ~25 new).
4. F3 silence holds in cbrt fixture (sentinel did not fire).
5. `campaign_results.json` byte-stable across repeat runs.
6. `pre_registration.md` byte-identical to the committed file (no post-hoc edits).
7. `layer_manifest.json` byte-identical to start state.
8. No physics-interpretive language in any new file.
9. No forbidden imports or arithmetic patterns introduced.
10. Headline classification recorded, grounded in Section A only.
11. Section B match/mismatch reported with cofire rates, regardless of outcome.
12. Forward observations recorded without drafting next task.
13. Final commit pushed to `origin/main`. `git status` returns clean. The pre-registration commit and the main task commit are both on `origin/main`, in order.

## 12. Discipline Notes

### Axiom 10 — V3 reference-only

V3 has no cbrt fixture. There is nothing to reference. The cbrt fixture is a clean V4 evals-layer construct following the existing V4 fixture pattern. No V3 lookup is required or permitted.

### Axiom 11 — Epistemic stance only

`numpy.cbrt` is admitted at the fixture/evals layer as an IEEE-correctly-rounded arithmetic operation, conceptually identical in status to `numpy.sqrt`. This admission **does not extend** to substrate primitives. No substrate primitive is permitted to depend on `numpy.cbrt` as a result of this task. If at any point a substrate-layer concept appears to require cbrt (which would be surprising and is not anticipated), the task halts and the design issue is reported in the summary; substrate is not modified to accommodate.

Forbidden:
- `math.cbrt` (Axiom 11 forbids `math` content)
- `f ** (1.0/3.0)` (different error structure; not IEEE-correctly-rounded for cubes)
- Hand-rolled Newton-iteration cube root in the fixture module (introduces solver dynamics; not the same operation as `numpy.sqrt`)
- Hardcoded mathematical constants (no `pi`, no `tau`, no `e`)

### Axiom 12 — Self-derivation

Every concept used at this task traces to existing parent-layer provisions. The cbrt fixture is a new instance of the existing chain-property fixture pattern, parameterised over radical degree. No new substrate concepts are minted. If during execution a concept appears to be required that does not exist in a parent layer, the task halts; the concept is reported as a forward observation; substrate is not extended ad hoc.

### V3-shape patterns to avoid

The cbrt fixture is a fresh evals-layer fixture. Any temptation to import V3 cbrt machinery (if any exists) is forbidden by Axiom 10. The fixture must be built from V4 evals-layer primitives only.

### Bottle-cap and negative-control discipline

The bottle-cap on F2/F4 promotion (all four grids cofire ≥ 10) and the negative-control on F1/F4 (must aggregate to `depolarized_invariant` or `open_underpowered`, never `grid_stable_polarity_coupling`) apply to the cbrt fixture exactly as they apply to the existing three fixtures. If either gate fires in an unexpected way for cbrt, it is a substantive observation that must be recorded in the summary and reported as a forward observation, not patched around.

### F3 sentinel

The F3 sentinel rule is unchanged: F3 ≡ 0 at every cell of every grid in every fixture at every precision tested in this task. If F3 ever fires non-zero, the fixture definition is wrong (the two cbrt invocations in F3 are not bit-identical) and the task halts loudly. F3 firing is not a publishable result; it is a fixture bug.

### Byte-stability

All campaign outputs must be byte-stable. Run the campaign twice. Diff. The diff must be empty. If outputs are not byte-stable, the campaign uses non-determinism somewhere (`numpy.random` is forbidden; `random.Random(seed)` is the only admitted source of stochasticity, and even that must produce deterministic output given a fixed seed).

### Physics-interpretive language ban

The cbrt fixture is a mathematical structural variation. It has no physics interpretation. Do not name it after a physical phenomenon. Do not describe it in physics terms. The grep test in Section 7.5 enforces this. The lens framing (different fixtures probe the same substrate property at different operand transformations) applies; physics labels do not.

### Git discipline non-negotiable

The pre-registration commit lands on `origin/main` before campaign code is executed. The main task commit lands on `origin/main` before the task is considered closed. `git status` returns clean. The summary references both commit hashes. If git push fails, retry; do not close the task with local-only commits.

---

## Appendix A — The Sterbenz boundary prediction in detail

The Sterbenz mechanism applies to subtractions `a − b` where `a/2 ≤ b ≤ 2a`. F2 across all fixtures begins with `R^n − 1` (where n = 2 in existing fixtures, n = 3 in this fixture). The subtraction is Sterbenz-exact whenever `R^n ≥ 1/2`.

Substituting `R^n = f = 1 − x`:

| Fixture | R^n expression | Sterbenz-exact when |
|---|---|---|
| Schwarzschild | `R² = 1 − 2/r` | `1 − 2/r ≥ 1/2` → `r ≥ 4` |
| SR | `R² = 1 − β²` | `1 − β² ≥ 1/2` → `β ≤ 1/√2` |
| Pure algebraic | `R² = 1 − x` | `1 − x ≥ 1/2` → `x ≤ 1/2` |
| **cbrt (this task)** | `R³ = 1 − x` | `1 − x ≥ 1/2` → `x ≤ 1/2` |

**The boundary location for the cbrt fixture is predicted to be exactly the same as the pure algebraic fixture: x = 1/2.** The radical degree (n) does not enter the Sterbenz condition because Sterbenz operates on the *value* of `R^n − 1`, not on n itself.

**Predicted directional bias:** below density > above density (matching pure algebraic, since both use `1 − x` operand transformation).

If the observed boundary location is also at x = 1/2 with below-density-higher bias, this is **strong evidence** that the Sterbenz mechanism is operating on the value of `R^n` (not on the radical degree) and that the chain-property's apparent universality reflects a substrate-level mechanism rather than a sqrt-specific accident.

If the observed boundary location shifts (e.g., to some other x value) or the bias direction inverts, the Sterbenz explanation needs refinement — most likely a secondary mechanism associated with the cbrt operation itself, which would be a substantive new observation worth a forward note.

The pre-registration locks this prediction in writing before the campaign runs. Match or mismatch, the result is informative.

---

## Appendix B — Refined F5+ predictions from Task 029b

Task 029b resolved the F5+ methodology question with headline `mixed_resolution`. The three classes of result from 029b inform the three Section B predictions in this task:

**1. Methodology-artefact candidates (collapsed under scale-invariant metric):**

- P_scaled_2 and P_scaled_half collapsed in all three sqrt-fixtures under the scale-invariant rank metric at cut = 0.10. They were tracking magnitude-dependent rank inflation, not substrate-distinct paths. **They are not in this task's Section B predictions.** They are closed as artefact.

**2. Universal refined F5+ paths (survived scale-invariant refinement):**

- **P_compound_split** survived in all three sqrt-fixtures. If the path is substrate-universal, it should appear in the cbrt fixture's strong cluster as well. Section B prediction: **PRESENT**.
- **P_sign_c** survived in all three sqrt-fixtures. Same rationale. Section B prediction: **PRESENT**.

**3. Operation-specific paths (aligned with sqrt-specific structure):**

- **P_distrib_sqrt_mul** aligned with sparse sqrt route-residual cells in Schwarzschild and SR. The name itself encodes the sqrt assumption (`distrib_sqrt_mul` = distribution of square-root multiplication). If the substrate-vs-operation discrimination is real, this path should not appear (or should be significantly attenuated) in a cbrt fixture. Section B prediction: **ABSENT or attenuated**.

**Why the negative prediction is the strongest:**

A positive prediction confirms an expected pattern. A correctly-fulfilled **negative** prediction is sharper evidence — it demonstrates the framework can identify what does *not* generalise, not just what does. If P_distrib_sqrt_mul is predicted absent in cbrt and observed absent, the cross-fixture campaign demonstrates **mechanism specificity**: the framework distinguishes substrate-universal from operation-specific structure. This is materially stronger ground than the existing "all five invariants hold across three sqrt-fixtures" line and a direct counter to the "you tuned it to the data" attack.

If P_distrib_sqrt_mul is observed present in cbrt instead, then the sqrt-specific characterisation from 029b needs revisiting. Either it was misnamed (the underlying structure is not sqrt-specific) or there is a cross-radical mechanism that happens to surface through the same path signature. Either direction is a substantive finding.

**Decimal scaled-form audit consistency:**

029b also classified all three sqrt-fixtures as `decimal_multiplication_rounding` at decimal-50 precision. This is consistent with the P_scaled_* artefact classification. For 029c, the decimal-50 audit at the cbrt fixture is not in scope (multi-precision execution is Task 017c). The cbrt strong-cluster determination in this task is at float64.

**Status in the headline:**

Section B predictions are reported with match/mismatch in the summary but do **not** determine the `chain_property_*` headline. The headline rides on Section A. Section B informs the cross-fixture evidence weight and is the primary mechanism-specificity test result for the paper.
