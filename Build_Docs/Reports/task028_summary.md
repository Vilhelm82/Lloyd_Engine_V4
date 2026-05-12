# Task 028 Summary - Conditional Masks, Joint Signed-Lattice, and Pure Algebraic Control

## Scope

Task 028 completed three linked observation campaigns:

- Conditional-mask decomposition for existing Schwarzschild and SR polarity
  outputs.
- Joint signed-lattice histograms for existing Schwarzschild and SR reference
  grids.
- A pure-algebraic four-form control with lattice, polarity-grid stability, and
  three-fixture comparison against Schwarzschild and SR.

No V4 primitive, runtime status enum, manifest entry, transition rule, solver
behavior, or Task 025 law-library term was added.

## Baseline

- Pre-task HEAD: `75a12b0 Task 027: SR four-form battery and cross-fixture comparison`.
- Pre-task suite: 487 tests passing.

## Test Results

- Added tests: 21 in `tests/test_task028_conditional_masks_joint_lattice_pure_algebraic.py`.
- Post-task collection/full suite: 508 tests passing.

## Files Changed

- `src/lloyd_v4/evals/conditional_mask_analysis.py`
- `src/lloyd_v4/evals/joint_signed_lattice_analysis.py`
- `src/lloyd_v4/evals/pure_algebraic_four_form.py`
- `src/lloyd_v4/evals/pure_algebraic_lattice_campaign.py`
- `src/lloyd_v4/evals/pure_algebraic_polarity_grid_stability.py`
- `src/lloyd_v4/evals/cross_fixture_comparison.py`
- `tests/test_task027_sr_four_form_cross_fixture.py`
- `tests/test_task028_conditional_masks_joint_lattice_pure_algebraic.py`
- `Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/*`
- `Build_Docs/Reports/task028_summary.md`
- `Build_Docs/Agent_tasks/Completed/codex_task028_conditional_masks_joint_lattice_pure_algebraic.md`

## Conditional Masks

F1/F2 conditional counts:

| Fixture | Grid | Precision | F1-only | F2-only | Co-fire | P(F2\|F1) | P(F1\|F2) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Schwarzschild | reference | float32 | 44 | 10 | 15 | 0.254237 | 0.600000 |
| Schwarzschild | reference | float64 | 53 | 12 | 16 | 0.231884 | 0.571429 |
| Schwarzschild | coarse_perturbation | float32 | 39 | 7 | 15 | 0.277778 | 0.681818 |
| Schwarzschild | coarse_perturbation | float64 | 41 | 7 | 17 | 0.293103 | 0.708333 |
| Schwarzschild | fine_perturbation | float32 | 53 | 11 | 12 | 0.184615 | 0.521739 |
| Schwarzschild | fine_perturbation | float64 | 49 | 7 | 19 | 0.279412 | 0.730769 |
| Schwarzschild | independent_uniform | float32 | 14 | 28 | 51 | 0.784615 | 0.645570 |
| Schwarzschild | independent_uniform | float64 | 13 | 36 | 57 | 0.814286 | 0.612903 |
| SR | reference | float32 | 0 | 64 | 28 | 1.000000 | 0.304348 |
| SR | reference | float64 | 0 | 61 | 34 | 1.000000 | 0.357895 |
| SR | coarse_perturbation | float32 | 0 | 53 | 32 | 1.000000 | 0.376471 |
| SR | coarse_perturbation | float64 | 0 | 69 | 24 | 1.000000 | 0.258065 |
| SR | fine_perturbation | float32 | 0 | 63 | 33 | 1.000000 | 0.343750 |
| SR | fine_perturbation | float64 | 0 | 60 | 27 | 1.000000 | 0.310345 |
| SR | independent_uniform | float32 | 0 | 59 | 22 | 1.000000 | 0.271605 |
| SR | independent_uniform | float64 | 0 | 65 | 24 | 1.000000 | 0.269663 |

Reference float64 all-pair decomposition:

| Fixture | Pair | Left-only | Right-only | Co-fire | Same sign | Opposite sign |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Schwarzschild | F1_F2 | 53 | 12 | 16 | 16 | 0 |
| Schwarzschild | F1_F4 | 21 | 44 | 48 | 23 | 25 |
| Schwarzschild | F2_F4 | 24 | 88 | 4 | 4 | 0 |
| SR | F1_F2 | 0 | 61 | 34 | 34 | 0 |
| SR | F1_F4 | 30 | 23 | 4 | 4 | 0 |
| SR | F2_F4 | 82 | 14 | 13 | 12 | 1 |

Headline observation: the F1/F2 co-fire subset is exactly where parallel
polarity lives, but the mask mechanism is fixture-dependent. Schwarzschild has
measurable F1-only and F2-only contributors on every grid and precision. SR has
F1 as a subset of the wider F2 mask on every grid and precision, with substantial
F2-only counts.

