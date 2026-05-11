# Task 021 — SingularAlphaJetBundle Primitive

## Repository

`/mnt/fast/Lloyd_Engine_V4`

V3 is reference-only (Axiom 10). V1 / OG engine are also reference-only.
Layer 2+ artifacts (metrology, branch, refinery, history, solver) are
V3-shaped deferred-consumer first-drafts and MUST NOT shape this task.
Do not cite them as evidence; do not coordinate fixes with them; do not
import from them. This task is at Layer 1 (primitives) and depends only
on Layer 0 (core) and the already-built Layer 1 primitives.

## Current Verified Baseline

- 349 tests passing (`pytest -x tests/`) as of Task 020 completion.
- Calibrated primitive operations: `typed_collection`, `typed_value`,
  `projective_ratio`, `stratified_quadratic_roots`,
  `typed_finite_difference`, `directional_alpha_probe`,
  `scalar_alpha_jet_bundle`.
- Internal operations: `projective_ratio.scalarize`,
  `stratified_quadratic_roots.select`, `typed_log_log_slope`.
- Status families at primitives: `CollectionStatus`, `ValueStatus`,
  `ProjectiveRatioStatus`, `QuadraticRootStatus`, `TransferStatus`,
  `SlopeStatus`, `AlphaProbeStatus`, `ScalarAlphaJetBundleStatus`.
- `_precision_floor("raw_python")` returns `2.0**-52` with a documented
  derivation as `2u` (worst-case forward-difference cancellation
  threshold). SingularAlphaJetBundle inherits this floor unchanged via
  AlphaProbe → typed_finite_difference.

## Task Goal

Add the fifth capability primitive at Layer 1:
`singular_alpha_jet_bundle`.

This primitive is the **sibling** of `scalar_alpha_jet_bundle`. Where the
scalar bundle constructs the local-additive probe
`g_local(h) = f(x₀+h) - f(x₀)` (which can only observe α ≥ 0 because
g_local → 0 as h → 0), the singular bundle constructs the
**singular-direct probe**
`g_singular(h) = f(x₀ + h)` (no subtraction). The singular-direct
construction naturally reaches **negative α**, which the local-additive
probe cannot structurally produce. The two primitives together cover
the regularity channel of local α observation; their composition at
L1.5/L2 (a future task) will produce the joint dual-channel object.

The bundle delegates α measurement to Task 018's
`directional_alpha_probe` via the singular-direct probe, mirrors
AlphaProbe lineage, and emits a typed result.

**Scope fence.** This is `SingularAlphaJetBundle`, sibling to
`ScalarAlphaJetBundle`. It is not the joint dual-channel composer
(deferred). It does not evaluate `f(x₀)` (deferred to whatever future
consumer needs that observation). It is not a singularity classifier
beyond what AlphaProbe natively produces. It is not a curvature object,
shape operator, or solver step generator.

## Source Labelling

- **(V4-surface evidence)** Task 019 established `ScalarAlphaJetBundle`
  as the local-additive probe primitive. The
  `SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY` stratum in that enum is
  structurally unreachable from `g_local` because `g_local(h) → 0`
  mechanically as `h → 0`. The negative-α stratum exists in the enum
  for explicit 1:1 mapping with AlphaProbe but is documented as
  unreachable through local-additive construction.

- **(V4-surface evidence)** The architecture document
  `Build_Docs/Architecture/V4_dual_probe_design_and_reference_hygiene.md`
  (or whichever path it landed at — Codex: verify) commits the project
  to the three-layer architecture: L1 sibling primitives,
  L1.5/L2 typed joint composition (future), L3 curvature on the implied
  joint surface (future, consumer-driven). This task implements the
  second L1 sibling.

- **(Theorem-derived)** For `g_singular(h) = f(x₀+h)`:
  - If `f(x₀+h) ≈ c·h^α` as `h → 0+` with `α < 0`, the function blows
    up at x₀. AlphaProbe observes `α < 0` and emits
    `ALPHA_NEGATIVE_SINGULARITY`.
  - If `α > 0` integer, f has a regular zero of integer order at x₀.
  - If `α > 0` fractional, f has a fractional-power branch zero at x₀.
  - If f is regular and nonzero at x₀, the log-log slope tends to 0
    and observed_alpha tends to 1 (typically classified as
    `ALPHA_REGULAR_INTEGER` if no declared model rejects it).
  - The α-1 transfer law from Theorem 1 of
    `transfer_function_exponent_family_v2.pdf` applies unchanged.
    AlphaProbe handles the α recovery; this bundle composes it.

- **(Architectural)** The construction `g_singular(h) = f(x₀+h)` does
  NOT require `f(x₀)` to be finite. x₀ may be exactly at the singularity.
  This is the substrate fact that makes the singular bundle's domain
  complement to the scalar bundle's: the scalar bundle requires f(x₀)
  finite; the singular bundle does not.

## Design Principles

- **Sibling, not extension (Axiom 12 layer discipline).** This task adds
  a sibling primitive at L1, NOT an additional mode on
  ScalarAlphaJetBundle and NOT a composer. Each bundle has one probe
  construction; the joint object lives one layer up and is a separate
  task.

- **Construction defines the primitive.** The probe construction is
  `g_singular(h) = f(x₀+h)`. No subtraction. No `f(x₀)` baseline. The
  primitive does not evaluate f at x₀ at all.

- **All AlphaProbe strata are reachable.** Unlike ScalarAlphaJetBundle,
  where `NEGATIVE_SINGULARITY` is structurally unreachable from the
  construction, the singular bundle can reach every AlphaProbe stratum.
  `SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY` is the primary target case
  and has a canonical test fixture (`f(x) = 1/x` at `x₀ = 0`).

- **Composition, not reimplementation.** AlphaProbe is the α primitive;
  this task composes it. SingularAlphaJetBundle MUST NOT reimplement
  slope fitting, transfer computation, or stratum classification logic
  that already exists in AlphaProbe or its dependencies.

