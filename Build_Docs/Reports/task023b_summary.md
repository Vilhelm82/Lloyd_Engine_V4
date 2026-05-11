# Task 023b Summary - AlphaProbe Reliability Evidence

## Scope

Implemented Layer 1 AlphaProbe reliability evidence for alpha-zero boundaries
and nested-window drift. No Layer 2+ solver, branch, refinery, history, proxy
calibration, or noise-floor machinery was changed.

## Code Changes

- Added `AlphaWindowFit` and `AlphaWindowStabilityStatus`.
- Added public AlphaProbe constants: `K_BOUNDARY = 2.0`,
  `K_DRIFT = 2.0`, `ALPHA_NUMERIC_FLOOR = 1e-9`,
  `DEFAULT_ALPHA_MATERIALITY = 0.05`, `MIN_WINDOW_POINTS = 3`,
  and `MIN_WINDOW_COUNT = 3`.
- Added nested-window evidence fields to `AlphaProbeObservation`, with
  all-or-none invariant validation and JSON-safe serialization.
- Added `alpha_zero_boundary` and `alpha_unstable_window` AlphaProbe
  statuses.
- Mapped the new AlphaProbe strata 1:1 into scalar and singular
  alpha-jet bundle statuses.
- Exposed the embedded `AlphaProbeObservation` on scalar and singular
  alpha-jet bundle observations.
- Updated Layer 1 exports, machine-readable and Markdown manifests,
  `STATUS_CALCULUS.md`, and `METROLOGY_PRINCIPLES.md`.

## Classification Order

AlphaProbe classification now resolves finite observed alpha in this order:

1. Refusal and non-finite statuses.
2. `alpha_zero_boundary`.
3. `alpha_unstable_window`.
4. Declared model matching.
5. Sign and integer/fractional classification.

Boundary classification wins before unstable-window classification.

## Nested-Window Strategy

For observed transfer pairs, AlphaProbe sorts by h and records the full grid,
then progressively removes the largest h until three points remain. A
seven-point grid produces window sizes `7, 6, 5, 4, 3`; a five-point grid
produces `5, 4, 3`; a four-point grid skips nested-window evidence because it
can only produce two windows.

## Empirical Calibration

The default materiality remains `0.05`, matching the task specification and
the first-run report. The iterated-log fixture uses the `1e-1..1e-7` grid so
its nested span is material under the default.

| Fixture | Status | Observed alpha | Window span | Propagated window error | Stability |
| --- | --- | ---: | ---: | ---: | --- |
| C `sqrt(x) * (1 + 0.1*x**0.1)` | `alpha_fractional_branch` | `0.5038604145993733` | `0.0015028138214885356` | `0.00036045203374965616` | `stable` |
| D `-log(x)` | `alpha_zero_boundary` | `-4.82165418702607e-11` | `2.3143820193638476e-10` | `1.3362104430603933e-10` | `stable` |
| E `log(-log(x))`, h=`1e-1..1e-7` | `alpha_unstable_window` | `0.13254948936333855` | `0.059485468415593656` | `0.01701442043018804` | `unstable` |
| G1 `x**0.01` | `alpha_fractional_branch` | `0.00999999952923114` | `4.981417500715679e-10` | `3.0959826769658898e-09` | `stable` |
| G2 `x**(-0.05)` | `alpha_negative_singularity` | `-0.05000000001772831` | `4.5159320727350405e-10` | `2.672135224729577e-10` | `stable` |

Diff checks:

- D boundary envelope: `max(2 * 5.705037064893224e-11, 1e-9) = 1e-9`;
  `abs(alpha) = 4.82165418702607e-11`, so boundary classification is
  justified.
- E instability: span `0.059485468415593656` is greater than materiality
  `0.05` and greater than `2 * propagated_error = 0.03402884086037608`.
- G1 and G2 remain stable and do not collapse into zero-boundary
  classification.

## Verification

- Baseline from Task 023: 379 tests.
- Post-task collection: 414 tests.
- `python -m pytest -q tests/test_task023b_alphaprobe_reliability.py`
  passed: 35 tests.
- `python -m pytest -x tests/test_task023b_alphaprobe_reliability.py -v`
  passed: 35 tests.
- `python -m pytest -q tests/test_task001_source_purity.py tests/test_task009a_source_purity.py tests/test_task022_audit_tightening.py`
  passed: 11 tests.
- `python -m pytest -q tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py`
  passed: 6 tests.
- `python -m pytest -x tests/ -q` passed all collected tests.
- `git diff --check` passed.
- `rg -n "threshold" src` returned no matches, so no new source audit
  allowance was introduced.

Diff statistics:

```text
src/lloyd_v4/core/status.py                        |   6 +
src/lloyd_v4/primitives/__init__.py                |  16 ++
src/lloyd_v4/primitives/directional_alpha_probe.py | 278 ++++++++++++++++++++-
src/lloyd_v4/primitives/scalar_alpha_jet_bundle.py |  25 +-
src/lloyd_v4/primitives/singular_alpha_jet_bundle.py        |  23 +-
5 files changed, 333 insertions(+), 15 deletions(-)

Build_Docs/Architecture/LAYER_MANIFEST.md       |  6 ++--
Build_Docs/Architecture/METROLOGY_PRINCIPLES.md | 47 +++++++++++++++++++++++++
Build_Docs/Architecture/STATUS_CALCULUS.md      | 20 +++++++++++
Build_Docs/Architecture/layer_manifest.json     |  6 ++--
4 files changed, 73 insertions(+), 6 deletions(-)
```

New task artifacts:

- `tests/test_task023b_alphaprobe_reliability.py`: 507 lines, 35 tests.
- `Build_Docs/Reports/task023b_summary.md`: 112 lines.

Task 024 can now be specified against AlphaProbe statuses that distinguish
alpha-zero boundary evidence from stable negative powers and unstable
finite-window drift from algebraic fractional branches.
