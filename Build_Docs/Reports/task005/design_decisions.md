# Task 005 Design Decisions

## Generic TypedResult With Runtime Validation

Decision: `TypedResult` is now generic over value type and status enum family, while runtime validation remains mandatory.

Reason: Generics improve static readability and future checkability, but Python runtime composition still needs explicit protocol checks.

## Runtime StatusCode Preserved

Decision: The existing runtime `StatusCode` union remains available.

Reason: Existing serialization and validation rely on concrete enum instances. The generic typing layer is additive.

## Protocols Are Status-Family Aware

Decision: `ProducerProtocol` and `ConsumerProtocol` now infer or declare `status_family`.

Reason: Wrong-family results should fail clearly before being treated as ordinary accepted-set misses.

## Generic Mixed Joins Stay Conservative

Decision: `join_statuses(...)` remains conservative and does not infer mixed-family composition.

Reason: Mixed status composition requires named transition rules, not a universal lattice.

## Named Rules Are Not A Universal Lattice

Decision: Task 005 adds explicit `StatusTransitionRule` objects for known composition paths only.

Reason: Projective scalarization, root selection, projection, limit-of-detection, and calibration are real protocol transitions. Other combinations remain invalid until named.

## Contextual Transitions

Decision: Contextual rules declare required context keys and use transition callbacks for branch or observable-specific outcomes.

Reason: Branch compatibility and limit-of-detection classification depend on context and should not be flattened into misleading status-only maps.

## Serialization Compatibility

Decision: Generic typing metadata is not serialized, and existing result serialization shape is unchanged.

Reason: Type aliases and TypeVar machinery are developer-facing metadata. They are not result evidence.

## BranchFingerprint Deferred

Decision: BranchFingerprint and slope-flow comparison remain deferred to Task 006.

Reason: Task 005 only hardens status-family composition so Task 006 can consume explicit transition rules.
