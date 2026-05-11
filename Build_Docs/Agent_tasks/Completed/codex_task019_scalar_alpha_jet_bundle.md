# Task 019 — Scalar AlphaJetBundle Primitive

## Repository

`/mnt/fast/Lloyd_Engine_V4`

V3 is reference-only (Axiom 10). V1 / OG engine are also reference-only.
Layer 2+ artifacts (metrology, branch, refinery, history, solver) are V3-shaped
deferred-consumer first-drafts and MUST NOT shape this task. Do not cite them
as evidence; do not coordinate fixes with them; do not import from them. This
task is at Layer 1 (primitives) and depends only on Layer 0 (core) and the
already-built Layer 1 primitives.

## Current Verified Baseline

- 319 tests passing (`pytest -x tests/`) as of Task 018 completion
- Calibrated primitive operations: `typed_collection`, `typed_value`,
  `projective_ratio`, `stratified_quadratic_roots`, `typed_finite_difference`,
  `directional_alpha_probe`
- Internal operations: `projective_ratio.scalarize`,
  `stratified_quadratic_roots.select`, `typed_log_log_slope`
- Status families at primitives: `CollectionStatus`, `ValueStatus`,
  `ProjectiveRatioStatus`, `QuadraticRootStatus`, `TransferStatus`,
  `SlopeStatus`, `AlphaProbeStatus`
- α evidence is now first-class: `AlphaProbeResult` carries probe identity,
  transfer parent trace_ids, slope parent trace_id, observed_alpha, declared
  model evidence, full lineage

## Task Goal

Add the fourth capability primitive at Layer 1: `scalar_alpha_jet_bundle`.

This primitive packages α evidence around a scalar point x₀ as typed local
geometric evidence ready for the future solver's admissibility phase. It
constructs a local probe `g_local(h) = f(x₀+h) - f(x₀)` internally, delegates
α measurement to Task 018's `directional_alpha_probe` via the local probe,
and emits a typed result carrying point identity, local α status, the
embedded AlphaProbe's full lineage, and a convenience derivative estimate.

**Narrowed scope by name.** This is `ScalarAlphaJetBundle`, not `JetBundle`.
The name fences the implementation against curvature tensors, shape
operators, Hessian rank/signature, and multidimensional probing — all of
which are deliberately out of scope.

## Source labelling

- **(V4-surface)** Task 018 made α typed and dispatchable per probe.
  AlphaProbe samples a callable along an explicit f-grid approaching f→0+.
  To use AlphaProbe at an arbitrary point x₀, the caller currently has to
  construct `g_local(h) = f(x₀+h) - f(x₀)` themselves, pass it to AlphaProbe,
  and track the relationship between the AlphaProbe result and the original
  point. ScalarAlphaJetBundle packages this composition as a typed primitive.
- **(theorem-derived)** The α-1 transfer law applies to local probes the
  same way as global probes: if `f(x₀+h) - f(x₀) ≈ c·h^α·L(h)` near h=0,
  then the local log-log slope of the finite differences recovers α-1, and
  observed_alpha = observed_slope + 1. ScalarAlphaJetBundle uses this
  identity through delegation; it does not reimplement α fitting.
