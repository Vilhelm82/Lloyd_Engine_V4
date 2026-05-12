# Codex Task 029b — Methodology Refinement: Scale-Invariant Lattice Metric, Decimal Scaled-Form Audit, and Sqrt-Roundtrip Characterization

## 1. Repository / Baseline

- Repo: `git@github.com:Vilhelm82/Lloyd_Engine_V4.git`, branch `main`.
- Working tree pre-task: clean. Origin/main matches local. `git log -1 --oneline` should return `8a62d32 Task 029: Path-basis rank exploration via algebraic-rewrite clustering`.
- Pre-task test baseline: 533 tests passing (`pytest -q tests/`).
- Pre-task data consumed read-only:
  - `Build_Docs/Reports/task029_path_basis_rank_clustering/*` (all Task 029 outputs)
  - Tasks 026c-prime, 027, 028 outputs as needed for comparison
  - All existing eval modules under `src/lloyd_v4/evals/`

## 2. Task Goal

Task 029 produced `basis_rank_divergent`. F1-F4 self-consistency held (methodology gate passed), but the substrate revealed 8-9 cluster signatures per fixture rather than the predicted rank-4 invariant. The result is genuine substrate evidence, but two of the universal F5+ candidates — `P_scaled_2` and `P_scaled_half` — clustered away from F1 in a manner that may be a metric artefact rather than a substrate finding. A third candidate, `P_distrib_sqrt_mul`, produced near-silent but non-F3-silent signatures that warrant direct characterization.

Task 029b answers three targeted methodology questions before Task 030 (operation-level Sterbenz annotation) commits to the current clustering as its target:

**Sub-objective A — Scale-invariant lattice metric variant.** Re-compute the signed-lattice histogram dimension using lattice levels relative to `ulp(value)` instead of `ulp(operand)`. Re-run signature computation and clustering with the alternative metric. Test whether `P_scaled_2` and `P_scaled_half` collapse into the F1 cluster under the scale-invariant variant. If they do, that part of the F5+ finding is metric-sensitive; if they don't, it's substrate-real.

**Sub-objective B — Decimal-50 scaled-form audit.** Investigate why `P_scaled_2` produces 31 non-zero decimal-50 cells while F1 produces 55 in Schwarzschild (and analogous discrepancies in SR and pure algebraic). Algebraically `2 × R² − 2 × f_direct` and `R² − f_direct` should produce proportional values; the decimal-50 count divergence suggests either: (a) `decimal.Decimal` multiplication rounding context behaviour, (b) ulp-level threshold artefacts in the lattice classifier, (c) genuine substrate behaviour of scaled-form chains at high precision. Resolve which.

**Sub-objective C — Sqrt-roundtrip characterization.** Sample the operand values where `P_distrib_sqrt_mul` fires (one cell each at f64 in Schwarzschild and SR; zero in pure algebraic) and characterize the sqrt double-roundtrip residual `sqrt(f) × sqrt(f) − f` across the full canonical grid for all three fixtures. Determine whether this is a sparse, fixture-dependent rounding event or a substrate-level signature class of its own.

The headline question this task answers: **after methodology refinement, what is the smallest defensible substrate F5+ candidate set, and is it consistent across fixtures?**

This is a methodology and analysis task. No new substrate primitive, no new runtime status enum, no manifest changes, no law-library term, no new candidate paths.

## 3. Source Labelling

- **V4-surface evidence**: Task 029 catalog and signatures; Tasks 026c-prime, 027, 028 outputs.
- **No V3 reference for scale-invariant metrics or decimal-form audit.** Both methodology refinements are V4-native.
- **Output**: alternative metric signatures and clustering; decimal-50 scaled-form audit findings; sqrt-roundtrip residual characterization; refined F5+ candidate set with cross-fixture consistency analysis.

## 4. Design Principles

