# Task 003 Design Decisions

## Consume Root-State Results

Decision: `exact_quadratic_projection` consumes Task 002 root-state `TypedResult` objects and rejects raw coefficients or scalar roots.

Reason: Projection is a protocol consumer over typed root-state evidence. Re-running quadratic classification from raw coefficients would bypass the typed substrate and provenance chain.

## Tangent Contact Is Not Advance-Valid

Decision: `repeated_root` maps to `projection_tangent_contact` with `selected_root_valid=True` and `advance_valid=False`.

Reason: Task 002 can select the repeated scalar root, but Task 003 distinguishes scalar selection from a valid projection advance. Tangent contact is a projection stratum, not generic success.

## Constant Identity Has Roots But No Unique Projection

Decision: `constant_identity` maps to `projection_identity` with `root_exists=True` and `projection_defined=False`.

Reason: Every real input satisfies the equation, so the solution set is nonempty. It does not define a unique projection target.

## No Positive, Nearest, Nonzero, Or Principal Policy

Decision: Task 003 imposes no branch selection policy beyond explicit compatibility.

Reason: Positive-time, nearest-root, nonzero-displacement, or principal-root rules are consumer policies. The substrate must preserve the branch request and refuse incompatible labels rather than choosing for the caller.

## Use Task 002 Selection

Decision: Successful projection obtains scalar roots through `select_quadratic_root(...)`.

Reason: Task 002 already routes selected roots through ProjectiveRatio scalarization and records the selection provenance. Task 003 wraps that result instead of recomputing formulas or dividing projective coordinates.

## Existing Provenance Metadata

Decision: The Task 000 `measurement_resolution` provenance field remains unchanged and may be copied through provenance.

Reason: It is substrate metadata, not a Task 003 metrology estimator or calibration mechanism.
