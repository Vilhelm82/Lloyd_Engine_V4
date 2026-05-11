# Task 009 Design Decisions

## Caller-Supplied Local Models

Task 009 deliberately consumes `LocalQuadraticStepModel` values supplied by the caller. It does not generate local models, inspect expressions, or extract jets.

## No V1 Transport Port

The solver does not port V1 Halley transport, multistart routing, or old scoring behavior. It composes V4 typed substrates only.

## Metrology-Backed Convergence

Convergence is determined by Task 004 limit-of-detection evidence. The solver does not compare residuals to an internal numeric tolerance.

## Below Detection Is Not Identity

`below_limit_of_detection` can terminate only when `SolverPolicy.accept_below_detection` is true. It remains distinct from `identity_zero`.

## Projection Semantics Come From Task 003

The solver uses Task 002 root-state construction and Task 003 exact projection. Tangent contact remains non-advance-valid, and the solver does not divide projective coordinates or implement another quadratic formula.

## History Tracks Projection Geometry

Projection history records accepted projection events and optional geometry signatures. It does not treat ordinary terminal solver-status changes as projection instability.

## Explicit Gates

BranchFingerprint and refinery checks are policy-controlled. When enabled, they are protocol-validated and block through typed solver statuses.

## No Domain Consumer

The solver does not infer any downstream domain meaning. It produces typed solver evidence only.
