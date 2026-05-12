# Codex Task 028 — Conditional Masks, Joint Signed-Lattice, and Pure Algebraic Four-Form Control

## 1. Repository / Baseline

- Repo: `git@github.com:Vilhelm82/Lloyd_Engine_V4.git`, branch `main`.
- Working tree pre-task: clean. Origin/main matches local. `git log -1 --oneline` should return `75a12b0 Task 027: SR four-form battery and cross-fixture comparison`.
- Pre-task test baseline: 487 tests passing (`pytest -q tests/`).
- Pre-task data consumed unchanged:
  - `Build_Docs/Reports/task026c_prime_polarity_grid_stability/campaign_output.json` (Schwarzschild polarity)
  - `Build_Docs/Reports/task027_sr_four_form_cross_fixture/sr_polarity_grid_stability.json` (SR polarity)
  - `Build_Docs/Reports/task024b_schwarzschild_four_form/campaign_output.json` (Schwarzschild four-form values)
  - existing eval modules under `src/lloyd_v4/evals/` consumed read-only

## 2. Task Goal

Three sub-objectives, executed and reported together in a single Task 028 commit:

**Sub-objective A — Conditional mask decomposition.** The "F2 is a Sterbenz-filtered subset of F1" hypothesis was contradicted by Task 027's SR results: F2 fires *more* than F1 on every SR grid at every precision, and on Schwarzschild's `independent_uniform` grid. The simple subset model is wrong. The sharper model — F1 and F2 measure rounding from *different* parts of the chain that happen to share dominant R²/η² rounding direction at overlap — needs typed evidence. Tabulate per (fixture, grid, precision):

```
P(F2 fires | F1 fires)
P(F1 fires | F2 fires)
F1-only event count
F2-only event count
co-fire event count
```

Plus the analogous decomposition for F1/F4 and F2/F4.

**Sub-objective B — Joint signed-lattice histogram.** Sign and lattice level have been analysed separately. Build the joint distribution per fixture: `(level_F1, level_F2, level_F4, sign_F1, sign_F2, sign_F4)` over all r/β values. Test whether the 100% F1∥F2 sign coupling decomposes further when conditioned on lattice level. For example, does F1 at level +1 always co-occur with F2 at a specific subset of half-integer levels? Does F4's lattice level correlate with the F1/F2 polarity state? The joint object may carry structure that neither sign nor lattice alone reveals.

**Sub-objective C — Pure algebraic four-form fixture.** Define a four-form battery with no physics in the operand: a uniform x-grid in [0.01, 0.99], where the algebraic identity is the same shape (sqrt of near-1 quantity, squared, subtracted via different routings) but the operand carries no physical interpretation. Run the same lattice analysis and polarity grid stability campaign. Compare against Schwarzschild and SR in a three-fixture comparison.

The headline question this task answers: **does the chain-property survive the removal of all physics from the operand, AND does the joint signed-lattice state reveal structure that pure sign or pure lattice analysis missed?**

This is a campaign and analysis task. No new substrate primitive, no new runtime status enum, no manifest changes, no law-library term.

## 3. Source Labelling

- **V4-surface evidence**: Existing Task 026c-prime Schwarzschild polarity output; Task 027 SR polarity output; Task 024b/027 four-form value tables.
- **No V3 reference for pure algebraic.** Pure algebraic has no V3 analog (V3 ran physics fixtures only). The pure-algebraic results are V4-native by definition.
- **Output**: per-fixture conditional mask tables; per-fixture joint signed-lattice histograms; pure-algebraic four-form values and full battery; three-fixture cross-comparison.

## 4. Design Principles

1. **A and B are pure analysis tasks on existing data.** No new four-form campaigns for Schwarzschild or SR. Read the existing campaign outputs, derive the new typed observables, emit new tables. Existing campaign outputs are byte-frozen; this task does NOT modify them.
2. **C is a new fixture with the full Task 026c-prime polarity battery applied.** Same four-grid structure (reference + coarse + fine + independent), same dedup discipline, same classification logic, same negative-control discipline.
3. **F3 sentinel preserved across all three sub-objectives.** Pure algebraic's F3 must remain identically zero across all precisions. If F3 ever fires in any fixture, halt and flag.
4. **Negative control preserved.** F1/F4 in pure algebraic must aggregate to `depolarized_invariant` or `open_underpowered`. If pure algebraic produces a `grid_stable_supported` F1/F4 on any grid, that flags `negative_control_failed` and is a campaign-level finding to investigate, not a polarity-coupling success.
5. **Bottle-cap discipline preserved.** F2/F4 in pure algebraic cannot reach `grid_stable_polarity_coupling` unless all four grids produce cofire ≥ 10.
6. **Joint signed-lattice histogram is descriptive.** Build the histogram, report it, point at any conditional structure it reveals. Do not promote the joint state to a runtime substrate primitive; that is a future task IF the histogram reveals a structural law.
7. **Conditional masks complete the F1/F2 mechanism characterization.** The verbal model "F1 and F2 measure different parts of the chain that share dominant rounding direction at overlap" makes specific predictions: F2-only events should exist in measurable numbers, F1-only events should exist in measurable numbers, and the co-fire subset should be where the polarity coupling lives.

