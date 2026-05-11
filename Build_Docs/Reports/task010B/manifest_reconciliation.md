# Manifest Reconciliation

## Summary

Task 010B replaced the 010A JSON manifest's mixed `concepts`/`exports` shape with a uniform categorised schema. Each layer now declares:

- `status_families`
- `value_types`
- `protocol_types`
- `transition_types`
- `errors_and_utilities`
- `operations`
- `all_exports`

The Markdown manifest was rewritten to render the same categories in the same order. The JSON manifest remains normative.

## Status Family Ownership

Status-family ownership was changed from physical declaration-site ownership to semantic ownership:

- `core`: `DomainStatus`, `StratumStatus`, `ValidityStatus`, `ConditioningStatus`, `ProtocolStatus`, `ProvenanceStatus`
- `primitives`: `ProjectiveRatioStatus`, `QuadraticRootStatus`
- `projection`: `ProjectionStatus`
- `metrology`: `MetrologyStatus`
- `branch`: `BranchFingerprintStatus`
- `refinery`: `RefineryStatus`
- `history`: `HistoryStatus`
- `solver`: `SolverStatus`

The families remain physically declared in `core/status.py`; the manifest records the layer that semantically owns each vocabulary.

## Layer Summaries

`core` records cross-cutting substrate status families, typed result/refusal and provenance value types, protocol check types, transition rule types, core errors, serialization/status-calculus utilities, and transition/protocol operations.

`primitives` records projective-ratio and quadratic-root status families, value/result types, producer/consumer protocols, scalarization/root-selection transition rules, operation-space constants, and primitive operations.

`projection` records projection status ownership, exact-projection value/result types, projection protocols, the quadratic-root-to-projection transition rule, and `exact_quadratic_projection`.

`metrology` records metrology status ownership, noise-floor, limit-of-detection, proxy-calibration, and valid-calibration value/result types, their protocols, transition rules, and metrology operations already present in the substrate.

`branch` records branch fingerprint status ownership, Kq stability, branch fingerprint, and slope-flow value/result types, branch/slope protocols, branch transition rules, status-set utilities, and branch operations.

`refinery` records refinery status ownership, typed-result snapshots, refinery observations, slag vectors, scenario comparisons, refinery decisions, refinery protocols, preservation/acceptance transition rules, slag utilities, and rewrite-evaluation operations.

`history` records history status ownership, status event/transition/trace value and result types, history protocols, history transition rules, status-set utilities, and trace operations.

`solver` records solver status ownership, solver policy, local step model, step/run value and result types, solver protocols, solver transition rules, terminal-status utilities, and solver operations.

## Discrepancies Found

The 010A JSON manifest collapsed every status family into `core` and used uneven `concepts`/`exports` keys. The Markdown already described richer `core` categories but did not provide uniform per-layer categories. 010B reconciled both surfaces to the categorised JSON schema.

## Export Drift

The `all_exports` list for every layer was verified against its actual `src/lloyd_v4/<layer>/__init__.py __all__`. All eight layers match exactly.
