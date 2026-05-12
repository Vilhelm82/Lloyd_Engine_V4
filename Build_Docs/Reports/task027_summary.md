# Task 027 Summary - SR Four-Form Cross-Fixture

## Scope

Task 027 added the SR time-dilation four-form fixture and ran the same lattice
and polarity-grid stability structure used for the Schwarzschild fixture. The
goal was to test whether the observed four-form signatures behave like an
arithmetic-chain property across fixtures or change qualitatively with the
fixture.

No V4 primitive, runtime status enum, manifest entry, transition rule, or Task
025 law-library term was added.

## Baseline

- Pre-task HEAD: `780d2bb Task 026c-prime: Polarity grid stability campaign`.
- Pre-task suite: 471 tests passing.

## Test Results

- Added tests: 16 in `tests/test_task027_sr_four_form_cross_fixture.py`.
- Post-task collection/full suite: 487 tests passing.

## Files Changed

- `src/lloyd_v4/evals/sr_four_form.py`
- `src/lloyd_v4/evals/sr_lattice_campaign.py`
- `src/lloyd_v4/evals/sr_polarity_grid_stability.py`
- `src/lloyd_v4/evals/cross_fixture_comparison.py`
- `tests/test_task027_sr_four_form_cross_fixture.py`
- `Build_Docs/Reports/task027_sr_four_form_cross_fixture/*`
- `Build_Docs/Reports/task027_summary.md`
- `Build_Docs/Agent_tasks/Completed/codex_task027_sr_four_form_cross_fixture.md`

## SR Beta Grid

The canonical SR grid has 137 strictly increasing beta values from `0.01` to
`0.9999`. The grid is deterministic and byte-stable across calls.

## SR Four-Form Counts

| Form | float32 non-zero | float64 non-zero | decimal-50 non-zero |
| --- | ---: | ---: | ---: |
| F1 | 28 | 34 | 21 |
| F2 | 92 | 95 | 59 |
| F3 | 0 | 0 | 0 |
| F4 | 42 | 27 | 83 |

F3 remained the calibration zero across every precision path.

## SR Lattice Findings

| Form | float64 classification | float64 non-zero | distinct levels | max integer residual |
| --- | --- | ---: | ---: | ---: |
| F1 | `lattice_integer` | 34 | 3 | 0.0 |
| F2 | `non_integer_lattice` | 95 | 5 | 0.5 |
| F3 | `lattice_empty` | 0 | 0 | 0.0 |
| F4 | `lattice_integer` | 27 | 10 | 0.0 |

Compared with the V3 SR sanity numbers, V4's 137-point grid produces fewer F4
levels than the 446-cell V3 report, but preserves the integer-lattice character
for F4 and the half-level F2 behavior.

## SR Polarity Grid Stability

| Pair | Aggregate | Key observation |
| --- | --- | --- |
| F1_F2 | `grid_stable_polarity_coupling` | All four grids support parallel polarity; reference float64 is 34/34 with p=1.164e-10. |
| F1_F4 | `open_underpowered` | No grid reaches precision-supported coupling power; negative control passed. |
| F2_F4 | `reference_grid_only` | Fine and independent grids support coupling, but reference/coarse reject; not promoted. |

## Cross-Fixture Comparison

| Pair | Schwarzschild | SR | Same |
| --- | --- | --- | --- |
| F1_F2 | `grid_stable_polarity_coupling` | `grid_stable_polarity_coupling` | yes |
| F1_F4 | `depolarized_invariant` | `open_underpowered` | no |
| F2_F4 | `open_underpowered` | `reference_grid_only` | no |

| Form | Schwarzschild float64 lattice | SR float64 lattice |
| --- | --- | --- |
| F1 | `lattice_integer`, 69 non-zero, 2 levels | `lattice_integer`, 34 non-zero, 3 levels |
| F2 | `non_integer_lattice`, 28 non-zero, 5 levels | `non_integer_lattice`, 95 non-zero, 5 levels |
| F3 | `lattice_empty`, 0 non-zero | `lattice_empty`, 0 non-zero |
| F4 | `lattice_integer`, 92 non-zero, 35 levels | `lattice_integer`, 27 non-zero, 10 levels |

