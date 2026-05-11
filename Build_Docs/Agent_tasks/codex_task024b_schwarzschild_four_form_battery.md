# Codex Task 024b — Schwarzschild Four-Form Battery Under V4 Typed Substrate

## 1. Repository & Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4` (laptop) — currently checked
out on the post-023b branch.

**Pre-task baseline (must be confirmed before any code is written):**

```bash
cd ~/projects/V4/Lloyd_Engine_V4
source .venv/bin/activate
git status                                    # tree should be clean
git log -1 --format='%h %s'                   # last commit should be Task 023b
python -m pytest -q tests/ 2>&1 | tail -3     # all tests passing
```

Record the post-023b test count in the completion report. Do not start the
task if the baseline is dirty or any tests fail.

---

## 2. Task Goal

Run a V4-native typed-substrate discovery campaign on V3's four-form
Schwarzschild battery. The campaign reconstructs the V3 fixture under V4
arithmetic, runs V4's existing primitives across the sweep, and emits a
typed observation report. The headline deliverable is the **stratum pattern
across the four forms**, not a fitted slope value.

This task is the V4 re-investigation of V3 Experiment 2 (Section 4 of the
V3 session report). It is **not** a replication of V3's slope. V3's
reported slope of −0.4988 on F₄ is mechanical-property reference evidence
that the design problem is real and that the (α−1) law has been observed
under V3 substrate. V4 must arrive at its own observations through V4
primitives.

The four forms (with M = 1, geometrised units):

| Form | Expression | Property |
|------|------------|----------|
| F₁ | R² − (1 − 2/r) | squared, subtraction |
| F₂ | R² − 1 + 2/r | squared, reordered addition |
| F₃ | R − √(1 − 2/r) | sqrt, same arithmetic path |
| F₄ | R − √((r − 2)/r) | sqrt, different arithmetic path |

with R := √(1 − 2/r) evaluated once at each r.

All four are algebraically identically zero. V3 reports F₃ identically
zero in floating point, F₁/F₂ as sparse ±1-ULP residuals, and F₄ as a
structurally non-zero ULP-quantised residual that follows
F₄ ≈ δf / (2·√f) where f := 1 − 2/r and δf is the path-roundoff residual
on f. V4 is asked to make its own typed observations of this structure
and report them through its primitives' typed statuses.

---

## 3. Source Labelling

Every quantity used in this task must fall into one of these three
categories. The spec is explicit about which category each piece of
evidence lives in, and the test layer enforces the discipline.

**V4-surface:** primitive operations, status families, value types, and
manifests already present in `src/lloyd_v4/`. This task adds no new
primitives, no new status families, no new value types, and no new
manifests. Only an `evals/` campaign module, a `Build_Docs/Reports/`
output directory, and a discovery-campaign test file.

**V3 reference (mechanical property):** the four-form formulas (F₁–F₄),
the canonical R-recipe, the sweep range r ∈ [2.005, 10.0] with 137 points,
the predicted transfer law F₄ ≈ δf / (2·√f), and the static reference
overlay table. These are V3 reference evidence per Axiom 10 and the
V3 reference hygiene rules. V4 reconstructs the fixture from formulas
and uses the V3 table only for a single fixture-validation assertion.

**Proposal evidence:** the empirical pattern V4 is asked to surface
(F₃ silent, F₁/F₂ partial-observe, F₄ observes-with-structure). This is
the predicted V4 finding under the V4 substrate, not a target V4 must
hit. Whatever V4 actually emits is the result.

The pre-task evidence section below records the import-failure and
output-absence facts that confirm Task 024b has not yet been executed.

---

## 4. Design Principles

**No new primitives.** This task exercises existing primitives. If a
primitive's typed output is not sufficient to characterise some form's
residual structure, that limitation is itself the finding — record it,
do not paper over it by adding ad-hoc machinery.

**No new status families.** All emitted statuses must be from existing
`TransferStatus`, `SlopeStatus`, `AlphaProbeStatus`, and (where used)
`ScalarAlphaJetBundleStatus` or `SingularAlphaJetBundleStatus`.