## 5. Primitive-Sufficiency Gate

| Concept used in this task | Origin | Layer |
|---|---|---|
| Pure algebraic four-form values (float32, float64, decimal-50) | new module `lloyd_v4.evals.pure_algebraic_four_form`, mirrors `multi_precision_four_form.py` shape | eval |
| Conditional mask computation | new module, pure data analysis on existing campaign JSON | eval |
| Joint signed-lattice histogram | new module, pure data analysis on existing campaign JSON | eval |
| x-grid construction | new module, mirrors `schwarzschild_four_form.sweep_r_values` pattern | eval |
| Lattice level computation | reuse from `lattice_anomaly_campaign` or mirror | eval |
| Polarity classification | reuse `polarity_grid_stability.classify_pair` logic | eval |
| Three-fixture comparison | extends `cross_fixture_comparison.py` to handle three fixtures | eval |
| `random.Random(seed)` | stdlib, admitted | eval |
| `math.comb` | stdlib, admitted | eval |
| `decimal.Decimal` | stdlib, admitted | eval |
| `numpy.float32`, `numpy.float64` | admitted as type containers | eval |

**No new substrate primitive. No new runtime status enum. No imports of `numpy.random`, `scipy`, `sympy`, `mpmath`, or `math`-named-constants in new code.**

## 6. Required Deliverables

### 6.1 Conditional Mask Module (Sub-objective A)

New file: `src/lloyd_v4/evals/conditional_mask_analysis.py`.

Public surface:

```python
def compute_conditional_masks(fixture: str, grid: str, precision: str) -> dict:
    """
    For one (fixture, grid, precision), compute the conditional event decomposition:
    Return {
        "fixture": ...,
        "grid": ...,
        "precision": ...,
        "n_cells": int,
        "pairs": {
            "F1_F2": {
                "F1_fires": int,
                "F2_fires": int,
                "cofire": int,
                "F1_only": int,           # F1 fires AND F2 silent
                "F2_only": int,           # F2 fires AND F1 silent
                "neither": int,
                "p_F2_given_F1": float | None,    # cofire / F1_fires
                "p_F1_given_F2": float | None,    # cofire / F2_fires
                "asymmetry_ratio": float | None,  # F2_only / F1_only (where defined)
                "cofire_same_sign": int,
                "cofire_opposite_sign": int,
            },
            "F1_F4": { ... same schema ... },
            "F2_F4": { ... same schema ... },
        },
    }
    """

def run_conditional_mask_campaign(fixtures: list[str] = ("schwarzschild", "sr")) -> dict:
    """Iterate over all (fixture, grid, precision) combinations and emit the full table."""

def write_conditional_mask_output(path: Path) -> dict: ...
def main() -> None: ...
```

Reads existing campaign outputs; does NOT regenerate them. The conditional masks are derived from the same sign sequences and four-form values already in the JSON files.

### 6.2 Joint Signed-Lattice Module (Sub-objective B)

New file: `src/lloyd_v4/evals/joint_signed_lattice_analysis.py`.

Public surface:

```python
def compute_joint_signed_lattice_histogram(fixture: str, precision: str) -> dict:
    """
    For one (fixture, precision), build the joint distribution over (level, sign) tuples:
    Return {
        "fixture": ...,
        "precision": ...,
        "n_cells": int,
        "joint_states": [
            {
                "state_key": "L1=+1,L2=+0.5,L4=+8,S1=+,S2=+,S4=+",
                "count": int,
                "fraction": float,
                "example_indices": [int, ...],   # first few cell indices producing this state
            },
            ...
        ],
        "marginals": {
            "by_F1_level": {level: count, ...},
            "by_F2_level": {level: count, ...},
            "by_F4_level": {level: count, ...},
            "by_polarity_state": {"all_silent": int, "F1F2_aligned_F4_silent": int, ...},
        },
        "conditional_summaries": {
            "F2_level_given_F1_plus1": {level: count, ...},
            "F2_level_given_F1_minus1": {level: count, ...},
            "F1F2_polarity_given_F4_level_band": {band: {"aligned": int, "opposed": int}, ...},
        },
    }
    """

def run_joint_lattice_campaign(fixtures: list[str] = ("schwarzschild", "sr")) -> dict:
    """Iterate over all (fixture, precision) combinations on reference grid."""

def write_joint_lattice_output(path: Path) -> dict: ...
def main() -> None: ...
```