- **h-grid is caller-supplied measurement policy (Axiom 3).** No default
  grid. h_values must all be finite and strictly positive — the bundle
  never evaluates f at exactly x₀.

- **Typed refusal propagation, never raise on substrate observation.**
  SingularAlphaJetBundle produces a typed result for every legal input,
  including all AlphaProbe refusal cases. The embedded AlphaProbe
  refusing is not an exception; it is a typed observation that the
  bundle reflects through its own stratum.

- **No derivative convenience field.** Unlike ScalarAlphaJetBundle,
  which surfaces a derivative-at-point as a convenience for downstream
  step construction, the singular bundle has no such field. The
  derivative-at-point concept does not apply at singularities, and for
  regular-zero cases it is the scalar bundle's job. Adding a derivative
  field to the singular bundle would conflate roles.

- **No f(x₀) evaluation.** The bundle does not evaluate f at x₀ for any
  reason. If a future consumer (e.g., the joint composer) needs to know
  whether f(x₀) is finite, raises, or returns nonfinite, that consumer
  evaluates f(x₀) itself. Adding that here is consumer-pull design.

- **Lineage discipline.** The bundle preserves AlphaProbe's trace_id as
  its only parent. The lineage walk from a bundle result reaches every
  underlying typed observation transitively through AlphaProbe.

## Primitive-Sufficiency Gate

| Concept used | Provided by | Location |
|---|---|---|
| `TypedResult`, `Validity`, `Conditioning`, `Provenance` | core | `core/*.py` |
| `ProducerProtocol`, `ConsumerProtocol`, `validate_protocol` | core | `core/protocols.py` |
| `ProtocolStatus`, `ConditioningStatus` | core | `core/status.py` |
| `ProtocolViolationError` | core | `core/errors.py` |
| `AlphaProbeResult`, `AlphaProbeStatus`, `directional_alpha_probe`, `DeclaredAlphaModel` | primitives | `directional_alpha_probe.py` |
| Pattern: calibrated primitive composing existing primitives internally | primitives | `directional_alpha_probe`, `scalar_alpha_jet_bundle` precedent |
| Pattern: typed refusal propagation via explicit AlphaProbeStatus → bundle-status mapping | primitives | `scalar_alpha_jet_bundle` (mirror with different reachability) |

Sufficiency gate **passes**. AlphaProbe is the load-bearing dependency,
identical to `scalar_alpha_jet_bundle`'s. No new substrate concepts.

## Required Deliverables

### 1. New status family in `src/lloyd_v4/core/status.py`

```python
class SingularAlphaJetBundleStatus(StrEnum):
    SINGULAR_JET_REGULAR_INTEGER_ALPHA = "singular_jet_regular_integer_alpha"
    SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH = "singular_jet_fractional_alpha_branch"
    SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY = "singular_jet_negative_alpha_singularity"
    SINGULAR_JET_ALPHA_MODEL_REFUSED = "singular_jet_alpha_model_refused"
    SINGULAR_JET_ALPHA_CANCELLATION_DOMINATED = "singular_jet_alpha_cancellation_dominated"
    SINGULAR_JET_ALPHA_INDETERMINATE = "singular_jet_alpha_indeterminate"
    SINGULAR_JET_DOMAIN_REFUSED = "singular_jet_domain_refused"
    SINGULAR_JET_NONFINITE = "singular_jet_nonfinite"
    SINGULAR_JET_PROTOCOL_REFUSED = "singular_jet_protocol_refused"
```

Add `SingularAlphaJetBundleStatus` to the `StatusCode` union.

Stratum semantics:

- **SINGULAR_JET_REGULAR_INTEGER_ALPHA**: Embedded AlphaProbe returned
  `ALPHA_REGULAR_INTEGER`. f is regular at x₀ (no singularity);
  observed α is approximately a positive integer. Either f has a
  regular zero of integer order at x₀ (α = n for n ≥ 1) or f is regular
  and nonzero at x₀ (observed α ≈ 1 from constant-plus-linear behavior).

- **SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH**: Embedded AlphaProbe returned
  `ALPHA_FRACTIONAL_BRANCH`. f has fractional-power behavior at x₀
  (e.g., sqrt branch). Not a singularity in the blow-up sense, but a
  non-smooth zero / branch point.

- **SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY**: Embedded AlphaProbe
  returned `ALPHA_NEGATIVE_SINGULARITY`. **The namesake case.** f blows
  up at x₀ at rate `h^α` with α < 0. This is the singularity the
  primitive is designed to detect. Canonical fixture: `f(x) = 1/x` at
  `x₀ = 0`, observed α ≈ -1.

- **SINGULAR_JET_ALPHA_MODEL_REFUSED**: Embedded AlphaProbe returned
  `ALPHA_MODEL_AMBIGUOUS` OR `ALPHA_MODEL_NO_MATCH`. Caller's declared
  models were inconsistent with observation. The specific case
  (ambiguous vs no_match) is preserved in `value.alpha_status` and
  `value.matching_alpha_model_names`.

- **SINGULAR_JET_ALPHA_CANCELLATION_DOMINATED**: Embedded AlphaProbe
  returned `ALPHA_CANCELLATION_DOMINATED`. The chosen h-grid produced
  transfer observations below the precision floor for enough samples;
  local α cannot be observed at this precision.

- **SINGULAR_JET_ALPHA_INDETERMINATE**: Embedded AlphaProbe returned
  `ALPHA_INSUFFICIENT_DATA` OR `ALPHA_INDETERMINATE`. h-grid too short
  or degenerate.

- **SINGULAR_JET_DOMAIN_REFUSED**: Embedded AlphaProbe returned
  `ALPHA_DOMAIN_REFUSED`. f raised or returned non-numeric at every
  sampled `x₀ + h`. Note: f raising AT `x₀` itself is fine and does
  not trigger this stratum — the bundle never evaluates f at x₀.