**No imports of named mathematical content beyond what is already
permitted.** No `math.sqrt`, no `scipy`, no `mpmath`. The campaign script
uses Python operators and `**0.5` for square roots (consistent with
the existing primitive code which is `math`-free per Axiom 11). `numpy`
is permitted at the campaign-script layer for array bookkeeping only —
no `numpy.sqrt`, no `numpy.linalg`, no special functions.

**Comparison-overlay only at one explicit point.** V3's reference table
is loaded for exactly one assertion: that V4's reconstructed F-values
agree with V3's table to within 1 ULP at every sweep point. After that
assertion, V3's table is not used again. V4's slope fits, status
emissions, and reliability evidence are V4's product alone.

**Stratum pattern is the primary deliverable.** Slope values are
secondary. The campaign report lists, for each form, the count of
samples that produced each terminal status across the sweep.

**The substrate gets to refuse.** If V4's `typed_finite_difference`
emits `TRANSFER_CANCELLATION_DOMINATED` at most or all F₄ steps near
the horizon, that is a legitimate finding. If `typed_log_log_slope`
refuses on F₃ because the input log-collection is degenerate, that is
the correct emission. The campaign does not retry with different probe
parameters to "make the slope fit succeed." It records what V4 says.

---

## 5. Primitive-Sufficiency Gate

| Concept used | Source layer | Provides | Notes |
|---|---|---|---|
| Square-root of a non-negative float | language operator | `x ** 0.5` | Used to evaluate R and the F₄ inner sqrt. |
| Sweep collection | `lloyd_v4.primitives.typed_collection` | typed wrapper over (r_i) sequence | Provides primitive lineage at the input boundary. |
| Adjacent-r transfer observation | `lloyd_v4.primitives.typed_finite_difference` | `TransferObservation` per adjacent pair | One sweep per form. |
| Slope of `log\|transfer\|` vs `log\|f\|` | `lloyd_v4.primitives.typed_log_log_slope` | `LogLogSlopeObservation` | One bare-slope fit per form. |
| α-probe near horizon | `lloyd_v4.primitives.directional_alpha_probe` | `AlphaProbeObservation` with 023b reliability fields | One probe per form, h-grid = r-sweep tail near horizon. |
| Status concepts and validity carriers | `lloyd_v4.core` | `TypedResult`, `Validity`, `Provenance` | Standard. |

No concept used in this task is absent from existing parent layers.
Axiom 12 is satisfied trivially because no new layer is being introduced.

---

## 6. Fixture Construction

### 6.1 The Schwarzschild four-form fixture

Implement a fixture module `src/lloyd_v4/evals/schwarzschild_four_form.py`
(create the `evals` package if it does not exist; see §9.1 for path
discipline). The module provides:

- A constant `M = 1.0`.
- A function `f_of_r(r: float) -> float` returning `1.0 - 2.0/r`.
- A function `R_of_r(r: float) -> float` returning `(1.0 - 2.0/r) ** 0.5`.
- Four callables:
  - `F1_of_r(r)` → `R_of_r(r) ** 2 - (1.0 - 2.0/r)`
  - `F2_of_r(r)` → `R_of_r(r) ** 2 - 1.0 + 2.0/r`
  - `F3_of_r(r)` → `R_of_r(r) - (1.0 - 2.0/r) ** 0.5`
  - `F4_of_r(r)` → `R_of_r(r) - ((r - 2.0) / r) ** 0.5`
- A function `delta_f_of_r(r)` returning the path-roundoff residual on
  f, computed as `(1.0 - 2.0/r) - (r - 2.0)/r`. (This is the V3 δf
  recipe. V4 evaluates it the same way to enable F₄/δf comparison.)
- A function `sweep_r_values()` returning the 137-point r-sweep used by
  V3, exactly as in the V3 reference table. The recipe is *not*
  uniform — V3 used a denser schedule near the horizon. The simplest
  honest reconstruction is to load the r-values from the static
  reference table (see §6.2) at module-load time.

### 6.2 V3 reference overlay (static fixture)

