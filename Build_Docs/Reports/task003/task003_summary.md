# Task 003 Summary

Task 003 implemented `ProjectionResultV4` and the exact quadratic projection protocol.

## Files Created

- `src/lloyd_v4/projection/__init__.py`
- `src/lloyd_v4/projection/exact_projection.py`
- `tests/test_task003_projection_result.py`
- `tests/test_task003_projection_protocol.py`
- `tests/test_task003_projection_serialization.py`
- `tests/test_task003_source_purity.py`
- `Build_Docs/Reports/task003/task003_summary.md`
- `Build_Docs/Reports/task003/projection_result_status_table.md`
- `Build_Docs/Reports/task003/design_decisions.md`

## Files Modified

- `src/lloyd_v4/core/status.py`

## Behavior Summary

`exact_quadratic_projection(root_state_result, branch)` consumes a validated Task 002 root-state `TypedResult`. It rejects raw coefficient tuples, scalar roots, and unrelated typed results through `ProtocolViolationError`.

Projection emits structured `ProjectionResultValue` evidence with:

- source root-state status
- requested branch
- selected branch and selected scalar root value when selection succeeds
- selected-root child trace ID when selection succeeds
- Task 002 refusal evidence when selection refuses
- projection flags
- source trace and source operation identity

The projection statuses are:

- `projection_transverse`
- `projection_tangent_contact`
- `projection_linear`
- `projection_no_real_root`
- `projection_identity`
- `projection_no_solution`
- `projection_selection_refused`

## Red Test Result

Command:

```text
python -m pytest tests/test_task003_projection_result.py tests/test_task003_projection_protocol.py tests/test_task003_projection_serialization.py tests/test_task003_source_purity.py -q
```

Result: failed during collection because `ProjectionStatus` and `lloyd_v4.projection` did not exist.

## Task 003 Test Slice

Command:

```text
python -m pytest tests/test_task003_projection_result.py tests/test_task003_projection_protocol.py tests/test_task003_projection_serialization.py tests/test_task003_source_purity.py -q
```

Result:

```text
...................                                                      [100%]
```

## Full Suite

Command:

```text
python -m pytest tests -q
```

Result:

```text
.................................................................        [100%]
```

## Source Audits

Command:

```text
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
```

Result: no matches.

Command:

```text
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard" src/lloyd_v4 -n
```

Result: no matches.

Command:

```text
rg "disc_floor|discriminant_floor|clamp_discriminant|safe_sqrt|sqrt_guard|small_discriminant|tolerance|threshold" src/lloyd_v4 -n
```

Result: no matches.

Command:

```text
rg "principal_root|nearest_root|default_branch|auto_branch|root_policy|advance_policy|projection_fallback|fallback_branch" src/lloyd_v4 -n
```

Result: no matches.

Adjusted metrology-machinery audit:

```text
rg "b_k|K_q|branch_fingerprint|fingerprint|noise_floor|calibration" src/lloyd_v4/projection src/lloyd_v4/primitives -n
```

Result: no matches.

The Task 000 provenance field `measurement_resolution` is intentionally allowed as substrate metadata and was not renamed.

## Deviations

The original Task 003 audit listed `measurement_resolution` beside new metrology machinery. The user clarified that the existing Task 000 provenance field is allowed and the audit should target new metrology estimators, protocols, noise-floor work, calibration, and branch-fingerprint machinery instead.

No domain consumer, spatial projection, flow integration, branch policy, metrology estimator, branch fingerprint, K_q calibration, V3 fixture, adapter, bridge, or compatibility mode was added.

## Task 004 Readiness

Task 004 is ready to scope as `Metrology foundation: b_k noise floor and K_q calibration`.
