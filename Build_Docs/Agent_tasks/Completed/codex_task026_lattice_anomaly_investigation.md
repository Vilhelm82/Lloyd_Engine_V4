# Codex Task 026 — Lattice and Anomaly Investigation Campaign

## 1. Repository & Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4` (laptop).

**Pre-task baseline:**

```bash
cd ~/projects/V4/Lloyd_Engine_V4
source .venv/bin/activate
git status                                    # clean tree
git log -1 --format='%h %s'                   # should be post-025
python -m pytest -q tests/ 2>&1 | tail -3     # 443 tests passing
```

Do not start if baseline is dirty or any tests fail.

---

## 2. Task Goal

Run Stage 1 of the V4 Discovery Battery: a five-sub-module campaign that
**deepens existing data without introducing new fixtures**. Each
sub-module pulls on a thread visible in the output of Tasks 017b, 024b,
or 025 that has not yet been characterised.

The five sub-modules:

- **026.A — Lattice structure detection.** Per-form, per-precision
  enumeration of the ULP-quantised residual lattice. Tests whether
  non-zero residuals are integer multiples of `ulp(f)` and characterises
  the lattice signature.
- **026.B — F2 anomaly deep-dive.** Per-point analysis of F2's 28
  non-zero float64 samples. Tests whether F2's precision-scaling
  failure is small-sample artefact or genuine structure.
- **026.C — Phase B spread characterisation.** Per-point analysis of the
  68 F4 float32/float64 overlap points from Task 017b Phase B.
  Characterises the factor-of-100 ratio spread around the median 2^29.
- **026.D — Multi-form cross-correlation.** Joint structure across F1,
  F2, F3, F4 — joint zero patterns, sum cancellation, differential
  patterns.
- **026.E — Sign-pattern decomposition.** Per-form sign histograms,
  sign sequences, cross-form sign correlations, and parity-correlation
  tests.

This is a **discovery campaign**, not a substrate change. It adds no
primitives, no status families, no manifest entries. The output is
typed observations that inform later stages of the discovery battery
(Tasks 027+).

---

## 3. Source Labelling

**V4-surface:** existing primitives, existing fixtures (Task 024b's
four-form battery, Task 017b's multi-precision four-form, Task 025's
candidate-term machinery). No new V4 substrate.

**Mechanical-property reference:** the IEEE 754 specification's
correctly-rounded operations and the ULP-quantisation observation from
the V3 session report. The ULP-lattice claim is what 026.A tests
empirically.

**Proposal evidence:** the five sub-module designs. Each sub-module
states a hypothesis or characterisation goal; the campaign tests it on
the existing data and reports findings.

---

## 4. Design Principles

**No new primitives, status families, or manifest entries.** Pure
discovery campaign output.

**Sub-modules are independent.** Each sub-module produces its own
section of the campaign output. Sub-modules do not share intermediate
state; their results live in separate JSON sections so each can be
analysed and re-run independently if the campaign grows.

**Each sub-module declares its own hypothesis.** The hypothesis is in
the spec; the test is in the implementation; the result is the data.
No retro-fitting hypotheses to match the data.

**Findings, not verdicts.** The campaign reports numerical
characterisations and candidate classifications. It does not declare
the substrate model "confirmed" or "rejected." Higher-level
interpretation is downstream.

**Determinism required.** All output JSON byte-stable across runs.

**Axiom 11 considerations.** `decimal.Decimal` for high-precision
oracle (admitted as substrate-precision arithmetic per Task 017b's
ruling). `numpy.float32` / `numpy.float64` as type containers. `struct`
for bit-pattern analysis (stdlib, low-level). `numpy.linalg.lstsq` for
any regression. Generic statistics (median, percentile, histogram,
corrcoef) admitted as substrate utilities. No `import math`, no
`numpy.sqrt`, no `scipy`, no `sympy`, no `sklearn`, no `mpmath`.

---

## 5. Primitive-Sufficiency Gate