Copy the V3 reference table into the repo as a static fixture:

```
Build_Docs/Reports/task024b_schwarzschild_four_form/
    v3_reference_overlay.csv
    v3_reference_overlay.json
```

These two files are the V3-provided 137-point reference table (CSV and
JSON formats already supplied to the user; copy from
`~/Downloads/schwarzschild_four_form_battery.{csv,json}` if present, or
note in the completion report that the reference table needs to be
sourced and placed manually). The CSV is the canonical form for the
fixture-validation test; the JSON carries V3's metadata block.

These are static reference evidence per Axiom 10. They are read in one
test (the fixture-validation test, §10.3) and nowhere else.

### 6.3 The campaign script

A campaign driver `src/lloyd_v4/evals/schwarzschild_four_form_campaign.py`
that runs the V4 primitive battery and emits the campaign report. The
campaign:

1. Builds `r_values = sweep_r_values()` (137 points).
2. For each form k ∈ {1, 2, 3, 4}:
   a. Constructs a `typed_collection` of (r_i, F_k(r_i)) value
      observations.
   b. Constructs the sequence of adjacent-pair transfer observations
      via `typed_finite_difference(F_k, base=r_i, delta_f=r_{i+1}-r_i,
      function_label=f"F{k}_of_r")` for i in 0..135.
   c. Runs `typed_log_log_slope` on the typed_collection of transfer
      observations, fitting `log|transfer|` vs `log|f_of_r(r_i)|`.
   d. Runs `directional_alpha_probe` on the callable `lambda h:
      F_k(2.0 + h)` with an h-grid = `[r_i - 2.0 for r_i in r_values]`
      and eta=1e-6, function_label=f"F{k}_horizon_approach".
3. Aggregates emitted statuses, slope values, alpha values, and
   023b reliability fields into a single campaign-output JSON.
4. Writes the JSON to
   `Build_Docs/Reports/task024b_schwarzschild_four_form/campaign_output.json`.

The campaign is deterministic — same r-sweep, same arithmetic, same
output every run. The output JSON must be byte-stable across runs (no
nondeterministic ordering, no timestamps in payload, no random ids).

---

## 7. Required Probes Per Form

For each of F₁, F₂, F₃, F₄ the campaign emits:

### 7.1 Transfer sweep

136 adjacent-pair transfer observations (137 samples → 136 adjacent
pairs). For each one, record:

- `transfer` value
- `g_at_f`, `g_at_f_plus_delta`, `delta_g`
- `cancellation_ratio`
- terminal `TransferStatus`
- `trace_id`

Per-form aggregate counts of each terminal status (e.g., for F₃ we
expect 136 × `transfer_observed` with `transfer = 0`; for F₄ we expect
some mix of `transfer_observed` and possibly
`transfer_cancellation_dominated`; record what V4 actually emits).

### 7.2 Log-log slope fit

One bare-slope fit per form: `log|transfer|` vs `log|f_of_r(r_i)|`. For
each, record:

- terminal `SlopeStatus`
- if `slope_observed`: slope, intercept, R², standard_error, n_used,
  log_f_min, log_f_max
- if refused: the refusal reason and n_used

V3-comparison overlay: for forms where `slope_observed` holds, report
the V4 slope alongside V3's reported slope of −0.4988 for F₄ (V3 fitted
log|F₄/δf| vs log f; V4 is fitting log|transfer| vs log f, so the
numerical slopes are not directly comparable — record both numbers
without claiming match-or-mismatch in the spec, let the report state
the relationship empirically).

### 7.3 Directional α-probe near horizon

One α-probe per form. Probe callable: `lambda h: F_k(2.0 + h)`. Approach
grid: the sorted positive h-values from `[r_i - 2.0 for r_i in r_values]`
(127 of the 137 points have r − 2 > 0; use those, ascending). Eta:
1e-6. Function label: `f"F{k}_horizon_approach"`.

Record:

- terminal `AlphaProbeStatus`
- if observed: observed_alpha, observed_slope, R², standard_error,
  n_observed, slope_trace_id
