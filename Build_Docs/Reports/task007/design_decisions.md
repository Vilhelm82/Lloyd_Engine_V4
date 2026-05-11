# Task 007 Design Decisions

## Typed observations, not equation parsing

The refinery consumes already-computed V4 `TypedResult` evidence. This keeps Task 007 inside the V4 typed numerical geometry boundary and avoids symbolic parsing, simplification, or rewrite generation.

## Evidence-based same geometry

`same_geometry` means preservation of supplied typed evidence, not a universal proof of algebraic equivalence. The check inspects family-specific fingerprints: projective coordinate shape, quadratic branch labels, projection branch and flags, metrology roles, fingerprint model evidence, observable kind, proxy mode, and source traces.

## Status preservation is mandatory

A candidate cannot claim improvement by changing a diagnostic status. For example, a metrology result moving from below-limit to detected is a status mismatch, not an improvement.

## Protocol preservation is mandatory

Producer protocol identity is part of the observation contract. If a candidate changes the evidence-producing protocol, the comparison is rejected before slag is considered.

## Validity preservation is mandatory

Validity fields encode whether the observation is defined, finite, selectable, advanceable, and observable. Changing those fields changes the typed geometry contract and is rejected.

## Branch, model, and fingerprint evidence are geometry

Projection branch labels, projection flags, selected model name, observable kind, proxy mode, and fingerprint components are geometry evidence for Task 007. A candidate that changes them is not the same observation with less diagnostic burden.

## Lower slag is explicit and componentwise

Slag is a named evidence vector: warning, refusal, indeterminate, incomplete, uncalibrated, unstable, max model residual, and max Kq slope evidence when present. The refinery does not compute a hidden scalar score and does not rank multiple candidates.

## Trace IDs may differ

Reference and candidate trace IDs may differ because a rewrite should usually have a different expression path. Source trace IDs must still be preserved sufficiently for auditability.

## Not a domain classifier

BranchFingerprint evidence is consumed as typed geometry evidence only. The refinery does not infer bearings, aerospace regimes, scanners, betting states, or any other downstream domain category.

## No hidden comparison constants

Task 007 compares finite Python values already stored in typed evidence. It does not add hidden numerical floors, confidence scores, weighted scores, or unreported comparison constants.
