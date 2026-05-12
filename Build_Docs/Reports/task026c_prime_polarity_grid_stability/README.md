# Task 026c-prime Polarity Grid Stability

This report directory contains the deterministic polarity-grid stability
campaign for the existing Schwarzschild four-form fixture.

## Reproduction

```bash
PYTHONPATH=src python -m lloyd_v4.evals.polarity_grid_stability
```

The command writes:

- `campaign_output.json`
- `polarity_grid_table.csv`
- `region_split_table.csv`
- `precision_overlap_table.csv`

## Grids

| Grid | Seed | n_after_dedup | Clamp low/high |
| --- | ---: | ---: | --- |
| reference | 0 | 137 | 0 / 0 |
| coarse_perturbation | 1042 | 121 | 17 / 1 |
| fine_perturbation | 2317 | 137 | 1 / 0 |
| independent_uniform | 4099 | 137 | 0 / 0 |

The coarse-grid clamp behavior differs from the sanity benchmark: this seed
concentrates boundary clamping at the low endpoint rather than the high endpoint.
The campaign records the measured behavior and does not re-seed.

## Headline Findings

- F1/F2: `grid_stable_polarity_coupling`
- F1/F4: `depolarized_invariant`
- F2/F4: `open_underpowered`

The F1/F4 negative control passed under the precision-consistent coupling gate.
F2/F4 is explicitly blocked from promotion because multiple grids are
underpowered.

## Report Statuses

- `reference_grid_confirmed`
- `grid_stable_supported`
- `grid_stability_rejected`
- `depolarized_supported`
- `underpowered_grid`
- `grid_stable_polarity_coupling`
- `depolarized_invariant`
- `reference_grid_only`
- `open_underpowered`
- `negative_control_failed`

These are report classifications only. They are not runtime status enums and
are not registered in the V4 substrate manifests.