| Concept | Source | Notes |
|---|---|---|
| Four-form float64 fixture | `lloyd_v4.evals.schwarzschild_four_form` | Re-used. |
| Multi-precision four-form | `lloyd_v4.evals.multi_precision_four_form` | Re-used. |
| ULP helper | same module | Re-used. |
| Chain envelope helper | same module | Re-used. |
| Candidate term library | `lloyd_v4.evals.path_law_discovery` | Re-used for cross-validation only. |
| Decimal oracle | `decimal.Decimal` (stdlib) | Re-used. |
| Bit-pattern extraction | `struct.pack` / `struct.unpack` | New, low-level stdlib. |
| Basic statistics | `numpy` (median, histogram, corrcoef) | Generic substrate utilities. |
| Sparse OLS | `numpy.linalg.lstsq` | Cross-validation only. |

No new substrate concepts.

---

## 6. Sub-Module Specifications

### 6.A — Lattice Structure Detection

**Goal:** For each (form, precision), determine whether the non-zero
residuals lie on the IEEE 754 ULP lattice — i.e., whether
`F_k(r) / ulp(f(r))` is integer-valued at every non-zero point. If yes,
characterise the lattice: distinct levels, level-jump distribution,
per-region level density.

**Hypothesis to test:**
- F4 non-zero residuals are integer multiples of `ulp(f)` at every
  sample. ~36 distinct levels expected across the 137-point sweep
  (consistent with V3 reference table).
- F1, F2 also lattice-quantised but at far fewer distinct levels (sparse
  residuals).
- F3 has no non-zero residuals; lattice is empty.

**Procedure (per form k ∈ {F1, F2, F3, F4}, per precision p ∈ {float32,
float64}):**

1. Evaluate F_k(r) across the 137-point sweep at precision p.
2. For each r where F_k(r) ≠ 0, compute `level(r) = F_k(r) / ulp(f(r))`.
3. Compute `level_integer_residual(r) = level(r) − round(level(r))` —
   how far off integer the level is. If all are within 1e-3 (allowing
   for floating-point representation slack), the lattice is integer.
4. Compute the set of distinct integer levels (rounded).
5. For each distinct level, count the number of r-values that produce
   it.
6. For each consecutive pair of distinct integer levels (sorted), record
   the difference (level-jump).
7. Partition the sweep into near/middle/far regions per Task 025
   conventions. Per region, count the number of distinct levels.
8. Emit candidate classification:
   - `lattice_integer` if all `level_integer_residual` < 1e-3 AND
     n_distinct > 0
   - `lattice_empty` if n_nonzero == 0 (calibration zero)
   - `non_integer_lattice` if n_distinct > 0 but
     `level_integer_residual` exceeds threshold (anomaly)
   - `single_level` if n_distinct == 1 (degenerate, but still typed)

**Output (sub-module A section of campaign output):**

```json
{
  "A_lattice_structure": {
    "by_form": {
      "F1": {
        "by_precision": {
          "float32": {
            "n_total": 137,
            "n_nonzero": <int>,
            "level_integer_residual_max": <float>,
            "level_integer_residual_median": <float>,
            "n_distinct_levels": <int>,
            "level_min": <int>,
            "level_max": <int>,
            "level_histogram": {<level>: <count>, ...},
            "level_jump_distribution": [<int>, ...],
            "regional_distinct_level_counts": {"near": <int>, "middle": <int>, "far": <int>},
            "candidate_classification": "<one of the four labels>"
          },
          "float64": { ... },
          "decimal_50": { ... }
        }
      },
      "F2": { ... },
      "F3": { ... },
      "F4": { ... }
    }
  }
}
```

**Expected findings:**

- F4 float64: ~36 distinct integer levels, regional density highest near
  horizon. Classification: `lattice_integer`.
- F1 float64: ~5–10 distinct levels (mostly ±1, ±2, occasional larger).
  Classification: `lattice_integer`.
- F2 float64: ~3–5 distinct levels. Classification: `lattice_integer`.
- F3 every precision: classification `lattice_empty`.

If any form classifies as `non_integer_lattice`, that is the headline
finding — the ULP-quantisation claim from the instrument-reframe report
would not hold cleanly and the model needs revision.

---

### 6.B — F2 Anomaly Deep-Dive

**Goal:** Determine whether F2's catastrophic precision-scaling failure
(median ratio 1.17e-9 vs expected 5.4e8 from Task 017b Phase B) is
small-sample artefact, lattice-structure-mismatch, or some other
specific anomaly.