- **SINGULAR_JET_NONFINITE**: Embedded AlphaProbe returned
  `ALPHA_NONFINITE`. Non-finite transfer or slope evidence blocked
  finite α observation.

- **SINGULAR_JET_PROTOCOL_REFUSED**: Reserved for recoverable downstream
  protocol refusal. No legal v1 input path emits it.

### 2. New module `src/lloyd_v4/primitives/singular_alpha_jet_bundle.py`

#### Module-level constants

```python
SINGULAR_ALPHA_JET_BUNDLE_SPACE = "SingularAlphaJetBundleObservation"

SINGULAR_ALPHA_JET_BUNDLE_STATUSES = frozenset({
    SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA,
    SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH,
    SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY,
    SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_MODEL_REFUSED,
    SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_CANCELLATION_DOMINATED,
    SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_INDETERMINATE,
    SingularAlphaJetBundleStatus.SINGULAR_JET_DOMAIN_REFUSED,
    SingularAlphaJetBundleStatus.SINGULAR_JET_NONFINITE,
    SingularAlphaJetBundleStatus.SINGULAR_JET_PROTOCOL_REFUSED,
})

SINGULAR_ALPHA_JET_BUNDLE_PROTOCOL = ProducerProtocol(
    name="singular_alpha_jet_bundle",
    emitted_statuses=SINGULAR_ALPHA_JET_BUNDLE_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=SingularAlphaJetBundleStatus,
)

SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="singular_alpha_jet_bundle_consumer",
    accepted_statuses=frozenset({
        SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA,
        SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH,
        SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY,
    }),
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
    status_family=SingularAlphaJetBundleStatus,
    refused_statuses=SINGULAR_ALPHA_JET_BUNDLE_STATUSES - frozenset({
        SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA,
        SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH,
        SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY,
    }),
)
```

The consumer protocol accepts the three "α observed" strata
(regular integer, fractional branch, negative singularity); everything
else is explicit refusal. Mirrors ScalarAlphaJetBundle's pattern,
adapted for the reachable stratum set.

#### Value type

```python
@dataclass(frozen=True, slots=True)
class SingularAlphaJetBundleObservation:
    # Point identity
    point: float
    probe_id: str                     # caller-supplied
    function_label: str               # caller-supplied
    h_values: tuple[float, ...]       # caller-supplied positive h-grid
    eta: float                        # passed through to AlphaProbe

    # Embedded AlphaProbe lineage
    alpha_probe_trace_id: str | None  # AlphaProbe trace_id; None if pre-probe refusal (none legal in v1)
    transfer_trace_ids: tuple[str, ...]  # mirrored from AlphaProbe.value for diagnostic ease
    slope_trace_id: str | None        # mirrored from AlphaProbe.value

    # α observation
    observed_slope: float | None
    observed_alpha: float | None
    alpha_status: AlphaProbeStatus | None  # embedded AlphaProbe's stratum

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
            "declared_alpha_models": [m.to_json_safe() for m in self.declared_alpha_models],
            "declared_alpha_band": to_json_safe(self.declared_alpha_band),
            "selected_alpha_model": self.selected_alpha_model,
            "matching_alpha_model_names": list(self.matching_alpha_model_names),
            "expression_path": self.expression_path,
        }


SingularAlphaJetBundleResult = TypedResult[
    SingularAlphaJetBundleObservation, SingularAlphaJetBundleStatus
]
```

**Compared to `ScalarAlphaJetBundleObservation`, this drops:**
`f_value`, `derivative_at_point`, `derivative_h`,
`derivative_transfer_trace_id`. The singular bundle does not evaluate
f at x₀ and does not surface a derivative.

#### Public function

```python
def singular_alpha_jet_bundle(
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
    expression_path: str = "singular_alpha_jet_singular_probe",
) -> SingularAlphaJetBundleResult:
    """Package singular-direct α evidence at the point x₀.

    Constructs g_singular(h) = func(x₀+h) internally and delegates α
    measurement to directional_alpha_probe. Does NOT evaluate func at
    x₀ itself; the singular-direct probe operates entirely on values
    at x₀+h for h > 0.

    Inputs:
        func: scalar callable. May raise or return non-numeric at any
              sampled x₀+h; handled as typed observations through
              AlphaProbe's refusal strata. Not called at x₀ itself.
        x0: the point at which singular α is measured. Must be finite.
              x₀ does not need to be a regular point of func; func may
              be undefined or singular exactly at x₀.
        h_values: explicit positive local probe grid. All values must
                  be finite and strictly positive. Caller's
                  measurement policy.
        probe_id: required caller-supplied label identifying this jet.
        function_label: required caller-supplied identifier for the
                  function being measured. The embedded AlphaProbe
                  receives a derived label that incorporates x₀.
        eta: relative delta multiplier passed to AlphaProbe.
        declared_alpha_models, declared_alpha_band: passed through to
                  AlphaProbe for model matching.
        precision, backend, device, measurement_resolution,
        expression_path: path metadata.

    Returns:
        TypedResult[SingularAlphaJetBundleObservation,
                    SingularAlphaJetBundleStatus].
        Always returns; never raises except for input-level
        ProtocolViolationError.
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
  (duplicate model names, non-finite alpha/band, etc.) — these
  propagate as raised exceptions from the underlying primitive

There is **no f(x₀) evaluation step** in this primitive. f raising at
x₀ is not a refusal mode for this bundle; the bundle never calls f(x₀).

#### Algorithm

```
1. Validate inputs (raise on bad inputs as above).

2. Construct the singular-direct observable. Use a closure that
   captures x₀ but does NOT evaluate f at x₀:

   def g_singular(h):
       return func(x0 + h)

