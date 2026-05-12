# Task 028 Report Bundle

This directory contains the Task 028 conditional-mask, joint signed-lattice,
pure-algebraic, and three-fixture comparison artifacts.

## Files

- `conditional_mask_output.json`: conditional event decomposition for
  Schwarzschild and SR polarity masks.
- `conditional_mask_table.csv`: flat table of the conditional-mask counts.
- `joint_signed_lattice_output.json`: joint `(level, sign)` histograms for
  Schwarzschild and SR on the reference grid.
- `joint_signed_lattice_table.csv`: flat joint-state table.
- `pure_algebraic_four_form_battery.json`: pure-algebraic four-form values on
  the canonical 137-point x-grid.
- `pure_algebraic_lattice_campaign_output.json`: pure-algebraic lattice
  analysis.
- `pure_algebraic_polarity_grid_stability.json`: pure-algebraic polarity grid
  stability campaign.
- `pure_algebraic_polarity_grid_table.csv`: pure-algebraic polarity table.
- `pure_algebraic_region_split_table.csv`: pure-algebraic region split table.
- `pure_algebraic_precision_overlap_table.csv`: pure-algebraic precision
  overlap table.
- `three_fixture_comparison.json`: Schwarzschild, SR, and pure-algebraic
  comparison.
- `three_fixture_per_pair_table.csv`: aggregate pair comparison.
- `three_fixture_lattice_grain_table.csv`: lattice comparison.
- `three_fixture_sterbenz_boundary_table.csv`: Sterbenz boundary comparison.

## Headline

`chain_property_supported`.

The pure-algebraic fixture preserves the same substrate-level invariants as the
two existing fixtures: F1/F2 grid-stable parallel polarity, F3 silence, F2
non-integer lattice grain, F4 integer lattice character, and the predicted
Sterbenz-side direction.

## Reproduction

From the repository root:

```bash
PYTHONPATH=src python -m lloyd_v4.evals.conditional_mask_analysis
PYTHONPATH=src python -m lloyd_v4.evals.joint_signed_lattice_analysis
PYTHONPATH=src python -m lloyd_v4.evals.pure_algebraic_lattice_campaign
PYTHONPATH=src python -m lloyd_v4.evals.pure_algebraic_polarity_grid_stability
PYTHONPATH=src python -m lloyd_v4.evals.cross_fixture_comparison
```