**Hypothesis space (the campaign tests which holds):**

1. **Small-sample artefact.** F2's 28 non-zero float64 points are too
   few; the median ratio over such a small set is unstable.
2. **Float32-mostly-zero.** F2 at float32 is zero at most of the
   r-values where F2 at float64 is non-zero, so the ratio at those
   points is undefined or dominated by floating-point representation
   artefacts.
3. **Sign-flip dominance.** Float32 and float64 produce opposite signs
   at most of the overlap points; the magnitude ratio is therefore
   ill-defined as a measure of scaling.
4. **Genuine lattice mismatch.** F2's float32 residuals lie on a
   different lattice than its float64 residuals (not just a scaled
   version). Real structural anomaly.

**Procedure:**

1. From the existing fixture, enumerate the 28 r-values where F2 at
   float64 is non-zero. For each one, record:
   - r (full precision)
   - F2 at float32, float64, decimal-50
   - ulp(f(r)) at each precision
   - F2_float64 / ulp_f64
   - F2_float32 / ulp_f32 (the per-precision level)
   - sign(F2_float32), sign(F2_float64), sign(F2_decimal_50)
   - sign_agreement_32_64 (boolean)
   - ratio F2_float32 / F2_float64 (or None if denominator zero or
     undefined)
2. Test hypothesis 1: bootstrap the ratio. Take 100 random subsets of
   size 14 (half) from the 28 overlap points and compute the median
   ratio for each. Record min, max, and IQR of those medians. If the
   IQR is comparable to the median itself, the small-sample hypothesis
   is supported.
3. Test hypothesis 2: count r-values where F2_float64 ≠ 0 AND
   F2_float32 == 0. If this is most of the 28 points, the "ratio" is
   effectively a division by absent data.
4. Test hypothesis 3: count r-values with sign disagreement between
   float32 and float64 among the points where both are non-zero.
5. Test hypothesis 4: enumerate F2_float32 level integers and compare
   to F2_float64 level integers at the same r-values. Are they
   integer-scaled versions of each other (predictable lattice relation)
   or unrelated?

**Output:**

```json
{
  "B_f2_anomaly": {
    "n_nonzero_float64": 28,
    "per_point_records": [
      {
        "r": <float>,
        "F2_float32": <float>,
        "F2_float64": <float>,
        "F2_decimal_50": <float>,
        "ulp_f_float32": <float>,
        "ulp_f_float64": <float>,
        "level_float32": <int or null>,
        "level_float64": <int or null>,
        "sign_float32": <int -1/0/1>,
        "sign_float64": <int>,
        "sign_decimal_50": <int>,
        "sign_agreement_32_64": <bool>,
        "ratio_32_over_64": <float or null>
      },
      ...
    ],
    "hypothesis_1_small_sample": {
      "bootstrap_median_iqr": <float>,
      "bootstrap_median_range": [<float>, <float>],
      "supported": <bool>
    },
    "hypothesis_2_float32_mostly_zero": {
      "n_float32_zero_at_float64_nonzero": <int>,
      "fraction": <float>,
      "supported": <bool>
    },
    "hypothesis_3_sign_disagreement": {
      "n_sign_disagree": <int>,
      "fraction": <float>,
      "supported": <bool>
    },
    "hypothesis_4_lattice_mismatch": {
      "n_predictable_scaling": <int>,
      "n_unrelated": <int>,
      "supported": <bool>
    },
    "primary_classification": "<best-fitting hypothesis name>",
    "anomaly_explained": <bool>
  }
}
```

**Expected findings:**

The most likely outcome is a combination of hypotheses 1 and 2 — F2 is
sparse to begin with, and float32 is sparser still, so the few overlap
points where both are non-zero produce noisy ratios. If that's the
case, F2's "axis B failure" in Task 025 is reframed: the chain envelope
genuinely bounds F2, but the ratio statistic was meaningless on so few
points. That re-categorises F2 from "anomalous" to "sparse but
consistent."

If instead hypothesis 4 holds (lattice mismatch), that's a genuinely
new finding worth investigating in Stage 2.

---

### 6.C — Phase B Spread Characterisation

**Goal:** Characterise the factor-of-100 spread in the F4
float32/float64 ratio distribution around the median 2^29 observed in
Task 017b Phase B (24% bit-exact, remainder spread).