### 6.3 Pure Algebraic Four-Form Module (Sub-objective C)

New file: `src/lloyd_v4/evals/pure_algebraic_four_form.py`.

Public surface:

```python
def x_grid() -> tuple[float, ...]:
    """Canonical pure-algebraic x-grid: 137 linearly-spaced points in [0.01, 0.99]."""

def f_of_x(x: float) -> float:
    """f = 1 - x, direct routing."""

def f_of_x_split_routing(x: float) -> float:
    """f via split routing: (1 - x/2) - x/2. Algebraically equal to f_of_x."""

def R_of_x(x: float) -> float:
    """R = sqrt(1 - x), computed via direct routing."""

def F1_of_x(x: float) -> float:
    """F1 = R^2 - (1 - x). Ratio computed once, squared, subtracted."""

def F2_of_x(x: float) -> float:
    """F2 = R^2 - 1 + x. Squared form, two-step subtract."""

def F3_of_x(x: float) -> float:
    """F3 = R - sqrt(1 - x). SAME path twice; calibration zero."""

def F4_of_x(x: float) -> float:
    """F4 = R - sqrt(f_via_split_routing). Two algebraically-identical sqrts via different operand routings."""

def four_form_float32(x: float) -> dict[str, float]: ...
def four_form_float64(x: float) -> dict[str, float]: ...
def four_form_decimal_oracle(x: float, precision: int = 50) -> dict[str, float]: ...
```

**Critical: each form must compute through its declared operand routing in float32 and float64, not refactored.** F4 explicitly uses `f_of_x_split_routing` (the (1 - x/2) - x/2 path), not `f_of_x`. This is what makes F4 distinct from F3.

### 6.4 Pure Algebraic Lattice Campaign

New file: `src/lloyd_v4/evals/pure_algebraic_lattice_campaign.py`.

Mirrors `sr_lattice_campaign.py` for the pure algebraic fixture. Region cutoffs:

- `small_x` (analog of `non_relativistic`): x < 0.25
- `mid_x` (analog of `mildly_relativistic`): 0.25 ≤ x < 0.75
- `large_x` (analog of `ultra_relativistic`): x ≥ 0.75

The Sterbenz boundary prediction for pure algebraic's F2 first-step (R² ⊖ 1 exact when R² ≥ 0.5, i.e., 1 - x ≥ 0.5, i.e., x ≤ 0.5) is in the middle of the sweep.

### 6.5 Pure Algebraic Polarity Grid Stability

New file: `src/lloyd_v4/evals/pure_algebraic_polarity_grid_stability.py`.

Mirrors `sr_polarity_grid_stability.py` for pure algebraic. Four grids:

1. **`reference`** — seed=0, the canonical 137-point x-grid from `x_grid()`. `n_after_dedup` must equal 137.
2. **`coarse_perturbation`** — seed=1042, `x_i * (1 + 0.05 * Uniform[-1, 1])` clamped to [0.01, 0.99], sorted, deduplicated.
3. **`fine_perturbation`** — seed=2317, factor 1e-4, same clamping and dedup.
4. **`independent_uniform`** — seed=4099, 137 samples drawn from Uniform(0.01, 0.99), sorted, deduplicated.

Same seeds as Schwarzschild and SR. Same five-criterion promotion gate.

### 6.6 Three-Fixture Comparison Extension

Modify `src/lloyd_v4/evals/cross_fixture_comparison.py` to handle THREE fixtures (schwarzschild, sr, pure_algebraic). The schema extends naturally — same comparison tables but with three columns instead of two. Backwards compatibility: if pure_algebraic data isn't present, the comparison falls back to two-fixture mode.

Update the headline-classification logic for three fixtures:

- `chain_property_supported`: all three fixtures agree on F1/F2 (grid-stable polarity coupling), F3 (silent), F2 lattice grain (half-integer), F4 lattice character (integer), Sterbenz boundary (predicted direction). Pure algebraic acts as the cleanest test; if it agrees with both physics fixtures, the chain-property hypothesis is corroborated at the substrate level.
- `chain_property_partial`: some invariants preserved across all three, others diverge. Specific divergences named.
- `chain_property_rejected`: pure algebraic produces qualitatively different patterns from Schwarzschild and SR on the substrate-level features. Would indicate that the physics fixtures share structure that bare algebra lacks.

### 6.7 Reports Directory

```
Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/
    conditional_mask_output.json
    conditional_mask_table.csv
    joint_signed_lattice_output.json
    joint_signed_lattice_table.csv
    pure_algebraic_four_form_battery.json
    pure_algebraic_lattice_campaign_output.json
    pure_algebraic_polarity_grid_stability.json
    pure_algebraic_polarity_grid_table.csv
    pure_algebraic_region_split_table.csv
    pure_algebraic_precision_overlap_table.csv
    three_fixture_comparison.json
    three_fixture_per_pair_table.csv
    three_fixture_lattice_grain_table.csv
    three_fixture_sterbenz_boundary_table.csv
    README.md
Build_Docs/Reports/task028_summary.md
```

## 7. Required Tests

New test file: `tests/test_task028_conditional_masks_joint_lattice_pure_algebraic.py`.

Required tests:

1. **`test_conditional_mask_schema`**: every (fixture, grid, precision) entry has the full pair schema with all required keys.
2. **`test_conditional_mask_counts_consistency`**: for each pair, `F1_fires + F2_only = F2_fires + F1_only` (basic set algebra holds); cofire + F1_only + F2_only + neither = n_cells.
3. **`test_conditional_mask_byte_stable`**: two consecutive runs produce identical output.
4. **`test_joint_signed_lattice_schema`**: every (fixture, precision) entry has joint_states, marginals, conditional_summaries.
5. **`test_joint_signed_lattice_marginals_sum_to_total`**: marginals across all levels per form sum to n_cells.
6. **`test_joint_signed_lattice_byte_stable`**: two consecutive runs produce identical output.
7. **`test_x_grid_deterministic_and_bounded`**: pure algebraic x-grid is 137 strictly-increasing values in [0.01, 0.99], reproducible.
8. **`test_F3_pure_algebraic_identically_zero`**: across all 137 x-values at float32, float64, AND decimal-50, F3 == 0.0 exactly. FAILS LOUDLY otherwise.
9. **`test_pure_algebraic_four_form_byte_stable`**: pure algebraic four-form battery output is byte-stable across runs.
10. **`test_pure_algebraic_polarity_grids_deterministic`**: each of the four pure algebraic grids is reproducible from its seed.
11. **`test_pure_algebraic_polarity_grids_clamped_and_deduped`**: every x-value in every grid satisfies 0.01 ≤ x ≤ 0.99; no two consecutive values within `2 * ulp(max)`.
12. **`test_pure_algebraic_negative_control_F1_F4`**: pure algebraic F1/F4 aggregate must be `depolarized_invariant` or `open_underpowered`. FAILS LOUDLY if `negative_control_failed`.
13. **`test_pure_algebraic_F2_F4_bottle_cap_guard`**: if any grid has F2/F4 cofire < 10, aggregate must NOT be `grid_stable_polarity_coupling`.
14. **`test_pure_algebraic_polarity_byte_stable`**: pure algebraic polarity campaign output is byte-stable.
15. **`test_three_fixture_comparison_byte_stable`**: three-fixture comparison output is byte-stable.
16. **`test_three_fixture_comparison_schema`**: comparison JSON contains all required sections including pure_algebraic columns and three-fixture headline classification.
17. **`test_sterbenz_boundary_three_fixtures`**: each fixture row has boundary value (4.0 Schwarzschild, 1/√2 SR, 0.5 pure algebraic), below/above counts, supports_prediction bool. Pure algebraic boundary at exactly 0.5.
18. **`test_no_runtime_status_enum_additions`**: `StatusCode` membership unchanged after importing new modules.
19. **`test_no_law_library_term_added`**: Task 025 law library candidates unchanged.
20. **`test_no_manifest_changes`**: `layer_manifest.json` and `LAYER_MANIFEST.md` unchanged.
21. **`test_existing_campaign_outputs_unchanged`**: Schwarzschild Task 026c-prime and SR Task 027 campaign output JSON files have unchanged byte hashes after running this task.

## 8. Required Commands

