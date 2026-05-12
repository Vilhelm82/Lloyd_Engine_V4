# Task 026 Summary - Lattice And Anomaly Investigation

## Scope

Sub-module A enumerated per-form ULP lattice structure across float32,
float64, and decimal-50. It tested whether observed four-form values are
integer multiples of `ulp(f)`.

Sub-module B deepened F2's precision-scaling anomaly with per-point float32,
float64, decimal-50, sign, ratio, and lattice-level records.

Sub-module C characterised F4 Phase B spread across the float32/float64 overlap
points and tested whether integer-level quantisation fully predicts the ratio
spread.

Sub-module D measured cross-form joint zero masks, four-form sums,
differentials, correlations, and declared linear relations.

Sub-module E measured sign histograms, sign sequences, cross-form sign
agreement, level parity, operand-bit correlation, and factored-sqrt rounding
direction correlation.

No primitives, status families, manifests, protocols, or transition rules were
added.

## Test Count

- Pre-task baseline: 443 tests passing.
- Post-Task 026 collection: 456 tests.
- Added tests: 13 in `tests/test_task026_lattice_anomaly_investigation.py`.

## Files Changed

- `src/lloyd_v4/evals/lattice_anomaly_campaign.py`
- `tests/test_task026_lattice_anomaly_investigation.py`
- `Build_Docs/Reports/task026_lattice_anomaly_investigation/campaign_output.json`
- `Build_Docs/Reports/task026_lattice_anomaly_investigation/README.md`
- `Build_Docs/Reports/task026_summary.md`
- `Build_Docs/Agent_tasks/Completed/codex_task026_lattice_anomaly_investigation.md`

## Sub-Module A - Lattice Findings

| Form | Float64 classification | Distinct levels | Max integer residual | Regional distinct levels |
| --- | --- | ---: | ---: | --- |
| F1 | `lattice_integer` | 2 | 0.0 | near 2, middle 2, far 2 |
| F2 | `non_integer_lattice` | 5 | 0.5 | near 0, middle 1, far 5 |
| F3 | `lattice_empty` | 0 | 0.0 | near 0, middle 0, far 0 |
| F4 | `lattice_integer` | 35 | 0.0 | near 27, middle 11, far 2 |

The headline anomaly is F2: its values sit on half-level offsets relative to
`ulp(f)`, so the integer-lattice claim does not hold cleanly for that path.

## Sub-Module B - F2 Anomaly Resolution

F2 produced 28 non-zero float64 points. The campaign did not support the
small-sample or float32-mostly-zero explanations:

- Small-sample bootstrap: IQR `0.0`, range `[536870912.0, 671088640.0]`,
  not supported.
- Float32 mostly zero: 10 of 28 float64-nonzero points were zero at float32,
  fraction `0.35714285714285715`, not supported.
- Sign disagreement: 10 of 18 both-nonzero points disagreed in sign,
  fraction `0.5555555555555556`, supported.
- Lattice mismatch: 2 predictable-scaling points and 16 unrelated points,
  supported.

Primary classification: `lattice_mismatch`. The anomaly is therefore not just a
ratio-statistic artefact; F2 has path-specific half-level lattice structure.

## Sub-Module C - Phase B Spread

F4 had 68 float32/float64 overlap points. The median ratio was
`536870912.0`, matching `2^29`.

The quantisation prediction explained 68 of 68 points within factor 2 and 68 of
68 points within factor 4. Median predicted/observed factor was `1.0`.

Spread status: fully explained by integer-level quantisation. Ten points were
flagged as factor-of-4 outliers relative to the global `2^29` median, but the
per-point lattice prediction explained them.

## Sub-Module D - Cross-Form Structure

Non-zero joint zero-mask patterns:

| Pattern | Count |
| --- | ---: |
| `0010` | 1 |
| `0011` | 15 |
| `0110` | 47 |
| `0111` | 6 |
| `1010` | 3 |
| `1011` | 9 |
| `1110` | 41 |
| `1111` | 15 |

Sum `F1 + F2 + F3 + F4` stayed at chain scale:

- min `-2.7755575615628914e-16`
- max `3.885780586188048e-16`
- median `0.0`
- IQR `1.3530843112619095e-16`
- max absolute `3.885780586188048e-16`
- non-zero count `122`

Declared linear relations all held within `1e-14`:

- `F1 - F2`, max residual `5.551115123125783e-17`
- `F2 - 2*F1`, max residual `1.6653345369377348e-16`
- `F4 - F1`, max residual `3.885780586188048e-16`

The strongest cross-form correlation was F1/F2 at
`0.7631117166952837`; F3 remained zero by construction.

## Sub-Module E - Sign Patterns

| Form | Positive | Negative | Zero |
| --- | ---: | ---: | ---: |
| F1 | 34 | 35 | 68 |
| F2 | 10 | 18 | 109 |
| F3 | 0 | 0 | 137 |
| F4 | 45 | 47 | 45 |

Cross-form sign agreement counts:

- F1/F2: 16
- F1/F4: 23
- F2/F4: 4

No sign hypothesis crossed the 0.7 support line. The best operand-bit
correlations were F1 bit 30 at `0.3071496493479117`, F2 bit 2 at
`0.5017348819226064`, and F4 bit 5 at `0.24269373433915167`. The
strongest factored-sqrt rounding-direction correlation was F2 at
`0.5962847939999439`.

No new sign term is recommended for the Task 025 law library yet.

## Cross-Validation

- F4 float64 lattice non-zero count: 92, matching the observed-value count from
  the four-form battery.
- F2 anomaly non-zero float64 count: 28, matching the observed-value count.
- F3 is zero across the lattice, cross-form, and sign modules.

## Honest Observations

- F2 was expected to be sparse integer lattice-like, but it is not integer on
  `ulp(f)`; the half-level residual of `0.5` is the primary Task 026 surprise.
- F4's Phase B spread is not open: the per-point integer-level prediction
  explains all overlap points within factor 2.
- The declared cross-form linear relations hold at chain scale, which makes the
  cross-form structure more coherent than the per-form sparse fits alone imply.
- Sign structure remains below the current candidate support line.

## Forward References

- A: Add half-level lattice detection before promoting lattice diagnostics.
- B: Treat F2 as a half-level or mixed-lattice path in Stage 2, rather than as a
  mere sparse-ratio artefact.
- C: Use per-point level-ratio scaling for future precision-scaling axes.
- D: Consider cross-form relation checks as typed promotion candidates.
- E: Keep sign-predictor enrichment open, but do not add a new candidate term
  until stronger evidence appears.

## Limits

- Existing Schwarzschild four-form fixture only.
- Float32, float64, and decimal-50 only.
- No new fixtures, long-double path, platform FMA axis, solver behavior,
  deconvolution, envelope predictor, or substrate promotion.

## Audits

- `python -m pytest -q tests/test_task026_lattice_anomaly_investigation.py`
- `python -m pytest -q tests/`
- `python -m pytest -q tests/test_task001_source_purity.py`
- `PYTHONPATH=src python -m lloyd_v4.evals.lattice_anomaly_campaign`
- `PYTHONPATH=src python -m lloyd_v4.evals.lattice_anomaly_campaign --output /tmp/lattice_anomaly_repeat.json`
- `diff Build_Docs/Reports/task026_lattice_anomaly_investigation/campaign_output.json /tmp/lattice_anomaly_repeat.json`
- `python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py`
