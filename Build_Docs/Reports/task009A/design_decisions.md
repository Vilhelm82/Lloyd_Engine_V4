# Task 009A Design Decisions

## Public API Fixtures

Scenario tests use public solver APIs and earlier public V4 APIs. Test helpers construct `LocalQuadraticStepModel`, BranchFingerprint, and refinery evidence without reaching into solver internals.

## Wrong-Family Evidence Behavior

Wrong-family noise-floor evidence returns `solver_protocol_refused` with typed refusal evidence. Invalid structural model construction still raises `ProtocolViolationError`, matching existing V4 validation style.

## Branch And Refinery Evidence

Branch evidence is created with Task 006 public constructors and status-replaced only when the test specifically targets a status-family gate path. Refinery evidence is produced through Task 007 APIs, then status-replaced for gate matrix coverage.

## History Geometry Signatures

Geometry signatures are simple caller-supplied strings. The tests cover both stable signatures and changed signatures. A separate scenario forced projection status itself to be preserved in history.

## Minimal Source Fixes

Two source fixes were made:

- Residual `detection_indeterminate` now maps to `solver_indeterminate`.
- Solver projection-history event sources now preserve actual projection status.

Both fixes keep Task 009 semantics inside existing V4 layers.

## No Task 010 Behavior

No JetBundle, local model extraction, parser, automatic differentiation, or model provider was added. The solver still consumes supplied local quadratic models.