3. Construct embedded probe identifiers that depend on x₀ AND make
   this bundle's embedded probe distinct from the scalar bundle's at
   the same point:

   embedded_probe_id = f"{probe_id}__x0_{x0!r}"
   embedded_function_label = f"{function_label}__singular_at_{x0!r}"

   The "singular_at" prefix (versus the scalar bundle's "local_at")
   ensures that the same caller (probe_id, function_label, x₀)
   produces distinct trace_ids across the two siblings. Verify by
   test.

4. Run the embedded AlphaProbe:

   alpha_probe_result = directional_alpha_probe(
       g_singular,
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

5. Extract α-evidence fields from alpha_probe_result.value:

   alpha_status = alpha_probe_result.status
   observed_slope = alpha_probe_result.value.observed_slope
   observed_alpha = alpha_probe_result.value.observed_alpha
   transfer_trace_ids = alpha_probe_result.value.transfer_trace_ids
   slope_trace_id = alpha_probe_result.value.slope_trace_id
   selected_alpha_model = alpha_probe_result.value.selected_alpha_model
   matching_alpha_model_names = alpha_probe_result.value.matching_alpha_model_names

6. Map AlphaProbeStatus -> SingularAlphaJetBundleStatus per the
   explicit table:

   ALPHA_REGULAR_INTEGER       -> SINGULAR_JET_REGULAR_INTEGER_ALPHA
   ALPHA_FRACTIONAL_BRANCH     -> SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH
   ALPHA_NEGATIVE_SINGULARITY  -> SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
   ALPHA_MODEL_AMBIGUOUS       -> SINGULAR_JET_ALPHA_MODEL_REFUSED
   ALPHA_MODEL_NO_MATCH        -> SINGULAR_JET_ALPHA_MODEL_REFUSED
   ALPHA_CANCELLATION_DOMINATED -> SINGULAR_JET_ALPHA_CANCELLATION_DOMINATED
   ALPHA_INSUFFICIENT_DATA     -> SINGULAR_JET_ALPHA_INDETERMINATE
   ALPHA_INDETERMINATE         -> SINGULAR_JET_ALPHA_INDETERMINATE
   ALPHA_DOMAIN_REFUSED        -> SINGULAR_JET_DOMAIN_REFUSED
   ALPHA_NONFINITE             -> SINGULAR_JET_NONFINITE

   Note that ALL AlphaProbe strata map cleanly; there is no
   structurally-unreachable stratum in this bundle (unlike the
   scalar bundle's NEGATIVE_ALPHA case).

7. Build SingularAlphaJetBundleObservation with all fields populated
   from alpha_probe_result and the input parameters.

   Build Provenance:

   provenance = Provenance(
       operation_id="singular_alpha_jet_bundle",
       expression_path=expression_path,
       precision=precision,
       backend=backend,
       device=device,
       measurement_resolution=measurement_resolution,
       inputs=(probe_id, function_label, x0, tuple(h_values), eta),
       parents=(alpha_probe_result.provenance.trace_id,),
   )

   Parents has exactly one entry (the AlphaProbe trace_id). The
   AlphaProbe transitively encodes every transfer and slope.

8. Return TypedResult with the mapped status, observation, validity,
   conditioning, provenance.
```

#### Validity per stratum

| Stratum | defined | finite | selectable | advanceable | observable |
|---|---|---|---|---|---|
| SINGULAR_JET_REGULAR_INTEGER_ALPHA | True | True | True | True | True |
| SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH | True | True | True | True | True |
| SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY | True | True | True | False | True |
| SINGULAR_JET_ALPHA_MODEL_REFUSED | True | True | False | False | True |
| SINGULAR_JET_ALPHA_CANCELLATION_DOMINATED | False | False | False | False | True |
| SINGULAR_JET_ALPHA_INDETERMINATE | False | False | False | False | True |
| SINGULAR_JET_DOMAIN_REFUSED | False | False | False | False | True |
| SINGULAR_JET_NONFINITE | True | False | False | False | True |
| SINGULAR_JET_PROTOCOL_REFUSED | False | False | False | False | True |

Identical to ScalarAlphaJetBundle's validity table. The negative-α
stratum carries `advanceable=False` because a singularity is a typed
geometric feature, not a step-target for a solver.

#### Conditioning per stratum

- **Three accepted strata**: `Conditioning(WELL_CONDITIONED, notes=(
  f"observed_alpha={alpha:.6g}",
  f"alpha_status={alpha_status.value}"))`.
- **Model refused**: `Conditioning(WARNING, notes=(
  f"alpha_status={alpha_status.value}",
  f"matching_models={list(matching_alpha_model_names)}"))`.
- **Other refusals**: `Conditioning(WARNING, notes=(
  f"alpha_status={alpha_status.value if alpha_status else 'pre_probe_refusal'}",
  f"reason={short_explanation}"))`.

### 3. Update `src/lloyd_v4/primitives/__init__.py`

```python
from .singular_alpha_jet_bundle import (
    SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL,
    SINGULAR_ALPHA_JET_BUNDLE_PROTOCOL,
    SINGULAR_ALPHA_JET_BUNDLE_SPACE,
    SingularAlphaJetBundleObservation,
    SingularAlphaJetBundleResult,
    singular_alpha_jet_bundle,
)
```

Add to `__all__`.

### 4. Update `Build_Docs/Architecture/layer_manifest.json`

In the `primitives` layer entry:

- Add `"SingularAlphaJetBundleStatus"` to `status_families`.
- Add `"SingularAlphaJetBundleObservation"`,
  `"SingularAlphaJetBundleResult"` to `value_types`.
- Add `"SINGULAR_ALPHA_JET_BUNDLE_PROTOCOL"`,
  `"SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL"` to `protocol_types`.
- Add `"SINGULAR_ALPHA_JET_BUNDLE_SPACE"` to `errors_and_utilities`.
- Add `"singular_alpha_jet_bundle"` to `operations` AND
  `calibrated_primitive_operations`.
- Update `all_exports` alphabetically.

### 5. Update `Build_Docs/Architecture/LAYER_MANIFEST.md`

Mirror the JSON changes.

### 6. Update `Build_Docs/Architecture/STATUS_CALCULUS.md`

Append a section on `SingularAlphaJetBundleStatus` covering the nine
strata and the explicit AlphaProbeStatus → SingularAlphaJetBundleStatus
mapping. Note that this mapping covers all AlphaProbe strata with no
structurally-unreachable cases.

### 7. New test file `tests/test_task021_singular_alpha_jet_bundle.py`

See Required Tests section.

## Required Tests

### Pre-task evidence

```python
def test_singular_alpha_jet_bundle_does_not_yet_exist() -> None:
    """Pre-task evidence; remove during implementation."""
    pass
```

### Stratum coverage

```python
def test_negative_alpha_singularity_stratum_reciprocal_at_origin():
    """f(x) = 1/x at x0 = 0. The canonical singularity case.

    This is the test that ScalarAlphaJetBundle structurally cannot
    reach: g_local would require f(0), which raises. The singular
    bundle never evaluates f(0); it samples f(0+h) for h > 0, where
    f(h) = 1/h ≈ h^{-1}. AlphaProbe should observe α ≈ -1 and emit
    ALPHA_NEGATIVE_SINGULARITY.
    """
    f = lambda x: 1.0 / x
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="reciprocal_jet",
        function_label="reciprocal",
        declared_alpha_band=0.01,
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert abs(result.value.observed_alpha - (-1.0)) < 1e-3
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY


def test_negative_alpha_singularity_inverse_square():
    """f(x) = 1/x^2 at x0 = 0. α should be -2."""
    f = lambda x: 1.0 / (x * x)
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="inv_sq_jet",
        function_label="inverse_square",
        declared_alpha_band=0.01,
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert abs(result.value.observed_alpha - (-2.0)) < 1e-2


def test_negative_alpha_singularity_inverse_sqrt():
    """f(x) = 1/sqrt(x) at x0 = 0. α should be -0.5."""
    import math as _m
    f = lambda x: 1.0 / _m.sqrt(x)
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="inv_sqrt_jet",
        function_label="inverse_sqrt",
        declared_alpha_band=0.01,
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert abs(result.value.observed_alpha - (-0.5)) < 1e-3


def test_regular_integer_alpha_stratum_linear_zero():
    """f(x) = x at x0 = 0. Regular zero of order 1; α should be 1."""
    f = lambda x: x
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="linear_jet",
        function_label="identity",
        declared_alpha_band=0.01,
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA
    assert abs(result.value.observed_alpha - 1.0) < 1e-3


def test_regular_integer_alpha_stratum_quadratic_zero():
    """f(x) = x^2 at x0 = 0. Regular zero of order 2; α should be 2."""
    f = lambda x: x * x
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="quad_jet",
        function_label="square",
        declared_alpha_band=0.01,
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA
    assert abs(result.value.observed_alpha - 2.0) < 1e-3


def test_fractional_alpha_branch_stratum_sqrt():
    """f(x) = sqrt(x) at x0 = 0. Fractional zero; α should be 0.5."""
    import math as _m
    f = lambda x: _m.sqrt(x)
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="sqrt_jet",
        function_label="sqrt",
        declared_alpha_band=0.01,
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH
    assert abs(result.value.observed_alpha - 0.5) < 1e-3


def test_alpha_model_refused_ambiguous():
    """Two declared models with overlapping bands both match observed α."""
    f = lambda x: 1.0 / x  # α = -1
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    models = (
        DeclaredAlphaModel("inverse", -1.0, 0.5),
        DeclaredAlphaModel("near_inverse", -1.2, 0.5),
    )
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="ambig_jet",
        function_label="reciprocal",
        declared_alpha_models=models,
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_MODEL_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS


def test_alpha_model_refused_no_match():
    """Declared model excludes observed α."""
    f = lambda x: 1.0 / x  # α = -1
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    models = (DeclaredAlphaModel("sqrt", 0.5, 0.05),)
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="no_match_jet",
        function_label="reciprocal",
        declared_alpha_models=models,
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_MODEL_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_MODEL_NO_MATCH


def test_cancellation_dominated_stratum_near_constant():
    """Near-constant callable: tiny perturbation rounds to zero."""
    f = lambda x: 1.0 + 1e-20 * x
    h_values = [1e-4, 1e-3, 1e-2, 1e-1]
    result = singular_alpha_jet_bundle(
        f, 1.0, h_values,
        probe_id="cancel_jet",
        function_label="near_constant",
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_CANCELLATION_DOMINATED


def test_domain_refused_stratum_f_raises_at_x0_plus_h():
    """f raises at every x0+h sampled. Note: f raising AT x0 is fine
    and does NOT cause domain refusal here — the bundle never evaluates
    f at x0."""
    def f(x):
        raise ValueError("never defined")
    h_values = [1e-4, 1e-3, 1e-2]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="raises",
        function_label="undefined",
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_DOMAIN_REFUSED
    assert result.value.alpha_status is AlphaProbeStatus.ALPHA_DOMAIN_REFUSED


def test_f_raises_at_x0_but_singular_observable_passes():
    """The diagnostic case: f raises at x0 itself, but f(x0+h) for
    h > 0 is well-defined and shows clean singular behavior. The
    bundle should produce a clean NEGATIVE_ALPHA_SINGULARITY result —
    proving that the bundle does not evaluate f at x0."""
    def f(x):
        if x == 0.0:
            raise ZeroDivisionError("f undefined at exactly zero")
        return 1.0 / x
    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="x0_raises_h_works",
        function_label="reciprocal_with_explicit_zero_guard",
        declared_alpha_band=0.01,
    )
    # Even though f(0) would raise, the bundle never calls f(0).
    # It samples f(h) for h > 0, where f(h) = 1/h. Should classify as
    # negative-α singularity.
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    assert abs(result.value.observed_alpha - (-1.0)) < 1e-3


def test_nonfinite_stratum_f_returns_inf():
    """f returns inf at sampled h values."""
    f = lambda x: float("inf")
    h_values = [1e-4, 1e-3, 1e-2]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="inf_jet",
        function_label="constant_inf",
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NONFINITE


def test_indeterminate_stratum_insufficient_h_values():
    """Only two h values."""
    f = lambda x: 1.0 / x
    h_values = [1e-3, 1e-2]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="few",
        function_label="reciprocal",
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_INDETERMINATE


def test_indeterminate_stratum_repeated_h():
    """All identical h values."""
    f = lambda x: 1.0 / x
    h_values = [1e-3, 1e-3, 1e-3, 1e-3]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="degen",
        function_label="reciprocal",
    )
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_INDETERMINATE
```

### Negative-α validation table

```python
def test_negative_alpha_recovery_across_exponents():
    """Validation across the negative-α regime that ScalarAlphaJetBundle
    structurally cannot reach.

    Mirrors the α-1 validation in Task 019 but on the negative side.
    """
    import math as _m

    cases = [
        # (func, expected_alpha, label)
        (lambda x: 1.0 / x, -1.0, "reciprocal"),
        (lambda x: 1.0 / (x * x), -2.0, "inverse_square"),
        (lambda x: 1.0 / (x ** 3), -3.0, "inverse_cube"),
        (lambda x: 1.0 / _m.sqrt(x), -0.5, "inverse_sqrt"),
    ]

    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    for func, expected_alpha, label in cases:
        result = singular_alpha_jet_bundle(
            func, 0.0, h_values,
            probe_id=f"validate_{label}",
            function_label=label,
            declared_alpha_band=0.05,
        )
        assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY, \
            f"{label}: expected NEGATIVE_ALPHA_SINGULARITY, got {result.status}"
        assert abs(result.value.observed_alpha - expected_alpha) < 1e-2, \
            f"{label}: expected α≈{expected_alpha}, got {result.value.observed_alpha}"
```

### Input validation

```python
def test_empty_h_values_raises():
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [],
            probe_id="x", function_label="x")


def test_non_positive_h_raises():
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [-1e-3, 1e-3, 1e-2],
            probe_id="x", function_label="x")


