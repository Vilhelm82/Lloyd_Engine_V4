# Task 026c-prime Summary - Polarity Grid Stability

## Scope

Task 026c-prime tested whether Task 026's F1/F2 parallel-polarization finding
is stable across independent r-grids. It also ran F1/F4 as the negative control
and F2/F4 as the explicit low-power promotion guard. The task is report-only:
no primitive, runtime status enum, manifest entry, transition rule, or Task 025
law-library term was added.

## Baseline

- Pre-task HEAD: `d561a3c Task 026: Lattice and anomaly investigation campaign`.
- Pre-task suite: 456 tests passing at the Task 026 closeout.
- Fixture modules were consumed unchanged.

## Test Results

- Added tests: 15 in `tests/test_task026c_prime_polarity_grid_stability.py`.
- The spec required 14 tests; the extra test is an explicit forbidden-import
  surface check for the new eval module.
- Post-task collection/full suite: 471 tests passing.

## Files Changed

- `src/lloyd_v4/evals/polarity_grid_stability.py`
- `tests/test_task026c_prime_polarity_grid_stability.py`
- `Build_Docs/Reports/task026c_prime_polarity_grid_stability/campaign_output.json`
- `Build_Docs/Reports/task026c_prime_polarity_grid_stability/polarity_grid_table.csv`
- `Build_Docs/Reports/task026c_prime_polarity_grid_stability/region_split_table.csv`
- `Build_Docs/Reports/task026c_prime_polarity_grid_stability/precision_overlap_table.csv`
- `Build_Docs/Reports/task026c_prime_polarity_grid_stability/README.md`
- `Build_Docs/Reports/task026c_prime_summary.md`
- `Build_Docs/Agent_tasks/Completed/codex_task026c_prime_polarity_grid_stability.md`

## Grid Construction

| Grid | Seed | n_input | n_after_dedup | Range | Clamp low/high |
| --- | ---: | ---: | ---: | --- | --- |
| reference | 0 | 137 | 137 | 2.005 to 10.0 | 0 / 0 |
| coarse_perturbation | 1042 | 137 | 121 | 2.005 to 10.0 | 17 / 1 |
| fine_perturbation | 2317 | 137 | 137 | 2.005 to 9.999976847694038 | 1 / 0 |
| independent_uniform | 4099 | 137 | 137 | 2.1008203559207943 to 9.90631481734936 | 0 / 0 |

The coarse-grid sanity benchmark expected mostly high-end clamping. The measured
seed produced 17 low-end clamps and 1 high-end clamp. This is recorded as an
honest boundary-metrology observation; the campaign did not change the seed.

## Polarity Summary

| Pair | Grid | float64 cofire/agree/fraction | float64 p_two_tail | Status |
| --- | --- | --- | ---: | --- |
| F1_F2 | reference | 16/16/1.000000 | 0.000031 | `reference_grid_confirmed` |
| F1_F2 | coarse_perturbation | 17/17/1.000000 | 0.000015 | `grid_stable_supported` |
| F1_F2 | fine_perturbation | 19/19/1.000000 | 0.000004 | `grid_stable_supported` |
| F1_F2 | independent_uniform | 57/57/1.000000 | 1.388e-17 | `grid_stable_supported` |
| F1_F4 | reference | 48/23/0.479167 | 0.885433 | `depolarized_supported` |
| F1_F4 | coarse_perturbation | 34/19/0.558824 | 0.607591 | `depolarized_supported` |
| F1_F4 | fine_perturbation | 38/25/0.657895 | 0.072951 | `grid_stability_rejected` |
| F1_F4 | independent_uniform | 12/12/1.000000 | 0.000488 | `grid_stability_rejected` |
| F2_F4 | reference | 4/4/1.000000 | 0.125000 | `underpowered_grid` |
| F2_F4 | coarse_perturbation | 3/3/1.000000 | 0.250000 | `underpowered_grid` |
| F2_F4 | fine_perturbation | 8/8/1.000000 | 0.007812 | `underpowered_grid` |
| F2_F4 | independent_uniform | 19/19/1.000000 | 0.000004 | `grid_stable_supported` |

## Region Split Summary

F1/F2 support is concentrated in the far region on every grid. The independent
uniform grid sampled no near-region points and placed 123 of 137 points in the
far region, so its F1/F2 support is overwhelmingly far-field. F1/F4 remains
depolarized on the reference and coarse grids; the fine and independent grids
produce one-precision skews but fail the precision-consistent coupling gate.

## Precision Overlap Invariance

| Grid | F1_F2 | F1_F4 | F2_F4 |
| --- | --- | --- | --- |
| reference | 6/6/1.000000 | 7/15/0.466667 | 0/0/null |
| coarse_perturbation | 5/5/1.000000 | 5/11/0.454545 | 1/1/1.000000 |
| fine_perturbation | 3/3/1.000000 | 6/14/0.428571 | 1/1/1.000000 |
| independent_uniform | 23/23/1.000000 | 1/1/1.000000 | 2/2/1.000000 |

F1/F2 preserves relation in every precision-overlap point. F1/F4 has no
precision-consistent coupling support despite the independent-grid float64 skew.
F2/F4 remains underpowered on overlap.

## Aggregate Classifications

- F1/F2: `grid_stable_polarity_coupling`. Reference and all non-reference grids
  meet support criteria.
- F1/F4: `depolarized_invariant`. The negative control passed: no
  non-reference grid passed the precision-consistent coupling gate.
- F2/F4: `open_underpowered`. The underpromotion guard blocks promotion because
  at least one grid is underpowered.

## Byte Stability

The campaign output is deterministic. A repeat run to
`/tmp/polarity_grid_repeat.json` was diff-clean against the report artifact.

## Honest Observations

- The empirical clamp pattern differed from the sanity table: low-end clamping,
  not high-end clamping, dominated the coarse perturbation grid.
- The fine perturbation grid clamped one low endpoint despite the no-clamp
  sanity expectation.
- The independent uniform grid produced no near-region samples; this makes it a
  strong far-field test, not a balanced region test.
- F1/F4 produced a float64-only independent-grid skew, but float32 and
  precision-overlap evidence did not support promotion.

## Limits

- Existing Schwarzschild four-form fixture only.
- Four deterministic grids only.
- No cross-fixture test, larger-N grid family, adaptive grid, long-double path,
  or platform FMA axis.
- No substrate primitive, runtime status enum, manifest entry, transition rule,
  or law-library term added.

## Forward References

F1/F2 grid-stable polarity coupling licenses a future substrate-promotion task
for a typed polarization observable. F2/F4 remains open under low power. F1/F4
should remain a negative-control requirement for any future promotion attempt.

## Audits

- `PYTHONPATH=src python -c "from lloyd_v4.evals.polarity_grid_stability import run_campaign; print(sorted(run_campaign().keys()))"`
- `PYTHONPATH=src python -m lloyd_v4.evals.polarity_grid_stability`
- `PYTHONPATH=src python -m lloyd_v4.evals.polarity_grid_stability --output /tmp/polarity_grid_repeat.json`
- `diff Build_Docs/Reports/task026c_prime_polarity_grid_stability/campaign_output.json /tmp/polarity_grid_repeat.json`
- `python -m pytest -q tests/test_task026c_prime_polarity_grid_stability.py`
- `python -m pytest -q tests/`
- `python -m pytest -q tests/test_task001_source_purity.py`
- `python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py`
- `rg "numpy\\.random|np\\.random|scipy|sympy|mpmath" src/lloyd_v4/evals/polarity_grid_stability.py`
