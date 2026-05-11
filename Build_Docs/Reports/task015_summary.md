# Task 015 Summary -- typed_finite_difference

## Scope

Added the first Layer 1 capability primitive, `typed_finite_difference`, for observing a callable's local forward-difference transfer.

## Tests

- Added `tests/test_task015_typed_finite_difference.py`
- New test count: 25
- Full suite after Task 015: 272 passing tests

Commands run:

```bash
PYTHONPATH=src python -c "from lloyd_v4.primitives import typed_finite_difference" 2>&1
python -m pytest tests/test_task015_typed_finite_difference.py -q
python -m pytest -x tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py
python -m pytest -x tests/
```

Pre-task import evidence with `PYTHONPATH=src`: `ImportError: cannot import name 'typed_finite_difference'`.

## Files changed

- `src/lloyd_v4/core/status.py`
- `src/lloyd_v4/primitives/typed_finite_difference.py`
- `src/lloyd_v4/primitives/__init__.py`
- `tests/test_task015_typed_finite_difference.py`
- `Build_Docs/Architecture/layer_manifest.json`
- `Build_Docs/Architecture/LAYER_MANIFEST.md`
- `Build_Docs/Architecture/STATUS_CALCULUS.md`
- `Build_Docs/Reports/task015_summary.md`

## Manifest

The JSON manifest and Markdown manifest both declare:

- `TransferStatus`
- `TransferObservation`
- `TransferObservationResult`
- `TYPED_FINITE_DIFFERENCE_PROTOCOL`
- `TRANSFER_OBSERVATION_CONSUMER_PROTOCOL`
- `TRANSFER_SPACE`
- `typed_finite_difference` as an operation and calibrated primitive operation

Manifest/export audits passed.

## Serialized sample

`typed_finite_difference(lambda x: x*x, 1.0, 0.001, function_label="square")`:

```json
{
  "space": "TransferObservation",
  "status": "transfer_observed",
  "value": {
    "transfer": 2.0009999999996975,
    "g_at_f": 1.0,
    "g_at_f_plus_delta": 1.0020009999999997,
    "delta_g": 0.0020009999999996975,
    "cancellation_ratio": 0.001997003995005692
  },
  "provenance": {
    "operation_id": "typed_finite_difference",
    "expression_path": "forward_difference",
    "precision": "raw_python",
    "backend": "python",
    "device": "cpu",
    "inputs": [1.0, 0.001, "square"],
    "parents": [],
    "trace_id": "430aa4d40dcccc52",
    "status": "complete"
  },
  "protocol": "ok"
}
```

## Strata demonstrated

- `transfer_observed`: `lambda x: x`, `f=1.0`, `delta_f=0.01`
- `transfer_cancellation_dominated`: `lambda x: 1.0 + 1e-20*x`, `f=1.0`, `delta_f=0.01`
- `transfer_non_finite`: `lambda x: float("inf")`, `f=1.0`, `delta_f=0.01`
- `transfer_domain_refused`: `lambda x: "bad"`, `f=1.0`, `delta_f=0.01`
- `transfer_delta_indeterminate`: `lambda x: x`, `f=1.0`, `delta_f=0.0`

All five serialize through `json.dumps(..., allow_nan=False)` without naked NaN or Infinity.

## Trace identity

Trace identity uses `Provenance.inputs=(f, delta_f, function_label)`.

Sanity check:

- `function_label="square"` trace id: `942dbd531d2a8c77`
- `function_label="linear"` trace id: `b28d67253348bba0`
- Distinct: true

## Limits

`typed_finite_difference` does not yet provide:

- multi-precision execution
- central differences
- slope fitting or window drift
- PPS-style amplitude/path separation
- alternative expression-path execution

Those are forward tasks. This task only adds the typed primitive observation surface.
