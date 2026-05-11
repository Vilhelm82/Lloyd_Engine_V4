# Task 002 Design Decisions

## Direct Algebraic Path Only

Decision: Task 002 uses the direct quadratic formula path and records it as `direct_quadratic_formula`.

Reason: Alternate formulas create multiple expression paths and belong in later path-aware work.

## Square Root Only After Stratum Classification

Decision: `sqrt(discriminant)` is computed only for `two_real_roots`.

Reason: `repeated_root` has a direct projective coordinate `[ -b : 2*a ]`, and `no_real_root` has no real-root coordinate in Task 002.

## Projective Coordinates Before Scalar Selection

Decision: Root branches are stored as `ProjectiveRatioValue` evidence before scalar root output.

Reason: This preserves the Task 001 rule that ratio-like quantities are typed projective states before scalarization.

## Selection Uses ProjectiveRatio

Decision: `select_quadratic_root` uses the Task 001 ProjectiveRatio scalarization path internally, then wraps the result in quadratic-root selection provenance.

Reason: This keeps scalar division behind the explicit protocol path and preserves both root-state and projective-ratio trace evidence.

## Non-Finite Inputs

Decision: Non-finite or non-real scalar coefficients raise `ProtocolViolationError`.

Reason: Task 002 is scalar-only for finite real coefficients. Non-finite inputs are not mathematical root strata.

## Conditioning

Decision: `repeated_root` is marked with `ConditioningStatus.WARNING`; other classified statuses are marked well-conditioned for M2.

Reason: Repeated roots are structurally degenerate. Task 002 does not estimate numeric condition values.