```bash
# Baseline confirmation
git log -1 --oneline
python -m pytest -q tests/

# Conditional mask analysis
PYTHONPATH=src python -m lloyd_v4.evals.conditional_mask_analysis
PYTHONPATH=src python -m lloyd_v4.evals.conditional_mask_analysis --output /tmp/conditional_mask_repeat.json
diff Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/conditional_mask_output.json /tmp/conditional_mask_repeat.json

# Joint signed-lattice analysis
PYTHONPATH=src python -m lloyd_v4.evals.joint_signed_lattice_analysis
PYTHONPATH=src python -m lloyd_v4.evals.joint_signed_lattice_analysis --output /tmp/joint_lattice_repeat.json
diff Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/joint_signed_lattice_output.json /tmp/joint_lattice_repeat.json

# Pure algebraic campaigns
PYTHONPATH=src python -m lloyd_v4.evals.pure_algebraic_polarity_grid_stability
PYTHONPATH=src python -m lloyd_v4.evals.pure_algebraic_polarity_grid_stability --output /tmp/pure_alg_polarity_repeat.json
diff Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/pure_algebraic_polarity_grid_stability.json /tmp/pure_alg_polarity_repeat.json

# Three-fixture comparison
PYTHONPATH=src python -m lloyd_v4.evals.cross_fixture_comparison
PYTHONPATH=src python -m lloyd_v4.evals.cross_fixture_comparison --output /tmp/three_fixture_repeat.json
diff Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/three_fixture_comparison.json /tmp/three_fixture_repeat.json

# Task-specific tests
python -m pytest -q tests/test_task028_conditional_masks_joint_lattice_pure_algebraic.py

# Full suite
python -m pytest -q tests/

# Source purity and manifest audits
python -m pytest -q tests/test_task001_source_purity.py
python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py

# Forbidden-import grep (expected: zero matches)
rg "numpy\.random|np\.random|scipy|sympy|mpmath" src/lloyd_v4/evals/conditional_mask_analysis.py src/lloyd_v4/evals/joint_signed_lattice_analysis.py src/lloyd_v4/evals/pure_algebraic_four_form.py src/lloyd_v4/evals/pure_algebraic_lattice_campaign.py src/lloyd_v4/evals/pure_algebraic_polarity_grid_stability.py
```

## 9. Non-Goals (explicit)

1. **No re-running of Schwarzschild or SR campaigns.** Sub-objectives A and B analyse existing campaign outputs; the existing JSON files are read-only.
2. **No new substrate primitive, runtime status enum, manifest entry, transition rule, or law-library term.**
3. **No promotion of joint signed-lattice or conditional-mask observables to substrate** even if the histogram reveals strong structure. A future task can promote if warranted; this task only produces typed evidence.
4. **No new physics fixtures.** Pure algebraic is intentionally NOT physics; Bell strain remains as a candidate Task 029 if cross-fixture evidence calls for it.
5. **No solver behavior changes.**
6. **No `numpy.random`.** Use `random.Random(seed)`.
7. **No named mathematical constants** (Axiom 11).
8. **No interpretive language about specific physics theories** (Kerr, lightspeed, branch points, etc.) in the README or summary prose. The task tests whether the chain pattern survives removal of all physics; physics-specific interpretations are explicitly out of scope.

## 10. Completion Report

`Build_Docs/Reports/task028_summary.md` must contain:

- Scope statement covering all three sub-objectives.
- Pre-task baseline confirmation (commit hash, test count = 487).
- Test results (new test count, full suite count).
- Files changed list.

**Sub-objective A — Conditional Masks:**
- Per-fixture, per-grid, per-precision table of F1_only / F2_only / co-fire counts.
- Headline observation on whether the F1/F2 mechanism shows the predicted asymmetry (F1 and F2 measure different parts of the chain with shared dominant rounding direction at overlap).
- Note any (fixture, grid, precision) where F1 and F2 have full overlap (subset relation) vs partial overlap (independent contributors).

**Sub-objective B — Joint Signed-Lattice:**
- Per-fixture, per-precision joint state histogram summary (top 10 most-populated states, total state count).
- Conditional summaries: does F1 sign predict F2 level distribution? Does F4 level band correlate with F1/F2 polarity state?
- Headline observation on whether the joint state carries structure beyond sign and lattice analysed separately.

**Sub-objective C — Pure Algebraic:**
- x-grid summary.
- Pure algebraic four-form non-zero counts per precision.
- Pure algebraic lattice findings (per-form, per-precision classification).
- Pure algebraic polarity grid stability headline per pair.
- Negative control verification (F1/F4 aggregate).
- F2/F4 bottle-cap verification.