## Sterbenz Boundary Verification

| Fixture | Boundary | Below count/density | Above count/density | Predicted | Observed | Supports |
| --- | ---: | --- | --- | --- | --- | --- |
| Schwarzschild | 4.0 | 6 / 0.053571 | 22 / 0.88 | above higher | above higher | yes |
| SR | 0.7071067811865476 | 86 / 0.895833 | 9 / 0.219512 | below higher | below higher | yes |

Both fixtures show the predicted directional bias at the shifted boundary.

## Headline Finding

`chain_property_partial`.

SR preserves the strongest chain signatures: F1/F2 grid-stable parallel
polarity, F3 silence, F2 half-level lattice behavior, F4 integer lattice
behavior, and the predicted Sterbenz boundary direction. It diverges on the
negative-control aggregate power and on F4 lattice grain, so the result is mixed
rather than fully supported.

## Byte Stability

SR polarity output and cross-fixture comparison output were regenerated to
temporary paths and diffed cleanly against the report artifacts.

## Honest Observations

- The initial implementation accidentally routed F1 through the F2 ordering;
  this was corrected before recording results.
- SR F4 has a much smaller float64 lattice spectrum than Schwarzschild on the
  137-point grid: 10 levels versus 35.
- SR F1/F4 does not become a negative-control failure after the
  precision-consistent promotion gate, but it is underpowered rather than
  cleanly depolarized.
- SR F2/F4 has stronger evidence than Schwarzschild on two non-reference grids,
  but fails aggregate promotion.

## Limits

- SR fixture only as the new fixture.
- No Bell, pure algebraic control, larger grid family, long-double path, or
  platform FMA axis.
- No substrate promotion or law-library expansion.

## Forward References

Task 028 can apply the same battery to the Bell strain fixture. Task 029 should
run a pure algebraic control with no fixture semantics. Task 030 can synthesize
cross-fixture evidence after those two additional controls.

## Audits

- `PYTHONPATH=src python -c "from lloyd_v4.evals.sr_four_form import four_form_float64, beta_grid; print(beta_grid()[:3], beta_grid()[-3:])"`
- `PYTHONPATH=src python -c "from lloyd_v4.evals.sr_polarity_grid_stability import run_campaign; print(sorted(run_campaign().keys()))"`
- `PYTHONPATH=src python -c "from lloyd_v4.evals.cross_fixture_comparison import compare_fixtures; print(sorted(compare_fixtures().keys()))"`
- `PYTHONPATH=src python -m lloyd_v4.evals.sr_polarity_grid_stability`
- `PYTHONPATH=src python -m lloyd_v4.evals.sr_polarity_grid_stability --output /tmp/sr_polarity_repeat.json`
- `diff Build_Docs/Reports/task027_sr_four_form_cross_fixture/sr_polarity_grid_stability.json /tmp/sr_polarity_repeat.json`
- `PYTHONPATH=src python -m lloyd_v4.evals.cross_fixture_comparison`
- `PYTHONPATH=src python -m lloyd_v4.evals.cross_fixture_comparison --output /tmp/cross_fixture_repeat.json`
- `diff Build_Docs/Reports/task027_sr_four_form_cross_fixture/cross_fixture_comparison.json /tmp/cross_fixture_repeat.json`
- `python -m pytest -q tests/test_task027_sr_four_form_cross_fixture.py`
- `python -m pytest -q tests/`
- `python -m pytest -q tests/test_task001_source_purity.py`
- `python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py`
- `rg "numpy\\.random|np\\.random|scipy|sympy|mpmath" src/lloyd_v4/evals/sr_four_form.py src/lloyd_v4/evals/sr_lattice_campaign.py src/lloyd_v4/evals/sr_polarity_grid_stability.py src/lloyd_v4/evals/cross_fixture_comparison.py`
