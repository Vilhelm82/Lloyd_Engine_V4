# Task 034 Summary - Schwarzschild-Quartic Transformed n=4

## Scope

Task 034 added a Schwarzschild-shape quartic transformed-operand fixture using the canonical 137-point `r` sweep, direct operand `1 - 2 / r`, alternate routing `(r - 2) / r`, and composed `numpy.sqrt(numpy.sqrt(...))`. The campaign ran the four-form battery, lattice campaign, polarity grid stability, Sterbenz boundary observation, and a multiplication-parenthesization observation. The load-bearing measurement was the float64 F2 lattice grain.

## Pre-registration

- Commit: `6a81d9d Task 034 pre-registration: Schwarzschild-quartic transformed-operand n=4 fixture`
- Full hash: `6a81d9d19c1d6f24f3232f74abe1291c8f846ed1`
- Date: `2026-05-14 11:43:41 +1000`
- File: `Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/pre_registration.md`
- Status: byte-identical to the pre-registration commit at completion.

## Fixture Construction

- Grid: canonical 137-point `schwarzschild_four_form.sweep_r_values`, `r in [2.005, 10.0]`.
- Direct operand: `1 - 2 / r`.
- Alternate operand: `(r - 2) / r`.
- Radical: `R = numpy.sqrt(numpy.sqrt(1 - 2 / r))`.
- Product grouping: `(R * R) * (R * R)`.
- Forms: F1=`R^4 - (1 - 2/r)`, F2=`R^4 - 1 + 2/r`, F3=`R - sqrt(sqrt(1 - 2/r))`, F4=`R - sqrt(sqrt((r - 2)/r))`.
- Full point-level values are in `schwarzschild_quartic_four_form_battery.json`.

## Lattice Classification

| Form | float32 class | float32 nonzero | float32 grain | float64 class | float64 nonzero | float64 grain |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| `F1` | `lattice_integer` | `102` | `0.0` | `lattice_integer` | `101` | `0.0` |
| `F2` | `non_integer_lattice` | `35` | `0.25` | `non_integer_lattice` | `37` | `0.25` |
| `F3` | `lattice_empty` | `0` | `0.0` | `lattice_empty` | `0` | `0.0` |
| `F4` | `lattice_integer` | `70` | `0.0` | `lattice_integer` | `75` | `0.0` |

## F2 Grain Comparison

| Fixture | n | Operand | F2 grain |
| --- | ---: | --- | ---: |
| Schwarzschild | 2 | transformed | `0.5` |
| SR | 2 | transformed | `0.5` |
| Pure-algebraic | 2 | identity | `0.25` |
| Cube-root | 3 | identity | `0.25` |
| Quartic-root | 4 | identity | `0.25` |
| Schwarzschild-cbrt | 3 | transformed | `0.25` |
| Schwarzschild-quartic (this task) | 4 | transformed | `0.25` |

## 2x3 Grid

| Operand | n=2 | n=3 | n=4 |
| --- | ---: | ---: | ---: |
| Identity | `0.25` | `0.25` | `0.25` |
| Transformed | `0.5` | `0.25` | `0.25` |

The transformed row does not continue to `0.125` at n=4 under the admitted composed-sqrt quartic fixture.

## Sterbenz Boundary

| Boundary | Nearest grid point | Below count | Above count | Below density | Above density | Direction | Match? |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `4.0` | `3.9655172413793105` | `13 / 112` | `24 / 25` | `0.11607142857142858` | `0.96` | `above_boundary_higher` | Y |

The analytic boundary record is `r = 4.0`, matching Schwarzschild n=2 and Schwarzschild-cbrt n=3. The canonical grid does not include an exact `4.0` sample; the nearest sampled point is recorded separately.

## Polarity Grid Stability

| Pair | Aggregate |
| --- | --- |
| `F1_F2` | `grid_stable_polarity_coupling` |
| `F1_F4` | `open_underpowered` |
| `F2_F4` | `open_underpowered` |

F3 nonzero count was zero across every polarity grid and precision.