**Hypothesis space:**

1. **Region-dependent spread.** Near-horizon points scatter more than
   far-field points, or vice versa.
2. **Sign-correlated spread.** Points where F4 changes sign between
   float32 and float64 produce extreme ratios.
3. **Level-dependent spread.** Specific F4/ulp integer levels at
   float64 correlate with predictable ratio deviations at float32.
4. **Quantisation explanation.** The spread is purely the consequence
   of float32 and float64 having different ULP grids, so the ratio
   tracks the integer-level differences exactly.

**Procedure:**

1. Identify the 68 r-values where F4 is non-zero at both float32 and
   float64 (from Task 017b Phase B output, or recompute).
2. For each: r, F4_float32, F4_float64, level_float32 (= F4_float32 /
   ulp_f_float32), level_float64, ratio = F4_float32 / F4_float64,
   log2(ratio / 2^29), region (near/middle/far).
3. Compute histogram of log2(ratio / 2^29) across the 68 points.
4. Compute correlation (Pearson and Spearman) of log2(ratio / 2^29)
   with: region label (0/1/2), sign agreement, level_float64,
   |level_float64|.
5. Test hypothesis 4 specifically: for each r, predict the ratio from
   `(level_float32 × ulp_f_float32) / (level_float64 × ulp_f_float64)`
   and compare to observed ratio.
6. Identify the points where ratio differs from 2^29 by more than a
   factor of 4 in either direction — outlier r-values worth flagging.

**Output:**

```json
{
  "C_phase_b_spread": {
    "n_overlap_points": 68,
    "median_ratio": <float>,
    "expected_ratio_2_to_29": 536870912.0,
    "log2_deviation_histogram": {
      "bins": [-4, -3, -2, -1, 0, 1, 2, 3, 4],
      "counts": [...]
    },
    "correlations": {
      "log2_dev_vs_region": {"pearson": <float>, "spearman": <float>},
      "log2_dev_vs_sign_agreement": {...},
      "log2_dev_vs_level_float64": {...},
      "log2_dev_vs_abs_level_float64": {...}
    },
    "quantisation_prediction_test": {
      "median_predicted_vs_observed_ratio": <float>,
      "n_predicted_within_factor_2": <int>,
      "n_predicted_within_factor_4": <int>,
      "supported": <bool>
    },
    "outlier_points": [
      {"r": <float>, "ratio": <float>, "log2_dev": <float>, "level_float32": <int>, "level_float64": <int>},
      ...
    ],
    "spread_explanation": "<best-fitting hypothesis name or 'open'>"
  }
}
```

**Expected findings:**

Hypothesis 4 (quantisation explanation) is the most likely. The factor-
of-2 spread around the median should be exactly explained by the
integer-level ratios at each precision. If 60+ of the 68 points are
predicted within a factor of 2, the spread is fully explained and the
mechanism is the integer-lattice scaling.

If outliers remain unexplained, those points become the next thread to
pull.

---

### 6.D — Multi-Form Cross-Correlation

**Goal:** Identify any structural relationship between F1, F2, F3, F4
that's not yet typed. Because the four forms are algebraically
identical, any non-trivial cross-correlation tells us about the
arithmetic chain rather than the algebra.

**Procedure:**

1. For each r in the sweep, at float64, record the 4-tuple `(F1(r),
   F2(r), F3(r), F4(r))`.
2. Compute the joint zero mask at each r: a 4-bit pattern (one bit per
   form) indicating which forms are zero.
3. Count occurrences of each of the 16 possible patterns across the
   sweep.
4. Compute the per-r sum `S(r) = F1(r) + F2(r) + F3(r) + F4(r)`. The
   algebraic value is exactly zero; the IEEE 754 sum may not be. Record
   the distribution of S(r): min, max, median, IQR, count where
   `|S(r)| > 0`.
5. Compute differential patterns:
   - `D14(r) = F1(r) - F4(r)` — sqrt-vs-squared signature
   - `D12(r) = F1(r) - F2(r)` — squared-form reordering signature
   - `D24(r) = F2(r) - F4(r)` — composite signature
6. For each differential, compute level integers (when non-zero) and
   classify as lattice-integer or not.