1. **No new candidate paths.** The Task 029 catalog (15 paths per fixture, 45 total) is the working set. Task 029b refines the analysis, not the candidate space.
2. **Original Task 029 outputs remain byte-frozen.** The scale-invariant variant produces a parallel signature set, NOT a replacement. Both signature sets co-exist; the comparison between them is the finding.
3. **Methodology gate preserved at the refined metric.** F1-F4 must remain self-consistent under the scale-invariant metric. If F1 and F2 cluster together under scale-invariant lattice, the alternative metric is more degenerate than the original and the refinement is itself problematic.
4. **Decimal-50 audit is mechanism-finding, not numerical patch.** The audit produces typed evidence about WHY the decimal-50 counts differ, not a "fix" that makes them equal. If `decimal.Decimal` multiplication has documented rounding behavior that produces the count divergence, that's a documented finding, not a methodology error.
5. **Sqrt-roundtrip characterization is its own substrate observation.** Even if `P_distrib_sqrt_mul` is removed from the F5+ set after refinement, the sqrt-roundtrip residual across the grid IS a typed observation about chain structure. Report it as such.
6. **Headline outcome is honest about resolution.** Sub-objective A may resolve scaled-identity candidates as artefact; B may resolve decimal-50 divergence as Decimal-context behavior; C may add sqrt-roundtrip as a real substrate observation. The final F5+ count after refinement is what it is.

## 5. Primitive-Sufficiency Gate

| Concept used in this task | Origin | Layer |
|---|---|---|
| Scale-invariant lattice level | new module, alternative to `ulp(operand)`-relative levels | eval |
| Decimal context inspection | stdlib `decimal.getcontext()`, admitted read-only | eval |
| sqrt double-roundtrip residual | new analysis, no new operation | eval |
| Re-clustering with alternative signature | reuse `path_clustering.py` with alternate signature input | eval |
| Refined F5+ candidate report | new module, composes A, B, C findings | eval |

**No new substrate primitive. No new runtime status enum. No imports of `numpy.random`, `scipy`, `sympy`, `mpmath`, or `math`-named-constants in new code. No clustering library imports. No modifications to existing Task 029 modules.**

## 6. Required Deliverables

### 6.1 Scale-Invariant Lattice Metric (Sub-objective A)

New file: `src/lloyd_v4/evals/scale_invariant_signature.py`.

Public surface:

```python
def signed_lattice_histogram_value_relative(
    path: CandidatePath,
    precision: str,
) -> dict[str, int]:
    """Compute the signed-lattice histogram using lattice levels relative to ulp(value)
    instead of ulp(operand). Returns the same shape as the original histogram dimension.
    """

def compute_path_signature_scale_invariant(path: CandidatePath) -> PathSignature:
    """Compute the full 6-dimensional path signature, but with the signed-lattice
    histogram dimension using value-relative lattice levels. All other dimensions
    (zero mask, precision scaling, alpha status, co-fire polarity, envelope shape)
    are unchanged from the original signature.
    """

def compute_all_signatures_scale_invariant(fixture: str) -> tuple[PathSignature, ...]: ...

def write_scale_invariant_output(path: Path) -> dict: ...
def main() -> None: ...
```

The scale-invariant lattice level for a non-zero value `v` is computed as:

```
level = round(v / ulp(v))
sign = +1 if v > 0 else -1 if v < 0 else 0
```

For F1 (no scaling), `ulp(v)` is approximately `ulp(operand) × |dF/d(operand)|` near the operand, so level is roughly proportional to the operand-relative level. For P_scaled_2 (value scaled by 2), `ulp(v)` is approximately `2 × ulp(F1 value)`, so the level is roughly half the operand-relative level — exactly the kind of scale invariance the refinement is testing.

### 6.2 Scale-Invariant Re-clustering

New file: `src/lloyd_v4/evals/scale_invariant_clustering.py`.

Public surface:

```python
def run_scale_invariant_clustering_campaign(
    cut_thresholds: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20),
) -> dict:
    """Re-run the Task 029 clustering with scale-invariant signatures.
    Same cut threshold sweep, same headline classifications.
    Output schema matches Task 029 basis_rank_clustering.json for direct comparison.
    """

def compare_original_vs_scale_invariant(cut_threshold: float = 0.10) -> dict:
    """For one cut threshold, report:
    - per-fixture rank under original signature
    - per-fixture rank under scale-invariant signature
    - F5+ candidates removed by scale-invariant variant (those that collapsed into canonical clusters)
    - F5+ candidates added by scale-invariant variant (those that newly split off)
    - F5+ candidates retained by scale-invariant variant (genuinely scale-insensitive distinctions)
    """

def write_scale_invariant_comparison(path: Path) -> dict: ...
def main() -> None: ...
```

### 6.3 Decimal-50 Scaled-Form Audit (Sub-objective B)

