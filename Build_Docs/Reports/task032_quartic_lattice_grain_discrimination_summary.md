# Task 032 Summary - Quartic Lattice Grain Discrimination

## Scope

Task 032 added a quartic-root identity-operand fixture using the admitted composed-root form `sqrt(sqrt(1 - x))`, then ran the four-form battery, lattice campaign, polarity grid stability, and Sterbenz boundary observation. The load-bearing measurement was the float64 F2 lattice grain.

## Pre-registration

- Commit: `ea1c8d7 Task 032 pre-registration: quartic-root identity-operand fixture for F2 lattice grain discrimination`
- Date: `2026-05-14 10:41:21 +1000`
- File: `Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/pre_registration.md`
- Status: byte-identical to the pre-registration commit at completion.

## Quartic Fixture Construction

- Grid: canonical 137-point pure_algebraic `x_grid`, `x in [0.01, 0.99]`.
- Direct operand: `1 - x`.
- Radical: `R = numpy.sqrt(numpy.sqrt(1 - x))`.
- Product grouping: `(R * R) * (R * R)`.
- Forms: F1=`R^4 - (1 - x)`, F2=`R^4 - 1 + x`, F3=`R - sqrt(sqrt(1 - x))`, F4=`R - sqrt(sqrt((1 - x/2) - x/2))`.
- Full point-level values are in `quartic_four_form_battery.json`.

## Lattice Classification

| Form | float32 class | float32 nonzero | float32 grain | float64 class | float64 nonzero | float64 grain |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| `F1` | `lattice_integer` | `51` | `0.0` | `lattice_integer` | `76` | `0.0` |
| `F2` | `non_integer_lattice` | `54` | `0.25` | `non_integer_lattice` | `79` | `0.25` |
| `F3` | `lattice_empty` | `0` | `0.0` | `lattice_empty` | `0` | `0.0` |
| `F4` | `lattice_integer` | `41` | `0.0` | `lattice_integer` | `57` | `0.0` |

## F2 Grain Comparison

| Fixture | n | Operand | F2 grain |
| --- | ---: | --- | ---: |
| Schwarzschild | 2 | transformed | `0.5` |
| SR | 2 | transformed | `0.5` |
| Pure-algebraic | 2 | identity | `0.25` |
| Cube-root | 3 | identity | `0.25` |
| Quartic-root | 4 | identity | `0.25` |

## Sterbenz Boundary

| Boundary | Below count | Above count | Below density | Above density | Direction | Match? |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| `0.5` | `60 / 69` | `19 / 68` | `0.8695652173913043` | `0.27941176470588236` | `below_boundary_higher` | Y |

## Polarity Grid Stability

| Pair | Aggregate |
| --- | --- |
| `F1_F2` | `grid_stable_polarity_coupling` |
| `F1_F4` | `open_underpowered` |
| `F2_F4` | `open_underpowered` |

F3 nonzero count was zero across every polarity grid and precision.

## Hypothesis Discrimination

| Hypothesis | Predicted | Observed | Match? |
| --- | ---: | ---: | --- |
| H1: algebraic-degree law | `0.125` | `0.25` | N |
| H2: operand-transformation law | `0.25` | `0.25` | Y |

## Headline Classification

Headline: `lattice_grain_h2_operand`.

The observed float64 F2 lattice grain was exactly `0.25`, matching the pre-registered operand-transformation law and not the algebraic-degree prediction. The result extends the identity-operand grain pattern to n=4 for the admitted composed-root quartic fixture.

## Two-Rounding-Events Caveat

The quartic root was computed as two composed square roots. This produces two root-rounding events. A native single-rounding quartic primitive would be a different fixture; the Task 032 result applies only to the admitted composed-root form.

## Tests

- Baseline at task start: `0650a448e68a5498ceb272fbd73cf9afd4cf44ba`, 686 passing tests.
- Pre-registration commit: `ea1c8d7`.
- Added tests: 37 collected tests in `tests/test_task032_quartic_lattice_grain_discrimination.py`.
- Post-task collection: 723 tests collected.
- Focused task suite: `PYTHONPATH=src python -m pytest tests/test_task032_quartic_lattice_grain_discrimination.py -q` passed.
- Full suite: `PYTHONPATH=src python -m pytest tests/ -q` passed.

## Byte-Stability

- `campaign_results.json`: repeat generation matched report bytes.
- `quartic_four_form_battery.json`: repeat generation matched report bytes.
- `quartic_lattice_campaign_output.json`: repeat generation matched report bytes.
- `headline_classification.md`: repeat generation matched report bytes.
- `pre_registration.md`: diff against `ea1c8d7` produced no output.

## Discipline Gates

- No substrate primitive or manifest files were modified.
- The existing Layer 2 refinery package was not imported or touched.
- The forbidden import and fractional-power pattern scans passed for new Task 032 source files.
- No numpy random API was introduced.
- The fixture uses only composed numpy square-root operations for the quartic radical.

## Files Changed

- `Build_Docs/Agent_tasks/Completed/codex_task032_quartic_lattice_grain_discrimination.md`
- `Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/pre_registration.md`
- `Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/campaign_results.json`
- `Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/quartic_four_form_battery.json`
- `Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/quartic_lattice_campaign_output.json`
- `Build_Docs/Reports/task032_quartic_lattice_grain_discrimination/headline_classification.md`
- `Build_Docs/Reports/task032_quartic_lattice_grain_discrimination_summary.md`
- `src/lloyd_v4/evals/pure_algebraic_quartic_four_form.py`
- `src/lloyd_v4/evals/pure_algebraic_quartic_lattice_campaign.py`
- `src/lloyd_v4/evals/pure_algebraic_quartic_polarity_grid_stability.py`
- `src/lloyd_v4/evals/pure_algebraic_quartic_campaign.py`
- `tests/test_task032_quartic_lattice_grain_discrimination.py`

## Forward Observations

- H2 is supported cleanly for the admitted quartic identity-operand fixture: the n=4 grain is `0.25`, not `0.125`.
- The five-fixture table now separates transformed operands at `0.5` from identity operands at `0.25` across n=2, n=3, and n=4.
- The two-root-rounding caveat does not weaken the observed H2 result for this admitted form, but it remains relevant to any comparison against a native single-rounding quartic primitive.
- Further discrimination would require fixtures that vary operand transformation, radical degree, and root-rounding structure independently; those are outside this task.