- 023b reliability fields: alpha_window_min, alpha_window_max,
  alpha_window_span, propagated_window_error, alpha_stability_status,
  nested_window_fits summary (count of fits, span across fits)

### 7.4 V3 transfer-function-law overlay

For F₄ only, compute V3's predicted F₄ at each r:

```
F4_pred(r) = delta_f_of_r(r) / (2.0 * f_of_r(r) ** 0.5)
```

and the ratio `F4_act / F4_pred` at each sweep point where F₄ ≠ 0 and
F₄_pred ≠ 0. Report the median and inter-quartile range of the ratio.
V3 reported ratios near 1.0. This is the closest 024b gets to V3's
quantitative claim, and it is reported as a single descriptive
statistic on V4's reconstructed values — not as a slope match.

---

## 8. Required Deliverables

### 8.1 Source files (new)

- `src/lloyd_v4/evals/__init__.py` — package marker (if `evals` package
  does not already exist).
- `src/lloyd_v4/evals/schwarzschild_four_form.py` — fixture module
  per §6.1.
- `src/lloyd_v4/evals/schwarzschild_four_form_campaign.py` — campaign
  driver per §6.3.

### 8.2 Test files (new)

- `tests/test_task024b_schwarzschild_four_form.py` — discipline tests
  per §10.

### 8.3 Report directory (new)

- `Build_Docs/Reports/task024b_schwarzschild_four_form/`
  - `v3_reference_overlay.csv` — static V3 reference table (CSV)
  - `v3_reference_overlay.json` — static V3 reference table (JSON with
    metadata)
  - `campaign_output.json` — V4 campaign output, generated by running
    the campaign script
  - `README.md` — short description of the directory contents and how
    to reproduce the campaign output
- `Build_Docs/Reports/task024b_summary.md` — the completion report
  (template in §13).

### 8.4 Manifest updates

None. Task 024b adds no new exports, no new status families, no new
operations.

### 8.5 Architecture doc updates

None unless the campaign discovers a substrate-honesty issue that
requires architectural acknowledgement — in which case raise it in the
completion report and propose a separate follow-up task rather than
patching architecture documents from within a discovery campaign.

---

## 9. File-Path & Module Discipline

### 9.1 Package layout

Place fixture and campaign code under `src/lloyd_v4/evals/` only if
that package does not already exist or already follows this pattern.
If the repo's existing convention puts discovery-campaign code
elsewhere (e.g., a top-level `evals/` directory, or under
`Build_Docs/Reports/<task>/`), follow the existing pattern instead and
note the location chosen in the completion report.

The rule: keep fixture/campaign code out of `tests/` (because tests
should not depend on test-internal fixtures for production-module
verification) and out of `src/lloyd_v4/primitives/` (because campaigns
are not primitives). A dedicated `evals/` package is the right home,
but the discovery task lives wherever the prior discovery campaigns
(Task 023, Task 023b) lived. Inspect that location first.

### 9.2 Import discipline

The fixture and campaign modules import from `lloyd_v4.primitives` and
`lloyd_v4.core` only. No imports from Layer 2+ V3-shape modules
(metrology, branch, refinery, history, solver). No imports of named
mathematical content (`math`, `scipy`, `mpmath`, `sympy`).

### 9.3 Determinism

Campaign output JSON must be byte-stable across runs. No timestamps in
the payload. No random ids. Numeric formatting: use the same float
serialisation V4 already uses elsewhere (no scientific-notation drift).

---

## 10. Required Tests

The test file `tests/test_task024b_schwarzschild_four_form.py` contains
the following discipline tests.

### 10.1 Pre-task evidence

```python
def test_pre_task_evidence_module_absent_before_task():
    """
    Before Task 024b, the campaign module must not exist. This test is
    deliberately fragile: it documents the pre-task state. After the
    task ships, this test asserts the module DOES exist (rename or
    update at landing).
    """
```

(In practice this is a one-shot evidence-recording test that gets
updated when the task lands.)

### 10.2 Fixture-module symbol availability

