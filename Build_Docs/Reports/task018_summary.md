# Task 018 Summary -- Directional AlphaProbe

## Scope

Added the Layer 1 calibrated primitive `directional_alpha_probe`. It samples a scalar callable along an explicit positive approach grid, composes `typed_finite_difference` and `typed_log_log_slope`, and emits typed directional alpha evidence.

## Tests

- Added `tests/test_task018_directional_alpha_probe.py`
- Added one targeted finite-precision observability audit in `tests/test_task001_source_purity.py`
- New test count: 23
- Full suite after Task 018: 319 passing tests

Commands run:

```bash
PYTHONPATH=src python -c "from lloyd_v4.primitives import directional_alpha_probe" 2>&1
python -m pytest tests/test_task018_directional_alpha_probe.py tests/test_task001_source_purity.py -q
python -m pytest -x tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py
python -m pytest -x tests/
rg "precision_floor|roundoff_floor|unit_roundoff|machine_epsilon|cancellation_ratio|2\.0\s*\*\*\s*-52|sys\.float_info\.epsilon|np\.finfo" src tests Build_Docs -n
```

Pre-task import evidence with `PYTHONPATH=src`: `ImportError: cannot import name 'directional_alpha_probe'`.

## Files changed

- `src/lloyd_v4/core/status.py`
- `src/lloyd_v4/primitives/directional_alpha_probe.py`
- `src/lloyd_v4/primitives/__init__.py`
- `src/lloyd_v4/projection/exact_projection.py`
- `tests/test_task018_directional_alpha_probe.py`
- `tests/test_task001_source_purity.py`
- `Build_Docs/Architecture/layer_manifest.json`
- `Build_Docs/Architecture/LAYER_MANIFEST.md`
- `Build_Docs/Architecture/STATUS_CALCULUS.md`
- `Build_Docs/Architecture/METROLOGY_PRINCIPLES.md`
- `Build_Docs/Reports/task018_summary.md`

## Manifest

The JSON and Markdown manifests declare:

- `AlphaProbeStatus`
- `DeclaredAlphaModel`
- `AlphaProbeObservation`
- `AlphaProbeResult`
- `DIRECTIONAL_ALPHA_PROBE_PROTOCOL`
- `ALPHA_PROBE_CONSUMER_PROTOCOL`
- `ALPHA_PROBE_SPACE`
- `directional_alpha_probe` as an operation and calibrated primitive operation

## Sample serialized outputs

Regular integer example, `g(f)=f^2`, `declared_alpha_band=0.01`:

```json
{
  "space": "AlphaProbeObservation",
  "status": "alpha_regular_integer",
  "value": {
    "probe_id": "quadratic_probe",
    "function_label": "square",
    "observed_slope": 1.000000000001573,
    "observed_alpha": 2.000000000001573,
    "r_squared": 1.0,
    "standard_error": 4.632963793521488e-12,
    "n_observed": 6,
    "slope_trace_id": "29466494d48e2f5b"
  },
  "provenance": {
    "operation_id": "directional_alpha_probe",
    "expression_path": "log_log_slope_fit",
    "inputs": ["quadratic_probe", "square", [1e-06, 1e-05, 0.0001, 0.001, 0.01, 0.1], 1e-06],
    "trace_id": "609e795ac085f0a1"
  }
}
```

Fractional branch example, `g(f)=sqrt(f)`, `declared_alpha_band=0.01`:

```json
{
  "space": "AlphaProbeObservation",
  "status": "alpha_fractional_branch",
  "value": {
    "probe_id": "sqrt_probe",
    "function_label": "sqrt",
    "observed_slope": -0.500000000020708,
    "observed_alpha": 0.499999999979292,
    "r_squared": 1.0,
    "standard_error": 5.2657553452307445e-12,
    "n_observed": 5,
    "slope_trace_id": "4a8f6ac9bb8531a5"
  },
  "provenance": {
    "operation_id": "directional_alpha_probe",
    "expression_path": "log_log_slope_fit",
    "inputs": ["sqrt_probe", "sqrt", [1e-06, 1e-05, 0.0001, 0.001, 0.01], 1e-06],
    "trace_id": "78a5a452d7f70e95"
  }
}
```

## Strata demonstrated

- `alpha_regular_integer`: `g(f)=f^2`, observed alpha `2.000000000001573`
- `alpha_fractional_branch`: `g(f)=sqrt(f)`, observed alpha `0.499999999979292`
- `alpha_negative_singularity`: `g(f)=1/f`, observed alpha `-0.9999999999795721`
- `alpha_model_ambiguous`: overlapping declared models for observed alpha near `2`
- `alpha_model_no_match`: declared model set excludes observed alpha near `2`
- `alpha_cancellation_dominated`: near-constant callable `1.0 + 1e-20*f`
- `alpha_insufficient_data`: two-point grid
- `alpha_domain_refused`: callable raises at every sample
- `alpha_nonfinite`: callable returns `inf`
- `alpha_indeterminate`: repeated identical `f` grid

## Alpha-minus-one validation

| alpha | observed alpha | R2 | status |
|---:|---:|---:|---|
| 0.5 | 0.49999999997887246 | 1.0 | `alpha_fractional_branch` |
| 1.5 | 1.4999999999884281 | 1.0 | `alpha_fractional_branch` |
| 2.0 | 2.000000000001573 | 1.0 | `alpha_regular_integer` |
| 3.0 | 2.9999999999928093 | 1.0 | `alpha_regular_integer` |

## Trace and lineage

- Distinct probe ids: `04bedfb8c2fff466` vs `1995bf9823789c1d`, distinct true.
- Identical inputs: `04bedfb8c2fff466` vs `04bedfb8c2fff466`, identical true.
- Parent trace ids include every transfer trace and the slope trace when the slope fit is computed.
- `transfer_trace_ids` match independently computed transfer observations for the same `(function_label, f, eta*f)` inputs.

## Cleanup confirmations

- Projection transition authority comment added above `QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE`.
- Test confirms runtime `transition()` callable overrides static default mapping for branch-contextual refusal.
- `METROLOGY_PRINCIPLES.md` documents `precision_floor` as status-only finite-precision observability evidence.
- Targeted floor audit pattern added to source-purity tests. Source-side matches are confined to `typed_finite_difference.py` and are allowed as declared observability evidence.

## Limits

AlphaProbe still does not provide:

- nested-window drift analysis
- multi-precision execution
- multidimensional direction probing
- JetBundle composition
- solver admission or tie-refusal logic

Those are forward tasks. Task 018 only makes alpha typed, traceable, and dispatchable.