New file: `src/lloyd_v4/evals/decimal_scaled_form_audit.py`.

Public surface:

```python
def audit_decimal_scaled_divergence(fixture: str) -> dict:
    """For one fixture, identify cells where F1 has non-zero decimal-50 value AND
    P_scaled_2 has zero decimal-50 value (or vice versa). Return:
    - n_cells_divergent: count of cells where the scaled form silent but F1 fires (or vice versa)
    - sample_operands: the operand values at those cells (up to 20)
    - decimal_context_at_evaluation: the Decimal context used (precision, rounding)
    - F1_value_decimal_50, scaled_2_value_decimal_50, ratio at each sample
    - hypothesized_cause: one of "decimal_multiplication_rounding", "ulp_threshold_artefact", "substrate_behavior", or "indeterminate"
    """

def reproduce_decimal_scaled_divergence_at_cell(
    fixture: str,
    cell_index: int,
) -> dict:
    """For one cell index in one fixture, fully reproduce the decimal-50 computation
    for F1 and P_scaled_2 with explicit logging of intermediate Decimal operations.
    Returns the operation-by-operation trace.
    """

def write_decimal_audit_output(path: Path) -> dict: ...
def main() -> None: ...
```

The hypothesized_cause classification is based on:
- `decimal_multiplication_rounding`: the decimal-50 context's rounding behaviour produces different results for `2 × R²` vs `R²` such that the subsequent subtraction lands at zero in one case and non-zero in the other.
- `ulp_threshold_artefact`: the lattice classifier's threshold for "non-zero" differs in proportion between F1 and scaled values, producing a count divergence that isn't reflected in the actual value distribution.
- `substrate_behavior`: the divergence is a genuine substrate-level property of scaled-identity chains at high precision, not explainable by either of the above.
- `indeterminate`: the audit could not distinguish among the three hypotheses.

### 6.4 Sqrt-Roundtrip Characterization (Sub-objective C)

New file: `src/lloyd_v4/evals/sqrt_roundtrip_residual.py`.

Public surface:

```python
def sqrt_roundtrip_residual_at_cell(
    fixture: str,
    cell_index: int,
    precision: str,
) -> float:
    """Compute sqrt(f) * sqrt(f) - f at one cell, one precision. Returns 0.0 when the
    roundtrip is exact, non-zero when sqrt introduces rounding."""

def sqrt_roundtrip_residual_full_grid(fixture: str, precision: str) -> tuple[float, ...]: ...

def characterize_sqrt_roundtrip(fixture: str) -> dict:
    """For one fixture, characterize the sqrt double-roundtrip residual across all
    precisions:
    - n_cells_with_nonzero_residual at each precision
    - max |residual| at each precision
    - cells with largest |residual| at f64 (top 5)
    - operand values at those cells
    - alignment with P_distrib_sqrt_mul firing: does the firing cell coincide with the largest |residual|?
    """

def write_sqrt_roundtrip_output(path: Path) -> dict: ...
def main() -> None: ...
```

### 6.5 Refined F5+ Report

New file: `src/lloyd_v4/evals/refined_f5_report.py`.

Public surface:

```python
def compile_refined_f5_set(cut_threshold: float = 0.10) -> dict:
    """Combine findings from A, B, and C:
    - F5+ candidates from original Task 029 clustering
    - F5+ candidates removed by scale-invariant variant (now classed as artefacts)
    - F5+ candidates retained across both variants (real substrate-level distinctions)
    - sqrt-roundtrip residual evidence: is this a substrate observation in its own right?
    - decimal-50 audit findings: is the divergence Decimal-context or substrate?
    Returns:
    - refined_F5_set per fixture
    - cross-fixture-universal refined F5+ (the most defensible substrate observation)
    - methodology_resolution: one of:
        "artefact_dominant" (most original F5+ candidates resolved as metric artefacts)
        "substrate_dominant" (most original F5+ candidates retained as substrate)
        "mixed_resolution" (genuine mix of artefact and substrate)
        "methodology_compromised" (scale-invariant metric fails F1-F4 self-consistency)
    """

def write_refined_f5_report(path: Path) -> dict: ...
def main() -> None: ...
```

### 6.6 Reports Directory

