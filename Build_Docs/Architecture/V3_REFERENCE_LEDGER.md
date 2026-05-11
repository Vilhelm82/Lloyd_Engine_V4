# V3 Reference Ledger

V3 is reference-only. V4 must not import, call, adapt, or bridge to V3.

V3 targets may be copied as static fixtures when a future task needs evidence. V3 known dirty equations are evidence, not architecture. V4 may deliberately diverge from V3 when the typed result is more honest.

## Initial Evidence

- `stratified_quadratic_roots` was the first true ingot.
- `safe_mask` was retired as a source of truth in V3 Pass11.
- V3 Pass08 integrated stratified quadratic projection in legacy-compatible mode.
- V3 Pass09 introduced exact projection mode.
- V3 Pass10 validated CUDA performance and tensor-native cleanup.
- V3 Pass11 made exact projection mode default.
- V4 should not inherit V3 legacy modes.

## Boundary

This ledger may name historical evidence. It must not become a live link to old runtime behavior. Static fixtures are acceptable; cross-engine calls are not.
