# Task 006 Design Decisions

## Slope Ratios Use ProjectiveRatio

Decision: Each finite-difference slope is represented as a ProjectiveRatio before scalarization.

Reason: `D log y / D log x` is still a ratio. Task 001 rules apply.

## Declared Bands Are Explicit Evidence

Decision: `declared_model_band` and `declared_stability_band` are caller-provided evidence fields and are serialized.

Reason: They are model-comparison policy, not hidden correction constants.

## Kq Pointwise Validity Is Not Enough

Decision: Proxy fingerprints require Kq slope-stability evidence, not only Task 004 pointwise calibration.

Reason: Pointwise finite nonzero Kq does not establish transfer-observable stability.

## BranchFingerprint Is Not A Domain Classifier

Decision: BranchFingerprint emits evidence-completeness and model-comparison status only.

Reason: Domain branch identity belongs to later consumers, not the substrate.

## Tangent Contact Remains Not Advance-Valid

Decision: Projection tangent contact can contribute usable projection evidence while preserving `advance_valid=False`.

Reason: Task 003 separated selected root validity from projection advancement.

## No Hidden Log Offset

Decision: Zero or non-loggable observables are excluded or marked indeterminate. No offset, smoothing, or adjusted logarithm is used.

Reason: Log-domain failure is evidence, not a value to patch.

## Named Transition Composition

Decision: BranchFingerprint composition uses exported Task 006 transition rules.

Reason: Mixed projection, transfer, and Kq statuses must compose through named protocols rather than local ad hoc joins.
