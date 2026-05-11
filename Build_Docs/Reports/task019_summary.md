# Task 019 Summary - Scalar AlphaJetBundle Primitive

## Scope

Implemented the Layer 1 `scalar_alpha_jet_bundle` calibrated primitive. The primitive constructs `g_local(h) = f(x0+h) - f(x0)`, delegates alpha measurement to `directional_alpha_probe`, mirrors AlphaProbe lineage, and exposes a convenience derivative from the smallest-h observed `typed_finite_difference` transfer.

No Layer 2+ V3-shaped modules were imported or used.

## Tests

- Added `tests/test_task019_scalar_alpha_jet_bundle.py` with 25 tests.
- Full suite result: `344 passed in 3.59s`.
- Baseline was 319 tests after Task 018; Task 019 adds 25 tests.

## Files Changed

- `src/lloyd_v4/core/status.py`
- `src/lloyd_v4/primitives/scalar_alpha_jet_bundle.py`
- `src/lloyd_v4/primitives/__init__.py`
- `tests/test_task019_scalar_alpha_jet_bundle.py`
- `Build_Docs/Architecture/layer_manifest.json`
- `Build_Docs/Architecture/LAYER_MANIFEST.md`
- `Build_Docs/Architecture/STATUS_CALCULUS.md`
- `Build_Docs/Reports/task019_summary.md`

## Manifest And Status Updates

- Added `ScalarAlphaJetBundleStatus` to the primitive status families and `StatusCode`.
- Added `ScalarAlphaJetBundleObservation` and `ScalarAlphaJetBundleResult`.
- Added `SCALAR_ALPHA_JET_BUNDLE_PROTOCOL`, `SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL`, and `SCALAR_ALPHA_JET_BUNDLE_SPACE`.
- Registered `scalar_alpha_jet_bundle` as an operation and calibrated primitive operation.
- Updated primitive `__all__` and both layer manifests.
- Updated `STATUS_CALCULUS.md` with the nine strata and the explicit AlphaProbeStatus to ScalarAlphaJetBundleStatus mapping.

## Sample Serialized Regular Result

```json
{
  "status": "scalar_jet_regular_integer_alpha",
  "space": "ScalarAlphaJetBundleObservation",
  "value": {
    "point": 0.0,
    "f_value": 0.0,
    "probe_id": "report_regular",
    "function_label": "square",
    "observed_alpha": 1.9999999999967675,
    "alpha_status": "alpha_regular_integer",
    "derivative_at_point": 0.0020000009999776016,
    "derivative_h": 0.001,
    "alpha_probe_trace_id": "9d7ae3225fa012ca",
    "slope_trace_id": "ff49e451e489345b",
    "transfer_trace_ids": [
      "6873f1fad20342cd",
      "c865b9f72f42c19e",
      "962ea59896d4da6f",
      "b777296f8802e796"
    ]
  },
  "provenance": {
    "operation_id": "scalar_alpha_jet_bundle",
    "parents": ["9d7ae3225fa012ca"],
    "trace_id": "5b59f225a273ebb3"
  }
}
```

## Sample Serialized Cancellation Result

```json
{
  "status": "scalar_jet_alpha_cancellation_dominated",
  "space": "ScalarAlphaJetBundleObservation",
  "value": {
    "point": 1.0,
    "f_value": 1.0,
    "probe_id": "report_cancel",
    "function_label": "identity",
    "observed_alpha": null,
    "alpha_status": "alpha_cancellation_dominated",
    "derivative_at_point": null,
    "derivative_h": null,
    "alpha_probe_trace_id": "70a9a99da6bd7e8f",
    "slope_trace_id": null,
    "transfer_trace_ids": [
      "fd120fac5ed1be20",
      "19aac06608072bcc",
      "9a7cb67eaf340709"
    ]
  },
  "provenance": {
    "operation_id": "scalar_alpha_jet_bundle",
    "parents": ["70a9a99da6bd7e8f"],
    "trace_id": "ae459b21e12ec2ca"
  }
}
```

## Strata Demonstrated

