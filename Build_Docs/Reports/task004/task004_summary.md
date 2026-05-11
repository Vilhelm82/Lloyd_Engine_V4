# Task 004 Summary

Task 004 implemented the first Layer 2 metrology foundation: b_k noise-floor evidence, limit-of-detection classification, and pointwise K_q proxy calibration.

## Files Created

- `src/lloyd_v4/metrology/noise_floor.py`
- `src/lloyd_v4/metrology/proxy_calibration.py`
- `tests/test_task004_bk_noise_floor.py`
- `tests/test_task004_kq_calibration.py`
- `tests/test_task004_metrology_protocols.py`
- `tests/test_task004_metrology_serialization.py`
- `tests/test_task004_no_reclassification.py`
- `tests/test_task004_source_purity.py`
- `Build_Docs/Reports/task004/task004_summary.md`
- `Build_Docs/Reports/task004/metrology_status_table.md`
- `Build_Docs/Reports/task004/design_decisions.md`

## Files Modified

- `src/lloyd_v4/core/status.py`
- `src/lloyd_v4/metrology/__init__.py`

## Behavior Summary

`declare_bk_noise_floor(...)` records explicit nonnegative caller-provided b_k noise-floor evidence.

`estimate_bk_noise_floor(...)` supports only `method="max_abs_observed"` and records either estimated evidence or indeterminate empty-observation evidence.

`classify_against_noise_floor(...)` consumes typed noise-floor evidence and emits detected, below-limit, detection-indeterminate, or explicit identity-zero evidence. Zero is not identity-zero unless `identity_evidence=True`.

`calibrate_proxy_kq(...)` creates K_q evidence through `ProjectiveRatio(proxy_observable, transfer_observable)` and explicit scalarization. It emits pointwise `calibration_valid`, `calibration_invalid`, or `calibration_indeterminate` evidence.

`proxy_uncalibrated(...)` records missing calibration evidence as a typed result.

`require_valid_proxy_calibration(...)` accepts only valid calibration evidence and returns typed refusals for invalid, indeterminate, or uncalibrated proxy evidence.

## Red Test Result

Command:

```text
python -m pytest tests/test_task004_bk_noise_floor.py tests/test_task004_kq_calibration.py tests/test_task004_metrology_protocols.py tests/test_task004_metrology_serialization.py tests/test_task004_no_reclassification.py tests/test_task004_source_purity.py -q
```

Result: failed during collection because Task 004 metrology APIs did not exist.

## Task 004 Test Slice

Command:

```text
python -m pytest tests/test_task004_bk_noise_floor.py tests/test_task004_kq_calibration.py tests/test_task004_metrology_protocols.py tests/test_task004_metrology_serialization.py tests/test_task004_no_reclassification.py tests/test_task004_source_purity.py -q
```

Result:

```text
..............................                                           [100%]
```

## Full Suite

Command:

```text
python -m pytest tests -q
```

Result:

```text
........................................................................ [ 75%]
.......................                                                  [100%]
```

## Source Audits

Command:

```text
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
```

Result: no matches.

Command:

```text
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Result: no matches.

Command:

```text
rg "disc_floor|discriminant_floor|clamp_discriminant|safe_sqrt|sqrt_guard|small_discriminant|threshold|tolerance" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Result: no matches.

Command:

```text
rg "lloyd_v4\.metrology|from lloyd_v4\.metrology|import .*metrology" src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Result: no matches.

Command:

```text
rg "branch_fingerprint|fingerprint|slope_flow|flow_model|finite_eta|domain_consumer" src/lloyd_v4/metrology src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Result: no matches.

Command:

```text
rg "b_k|K_q|noise_floor|calibration" src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Result: no matches.

## Deviations

No deviations from Task 004 scope.

The existing Task 000 `measurement_resolution` provenance field remains unchanged.

## Task 005 Readiness

Task 005 is ready to scope as `BranchFingerprint object and slope-flow model comparison`.
