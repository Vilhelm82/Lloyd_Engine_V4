# Task 020 Summary - Precision Floor Reconciliation

## Scope

Task 020 reconciled the `raw_python` precision-floor documentation with the existing implementation. `_precision_floor("raw_python")` still returns `2.0**-52`; the task documents that value as the worst-case `2u` cancellation threshold for forward-difference subtraction, not the per-operand unit roundoff `u = 2^-53`.

## Test Counts

- Pre-task baseline: 344 tests passing.
- Post-task collection: 349 tests.
- Added tests: 5 in `tests/test_task020_precision_floor_reconciliation.py`.
- Full suite: `349 passed in 3.59s`.

## Files Changed

- `src/lloyd_v4/primitives/typed_finite_difference.py`: comment-only derivation above `return 2.0**-52`.
- `Build_Docs/Architecture/METROLOGY_PRINCIPLES.md`: first section replaced with the `2u` subtraction-envelope derivation.
- `tests/test_task020_precision_floor_reconciliation.py`: new regression tests locking value, runtime cross-reference, unsupported precision refusal, and status-only behavior.
- `tests/test_task001_source_purity.py` through `tests/test_task009a_source_purity.py`: narrowed source-purity allowances for the required `_precision_floor` comment only.
- `Build_Docs/Reports/task020_summary.md`: this report.

The source-purity audit adjustment was required because the mandated source comment contains `sys.float_info.epsilon`, `guard`, and `worst-case`; older broad grep audits caught `epsilon`, `eps`, `guard`, and `cas`. The allowance is limited to `src/lloyd_v4/primitives/typed_finite_difference.py`.

## METROLOGY_PRINCIPLES Excerpt

```text
The `_precision_floor` lookup in `typed_finite_difference` returns the
worst-case relative round-off envelope of forward-difference subtraction
for the declared precision. For `raw_python` (IEEE 754 double under
round-to-nearest), the floor is `2.0**-52`, derived from the per-operand
unit roundoff `u = 2^-53`.
```

## Source Comment Excerpt

```python
# Per-operand unit roundoff: u = 2^-53.
# For forward finite difference delta_g = g(f+delta_f) - g(f),
# worst-case absolute round-off in delta_g is approximately
# 2u * max(|g_f|, |g_f_plus|).
# Status-only: this floor never alters the computed transfer value;
return 2.0**-52
```

## Locked-In Assertions

```python
assert floor == 2.0 * u
assert floor == 2.0**-52
assert _precision_floor("raw_python") == sys.float_info.epsilon
assert floor != unit_roundoff
assert result.value.cancellation_ratio < _precision_floor("raw_python")
```

Additional assertions confirm unsupported precision modes raise `ProtocolViolationError`, computed transfer fields are preserved on `TRANSFER_CANCELLATION_DOMINATED`, and validity remains non-selectable/non-advanceable but observable.

## Reclassification Check

No numerical code path changed. The full suite remained green at 349 tests, which is the evidence that existing observations and alpha-recovery fixtures did not reclassify. No behavioral tests required re-baselining.

## Source-Purity Audit

- `tests/test_task001_source_purity.py` through `tests/test_task009a_source_purity.py` pass after the narrow Task 020 comment allowance.
- The explicit pattern audit returned expected source matches in `typed_finite_difference.py`, expected test matches in Task 020 and purity audits, expected architecture matches in `METROLOGY_PRINCIPLES.md`, plus pre-existing historical task/report matches under `Build_Docs/Agent_tasks/Completed` and `Build_Docs/Reports/targeted_audit_jetbundle_solver`.
- No new source-side metrology estimator, new protocol, b_k noise floor, K_q calibration, or branch-fingerprint machinery was introduced.

## Limits

- No numerical value change.
- No new precision mode.
- No new status, value type, protocol, field, or computation branch.
- No changes to `directional_alpha_probe`, `scalar_alpha_jet_bundle`, or Layer 2+ modules.
