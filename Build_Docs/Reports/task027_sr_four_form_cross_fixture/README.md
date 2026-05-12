# Task 027 SR Four-Form Cross-Fixture

This directory contains the SR time-dilation four-form battery, SR lattice
campaign, SR polarity grid-stability campaign, and side-by-side comparison with
the existing Schwarzschild reports.

## Reproduction

```bash
PYTHONPATH=src python -m lloyd_v4.evals.sr_lattice_campaign
PYTHONPATH=src python -m lloyd_v4.evals.sr_polarity_grid_stability
PYTHONPATH=src python -m lloyd_v4.evals.cross_fixture_comparison
```

## Headline

Headline classification: `chain_property_partial`.

SR matches the Schwarzschild fixture on the load-bearing F1/F2 grid-stable
parallel polarity coupling, F3 silence, F2 half-level lattice behavior, F4
integer lattice behavior, and predicted Sterbenz direction. It diverges in
F1/F4 power (`open_underpowered` rather than `depolarized_invariant`) and in
F4 lattice grain (10 SR float64 levels versus 35 Schwarzschild float64 levels).

## SR Aggregates

| Pair | Aggregate |
| --- | --- |
| F1_F2 | `grid_stable_polarity_coupling` |
| F1_F4 | `open_underpowered` |
| F2_F4 | `reference_grid_only` |

F1/F4 did not fail the negative control; all grids were underpowered for that
pair after the precision-consistent promotion gate. F2/F4 was not promoted to
grid-stable polarity coupling.

## Artifacts

- `sr_four_form_battery.json`
- `sr_lattice_campaign_output.json`
- `sr_polarity_grid_stability.json`
- `sr_polarity_grid_table.csv`
- `sr_region_split_table.csv`
- `sr_precision_overlap_table.csv`
- `cross_fixture_comparison.json`
- `cross_fixture_per_pair_table.csv`
- `cross_fixture_lattice_grain_table.csv`
- `cross_fixture_sterbenz_boundary_table.csv`
