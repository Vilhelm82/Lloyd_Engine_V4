# Codex Task 027 — SR Time Dilation Four-Form Battery and Cross-Fixture Comparison

## 1. Repository / Baseline

- Repo: `git@github.com:Vilhelm82/Lloyd_Engine_V4.git`, branch `main`.
- Working tree pre-task: clean. Origin/main matches local. `git log -1 --oneline` should return `780d2bb Task 026c-prime: Polarity grid stability campaign`.
- Pre-task test baseline: 471 tests passing (`pytest -q tests/`).
- Pre-task fixture modules to be consumed unchanged:
  - `src/lloyd_v4/evals/schwarzschild_four_form.py`
  - `src/lloyd_v4/evals/multi_precision_four_form.py`
  - `src/lloyd_v4/evals/lattice_anomaly_campaign.py`
  - `src/lloyd_v4/evals/polarity_grid_stability.py`

## 2. Task Goal

Apply the four-form battery, the lattice spectrum analysis, and the polarity grid stability campaign to the SR time dilation fixture. Then compare the SR results directly with the Schwarzschild results on the same battery of typed observables. The headline question this task answers:

**Are the F1/F2/F3/F4 lattice and polarity findings a property of the IEEE 754 chain (V4's stance) or a property of the Schwarzschild metric (the Kerr-leap hypothesis)?**

If SR produces structurally identical patterns (F1/F2 grid-stable parallel polarity coupling, F1/F4 depolarized invariant, F3 silent, F2 half-ULP lattice, F4 wide integer lattice, Sterbenz filtering at a shifted but predictable boundary), the chain-property hypothesis is corroborated. If SR produces qualitatively different patterns, the physics is entering and that becomes the next substrate question.

This is a **campaign task**. No new substrate primitive, no new runtime status enum, no new manifest entry, no new transition rule, no new law-library term.

## 3. Source Labelling

- **V3 reference**: V3 session report at `~/Downloads/lloyd_v3_session_report.md` documents the SR four-form battery results across 446 cells (F1: 10 non-zero / 2 levels; F2: 36 / 16 levels; F3: 0 / silent; F4: 378 / 185 levels). These are **reference evidence only** per Axiom 10 and the reference hygiene rules. V4 must derive its own results from V4-native primitives and not import V3 dicts, status enums, score functions, or tolerance bands. The V3 numbers serve as a sanity benchmark, not as targets.
- **V4-surface evidence consumed**: existing four-form battery patterns (algebraic identity, four operand-routings, F3-as-calibration-zero discipline), polarity grid stability machinery (4-grid construction, dedup discipline, classification logic).
- **Output**: per-grid, per-precision lattice and polarity tables for SR; cross-fixture comparison tables; aggregate classification per pair; headline finding statement.

## 4. Design Principles

1. **Parallel structure to Schwarzschild.** SR four-form, lattice analysis, and polarity grid stability mirror the Schwarzschild versions exactly. The point is to compare apples to apples. Same number of grid points (137), same dedup discipline, same precision split, same statistical thresholds.
2. **Different operand, same chain.** The four SR forms use β (velocity / c) and η = √(1−β²) where Schwarzschild used r and R = √(1−2/r). The chain structure (sqrt of near-1 quantity, squared, subtracted via different routings) is parallel; only the input variable name and definition change.
3. **F3 sentinel is loud.** F3_SR = η − √(1−β²) is the same path on both sides; must be identically zero on every grid at every precision. If F3_SR ever fires, halt and flag — substrate has changed.
4. **Sterbenz boundary shifts predictably.** Schwarzschild's F2 first-step Sterbenz boundary was r ≥ 4M (where R² = 1−2/r ≥ 1/2). SR's analogous boundary is β ≤ 1/√2 (where η² = 1−β² ≥ 1/2). The spec must record whether the empirical F2_SR firing density tracks this predicted boundary shift; this is a falsifiable prediction of the chain-property hypothesis.
5. **Negative control discipline preserved.** F1_F4_SR must aggregate to `depolarized_invariant` (or `open_underpowered` if cofires < 10 on enough grids). If F1_F4_SR shows significant polarity coupling on any grid, that flags `negative_control_failed` for the SR fixture and is a real finding.
6. **Bottle-cap discipline preserved.** F2_F4_SR cannot aggregate to `grid_stable_polarity_coupling` unless all four grids produce cofire ≥ 10.
7. **Cross-fixture comparison is descriptive, not evaluative.** The comparison tables report what Schwarzschild and SR produced side-by-side. The interpretation (chain-property vs physics-property) is in the summary prose, not in a quantitative score.

## 5. Primitive-Sufficiency Gate

| Concept used in this task | Origin | Layer |
|---|---|---|
| SR four-form values (float32, float64, decimal-50) | new eval module `lloyd_v4.evals.sr_four_form`, mirrors `multi_precision_four_form.py` | eval |
| β-grid construction | new module, mirrors `schwarzschild_four_form.sweep_r_values` pattern | eval |
| Lattice level computation | reuse `lattice_anomaly_campaign._lattice_for_form_precision` if importable, else mirror its logic | eval |
| Polarity classification | reuse `polarity_grid_stability.classify_pair` and grid-construction utilities, parameterized by fixture | eval |
| Cross-fixture comparison | new function, reads both fixtures' campaign outputs and emits combined tables | eval |
| `decimal.Decimal` | stdlib, admitted | eval |
| `numpy.float32`, `numpy.float64` | admitted as type containers | eval |
| `math.comb` for binomial p-values | stdlib, admitted | eval |
| `random.Random(seed)` | stdlib, admitted | eval |

**No new substrate primitive. No new runtime status enum. The existing report-status vocabulary from Task 026c-prime is reused unchanged.**

## 6. Required Deliverables

### 6.1 SR Four-Form Module

New file: `src/lloyd_v4/evals/sr_four_form.py`.

Public surface (mirrors `schwarzschild_four_form.py` + `multi_precision_four_form.py`):

```python
def beta_grid() -> tuple[float, ...]:
    """Return the canonical SR β-grid: 137 linearly-spaced points in [0.01, 0.9999]."""

def eta_of_beta(beta: float) -> float:
    """η = sqrt(1 - β²) computed in float64."""

def F1_of_beta(beta: float) -> float:
    """F1 = η² + β² − 1, computed as written (η computed first, then squared, then added to β², then subtracted from 1)."""

def F2_of_beta(beta: float) -> float:
    """F2 = η² − 1 + β², computed as written (η computed first, squared, subtracted from 1, then β² added)."""

def F3_of_beta(beta: float) -> float:
    """F3 = η − sqrt(1 − β²) — same path twice, calibration zero."""

def F4_of_beta(beta: float) -> float:
    """F4 = η − sqrt((1 − β) * (1 + β)) — algebraically equal sqrts via different operand routings."""

def four_form_float32(beta: float) -> dict[str, float]: ...
def four_form_float64(beta: float) -> dict[str, float]: ...
def four_form_decimal_oracle(beta: float, precision: int = 50) -> dict[str, float]: ...
```

**Critical: the float32 and float64 implementations must compute each form using exactly the operand-routing implied by the algebraic expression, not a refactored form.** For example, F2 must compute `(η² − 1) + β²` (parenthesised), not `(η² + β²) − 1` (different routing). This is what makes the four forms distinguishable.

### 6.2 SR Lattice Analysis Module

New file: `src/lloyd_v4/evals/sr_lattice_campaign.py`.

Mirrors `lattice_anomaly_campaign.py` Sub-module A (per-form, per-precision lattice level analysis) for SR. Same status families and table schema. Reports `n_distinct_levels`, `level_integer_residual_max`, `level_histogram`, `regional_distinct_level_counts` per (form, precision).

Region cutoffs for SR are velocity-based:
- `non_relativistic` (analog of `far`): β < 0.5
- `mildly_relativistic` (analog of `middle`): 0.5 ≤ β < 0.9
- `ultra_relativistic` (analog of `near`): β ≥ 0.9

The naming is fixture-specific because the velocity-coordinate interpretation differs from the radial-coordinate interpretation. Both correspond to "approaching the branch point" in their respective fixtures.

### 6.3 SR Polarity Grid Stability Module

New file: `src/lloyd_v4/evals/sr_polarity_grid_stability.py`.

Mirrors `polarity_grid_stability.py` for the SR fixture. Four grids:

1. **`reference`** — seed=0, the canonical 137-point β-grid from `beta_grid()`. `n_after_dedup` must equal 137.
2. **`coarse_perturbation`** — seed=1042, `β_i * (1 + 0.05 * Uniform[-1, 1])` clamped to [0.01, 0.9999], sorted, deduplicated with the same `2 * ulp(max)` rule as 026c-prime.
3. **`fine_perturbation`** — seed=2317, factor 1e-4, same clamping and dedup.
4. **`independent_uniform`** — seed=4099, 137 samples drawn from Uniform(0.01, 0.9999), sorted, deduplicated.

The seeds are reused from 026c-prime intentionally — the question is whether the same seeds produce structurally similar patterns when the fixture changes.

Polarity classification logic is **identical** to 026c-prime: same five promotion criteria, same `underpowered_grid` threshold (cofire < 10), same `negative_control_failed` discipline for F1/F4, same `bottle-cap` guard for F2/F4. Same report statuses.

### 6.4 Cross-Fixture Comparison Module

New file: `src/lloyd_v4/evals/cross_fixture_comparison.py`.

Reads both fixtures' campaign outputs (Schwarzschild from Task 026c-prime, SR from this task) and emits a comparison report.

Public surface:

```python
def load_fixture_results(fixture: str) -> dict:
    """Load the polarity grid stability output for 'schwarzschild' or 'sr'."""

def compare_fixtures() -> dict:
    """Return cross-fixture comparison payload with sections:
       - per_pair_aggregate_comparison
       - per_grid_per_precision_comparison
       - lattice_grain_comparison
       - sterbenz_boundary_comparison
       - headline_finding
    """

def write_comparison_output(path: Path = DEFAULT_OUTPUT) -> dict: ...
def main() -> None: ...
```

The comparison output must be **descriptive, not evaluative**. Side-by-side tables for each observable; no score, no "winner". The interpretation prose in the README discusses what the comparison implies for the chain-property hypothesis, but the JSON/CSV outputs are pure data.

### 6.5 Reports Directory

```
Build_Docs/Reports/task027_sr_four_form_cross_fixture/
    sr_four_form_battery.json          # SR analog of task024b output
    sr_lattice_campaign_output.json    # SR analog of task026 output
    sr_polarity_grid_stability.json    # SR analog of task026c_prime output
    sr_polarity_grid_table.csv
    sr_region_split_table.csv
    sr_precision_overlap_table.csv
    cross_fixture_comparison.json
    cross_fixture_per_pair_table.csv
    cross_fixture_lattice_grain_table.csv
    cross_fixture_sterbenz_boundary_table.csv
    README.md
Build_Docs/Reports/task027_summary.md
```

### 6.6 Sterbenz Boundary Verification

The cross-fixture comparison must include explicit verification of the Sterbenz prediction:

- Schwarzschild: F2 first-step Sterbenz boundary at r ≥ 4 (where R² = 1 − 2/r ≥ 1/2). Predicted F2 firing density should be higher at r ≥ 4 than at r < 4.
- SR: F2 first-step Sterbenz boundary at β ≤ 1/√2 ≈ 0.7071 (where η² = 1 − β² ≥ 1/2). Predicted F2 firing density should be higher at β ≤ 1/√2 than at β > 1/√2.

The Sterbenz boundary table reports F2 firing count above and below the predicted boundary for each fixture. If both fixtures show the predicted directional bias, that's evidence the Sterbenz mechanism generalises. If only Schwarzschild does, the mechanism is fixture-specific.

## 7. Required Tests

New test file: `tests/test_task027_sr_four_form_cross_fixture.py`.

Required tests:

1. **`test_beta_grid_deterministic_and_bounded`**: `beta_grid()` returns exactly 137 strictly-increasing values in [0.01, 0.9999], reproducible across calls.
2. **`test_F3_sr_is_identically_zero`**: across all 137 β-values at float32, float64, AND decimal-50, F3_SR == 0.0 exactly. FAILS LOUDLY if any nonzero. This is the calibration zero sentinel.
3. **`test_sr_four_form_byte_stable`**: two consecutive runs of the SR four-form battery produce identical JSON.
4. **`test_sr_lattice_campaign_schema`**: SR lattice analysis output has the same schema as Task 026 lattice campaign (same keys, same structure).
5. **`test_sr_polarity_grids_deterministic`**: each of the four SR grids is reproducible from its seed; identical r_values between two consecutive constructions.
6. **`test_sr_polarity_grids_clamped_and_deduped`**: every β-value in every grid satisfies 0.01 ≤ β ≤ 0.9999; no two consecutive values within `2 * ulp(max)`.
7. **`test_sr_negative_control_f1_f4`**: SR's F1/F4 aggregate must be `depolarized_invariant` or `open_underpowered`. FAILS LOUDLY if `negative_control_failed`.
8. **`test_sr_f2_f4_bottle_cap_guard`**: if any grid has F2/F4 cofire < 10, the F2/F4 aggregate must NOT be `grid_stable_polarity_coupling`.
9. **`test_sr_polarity_byte_stable`**: SR polarity grid stability campaign output is byte-stable across runs.
10. **`test_cross_fixture_comparison_byte_stable`**: cross-fixture comparison output is byte-stable across runs.
11. **`test_cross_fixture_comparison_schema`**: comparison JSON contains all required sections (per_pair_aggregate_comparison, lattice_grain_comparison, sterbenz_boundary_comparison, headline_finding).
12. **`test_sterbenz_boundary_table_schema`**: each fixture row contains f2_count_above_boundary, f2_count_below_boundary, predicted_direction, observed_direction, supports_prediction (bool).
13. **`test_no_runtime_status_enum_additions`**: `StatusCode` membership is unchanged after importing all new modules.
14. **`test_no_law_library_term_added`**: Task 025 law library candidate list is unchanged.
15. **`test_no_manifest_changes`**: `layer_manifest.json` and `LAYER_MANIFEST.md` are unchanged from pre-task hashes.
16. **`test_sr_p_value_exact_check`**: known-input check — for cofire=20, same_sign=20, `p_one_tail_upper` must equal `2**-20` exactly.

## 8. Required Commands

In completion report:

```bash
# Baseline confirmation
git log -1 --oneline
python -m pytest -q tests/

# Module import sanity
PYTHONPATH=src python -c "from lloyd_v4.evals.sr_four_form import four_form_float64, beta_grid; print(beta_grid()[:3], beta_grid()[-3:])"
PYTHONPATH=src python -c "from lloyd_v4.evals.sr_polarity_grid_stability import run_campaign; print(sorted(run_campaign().keys()))"
PYTHONPATH=src python -c "from lloyd_v4.evals.cross_fixture_comparison import compare_fixtures; print(sorted(compare_fixtures().keys()))"

# Run all SR campaigns and verify byte-stable
PYTHONPATH=src python -m lloyd_v4.evals.sr_polarity_grid_stability
PYTHONPATH=src python -m lloyd_v4.evals.sr_polarity_grid_stability --output /tmp/sr_polarity_repeat.json
diff Build_Docs/Reports/task027_sr_four_form_cross_fixture/sr_polarity_grid_stability.json /tmp/sr_polarity_repeat.json

PYTHONPATH=src python -m lloyd_v4.evals.cross_fixture_comparison
PYTHONPATH=src python -m lloyd_v4.evals.cross_fixture_comparison --output /tmp/cross_fixture_repeat.json
diff Build_Docs/Reports/task027_sr_four_form_cross_fixture/cross_fixture_comparison.json /tmp/cross_fixture_repeat.json

# Task-specific tests
python -m pytest -q tests/test_task027_sr_four_form_cross_fixture.py

# Full suite
python -m pytest -q tests/

# Source purity audit
python -m pytest -q tests/test_task001_source_purity.py

# Manifest audits
python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py

# Forbidden-import grep (expected: zero matches)
rg "numpy\.random|np\.random|scipy|sympy|mpmath" src/lloyd_v4/evals/sr_four_form.py src/lloyd_v4/evals/sr_lattice_campaign.py src/lloyd_v4/evals/sr_polarity_grid_stability.py src/lloyd_v4/evals/cross_fixture_comparison.py
```

## 9. Non-Goals (explicit)

1. **No new substrate primitive.**
2. **No new runtime status enum.**
3. **No new manifest entries.**
4. **No new transition rule.**
5. **No new law-library term.**
6. **No promotion to substrate even on full pass.** Successful chain-property confirmation licenses a *future* substrate task; it does not itself promote anything.
7. **No solver behavior changes.**
8. **No new physics fixtures beyond SR.** Bell strain, RN, QM⊕GR, etc. are NOT part of this task. Task 028 (if commissioned) will handle Bell.
9. **No retroactive changes to Schwarzschild campaign outputs.** The Schwarzschild data from Tasks 024b/026/026c-prime is read-only; this task adds the SR analogs alongside, never modifies the existing reports.
10. **No `numpy.random` global state.** Use `random.Random(seed)`.
11. **No use of `math.pi`, `math.e`, `math.tau`, or any other named mathematical constant** (Axiom 11).
12. **No Kerr, no rotational shear, no frame-dragging analogies in the README or summary prose.** This task tests the chain-property vs physics-property dichotomy; speculative cross-metric interpretations are explicitly out of scope.

## 10. Completion Report

`Build_Docs/Reports/task027_summary.md` must contain:

- Scope statement (the chain-property vs physics-property question).
- Pre-task baseline confirmation (commit hash, test count = 471).
- Test results (new test count, full suite count).
- Files changed list.
- SR β-grid summary.
- SR four-form per-form non-zero counts and distinct-level counts (compared with V3 reference: F1 2 levels, F2 ~16 levels, F3 silent, F4 ~185 levels).
- SR lattice campaign findings (per-form, per-precision).
- SR polarity grid stability headline (per pair: aggregate status, cofire totals across grids, key p-values).
- Cross-fixture comparison summary: side-by-side per-pair aggregates, lattice grain comparison, Sterbenz boundary verification table.
- Negative control verification (F1/F4 SR aggregates to `depolarized_invariant`).
- Bottle-cap discipline verification (F2/F4 SR not promoted unless all grids cofire ≥ 10).
- Byte-stability verification for both campaigns and the cross-fixture comparison.
- **Headline finding** stated in one of these explicit forms:
  - `chain_property_supported`: SR produces structurally identical patterns to Schwarzschild on all measured observables (F1/F2 grid-stable parallel polarity, F1/F4 depolarized invariant, F3 silent, F2 half-ULP lattice, F4 wide integer lattice, Sterbenz boundary tracks predicted shift). Both fixtures' classifications and observables agree within statistical noise.
  - `chain_property_partial`: SR matches Schwarzschild on most observables but diverges on one or more specific items (named explicitly). Evidence is mixed.
  - `chain_property_rejected`: SR produces qualitatively different patterns from Schwarzschild on the F1/F2 polarity, lattice grain, or Sterbenz behavior. Physics-property hypothesis warrants further investigation.
- Honest observations: any surprises, any V3-reference disagreements, any unexpected grid behavior.
- Limits: SR fixture only; no Bell, no pure algebraic control, no other physics.
- Forward references: Task 028 (Bell strain), Task 029 (pure algebraic control — the cleanest test, with no physics), Task 030 (cross-fixture synthesis).

## 11. Acceptance Criteria

- All 16 required tests pass.
- Full pytest suite count == 471 + 16 == 487 (report exact number; flag if Codex adds additional tests).
- Byte-stable SR polarity output verified.
- Byte-stable cross-fixture comparison output verified.
- No additions to `StatusCode` enum.
- No modifications to `layer_manifest.json` or `LAYER_MANIFEST.md`.
- No imports of `numpy.random`, `scipy`, `sympy`, `mpmath`, or `math`-named-constants in the new modules.
- `tests/test_task001_source_purity.py` passes.
- All manifest-audit tests pass.
- Headline classification is one of `chain_property_supported`, `chain_property_partial`, or `chain_property_rejected`. The classification reflects the data; the task does not pre-decide which outcome.
- F1/F4 SR aggregate is `depolarized_invariant` or `open_underpowered`; `negative_control_failed` triggers `test_sr_negative_control_f1_f4` to fail loudly.
- F2/F4 SR aggregate is NOT `grid_stable_polarity_coupling` unless all four grids have cofire ≥ 10.
- F3_SR is identically zero everywhere; `test_F3_sr_is_identically_zero` fails loudly otherwise.

## 12. Discipline Notes

1. **The conclusion follows from the data.** The hypothesis (chain-property) has a specific prediction (SR mirrors Schwarzschild). If SR mirrors Schwarzschild, report `chain_property_supported`. If it doesn't, report the divergence honestly. Don't shade the result toward the hypothesis.

2. **F3 sentinel is loud across BOTH fixtures.** F3_Schwarzschild remained zero through every prior campaign; F3_SR must do the same here. If either F3 fires, halt and flag.

3. **Negative control is loud.** F1/F4 should be `depolarized_invariant` in SR just as it is in Schwarzschild. If SR produces a `grid_stable_supported` F1/F4 anywhere, that flags the entire analysis framework as too permissive, not as a finding about SR.

4. **No physics interpretations in the prose.** The task documents what the data shows: lattice grain X, polarity coupling Y, Sterbenz boundary at predicted location. It does NOT interpret these in terms of relativistic mechanics, lightspeed barriers, branch points of sqrt, or any physics framing beyond "Sterbenz Lemma applies where it applies." Physics interpretation is out of scope; this task tests whether the chain pattern survives the fixture change.

5. **Cross-fixture comparison is descriptive.** The comparison tables show Schwarzschild and SR side-by-side. They do not declare one fixture "right" or one observable "more important." The headline finding draws the conclusion from the totality of observables; the per-row data is just data.

6. **V3 reference hygiene.** V3's SR session report is read-only reference for sanity-checking V4's results. V4 must derive its values, status families, and classifications from V4-native primitives. V3 non-zero counts (10, 36, 0, 378) are sanity benchmarks, not targets. If V4 produces different non-zero counts, that's a finding — could be a real divergence, could be a 137-vs-446 cell count difference, could be a grid-construction difference. Report and investigate.

7. **The Kerr leap is explicitly NOT this task.** If the headline finding is `chain_property_supported`, that retires the physics-property hypothesis at the SR-Schwarzschild comparison level. It does NOT confirm or deny anything about Kerr, rotation, frame dragging, or any other cross-metric speculation. The next legitimate substrate question after this task is "do other physics fixtures (Bell) and pure algebraic controls also conform?", not "is Kerr in the lattice?".

8. **End-of-task git discipline (non-negotiable).**

```bash
git add -A
git status
git commit -m "Task 027: SR four-form battery and cross-fixture comparison"
git push origin main
```

The commit MUST land on origin/main before the task is considered closed. The completion summary MUST include the commit hash and confirmation that `git status` returned clean.