def test_zero_in_h_values_raises():
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [0.0, 1e-3, 1e-2],
            probe_id="x", function_label="x")


def test_non_finite_x0_raises():
    import math as _m
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, _m.inf, [1e-3, 1e-2],
            probe_id="x", function_label="x")


def test_empty_probe_id_raises():
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(lambda x: 1.0 / x, 0.0, [1e-3, 1e-2, 1e-1],
            probe_id="", function_label="x")


def test_non_callable_func_raises():
    with pytest.raises(ProtocolViolationError):
        singular_alpha_jet_bundle(42, 0.0, [1e-3, 1e-2],
            probe_id="x", function_label="x")
```

### Discipline: bundle does not evaluate f at x₀

```python
def test_bundle_never_evaluates_f_at_x0():
    """Audit-strength test: instrument func to record every call, and
    verify that x0 itself is never in the call list."""
    calls = []
    def f(x):
        calls.append(x)
        if x == 0.0:
            raise AssertionError("bundle must not evaluate f at x0=0")
        return 1.0 / x

    h_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="audit",
        function_label="reciprocal_audited",
        declared_alpha_band=0.01,
    )
    # Bundle should succeed without assertion error
    assert result.status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    # And x0 = 0.0 should not appear in the call list
    assert 0.0 not in calls, f"bundle evaluated f at x0=0; calls were {calls}"