```
Build_Docs/Reports/task029b_methodology_refinement/
    scale_invariant_signatures.json
    scale_invariant_clustering.json
    scale_invariant_vs_original_comparison.json
    decimal_scaled_form_audit.json
    decimal_scaled_form_audit_table.csv
    sqrt_roundtrip_residual.json
    sqrt_roundtrip_summary_table.csv
    refined_f5_report.json
    refined_f5_summary_table.csv
    README.md
Build_Docs/Reports/task029b_summary.md
```

## 7. Required Tests

New test file: `tests/test_task029b_methodology_refinement.py`.

Required tests:

1. **`test_scale_invariant_signature_schema`**: every scale-invariant PathSignature has all six dimensions populated, with the signed-lattice histogram using value-relative levels.
2. **`test_scale_invariant_signatures_byte_stable`**: scale-invariant signature output is byte-stable across runs.
3. **`test_canonical_anchors_self_consistent_under_scale_invariant`**: F1, F2, F3, F4 each fall into distinct clusters under the scale-invariant metric at cut=0.10 in all three fixtures. If this fails, the scale-invariant metric is itself problematic and the refinement loses interpretive power.
4. **`test_F3_silent_under_scale_invariant`**: F3's signed-lattice histogram under value-relative levels is empty (no non-zero values to assign levels to).
5. **`test_scale_invariant_clustering_byte_stable`**: scale-invariant clustering output is byte-stable.
6. **`test_scale_invariant_comparison_schema`**: original-vs-scale-invariant comparison contains removed/added/retained F5+ candidate lists per fixture.
7. **`test_decimal_audit_schema_per_fixture`**: decimal audit output contains the required fields per fixture (n_cells_divergent, sample_operands, decimal_context, hypothesized_cause).
8. **`test_decimal_audit_byte_stable`**: decimal audit output is byte-stable.
9. **`test_decimal_audit_hypothesized_cause_one_of_four`**: the hypothesized_cause for each fixture is exactly one of the four declared options.
10. **`test_sqrt_roundtrip_residual_byte_stable`**: sqrt-roundtrip output is byte-stable.
11. **`test_sqrt_roundtrip_zero_at_F3_firing_cells`**: at any cell where F3 evaluates to exactly zero (which should be all cells in all fixtures), the sqrt-roundtrip residual at that cell is well-defined (not NaN or inf), regardless of whether it's zero or non-zero.
12. **`test_sqrt_roundtrip_alignment_with_P_distrib_sqrt_mul`**: in Schwarzschild and SR, the f64 cell where P_distrib_sqrt_mul fires coincides with one of the cells with the largest |sqrt-roundtrip residual| at f64.
13. **`test_refined_f5_report_byte_stable`**: refined F5+ report is byte-stable.
14. **`test_refined_f5_report_methodology_resolution_valid`**: the methodology_resolution field is one of the four declared values.
15. **`test_no_modifications_to_task029_outputs`**: Task 029 output JSON files have unchanged byte hashes after running Task 029b.
16. **`test_no_runtime_status_enum_additions`**: `StatusCode` membership unchanged.
17. **`test_no_law_library_term_added`**: Task 025 law library candidates unchanged.
18. **`test_no_manifest_changes`**: `layer_manifest.json` and `LAYER_MANIFEST.md` unchanged.
19. **`test_no_clustering_library_imported`**: rg search for `scipy.cluster`, `sklearn.cluster`, `scipy.spatial.distance` in new modules returns zero matches.
20. **`test_no_existing_module_modifications`**: `path_catalog.py`, `path_signature.py`, `path_distance.py`, `path_clustering.py`, `basis_rank_comparison.py` all have unchanged byte hashes.

## 8. Required Commands