Every public symbol of the fixture module is importable and callable:
`f_of_r`, `R_of_r`, `F1_of_r`, `F2_of_r`, `F3_of_r`, `F4_of_r`,
`delta_f_of_r`, `sweep_r_values`. The sweep returns exactly 137 floats,
sorted ascending, with r_values[0] == 2.005 and r_values[-1] == 10.0.

### 10.3 V3 reference overlay agreement (the *only* place V3's table is
read)

Load `v3_reference_overlay.csv`. For each row, recompute F₁, F₂, F₃,
F₄, δf, f, R using V4's fixture module. Assert each V4-computed value
agrees with the V3 reference value to within 1 ULP (where ULP is
measured at the V3 value's magnitude; for V3 values of 0, V4 must also
be 0). If any row fails, the test fails with the row index, the
expected V3 value, the V4 value, and their ULP separation.

This is the single fixture-validation point. No other test reads the
V3 reference table.

### 10.4 Stratum pattern across the four forms

Run the campaign in-test (or load `campaign_output.json` written by a
previous campaign run within the same test session, depending on which
is faster). Assert:

- F₃: 136/136 transfer observations are `transfer_observed` with
  `transfer == 0.0`. (Document if this is not the case.)
- F₁, F₂: every transfer is one of {`transfer_observed`,
  `transfer_cancellation_dominated`} — no `transfer_non_finite`, no
  `transfer_domain_refused`, no `transfer_delta_indeterminate`.
- F₄: every transfer is one of {`transfer_observed`,
  `transfer_cancellation_dominated`}.

These are assertions on the *shape* of the strata pattern, not on
specific counts. Specific counts go in the completion report.

### 10.5 Slope-fit non-crash for non-degenerate forms

The bare-slope fit on F₄ either emits `slope_observed` or
`slope_insufficient_data` with a specific reason; it does not emit a
silent NaN or raise. The slope fit on F₃ emits one of
`slope_insufficient_data` / `slope_degenerate_input` (because the input
transfers are all zero); it does not return a numerical slope.

### 10.6 Alpha-probe reliability evidence is populated

For every form where the α-probe emits a terminal status that promises
reliability fields (per the 023b stratum-to-field mapping), the fields
are populated (not None) and self-consistent (`alpha_window_min ≤
alpha_window_max`, `alpha_window_span ≥ 0`, etc.).

### 10.7 Determinism

Run the campaign twice in-test, assert the two output JSONs are equal
byte-for-byte after sorting keys.

### 10.8 No legacy imports

Source-purity test confirming the fixture and campaign modules do not
import `numpy.linalg`, `scipy`, `sympy`, `mpmath`, `math`, or
`lloyd_v3`.

### 10.9 Manifest non-regression

The campaign adds no new exports to `lloyd_v4`. Assert
`len(lloyd_v4.primitives.__all__)` is unchanged from baseline (record
baseline in the test).

---

## 11. Required Commands

Run from `~/projects/V4/Lloyd_Engine_V4` with `.venv` activated.

```bash
# Pre-task baseline (do not start if any of these fail)
git status                                            # clean tree
python -m pytest -q tests/ 2>&1 | tail -3             # all green

# Implementation (Codex)
# ... (fixture module, campaign module, test file, report directory) ...

# Verification
python -m pytest -q tests/test_task024b_schwarzschild_four_form.py
python -m pytest -q tests/                            # full suite still green
python -m pytest -q tests/test_task001_source_purity.py   # purity audit

# Run the campaign to produce campaign_output.json
python -m lloyd_v4.evals.schwarzschild_four_form_campaign

# Verify campaign output is reproducible (run twice, diff)
python -m lloyd_v4.evals.schwarzschild_four_form_campaign \
    --output /tmp/campaign_output_repeat.json
diff Build_Docs/Reports/task024b_schwarzschild_four_form/campaign_output.json \
     /tmp/campaign_output_repeat.json

# Audit no manifest drift
python -m pytest -q \
    tests/test_task010a_layer_manifest_machine_readable.py \
    tests/test_task010b_export_drift.py \
    tests/test_task010b_manifest_completeness.py \
    tests/test_task010c_no_unregistered_operations.py \
    tests/test_task010c_lineage_terminates_in_primitive.py \
    tests/test_task010c_no_chain_cycles.py

# Commit and push (mandatory — do not skip)
git add -A
git status                                            # confirm only expected files
git commit -m "Task 024b: Schwarzschild four-form battery under V4 typed substrate"
git push origin main
```

