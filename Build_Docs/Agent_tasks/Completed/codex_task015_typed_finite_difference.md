# Task 015 — First Capability Primitive: typed_finite_difference

## Repository

`/mnt/fast/Lloyd_Engine_V4`

V3 is reference-only (Axiom 10). V1 / OG engine are also reference-only.
Layer 2+ artifacts (metrology, branch, refinery, history, solver) are V3-shaped
deferred-consumer first-drafts and MUST NOT shape this task. Do not cite them
as evidence; do not coordinate fixes with them; do not import from them. This
task is at Layer 1 (primitives) and depends only on Layer 0 (core).

## Current Verified Baseline

- 247 tests passing (`pytest -x tests/`) as of Task 011 completion
- Layers: core, primitives, projection, plus deferred-consumer Layers 2/3
- Calibrated primitive operations: `typed_collection`, `typed_value`,
  `projective_ratio`, `stratified_quadratic_roots` (4 total)
- Internal operations: `projective_ratio.scalarize`,
  `stratified_quadratic_roots.select`
- Projection layer: `branch_selection`, `exact_quadratic_projection` (rebuilt
  V4-native per Task 010)
- Provenance carries content-addressed identity via `inputs` field (Task 011)

## Task Goal

Add the first capability primitive at Layer 1: `typed_finite_difference`.
This primitive observes the local transfer of a callable function `g(f)` at a
point `f` under perturbation `δf`. It produces a typed observation of
`T(f) = (g(f+δf) - g(f)) / δf` with stratum classification, observation-honest
validity, and conditioning notes capturing cancellation magnitude.