def test_observation_has_no_f_value_or_derivative_fields():
    """Discipline check: SingularAlphaJetBundleObservation must not
    have f_value, derivative_at_point, derivative_h, or
    derivative_transfer_trace_id fields. Those belong to
    ScalarAlphaJetBundle."""
    import dataclasses

    f = lambda x: 1.0 / x
    result = singular_alpha_jet_bundle(
        f, 0.0, [1e-3, 1e-2, 1e-1],
        probe_id="x", function_label="x")
    field_names = {field.name for field in dataclasses.fields(result.value)}
    forbidden = {"f_value", "derivative_at_point", "derivative_h",
                 "derivative_transfer_trace_id"}
    assert field_names.isdisjoint(forbidden), \
        f"forbidden fields present: {field_names & forbidden}"
```

### Provenance and identity

```python
def test_inputs_carry_probe_function_label_x0_h_eta():
    f = lambda x: 1.0 / x
    h_values = (1e-3, 1e-2, 1e-1)
    result = singular_alpha_jet_bundle(
        f, 0.0, list(h_values),
        probe_id="recip", function_label="reciprocal",
        eta=1e-6,
    )
    assert result.provenance.inputs == ("recip", "reciprocal", 0.0, h_values, 1e-6)


def test_parents_contains_only_alpha_probe_trace():
    f = lambda x: 1.0 / x
    h_values = [10**(-i) for i in range(2, 8)]
    result = singular_alpha_jet_bundle(
        f, 0.0, h_values,
        probe_id="x", function_label="reciprocal",
        declared_alpha_band=0.01,
    )
    assert len(result.provenance.parents) == 1
    assert result.provenance.parents[0] == result.value.alpha_probe_trace_id


def test_distinct_x0_distinct_trace_ids():
    f = lambda x: 1.0 / x if x != 0 else 0.0  # define some baseline; x0 itself is the differentiator
    h_values = [1e-3, 1e-2, 1e-1]
    r1 = singular_alpha_jet_bundle(f, 0.5, h_values,
        probe_id="x", function_label="rec")
    r2 = singular_alpha_jet_bundle(f, 1.0, h_values,
        probe_id="x", function_label="rec")
    assert r1.provenance.trace_id != r2.provenance.trace_id


