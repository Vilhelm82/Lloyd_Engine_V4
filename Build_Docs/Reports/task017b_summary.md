# Task 017b Summary - Multi-Precision Instrument Model

## Scope

Task 017b added a confirmation campaign over the Task 024b Schwarzschild
four-form battery. Phase A compared V4 float64 residuals against a
decimal-50 oracle and deliberately preserved the specified result-ULP
bound as a failing finding. Phase B compared binary IEEE float32 and
float64 F4 residual magnitudes. Phase C verified F3 as the precision-
independent calibration zero. No primitives, status families, manifests,
or architecture documents were changed.

## Test Count

- Pre-task baseline after Task 024b: 423 tests passing.
- Post-task suite: 431 tests passing.
- Added tests: 8 in `tests/test_task017b_multi_precision_instrument_model.py`.

## Files Changed

- `src/lloyd_v4/evals/multi_precision_four_form.py`
- `src/lloyd_v4/evals/multi_precision_campaign.py`
- `tests/test_task017b_multi_precision_instrument_model.py`
- `Build_Docs/Reports/task017b_multi_precision_instrument_model/campaign_output.json`
- `Build_Docs/Reports/task017b_multi_precision_instrument_model/README.md`
- `Build_Docs/Reports/task017b_summary.md`
- Task-ledger handoff moves for completed task briefs 022, 023, 023b, and
  024b, plus the new `codex_task017b_multi_precision_instrument_model.md`
  task brief.

## Phase A - Instrument Self-Consistency

The originally specified result-ULP bound failed as expected after
implementation. For algebraically-zero forms, the decimal oracle reports
the algebraic truth while float64 reports the instrument residual, so
`abs(F_float64 - F_decimal50) ~= abs(F_float64)`. Measuring that residual
in ULPs of the tiny observed residual is therefore wrong by construction.

| Form | float64 non-zero count | Median residual | Median chain envelope | Median residual / chain envelope | Result-bound exceed count | Median residual / result bound | Phase A result-bound pass | Chain diagnostic pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| F1 | 69 | `1.3877787807814457e-17` | `1.942890293094024e-16` | `0.07142857142857142` | 69 | `450359962737049.6` | fail | pass |
| F2 | 28 | `5.551115123125783e-17` | `3.885780586188048e-16` | `0.14285714285714285` | 28 | `450359962737049.6` | fail | pass |
| F3 | 0 | n/a | n/a | n/a | 0 | n/a | pass | pass |
| F4 | 92 | `8.326672684688674e-17` | `9.71445146547012e-17` | `0.5714285714285714` | 92 | `450359962737049.6` | fail | pass |

F4's result-bound failure is the useful artifact: 92/92 non-zero float64
points exceed `10 * ulp(F4_float64)`, with median residual/result-bound
ratio about `4.5e14`. The residual itself tracks `abs(F4_float64)` with
median residual/absolute-float64 ratio `1.0`.

Spec finding: the Phase A bound should not be `K * ulp(F4_observed)`.
For the F4 path, the correct leading envelope is the path residual law
`delta_f / (2 * sqrt(f))`, which is the V3 transfer law restated as an
instrument envelope. This should feed a follow-up chain-predictor task
rather than being retrofitted into 017b.

## Phase B - Multi-Precision Scaling

- Points where both float32 and float64 produced non-zero F4: 68.
- Points where `abs(F4_float32) > abs(F4_float64)`: 80.
- Median `abs(F4_float32 / F4_float64)`: `536870912.0`.
- Expected binary unit ratio: `536870912.0`.
- Observed / expected: `1.0`.
- Phase B pass: yes.

## Phase C - Calibration Zero

- F3 was exactly `0.0` for all 137 r-values at float32.
- F3 was exactly `0.0` for all 137 r-values at float64.
- F3 was exactly `0.0` for all 137 r-values at decimal-50.
- Non-zero F3 observations: none.
- Phase C pass: yes.

## Honest Observations

- Phase A, as specified, fails for F1, F2, and F4. This is not a data bug;
  it proves the result-ULP bound was attached to the wrong quantity.
- The diagnostic chain-scale envelope records no `10x` failures, so the
  measured float64 residuals remain consistent with operand-scale
  propagation.
- Phase B is unusually crisp: the median float32/float64 F4 magnitude
  ratio equals `2^29` exactly on the shared non-zero subset.
- Phase C confirms F3 is a valid calibration zero across all tested
  arithmetic pathways.
- Overall `model_supported` is `false` in the campaign output because
  Phase A's declared result-bound test fails. The meaningful outcome is
  split: the declared bound fails, while the float32/float64 scaling and
  F3 calibration-zero checks pass.

## Limits

- This task tests only the Schwarzschild four-form battery. SR and Bell
  analogs remain untested at multi-precision.
- Decimal-50 is an oracle arithmetic path, not higher-precision IEEE 754.
- No long-double, mpmath, or platform-specific precision backend was used.
- No chain-predictor utility was added. The corrected F4 envelope belongs
  in a future task.

## Audits

- `python -m pytest -q tests/test_task017b_multi_precision_instrument_model.py`: passed, 8 tests.
- `python -m pytest -q tests/`: passed, 431 tests.
- `python -m pytest -q tests/test_task001_source_purity.py tests/test_task007_source_purity.py tests/test_task008_source_purity.py tests/test_task009a_source_purity.py tests/test_task022_audit_tightening.py`: passed.
- `python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py`: passed.
- `PYTHONPATH=src python -m lloyd_v4.evals.multi_precision_campaign --output /tmp/multi_precision_repeat.json`: passed.
- `diff Build_Docs/Reports/task017b_multi_precision_instrument_model/campaign_output.json /tmp/multi_precision_repeat.json`: passed.
- `git diff --check`: passed.
- Implementation commit: `e598e6ea5e0b4864459acf164ca9b0d23e1a2c7f`.
- Git push: confirmed in final handoff after pushing the task commits.