## Parenthesization Observation

The paired grouping `(R * R) * (R * R)` and the left-fold grouping `((R * R) * R) * R` were not bit-identical at all points. The campaign recorded `50` mismatches out of `137` grid points. This contradicts the task's proposed parenthesization sanity assumption and is preserved as substrate evidence rather than corrected away.

## Hypothesis Discrimination

| Hypothesis | Predicted | Observed | Match? |
| --- | ---: | ---: | --- |
| H3: compound law | `0.125` | `0.25` | N |
| H3-converges: transformed floors at identity baseline | `0.25` | `0.25` | Y |
| H_rounding: rounding-event count dominates | `0.0625` | `0.25` | N |

## Headline Classification

Headline: `transformed_decay_converges_to_identity_floor`.

The observed float64 F2 lattice grain was exactly `0.25`. Under the pre-registered mapping, that supports the convergence/floor outcome: the transformed row moves from `0.5` at n=2 to `0.25` at n=3 and remains at `0.25` at n=4 for the admitted composed-sqrt quartic fixture.

## Tests

- Baseline at task start: `42ff428957054e3079839ff142aa22795dd16f83`, 762 passing tests.
- Pre-registration commit: `6a81d9d`.
- Added tests: 41 collected tests in `tests/test_task034_schwarzschild_quartic_transformed_n4.py`.
- Post-task collection: 803 tests collected.
- Focused task suite: `PYTHONPATH=src python -m pytest tests/test_task034_schwarzschild_quartic_transformed_n4.py -q` passed.
- Slow-test bypass: `PYTHONPATH=src python -m pytest tests/ --skip-slow -q -ra` passed with 380 campaign/report regression tests skipped.
- Full suite: `PYTHONPATH=src python -m pytest tests/ -q` passed.

## Byte-Stability

- `campaign_results.json`: repeat generation matched report bytes.
- `schwarzschild_quartic_four_form_battery.json`: repeat generation matched report bytes.
- `schwarzschild_quartic_lattice_campaign_output.json`: repeat generation matched report bytes.
- `headline_classification.md`: repeat generation matched report bytes.
- `pre_registration.md`: diff against `6a81d9d` produced no output.

## Discipline Gates

- No substrate primitive or manifest files were modified.
- The existing Layer 2 refinery package was not imported or touched.
- The forbidden import and fractional-power pattern scans passed for new Task 034 source files.
- No numpy random API was introduced.
- The fixture uses composed `numpy.sqrt` calls and explicit multiplication for the quartic product.

## Files Changed

- `Build_Docs/Agent_tasks/Completed/codex_task034_schwarzschild_quartic_transformed_n4.md`
- `Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/pre_registration.md`
- `Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/campaign_results.json`
- `Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/schwarzschild_quartic_four_form_battery.json`
- `Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/schwarzschild_quartic_lattice_campaign_output.json`
- `Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4/headline_classification.md`
- `Build_Docs/Reports/task034_schwarzschild_quartic_transformed_n4_summary.md`
- `src/lloyd_v4/evals/schwarzschild_quartic_four_form.py`
- `src/lloyd_v4/evals/schwarzschild_quartic_lattice_campaign.py`
- `src/lloyd_v4/evals/schwarzschild_quartic_polarity_grid_stability.py`
- `src/lloyd_v4/evals/schwarzschild_quartic_campaign.py`
- `tests/conftest.py`
- `tests/test_task034_schwarzschild_quartic_transformed_n4.py`

## Forward Observations

- H3-converges is supported by this fixture: the transformed row now reads `0.5`, `0.25`, `0.25` for n=2, n=3, n=4.
- The `0.0625` rounding-event-count outcome was not observed, so this fixture does not support the claim that the composed-sqrt two-rounding event count dominates the F2 grain. The parenthesization mismatch still shows that multiplication grouping itself is observable at the residual level.
- Further discrimination would require varying operand structure and radical implementation independently, such as an SR-style quartic transformed fixture or a native-rounding quartic primitive if the admitted-operation set changes; those are observations, not task drafts.
