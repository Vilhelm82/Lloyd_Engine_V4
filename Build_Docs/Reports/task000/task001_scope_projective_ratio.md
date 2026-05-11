# Task 001 Scope: ProjectiveRatio

Implement ProjectiveRatio as the first primitive.

Represent `n/d` as a projective state, not a scalar.

Statuses:

- `finite_ratio`
- `signed_zero`
- `infinite_direction`
- `indeterminate`

Scalarization must be explicit and may refuse.

No eps, no denominator floor, no hidden guard rail.

## Required Shape

ProjectiveRatio should emit a `TypedResult` whose value is a projective representation such as `[n:d]` or an equivalent structured object.

Scalarization should be a separate operation. It may return a scalar only for statuses whose protocol permits scalar output.

## Required Tests

- finite denominator produces `finite_ratio`
- zero numerator with finite denominator produces `signed_zero`
- zero denominator with nonzero numerator produces `infinite_direction`
- zero numerator and zero denominator produces `indeterminate`
- scalarization refuses non-scalarizable strata
- no hidden denominator rescue appears in implementation