**Three-Fixture Comparison:**
- Side-by-side aggregate classifications for F1/F2, F1/F4, F2/F4 across (Schwarzschild, SR, pure_algebraic).
- Side-by-side lattice grain comparisons.
- Sterbenz boundary verification table with all three fixtures.
- **Headline finding** stated in one of these explicit forms:
  - `chain_property_supported`: all three fixtures agree on substrate-level invariants (F1/F2 grid-stable parallel polarity, F3 silent, F2 half-level lattice, F4 integer lattice, Sterbenz direction). Pure algebraic confirms the property is independent of physics.
  - `chain_property_partial`: most invariants preserved, specific divergences named.
  - `chain_property_rejected`: pure algebraic diverges qualitatively from Schwarzschild and SR on the substrate-level features. Indicates physics-shared structure not present in bare algebra.

- Honest observations: surprises in conditional masks, unexpected joint-state structure, pure-algebraic anomalies.
- Limits: pure algebraic uses the (1−x/2)−x/2 split routing for F4; alternative split routings not tested. No Bell strain. No long-double. No platform FMA axis.
- Forward references: Task 029 (Bell strain if cross-fixture motivation persists), Task 030 (operation-level Sterbenz annotation — the substrate-deepening task), substrate promotion considered IF and ONLY IF chain-property is fully supported AND joint-state reveals a derivable structural law.

## 11. Acceptance Criteria

- All 21 required tests pass.
- Full pytest suite count == 487 + 21 == 508 (report exact number; flag if Codex adds additional tests).
- All four campaign outputs byte-stable.
- No additions to `StatusCode` enum.
- No modifications to `layer_manifest.json` or `LAYER_MANIFEST.md`.
- Existing Schwarzschild and SR campaign output JSON files have unchanged byte hashes.
- No forbidden imports.
- All manifest-audit and source-purity tests pass.
- Three-fixture headline classification is one of `chain_property_supported`, `chain_property_partial`, or `chain_property_rejected`. Reflects the data; not pre-decided.
- F3 identically zero in pure algebraic across all precisions; `test_F3_pure_algebraic_identically_zero` fails loudly otherwise.
- F1/F4 pure algebraic aggregate is `depolarized_invariant` or `open_underpowered`; `negative_control_failed` triggers test failure.
- F2/F4 pure algebraic NOT `grid_stable_polarity_coupling` unless all grids have cofire ≥ 10.

## 12. Discipline Notes

1. **The conclusion follows from the data.** The hypothesis (chain-property invariant across physics removal) has a specific prediction: pure algebraic mirrors Schwarzschild and SR on the substrate-level features. If it does, report `chain_property_supported`. If it doesn't, report honestly.

2. **F3 sentinel is loud across all three fixtures.** Pure algebraic's F3 silence is the critical control. If it breaks, halt.

3. **Negative control is loud.** F1/F4 in pure algebraic must NOT promote. If it does, the framework is too permissive and the entire campaign needs review.

4. **Bottle-cap discipline is loud.** Small-N cofires never promote.

5. **A and B work on byte-frozen existing data.** The conditional mask and joint signed-lattice analyses MUST NOT modify the Schwarzschild Task 026c-prime or SR Task 027 outputs. Test 21 explicitly verifies this.

6. **Sub-objective C tests the strongest discriminator.** Pure algebraic has no physics — if the property still appears, that's strong evidence the chain is the source. If it doesn't appear in pure algebraic but DOES appear in Schwarzschild and SR, that's evidence the two physics fixtures share structure (e.g., sqrt-of-near-1 algebraic shape) that bare algebra lacks. Either outcome is informative; the task does not pre-decide.

7. **Joint state is descriptive only, not promotional.** Even if Sub-objective B reveals striking structure, this task does not promote anything to substrate. A future task can promote if the histogram reveals a derivable law (e.g., "F1 sign deterministically predicts F2 level class"). For now, just typed evidence.

8. **No physics analogies in prose.** The Kerr leap has been retired. The task tests substrate properties; speculative metric-shape analogies are out of scope.

9. **End-of-task git discipline (non-negotiable).**

```bash
git add -A
git status
git commit -m "Task 028: Conditional masks, joint signed-lattice, and pure algebraic four-form control"
git push origin main
```

The commit MUST land on origin/main before the task is considered closed. The completion summary MUST include the commit hash and confirmation that `git status` returned clean.