def test_distinct_x0_distinct_alpha_probe_trace_ids():
    f = lambda x: 1.0 / x if x != 0 else 0.0
    h_values = [1e-3, 1e-2, 1e-1]
    r1 = singular_alpha_jet_bundle(f, 0.5, h_values,
        probe_id="x", function_label="rec")
    r2 = singular_alpha_jet_bundle(f, 1.0, h_values,
        probe_id="x", function_label="rec")
    assert r1.value.alpha_probe_trace_id != r2.value.alpha_probe_trace_id


def test_sibling_bundles_at_same_x0_distinct_alpha_probe_trace_ids():
    """The most important provenance-distinctness test: the singular
    bundle and the scalar bundle at the same point with otherwise-
    identical inputs must produce DISTINCT AlphaProbe trace_ids,
    because their embedded probe constructions differ (local-additive
    vs singular-direct)."""
    from lloyd_v4.primitives import scalar_alpha_jet_bundle

    # Pick a function regular at x0 so both bundles produce a result
    f = lambda x: x * x  # f(1) = 1 finite; f(1+h) = (1+h)^2
    h_values = [1e-3, 1e-2, 1e-1]

    singular = singular_alpha_jet_bundle(
        f, 1.0, h_values,
        probe_id="shared", function_label="square",
    )
    scalar = scalar_alpha_jet_bundle(
        f, 1.0, h_values,
        probe_id="shared", function_label="square",
    )

    # Both should succeed
    assert singular.status in {
        SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA,
        SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH,
    }
    # AlphaProbe trace_ids must differ
    assert singular.value.alpha_probe_trace_id != scalar.value.alpha_probe_trace_id
    # Bundle trace_ids must differ
    assert singular.provenance.trace_id != scalar.provenance.trace_id


def test_identical_inputs_identical_trace_ids():
    f = lambda x: 1.0 / x
    h_values = [1e-3, 1e-2, 1e-1]
    r1 = singular_alpha_jet_bundle(f, 0.5, h_values,
        probe_id="x", function_label="rec")
    r2 = singular_alpha_jet_bundle(f, 0.5, h_values,
        probe_id="x", function_label="rec")
    assert r1.provenance.trace_id == r2.provenance.trace_id
    assert r1.value.alpha_probe_trace_id == r2.value.alpha_probe_trace_id


def test_provenance_records_path_metadata():
    f = lambda x: 1.0 / x
    result = singular_alpha_jet_bundle(
        f, 0.0, [1e-3, 1e-2, 1e-1],
        probe_id="x", function_label="rec")
    assert result.provenance.operation_id == "singular_alpha_jet_bundle"
    assert result.provenance.expression_path == "singular_alpha_jet_singular_probe"
    assert result.provenance.precision == "raw_python"
