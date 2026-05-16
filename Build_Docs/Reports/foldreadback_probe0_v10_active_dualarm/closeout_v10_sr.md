# Fold-Readback Probe 0 v10 SR Fixture Closeout

Accepted outcome: `active_handoff_gap_resolved`

## Required Answers

1. ARM-W entered warning or below-floor near the SR singular endpoint: `True`.
   Near-endpoint band checked: beta in [`0.9052772058823529`, `0.9999`].
   ARM-W state counts: `{'readable': 13, 'warning': 5, 'below_floor': 19, 'recovered': 4, 'underpopulated': 0}`.
2. ARM-N activated from ARM-W falloff telemetry: `True`.
3. ARM-N valid reads inside ARM-W core-gap intervals: `True` (`13` contexts).
4. Both arms valid in overlap/guard regions: `9` contexts; agreements: `['agree']`.
5. Exact-zero and matched-affine controls remained silent: `True`.
6. Partition invariance held: `True`; guard invariance held: `True`.
7. Result category: `active_handoff_gap_resolved`.

## Fixture And Reuse

- Reused SR fixture functions: `beta_grid()`, `eta_of_beta(beta)`, `four_form_float64(beta)`.
- Used canonical SR surface `f(beta)=1-beta^2`, `eta(beta)=sqrt(f(beta))`, beta -> 1.
- Reused v10 active dual-arm mechanics; no new dual-arm method was introduced.
- Reused v7 primitives and v8 `classify_instrument`/`ANALYTIC_MAX`; no v7 primitive was copied or modified.

## Verification

- `PYTHONPATH=src python scratch/run_foldreadback_probe0_v10_active_dualarm.py --sr`
  Result: passed; accepted_outcome=active_handoff_gap_resolved.
- `PYTHONPATH=src python -m pytest tests/test_foldreadback_probe0_v10_sr.py -q`
  Result: passed; 8 tests.
- `PYTHONPATH=src python -m pytest tests/test_foldreadback_probe0_v10_active_dualarm.py tests/test_task027_sr_four_form_cross_fixture.py::test_beta_grid_deterministic_and_bounded tests/test_task027_sr_four_form_cross_fixture.py::test_F3_sr_is_identically_zero tests/test_task027_sr_four_form_cross_fixture.py::test_sr_four_form_byte_stable -q`
  Result: passed; 17 tests.
- `PYTHONPATH=src python -m pytest tests/ --skip-slow -q -ra`
  Result: passed; slow campaign/report tests skipped by --skip-slow.

## Artifact

- `Build_Docs/Reports/foldreadback_probe0_v10_active_dualarm/artifact_v10_sr.json`
- `Build_Docs/Reports/foldreadback_probe0_v10_active_dualarm/closeout_v10_sr.md`