- **(Codex updated proposal, agreed refinements)** ScalarAlphaJetBundle
  consumes Directional AlphaProbe via internal construction (not caller-
  supplied AlphaProbeResult). The h-grid is caller-supplied with no default
  (measurement policy is the caller's). The derivative is a convenience
  field pulled from existing computation, not its own strata-bearing
  observation. `scalar_jet_constant` is dropped from v1 (constancy
  detection doesn't fall cleanly out of AlphaProbe's mechanics for nonzero
  vs zero constants). AlphaProbe refusals propagate as typed JetBundle
  refusals; the bundle must produce a typed result for every legal input.

## Design Principles

- **Narrow by name (Axiom 12).** ScalarAlphaJetBundle measures α evidence
  at a scalar point. No multi-dim. No Hessian. No curvature. No solver.
  The narrow name is the architectural fence.
- **Composition, not reimplementation.** AlphaProbe is the α primitive;
  this task composes it. ScalarAlphaJetBundle MUST NOT reimplement slope
  fitting, transfer computation, or stratum classification logic that
  already exists in AlphaProbe or its dependencies.
- **h-grid is caller-supplied measurement policy (Axiom 3).** No default
  grid. The local h_values are declared metrology, just like AlphaProbe's
  f_values were declared metrology for the f→0+ probe.
- **Typed refusal propagation, never raise on substrate observation.**
  ScalarAlphaJetBundle produces a typed result for every legal input,
  including all AlphaProbe refusal cases. The embedded AlphaProbe failing
  is not an exception; it is a typed observation that JetBundle reflects
  through its own stratum.
- **Derivative as convenience field, not separate stratum.** The future
  solver needs a derivative number for step construction. ScalarAlphaJetBundle
  pulls one from the smallest-h OBSERVED transfer in the embedded AlphaProbe's
  computation. If no h produces OBSERVED, derivative_at_point is None.
  No separate derivative status family. No derivative confidence subsystem.
- **Lineage discipline.** The JetBundle preserves AlphaProbe's trace_id
  (which transitively reaches every transfer trace_id and the slope
  trace_id). The lineage walk from a JetBundle result reaches every
  underlying typed observation.

## Primitive-Sufficiency Gate

| Concept used | Provided by | Location |
|---|---|---|
| `TypedResult`, `Validity`, `Conditioning`, `Provenance` | core | `core/*.py` |
| `ProducerProtocol`, `ConsumerProtocol`, `validate_protocol` | core | `core/protocols.py` |
| `ProtocolStatus`, `ConditioningStatus` | core | `core/status.py` |
| `ProtocolViolationError` | core | `core/errors.py` |
| `TransferObservationResult`, `TransferStatus`, `typed_finite_difference` | primitives | `typed_finite_difference.py` |
| `AlphaProbeResult`, `AlphaProbeStatus`, `directional_alpha_probe`, `DeclaredAlphaModel` | primitives | `directional_alpha_probe.py` |
| Pattern: calibrated primitive composing existing primitives internally | primitives | `directional_alpha_probe` precedent |
| Pattern: typed refusal propagation via explicit status mapping | primitives | first explicit such mapping; see Algorithm |

Sufficiency gate **passes**. AlphaProbe is the load-bearing dependency.

## Required Deliverables

### 1. New status family in `src/lloyd_v4/core/status.py`

```python
class ScalarAlphaJetBundleStatus(StrEnum):
    SCALAR_JET_REGULAR_INTEGER_ALPHA = "scalar_jet_regular_integer_alpha"
    SCALAR_JET_FRACTIONAL_ALPHA_BRANCH = "scalar_jet_fractional_alpha_branch"
    SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY = "scalar_jet_negative_alpha_singularity"
    SCALAR_JET_ALPHA_MODEL_REFUSED = "scalar_jet_alpha_model_refused"
    SCALAR_JET_ALPHA_CANCELLATION_DOMINATED = "scalar_jet_alpha_cancellation_dominated"
    SCALAR_JET_ALPHA_INDETERMINATE = "scalar_jet_alpha_indeterminate"
    SCALAR_JET_DOMAIN_REFUSED = "scalar_jet_domain_refused"
    SCALAR_JET_NONFINITE = "scalar_jet_nonfinite"
    SCALAR_JET_PROTOCOL_REFUSED = "scalar_jet_protocol_refused"
```

Add `ScalarAlphaJetBundleStatus` to the `StatusCode` union.

Stratum semantics:

- **SCALAR_JET_REGULAR_INTEGER_ALPHA**: Embedded AlphaProbe returned
  `ALPHA_REGULAR_INTEGER`. Local behavior at x₀ is approximately
  `f(x₀+h) ≈ f(x₀) + c·h^n` for integer n ≥ 1, within declared band.
- **SCALAR_JET_FRACTIONAL_ALPHA_BRANCH**: Embedded AlphaProbe returned
  `ALPHA_FRACTIONAL_BRANCH`. Local behavior is fractional-power
  (e.g., sqrt branch, cube-root branch).
- **SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY**: Embedded AlphaProbe returned
  `ALPHA_NEGATIVE_SINGULARITY`. Local behavior is singular (f blowing up).
- **SCALAR_JET_ALPHA_MODEL_REFUSED**: Embedded AlphaProbe returned
  `ALPHA_MODEL_AMBIGUOUS` OR `ALPHA_MODEL_NO_MATCH`. Caller's declared
  models were inconsistent with observation. The specific case
  (ambiguous vs no_match) is preserved in `value.alpha_status` and
  `value.matching_alpha_model_names`.
- **SCALAR_JET_ALPHA_CANCELLATION_DOMINATED**: Embedded AlphaProbe returned
  `ALPHA_CANCELLATION_DOMINATED`. The chosen h-grid is below the precision
  floor for cancellation; local α cannot be observed at this precision.
- **SCALAR_JET_ALPHA_INDETERMINATE**: Embedded AlphaProbe returned
  `ALPHA_INSUFFICIENT_DATA` OR `ALPHA_INDETERMINATE`. h-grid too short
  or degenerate.
- **SCALAR_JET_DOMAIN_REFUSED**: Either f(x₀) itself raised or returned
  non-numeric, OR the embedded AlphaProbe returned `ALPHA_DOMAIN_REFUSED`.
- **SCALAR_JET_NONFINITE**: f(x₀) was non-finite, OR the embedded
  AlphaProbe returned `ALPHA_NONFINITE`.
- **SCALAR_JET_PROTOCOL_REFUSED**: An input failed protocol validation in
  a recoverable way (rare; most input failures raise ProtocolViolationError
  before TypedResult construction). Reserved for cases where downstream
  protocols (e.g., transitions) refuse cleanly.

### 2. New module `src/lloyd_v4/primitives/scalar_alpha_jet_bundle.py`

#### Module-level constants

```python
SCALAR_ALPHA_JET_BUNDLE_SPACE = "ScalarAlphaJetBundleObservation"

SCALAR_ALPHA_JET_BUNDLE_STATUSES = frozenset({
    ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA,
    ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH,
    ScalarAlphaJetBundleStatus.SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY,
    ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_MODEL_REFUSED,
    ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_CANCELLATION_DOMINATED,
    ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_INDETERMINATE,
    ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED,
    ScalarAlphaJetBundleStatus.SCALAR_JET_NONFINITE,
    ScalarAlphaJetBundleStatus.SCALAR_JET_PROTOCOL_REFUSED,
})

SCALAR_ALPHA_JET_BUNDLE_PROTOCOL = ProducerProtocol(
    name="scalar_alpha_jet_bundle",
    emitted_statuses=SCALAR_ALPHA_JET_BUNDLE_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=ScalarAlphaJetBundleStatus,
)

SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="scalar_alpha_jet_bundle_consumer",
    accepted_statuses=frozenset({
        ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA,
        ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH,
        ScalarAlphaJetBundleStatus.SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY,
    }),
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
    status_family=ScalarAlphaJetBundleStatus,
    refused_statuses=SCALAR_ALPHA_JET_BUNDLE_STATUSES - frozenset({
        ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA,
        ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH,
        ScalarAlphaJetBundleStatus.SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY,
    }),
)
```

The consumer protocol accepts the three observation strata; everything
else is explicit refusal. Same pattern as AlphaProbe.

#### Value type

```python
@dataclass(frozen=True, slots=True)
class ScalarAlphaJetBundleObservation:
    # Point identity
    point: float
    f_value: float | None             # f(x₀); None if evaluation refused/nonfinite
    probe_id: str                     # caller-supplied
    function_label: str               # caller-supplied
    h_values: tuple[float, ...]       # caller-supplied local h-grid
    eta: float                        # passed through to AlphaProbe

    # Embedded AlphaProbe lineage
    alpha_probe_trace_id: str | None  # the embedded AlphaProbe's trace_id (None if pre-probe refusal)
    transfer_trace_ids: tuple[str, ...]  # mirrored from AlphaProbe.value for diagnostic ease
    slope_trace_id: str | None        # mirrored from AlphaProbe.value

    # α observation
    observed_slope: float | None
    observed_alpha: float | None
    alpha_status: AlphaProbeStatus | None  # the embedded AlphaProbe's stratum

    # Derivative convenience field (smallest-h OBSERVED transfer)
    derivative_at_point: float | None
    derivative_h: float | None
    derivative_transfer_trace_id: str | None

    # Declared model evidence (passed through to AlphaProbe and mirrored here)
    declared_alpha_models: tuple[DeclaredAlphaModel, ...]
    declared_alpha_band: float | None
    selected_alpha_model: str | None
    matching_alpha_model_names: tuple[str, ...]

    expression_path: str

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe
        return {
            "point": self.point,
            "f_value": to_json_safe(self.f_value),
            "probe_id": self.probe_id,
            "function_label": self.function_label,
            "h_values": list(self.h_values),
            "eta": self.eta,
            "alpha_probe_trace_id": self.alpha_probe_trace_id,
            "transfer_trace_ids": list(self.transfer_trace_ids),
            "slope_trace_id": self.slope_trace_id,
            "observed_slope": to_json_safe(self.observed_slope),
            "observed_alpha": to_json_safe(self.observed_alpha),
            "alpha_status": self.alpha_status.value if self.alpha_status is not None else None,
            "derivative_at_point": to_json_safe(self.derivative_at_point),
            "derivative_h": to_json_safe(self.derivative_h),
            "derivative_transfer_trace_id": self.derivative_transfer_trace_id,
            "declared_alpha_models": [m.to_json_safe() for m in self.declared_alpha_models],
            "declared_alpha_band": to_json_safe(self.declared_alpha_band),
            "selected_alpha_model": self.selected_alpha_model,
            "matching_alpha_model_names": list(self.matching_alpha_model_names),
            "expression_path": self.expression_path,
        }


ScalarAlphaJetBundleResult = TypedResult[
    ScalarAlphaJetBundleObservation, ScalarAlphaJetBundleStatus
]
```

#### Public function

```python
def scalar_alpha_jet_bundle(
    func: Callable[[float], float],
    x0: float,
    h_values: Sequence[float],
    *,
    probe_id: str,
    function_label: str,
    eta: float = 1e-6,
    declared_alpha_models: Sequence[DeclaredAlphaModel] = (),
    declared_alpha_band: float | None = None,
    precision: str = "raw_python",
    backend: str = "python",
    device: str = "cpu",
    measurement_resolution: Any | None = None,
    expression_path: str = "scalar_alpha_jet_local_probe",
) -> ScalarAlphaJetBundleResult:
    """Package local α evidence around a scalar point x₀.

    Constructs g_local(h) = func(x₀+h) - func(x₀) internally and delegates
    α measurement to directional_alpha_probe. Pulls a derivative estimate
    from the smallest-h OBSERVED transfer in the embedded computation.

    Inputs:
        func: scalar callable. May raise or return non-numeric at x₀ or
              x₀+h; handled as typed observations.
        x0: the point at which local α is measured. Must be finite.
        h_values: explicit positive local probe grid. All values must be
                  finite and strictly positive. Caller's measurement policy.
        probe_id: required caller-supplied label identifying this jet.
                  Distinguishes jets at different points or with different
                  intent.
        function_label: required caller-supplied identifier for the outer
                  function being measured. The embedded AlphaProbe receives
                  a derived label that incorporates x₀.
        eta: relative delta multiplier passed to AlphaProbe.
        declared_alpha_models, declared_alpha_band: passed through to
                  AlphaProbe for model matching.
        precision, backend, device, measurement_resolution, expression_path:
                  path metadata.

    Returns:
        TypedResult[ScalarAlphaJetBundleObservation, ScalarAlphaJetBundleStatus].
        Always returns; never raises except for input-level ProtocolViolationError.
    """
```

#### Input validation

Raise `ProtocolViolationError` BEFORE any TypedResult construction for:

- `func` is not callable
- `x0` is not int/float, OR is non-finite
- `h_values` is empty, OR contains any non-finite or non-positive value
- `eta` is not finite, OR is zero
- `probe_id` is not a non-empty string
- `function_label` is not a non-empty string
- Other input failures already caught by `directional_alpha_probe`
  (duplicate model names, non-finite alpha/band, etc.) — these propagate
  as raised exceptions from the underlying primitive

Failures at f(x₀) evaluation are NOT raised; they become
`SCALAR_JET_DOMAIN_REFUSED` or `SCALAR_JET_NONFINITE` typed observations.

#### Algorithm

```
1. Validate inputs (raise on bad inputs as above).

2. Evaluate f(x₀):
   try:
       f_at_x0_raw = func(x0)
   except Exception as exc:
       return _domain_refused_result(
           reason=f"f(x0) raised {type(exc).__name__}",
           f_value=None, alpha_probe_trace_id=None,
           ... (all alpha fields None, transfer_trace_ids empty)
       )

   if not isinstance(f_at_x0_raw, (int, float)):
       return _domain_refused_result(
           reason=f"f(x0) returned {type(f_at_x0_raw).__name__}",
           f_value=None, ...
       )

   f_at_x0 = float(f_at_x0_raw)

   if not math.isfinite(f_at_x0):
       return _nonfinite_result(
           f_value=f_at_x0, alpha_probe_trace_id=None, ...
       )

3. Construct the local observable. Use a closure that captures f_at_x0
   so the JetBundle does not re-evaluate func at x₀ for every h:

   def g_local(h):
       return func(x0 + h) - f_at_x0

4. Construct embedded probe identifiers that depend on x₀:

   embedded_probe_id = f"{probe_id}__x0_{x0!r}"
   embedded_function_label = f"{function_label}__local_at_{x0!r}"

   This ensures the embedded AlphaProbe's trace_id varies with x₀
   even when (probe_id, function_label, h_values, eta) are otherwise
   identical across jets at different points.

5. Run the embedded AlphaProbe:

   alpha_probe_result = directional_alpha_probe(
       g_local,
       list(h_values),
       probe_id=embedded_probe_id,
       function_label=embedded_function_label,
       eta=eta,
       declared_alpha_models=declared_alpha_models,
       declared_alpha_band=declared_alpha_band,
       precision=precision,
       backend=backend,
       device=device,
       measurement_resolution=measurement_resolution,
       expression_path="log_log_slope_fit",
   )

6. Extract α-evidence fields from alpha_probe_result.value:

   alpha_status = alpha_probe_result.status
   observed_slope = alpha_probe_result.value.observed_slope
   observed_alpha = alpha_probe_result.value.observed_alpha
   transfer_trace_ids = alpha_probe_result.value.transfer_trace_ids
   slope_trace_id = alpha_probe_result.value.slope_trace_id
   selected_alpha_model = alpha_probe_result.value.selected_alpha_model
   matching_alpha_model_names = alpha_probe_result.value.matching_alpha_model_names

7. Compute derivative_at_point (convenience field):

   sorted_h = sorted(set(h_values))
   derivative_at_point = None
   derivative_h = None
   derivative_transfer_trace_id = None

   for h in sorted_h:
       transfer = typed_finite_difference(
           g_local, h, eta * h,
           function_label=embedded_function_label,
           precision=precision, backend=backend, device=device,
           measurement_resolution=measurement_resolution,
           expression_path="forward_difference",
       )
       if transfer.status is TransferStatus.TRANSFER_OBSERVED:
           derivative_at_point = transfer.value.transfer
           derivative_h = h
           derivative_transfer_trace_id = transfer.provenance.trace_id
           break

   By content-addressed identity, the typed_finite_difference call at
   each h here produces the same trace_id as the AlphaProbe's internal
   call at the same h. The lineage walk is the same observation.

8. Map AlphaProbeStatus -> ScalarAlphaJetBundleStatus per the explicit
   table:

   ALPHA_REGULAR_INTEGER       -> SCALAR_JET_REGULAR_INTEGER_ALPHA
   ALPHA_FRACTIONAL_BRANCH     -> SCALAR_JET_FRACTIONAL_ALPHA_BRANCH
   ALPHA_NEGATIVE_SINGULARITY  -> SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY
   ALPHA_MODEL_AMBIGUOUS       -> SCALAR_JET_ALPHA_MODEL_REFUSED
   ALPHA_MODEL_NO_MATCH        -> SCALAR_JET_ALPHA_MODEL_REFUSED
   ALPHA_CANCELLATION_DOMINATED -> SCALAR_JET_ALPHA_CANCELLATION_DOMINATED
   ALPHA_INSUFFICIENT_DATA     -> SCALAR_JET_ALPHA_INDETERMINATE
   ALPHA_INDETERMINATE         -> SCALAR_JET_ALPHA_INDETERMINATE
   ALPHA_DOMAIN_REFUSED        -> SCALAR_JET_DOMAIN_REFUSED
   ALPHA_NONFINITE             -> SCALAR_JET_NONFINITE

9. Build ScalarAlphaJetBundleObservation with all fields populated.
   Build Provenance:

   provenance = Provenance(
       operation_id="scalar_alpha_jet_bundle",
       expression_path=expression_path,
       precision=precision,
       backend=backend,
       device=device,
       measurement_resolution=measurement_resolution,
       inputs=(probe_id, function_label, x0, tuple(h_values), eta),
       parents=(alpha_probe_result.provenance.trace_id,),
   )

   Note: parents has exactly one entry (the AlphaProbe trace_id). The
   AlphaProbe transitively encodes every transfer and slope. The
   derivative transfer's trace_id is reachable through AlphaProbe's
   parents; it does NOT appear separately in JetBundle's parents.

10. Return TypedResult with the mapped status, observation, validity,
    conditioning, provenance.
```

#### Validity per stratum

| Stratum | defined | finite | selectable | advanceable | observable |
|---|---|---|---|---|---|
| SCALAR_JET_REGULAR_INTEGER_ALPHA | True | True | True | True | True |
| SCALAR_JET_FRACTIONAL_ALPHA_BRANCH | True | True | True | True | True |
| SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY | True | True | True | False | True |
| SCALAR_JET_ALPHA_MODEL_REFUSED | True | True | False | False | True |
| SCALAR_JET_ALPHA_CANCELLATION_DOMINATED | False | False | False | False | True |
| SCALAR_JET_ALPHA_INDETERMINATE | False | False | False | False | True |
| SCALAR_JET_DOMAIN_REFUSED | False | False | False | False | True |
| SCALAR_JET_NONFINITE | True | False | False | False | True |
| SCALAR_JET_PROTOCOL_REFUSED | False | False | False | False | True |

Mirrors AlphaProbe's validity per stratum after the status mapping.

#### Conditioning per stratum

- **Three accepted strata**: `Conditioning(WELL_CONDITIONED, notes=(
  f"observed_alpha={alpha:.6g}", f"alpha_status={alpha_status.value}",
  f"derivative_at_point={dap:.3e if dap is not None else 'unavailable'}",
  f"h_used={dh:.3e if dh is not None else 'none'}"))`.
- **Model refused**: `Conditioning(WARNING, notes=(
  f"alpha_status={alpha_status.value}",
  f"matching_models={list(matching_alpha_model_names)}"))`.
- **Other refusals**: `Conditioning(WARNING, notes=(
  f"alpha_status={alpha_status.value if alpha_status else 'pre_probe_refusal'}",
  f"reason={short_explanation}"))`.

### 3. Update `src/lloyd_v4/primitives/__init__.py`

```python
from .scalar_alpha_jet_bundle import (
    SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL,
    SCALAR_ALPHA_JET_BUNDLE_PROTOCOL,
    SCALAR_ALPHA_JET_BUNDLE_SPACE,
    ScalarAlphaJetBundleObservation,
    ScalarAlphaJetBundleResult,
    scalar_alpha_jet_bundle,
)
```

Add to `__all__`.

### 4. Update `Build_Docs/Architecture/layer_manifest.json`

In the `primitives` layer entry:

- Add `"ScalarAlphaJetBundleStatus"` to `status_families`
- Add `"ScalarAlphaJetBundleObservation"`, `"ScalarAlphaJetBundleResult"`
  to `value_types`
- Add `"SCALAR_ALPHA_JET_BUNDLE_PROTOCOL"`,
  `"SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL"` to `protocol_types`
- Add `"SCALAR_ALPHA_JET_BUNDLE_SPACE"` to `errors_and_utilities`
- Add `"scalar_alpha_jet_bundle"` to `operations` AND
  `calibrated_primitive_operations`
- Update `all_exports` alphabetically

### 5. Update `Build_Docs/Architecture/LAYER_MANIFEST.md`

Mirror the JSON changes.

### 6. Update `Build_Docs/Architecture/STATUS_CALCULUS.md`

Append a section on `ScalarAlphaJetBundleStatus` covering the nine strata
and the explicit AlphaProbeStatus → ScalarAlphaJetBundleStatus mapping.

### 7. New test file `tests/test_task019_scalar_alpha_jet_bundle.py`

See Required Tests section.

## Required Tests

### Pre-task evidence

```python
def test_scalar_alpha_jet_bundle_does_not_yet_exist() -> None:
    """Pre-task evidence; remove during implementation."""
    pass
```

### Stratum coverage

```python
def test_regular_integer_stratum_quadratic_at_origin():
    """f(x) = x^2 at x0=0 with explicit h-grid."""
    f = lambda x: x * x
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    result = scalar_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="quad_jet",
        function_label="square",
        declared_alpha_band=0.01,
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA
    assert abs(result.value.observed_alpha - 2.0) < 1e-3
    assert result.value.point == 0.0
    assert result.value.f_value == 0.0
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_REGULAR_INTEGER


def test_fractional_branch_stratum_sqrt_at_origin():
    """f(x) = sqrt(x) at x0=0."""
    import math as _m
    f = lambda x: _m.sqrt(x)
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    result = scalar_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="sqrt_jet",
        function_label="sqrt",
        declared_alpha_band=0.01,
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH
    assert abs(result.value.observed_alpha - 0.5) < 1e-3


def test_negative_alpha_singularity_stratum():
    """f(x) = log(x), at x0=1 the local behavior is regular,
    but f(x0+h)-f(x0) ≈ h - h²/2 + ... so local α should be 1."""
    # For singularity test, pick a function genuinely singular locally:
    # f(x) = 1/x at x0=1 -> f(1+h) - f(1) = 1/(1+h) - 1 = -h/(1+h),
    # which has α=1 locally (regular). For NEGATIVE alpha at the JetBundle
    # level, we need f(x0+h)-f(x0) to scale like h^α with α < 0, which
    # requires the function to be singular AT x0.
    # Use: f(x) = 1/x, x0 = 0+ approached. Local probe at x0 ≈ 0+ would
    # produce nonfinite f(x0) before AlphaProbe runs.
    # Construct: at x0=0, define f(x) = 1/x for x>0 (raises at x=0).
    # The JetBundle should classify as SCALAR_JET_DOMAIN_REFUSED because
    # f(x0=0) raises (ZeroDivisionError).
    # For genuine NEGATIVE_ALPHA_SINGULARITY: use f(x) = 1/x at a point
    # where f(x0) is finite but the local g_local(h) has divergent behavior.
    # Tricky in the scalar JetBundle frame. For v1, demonstrate via:
    # construct a function whose g_local(h) = h^{-1} type behavior
    # by adding an offset.
    def f(x):
        # f(x) = 1 + 1/x for x near (but not at) a chosen point.
        # At x0 = 1, f(1) = 2; f(1+h) - f(1) = 1/(1+h) - 1 = -h/(1+h).
        # That's α=1 (regular), not negative.
        # For genuine negative-alpha behavior on g_local, need:
        # g_local(h) = h^α with α<0, which is impossible for a callable
        # that's finite at x0 (g_local(h) → 0 as h → 0 by definition).
        # So at a finite x0, NEGATIVE_ALPHA cannot be observed in
        # ScalarAlphaJetBundle. The only path is through AlphaProbe at
        # a non-JetBundle approach grid (f→0+ directly).
        # This stratum may be unreachable in practice for ScalarAlphaJetBundle;
        # if a future consumer needs it, they go through AlphaProbe directly.
        return 1.0 + 1.0/x

    # We expect SCALAR_JET_REGULAR_INTEGER_ALPHA (α=1) here, not singularity.
    h_values = [1e-6, 1e-5, 1e-4, 1e-3]
    result = scalar_alpha_jet_bundle(
        f, 1.0, h_values,
        probe_id="reciprocal_jet",
        function_label="one_plus_inverse",
        declared_alpha_band=0.01,
    )
    # Expect REGULAR_INTEGER_ALPHA because g_local is well-behaved at x0=1.
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA
    # Note: SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY is structurally hard to
    # reach via ScalarAlphaJetBundle because g_local(h) = f(x0+h) - f(x0)
    # always tends to 0 at h=0 for finite f(x0). Document this in the spec
    # rather than force-testing the stratum.


def test_alpha_model_refused_ambiguous():
    """Two declared models with overlapping bands both match observed α."""
    f = lambda x: x * x
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    models = (
        DeclaredAlphaModel("quadratic", 2.0, 0.5),
        DeclaredAlphaModel("near_quadratic", 2.4, 0.5),
    )
    result = scalar_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="ambig_jet",
        function_label="square",
        declared_alpha_models=models,
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_MODEL_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS
    assert set(result.value.matching_alpha_model_names) == {"quadratic", "near_quadratic"}


def test_alpha_model_refused_no_match():
    """Declared models exclude observed α."""
    f = lambda x: x * x  # α=2
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    models = (DeclaredAlphaModel("sqrt", 0.5, 0.05),)
    result = scalar_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="no_match_jet",
        function_label="square",
        declared_alpha_models=models,
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_MODEL_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_MODEL_NO_MATCH


def test_cancellation_dominated_stratum_near_constant():
    """Near-constant callable: tiny perturbation rounds to zero."""
    f = lambda x: 1.0 + 1e-20 * x
    h_values = [1e-4, 1e-3, 1e-2, 1e-1]
    result = scalar_alpha_jet_bundle(
        f, 1.0, h_values,
        probe_id="cancel_jet",
        function_label="near_constant",
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_CANCELLATION_DOMINATED


def test_domain_refused_stratum_at_x0():
    """f raises at x0 itself."""
    def f(x):
        if x == 0:
            raise ValueError("undefined at 0")
        return 1.0 / x
    h_values = [1e-4, 1e-3, 1e-2]
    result = scalar_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="x0_raises",
        function_label="reciprocal",
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED
    assert result.value.f_value is None
    assert result.value.alpha_probe_trace_id is None
    # AlphaProbe was never invoked
    assert result.value.transfer_trace_ids == ()


def test_domain_refused_stratum_at_x0_plus_h():
    """f succeeds at x0 but fails at x0+h."""
    def f(x):
        if x == 0.0:
            return 1.0
        raise ValueError("only defined at 0")
    h_values = [1e-4, 1e-3, 1e-2]
    result = scalar_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="h_raises",
        function_label="point_only",
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED
    assert result.value.f_value == 1.0
    assert result.value.alpha_probe_trace_id is not None
    # AlphaProbe ran but classified ALPHA_DOMAIN_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_DOMAIN_REFUSED


def test_nonfinite_stratum_f_at_x0():
    """f returns inf at x0."""
    f = lambda x: float("inf")
    h_values = [1e-4, 1e-3, 1e-2]
    result = scalar_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="inf_jet",
        function_label="constant_inf",
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_NONFINITE
    assert result.value.f_value == float("inf") or math.isinf(result.value.f_value)
    # Actually f_value gets stored even if non-finite; check it's non-finite
    assert not math.isfinite(result.value.f_value)


def test_indeterminate_stratum_insufficient_h_values():
    """Only two h values."""
    f = lambda x: x * x
    h_values = [1e-3, 1e-2]
    result = scalar_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="few",
        function_label="square",
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_INDETERMINATE
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_INSUFFICIENT_DATA


def test_indeterminate_stratum_repeated_h():
    """All identical h values."""
    f = lambda x: x * x
    h_values = [1e-3, 1e-3, 1e-3, 1e-3]
    result = scalar_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="degen",
        function_label="square",
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_INDETERMINATE
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_INDETERMINATE
```

### Input validation

```python
def test_empty_h_values_raises():
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(lambda x: x, 0.0, [],
            probe_id="x", function_label="x")


def test_non_positive_h_raises():
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(lambda x: x, 0.0, [-1e-3, 1e-3, 1e-2],
            probe_id="x", function_label="x")


def test_non_finite_x0_raises():
    import math as _m
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(lambda x: x, _m.inf, [1e-3, 1e-2],
            probe_id="x", function_label="x")


def test_empty_probe_id_raises():
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(lambda x: x, 0.0, [1e-3, 1e-2, 1e-1],
            probe_id="", function_label="x")


def test_non_callable_func_raises():
    with pytest.raises(ProtocolViolationError):
        scalar_alpha_jet_bundle(42, 0.0, [1e-3, 1e-2],
            probe_id="x", function_label="x")
```

### Derivative convenience field

```python
def test_derivative_pulled_from_smallest_observed_h():
    """For f(x)=x^2 at x0=1, derivative is 2*1+h ≈ 2 for small h."""
    f = lambda x: x * x
    h_values = [1e-3, 1e-2, 1e-1]  # ascending
    result = scalar_alpha_jet_bundle(
        f, 1.0, h_values,
        probe_id="deriv_check",
        function_label="square",
        declared_alpha_band=0.01,
    )
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA
    # smallest h is 1e-3; derivative = (f(1.001) - f(1))/0.001 ≈ 2.001
    assert result.value.derivative_h == 1e-3
    assert abs(result.value.derivative_at_point - 2.001) < 1e-9


def test_derivative_none_when_no_h_observed():
    """Cancellation-dominated function: no derivative recoverable."""
    f = lambda x: 1.0 + 1e-20 * x
    h_values = [1e-4, 1e-3, 1e-2]
    result = scalar_alpha_jet_bundle(
        f, 1.0, h_values,
        probe_id="no_deriv",
        function_label="near_constant",
    )
    assert result.value.derivative_at_point is None
    assert result.value.derivative_h is None
    assert result.value.derivative_transfer_trace_id is None
```

### Provenance and identity

```python
def test_inputs_carry_probe_function_label_x0_h_eta():
    f = lambda x: x * x
    h_values = (1e-3, 1e-2, 1e-1)
    result = scalar_alpha_jet_bundle(
        f, 0.5, list(h_values),
        probe_id="quad", function_label="square",
        eta=1e-6,
    )
    assert result.provenance.inputs == ("quad", "square", 0.5, h_values, 1e-6)


def test_parents_contains_only_alpha_probe_trace():
    f = lambda x: x * x
    h_values = [10**(-i) for i in range(2, 8)]
    result = scalar_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="x", function_label="square",
        declared_alpha_band=0.01,
    )
    # parents is just the AlphaProbe trace_id
    assert len(result.provenance.parents) == 1
    assert result.provenance.parents[0] == result.value.alpha_probe_trace_id


def test_distinct_x0_distinct_trace_ids():
    """Two JetBundles at different x0 produce distinct trace_ids."""
    f = lambda x: x * x
    h_values = [1e-3, 1e-2, 1e-1]
    r1 = scalar_alpha_jet_bundle(f, 0.0, h_values,
        probe_id="x", function_label="square")
    r2 = scalar_alpha_jet_bundle(f, 1.0, h_values,
        probe_id="x", function_label="square")
    assert r1.provenance.trace_id != r2.provenance.trace_id


def test_distinct_x0_distinct_alpha_probe_trace_ids():
    """The embedded AlphaProbe at different x0 must have distinct trace_ids
    (via the embedded probe_id / function_label augmentation with x0)."""
    f = lambda x: x * x
    h_values = [1e-3, 1e-2, 1e-1]
    r1 = scalar_alpha_jet_bundle(f, 0.0, h_values,
        probe_id="x", function_label="square")
    r2 = scalar_alpha_jet_bundle(f, 1.0, h_values,
        probe_id="x", function_label="square")
    # The embedded AlphaProbe trace_ids must differ — discipline test that
    # ScalarAlphaJetBundle is not collapsing local probes at different points.
    assert r1.value.alpha_probe_trace_id != r2.value.alpha_probe_trace_id


def test_identical_inputs_identical_trace_ids():
    f = lambda x: x * x
    h_values = [1e-3, 1e-2, 1e-1]
    r1 = scalar_alpha_jet_bundle(f, 0.5, h_values,
        probe_id="x", function_label="square")
    r2 = scalar_alpha_jet_bundle(f, 0.5, h_values,
        probe_id="x", function_label="square")
    assert r1.provenance.trace_id == r2.provenance.trace_id
    assert r1.value.alpha_probe_trace_id == r2.value.alpha_probe_trace_id


def test_lineage_walks_to_underlying_transfers():
    """Audit machinery should walk JetBundle -> AlphaProbe -> transfers."""
    from _audit_helpers.lineage import build_trace_id_index, walk_chain
    f = lambda x: x * x
    h_values = [10**(-i) for i in range(2, 8)]
    result = scalar_alpha_jet_bundle(f, 0.0, h_values,
        probe_id="x", function_label="square",
        declared_alpha_band=0.01)
    # The walk should reach the AlphaProbe's transfer trace_ids and slope trace_id
    # (transitively through the AlphaProbe parent).
    # Test infrastructure: collect every typed result the implementation produced
    # and verify lineage closure.
    # Implementation note: this test may need to instantiate a registry of
    # typed results encountered during scalar_alpha_jet_bundle's execution.
    # If the existing lineage helpers don't support this, skip — the lineage
    # is tested at the audit-machinery level by test_task010c_lineage_terminates_in_primitive.
    pass  # placeholder; the audit-level lineage test covers structural correctness


def test_provenance_records_path_metadata():
    f = lambda x: x * x
    result = scalar_alpha_jet_bundle(f, 0.0, [1e-3, 1e-2, 1e-1],
        probe_id="x", function_label="square")
    assert result.provenance.operation_id == "scalar_alpha_jet_bundle"
    assert result.provenance.expression_path == "scalar_alpha_jet_local_probe"
    assert result.provenance.precision == "raw_python"
```

### Discipline: typed refusal propagation

```python
def test_alpha_probe_refusal_propagates_as_typed_result_not_exception():
    """When the embedded AlphaProbe refuses, JetBundle returns a typed
    result, never raises."""
    # Use a callable that raises after a few samples
    call_count = [0]
    def f(x):
        call_count[0] += 1
        if call_count[0] > 1:  # f(x0) succeeds, all subsequent calls fail
            raise ValueError("only first call allowed")
        return 0.0  # f(0) = 0
    h_values = [1e-3, 1e-2, 1e-1]
    # Should NOT raise. Should return a JetBundle with DOMAIN_REFUSED.
    result = scalar_alpha_jet_bundle(f, 0.0, h_values,
        probe_id="x", function_label="restricted")
    assert isinstance(result, TypedResult)
    assert result.status is ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED


def test_no_default_h_grid():
    """Passing None or omitting h_values must not be accepted by accident."""
    f = lambda x: x * x
    # h_values is positional-only required — calling without it is a TypeError
    # from Python itself (not a typed refusal). Test that it's required:
    import inspect
    sig = inspect.signature(scalar_alpha_jet_bundle)
    h_param = sig.parameters["h_values"]
    assert h_param.default is inspect.Parameter.empty
```

### Serialization

```python
def test_serialization_round_trip_observed():
    import json
    from lloyd_v4.core.serialization import to_json_safe
    f = lambda x: x * x
    result = scalar_alpha_jet_bundle(
        f, 0.0, [1e-3, 1e-2, 1e-1, 1.0],
        probe_id="x", function_label="square",
        declared_alpha_band=0.05,
    )
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    decoded = json.loads(encoded)
    assert decoded["status"] == "scalar_jet_regular_integer_alpha"
    assert decoded["value"]["observed_alpha"] is not None
    assert decoded["value"]["alpha_status"] == "alpha_regular_integer"


def test_serialization_round_trip_refusal():
    import json
    from lloyd_v4.core.serialization import to_json_safe
    f = lambda x: 1.0 + 1e-20 * x
    result = scalar_alpha_jet_bundle(
        f, 1.0, [1e-3, 1e-2, 1e-1],
        probe_id="x", function_label="near_constant",
    )
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    assert "Infinity" not in encoded
    assert "NaN" not in encoded
```

### Protocol validation

```python
def test_consumer_protocol_accepts_observed_strata():
    f = lambda x: x * x
    result = scalar_alpha_jet_bundle(
        f, 0.0, [1e-3, 1e-2, 1e-1, 1.0],
        probe_id="x", function_label="square",
        declared_alpha_band=0.05,
    )
    check = validate_protocol(result, SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL)
    assert check.ok


def test_consumer_protocol_refuses_refusal_strata():
    f = lambda x: 1.0 + 1e-20 * x
    result = scalar_alpha_jet_bundle(
        f, 1.0, [1e-3, 1e-2, 1e-1],
        probe_id="x", function_label="near_constant",
    )
    check = validate_protocol(result, SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL)
    assert not check.ok
```

## Required Commands

```bash
# Pre-task
python -c "from lloyd_v4.primitives import scalar_alpha_jet_bundle" 2>&1
# Expected: ImportError

# Green slice
pytest -x tests/test_task019_scalar_alpha_jet_bundle.py -v

# Full suite
pytest -x tests/

# Source audits (existing + new pattern from Task 018)
pytest -x tests/test_task010a_layer_manifest_machine_readable.py
pytest -x tests/test_task010b_export_drift.py
pytest -x tests/test_task010b_manifest_completeness.py
pytest -x tests/test_task010c_no_unregistered_operations.py
pytest -x tests/test_task010c_lineage_terminates_in_primitive.py
pytest -x tests/test_task010c_no_chain_cycles.py
pytest -x tests/test_task001_source_purity.py
```

## Non-Goals

This task explicitly does NOT (Codex's loud list):

- **No default h-grid.** h_values is required and caller-supplied.
- **No parser.** ScalarAlphaJetBundle takes a callable, not an expression
  string. Symbolic parsing is not in scope.
- **No multidimensional probing.** point is a scalar (float), not a
  vector. Direction-aware probing in higher dimensions is for a later
  multi-dim JetBundle, when there's a consumer for it.
- **No HyperDual port.** Autodiff via dual numbers / hyperdual is its own
  primitive subsystem, not in scope.
- **No Hessian, rank, signature.** Second-derivative observation, rank
  classification, signature classification — all out of scope. v1 carries
  α evidence only.
- **No shape operator.** Geometric shape decomposition is multi-dim
  territory.
- **No curvature decomposition.** Same.
- **No local quadratic model generation.** That's a downstream
  LocalModelProvider candidate primitive, scheduled (or not) after Task 019
  reveals patterns.
- **No Newton/Halley/candidate-step logic.** ScalarAlphaJetBundle measures;
  it does not propose steps. Solver work is forward.
- **No branch fingerprint, refinery, or history dependency.** Layer 2+
  V3-shape modules are deferred-consumer reference, not authoritative
  substrate.
- **No assumption that AlphaProbe succeeds.** ScalarAlphaJetBundle must
  produce a typed result for every legal input, including all AlphaProbe
  refusal cases.
- **No raising on AlphaProbe refusal; propagate through typed mapping.**
  AlphaProbe refusal is a typed observation, not an exception.
- **No `scalar_jet_constant` stratum.** Constant detection doesn't fall
  cleanly out of AlphaProbe's mechanics (zero vs nonzero constants route
  through different downstream strata). Constancy detection, if needed,
  is a separate primitive.
- **No nested-window drift / BIC.** AlphaProbe doesn't expose this yet;
  ScalarAlphaJetBundle won't add it.
- **No multi-precision execution.** precision is metadata only.
- **No re-classification of α regimes.** ScalarAlphaJetBundle MUST use the
  explicit AlphaProbeStatus → ScalarAlphaJetBundleStatus mapping. It must
  NOT re-examine observed_alpha to reclassify (e.g., decide that
  ALPHA_REGULAR_INTEGER should actually be FRACTIONAL_BRANCH based on
  the value). Inherit AlphaProbe's classification honestly.

## Completion Report

Generate `Build_Docs/Reports/task019_summary.md` with:

- Number of tests added (target ~22)
- Full suite count (must be 319 + new)
- Sample serialized output for a SCALAR_JET_REGULAR_INTEGER_ALPHA result
- Sample serialized output for a SCALAR_JET_ALPHA_CANCELLATION_DOMINATED result
- Each implementable stratum demonstrated with one example
  (note: SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY may be unreachable via
  ScalarAlphaJetBundle's local probe construction since g_local(h) → 0
  at h=0 for finite f(x₀); document this in the summary if confirmed
  during implementation)
- The Task 018 α-1 validation re-run THROUGH ScalarAlphaJetBundle at
  x₀ = 0 for α ∈ {0.5, 1.5, 2.0, 3.0}: observed_alpha, JetBundle status,
  derivative_at_point, derivative_h
- Confirmation that distinct x₀ produces distinct embedded AlphaProbe
  trace_ids (the discipline test that x₀ enters the probe identity)
- Confirmation that JetBundle parents tuple is exactly (alpha_probe_trace_id,)
  and lineage walks transitively to all transfers and the slope
- Confirmation that derivative_at_point matches an independent
  typed_finite_difference call for the same h
- Honest limits: no multi-dim, no Hessian, no constant detection,
  NEGATIVE_ALPHA_SINGULARITY stratum may be unreachable for local probes,
  no multi-precision, no nested-window drift

## Acceptance Criteria

1. `ScalarAlphaJetBundleStatus` enum exists in `core/status.py` with nine strata.
2. `ScalarAlphaJetBundleStatus` is added to `StatusCode` union.
3. New module `src/lloyd_v4/primitives/scalar_alpha_jet_bundle.py` exists
   with `ScalarAlphaJetBundleObservation` value type, both protocols, and
   the public `scalar_alpha_jet_bundle` function.
4. `primitives/__init__.py` exports the new symbols.
5. `layer_manifest.json` and `LAYER_MANIFEST.md` declare the new entries.
   `scalar_alpha_jet_bundle` is listed in `calibrated_primitive_operations`.
6. The explicit AlphaProbeStatus → ScalarAlphaJetBundleStatus mapping is
   implemented per the table in Algorithm step 8.
7. All reachable strata are produced by appropriately-constructed inputs
   and verified by tests. (NEGATIVE_ALPHA_SINGULARITY may be unreachable
   via ScalarAlphaJetBundle's local-probe construction; if so, document
   the stratum as inherited-from-AlphaProbe but structurally unreachable
   from this primitive.)
8. The α-1 validation re-runs through ScalarAlphaJetBundle at x₀=0 for
   α ∈ {0.5, 1.5, 2.0, 3.0} with observed_alpha within 1e-2 of α.
9. Trace_id uniqueness tests pass: distinct x₀ → distinct trace_ids;
   identical inputs → identical trace_ids; distinct x₀ → distinct
   embedded AlphaProbe trace_ids.
10. Discipline test: derivative_at_point equals the transfer value from
    an independent typed_finite_difference call at the same (g_local, h,
    eta*h, embedded_function_label).
11. Discipline test: AlphaProbe refusal propagates as JetBundle typed
    refusal, never raises.
12. parents tuple contains exactly the embedded AlphaProbe trace_id (one entry).
13. Serialization round-trip works for observation and refusal strata.
14. Consumer protocol validation passes for the three accepted observation
    strata and refuses everything else.
15. All existing 319 tests continue to pass.
16. Source-purity audits return no unintentional matches.
17. `tests/test_task010c_*` audits pass; new operation is registered;
    lineage terminates in calibrated primitives.
18. Completion report at `Build_Docs/Reports/task019_summary.md` is written.

## Discipline Notes

### Local probe construction note

The local probe `g_local(h) = f(x₀+h) - f(x₀)` has the property that
`g_local(h) → 0` as `h → 0` for any finite-valued f. This means the
local probe's α observation reflects the leading-order Taylor behavior
of f at x₀:

- f smooth, f'(x₀) ≠ 0 → α = 1 (linear local behavior)
- f smooth, f'(x₀) = 0, f''(x₀) ≠ 0 → α = 2 (quadratic local behavior)
- f has a fractional-power branch at x₀ → α matches the branch exponent
- f is constant near x₀ → all g_local(h) = 0 → AlphaProbe cancellation-dominated

A consequence: **SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY may be unreachable**
through ScalarAlphaJetBundle's local-probe construction, because the
local probe always tends to 0 at h=0. The stratum is preserved in the
enum because the explicit AlphaProbe → JetBundle mapping declares it;
whether it's reachable in practice is an empirical question for the
completion report. If unreachable, document it.

### Readiness notes for forward tasks

- **Task 020+** (forward, not in scope): may include LocalModelProvider
  (composing JetBundle with derivative evidence into a local quadratic
  step model), or may add a separate `typed_local_derivative` primitive
  if the convenience derivative field in ScalarAlphaJetBundle proves
  insufficient. **Do not draft until Task 019 lands and its typed shape
  is inspected.**
- **Task 021** (forward, not in scope): AlphaProjectionSolver MVP
  composing projection admissibility with JetBundle α-stratum dispatch
  per the two-phase + tie-refusal acceptance law recorded in Task 018's
  discipline notes. **Do not draft until LocalModelProvider patterns
  are known.**
- The six missing V4-plan Layer 1 primitives (signed_difference,
  norm_state, stratified_sqrt, spectral_gap_state, projector_state,
  constraint_zero_state) are likely real dependencies during Task 020+
  (e.g., signed_difference for residual observation, stratified_sqrt
  for fractional-α step construction in the solver). Their schedule
  should be revisited after Task 019 lands.

### V3-shape Layer 2+ stance (unchanged)

Per the drift audit:

- `metrology`: candidate substrate (may be rebuilt later)
- `branch`: reference only
- `refinery`: reference only
- `history`: candidate substrate
- `solver`: reference only

ScalarAlphaJetBundle MUST NOT depend on any Layer 2+ V3-shape module.

### Solver acceptance law (forward reference, not in scope)

For the future solver, ScalarAlphaJetBundle evidence enters Phase 1
admissibility:

- The JetBundle's `selectable` and `advanceable` validity fields
  determine whether the JetBundle is admissible at all.
- The JetBundle's status determines which candidate generators are
  compatible (e.g., a sqrt-shaped step generator is compatible with
  SCALAR_JET_FRACTIONAL_ALPHA_BRANCH at α≈0.5; a linear-step generator
  is compatible with SCALAR_JET_REGULAR_INTEGER_ALPHA at α=1).
- Residual decrease cannot make an inadmissible JetBundle admissible.

This is recorded for awareness only; Task 019 implements the
measurement, not the dispatch.