## Joint Signed-Lattice

State counts:

| Fixture | Precision | Joint states | Most populated state | Count |
| --- | --- | ---: | --- | ---: |
| Schwarzschild | float32 | 66 | `L1=0,L2=0,L4=0,S1=0,S2=0,S4=0` | 21 |
| Schwarzschild | float64 | 67 | `L1=0,L2=0,L4=0,S1=0,S2=0,S4=0` | 15 |
| Schwarzschild | decimal_50 | 13 | `L1=0,L2=0,L4=0,S1=0,S2=0,S4=0` | 51 |
| SR | float32 | 33 | `L1=0,L2=0,L4=0,S1=0,S2=0,S4=0` | 26 |
| SR | float64 | 29 | `L1=0,L2=0,L4=0,S1=0,S2=0,S4=0` | 28 |
| SR | decimal_50 | 11 | `L1=0,L2=0,L4=0,S1=0,S2=0,S4=0` | 35 |

Top-state and conditional summaries are fully serialized in
`joint_signed_lattice_output.json`. The float64 conditional summaries show:

- Schwarzschild F1 level `+1` maps F2 into `{0, +0.5, +1, +2}` and F1 level
  `-1` maps F2 into `{0, -0.5, -1, -1.5, -2}`.
- SR has no F1 level `+1` cases at float64; F1 level `-1` maps F2 into
  `{-0.5, -1, -1.5}`.
- F1/F2 aligned co-fire is concentrated in the F4-zero band for both fixtures,
  while most non-zero F4 bands are single-form or silent for F1/F2.

Headline observation: the joint state carries extra descriptive structure. F1
sign constrains the F2 level side in the co-fire subset, and F4 level bands show
where F1/F2 coupling is absent rather than merely what the marginal lattice
histograms contain. This remains evidence only, not a promoted substrate object.

## Pure Algebraic Grid

The canonical x-grid has 137 strictly increasing values from `0.01` to `0.99`.
The four-form operand has no fixture semantics; F4 uses the split routing
`(1 - x/2) - x/2`.

## Pure Algebraic Four-Form Counts

| Form | float32 non-zero | float64 non-zero | decimal-50 non-zero |
| --- | ---: | ---: | ---: |
| F1 | 65 | 70 | 45 |
| F2 | 60 | 64 | 128 |
| F3 | 0 | 0 | 0 |
| F4 | 39 | 40 | 51 |

F3 remained exactly zero across float32, float64, and decimal-50.

## Pure Algebraic Lattice

| Form | Precision | Classification | Non-zero | Distinct levels | Max residual |
| --- | --- | --- | ---: | ---: | ---: |
| F1 | float32 | `non_integer_lattice` | 65 | 3 | 0.0 |
| F1 | float64 | `lattice_integer` | 70 | 2 | 0.0 |
| F1 | decimal_50 | `single_level` | 45 | 1 | 2.8823037615171175e-34 |
| F2 | float32 | `non_integer_lattice` | 60 | 9 | 0.25 |
| F2 | float64 | `non_integer_lattice` | 64 | 8 | 0.25 |
| F2 | decimal_50 | `single_level` | 128 | 1 | 1.4411518807585587e-33 |
| F3 | float32 | `lattice_empty` | 0 | 0 | 0.0 |
| F3 | float64 | `lattice_empty` | 0 | 0 | 0.0 |
| F3 | decimal_50 | `lattice_empty` | 0 | 0 | 0.0 |
| F4 | float32 | `lattice_integer` | 39 | 12 | 0.0 |
| F4 | float64 | `lattice_integer` | 40 | 11 | 0.0 |
| F4 | decimal_50 | `single_level` | 51 | 1 | 8.646911284551352e-33 |

## Pure Algebraic Polarity

| Pair | Aggregate | Per-grid statuses |
| --- | --- | --- |
| F1_F2 | `grid_stable_polarity_coupling` | reference confirmed; all three non-reference grids supported |
| F1_F4 | `open_underpowered` | all grids rejected precision-supported coupling; negative control passed |
| F2_F4 | `open_underpowered` | coarse grid underpowered; bottle-cap discipline blocked promotion |

## Three-Fixture Comparison

Aggregate polarity:

| Pair | Schwarzschild | SR | Pure algebraic |
| --- | --- | --- | --- |
| F1_F2 | `grid_stable_polarity_coupling` | `grid_stable_polarity_coupling` | `grid_stable_polarity_coupling` |
| F1_F4 | `depolarized_invariant` | `open_underpowered` | `open_underpowered` |
| F2_F4 | `open_underpowered` | `reference_grid_only` | `open_underpowered` |

Float64 lattice:

| Form | Schwarzschild | SR | Pure algebraic |
| --- | --- | --- | --- |
| F1 | `lattice_integer`, 69 non-zero, 2 levels | `lattice_integer`, 34 non-zero, 3 levels | `lattice_integer`, 70 non-zero, 2 levels |
| F2 | `non_integer_lattice`, 28 non-zero, 5 levels | `non_integer_lattice`, 95 non-zero, 5 levels | `non_integer_lattice`, 64 non-zero, 8 levels |
| F3 | `lattice_empty`, 0 non-zero | `lattice_empty`, 0 non-zero | `lattice_empty`, 0 non-zero |
| F4 | `lattice_integer`, 92 non-zero, 35 levels | `lattice_integer`, 27 non-zero, 10 levels | `lattice_integer`, 40 non-zero, 11 levels |

Sterbenz boundary:

| Fixture | Boundary | Below count/density | Above count/density | Predicted | Observed | Supports |
| --- | ---: | --- | --- | --- | --- | --- |
| Schwarzschild | 4.0 | 6 / 0.053571 | 22 / 0.88 | above higher | above higher | yes |
| SR | 0.7071067811865476 | 86 / 0.895833 | 9 / 0.219512 | below higher | below higher | yes |
| Pure algebraic | 0.5 | 55 / 0.797101 | 9 / 0.132353 | below higher | below higher | yes |

## Headline Finding

`chain_property_supported`.

All three fixtures agree on the requested substrate-level invariants: F1/F2
grid-stable parallel polarity, F3 silence, F2 non-integer lattice grain, F4
integer lattice character, and the predicted Sterbenz-side direction. The pure
algebraic control therefore supports the conclusion that the observed pattern is
an arithmetic-chain property rather than a fixture-specific property.

## Honest Observations

- The conditional masks do not reduce to one universal subset relation:
  Schwarzschild has two-sided exclusive contributors, while SR has F1 inside a
  wider F2 mask.
- Pure F2/F4 has strong grids, but the coarse grid is underpowered, so the
  aggregate remains `open_underpowered`.
- Decimal-50 pure-algebraic lattice collapses several forms to single-level
  behavior while preserving F3 silence.

## Limits

- Pure algebraic F4 tested only the `(1 - x/2) - x/2` split routing.
- No additional fixture, long-double path, platform FMA axis, or alternate
  split-routing family was tested.
- Conditional masks and joint signed-lattice states were reported only as typed
  evidence; no substrate promotion was performed.

## Forward References

- Task 029 can add a new fixture if cross-fixture motivation persists.
- Task 030 can add operation-level Sterbenz annotations as the substrate-deepening
  task.
- Substrate promotion should be considered only if the joint-state structure is
  converted into a derivable law rather than a descriptive histogram.

## Verification

- `git log -1 --oneline`
- `python -m pytest -q tests/`
- `PYTHONPATH=src python -m lloyd_v4.evals.conditional_mask_analysis`
- `PYTHONPATH=src python -m lloyd_v4.evals.conditional_mask_analysis --output /tmp/conditional_mask_repeat.json`
- `diff Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/conditional_mask_output.json /tmp/conditional_mask_repeat.json`
- `PYTHONPATH=src python -m lloyd_v4.evals.joint_signed_lattice_analysis`
- `PYTHONPATH=src python -m lloyd_v4.evals.joint_signed_lattice_analysis --output /tmp/joint_lattice_repeat.json`
- `diff Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/joint_signed_lattice_output.json /tmp/joint_lattice_repeat.json`
- `PYTHONPATH=src python -m lloyd_v4.evals.pure_algebraic_polarity_grid_stability`
- `PYTHONPATH=src python -m lloyd_v4.evals.pure_algebraic_polarity_grid_stability --output /tmp/pure_alg_polarity_repeat.json`
- `diff Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/pure_algebraic_polarity_grid_stability.json /tmp/pure_alg_polarity_repeat.json`
- `PYTHONPATH=src python -m lloyd_v4.evals.cross_fixture_comparison`
- `PYTHONPATH=src python -m lloyd_v4.evals.cross_fixture_comparison --output /tmp/three_fixture_repeat.json`
- `diff Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/three_fixture_comparison.json /tmp/three_fixture_repeat.json`
- `python -m pytest -q tests/test_task028_conditional_masks_joint_lattice_pure_algebraic.py`
- `python -m pytest -q tests/`
- `python -m pytest -q tests/test_task001_source_purity.py`
- `python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py`
- `rg "numpy\\.random|np\\.random|scipy|sympy|mpmath" src/lloyd_v4/evals/conditional_mask_analysis.py src/lloyd_v4/evals/joint_signed_lattice_analysis.py src/lloyd_v4/evals/pure_algebraic_four_form.py src/lloyd_v4/evals/pure_algebraic_lattice_campaign.py src/lloyd_v4/evals/pure_algebraic_polarity_grid_stability.py`
