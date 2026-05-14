# Task 033 Summary - Schwarzschild-Cbrt Transformed n=3

## Scope

Task 033 added a Schwarzschild-shape cube-root transformed-operand fixture using the canonical 137-point `r` sweep, direct operand `1 - 2 / r`, alternate routing `(r - 2) / r`, and native `numpy.cbrt`. The campaign ran the four-form battery, lattice campaign, polarity grid stability, and Sterbenz boundary observation. The load-bearing measurement was the float64 F2 lattice grain.

## Pre-registration

- Commit: `8094f8c Task 033 pre-registration: Schwarzschild-cbrt transformed-operand n=3 fixture`
- Full hash: `8094f8c23d11cb4874d596f742ed9b03c44fcd92`
- Date: `2026-05-14 11:08:31 +1000`
- File: `Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/pre_registration.md`
- Status: byte-identical to the pre-registration commit at completion.

## Fixture Construction

- Grid: canonical 137-point `schwarzschild_four_form.sweep_r_values`, `r in [2.005, 10.0]`.
- Direct operand: `1 - 2 / r`.
- Alternate operand: `(r - 2) / r`.
- Radical: `R = numpy.cbrt(1 - 2 / r)`.
- Product grouping: `R * R * R`.
- Forms: F1=`R^3 - (1 - 2/r)`, F2=`R^3 - 1 + 2/r`, F3=`R - cbrt(1 - 2/r)`, F4=`R - cbrt((r - 2)/r)`.
- Full point-level values are in `schwarzschild_cbrt_four_form_battery.json`.

## Lattice Classification

| Form | float32 class | float32 nonzero | float32 grain | float64 class | float64 nonzero | float64 grain |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| `F1` | `lattice_integer` | `94` | `0.0` | `lattice_integer` | `111` | `0.0` |
| `F2` | `non_integer_lattice` | `28` | `0.25` | `non_integer_lattice` | `45` | `0.25` |
| `F3` | `lattice_empty` | `0` | `0.0` | `lattice_empty` | `0` | `0.0` |
| `F4` | `lattice_integer` | `72` | `0.0` | `lattice_integer` | `87` | `0.0` |

## F2 Grain Comparison

| Fixture | n | Operand | F2 grain |
| --- | ---: | --- | ---: |
| Schwarzschild | 2 | transformed | `0.5` |
| SR | 2 | transformed | `0.5` |
| Pure-algebraic | 2 | identity | `0.25` |
| Cube-root | 3 | identity | `0.25` |
| Quartic-root | 4 | identity | `0.25` |
| Schwarzschild-cbrt (this task) | 3 | transformed | `0.25` |

## Sterbenz Boundary

| Boundary | Nearest grid point | Below count | Above count | Below density | Above density | Direction | Match? |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `4.0` | `3.9655172413793105` | `22 / 112` | `23 / 25` | `0.19642857142857142` | `0.92` | `above_boundary_higher` | Y |

The analytic boundary record is `r = 4.0`, matching the existing Schwarzschild n=2 boundary. The canonical grid does not include an exact `4.0` sample; the nearest sampled point is recorded separately.

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
| H2: transformed operand gives `0.5`, independent of `n` | `0.5` | `0.25` | N |
| H2-refined: transformed effect is n=2-specific | `0.25` | `0.25` | Y |

## Headline Classification

Headline: `transformed_operand_law_refuted_at_n3`.

The observed float64 F2 lattice grain was exactly `0.25`. Under the pre-registered mapping, that refutes the n-independent transformed-operand law at n=3 and supports the refined reading that the observed transformed-operand grain effect is specific to n=2 on the current fixture set.

## Tests

- Baseline at task start: `482998f343b555c2eddd7f5ad4845ad6170bfce8`, 723 passing tests.
- Pre-registration commit: `8094f8c`.
- Added tests: 39 collected tests in `tests/test_task033_schwarzschild_cbrt_transformed_n3.py`.
- Post-task collection: 762 tests collected.
- Focused task suite: `PYTHONPATH=src python -m pytest tests/test_task033_schwarzschild_cbrt_transformed_n3.py -q` passed.
- Slow-test bypass: `PYTHONPATH=src python -m pytest tests/ --skip-slow -q -ra` passed with 339 campaign/report regression tests skipped.
- Full suite: `PYTHONPATH=src python -m pytest tests/ -q` passed.

## Byte-Stability

- `campaign_results.json`: repeat generation matched report bytes.
- `schwarzschild_cbrt_four_form_battery.json`: repeat generation matched report bytes.
- `schwarzschild_cbrt_lattice_campaign_output.json`: repeat generation matched report bytes.
- `headline_classification.md`: repeat generation matched report bytes.
- `pre_registration.md`: diff against `8094f8c` produced no output.

## Discipline Gates

- No substrate primitive or manifest files were modified.
- The existing Layer 2 refinery package was not imported or touched.
- The forbidden import and fractional-power pattern scans passed for new Task 033 source files.
- No numpy random API was introduced.
- The fixture uses native `numpy.cbrt` and explicit multiplication for the cube.
- Pytest now supports an explicit `--skip-slow` flag for rapid iteration; default pytest remains exhaustive.

## Files Changed

- `Build_Docs/Agent_tasks/Completed/codex_task033_schwarzschild_cbrt_transformed_n3.md`
- `Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/pre_registration.md`
- `Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/campaign_results.json`
- `Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/schwarzschild_cbrt_four_form_battery.json`
- `Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/schwarzschild_cbrt_lattice_campaign_output.json`
- `Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3/headline_classification.md`
- `Build_Docs/Reports/task033_schwarzschild_cbrt_transformed_n3_summary.md`
- `pyproject.toml`
- `src/lloyd_v4/evals/schwarzschild_cbrt_four_form.py`
- `src/lloyd_v4/evals/schwarzschild_cbrt_lattice_campaign.py`
- `src/lloyd_v4/evals/schwarzschild_cbrt_polarity_grid_stability.py`
- `src/lloyd_v4/evals/schwarzschild_cbrt_campaign.py`
- `tests/conftest.py`
- `tests/test_task033_schwarzschild_cbrt_transformed_n3.py`

## Forward Observations

- H2 is refuted by this data point: the transformed n=3 fixture reports `0.25`, not `0.5`.
- The Sterbenz boundary location is operand-determined in this fixture family: the boundary remains `r = 4.0`, the same as Schwarzschild n=2, while the sampled directional density also matches the above-boundary prediction.
- Further discrimination would require fixtures that independently vary transformed-operand structure and radical degree, such as a cube-root fixture over the SR-style transformed operand or a quartic fixture over the Schwarzschild operand; those are observations, not task drafts.