The final commit and push are non-negotiable. Prior Codex tasks have
landed on the home machine without being pushed to GitHub, leaving the
laptop and home-machine substrates out of sync. Every task must end on
GitHub.

---

## 12. Non-Goals

The following are **out of scope** for Task 024b. Codex must not silently
implement any of them and must flag if a non-goal becomes load-bearing
for completing the task.

- **No new primitives.** No K_G computation, no bordered Hessian, no
  ∇K_G, no shape operator, no Gaussian curvature, no Hessian eigenvalue
  extraction, no rank/nullity/signature observation.
- **No multi-precision execution.** mpmath, numpy float128, decimal —
  all out. Task 017b territory.
- **No SR time dilation or Bell strain fixtures.** Those are V3
  Experiments 1c and 1d; out of scope for 024b. If 024b lands cleanly,
  natural follow-ups are 024c (SR) and 024d (Bell), each a separate
  task.
- **No 10¹⁰ ratio claim.** V4 does not assert this claim and 024b does
  not test it. The user-memory note about the cone fixture's 10¹⁰
  ratio is not part of V4's substrate-confirmed evidence.
- **No "V3 was right" / "V3 was wrong" verdicts.** V4 reports what V4
  sees. The relationship between V4's slope and V3's slope is a
  descriptive overlay, not a verdict.
- **No retry-until-it-works probe tuning.** If a probe refuses, record
  the refusal. Do not change eta, the h-grid, or the sweep schedule to
  force a different emission.
- **No K_G framework reference.** The "user memory" framing involving
  K-manifest, Gaussian curvature, intrinsic decomposition, etc., is not
  the V4 anchor. The V4 anchor for this task is the (α−1) transfer law
  per V3 Experiment 2 and the V3 transfer-function paper. Do not
  introduce K_G vocabulary anywhere.
- **No K_G ratio fixture (the original Task 024).** The original Task
  024 used a cone K_G fixture and was found to have a fixture-design
  flaw (the bordered-Hessian determinant simplified algebraically to
  16·F for that cone). Task 024b explicitly replaces that fixture with
  the V3 four-form battery. Do not import or reference the original
  Task 024 code or report.

---

## 13. Completion Report Template

`Build_Docs/Reports/task024b_summary.md` must contain:

### Scope

One paragraph describing what the task implemented and what it
deliberately did not.

### Test count

Pre-task baseline (post-023b): N tests passing.
Post-Task 024b: N + delta tests passing.

### Files changed

Bulleted list of every file created, modified, or moved.

### Stratum pattern across the four forms

A table with rows F₁, F₂, F₃, F₄ and columns:

- Transfer stratum counts (e.g., "136 × transfer_observed, 0 ×
  cancellation_dominated").
- Slope status (e.g., "slope_observed" or
  "slope_insufficient_data").
- Alpha-probe status (e.g., "alpha_regular_integer" or
  "alpha_cancellation_dominated").
- Alpha stability status (from 023b).

### Slope and α values where observed

For each form where `slope_observed` or an `alpha_*` terminal status
holds, list:

- bare slope (log|transfer| vs log|f|), R², n_used
- α-probe observed_alpha, observed_slope, R², propagated_window_error,
  alpha_window_span

### V3 overlay

A single short subsection. For F₄: V4's `F4_act / F4_pred` ratio median
and IQR across the sweep, where F4_pred follows V3's transfer law
F4_pred = δf / (2·√f). V3 reported a slope of −0.4988 on log|F₄/δf|
vs log f; V4's measurement is different in protocol and produces a
different numerical slope. State what V4 observed; do not claim or
deny agreement with V3.

### Sample serialized observations

One short JSON sample for each form's transfer-mid-sweep observation,
slope observation, and α-probe observation. (Three small JSON blocks
per form.)

### V3 fixture-validation result

Confirmation that all 137 rows of V4-computed F-values agreed with V3's
reference table to within 1 ULP. If any rows disagreed, list them
with the deltas.

### Limits

List of what 024b does not cover and what would be required to extend
it (e.g., SR fixture for 024c, denser sweep, multi-precision, etc.).

### Honest observations

Any V4 emission that did not match the design-time prediction. This is
the most important section. The whole point of a discovery campaign is
to surface what V4 actually says, not what we expected V4 to say. If
F₃ is not 100% silent, if F₄ refuses everywhere, if the α-probe's
reliability fields are inconsistent — all of that goes here, plainly.

### Audits

Final test count, source-purity audit result, manifest-non-regression
audit result, deterministic-output audit result, git commit hash, git
push confirmation.

---

## 14. Acceptance Criteria

Task 024b is complete when **all** of the following are true:

1. Pre-task baseline confirmed clean and green.
2. New fixture and campaign modules exist at the agreed paths.
3. Static V3 reference overlay table is copied into the report
   directory.
4. `tests/test_task024b_schwarzschild_four_form.py` exists and all
   tests in it pass.
5. The full test suite passes with no regressions.
6. The campaign script runs cleanly and produces a deterministic
   `campaign_output.json`.
7. The V3 fixture-validation test confirms 1-ULP agreement across all
   137 rows.
8. The completion report `task024b_summary.md` is filled out per the
   template.
9. All changes are committed and pushed to `origin/main` on
   `git@github.com:Vilhelm82/Lloyd_Engine_V4.git`.

---

## 15. Discipline Notes (Forward References)

These are out-of-scope observations that may become future tasks
depending on what Task 024b finds:

- **024c — SR time dilation four-form analog.** If 024b lands cleanly,
  the natural next is V3 Experiment 1c (SR time dilation,
  γ = 1/√(1 − v²/c²)). Same fixture pattern, different physics.
- **024d — Bell strain four-form analog.** V3 Experiment 1d. Different
  α (α = −1/2 instead of +1/2). Different sign of slope. Useful as
  α-symmetry check.
- **Future joint analysis.** Once 024b/c/d all land, a synthesis task
  could plot V4's bare slope (and V4's reliability evidence) across
  the three physical systems and compare to V3's reported (α−1)
  values jointly. This would be the V4 analog of V3 session report
  Section 4 Table 1.
- **Substrate question — value-vs-value slope primitive.** 024b uses
  `typed_log_log_slope` on transfers fitted via adjacent-r
  differences, which gives a particular bare slope (log|ΔF/Δr| vs
  log|f|). A *value-vs-value* slope primitive (fitting log|F_k(r_i)|
  vs log|f(r_i)| directly, no transfer indirection) would be a
  cleaner reproduction of V3's protocol. If 024b suggests this would
  be useful, raise it as a candidate new internal operation. Do not
  add it inside 024b.
- **Substrate question — δf as a primitive concept.** V3's protocol
  uses δf (path-roundoff residual on f) as a normaliser. V4
  currently treats δf as a fixture-level derived quantity. If the
  bare/normalised slope gap is large enough to matter, a future task
  could promote "algebraically-equivalent path residual" to a typed
  V4 observable. Do not do this inside 024b.

The point of recording these forward references is to keep them out
of the current task while still capturing the thinking. Do not draft
specs for them. Do not implement them.

---

## 16. Spec Hygiene Notes

This spec is V4-substrate-honest. It does not import V1/V3 patterns by
shape. It does not propose new primitives. It does not commit to a
slope value V4 must hit. It restricts V3 reference table usage to one
explicit assertion. Every concept used traces to existing parent
layers per Axiom 12.

If Codex finds an axiom-conflict, layer-violation, or substrate-honesty
gap while implementing this spec, halt and report. Do not paper over
it. The discipline of the V4 substrate is more important than landing
the task.

---

*End of Codex Task 024b specification.*