```bash
# Baseline confirmation
git log -1 --oneline
python -m pytest -q tests/

# Scale-invariant signatures
PYTHONPATH=src python -m lloyd_v4.evals.scale_invariant_signature
PYTHONPATH=src python -m lloyd_v4.evals.scale_invariant_signature --output /tmp/scale_inv_sigs_repeat.json
diff Build_Docs/Reports/task029b_methodology_refinement/scale_invariant_signatures.json /tmp/scale_inv_sigs_repeat.json

# Scale-invariant clustering and comparison
PYTHONPATH=src python -m lloyd_v4.evals.scale_invariant_clustering
PYTHONPATH=src python -m lloyd_v4.evals.scale_invariant_clustering --output /tmp/scale_inv_cluster_repeat.json
diff Build_Docs/Reports/task029b_methodology_refinement/scale_invariant_clustering.json /tmp/scale_inv_cluster_repeat.json

# Decimal-50 scaled-form audit
PYTHONPATH=src python -m lloyd_v4.evals.decimal_scaled_form_audit
PYTHONPATH=src python -m lloyd_v4.evals.decimal_scaled_form_audit --output /tmp/decimal_audit_repeat.json
diff Build_Docs/Reports/task029b_methodology_refinement/decimal_scaled_form_audit.json /tmp/decimal_audit_repeat.json

# Sqrt-roundtrip characterization
PYTHONPATH=src python -m lloyd_v4.evals.sqrt_roundtrip_residual
PYTHONPATH=src python -m lloyd_v4.evals.sqrt_roundtrip_residual --output /tmp/sqrt_roundtrip_repeat.json
diff Build_Docs/Reports/task029b_methodology_refinement/sqrt_roundtrip_residual.json /tmp/sqrt_roundtrip_repeat.json

# Refined F5+ report
PYTHONPATH=src python -m lloyd_v4.evals.refined_f5_report
PYTHONPATH=src python -m lloyd_v4.evals.refined_f5_report --output /tmp/refined_f5_repeat.json
diff Build_Docs/Reports/task029b_methodology_refinement/refined_f5_report.json /tmp/refined_f5_repeat.json

# Task-specific tests
python -m pytest -q tests/test_task029b_methodology_refinement.py

# Full suite
python -m pytest -q tests/

# Source purity and manifest audits
python -m pytest -q tests/test_task001_source_purity.py
python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py

# Forbidden-import grep (expected: zero matches)
rg "numpy\.random|np\.random|scipy|sympy|mpmath|sklearn" src/lloyd_v4/evals/scale_invariant_signature.py src/lloyd_v4/evals/scale_invariant_clustering.py src/lloyd_v4/evals/decimal_scaled_form_audit.py src/lloyd_v4/evals/sqrt_roundtrip_residual.py src/lloyd_v4/evals/refined_f5_report.py
```

## 9. Non-Goals (explicit)

1. **No new substrate primitive, runtime status enum, manifest entry, transition rule, or law-library term.**
2. **No new candidate paths.** The Task 029 catalog is the working set.
3. **No new fixtures.** The three existing fixtures are the analysis subjects.
4. **No modifications to existing Task 029 modules.** Refinement is additive.
5. **No re-running of existing campaigns** beyond what Task 029b's modules produce.
6. **No clustering library imports.**
7. **No fixes to Decimal multiplication behavior.** The audit characterises, it does not patch.
8. **No promotion of refined F5+ candidates to substrate** even if confirmed.
9. **No interpretive language about specific physics theories.**
10. **No `numpy.random`, `math`-named constants, or other forbidden imports.**

## 10. Completion Report

`Build_Docs/Reports/task029b_summary.md` must contain:

- Scope statement covering all three sub-objectives.
- Pre-task baseline confirmation (commit hash, test count = 533).
- Test results (new test count = 20, full suite count = 553).
- Files changed list.

**Sub-objective A — Scale-Invariant Lattice Metric:**
- Per-fixture rank under scale-invariant metric at cut=0.10.
- F1-F4 self-consistency under scale-invariant metric (must hold; otherwise refinement is itself compromised).
- F5+ candidates removed (collapsed into canonical clusters) — these are the metric artefacts.
- F5+ candidates retained — these are the scale-insensitive distinctions.
- F5+ candidates added (new splits under scale-invariant) — should be empty or rare; if present, characterise.

**Sub-objective B — Decimal Scaled-Form Audit:**
- Per-fixture summary of decimal-50 divergence between F1 and P_scaled_2.
- Hypothesized cause classification per fixture.
- If `decimal_multiplication_rounding`: the specific Decimal context behaviour responsible.
- If `ulp_threshold_artefact`: the specific threshold and its proportionality issue.
- If `substrate_behavior`: the evidence that rules out the other two hypotheses.
- If `indeterminate`: what additional investigation would distinguish among the three.

**Sub-objective C — Sqrt-Roundtrip Characterization:**
- Per-fixture per-precision summary of sqrt(f)*sqrt(f) - f residual.
- Cells with non-zero residual count.
- Maximum |residual| magnitude per precision.
- Alignment with P_distrib_sqrt_mul firing (verification of test 12).
- Headline observation: is sqrt-roundtrip a real substrate observation deserving its own typed observable, or a sparse fixture-dependent rounding event?

