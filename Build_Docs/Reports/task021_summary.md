# Task 021 Summary - Singular AlphaJetBundle

## Scope

Task 021 added the Layer 1 primitive `singular_alpha_jet_bundle` as a sibling of `scalar_alpha_jet_bundle`.

The primitive constructs only the singular-direct probe
`g_singular(h) = func(x0 + h)` and delegates alpha measurement to
`directional_alpha_probe`. It does not evaluate `func(x0)`, does not add
derivative fields, and does not include an `f_value` field.

## Test Counts

- Pre-task baseline: 349 tests passing.
- Added tests: 23 in `tests/test_task021_singular_alpha_jet_bundle.py`.
- Post-task collection: 372 tests.
- Full suite: `372 passed in 4.27s`.

## Files Changed

- `src/lloyd_v4/core/status.py`: added `SingularAlphaJetBundleStatus` and included it in `StatusCode`.
- `src/lloyd_v4/primitives/singular_alpha_jet_bundle.py`: new Layer 1 primitive, observation type, protocols, status mapping, provenance, validity, and conditioning.
- `src/lloyd_v4/primitives/__init__.py`: exported the singular bundle API.
- `tests/test_task021_singular_alpha_jet_bundle.py`: new regression coverage for singular strata, no-`x0` evaluation, protocol behavior, serialization, trace identity, and sibling separation from scalar bundles.
- `Build_Docs/Architecture/layer_manifest.json`: registered the new Layer 1 status family, value types, protocols, space, operation, calibrated primitive operation, and exports.
- `Build_Docs/Architecture/LAYER_MANIFEST.md`: human-readable manifest rendering updated.
- `Build_Docs/Architecture/STATUS_CALCULUS.md`: added Singular AlphaJetBundle strata and explicit AlphaProbe mapping doctrine.
- `Build_Docs/Reports/task021_summary.md`: this report.

## Status Mapping

Singular AlphaJetBundle maps the embedded `AlphaProbeStatus` directly:

- `alpha_regular_integer` -> `singular_jet_regular_integer_alpha`
- `alpha_fractional_branch` -> `singular_jet_fractional_alpha_branch`
- `alpha_negative_singularity` -> `singular_jet_negative_alpha_singularity`
- `alpha_model_ambiguous` or `alpha_model_no_match` -> `singular_jet_alpha_model_refused`
- `alpha_cancellation_dominated` -> `singular_jet_alpha_cancellation_dominated`
- `alpha_insufficient_data` or `alpha_indeterminate` -> `singular_jet_alpha_indeterminate`
- `alpha_domain_refused` -> `singular_jet_domain_refused`
- `alpha_nonfinite` -> `singular_jet_nonfinite`

`singular_jet_protocol_refused` remains reserved for recoverable downstream protocol refusal. No structurally unreachable status cases were introduced.

## Runtime Evidence

Canonical singular-direct probes at `x0=0` produced the expected alpha strata:

```text
1/x       -> singular_jet_negative_alpha_singularity, alpha ~= -1.0
1/x^2     -> singular_jet_negative_alpha_singularity, alpha ~= -2.0
sqrt(x)   -> singular_jet_fractional_alpha_branch, alpha ~= 0.5
x         -> singular_jet_regular_integer_alpha, alpha ~= 1.0
x^2       -> singular_jet_regular_integer_alpha, alpha ~= 2.0
```

The no-origin-evaluation audit used a callable that raises at `x == 0.0`.
The result still classified `1/x` as `singular_jet_negative_alpha_singularity`,
and the recorded call list did not contain `0.0`.

The sibling trace audit confirmed that `singular_alpha_jet_bundle` and
`scalar_alpha_jet_bundle` at the same `x0` produce distinct AlphaProbe trace
IDs because the embedded probe labels and probe semantics differ.

## Verification

- `PYTHONPATH=src python -m pytest -x tests/test_task021_singular_alpha_jet_bundle.py -q`
  - `23 passed`
- `PYTHONPATH=src python -m pytest -x tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py -q`
  - `7 passed`
- `PYTHONPATH=src python -m pytest -x tests/test_task001_source_purity.py tests/test_task009a_source_purity.py -q`
  - `4 passed`
- `PYTHONPATH=src python -m pytest -x tests/`
  - `372 passed in 4.27s`

Explicit contamination scans returned no matches:

```text
rg "lloyd_v3|lloyd_v1|safe_mask|legacy_compat|clamp_min|epsilon|eps" src/lloyd_v4/primitives/singular_alpha_jet_bundle.py -n
rg "from lloyd_v4\.(metrology|branch|refinery|history|solver)" src/lloyd_v4/primitives/singular_alpha_jet_bundle.py -n
```

## Boundary Notes

- No Layer 2+ modules were imported or modified.
- No metrology estimator, metrology protocol, `b_k` noise floor, `K_q` calibration, or branch-fingerprint machinery was introduced.
- `scalar_alpha_jet_bundle.py` was not modified.
- Existing core provenance fields, including `measurement_resolution`, were left intact.
