# Task 026 Lattice And Anomaly Investigation

This directory contains the deterministic Stage 1 lattice/anomaly campaign for
the existing Schwarzschild four-form fixture.

## Reproduction

```bash
PYTHONPATH=src python -m lloyd_v4.evals.lattice_anomaly_campaign
```

The command writes `campaign_output.json`. The campaign is report-only: it adds
no V4 primitive, status family, manifest entry, or transition rule.

## Headline Findings

- F4 float64 is an integer ULP lattice on `ulp(f)`: 92 non-zero points,
  35 distinct integer levels, max integer residual `0.0`.
- F1 float64 is also integer on the same lattice, but only at levels `-1`
  and `1`.
- F2 float64 is not integer on `ulp(f)`: 28 non-zero points, 5 rounded
  levels, max integer residual `0.5`. This is the main anomaly.
- F3 is lattice-empty at float32, float64, and decimal-50.
- F4 Phase B spread is fully explained by quantisation: 68 of 68 overlap
  points were predicted within factor 2 and factor 4.

## Sub-Modules

- `A_lattice_structure`: per-form lattice classification by precision.
- `B_f2_anomaly`: F2 per-point anomaly decomposition.
- `C_phase_b_spread`: F4 float32/float64 ratio-spread decomposition.
- `D_cross_form`: joint zero masks, cross-form sums, differentials, and
  linear relation checks.
- `E_sign_pattern`: sign sequences, sign correlations, and candidate sign
  predictor checks.