**Refined F5+ Report:**
- Universal F5+ candidates retained after refinement (intersection across all three fixtures of F5+ candidates surviving scale-invariant clustering AND not classified as decimal artefacts).
- The "minimum defensible F5+ set" — the cleanest characterisation of substrate beyond F1-F4.
- **Headline finding** stated in one of the four explicit forms:
  - `artefact_dominant` (most original F5+ candidates resolved as metric artefacts; refined F5+ count ≤ 1 per fixture)
  - `substrate_dominant` (most original F5+ candidates retained; refined F5+ count ≥ 4 per fixture)
  - `mixed_resolution` (genuine mix; refined F5+ count 2-3 per fixture)
  - `methodology_compromised` (scale-invariant metric fails F1-F4 self-consistency in at least one fixture)

- Honest observations: any candidate whose status changed unexpectedly, any cross-fixture inconsistency in the refined F5+ set.
- Limits: only the scale-invariant variant tested for the signed-lattice dimension; other dimensions (precision scaling, alpha status, etc.) not re-tested under alternative metrics.
- Forward references: Task 030 (operation-level Sterbenz annotation, targeted at the refined F5+ set rather than the original); substrate promotion of refined F5+ observable considered IF AND ONLY IF the refined set is cross-fixture-consistent AND has a derivable explanation via Task 030.

## 11. Acceptance Criteria

- All 20 required tests pass.
- Full pytest suite count == 533 + 20 == 553 (report exact number; flag if Codex adds additional tests).
- All five new module outputs byte-stable.
- No additions to `StatusCode` enum.
- No modifications to `layer_manifest.json` or `LAYER_MANIFEST.md`.
- Existing Task 029, 028, 027, 026c-prime campaign output JSON files have unchanged byte hashes.
- Existing Task 029 modules have unchanged byte hashes (test 20).
- No forbidden imports.
- All manifest-audit and source-purity tests pass.
- F1-F4 self-consistency under scale-invariant metric at cut=0.10 holds in all three fixtures (test 3). If it fails, headline classification MUST be `methodology_compromised`.
- Decimal hypothesized_cause is one of the four declared values per fixture (test 9).
- Sqrt-roundtrip alignment with P_distrib_sqrt_mul holds where the candidate fires (test 12).
- Methodology resolution headline is one of the four explicit forms.

## 12. Discipline Notes

1. **The conclusion follows from the data.** If scale-invariant clustering collapses P_scaled_2/P_scaled_half into F1, the original F5+ finding was partly artefact. If it doesn't, those candidates are substrate. If decimal-50 audit reveals Decimal-context behaviour as the cause, the decimal-50 dimension carries an implementation signature rather than a substrate signature. Report honestly.

2. **F3 sentinel still loud.** Any path labelled F3 in any module of this task must be silent across all precisions and metrics. If F3's value-relative lattice produces non-empty histogram, the implementation is wrong.

3. **F1-F4 self-consistency under refined metric is the methodology gate.** If F1 and F2 cluster together under scale-invariant lattice, the refinement is itself degenerate and `methodology_compromised` is the only honest headline.

4. **No silent fixes.** If a candidate path's behaviour under the scale-invariant metric is unexpected, report it; do not "correct" the candidate definition. The candidate catalog is frozen from Task 029.

5. **Audit reports characterise, not patch.** The decimal-50 divergence audit produces typed evidence about its cause. It does not "fix" the decimal-50 dimension by rewriting how non-zero values are counted. If the audit reveals an artefact, the FINDING is that the dimension carries an implementation signature; the dimension itself stays in the signature definition.

6. **Sqrt-roundtrip is a clean candidate for its own substrate observation.** Even if removed from F5+ list by being subsumed elsewhere, the residual `sqrt(f) × sqrt(f) − f` is a well-defined, typed, operation-level quantity. Task 030's annotation should engage with it.

7. **End-of-task git discipline (non-negotiable).**

```bash
git add -A
git status
git commit -m "Task 029b: Methodology refinement - scale-invariant lattice, decimal scaled-form audit, sqrt-roundtrip characterization"
git push origin main
```

The commit MUST land on origin/main before the task is considered closed. The completion summary MUST include the commit hash and confirmation that `git status` returned clean.