7. Compute the 4×4 Pearson correlation matrix of `(F1(r), F2(r),
   F3(r), F4(r))` across the 137 points. F3 is constant 0, so its
   correlations are undefined; record as 0 by convention. The
   remaining correlations test cross-form structure.
8. Test for any unexpected invariant: e.g., does
   `F2(r) - 2 * F1(r) == 0` ever hold consistently? Try a small set of
   declared linear relations and report which hold within tolerance.

**Output:**

```json
{
  "D_cross_form": {
    "joint_zero_patterns": {
      "0000": <count>, "0001": <count>, ..., "1111": <count>
    },
    "sum_F1_F2_F3_F4": {
      "min": <float>, "max": <float>, "median": <float>, "iqr": <float>,
      "n_nonzero": <int>,
      "max_abs": <float>
    },
    "differential_D14": {
      "n_nonzero": <int>,
      "level_classification": "<lattice_integer | ...>",
      "level_count": <int>
    },
    "differential_D12": { ... },
    "differential_D24": { ... },
    "correlation_matrix_pearson": [
      [1.0, <c12>, 0.0, <c14>],
      [<c12>, 1.0, 0.0, <c24>],
      [0.0,   0.0,   1.0, 0.0  ],
      [<c14>, <c24>, 0.0, 1.0  ]
    ],
    "tested_linear_relations": [
      {"expression": "F1 - F2", "holds_within_tolerance": <bool>, "max_residual": <float>},
      {"expression": "F2 - 2*F1", "holds_within_tolerance": <bool>, "max_residual": <float>},
      {"expression": "F4 - F1", "holds_within_tolerance": <bool>, "max_residual": <float>}
    ],
    "cross_form_findings": ["<any unexpected invariant>", ...]
  }
}
```

**Expected findings:**

The sum `S(r) = F1+F2+F3+F4` should be at chain-envelope scale —
roughly the magnitude of any individual form, since they're algebraically
zero and the chain residuals don't perfectly cancel across the four
different paths. If S is *smaller* than any individual form, that
indicates a hidden cancellation invariant worth flagging. If S equals
F4 to high accuracy, that confirms F1+F2 ≈ 0 (squared-form
reorderings cancel) and F3 ≡ 0.

The differential D14 = F1-F4 isolates the squared-vs-sqrt arithmetic
signature. If D14 has a clean closed-form law (testable via the Task
025 candidate library), that's a typed promotion candidate.

---

### 6.E — Sign-Pattern Decomposition

**Goal:** Characterise per-form sign distributions, sign sequences, and
cross-form sign correlations. Test whether sign correlates with any
predictable bit-pattern feature of `r` or its derivatives.

**Procedure:**

1. For each form at float64, compute the per-r sign:
   `sign(r) = -1, 0, +1`.
2. Per form: counts of -1, 0, +1. Histogram.
3. Per form: the full sign sequence across the 137 r-values, recorded
   as a list.