| Example | JetBundle status | Embedded AlphaProbe status | Observed alpha |
|---|---|---|---|
| `x^2` at `x0=0` | `scalar_jet_regular_integer_alpha` | `alpha_regular_integer` | `2.000000000001573` |
| `sqrt(x)` at `x0=0` | `scalar_jet_fractional_alpha_branch` | `alpha_fractional_branch` | `0.499999999979292` |
| identity with broad negative declared model | `scalar_jet_negative_alpha_singularity` | `alpha_negative_singularity` | `0.9999999999969099` |
| `x^2` with excluded declared model | `scalar_jet_alpha_model_refused` | `alpha_model_no_match` | `2.000000000001573` |
| identity with `eta=1e-18` | `scalar_jet_alpha_cancellation_dominated` | `alpha_cancellation_dominated` | `null` |
| repeated h-grid | `scalar_jet_alpha_indeterminate` | `alpha_indeterminate` | `null` |
| f(x0) raises | `scalar_jet_domain_refused` | `null` | `null` |
| f(x0) is `inf` | `scalar_jet_nonfinite` | `null` | `null` |

`scalar_jet_protocol_refused` is reserved. No legal v1 input path emits it.

## Negative Alpha Limit

A genuine negative local alpha is structurally hard to realize through `g_local(h) = f(x0+h) - f(x0)` when `f(x0)` is finite, because the local probe tends to zero as `h -> 0`. The negative stratum is preserved by explicit AlphaProbe mapping and is demonstrable through a declared negative alpha model, but direct finite-point blow-up should use `directional_alpha_probe` rather than `ScalarAlphaJetBundle`.

## Alpha Minus One Validation Through JetBundle

| α | observed_alpha | JetBundle status | derivative_at_point | derivative_h |
|---|---:|---|---:|---:|
| 0.5 | `0.49999999997887246` | `scalar_jet_fractional_alpha_branch` | `499.9998750535722` | `1e-06` |
| 1.5 | `1.4999999999884281` | `scalar_jet_fractional_alpha_branch` | `0.0015000003751909745` | `1e-06` |
| 2.0 | `2.000000000001573` | `scalar_jet_regular_integer_alpha` | `2.000000999991276e-06` | `1e-06` |
| 3.0 | `2.9999999999928093` | `scalar_jet_regular_integer_alpha` | `3.000003000097248e-12` | `1e-06` |

## Trace And Lineage

- Distinct `x0` values produce distinct embedded AlphaProbe trace IDs: `38c803277467fcd2` vs `bfab5d6819716d88`.
- JetBundle parents are exactly `(alpha_probe_trace_id,)`; example: `('d2da9cdefcb5dede',)`.
- The embedded AlphaProbe carries the transfer trace IDs and slope trace ID, so lineage walks transitively to the transfer observations and slope observation.
- The derivative transfer is not duplicated in JetBundle parents. It is reachable through AlphaProbe's parents.
- Independent derivative check matched: JetBundle derivative trace `6e626950e4a4a8dd` equals an independent `typed_finite_difference` trace for the same `(g_local, h, eta*h, function_label)`.

## Audits

- Focused Task 019 tests: `25 passed`.
- Manifest/export/lineage audits: `7 passed`.
- Source-purity tests: `3 passed`.
- Full suite: `344 passed in 3.59s`.
- Legacy source grep returned no matches for `lloyd_v3`, `safe_mask`, legacy projection mode, `legacy_compat`, `clamp_min`, `epsilon`, or `eps`.
- The targeted precision-floor grep returned only intentional/documented matches in `typed_finite_difference.py`, tests, task specs, architecture docs, and reports. No new metrology estimator, protocol, b_k noise floor, K_q calibration, or branch-fingerprint machinery was introduced.

## Limits

- No default h-grid.
- No parser.
- No multidimensional probing.
- No Hessian, rank, signature, shape operator, curvature decomposition, or local quadratic model.
- No Newton/Halley/candidate-step logic.
- No branch fingerprint, refinery, history, solver, or metrology dependency.
- No constant-detection stratum.
- No multi-precision execution.
- No nested-window drift or BIC.
