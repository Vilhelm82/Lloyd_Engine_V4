# Task 029b Summary - Methodology Refinement

## Scope

Task 029b added a parallel methodology-refinement campaign for the Task 029
path-basis clustering result. The work covered:

- scale-invariant signed-lattice signatures and clustering,
- decimal-50 scaled-form divergence audit for F1 versus `P_scaled_2`,
- sqrt route-residual characterization for `P_distrib_sqrt_mul`,
- a composed refined F5+ report.

No substrate primitive, runtime status enum, manifest entry, law-library term, or
Task 029 module was modified.

## Baseline And Tests

- Pre-task baseline commit: `8a62d32 Task 029: Path-basis rank exploration via algebraic-rewrite clustering`.
- Pre-task baseline: 533 tests passing.
- Added tests: 20 in `tests/test_task029b_methodology_refinement.py`.
- Post-task collection: 553 tests collected.
- Post-task full suite: `python -m pytest -q tests/` passed.

## Files Changed

- `src/lloyd_v4/evals/scale_invariant_signature.py`
- `src/lloyd_v4/evals/scale_invariant_clustering.py`
- `src/lloyd_v4/evals/decimal_scaled_form_audit.py`
- `src/lloyd_v4/evals/sqrt_roundtrip_residual.py`
- `src/lloyd_v4/evals/refined_f5_report.py`
- `tests/test_task029b_methodology_refinement.py`
- `Build_Docs/Reports/task029b_methodology_refinement/*`
- `Build_Docs/Reports/task029b_summary.md`
- `Build_Docs/Agent_tasks/Completed/codex_task029b_methodology_refinement.md`

## Sub-objective A - Scale-Invariant Lattice Metric

At cut=0.10, F1-F4 self-consistency held under the value-relative lattice metric
for all fixtures. The refinement is therefore not methodology-compromised.

| Fixture | Scale rank | F1-F4 self-consistent | Removed F5+ | Retained F5+ | Added F5+ |
| --- | ---: | --- | --- | --- | --- |
| `schwarzschild` | 6 | true | `P_scaled_2`, `P_scaled_half` | `P_compound_split`, `P_distrib_sqrt_mul`, `P_sign_c` | none |
| `sr` | 7 | true | none | `P_compound_split`, `P_compound_zero`, `P_distrib_mul`, `P_distrib_sqrt_mul`, `P_scaled_2`, `P_scaled_half`, `P_sign_a`, `P_sign_c` | none |
| `pure_algebraic` | 6 | true | `P_scaled_2`, `P_scaled_half` | `P_compound_split`, `P_factor_b`, `P_sign_c` | none |

`P_scaled_2` and `P_scaled_half` collapse under the scale-invariant variant in
Schwarzschild and pure algebraic, but not in SR.

## Sub-objective B - Decimal Scaled-Form Audit

| Fixture | Divergent cells | Hypothesized cause |
| --- | ---: | --- |
| `schwarzschild` | 24 | `decimal_multiplication_rounding` |
| `sr` | 24 | `decimal_multiplication_rounding` |
| `pure_algebraic` | 29 | `decimal_multiplication_rounding` |

The Decimal context at evaluation is precision 50 with `ROUND_HALF_EVEN`.
The divergent samples show expression-route rounding at the context boundary:
F1 leaves residuals such as `1E-50`, `-1E-50`, or `1E-51`, while the scaled
route often rounds to zero after the independent `2 * R**2` and `2 * direct`
operations. The audit therefore records `P_scaled_2` as a decimal-context
artifact, not a new substrate candidate.

## Sub-objective C - Sqrt Route-Residual Characterization

The characterized observable is the route residual expressed by the frozen
Task 029 candidate `P_distrib_sqrt_mul`:

```text
(sqrt(f))**2 - sqrt(f) * sqrt(f)
```

| Fixture | Precision | Non-zero cells | Max abs residual | Aligns with `P_distrib_sqrt_mul` |
| --- | --- | ---: | ---: | --- |
| `schwarzschild` | `float32` | 0 | 0.0 | true |
| `schwarzschild` | `float64` | 1 | 1.3877787807814457e-17 | true |
| `schwarzschild` | `decimal_50` | 0 | 0.0 | true |
| `sr` | `float32` | 0 | 0.0 | true |
| `sr` | `float64` | 1 | 5.551115123125783e-17 | true |
| `sr` | `decimal_50` | 1 | 1e-50 | true |
| `pure_algebraic` | `float32` | 0 | 0.0 | true |
| `pure_algebraic` | `float64` | 0 | 0.0 | true |
| `pure_algebraic` | `decimal_50` | 0 | 0.0 | true |

The residual is sparse and fixture-dependent. It is a real operation-level
observation for Schwarzschild and SR, but not a cross-fixture universal F5+
candidate in this task.

## Refined F5+ Report

| Fixture | Refined F5+ |
| --- | --- |
| `schwarzschild` | `P_compound_split`, `P_distrib_sqrt_mul`, `P_sign_c` |
| `sr` | `P_compound_split`, `P_compound_zero`, `P_distrib_mul`, `P_distrib_sqrt_mul`, `P_scaled_half`, `P_sign_a`, `P_sign_c` |
| `pure_algebraic` | `P_compound_split`, `P_factor_b`, `P_sign_c` |

- Universal refined F5+ candidates: `P_compound_split`, `P_sign_c`.
- Minimum defensible F5+ set: `P_compound_split`, `P_sign_c`.
- Headline finding: `mixed_resolution`.

The outcome is mixed because the scale-invariant metric removes the scaled-form
candidates in two fixtures, the decimal audit removes `P_scaled_2` as a
Decimal-context artifact, and SR still retains a broader fixture-specific F5+
set. No new F5+ candidates were added by the scale-invariant variant.

## Limits And Forward Reference

Only the signed-lattice dimension was re-tested under a scale-invariant variant.
The precision-scaling, alpha-status, co-fire-polarity, and envelope-shape
dimensions were reused unchanged from Task 029. Task 030 should target the
refined set, especially `P_compound_split`, `P_sign_c`, and the operation-level
sqrt route residual, before any substrate promotion is considered.

## Verification

- `python -m pytest -q tests/test_task029b_methodology_refinement.py`
- `python -m pytest --collect-only tests`
- `python -m pytest -q tests/`
- Byte-stability diffs for all five generated JSON outputs passed.
- Source-purity and manifest-audit tests passed.
- Forbidden-import grep returned zero matches.
