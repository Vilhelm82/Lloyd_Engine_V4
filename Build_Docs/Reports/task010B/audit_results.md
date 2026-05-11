# Audit Results

## Manifest Completeness

Result: pass.

The manifest contains all eight layers in topological order: `core`, `primitives`, `projection`, `metrology`, `branch`, `refinery`, `history`, `solver`. Every layer has the required keys and all seven `provides` categories.

## Export Drift

Result: pass.

- `core`: match
- `primitives`: match
- `projection`: match
- `metrology`: match
- `branch`: match
- `refinery`: match
- `history`: match
- `solver`: match

No manifest-only or source-only export names were found.

## Cross-Layer Parent Check

Result: pass.

- Total `lloyd_v4` imports inspected: 118
- Total cross-layer imports inspected: 113
- Total violations: 0

Every cross-layer import targets a layer declared as a parent of the importing layer.

## Status-Family Layer Coherence

Result: pass.

- `DomainStatus`: non-allowed references 0
- `StratumStatus`: non-allowed references 0
- `ValidityStatus`: non-allowed references 0
- `ConditioningStatus`: non-allowed references 0
- `ProtocolStatus`: non-allowed references 0
- `ProvenanceStatus`: non-allowed references 0
- `ProjectiveRatioStatus`: non-allowed references 0
- `QuadraticRootStatus`: non-allowed references 0
- `ProjectionStatus`: non-allowed references 0
- `MetrologyStatus`: non-allowed references 0
- `BranchFingerprintStatus`: non-allowed references 0
- `RefineryStatus`: non-allowed references 0
- `HistoryStatus`: non-allowed references 0
- `SolverStatus`: non-allowed references 0

The physical declarations in `core/status.py` were excluded from reference counting as required.

## Manifest Corrections

No source violations required correction. The only manifest correction was the intended 010B reconciliation: semantic status-family ownership was distributed across layers and `all_exports` was made explicit per layer.