4. Cross-form sign-agreement: for each pair (k, k') of forms, count
   r-values where `sign_k == sign_k'` (excluding both-zero points).
5. Test hypothesis A: sign correlates with the parity of the integer
   level at that r (`level mod 2`). If sign is determined by parity,
   reporting `corr(sign, level % 2)` should be ±1.
6. Test hypothesis B: sign correlates with the parity of the integer
   `floor(2 / r * 2^k)` for some bit shift k (i.e., a specific bit of
   the operand 2/r). Test for k ∈ {0..52}.
7. Test hypothesis C: sign correlates with whether (r-2)/r as computed
   produces an "up-rounded" vs "down-rounded" sqrt. Test by comparing
   `sqrt((r-2)/r)` to the high-precision truth and recording rounding
   direction.

**Output:**

```json
{
  "E_sign_pattern": {
    "per_form": {
      "F1": {
        "n_pos": <int>, "n_neg": <int>, "n_zero": <int>,
        "sign_sequence": [<int>, <int>, ...],
        "sign_density_by_region": {"near": <float>, "middle": <float>, "far": <float>}
      },
      "F2": { ... },
      "F3": { ... },
      "F4": { ... }
    },
    "cross_form_sign_agreement": {
      "F1_F2": <int>, "F1_F4": <int>, "F2_F4": <int>
    },
    "hypothesis_A_level_parity": {
      "per_form": {"F1": <correlation>, "F2": <correlation>, "F4": <correlation>},
      "any_form_supports": <bool>
    },
    "hypothesis_B_operand_bit": {
      "best_bit_per_form": {"F1": <int>, "F2": <int>, "F4": <int>},
      "best_correlation_per_form": {"F1": <float>, "F2": <float>, "F4": <float>},
      "any_form_supports_above_0.7": <bool>
    },
    "hypothesis_C_rounding_direction": {
      "per_form": {"F1": <float>, "F2": <float>, "F4": <float>},
      "supports_above_0.7": <bool>
    },
    "candidate_new_term_for_law_library": "<term name if any hypothesis strongly supported, else null>"
  }
}
```

**Expected findings:**

If any of the hypotheses (A, B, C) correlates above 0.7 for any form,
that's a candidate new term for the Task 025 candidate library. The
term would be something like `sign_predictor(r)` and the next iteration
of law discovery (Stage 2) would include it.

If none of the hypotheses correlate, sign is genuinely structured at a
level the current machinery can't explain — that's a substrate-open
finding to record.

---

## 7. Module Layout

### 7.1 New module: `src/lloyd_v4/evals/lattice_anomaly_campaign.py`

The campaign driver. Imports existing fixtures. Implements the five
sub-modules:

```python
def run_submodule_A_lattice() -> Dict: ...
def run_submodule_B_f2_anomaly() -> Dict: ...
def run_submodule_C_phase_b_spread() -> Dict: ...
def run_submodule_D_cross_form() -> Dict: ...
def run_submodule_E_sign_pattern() -> Dict: ...

def run_campaign() -> Dict:
    return {
        "campaign": "task026_lattice_anomaly_investigation",
        "r_sweep": {...},
        "submodules": {
            "A_lattice_structure": run_submodule_A_lattice(),
            "B_f2_anomaly": run_submodule_B_f2_anomaly(),
            "C_phase_b_spread": run_submodule_C_phase_b_spread(),
            "D_cross_form": run_submodule_D_cross_form(),
            "E_sign_pattern": run_submodule_E_sign_pattern(),
        }
    }

def main(): ...
```

Helper functions live in the same module:

```python
def extract_double_bits(x: float) -> int: ...  # via struct
def integer_level_or_none(value, ulp) -> Optional[int]: ...
def bootstrap_median_ratios(ratios, n_iter, subset_size) -> Dict: ...
def correlation_with_bit_pattern(values, operand_values, bit_index) -> float: ...
```

### 7.2 Output directory

`Build_Docs/Reports/task026_lattice_anomaly_investigation/`
- `campaign_output.json` — combined output of all five sub-modules
- `README.md` — short description and reproduction instructions

Plus `Build_Docs/Reports/task026_summary.md` — completion report.

---

## 8. Required Tests

`tests/test_task026_lattice_anomaly_investigation.py`:

### 8.1 Module symbol availability

All public symbols importable and callable.

### 8.2 Campaign determinism

Run the campaign twice in-test (single process). Assert byte-equal
output after key sorting. This is the campaign's own calibration.

### 8.3 Sub-module A — F3 lattice empty

For all three precisions, `A_lattice_structure["by_form"]["F3"]
["by_precision"][p]["candidate_classification"] == "lattice_empty"`.
This is the calibration zero confirmation at the lattice level.

### 8.4 Sub-module A — F4 lattice integer at float64

`A_lattice_structure["by_form"]["F4"]["by_precision"]["float64"]
["candidate_classification"] == "lattice_integer"`. Assert
`n_distinct_levels` is in [20, 50] (the V3 reference table shows ~36).
Assert `level_integer_residual_max < 1e-3`.

### 8.5 Sub-module B — record count and structure

`B_f2_anomaly["n_nonzero_float64"] == 28`. Assert
`len(B_f2_anomaly["per_point_records"]) == 28`. Assert all four
hypothesis sections have a `supported` boolean field.

### 8.6 Sub-module C — overlap count and prediction test

`C_phase_b_spread["n_overlap_points"]` is in [60, 80] (we expect 68 but
allow some slack if the recomputation produces slightly different
counts). Assert `quantisation_prediction_test` has a `supported` field
and `n_predicted_within_factor_2` and `n_predicted_within_factor_4`
are integers.

### 8.7 Sub-module D — sum cancellation

`D_cross_form["sum_F1_F2_F3_F4"]["max_abs"]` is at chain-envelope scale
or smaller (< 1e-14 in absolute terms). If the sum is dramatically
larger than any individual form, that's a calibration issue worth
flagging — the test should fail loudly.

### 8.8 Sub-module D — correlation matrix structure

The correlation matrix has F3 row and column as zeros, diagonal as 1.0,
and is symmetric. Off-diagonal entries (F1-F2, F1-F4, F2-F4) are
finite real numbers in [-1, 1].

### 8.9 Sub-module E — sign counts add up

For each form, `n_pos + n_neg + n_zero == 137` at float64. For F3,
`n_pos == n_neg == 0` and `n_zero == 137`.

### 8.10 Cross-validation against prior tasks

- `A_lattice_structure["by_form"]["F4"]["by_precision"]["float64"]
  ["n_nonzero"] == 92` (matches Task 025 F4 non-zero count).
- `B_f2_anomaly["n_nonzero_float64"] == 28` (matches Task 025 F2
  non-zero count).
- `D_cross_form` confirms F3 entries are all zero (matches Task 024b
  F3 silence).

### 8.11 Determinism (cross-process)

Run the campaign twice in separate processes via subprocess. Diff
output JSONs byte-for-byte.

### 8.12 Source purity

No `import math`, `import scipy`, `import sympy`, `import sklearn`,
`import mpmath`. No `numpy.sqrt`, `numpy.cos`, `numpy.exp`. Decimal
admitted in oracle pathway only.

### 8.13 Manifest non-regression

`len(lloyd_v4.primitives.__all__)` unchanged from post-025 baseline.

---

## 9. Required Commands

```bash
# Pre-task baseline
git status                                            # clean tree
python -m pytest -q tests/ 2>&1 | tail -3             # 443 passing

# Implementation
# ... campaign module, test file, report directory ...

# Verification
python -m pytest -q tests/test_task026_lattice_anomaly_investigation.py
python -m pytest -q tests/                            # full suite still green
python -m pytest -q tests/test_task001_source_purity.py

# Run the campaign
PYTHONPATH=src python -m lloyd_v4.evals.lattice_anomaly_campaign

# Determinism verification
PYTHONPATH=src python -m lloyd_v4.evals.lattice_anomaly_campaign \
    --output /tmp/lattice_anomaly_repeat.json
diff Build_Docs/Reports/task026_lattice_anomaly_investigation/campaign_output.json \
     /tmp/lattice_anomaly_repeat.json

# Manifest audits
python -m pytest -q \
    tests/test_task010a_layer_manifest_machine_readable.py \
    tests/test_task010b_export_drift.py \
    tests/test_task010b_manifest_completeness.py \
    tests/test_task010c_no_unregistered_operations.py \
    tests/test_task010c_lineage_terminates_in_primitive.py \
    tests/test_task010c_no_chain_cycles.py

# Commit and push
git add -A
git status
git commit -m "Task 026: Lattice and anomaly investigation campaign"
git push origin main
```

The final commit and push are non-negotiable.

---

## 10. Non-Goals

- **No new primitives, status families, or manifest entries.**
- **No SR or Bell fixture work** (those are Stage 2 — Task 027, 028).
- **No envelope predictor.** This task discovers more invariants; the
  predictor remains a downstream task informed by Stage 1's findings.
- **No deconvolution.** Same reasoning.
- **No expansion of the Task 025 candidate library mid-flight.** If a
  new candidate term is suggested by 026.E, it gets recorded as a
  forward reference for Stage 2 enrichment, not retro-added to 025.
- **No retro-fitting hypotheses.** Each sub-module's hypothesis space
  is declared in this spec. If the data doesn't fit any of them, the
  result is "open" — record what was measured and stop.
- **No "model confirmed" or "model rejected" verdicts.** The campaign
  produces classifications and characterisations. Interpretation is
  downstream.
- **No long-double precision.** Float32, float64, decimal-50 only.
- **No platform-specific FMA testing.** That's a separate axis we
  haven't yet introduced.

---

## 11. Completion Report Template

`Build_Docs/Reports/task026_summary.md` must contain:

### Scope

One paragraph per sub-module.

### Test count

Pre-task baseline (post-025): 443.
Post-Task 026: 443 + N.

### Files changed

Bulleted list.

### Sub-module A — Lattice findings

A table with rows F1, F2, F3, F4 and columns:
- candidate_classification at float64
- n_distinct_levels at float64
- level_integer_residual_max at float64
- regional level density distribution

### Sub-module B — F2 anomaly resolution

State which of the four hypotheses (small-sample, float32-mostly-zero,
sign-flip-dominance, lattice-mismatch) the data supports. If multiple
hypotheses are partially supported, state which is primary. If none
are clearly supported, state "anomaly remains open" with the per-point
table summarised.

### Sub-module C — Phase B spread

Headline number: how many of the 68 overlap points are explained by
the quantisation-prediction test. State whether the spread is
fully-explained, partially-explained, or open.

### Sub-module D — Cross-form structure

The 16-pattern joint-zero histogram (most common patterns). The sum
S(r) distribution. Any tested linear relation that held within
tolerance. Any unexpected cross-form invariants flagged for follow-up.

### Sub-module E — Sign patterns

Per-form sign counts. Which hypothesis (A, B, C) correlated above 0.7
for any form. If a candidate new term emerged for the law-discovery
library, name it.

### Cross-validation

Confirmation that 026 results agree with 024b's F-value table and
025's non-zero counts. Any discrepancy must be explained.

### Honest observations

The standard section. Anything that didn't match design-time
prediction.

### Forward references

For each sub-module, what (if anything) the result suggests as a Stage
2+ task. These are notes, not draft specs.

### Limits

Standard.

### Audits

pytest, source purity, manifest non-regression, byte-identical re-runs.
git commit hash, git push confirmation.

---

## 12. Acceptance Criteria

1. Pre-task baseline confirmed (443 tests green).
2. New campaign module exists at
   `src/lloyd_v4/evals/lattice_anomaly_campaign.py`.
3. `tests/test_task026_lattice_anomaly_investigation.py` exists and
   all tests pass.
4. Full test suite green.
5. Campaign produces deterministic `campaign_output.json` containing
   all five sub-module sections with the documented JSON structure.
6. All cross-validation tests against prior tasks pass.
7. Completion report `task026_summary.md` is filled per §11.
8. All changes committed and pushed to `origin/main`.

A "passing" campaign is one where the five sub-modules run to
completion and produce typed output per the spec. Whether any
particular hypothesis is supported is empirical — the campaign
succeeds whether it resolves anomalies or precisely characterises them
as open.

---

## 13. Discipline Notes (Forward References)

### What this campaign's findings inform

- **Lattice detection (026.A)** becomes substrate machinery for Task
  025-style discovery in Stage 2 fixtures (SR, Bell). The
  `path_law_lattice_structured` status becomes diagnosable, not just
  declarable.
- **F2 resolution (026.B)** either dismisses an anomaly or surfaces a
  new substrate question for Stage 2 to address.
- **Phase B explanation (026.C)** if confirmed, lets us predict
  per-point precision-scaling exactly, not just median-scaling.
- **Cross-form invariants (026.D)** are typed promotion candidates if
  found.
- **Sign-pattern candidates (026.E)** are inputs to an enriched
  candidate library for Stage 2 law discovery.

### What this task explicitly does not do

- No modifications to existing V4 primitives.
- No promotion to substrate — all observations stay in campaign output.
- No claim that the IEEE 754 instrument model is "confirmed" or
  "rejected" globally.

### The deeper claim this task tests

The hypothesis that emerged from Tasks 017b, 024b, 025 is: IEEE 754
arithmetic paths produce typed, deterministic invariant signatures that
V4 can characterise. This campaign tests that hypothesis at the level
of detail the prior tasks couldn't reach — lattice structure,
per-point scaling, cross-form structure, sign predictability. If those
detailed observations consistent with the hypothesis, Stage 2 (cross-
fixture) is licensed. If they reveal substrate-level surprises, Stage 2
adjusts accordingly.

---

*End of Codex Task 026 specification.*
