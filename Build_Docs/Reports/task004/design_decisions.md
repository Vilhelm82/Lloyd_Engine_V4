# Task 004 Design Decisions

## Observability Only

Decision: Declared and estimated limits classify observability only.

Reason: Metrology evidence must not alter exact ProjectiveRatio, quadratic-root, or projection strata.

## No Exact-Stratum Reclassification

Decision: Task 004 does not import into earlier primitive/projection layers and does not change their behavior.

Reason: Earlier layers carry exact algebraic strata. Metrology may annotate evidence but cannot rewrite those results.

## Zero Requires Identity Evidence

Decision: `observable == 0` is not `identity_zero` unless `identity_evidence=True`.

Reason: A zero observation may be below the observation limit, instrument-limited, or indeterminate. Identity-zero is a stronger claim.

## K_q Uses ProjectiveRatio

Decision: K_q calibration uses `projective_ratio(proxy_observable, transfer_observable)` and explicit scalarization.

Reason: K_q is a ratio. Task 001 already established that a ratio is projective evidence before it is a scalar.

## Pointwise Calibration Only

Decision: `calibration_valid` means finite nonzero pointwise K_q evidence only.

Reason: Slope-flow stability, transfer-exponent identification, and model comparison belong to later tasks.

## Deferred Work

Decision: BranchFingerprint and slope-flow comparison are deferred to Task 005.

Reason: Task 004 creates the metrology evidence substrate needed by that later work but does not infer branch identity.

## Existing Provenance Metadata

Decision: The existing `measurement_resolution` provenance field remains unchanged.

Reason: It was introduced in Task 000 as substrate metadata and is distinct from Task 004 metrology estimators.
