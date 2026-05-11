# ProjectiveRatio Scalarization Protocol

Producer:

```text
PROJECTIVE_RATIO_PROTOCOL
```

Emitted statuses:

- `finite_ratio`
- `signed_zero`
- `infinite_direction`
- `indeterminate`

Consumer:

```text
PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL
```

Accepted statuses:

- `finite_ratio`
- `signed_zero`

Refused statuses:

- `infinite_direction`
- `indeterminate`

## Runtime Validation

`scalarize_projective_ratio(result)` validates the result against `PROJECTIVE_RATIO_SCALARIZATION_PROTOCOL`.

If validation succeeds, scalarization creates a child `TypedResult` in scalar space. Its provenance parent is the trace ID of the projective result.

If validation fails, scalarization returns a scalar-space `TypedResult` with:

- `value=None`
- `protocol=scalarization_refused`
- original projective status preserved
- `TypedRefusal` carrying the projective status and protocol reason

Unhandled statuses therefore fail explicitly through the protocol path.