```

### Serialization

```python
def test_serialization_round_trip_negative_alpha():
    import json
    from lloyd_v4.core.serialization import to_json_safe

    f = lambda x: 1.0 / x
    result = singular_alpha_jet_bundle(
        f, 0.0, [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
        probe_id="x", function_label="rec",
        declared_alpha_band=0.05,
    )
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    decoded = json.loads(encoded)
    assert decoded["status"] == "singular_jet_negative_alpha_singularity"
    assert decoded["value"]["observed_alpha"] is not None
    assert decoded["value"]["alpha_status"] == "alpha_negative_singularity"
    assert "Infinity" not in encoded
    assert "NaN" not in encoded


def test_serialization_round_trip_refusal():
    import json
    from lloyd_v4.core.serialization import to_json_safe

    f = lambda x: 1.0 + 1e-20 * x
    result = singular_alpha_jet_bundle(
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
def test_consumer_protocol_accepts_negative_singularity():
    f = lambda x: 1.0 / x
    result = singular_alpha_jet_bundle(
        f, 0.0, [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
        probe_id="x", function_label="rec",
        declared_alpha_band=0.05,
    )
    check = validate_protocol(result, SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL)
    assert check.ok


def test_consumer_protocol_accepts_regular_integer():
    f = lambda x: x * x
    result = singular_alpha_jet_bundle(
        f, 0.0, [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
        probe_id="x", function_label="sq",
        declared_alpha_band=0.05,
    )
    check = validate_protocol(result, SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL)
    assert check.ok


def test_consumer_protocol_refuses_cancellation_dominated():
    f = lambda x: 1.0 + 1e-20 * x
    result = singular_alpha_jet_bundle(
        f, 1.0, [1e-3, 1e-2, 1e-1],
        probe_id="x", function_label="nc",
    )
    check = validate_protocol(result, SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL)
    assert not check.ok
```

## Required Commands

```bash
# Pre-task baseline
python -m pytest -x tests/ -q

# Verify the primitive does not yet exist
python -c "from lloyd_v4.primitives import singular_alpha_jet_bundle" 2>&1 || true

# Targeted test for this task
python -m pytest tests/test_task021_singular_alpha_jet_bundle.py -v

# Manifest/export/lineage audits
python -m pytest -x tests/test_task010a_layer_manifest_machine_readable.py \
                   tests/test_task010b_export_drift.py \
                   tests/test_task010b_manifest_completeness.py \
                   tests/test_task010c_no_unregistered_operations.py \
                   tests/test_task010c_lineage_terminates_in_primitive.py \
                   tests/test_task010c_no_chain_cycles.py

# Source-purity audits
python -m pytest -x tests/test_task001_source_purity.py \
                   tests/test_task009a_source_purity.py

# Full suite after implementation
python -m pytest -x tests/ -q

# Confirm no V3/V1 substrate contamination
rg "lloyd_v3|lloyd_v1|safe_mask|legacy_compat|clamp_min|epsilon|eps" \
   src/lloyd_v4/primitives/singular_alpha_jet_bundle.py -n

# Confirm no Layer 2+ imports
rg "from lloyd_v4\\.(metrology|branch|refinery|history|solver)" \
   src/lloyd_v4/primitives/singular_alpha_jet_bundle.py -n
```

Expected: full suite passes with 349 + ~25 new tests = ~374 passing.

## Non-Goals (loud and explicit)

- **Do NOT evaluate f at x₀.** The bundle never calls `func(x0)` for any
  reason. f raising at x₀ is not a refusal mode for this bundle.
- **Do NOT add a derivative convenience field.** No `derivative_at_point`,
  no `derivative_h`, no `derivative_transfer_trace_id`. Derivatives at
  singularities do not exist; derivatives at regular zeros are the
  scalar bundle's concern.
- **Do NOT add an f_value field.** That's the scalar bundle's surface.
- **Do NOT implement the joint dual-channel composer.** That is a future
  L1.5/L2 task. This task only adds the L1 sibling primitive.
- **Do NOT compute curvature, shape operator, or any geometric object
  beyond what AlphaProbe natively emits.** L3 territory; not now.
- **Do NOT implement a default h-grid.** h_values is a required
  positional argument; passing None or omitting it is a Python TypeError,
  which is fine.
- **Do NOT import from Layer 2+ modules** (metrology, branch, refinery,
  history, solver). They remain reference-only.
- **Do NOT touch `scalar_alpha_jet_bundle.py`** except to verify imports
  in `__init__.py`. The sibling is added alongside, not refactored.
- **Do NOT reimplement slope fitting, transfer computation, or stratum
  classification.** AlphaProbe owns those.
- **Do NOT reuse `ScalarAlphaJetBundleStatus` enum values.** New status
  family with the `SINGULAR_JET_` prefix.

## Completion Report

Create `Build_Docs/Reports/task021_summary.md` with:

- **Scope summary** (one paragraph).
- **Test counts.** Expected: pre 349, post ~374.
- **Files changed**, with one-line description per file.
- **Manifest and status updates** (list of added entries).
- **Sample serialized result** for the canonical case
  (`f(x) = 1/x` at x₀ = 0).
- **Negative-α validation table** showing observed_alpha for the
  validation suite (reciprocal, inverse_square, inverse_cube,
  inverse_sqrt).
- **Strata demonstrated** table mapping each test fixture to its
  resulting bundle status and AlphaProbe status.
- **Trace and lineage confirmation**:
  - distinct x₀ → distinct trace_ids
  - identical inputs → identical trace_ids
  - sibling bundles at same x₀ → distinct AlphaProbe trace_ids
    (this is the critical structural test)
- **Audit results** (manifest, export, lineage, source-purity).
- **Confirmation** that `scalar_alpha_jet_bundle` behavior is
  unchanged.

## Acceptance Criteria

- `singular_alpha_jet_bundle` importable from `lloyd_v4.primitives`.
- `SingularAlphaJetBundleStatus` added to `StatusCode` union and
  exported from `core/status.py`.
- All listed deliverables landed.
- All stratum-coverage tests pass.
- Negative-α validation across all four exponents
  (-1, -2, -3, -0.5) recovers observed_alpha within 1e-2 of expected.
- The canonical `1/x` at `x₀ = 0` test passes with
  `SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY`. This is the existence
  proof that V4 can now reach the negative-α stratum.
- The discipline test confirming no f(x₀) evaluation passes.
- The discipline test confirming no f_value / derivative_* fields
  passes.
- Sibling bundles at the same x₀ produce distinct AlphaProbe trace_ids.
- Full suite passes (349 + ~25 new = ~374 passing).
- All manifest/export/lineage audits pass.
- Source-purity audits pass without further narrowing
  (the new file should be clean from the start).
- No changes to `scalar_alpha_jet_bundle.py` (other than imports).

## Discipline Notes

- **Reachability is the architectural point.** The whole reason this
  primitive exists is that
  `SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY` is structurally unreachable
  from the local-additive probe. The canonical test
  (`f(x) = 1/x` at `x₀ = 0`) is the existence proof that V4 can now
  reach it. That test failing — or only passing with declared
  models — would mean the sibling primitive is not doing what it
  needs to.

- **Sibling, not extension.** The temptation to merge the two bundles
  into a single primitive with a mode switch must be resisted. Two
  primitives with one probe construction each is the correct shape.
  Mode switches conflate roles and make the architectural distinction
  invisible to consumers.

- **Forward reference (joint composer, candidate next task at L1.5/L2).**
  The joint dual-channel object will consume both
  `ScalarAlphaJetBundleResult` and `SingularAlphaJetBundleResult` and
  emit a typed joint observation with both arms' lineage preserved.
  That is a future task and must not shape this one. The sibling
  primitives are sovereign in their own probe domains; the joint
  object is composer-only.

- **Forward reference (L3 curvature consumer).** Any curvature work on
  the implied joint surface F(h, u, v) = 0 is L3 consumer territory
  and not part of this task. Axiom 11 (Epistemic Stance Only) forbids
  pre-loading curvature as substrate.

- **Layer 2+ remains reference-only.** Do not consult metrology,
  branch, refinery, history, or solver modules for evidence. The
  primitive derives entirely from Layer 0/1.

- **The precision floor inherited via Task 020.** SingularAlphaJetBundle
  uses `typed_finite_difference` transitively through
  `directional_alpha_probe`. The `2u = 2^-52` worst-case cancellation
  floor applies unchanged. Negative-α observations approaching the
  precision floor will classify as
  `SINGULAR_JET_ALPHA_CANCELLATION_DOMINATED`, just as positive-α
  observations do in the scalar bundle. No special handling required.