This is the smallest geometric measurement primitive needed to begin the
precision/path separation (PPS) experiment that V4 was built to support. It
exposes a measurement-level surface (observe a function's local slope as a
typed result) without exposing arithmetic-level surface (no `typed_addition`,
`typed_subtraction`, etc., which would drag V4 back to floating-point-shaped
typing — Axiom 1 forbids treating arithmetic as the substrate's primary verb).

## Design Principles

- **Geometric measurement, not arithmetic wrapper.** The primitive observes a
  geometric feature of `g` (its local slope at `f`). The arithmetic
  (`+`, `-`, `/`) happens internally and is never exposed as a V4 operation.
  This matches `projective_ratio`, which uses `==0` checks internally without
  exposing `typed_equality_check`.

- **Strata are geometric in nature.** Each stratum corresponds to a meaningful
  observational state: clean transfer observed, cancellation-dominated
  observation, non-finite intermediate value, function refused to evaluate, or
  perturbation was zero. These are not floating-point pathologies relabelled
  with stickers; they are distinct geometric measurement outcomes.

- **Observation-honest validity (Axiom 4).** `validity.finite` reflects whether
  the observed transfer scalar is finite, not what the input stratum was. This
  resolves the validity-semantics question (object-validity vs
  observation-validity) at this primitive: validity describes the *transfer
  observation* this layer produced.

- **Cancellation as a typed observation, not a hidden floor (Axiom 3).** The
  precision floor used to declare CANCELLATION_DOMINATED is the unit roundoff
  for the declared precision, which is a metrology property, not a hidden
  rescue tolerance.

- **Function identity is part of the observation path (Axiom 5).** A required
  `function_label` parameter names the function being measured. This enters
  `Provenance.inputs` so two measurements of different functions at the same
  `(f, δf, precision)` produce distinct trace_ids.

## Primitive-Sufficiency Gate

Per Axiom 12, every concept this task uses must already exist in a parent
layer. Verifying:

| Concept used | Provided by | Location |
|---|---|---|
| `TypedResult` | core | `core/result.py` |
| `Validity` | core | `core/validity.py` |
| `Conditioning` | core | `core/conditioning.py` |
| `Provenance` (with `inputs`) | core (Task 011) | `core/provenance.py` |
| `ProducerProtocol`, `ConsumerProtocol`, `validate_protocol` | core | `core/protocols.py` |
| `ProtocolStatus`, `ConditioningStatus`, `ProvenanceStatus` | core | `core/status.py` |
| `StatusTransitionRule` | core | `core/transitions.py` |
| `to_json_safe` | core | `core/serialization.py` |
| `ProtocolViolationError` | core | `core/errors.py` |
| Pattern: primitive that classifies inputs into strata | primitives | `projective_ratio.py`, `stratified_quadratic_roots.py` |
| Pattern: primitive that takes a callable / opaque object | (NEW — first such primitive) | n/a |

The new pattern (primitive accepting a callable) does not require new core
machinery. The callable is treated as a raw input that is *not* canonicalized
into the trace_id payload (cannot be serialized stably across runs); function
identity is carried by the `function_label` string parameter, which IS in
`inputs`. This matches the Task 011 design decision that opaque inputs use a
stable string identifier rather than `repr`-with-address.

The new status family (`TransferStatus`) is defined in `core/status.py` for
co-location with other enum definitions but declared as belonging to the
primitives layer in the layer manifest, matching the existing pattern for
`ProjectiveRatioStatus`, `QuadraticRootStatus`, `ValueStatus`,
`CollectionStatus` (all defined in `core/status.py`, declared at primitives
layer in `layer_manifest.json`).

Sufficiency gate **passes**. No prior parent-extension task required.

## Required Deliverables

### 1. New status family in `src/lloyd_v4/core/status.py`

```python
class TransferStatus(StrEnum):
    TRANSFER_OBSERVED = "transfer_observed"
    TRANSFER_CANCELLATION_DOMINATED = "transfer_cancellation_dominated"
    TRANSFER_NON_FINITE = "transfer_non_finite"
    TRANSFER_DOMAIN_REFUSED = "transfer_domain_refused"
    TRANSFER_DELTA_INDETERMINATE = "transfer_delta_indeterminate"
```

Add `TransferStatus` to the `StatusCode` union at the bottom of `status.py`.

Stratum semantics:

- **TRANSFER_OBSERVED**: `δf ≠ 0`, both `g(f)` and `g(f+δf)` finite, the
  transfer `T = (g(f+δf) - g(f))/δf` is finite, and the cancellation ratio
  `|Δg| / max(|g(f)|, |g(f+δf)|)` is at or above the precision floor (or
  both endpoints are exactly zero). The observation is clean.

- **TRANSFER_CANCELLATION_DOMINATED**: `δf ≠ 0`, both endpoints finite, but
  `|Δg| / max(|g(f)|, |g(f+δf)|) < precision_floor` AND `max(|g(f)|, |g(f+δf)|) > 0`.
  The substrate cannot distinguish "function is locally constant" from "the
  difference is below precision floor" at this `(f, δf, precision)` cell.

- **TRANSFER_NON_FINITE**: `δf ≠ 0`, but `g(f)`, `g(f+δf)`, or the computed
  transfer `T` is non-finite (`±inf` or `NaN`). Note: NaN from `g` is
  classified here, not in DOMAIN_REFUSED — `g` returned a value, the value
  just isn't a real finite number.

- **TRANSFER_DOMAIN_REFUSED**: `g(f)` or `g(f+δf)` raised an exception or
  returned a non-numeric value (not int/float). The function refused to
  produce a value at one of the sample points.

- **TRANSFER_DELTA_INDETERMINATE**: `δf == 0`. No perturbation, no observation
  possible. Mathematically `0/0`. (Note: `δf` is required to be finite by
  input validation; this stratum handles only the `δf == 0` case.)

### 2. New module `src/lloyd_v4/primitives/typed_finite_difference.py`

#### Module-level constants

```python
TRANSFER_SPACE = "TransferObservation"

TYPED_FINITE_DIFFERENCE_PROTOCOL = ProducerProtocol(
    name="typed_finite_difference",
    emitted_statuses=frozenset({
        TransferStatus.TRANSFER_OBSERVED,
        TransferStatus.TRANSFER_CANCELLATION_DOMINATED,
        TransferStatus.TRANSFER_NON_FINITE,
        TransferStatus.TRANSFER_DOMAIN_REFUSED,
        TransferStatus.TRANSFER_DELTA_INDETERMINATE,
    }),
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
)

TRANSFER_OBSERVATION_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="transfer_observation_consumer",
    accepted_statuses=frozenset({TransferStatus.TRANSFER_OBSERVED}),
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
    refused_statuses=frozenset({
        TransferStatus.TRANSFER_CANCELLATION_DOMINATED,
        TransferStatus.TRANSFER_NON_FINITE,
        TransferStatus.TRANSFER_DOMAIN_REFUSED,
        TransferStatus.TRANSFER_DELTA_INDETERMINATE,
    }),
)
```

A consumer that wants to use the transfer observation as a clean slope sample
declares `TRANSFER_OBSERVATION_CONSUMER_PROTOCOL`. Other strata are explicit
refusals.

#### Value type

```python
@dataclass(frozen=True, slots=True)
class TransferObservation:
    transfer: float | None       # T = Δg/δf, None if not observable
    g_at_f: float | None         # g(f), if it was computed
    g_at_f_plus_delta: float | None  # g(f+δf), if it was computed
    delta_g: float | None        # g(f+δf) - g(f), if both were computed
    cancellation_ratio: float | None  # |Δg|/max(|g_f|, |g_f_plus|), if defined

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe
        return {
            "transfer": to_json_safe(self.transfer),
            "g_at_f": to_json_safe(self.g_at_f),
            "g_at_f_plus_delta": to_json_safe(self.g_at_f_plus_delta),
            "delta_g": to_json_safe(self.delta_g),
            "cancellation_ratio": to_json_safe(self.cancellation_ratio),
        }


TransferObservationResult = TypedResult[TransferObservation, TransferStatus]
```

The value carries the full observation including diagnostics. Consumers can
read `.transfer` for slope-fitting; auditors can read `.cancellation_ratio`
or the endpoints for diagnosis.

#### Public function

```python
def typed_finite_difference(
    g_callable: Callable[[float], float],
    f: float,
    delta_f: float,
    *,
    function_label: str,
    precision: str = "raw_python",
    backend: str = "python",
    device: str = "cpu",
    measurement_resolution: Any | None = None,
    expression_path: str = "forward_difference",
) -> TransferObservationResult:
    """Observe the local transfer T(f) = (g(f+δf) - g(f))/δf as a typed result.

    Inputs:
        g_callable: function f -> y. May raise; may return NaN/inf; may return
                    non-numeric (caught and classified into refusal strata).
        f: base point (must be finite).
        delta_f: perturbation (must be finite; may be 0, classified as
                 TRANSFER_DELTA_INDETERMINATE).
        function_label: required string naming the function being measured.
                        Enters Provenance.inputs so distinct functions
                        produce distinct trace_ids.
        precision, backend, device, measurement_resolution, expression_path:
                        path metadata. precision="raw_python" is the only
                        currently-supported value; future tasks may add
                        numpy/mpmath backends.

    Returns:
        TypedResult[TransferObservation, TransferStatus] classified into one
        of five strata. Always returns; never raises except for input-level
        ProtocolViolationError (non-finite f or delta_f, non-callable g, or
        empty function_label).
    """
```

#### Input validation

Raise `ProtocolViolationError` BEFORE any TypedResult construction for:

- `f` is not int/float, or is non-finite (NaN/inf).
- `delta_f` is not int/float, or is non-finite (NaN/inf).
- `g_callable` is not callable.
- `function_label` is not a non-empty string.

Note: `delta_f == 0` is NOT a hard refusal; it is a typed observation with
status TRANSFER_DELTA_INDETERMINATE.

#### Algorithm

```
1. Validate inputs (raise on bad inputs as above).

2. If delta_f == 0:
   return TypedResult with:
     status = TRANSFER_DELTA_INDETERMINATE
     value = TransferObservation(transfer=None, g_at_f=None,
                                  g_at_f_plus_delta=None,
                                  delta_g=None, cancellation_ratio=None)
     validity = Validity(defined=False, finite=False, selectable=False,
                         advanceable=False, observable=True)
     conditioning = Conditioning(WARNING, notes=("delta_f_is_zero",))

3. Try to evaluate g(f) and g(f + delta_f), catching any exception as
   TRANSFER_DOMAIN_REFUSED:
   try:
       g_f = g_callable(f)
       g_f_plus = g_callable(f + delta_f)
   except Exception as exc:
       return TypedResult with TRANSFER_DOMAIN_REFUSED status, TransferObservation
       fields populated with whatever was computed before the exception (g_at_f
       may be set if g(f) succeeded but g(f+δf) failed; otherwise None).
       conditioning notes include the exception type as a string.

4. If either return value is not int/float (covers None, str, complex, etc.):
   return TRANSFER_DOMAIN_REFUSED with conditioning notes describing the type
   issue.

5. If g_f or g_f_plus is non-finite (NaN or ±inf):
   return TRANSFER_NON_FINITE with TransferObservation populated. transfer
   field is computed if possible (delta_g / delta_f); if intermediate is
   non-finite, transfer is also non-finite. cancellation_ratio is set if both
   endpoints are finite, else None.

6. Compute delta_g = g_f_plus - g_f, transfer = delta_g / delta_f.
   If transfer is non-finite (overflow during division):
     return TRANSFER_NON_FINITE.

7. Compute max_g = max(abs(g_f), abs(g_f_plus)).
   If max_g == 0:
     # Both endpoints are exactly zero. Observation is unambiguous.
     return TRANSFER_OBSERVED with transfer = 0.0,
     cancellation_ratio = None (undefined when max_g == 0).

8. Compute cancellation_ratio = abs(delta_g) / max_g.
   Compute precision_floor = _precision_floor(precision)
     (sys.float_info.epsilon for "raw_python", future precisions add their own).
   If cancellation_ratio < precision_floor:
     return TRANSFER_CANCELLATION_DOMINATED with TransferObservation populated.
     Note: the transfer field IS populated (it's a valid float, just untrustworthy);
     downstream consumers see validity.selectable = False and refuse it
     accordingly.

9. Otherwise:
   return TRANSFER_OBSERVED with full TransferObservation.
```

#### Validity per stratum

| Stratum | defined | finite | selectable | advanceable | observable |
|---|---|---|---|---|---|
| TRANSFER_OBSERVED | True | True | True | True | True |
| TRANSFER_CANCELLATION_DOMINATED | True | True | False | False | True |
| TRANSFER_NON_FINITE | True | False | False | False | True |
| TRANSFER_DOMAIN_REFUSED | False | False | False | False | True |
| TRANSFER_DELTA_INDETERMINATE | False | False | False | False | True |

Note for CANCELLATION_DOMINATED: `finite=True` because the float value IS
finite; `selectable=False` because the value is dominated by rounding noise
and cannot be trusted as a slope estimate. This is exactly the multi-field
validity Axiom 4 mandates: "finite but not selectable" is a representable
state.

#### Conditioning per stratum

- **TRANSFER_OBSERVED**: `Conditioning(WELL_CONDITIONED)`. Notes may include
  `f"cancellation_ratio={ratio:.3e}"` if useful, but the status is the
  primary signal.
- **TRANSFER_CANCELLATION_DOMINATED**: `Conditioning(WARNING, notes=(f"cancellation_ratio={ratio:.3e}", f"precision_floor={floor:.3e}"))`.
- **TRANSFER_NON_FINITE**: `Conditioning(WARNING, notes=(f"non_finite_endpoint:{which}",))`
  where `which` indicates `g_at_f`, `g_at_f_plus_delta`, or `transfer`.
- **TRANSFER_DOMAIN_REFUSED**: `Conditioning(WARNING, notes=(f"exception:{type_name}",))`
  or `(f"non_numeric_return:{type_name}",)`.
- **TRANSFER_DELTA_INDETERMINATE**: `Conditioning(WARNING, notes=("delta_f_is_zero",))`.

(Conditioning is left as `WARNING` for all non-OBSERVED strata. Task 013 may
later refine conditioning into a continuous-or-stratified observation; this
task does not preempt that work.)

#### Provenance

```python
provenance=Provenance(
    operation_id="typed_finite_difference",
    expression_path=expression_path,  # default "forward_difference"
    precision=precision,
    backend=backend,
    device=device,
    measurement_resolution=measurement_resolution,
    inputs=(f, delta_f, function_label),
    parents=(),
)
```

`g_callable` is NOT in `inputs` (cannot be canonicalized stably across runs).
`function_label` is the identity-of-function carrier and IS in `inputs`.

#### Precision floor helper

```python
import sys

def _precision_floor(precision: str) -> float:
    """Unit roundoff for the declared precision."""
    if precision == "raw_python":
        return sys.float_info.epsilon  # ≈ 2.22e-16
    raise ProtocolViolationError(
        f"unsupported precision {precision!r}; "
        f"raw_python is the only currently-supported value"
    )
```

This makes the precision-to-floor mapping explicit and extensible. Future
tasks adding numpy/mpmath backends extend this dispatch.

### 3. Update `src/lloyd_v4/primitives/__init__.py`

Add the new exports:

```python
from .typed_finite_difference import (
    TYPED_FINITE_DIFFERENCE_PROTOCOL,
    TRANSFER_OBSERVATION_CONSUMER_PROTOCOL,
    TRANSFER_SPACE,
    TransferObservation,
    TransferObservationResult,
    typed_finite_difference,
)
```

And add them to `__all__`.

### 4. Update `Build_Docs/Architecture/layer_manifest.json`

In the `primitives` layer entry:

- Add `"TransferStatus"` to `status_families`
- Add `"TransferObservation"`, `"TransferObservationResult"` to `value_types`
- Add `"TYPED_FINITE_DIFFERENCE_PROTOCOL"`, `"TRANSFER_OBSERVATION_CONSUMER_PROTOCOL"` to `protocol_types`
- Add `"TRANSFER_SPACE"` to `errors_and_utilities`
- Add `"typed_finite_difference"` to `operations` and `calibrated_primitive_operations`
- Add all the above to `all_exports` (alphabetically)

### 5. Update `Build_Docs/Architecture/LAYER_MANIFEST.md`

Mirror the JSON changes in the human-readable manifest under the `primitives` section.

### 6. New test file `tests/test_task015_typed_finite_difference.py`

See Required Tests section below.

### 7. Optional: Update `Build_Docs/Architecture/STATUS_CALCULUS.md`

If this doc enumerates status families and their semantics, append a section
on `TransferStatus`. If it doesn't, skip.

## Required Tests

New file: `tests/test_task015_typed_finite_difference.py`. The test file must
verify, at minimum:

### Pre-task evidence: V4 currently cannot observe a function's local slope

```python
def test_typed_finite_difference_does_not_yet_exist() -> None:
    """Pre-task evidence: importing the primitive fails before this task."""
    # Should be deleted from this file once the task is in progress.
    # Documents that the gap was real before the task began.
    pass  # placeholder; remove during implementation
```

### Stratum coverage tests (one per stratum)

```python
def test_observed_stratum_clean_linear_function():
    """g(f) = 2f, T(f) = 2 exactly."""
    g = lambda x: 2.0 * x
    result = typed_finite_difference(g, 1.0, 0.01, function_label="linear_2x")
    assert result.status is TransferStatus.TRANSFER_OBSERVED
    assert result.value.transfer == 2.0
    assert result.validity.finite is True
    assert result.validity.selectable is True
    assert result.conditioning.status is ConditioningStatus.WELL_CONDITIONED


def test_observed_stratum_quadratic():
    """g(f) = f^2, T(1.0, 0.001) ≈ 2.001."""
    g = lambda x: x * x
    result = typed_finite_difference(g, 1.0, 0.001, function_label="square")
    assert result.status is TransferStatus.TRANSFER_OBSERVED
    assert abs(result.value.transfer - 2.001) < 1e-12


def test_observed_stratum_both_endpoints_zero():
    """g(f) = 0 everywhere; transfer is exactly 0."""
    g = lambda x: 0.0
    result = typed_finite_difference(g, 1.0, 0.01, function_label="zero")
    assert result.status is TransferStatus.TRANSFER_OBSERVED
    assert result.value.transfer == 0.0
    assert result.value.cancellation_ratio is None  # undefined when max_g == 0


def test_cancellation_dominated_stratum():
    """Function whose finite difference is below precision floor."""
    # g(f) = 1.0 + tiny perturbation that rounds away in float64
    g = lambda x: 1.0 + 1e-20 * x  # the 1e-20 perturbation is below epsilon for 1.0
    result = typed_finite_difference(g, 1.0, 0.01, function_label="cancel")
    assert result.status is TransferStatus.TRANSFER_CANCELLATION_DOMINATED
    assert result.validity.finite is True   # transfer IS finite
    assert result.validity.selectable is False  # but not trustworthy
    assert "cancellation_ratio" in str(result.conditioning.notes[0]) or \
           result.conditioning.notes  # notes carry quantitative detail


def test_non_finite_stratum_overflow():
    """g(f) overflows at f+δf."""
    g = lambda x: x * 1e308 if x < 2 else float("inf")
    result = typed_finite_difference(g, 1.5, 1.0, function_label="overflow_at_2")
    assert result.status is TransferStatus.TRANSFER_NON_FINITE
    assert result.validity.finite is False


def test_non_finite_stratum_nan():
    """g returns NaN."""
    import math
    g = lambda x: math.nan
    result = typed_finite_difference(g, 1.0, 0.01, function_label="nan_function")
    assert result.status is TransferStatus.TRANSFER_NON_FINITE


def test_domain_refused_stratum_exception():
    """g raises an exception."""
    def g(x):
        raise ValueError("not defined here")
    result = typed_finite_difference(g, 1.0, 0.01, function_label="raises")
    assert result.status is TransferStatus.TRANSFER_DOMAIN_REFUSED
    assert result.validity.defined is False


def test_domain_refused_stratum_non_numeric():
    """g returns a non-numeric value."""
    g = lambda x: "not a number"
    result = typed_finite_difference(g, 1.0, 0.01, function_label="returns_string")
    assert result.status is TransferStatus.TRANSFER_DOMAIN_REFUSED


def test_delta_indeterminate_stratum():
    """delta_f == 0 produces TRANSFER_DELTA_INDETERMINATE."""
    g = lambda x: x * x
    result = typed_finite_difference(g, 1.0, 0.0, function_label="delta_zero")
    assert result.status is TransferStatus.TRANSFER_DELTA_INDETERMINATE
    assert result.value.transfer is None
    assert result.validity.defined is False
```

### Input validation tests

```python
def test_non_finite_f_raises():
    g = lambda x: x
    with pytest.raises(ProtocolViolationError):
        typed_finite_difference(g, float("inf"), 0.01, function_label="x")


def test_nan_delta_f_raises():
    import math
    g = lambda x: x
    with pytest.raises(ProtocolViolationError):
        typed_finite_difference(g, 1.0, math.nan, function_label="x")


def test_non_callable_raises():
    with pytest.raises(ProtocolViolationError):
        typed_finite_difference(42, 1.0, 0.01, function_label="x")


def test_empty_function_label_raises():
    g = lambda x: x
    with pytest.raises(ProtocolViolationError):
        typed_finite_difference(g, 1.0, 0.01, function_label="")
```

### Provenance and identity tests

```python
def test_inputs_field_carries_f_delta_label():
    g = lambda x: x
    result = typed_finite_difference(g, 1.0, 0.01, function_label="identity")
    assert result.provenance.inputs == (1.0, 0.01, "identity")


def test_distinct_function_labels_distinct_trace_ids():
    """Same f, delta_f, precision but different function => different trace_ids."""
    g1 = lambda x: x
    g2 = lambda x: x * x
    r1 = typed_finite_difference(g1, 1.0, 0.01, function_label="identity")
    r2 = typed_finite_difference(g2, 1.0, 0.01, function_label="square")
    assert r1.provenance.trace_id != r2.provenance.trace_id


def test_same_inputs_identical_trace_ids():
    """Content-addressed identity: same inputs (including label) => same trace_id."""
    g = lambda x: x
    r1 = typed_finite_difference(g, 1.0, 0.01, function_label="identity")
    r2 = typed_finite_difference(g, 1.0, 0.01, function_label="identity")
    assert r1.provenance.trace_id == r2.provenance.trace_id


def test_distinct_f_distinct_trace_ids():
    g = lambda x: x
    r1 = typed_finite_difference(g, 1.0, 0.01, function_label="x")
    r2 = typed_finite_difference(g, 2.0, 0.01, function_label="x")
    assert r1.provenance.trace_id != r2.provenance.trace_id


def test_distinct_delta_distinct_trace_ids():
    g = lambda x: x
    r1 = typed_finite_difference(g, 1.0, 0.01, function_label="x")
    r2 = typed_finite_difference(g, 1.0, 0.001, function_label="x")
    assert r1.provenance.trace_id != r2.provenance.trace_id


def test_provenance_records_path_metadata():
    g = lambda x: x
    result = typed_finite_difference(g, 1.0, 0.01, function_label="x")
    assert result.provenance.operation_id == "typed_finite_difference"
    assert result.provenance.expression_path == "forward_difference"
    assert result.provenance.precision == "raw_python"
    assert result.provenance.backend == "python"
    assert result.provenance.parents == ()
```

### Serialization round-trip

```python
def test_serialization_round_trip_observed():
    import json
    from lloyd_v4.core.serialization import to_json_safe
    g = lambda x: x * x
    result = typed_finite_difference(g, 1.0, 0.001, function_label="square")
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    decoded = json.loads(encoded)
    assert decoded["status"] == "transfer_observed"
    assert decoded["value"]["transfer"] is not None
    assert decoded["provenance"]["inputs"] == [1.0, 0.001, "square"]


def test_serialization_round_trip_non_finite():
    import json
    from lloyd_v4.core.serialization import to_json_safe
    g = lambda x: float("inf")
    result = typed_finite_difference(g, 1.0, 0.01, function_label="inf_fn")
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    # Must not crash; non-finite values get the {"kind": "nonfinite_float", ...}
    # treatment from to_json_safe.
    assert "Infinity" not in encoded
    assert "NaN" not in encoded
```

### Protocol validation

```python
def test_consumer_protocol_accepts_observed():
    g = lambda x: x
    result = typed_finite_difference(g, 1.0, 0.01, function_label="x")
    check = validate_protocol(result, TRANSFER_OBSERVATION_CONSUMER_PROTOCOL)
    assert check.ok


def test_consumer_protocol_refuses_cancellation_dominated():
    g = lambda x: 1.0 + 1e-20 * x
    result = typed_finite_difference(g, 1.0, 0.01, function_label="cancel")
    check = validate_protocol(result, TRANSFER_OBSERVATION_CONSUMER_PROTOCOL)
    assert not check.ok
    assert "cancellation_dominated" in check.reason or "unhandled" in check.reason
```

## Required Commands

```bash
# Pre-task: confirm gap exists.
python -c "from lloyd_v4.primitives import typed_finite_difference" 2>&1
# Expected: ImportError or AttributeError before task begins.

# Red slice: write failing tests first if practicing TDD; else skip.

# Green slice (during implementation):
pytest -x tests/test_task015_typed_finite_difference.py -v

# Full suite:
pytest -x tests/

# Source audits (these should pass automatically; documented for completeness):
pytest -x tests/test_task010a_layer_manifest_machine_readable.py
pytest -x tests/test_task010b_export_drift.py
pytest -x tests/test_task010b_manifest_completeness.py
pytest -x tests/test_task010c_no_unregistered_operations.py
```

## Non-Goals

This task explicitly does NOT:

- Add `typed_addition`, `typed_subtraction`, `typed_multiplication`, or
  `typed_power`. Arithmetic primitives are off-pattern for V4 (Axiom 1) and
  not required for `typed_finite_difference` (which uses raw Python arithmetic
  internally).
- Add multi-precision execution (numpy float32/longdouble or mpmath backends).
  `precision="raw_python"` is the only supported value; future tasks add
  others by extending `_precision_floor` dispatch.
- Add multi-path execution (e.g., `central_difference`, `direct_power` vs
  `exp_log_power`). Only `expression_path="forward_difference"` is
  implemented; `expression_path` is propagated as metadata for future variants.
- Implement linear regression, slope-window drift, BIC, or any of the
  higher-level PPS machinery. Those are downstream tasks that consume
  `typed_finite_difference` results.
- Resolve Stress Test Findings 2 (validity dishonesty) or 3 (conditioning
  honesty) at other primitives. Those remain as backlog tasks 012 and 013.
  This task introduces observation-honest validity AT THIS PRIMITIVE.
- Update metrology, branch, refinery, history, or solver layers. Those are
  V3-shaped deferred-consumer artifacts.

## Completion Report

Generate `Build_Docs/Reports/task015_summary.md` with:

- Number of tests added (target: ~20 in `test_task015_*`)
- Number of tests passing in full suite (must be 247 + new test count)
- Sample output: `typed_finite_difference(lambda x: x*x, 1.0, 0.001, function_label="square")` shown serialized
- Each of the 5 strata demonstrated with one example
- Confirmation that the layer manifest update was reflected in
  `LAYER_MANIFEST.md` (markdown) and `layer_manifest.json` (JSON)
- Trace_id uniqueness sanity: `typed_finite_difference(g, 1.0, 0.01, "square")`
  vs `typed_finite_difference(g, 1.0, 0.01, "linear")` → distinct trace_ids
- Honest note on what `typed_finite_difference` cannot yet do: no
  multi-precision, no central differences, no slope-fitting, no PPS-style
  amplitude separation. These are forward tasks.

## Acceptance Criteria

1. `TransferStatus` enum exists in `core/status.py` with the five strata named.
2. `TransferStatus` is added to the `StatusCode` union.
3. New module `src/lloyd_v4/primitives/typed_finite_difference.py` exists with
   `TransferObservation` value type, `TYPED_FINITE_DIFFERENCE_PROTOCOL`,
   `TRANSFER_OBSERVATION_CONSUMER_PROTOCOL`, and the public `typed_finite_difference`
   function.
4. `primitives/__init__.py` exports the new symbols and updates `__all__`.
5. `layer_manifest.json` declares `TransferStatus` as a primitives-layer status
   family; `TransferObservation`, `TransferObservationResult` as value types;
   the new protocols; and `typed_finite_difference` as a calibrated primitive
   operation.
6. `LAYER_MANIFEST.md` mirrors the JSON manifest changes.
7. All five strata are produced by appropriately-constructed inputs and verified
   by tests.
8. Input validation tests verify hard refusals for non-finite f, non-finite
   delta_f, non-callable g, and empty function_label.
9. Trace_id uniqueness tests pass: distinct `(f, delta_f, function_label)` produce
   distinct trace_ids; identical inputs produce identical trace_ids.
10. Serialization round-trip works for all five strata; `json.dumps(allow_nan=False)`
    succeeds (no naked NaN or Infinity in the JSON).
11. Consumer protocol validation: TRANSFER_OBSERVATION_CONSUMER_PROTOCOL accepts
    OBSERVED status, refuses other strata.
12. All existing 247 tests continue to pass.
13. `tests/test_task010c_no_unregistered_operations.py` passes (the new
    operation_id `typed_finite_difference` is registered in source AND manifest).
14. Completion report at `Build_Docs/Reports/task015_summary.md` is written.

## Discipline Notes

- Task derives from V4's own surface (the gap analysis showing V4 cannot
  currently observe a function's local slope) and theorem-derived constraints
  (the α-1 transfer law from `transfer_function_exponent_family_revised.tex`,
  which requires exactly this measurement primitive as input).
- No V3 reference required at runtime. The α-1 paper informs *what kind of
  observation* this primitive should make; the implementation derives entirely
  from V4's existing parent layers.
- No metrology, branch, refinery, or any Layer 2+ artifact is referenced or
  coordinated with. Those layers are V3-shaped deferred-consumer.
- Patent 1 (Lloyd 280326-01) framed transfer slopes as part of the diagnostic
  apparatus. Patent 2 (Lloyd 010426-02) listed Diagnostic Field Extension
  including approach-exponent observations. Both treat this kind of measurement
  as substrate-relevant, supporting the choice to add it as a Layer 1 primitive
  rather than as a downstream consumer-shaped operation.

## Subsequent tasks (forward references, not part of 015)

- **Task 016**: Add `typed_log_log_slope` — takes a typed_collection of
  (f, T) observations, fits log|T| vs log f, produces a typed slope estimate
  with R², SE, and stratum classification (SLOPE_OBSERVED,
  SLOPE_INSUFFICIENT_DATA, SLOPE_NON_LINEAR).
- **Task 017**: Add multi-precision support — extend `_precision_floor`
  dispatch to handle "float32", "float64", "longdouble", and mpmath modes;
  add execution backends.
- **Task 018**: Add `typed_window_drift` — slope estimation across nested
  windows, BIC-based model comparison for algebraic-vs-non-algebraic branch.
- **Task 019**: Add multi-path expression variants (`central_difference`,
  alternative algebraic paths for the same observable).
- **Task 020 (PPS milestone)**: Compose 015–019 to run the full
  precision/path separation experiment; recover `a` and `b_k` from
  `c_hat[p,k] = a + u_p · b_k` fit; reproduce V3's PPS report at V4 fidelity.
