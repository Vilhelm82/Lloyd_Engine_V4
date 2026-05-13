# Task 029c Headline Classification

Headline: `chain_property_universal`

| Invariant | Prediction | Observed | Match? |
| --- | --- | --- | --- |
| F1||F2 grid-stable polarity coupling | 100% sign agreement, p < 0.01, all 4 grids cofire >= 10 | aggregate=grid_stable_polarity_coupling; reference_fraction=1.0; reference_p=8.077935669463161e-28; grid_cofire={'reference': 91, 'coarse_perturbation': 89, 'fine_perturbation': 83, 'independent_uniform': 94} | Y |
| F3 identity silence | F3 == 0.0 at every cell | all polarity-grid F3 nonzero counts are zero | Y |
| F2 non-integer lattice grain | non-integer lattice character | classification=non_integer_lattice; residual_max=0.25 | Y |
| F4 integer lattice character | integer-lattice classification | classification=lattice_integer; residual_max=0.0 | Y |
| Sterbenz boundary at x = 1/2 | location at x = 1/2, below density > above | location=0.5; below_density=0.9420289855072463; above_density=0.4852941176470588; direction=below_boundary_higher | Y |

The headline is grounded in Section A only. Section B F5+ predictions are reported in the task summary and campaign JSON.
