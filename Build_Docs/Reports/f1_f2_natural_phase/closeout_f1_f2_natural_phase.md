# F1/F2 Natural Half-ULP Phase Offset Audit

Accepted outcome: `phase_drift_not_mergeable`

## Required Answers

1. F2 naturally sits at half-ULP phase relative to F1 pointwise: `False`.
   SR usable paired coordinates: `95` / `137` finite pairs.
   Pointwise delta relation: `half_phase_present_but_drifting`.
   Delta-to-half median/max: `0.25` / `0.5`.
2. Stability: `half_phase_present_but_drifting`; half-phase hits are present but drift across the usable region rather than forming one coherent interleaved comb.
3. Same-route controls reject manufactured half-phase: `True`.
4. F3 calibration zero remains clean: `True`.
5. F4 behaves as a route-residual stressor, not the promoted phase companion: `True`.
6. Justified candidate interleaved lattice readback: `False`.
7. Double precision language justified: `False`. The result remains eval-layer phase-drift evidence, not a precision-doubling method.

## Fixture Summary

- `sr_four_form`: `half_phase_present_but_drifting` with `95` usable pairs; delta-to-half median `0.25`, max `0.5`.
- `schwarzschild_four_form`: `half_phase_present_but_drifting` with `81` usable pairs; delta-to-half median `0.5`, max `0.5`.

## Verification

- `PYTHONPATH=src python -m lloyd_v4.evals.f1_f2_natural_phase`
  Result: passed; generated artifact_f1_f2_natural_phase.json and closeout_f1_f2_natural_phase.md.
- `PYTHONPATH=src python -m pytest tests/test_f1_f2_natural_phase.py -q`
  Result: passed; 8 tests.
- `PYTHONPATH=src python -m pytest tests/test_f1_f2_natural_phase.py tests/test_task027_sr_four_form_cross_fixture.py::test_beta_grid_deterministic_and_bounded tests/test_task027_sr_four_form_cross_fixture.py::test_F3_sr_is_identically_zero tests/test_task027_sr_four_form_cross_fixture.py::test_sr_four_form_byte_stable -q`
  Result: passed; 11 tests.
- `PYTHONPATH=src python -m pytest tests/ --skip-slow -q -ra`
  Result: passed; slow campaign/report tests skipped by --skip-slow.

## Artifact

- `Build_Docs/Reports/f1_f2_natural_phase/artifact_f1_f2_natural_phase.json`
- `Build_Docs/Reports/f1_f2_natural_phase/closeout_f1_f2_natural_phase.md`
