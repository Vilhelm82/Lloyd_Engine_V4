# Task 018 — Directional AlphaProbe Primitive

## Repository

`/mnt/fast/Lloyd_Engine_V4`

V3 is reference-only (Axiom 10). V1 / OG engine are also reference-only.
Layer 2+ artifacts (metrology, branch, refinery, history, solver) are V3-shaped
deferred-consumer first-drafts and MUST NOT shape this task. Do not cite them
as evidence; do not coordinate fixes with them; do not import from them. This
task is at Layer 1 (primitives) and depends only on Layer 0 (core) and the
already-built Layer 1 primitives.

## Current Verified Baseline

- 296 tests passing (`pytest -x tests/`) as of Task 016 completion
- Layers: core, primitives, projection, plus deferred-consumer Layers 2/3
- Calibrated primitive operations: `typed_collection`, `typed_value`,
  `projective_ratio`, `stratified_quadratic_roots`, `typed_finite_difference`
- Internal operations: `projective_ratio.scalarize`,
  `stratified_quadratic_roots.select`, `typed_log_log_slope`
- Status families at primitives: `CollectionStatus`, `ValueStatus`,
  `ProjectiveRatioStatus`, `QuadraticRootStatus`, `TransferStatus`,
  `SlopeStatus`
- α-1 recovery validated on clean synthetic branches at raw_python precision
  for α ∈ {0.5, 1.5, 2.0, 3.0}, errors all below 1e-11
- Drift audit completed; V3-shape Layer 2+ confirmed deferred-consumer

## Task Goal

Add the third capability primitive at Layer 1: `directional_alpha_probe`.
This primitive turns α from a fitted-slope test result into a first-class
typed object — **Directional AlphaProbe evidence** — that the future solver
can dispatch on.

It samples a scalar callable along an explicit positive approach coordinate
grid `f → 0+`, constructs typed finite-difference transfer observations,
consumes typed log-log slope evidence, computes `observed_alpha = observed_slope + 1`
per the α-1 transfer law (Theorem 1 of
`transfer_function_exponent_family_revised.tex`), classifies the result into
a solver-relevant stratum, and emits the observation with full provenance
(probe identity, transfer parent traces, slope parent trace, cancellation
evidence, declared-model evidence).

After this task lands, α is an engine object, not a test result.

## Source labelling

- **(V4-surface)** Task 016's `typed_log_log_slope` recovers α-1 from a
  `typed_collection` of `TransferObservationResult` items, with R²=1.0 and
  errors ~10⁻¹² across α ∈ {0.5, 1.5, 2.0, 3.0}. But the result is fitted
  slope evidence over a caller-supplied observation set. It is not yet a
  typed object that says: *this α was measured along this probe, from these
  samples, under this precision path, with these transfer traces, with this
  cancellation status.* AlphaProbe provides that.
- **(theorem-derived, Theorem 1 of α-1 paper)** "If g has the controlled
  branch expansion `g(f) = g_0 + c·f^α·L(f)(1 + r(f))`, then
  `D log T_{δf}(f) → α-1` as `f → 0+`." The substrate's α-estimate is
  therefore `observed_log_log_slope + 1`. AlphaProbe applies this identity
  honestly and never invokes hidden corrections.
- **(Codex updated proposal)** AlphaProbe before JetBundle: α must be a
  typed object before JetBundle composes it with gradient/Hessian. AlphaProbe
  must depend only on certified Layer 1 primitives + projection; no Layer 2+
  V3-shape dependencies. No hidden closeness-to-integer rules; all bands
  declared explicitly. Status names carry solver-relevant strata.

## Design Principles

- **α as typed evidence, not naked number (Axiom 1).** The primitive's value
  carries probe identity, the sample grid, parent trace IDs for every
  transfer observation, the slope parent trace, observed counts at each
  transfer stratum, declared-model evidence, and the matched model name
  (if any). No scalar α floats free in the substrate.
- **Honest application of the α-1 transfer law.** `observed_alpha =
  observed_slope + 1`. No fudge factors, no integer snapping unless
  caller supplies a declared band for it.
- **Declared bands only (Axiom 3).** Any tolerance used in model matching
  is caller-supplied via `declared_alpha_band` or per-model `band` fields.
  No hidden closeness-to-integer thresholds. No magic snapping at α=2.
- **Refusal preserved as evidence.** Cancellation-dominated, domain-refused,
  and non-finite transfer observations are preserved with counts in the
  AlphaProbeValue and influence the stratum classification. They do not
  alter computed values. They do not participate in the slope fit.
- **Lineage discipline.** AlphaProbe never alters computed transfer values.
  It preserves transfer and slope parent trace IDs in `parents`. The
  audit machinery walking lineage from an AlphaProbe result reaches every
  underlying transfer observation and the slope estimate.
- **Geometric measurement primitive, not statistical wrapper (Axiom 1).**
  AlphaProbe observes one geometric feature: the leading-order asymptotic
  exponent of a function near a branch point at f=0. Strata classify
  geometric outcomes (regular integer branch, fractional branch, negative
  singularity, declared-model mismatch, refusal). Not a generic regression
  utility.

## Primitive-Sufficiency Gate

| Concept used | Provided by | Location |
|---|---|---|
| `TypedResult`, `Validity`, `Conditioning`, `Provenance` | core | `core/*.py` |
| `ProducerProtocol`, `ConsumerProtocol`, `validate_protocol` | core | `core/protocols.py` |
| `ProtocolStatus`, `ConditioningStatus` | core | `core/status.py` |
| `ProtocolViolationError` | core | `core/errors.py` |
| `TransferObservationResult`, `TransferStatus.TRANSFER_OBSERVED` etc. | primitives | `typed_finite_difference.py` |
| `LogLogSlopeResult`, `SlopeStatus` | primitives | `typed_log_log_slope.py` |
| `TypedCollectionResult` | primitives | `typed_collection.py` |
| `typed_finite_difference`, `typed_log_log_slope`, `typed_collection` operations | primitives | various |
| Pattern: calibrated primitive composing existing primitives internally | primitives | first such primitive — see notes below |

This primitive composes `typed_finite_difference` and `typed_log_log_slope`
internally. That's a new pattern at Layer 1 (other primitives have been
either leaf operations on raw inputs or transformations of single typed
inputs). The composition is legitimate because the produced result is a
fresh geometric observation — the asymptotic exponent — not a transformation
of any single input. The composing primitives' outputs become parents of
the AlphaProbe result; the AlphaProbe operation introduces new path
information (the probe identity and sample grid) into the substrate.

Sufficiency gate **passes**.

## Required Deliverables

### 1. New status family in `src/lloyd_v4/core/status.py`

```python
class AlphaProbeStatus(StrEnum):
    ALPHA_REGULAR_INTEGER = "alpha_regular_integer"
    ALPHA_FRACTIONAL_BRANCH = "alpha_fractional_branch"
    ALPHA_NEGATIVE_SINGULARITY = "alpha_negative_singularity"
    ALPHA_MODEL_AMBIGUOUS = "alpha_model_ambiguous"
    ALPHA_MODEL_NO_MATCH = "alpha_model_no_match"
    ALPHA_CANCELLATION_DOMINATED = "alpha_cancellation_dominated"
    ALPHA_INSUFFICIENT_DATA = "alpha_insufficient_data"
    ALPHA_DOMAIN_REFUSED = "alpha_domain_refused"
    ALPHA_NONFINITE = "alpha_nonfinite"
    ALPHA_INDETERMINATE = "alpha_indeterminate"
```

Add `AlphaProbeStatus` to the `StatusCode` union.

Stratum semantics:

- **ALPHA_REGULAR_INTEGER**: `observed_alpha` was computed cleanly (slope
  fit succeeded with ≥3 OBSERVED transfer points) and is within
  `declared_alpha_band` of a positive integer (typically 1, 2, 3). If
  `declared_alpha_models` was supplied, this stratum is emitted only when
  the matched model's α is integer.
- **ALPHA_FRACTIONAL_BRANCH**: `observed_alpha` was computed cleanly and is
  positive but not within `declared_alpha_band` of any integer (or matches
  a declared model whose α is non-integer). Examples: α = 0.5
  (square-root branch), α = 1/3 (cube-root branch), α = 1.5 (mixed).
- **ALPHA_NEGATIVE_SINGULARITY**: `observed_alpha` was computed cleanly
  and is strictly negative. Indicates a singularity at f=0 (function
  blowing up rather than vanishing).
- **ALPHA_MODEL_AMBIGUOUS**: `declared_alpha_models` was supplied, and
  `observed_alpha` matched more than one declared model within their
  declared bands. Caller's model set was inconsistent with observation.
- **ALPHA_MODEL_NO_MATCH**: `declared_alpha_models` was supplied (non-empty),
  and `observed_alpha` matched zero declared models. Observation falls
  outside the caller's expected model set.
- **ALPHA_CANCELLATION_DOMINATED**: After running typed_finite_difference
  at every f_value, the count of `TRANSFER_CANCELLATION_DOMINATED` results
  exceeded a caller-controlled threshold, leaving fewer than 3 OBSERVED
  results to fit. The substrate cannot estimate α at this precision floor
  for this f-range.
- **ALPHA_INSUFFICIENT_DATA**: Fewer than 3 `f_values` were provided, OR
  after filtering to OBSERVED transfers fewer than 3 remained for reasons
  other than cancellation (e.g., a mix of non-finite and domain-refused).
- **ALPHA_DOMAIN_REFUSED**: The observable callable raised or returned
  non-numeric for the majority of f-values, leaving fewer than 3 OBSERVED.
- **ALPHA_NONFINITE**: Slope fit succeeded numerically but produced a
  non-finite slope or intercept (extreme overflow during regression).
  Should be rare.
- **ALPHA_INDETERMINATE**: `typed_log_log_slope` returned
  `SLOPE_DEGENERATE_INPUT` (all log_f values identical), or the f-grid was
  pathological for slope estimation.

### 2. New module `src/lloyd_v4/primitives/directional_alpha_probe.py`

#### Module-level constants

```python
ALPHA_PROBE_SPACE = "AlphaProbeObservation"

ALPHA_PROBE_STATUSES = frozenset({
    AlphaProbeStatus.ALPHA_REGULAR_INTEGER,
    AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH,
    AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY,
    AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS,
    AlphaProbeStatus.ALPHA_MODEL_NO_MATCH,
    AlphaProbeStatus.ALPHA_CANCELLATION_DOMINATED,
    AlphaProbeStatus.ALPHA_INSUFFICIENT_DATA,
    AlphaProbeStatus.ALPHA_DOMAIN_REFUSED,
    AlphaProbeStatus.ALPHA_NONFINITE,
    AlphaProbeStatus.ALPHA_INDETERMINATE,
})

DIRECTIONAL_ALPHA_PROBE_PROTOCOL = ProducerProtocol(
    name="directional_alpha_probe",
    emitted_statuses=ALPHA_PROBE_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=AlphaProbeStatus,
)

ALPHA_PROBE_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="alpha_probe_consumer",
    accepted_statuses=frozenset({
        AlphaProbeStatus.ALPHA_REGULAR_INTEGER,
        AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH,
        AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY,
    }),
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
    status_family=AlphaProbeStatus,
    refused_statuses=ALPHA_PROBE_STATUSES - frozenset({
        AlphaProbeStatus.ALPHA_REGULAR_INTEGER,
        AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH,
        AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY,
    }),
)
```

The consumer protocol accepts the three strata that carry a usable α
observation. Model-match refusals and substrate refusals are explicitly
refused, forcing downstream consumers (future JetBundle, future solver) to
handle them deliberately rather than silently scalarize.

#### Value types

```python
@dataclass(frozen=True, slots=True)
class DeclaredAlphaModel:
    """Caller-declared α model for matching against observed α.

    band is the matching tolerance: observed_alpha matches this model iff
    abs(observed_alpha - alpha) <= band. Both alpha and band are declared
    metrology (Axiom 3); no hidden defaults applied by the primitive.
    """
    name: str
    alpha: float
    band: float

    def to_json_safe(self) -> dict[str, Any]:
        return {"name": self.name, "alpha": self.alpha, "band": self.band}


@dataclass(frozen=True, slots=True)
class AlphaProbeObservation:
    probe_id: str
    function_label: str
    f_values: tuple[float, ...]
    delta_values: tuple[float, ...]
    eta: float

    # Parent traces — preserve lineage without inflating provenance.parents
    transfer_trace_ids: tuple[str, ...]
    slope_trace_id: str | None

    # Slope-fit observation (None if not computed)
    observed_slope: float | None
    observed_alpha: float | None      # observed_slope + 1 per α-1 law
    r_squared: float | None
    standard_error: float | None
    log_f_min: float | None
    log_f_max: float | None

    # Transfer stratum counts
    n_input_observations: int
    n_observed: int
    n_cancellation_dominated: int
    n_non_finite: int
    n_domain_refused: int
    n_delta_indeterminate: int

    # Declared model evidence
    declared_alpha_models: tuple[DeclaredAlphaModel, ...]
    declared_alpha_band: float | None
    selected_alpha_model: str | None        # name of single matching model, if unique
    matching_alpha_model_names: tuple[str, ...]  # all matching model names

    expression_path: str

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe
        return {
            "probe_id": self.probe_id,
            "function_label": self.function_label,
            "f_values": list(self.f_values),
            "delta_values": list(self.delta_values),
            "eta": self.eta,
            "transfer_trace_ids": list(self.transfer_trace_ids),
            "slope_trace_id": self.slope_trace_id,
            "observed_slope": to_json_safe(self.observed_slope),
            "observed_alpha": to_json_safe(self.observed_alpha),
            "r_squared": to_json_safe(self.r_squared),
            "standard_error": to_json_safe(self.standard_error),
            "log_f_min": to_json_safe(self.log_f_min),
            "log_f_max": to_json_safe(self.log_f_max),
            "n_input_observations": self.n_input_observations,
            "n_observed": self.n_observed,
            "n_cancellation_dominated": self.n_cancellation_dominated,
            "n_non_finite": self.n_non_finite,
            "n_domain_refused": self.n_domain_refused,
            "n_delta_indeterminate": self.n_delta_indeterminate,
            "declared_alpha_models": [m.to_json_safe() for m in self.declared_alpha_models],
            "declared_alpha_band": to_json_safe(self.declared_alpha_band),
            "selected_alpha_model": self.selected_alpha_model,
            "matching_alpha_model_names": list(self.matching_alpha_model_names),
            "expression_path": self.expression_path,
        }


AlphaProbeResult = TypedResult[AlphaProbeObservation, AlphaProbeStatus]
```

#### Public function

```python
def directional_alpha_probe(
    observable: Callable[[float], float],
    f_values: Sequence[float],
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
    expression_path: str = "log_log_slope_fit",
) -> AlphaProbeResult:
    """Observe the local asymptotic exponent α along an approach grid f → 0+.

    Inputs:
        observable: scalar callable g(f). Same semantics as
                    typed_finite_difference's g_callable.
        f_values: explicit positive approach coordinate grid. All values must
                  be finite and strictly positive. Order does not matter for
                  the slope fit but is preserved in the value.
        probe_id: required caller-supplied label identifying this probe.
                  Enters Provenance.inputs so distinct probes produce
                  distinct trace_ids.
        function_label: passed through to typed_finite_difference for each
                  transfer observation's identity. Required for the same
                  reason as in typed_finite_difference.
        eta: relative delta multiplier. For each f_i, the perturbation is
             delta_i = eta * f_i. Must be finite and nonzero. Default 1e-6
             matches V3's PPS experiment convention.
        declared_alpha_models: optional caller-declared α models for matching.
                  If empty, regime-based classification uses declared_alpha_band.
                  If non-empty, model matching determines the stratum.
        declared_alpha_band: optional band for regime-based integer matching
                  when declared_alpha_models is empty. If None and models
                  are empty, no integer-snapping is performed and any
                  observed α with non-zero fractional part is classified
                  as ALPHA_FRACTIONAL_BRANCH. Per Axiom 3, this is declared
                  metrology; there is no hidden default.
        precision, backend, device, measurement_resolution, expression_path:
                  path metadata. Propagated to each transfer observation
                  and stored in this probe's Provenance.

    Returns:
        TypedResult[AlphaProbeObservation, AlphaProbeStatus]. Always returns;
        never raises except for input-level ProtocolViolationError.
    """
```

#### Input validation

Raise `ProtocolViolationError` BEFORE any TypedResult construction for:

- `observable` is not callable
- `f_values` is empty, OR contains any non-finite, non-positive value
- `eta` is not finite, OR is zero
- `probe_id` is not a non-empty string
- `function_label` is not a non-empty string
- Any item in `declared_alpha_models` has non-finite alpha or non-finite,
  non-positive band, or empty name
- `declared_alpha_band` is provided and is non-finite or non-positive
- `declared_alpha_models` contains duplicate model names

Empty `f_values`, non-positive f-values, zero eta — all hard refusals.
Insufficient observations after filtering are NOT hard refusals; they
are classified as ALPHA_INSUFFICIENT_DATA.

#### Algorithm

```
1. Validate inputs (raise on bad inputs as above).

2. For each f_i in f_values:
     delta_i = eta * f_i
     transfer_i = typed_finite_difference(
         observable, f_i, delta_i,
         function_label=function_label,
         precision=precision, backend=backend, device=device,
         measurement_resolution=measurement_resolution,
         expression_path="forward_difference",
     )
   Collect all transfer_i into transfers_tuple.

3. Count strata:
     n_observed = count where status == TRANSFER_OBSERVED
     n_cancellation_dominated = count where status == TRANSFER_CANCELLATION_DOMINATED
     n_non_finite = count where status == TRANSFER_NON_FINITE
     n_domain_refused = count where status == TRANSFER_DOMAIN_REFUSED
     n_delta_indeterminate = count where status == TRANSFER_DELTA_INDETERMINATE

4. If n_observed < 3:
   Classify refusal stratum by dominant failure mode:
     if n_cancellation_dominated >= (len - n_observed) // 2 + 1:
       → ALPHA_CANCELLATION_DOMINATED
     elif n_domain_refused >= (len - n_observed) // 2 + 1:
       → ALPHA_DOMAIN_REFUSED
     else:
       → ALPHA_INSUFFICIENT_DATA
   Return AlphaProbeObservation with slope/alpha/r2/se = None,
   slope_trace_id = None.

5. Construct typed_collection of transfers_tuple. Run typed_log_log_slope on it.
   Record slope_result.provenance.trace_id as slope_trace_id.

6. Handle slope_result strata:
   - SLOPE_OBSERVED: extract slope, intercept, r_squared, standard_error,
     log_f_min, log_f_max. Compute observed_alpha = observed_slope + 1.
     Continue to step 7 for classification.
   - SLOPE_INSUFFICIENT_DATA: should not occur (we checked n_observed >= 3),
     but if it does, return ALPHA_INSUFFICIENT_DATA.
   - SLOPE_DEGENERATE_INPUT: return ALPHA_INDETERMINATE
     (log_f values identical; can't fit slope).

7. Check observed_alpha is finite:
   - If not, return ALPHA_NONFINITE.

8. Classify observed_alpha:
   8a. If declared_alpha_models is non-empty:
       matching = [m.name for m in declared_alpha_models
                   if abs(observed_alpha - m.alpha) <= m.band]
       if len(matching) > 1:
         → ALPHA_MODEL_AMBIGUOUS (carry matching list)
       elif len(matching) == 0:
         → ALPHA_MODEL_NO_MATCH
       else:
         # Unique match. Determine regime from the matched model's α value.
         matched = next(m for m in declared_alpha_models if m.name == matching[0])
         if matched.alpha < 0:
           → ALPHA_NEGATIVE_SINGULARITY
         elif _is_close_to_positive_integer(matched.alpha, matched.band):
           → ALPHA_REGULAR_INTEGER
         else:
           → ALPHA_FRACTIONAL_BRANCH
         selected_alpha_model = matched.name
   8b. If declared_alpha_models is empty:
       if observed_alpha < 0:
         → ALPHA_NEGATIVE_SINGULARITY
       elif declared_alpha_band is not None and
            _is_close_to_positive_integer(observed_alpha, declared_alpha_band):
         → ALPHA_REGULAR_INTEGER
       else:
         → ALPHA_FRACTIONAL_BRANCH

9. Construct AlphaProbeObservation with all fields populated.
   Construct Provenance:
     operation_id = "directional_alpha_probe"
     expression_path = expression_path
     precision = precision
     inputs = (probe_id, function_label, tuple(f_values), eta)
     parents = tuple(t.provenance.trace_id for t in transfers_tuple) + \
               ((slope_trace_id,) if slope_trace_id is not None else ())
   Return TypedResult.
```

Helper:

```python
def _is_close_to_positive_integer(alpha: float, band: float) -> bool:
    """True iff alpha is within band of a positive integer >= 1.
    Per Axiom 3, band must be caller-supplied; no hidden defaults."""
    import math
    if alpha <= 0:
        return False
    nearest = round(alpha)
    if nearest < 1:
        return False
    return abs(alpha - nearest) <= band
```

#### Validity per stratum

| Stratum | defined | finite | selectable | advanceable | observable |
|---|---|---|---|---|---|
| ALPHA_REGULAR_INTEGER | True | True | True | True | True |
| ALPHA_FRACTIONAL_BRANCH | True | True | True | True | True |
| ALPHA_NEGATIVE_SINGULARITY | True | True | True | False | True |
| ALPHA_MODEL_AMBIGUOUS | True | True | False | False | True |
| ALPHA_MODEL_NO_MATCH | True | True | False | False | True |
| ALPHA_CANCELLATION_DOMINATED | False | False | False | False | True |
| ALPHA_INSUFFICIENT_DATA | False | False | False | False | True |
| ALPHA_DOMAIN_REFUSED | False | False | False | False | True |
| ALPHA_NONFINITE | True | False | False | False | True |
| ALPHA_INDETERMINATE | False | False | False | False | True |

Note: ALPHA_NEGATIVE_SINGULARITY is selectable (the observation IS valid)
but not advanceable by default (stepping into a singularity is not a
lawful default). The future solver decides via its acceptance protocol
whether to advance into a singularity.

#### Conditioning per stratum

- **Three accepted observation strata** (REGULAR_INTEGER, FRACTIONAL_BRANCH,
  NEGATIVE_SINGULARITY): `Conditioning(WELL_CONDITIONED, notes=(
  f"observed_alpha={alpha:.6g}", f"r_squared={r2:.6g}",
  f"standard_error={se:.3e}", f"n_observed={n_observed}/{n_input}"))`.
- **Model-match refusals** (AMBIGUOUS, NO_MATCH): `Conditioning(WARNING,
  notes=(f"observed_alpha={alpha:.6g}", f"matching_models={list_of_names}",
  f"declared_models={count}"))`.
- **Substrate refusals** (CANCELLATION_DOMINATED, INSUFFICIENT_DATA,
  DOMAIN_REFUSED, INDETERMINATE): `Conditioning(WARNING, notes=(
  f"n_observed={n_observed}", f"n_cancellation_dominated={n_cd}",
  f"n_domain_refused={n_dr}"))`.
- **ALPHA_NONFINITE**: `Conditioning(WARNING, notes=("slope_fit_overflow",
  f"observed_slope={raw_slope}"))`.

#### Provenance

```python
provenance = Provenance(
    operation_id="directional_alpha_probe",
    expression_path=expression_path,
    precision=precision,
    backend=backend,
    device=device,
    measurement_resolution=measurement_resolution,
    inputs=(probe_id, function_label, tuple(f_values), eta),
    parents=tuple(t.provenance.trace_id for t in transfers_tuple) + \
            ((slope_trace_id,) if slope_trace_id is not None else ()),
)
```

`inputs` carries probe identity and the sample grid. `parents` carries
every transfer observation's trace_id AND (if computed) the slope's
trace_id. The lineage walk from this AlphaProbeResult reaches every
underlying typed observation. For N=10 f-values, parents has 10 or 11
trace_ids — bounded and walkable.

The `observable` callable is NOT in inputs (cannot be canonicalized stably).
`function_label` is the callable's identity carrier.

### 3. Update `src/lloyd_v4/primitives/__init__.py`

```python
from .directional_alpha_probe import (
    ALPHA_PROBE_CONSUMER_PROTOCOL,
    ALPHA_PROBE_SPACE,
    DIRECTIONAL_ALPHA_PROBE_PROTOCOL,
    AlphaProbeObservation,
    AlphaProbeResult,
    DeclaredAlphaModel,
    directional_alpha_probe,
)
```

Add to `__all__`.

### 4. Update `Build_Docs/Architecture/layer_manifest.json`

In the `primitives` layer entry:

- Add `"AlphaProbeStatus"` to `status_families`
- Add `"AlphaProbeObservation"`, `"AlphaProbeResult"`, `"DeclaredAlphaModel"` to `value_types`
- Add `"DIRECTIONAL_ALPHA_PROBE_PROTOCOL"`, `"ALPHA_PROBE_CONSUMER_PROTOCOL"` to `protocol_types`
- Add `"ALPHA_PROBE_SPACE"` to `errors_and_utilities`
- Add `"directional_alpha_probe"` to `operations` AND `calibrated_primitive_operations`
  (it produces a fresh geometric observation; not an internal transformation)
- Update `all_exports` alphabetically

### 5. Update `Build_Docs/Architecture/LAYER_MANIFEST.md`

Mirror the JSON changes.

### 6. New test file `tests/test_task018_directional_alpha_probe.py`

See Required Tests section.

### 7. Update `Build_Docs/Architecture/STATUS_CALCULUS.md`

Append a section on `AlphaProbeStatus` covering the ten strata.

### 8. Cleanup items folded in

#### 8a. precision_floor documentation

Create `Build_Docs/Architecture/METROLOGY_PRINCIPLES.md` (or append to an
existing principles doc). Include the following block:

> ## precision_floor as finite-precision observability evidence
>
> The `_precision_floor` lookup in `typed_finite_difference` returns
> the unit roundoff for the declared precision. It is used solely to
> classify a transfer observation as `TRANSFER_CANCELLATION_DOMINATED`
> when `|Δg| / max(|g(f)|, |g(f+δf)|) < precision_floor`.
>
> The precision_floor IS:
> - declared finite-precision observability evidence per Axiom 3
> - status-only: it determines stratum classification, never computed values
>
> The precision_floor IS NOT:
> - a denominator floor
> - a rescue constant
> - a clamp
> - a hidden tolerance
>
> A transfer observation reaching CANCELLATION_DOMINATED carries the same
> numerical transfer value it would have without the floor; only the
> stratum classification changes. Downstream consumers refuse the value
> based on its (selectable=False) validity, not its number.

#### 8b. Targeted audit pattern

Add to the source-purity audit script the pattern:

```text
precision_floor|roundoff_floor|unit_roundoff|machine_epsilon|cancellation_ratio|2\.0\s*\*\*\s*-52|sys\.float_info\.epsilon|np\.finfo
```

This complements the existing pattern (`lloyd_v3|safe_mask|clamp_min|eps|...`)
without catching unrelated occurrences of `floor` (which would hit
`noise_floor` and mathematical floors). New occurrences in source/tests
that match this pattern must be reviewed for Axiom 3 compliance during
review.

#### 8c. Projection transition rule authority

Add a comment block in `src/lloyd_v4/projection/exact_projection.py` above
the `QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE` definition:

```python
# Authority note (Task 018):
# For contextual transition rules, the transition() callable output is
# authoritative at runtime. The static `mapped_statuses` dict is
# branch-compatible coverage hints only — it shows the default mapping
# under a branch-compatible context but does not capture branch-conditional
# refusals (e.g., TWO_REAL_ROOTS with branch=LINEAR yields
# PROJECTION_SELECTION_REFUSED, not TRANSVERSE). Auditors reading the rule
# must consult the transition() callable for full semantics.
```

Add a test in `tests/test_task018_*` that demonstrates this:
`TWO_REAL_ROOTS` with `branch=BranchSelection.LINEAR` yields
`PROJECTION_SELECTION_REFUSED` at runtime, distinct from the dict's
declared default mapping.

## Required Tests

New file: `tests/test_task018_directional_alpha_probe.py`. Verify, at minimum:

### Pre-task evidence

```python
def test_directional_alpha_probe_does_not_yet_exist() -> None:
    """Pre-task evidence; remove during implementation."""
    pass
```

### Stratum coverage

```python
def test_regular_integer_stratum_alpha_2():
    """g(f) = f^2, α=2, no declared models, band lets it snap to integer."""
    g = lambda f: f * f
    f_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    result = directional_alpha_probe(
        g, f_values,
        probe_id="quadratic_probe",
        function_label="square",
        declared_alpha_band=0.01,
    )
    assert result.status is AlphaProbeStatus.ALPHA_REGULAR_INTEGER
    assert abs(result.value.observed_alpha - 2.0) < 1e-3
    assert result.value.r_squared > 0.999
    assert result.value.n_observed == 6


def test_fractional_branch_stratum_alpha_half():
    """g(f) = sqrt(f), α=0.5, declared band keeps it non-integer."""
    import math as _m
    g = lambda f: _m.sqrt(f)
    f_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    result = directional_alpha_probe(
        g, f_values,
        probe_id="sqrt_probe",
        function_label="sqrt",
        declared_alpha_band=0.01,  # 0.5 is not within 0.01 of any positive integer
    )
    assert result.status is AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH
    assert abs(result.value.observed_alpha - 0.5) < 1e-3


def test_negative_singularity_stratum():
    """g(f) = 1/f near zero: α = -1."""
    g = lambda f: 1.0 / f
    f_values = [1e-4, 1e-3, 1e-2, 1e-1]
    result = directional_alpha_probe(
        g, f_values,
        probe_id="reciprocal_probe",
        function_label="reciprocal",
        declared_alpha_band=0.01,
    )
    assert result.status is AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY
    assert result.value.observed_alpha < 0
    assert abs(result.value.observed_alpha - (-1.0)) < 1e-2


def test_model_unique_match_emits_regime_stratum():
    """Declared model match for α=2 emits ALPHA_REGULAR_INTEGER + selected_alpha_model."""
    g = lambda f: f * f
    f_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    models = (DeclaredAlphaModel(name="quadratic", alpha=2.0, band=0.05),)
    result = directional_alpha_probe(
        g, f_values,
        probe_id="quadratic_with_model",
        function_label="square",
        declared_alpha_models=models,
    )
    assert result.status is AlphaProbeStatus.ALPHA_REGULAR_INTEGER
    assert result.value.selected_alpha_model == "quadratic"
    assert result.value.matching_alpha_model_names == ("quadratic",)


def test_model_ambiguous_stratum():
    """Two declared models with overlapping bands both match observed α."""
    g = lambda f: f * f
    f_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    models = (
        DeclaredAlphaModel(name="quadratic", alpha=2.0, band=0.5),
        DeclaredAlphaModel(name="near_quadratic", alpha=2.4, band=0.5),
    )
    result = directional_alpha_probe(
        g, f_values,
        probe_id="ambiguous",
        function_label="square",
        declared_alpha_models=models,
    )
    assert result.status is AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS
    assert set(result.value.matching_alpha_model_names) == {"quadratic", "near_quadratic"}
    assert result.value.selected_alpha_model is None


def test_model_no_match_stratum():
    """Declared models don't include the observed α."""
    g = lambda f: f * f  # α=2
    f_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    models = (
        DeclaredAlphaModel(name="cubic", alpha=3.0, band=0.05),
        DeclaredAlphaModel(name="sqrt", alpha=0.5, band=0.05),
    )
    result = directional_alpha_probe(
        g, f_values,
        probe_id="no_match",
        function_label="square",
        declared_alpha_models=models,
    )
    assert result.status is AlphaProbeStatus.ALPHA_MODEL_NO_MATCH
    assert result.value.matching_alpha_model_names == ()


def test_insufficient_data_stratum_too_few_f_values():
    g = lambda f: f * f
    result = directional_alpha_probe(
        g, [1e-3, 1e-2],  # only 2
        probe_id="too_few",
        function_label="square",
    )
    assert result.status is AlphaProbeStatus.ALPHA_INSUFFICIENT_DATA
    assert result.value.observed_alpha is None
    assert result.value.n_observed == 2


def test_cancellation_dominated_stratum():
    """Function whose finite-difference is below precision floor everywhere."""
    g = lambda f: 1.0 + 1e-20 * f  # tiny perturbation rounds away
    f_values = [1e-4, 1e-3, 1e-2, 1e-1]
    result = directional_alpha_probe(
        g, f_values,
        probe_id="cancel",
        function_label="near_constant",
    )
    assert result.status is AlphaProbeStatus.ALPHA_CANCELLATION_DOMINATED
    assert result.value.n_cancellation_dominated >= 3
    assert result.value.observed_alpha is None


def test_domain_refused_stratum():
    """Observable raises for all f-values."""
    def g(f):
        raise ValueError("not defined")
    f_values = [1e-4, 1e-3, 1e-2, 1e-1]
    result = directional_alpha_probe(
        g, f_values,
        probe_id="bad",
        function_label="raises",
    )
    assert result.status is AlphaProbeStatus.ALPHA_DOMAIN_REFUSED


def test_indeterminate_stratum_via_degenerate_input():
    """All f-values identical -> SLOPE_DEGENERATE_INPUT from typed_log_log_slope."""
    g = lambda f: f * f
    f_values = [1e-3, 1e-3, 1e-3, 1e-3]  # all identical
    result = directional_alpha_probe(
        g, f_values,
        probe_id="degen",
        function_label="square",
    )
    assert result.status is AlphaProbeStatus.ALPHA_INDETERMINATE
```

### Input validation

```python
def test_empty_f_values_raises():
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [],
            probe_id="x", function_label="x")


def test_non_positive_f_value_raises():
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [-1e-3, 1e-3, 1e-2],
            probe_id="x", function_label="x")


def test_zero_f_value_raises():
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [0.0, 1e-3, 1e-2],
            probe_id="x", function_label="x")


def test_non_finite_f_value_raises():
    import math as _m
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [1e-3, _m.inf, 1e-2],
            probe_id="x", function_label="x")


def test_zero_eta_raises():
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [1e-3, 1e-2], eta=0.0,
            probe_id="x", function_label="x")


def test_empty_probe_id_raises():
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(lambda f: f, [1e-3, 1e-2],
            probe_id="", function_label="x")


def test_duplicate_model_names_raise():
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(
            lambda f: f, [1e-3, 1e-2, 1e-1],
            probe_id="x", function_label="x",
            declared_alpha_models=(
                DeclaredAlphaModel("dup", 0.5, 0.05),
                DeclaredAlphaModel("dup", 1.5, 0.05),
            ),
        )


def test_non_callable_observable_raises():
    with pytest.raises(ProtocolViolationError):
        directional_alpha_probe(42, [1e-3, 1e-2],
            probe_id="x", function_label="x")
```

### Provenance and identity

```python
def test_inputs_carry_probe_and_function_labels():
    g = lambda f: f * f
    f_values = (1e-3, 1e-2, 1e-1)
    result = directional_alpha_probe(
        g, list(f_values),
        probe_id="quad_probe",
        function_label="square",
        eta=1e-6,
    )
    assert result.provenance.inputs == ("quad_probe", "square", f_values, 1e-6)


def test_parents_include_all_transfers_and_slope():
    g = lambda f: f * f
    f_values = [10**(-i) for i in range(2, 8)]  # 6 values
    result = directional_alpha_probe(
        g, f_values,
        probe_id="x", function_label="square",
    )
    # 6 transfer trace_ids + 1 slope trace_id = 7 parents
    assert len(result.provenance.parents) == 7


def test_distinct_probe_ids_distinct_trace_ids():
    g = lambda f: f * f
    f_values = [1e-3, 1e-2, 1e-1]
    r1 = directional_alpha_probe(g, f_values, probe_id="A", function_label="square")
    r2 = directional_alpha_probe(g, f_values, probe_id="B", function_label="square")
    assert r1.provenance.trace_id != r2.provenance.trace_id


def test_identical_inputs_identical_trace_ids():
    g = lambda f: f * f
    f_values = [1e-3, 1e-2, 1e-1]
    r1 = directional_alpha_probe(g, f_values, probe_id="x", function_label="square")
    r2 = directional_alpha_probe(g, f_values, probe_id="x", function_label="square")
    assert r1.provenance.trace_id == r2.provenance.trace_id


def test_alpha_probe_never_alters_transfer_values():
    """Discipline: AlphaProbe must preserve transfer computations exactly."""
    g = lambda f: f * f
    f_values = [1e-3, 1e-2, 1e-1]
    # Compute transfers directly
    direct_transfers = [
        typed_finite_difference(g, f, 1e-6 * f, function_label="square")
        for f in f_values
    ]
    # Run probe
    probe_result = directional_alpha_probe(
        g, f_values, probe_id="x", function_label="square", eta=1e-6,
    )
    # The probe's transfer_trace_ids should match the direct transfers' trace_ids
    direct_trace_ids = tuple(t.provenance.trace_id for t in direct_transfers)
    assert probe_result.value.transfer_trace_ids == direct_trace_ids
```

### Headline α-1 recovery via AlphaProbe

```python
def test_alpha_minus_one_law_via_alpha_probe():
    """Replay the Task 016 headline test through AlphaProbe."""
    test_cases = [
        (0.5, AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH),
        (1.5, AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH),
        (2.0, AlphaProbeStatus.ALPHA_REGULAR_INTEGER),
        (3.0, AlphaProbeStatus.ALPHA_REGULAR_INTEGER),
    ]
    f_values = [10**(-i) for i in range(1, 7)]

    for alpha, expected_status in test_cases:
        g = lambda f, a=alpha: f ** a
        result = directional_alpha_probe(
            g, f_values,
            probe_id=f"alpha_{alpha}",
            function_label=f"power_{alpha}",
            declared_alpha_band=0.05,
        )
        assert result.status is expected_status, (
            f"alpha={alpha}: expected {expected_status.value}, got {result.status.value}")
        assert abs(result.value.observed_alpha - alpha) < 1e-2
        assert result.value.r_squared > 0.999
```

### Projection transition authority (Cleanup item 8c test)

```python
def test_projection_transition_rule_callable_authoritative():
    """The transition() callable, not mapped_statuses, is authoritative.
    Demonstrates the auditor-trap noted in the rule's comment."""
    from lloyd_v4.core.transitions import apply_status_transition
    from lloyd_v4.projection.exact_projection import (
        QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE,
    )
    from lloyd_v4.projection.branches import BranchSelection
    from lloyd_v4.core.status import QuadraticRootStatus, ProjectionStatus

    # mapped_statuses says TWO_REAL_ROOTS -> PROJECTION_TRANSVERSE
    rule = QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE
    assert (rule.mapped_statuses[QuadraticRootStatus.TWO_REAL_ROOTS]
            is ProjectionStatus.PROJECTION_TRANSVERSE)

    # But with branch=LINEAR, the callable returns PROJECTION_SELECTION_REFUSED.
    outcome = apply_status_transition(
        rule,
        QuadraticRootStatus.TWO_REAL_ROOTS,
        branch=BranchSelection.LINEAR,
    )
    assert outcome.output_status is ProjectionStatus.PROJECTION_SELECTION_REFUSED
```

### Serialization

```python
def test_serialization_round_trip_observed():
    import json
    from lloyd_v4.core.serialization import to_json_safe
    g = lambda f: f * f
    result = directional_alpha_probe(
        g, [1e-3, 1e-2, 1e-1, 1.0],
        probe_id="x", function_label="square",
        declared_alpha_band=0.05,
    )
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    decoded = json.loads(encoded)
    assert decoded["status"] == "alpha_regular_integer"
    assert decoded["value"]["observed_alpha"] is not None


def test_serialization_round_trip_refusal():
    import json
    from lloyd_v4.core.serialization import to_json_safe
    result = directional_alpha_probe(
        lambda f: f, [1e-3, 1e-2],  # insufficient
        probe_id="x", function_label="x",
    )
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    assert "Infinity" not in encoded
    assert "NaN" not in encoded
```

### Protocol validation

```python
def test_consumer_protocol_accepts_observed_strata():
    g = lambda f: f * f
    result = directional_alpha_probe(
        g, [1e-3, 1e-2, 1e-1, 1.0],
        probe_id="x", function_label="square",
        declared_alpha_band=0.05,
    )
    check = validate_protocol(result, ALPHA_PROBE_CONSUMER_PROTOCOL)
    assert check.ok


def test_consumer_protocol_refuses_model_no_match():
    g = lambda f: f * f  # α=2
    models = (DeclaredAlphaModel("sqrt", 0.5, 0.05),)
    result = directional_alpha_probe(
        g, [1e-3, 1e-2, 1e-1, 1.0],
        probe_id="x", function_label="square",
        declared_alpha_models=models,
    )
    check = validate_protocol(result, ALPHA_PROBE_CONSUMER_PROTOCOL)
    assert not check.ok
```

## Required Commands

```bash
# Pre-task
python -c "from lloyd_v4.primitives import directional_alpha_probe" 2>&1
# Expected: ImportError

# Green slice
pytest -x tests/test_task018_directional_alpha_probe.py -v

# Full suite
pytest -x tests/

# Source audits (existing + new pattern from 8b)
pytest -x tests/test_task010a_layer_manifest_machine_readable.py
pytest -x tests/test_task010b_export_drift.py
pytest -x tests/test_task010b_manifest_completeness.py
pytest -x tests/test_task010c_no_unregistered_operations.py
pytest -x tests/test_task010c_lineage_terminates_in_primitive.py
pytest -x tests/test_task010c_no_chain_cycles.py

# Targeted floor audit (cleanup item 8b)
rg "precision_floor|roundoff_floor|unit_roundoff|machine_epsilon|cancellation_ratio|2\.0\s*\*\*\s*-52|sys\.float_info\.epsilon|np\.finfo" src tests Build_Docs -n
# Each match must be intentional and Axiom-3 compliant; document any new occurrences.
```

## Non-Goals

This task explicitly does NOT:

- Build JetBundle. AlphaProbe must land and reveal its typing patterns
  before JetBundle is scoped (forward Task 019).
- Build any solver. Solver work (forward Tasks 020/021) must not be
  drafted until AlphaProbe is complete.
- Add nested-window slope drift / BIC model comparison (the
  `require_stable_windows` parameter is reserved as a forward extension
  but not implemented in v1; if implemented, it would emit a new stratum
  `ALPHA_NON_ALGEBRAIC_DRIFT` not present in this task).
- Add multi-precision execution. `precision="raw_python"` is the only
  supported value; AlphaProbe just propagates whatever precision the
  caller declares.
- Add multi-path expression variants. `expression_path="log_log_slope_fit"`
  is the only supported path.
- Add multi-dimensional or vector-direction probing. AlphaProbe in v1 is
  scalar along an explicit positive approach grid `f → 0+`. Multi-dim
  directional probing belongs to a later JetBundle or LocalModelProvider
  task.
- Add hidden closeness-to-integer rules. Integer-snapping requires explicit
  caller-supplied `declared_alpha_band` or per-model `band`.
- Resolve Stress Test Findings 2/3 (validity dishonesty backlog,
  conditioning honesty backlog). Those remain backlog Tasks 012/013.
- Build any of the six missing V4-plan Layer 1 primitives
  (`signed_difference`, `norm_state`, `stratified_sqrt`,
  `spectral_gap_state`, `projector_state`, `constraint_zero_state`).
  Their absence is noted; they remain forward work.
- Touch metrology, branch, refinery, history, solver Layer 2+ V3-shape
  modules. Per the drift audit, those remain deferred-consumer reference.

## Completion Report

Generate `Build_Docs/Reports/task018_summary.md` with:

- Number of tests added (target ~25)
- Full suite count (must be 296 + new)
- Sample serialized output for an `ALPHA_REGULAR_INTEGER` and an
  `ALPHA_FRACTIONAL_BRANCH` AlphaProbe result
- Each of the ten implementable strata demonstrated with one example
- The headline α-1 validation table re-run through AlphaProbe:
  α ∈ {0.5, 1.5, 2.0, 3.0} with recovered α, R², expected stratum,
  selected_alpha_model (where applicable)
- Confirmation of trace_id uniqueness and lineage walk (probe → transfers
  → slope)
- Confirmation that AlphaProbe's `transfer_trace_ids` match independently-
  computed transfer trace_ids for the same inputs (the discipline test
  that AlphaProbe never alters transfer values)
- Confirmation of the projection transition authority comment and test
- Confirmation of the precision_floor METROLOGY_PRINCIPLES.md entry
- Confirmation of the targeted floor audit pattern integration
- Honest limits: no nested-window drift analysis, no multi-precision,
  scalar-direction only, no JetBundle composition yet

## Acceptance Criteria

1. `AlphaProbeStatus` enum exists in `core/status.py` with ten strata.
2. `AlphaProbeStatus` is added to `StatusCode` union.
3. New module `src/lloyd_v4/primitives/directional_alpha_probe.py` exists
   with `AlphaProbeObservation`, `DeclaredAlphaModel`, both protocols,
   and the public `directional_alpha_probe` function.
4. `primitives/__init__.py` exports the new symbols.
5. `layer_manifest.json` and `LAYER_MANIFEST.md` declare the new entries.
   `directional_alpha_probe` is listed in `calibrated_primitive_operations`.
6. All ten strata are produced by appropriately-constructed inputs and
   verified by tests.
7. The α-1 paper validation re-runs through AlphaProbe: for
   α ∈ {0.5, 1.5, 2.0, 3.0}, the probe produces the expected stratum
   (FRACTIONAL/FRACTIONAL/REGULAR/REGULAR) with `observed_alpha` within
   1e-2 of α and R² > 0.999.
8. Trace_id uniqueness tests pass (distinct probe_id → distinct trace_ids;
   identical inputs → identical trace_ids).
9. Discipline test passes: AlphaProbe's transfer_trace_ids match
   independently-computed transfer trace_ids for the same inputs (no
   alteration of underlying computation).
10. Lineage walk test passes: probe parents include every transfer's
    trace_id plus the slope trace_id (when computed).
11. Projection transition authority comment exists in source; test
    confirms callable supersedes mapped_statuses.
12. METROLOGY_PRINCIPLES.md (new or appended) contains the
    precision_floor declaration as status-only evidence.
13. The targeted floor audit pattern is integrated into the source-purity
    audit; new occurrences in source are documented.
14. Serialization round-trip works for all ten strata.
15. Consumer protocol validation passes for the three accepted observation
    strata and refuses the seven refusal strata.
16. All existing 296 tests continue to pass.
17. Source-purity audits (existing pattern + new floor pattern) return
    no unintentional matches.
18. `tests/test_task010c_*` audits pass.
19. Completion report at `Build_Docs/Reports/task018_summary.md` is written.

## Discipline Notes

### Solver acceptance law (forward reference for Task 021, not in scope for 018)

When the future solver consumes AlphaProbe evidence, it follows a
two-phase + tie-refusal acceptance law:

**Phase 1: admissibility.** A candidate is admissible only if:
1. Candidate evidence is protocol-valid.
2. Projection evidence is defined.
3. Projection evidence is advance-valid.
4. AlphaProbe evidence is observed or classified into an accepted alpha
   stratum.
5. Candidate generator is compatible with that alpha stratum.
6. The candidate induces no unhandled status transition.

Residual decrease cannot make an inadmissible candidate admissible.

**Phase 2: selection among admissible candidates.** Compare admissible
candidates only by explicitly declared typed comparators. Residual/progress
decrease may be used only as one declared typed comparator after the
geometry gates have admitted the candidates. The comparator itself must
emit a typed result:

```
candidate_preferred_by_progress
candidate_progress_tied
candidate_progress_indeterminate
candidate_progress_comparison_refused
```

No hidden numeric sort. No "lowest residual wins" unless the policy
explicitly declares it AND the residual evidence is observable.

**Phase 3: typed tie-refusal.** If no declared comparator resolves the
tie, or declared comparators produce equality, emit a typed tie-refusal
rather than choosing by hidden order.

This is recorded here so Task 018 is built with awareness of how
AlphaProbe evidence will be consumed. AlphaProbe's `selectable` and
`advanceable` validity fields, the three "observation strata"
(REGULAR_INTEGER, FRACTIONAL_BRANCH, NEGATIVE_SINGULARITY), and the four
"refusal strata" map directly onto the solver's Phase 1 gates.

### Readiness note for forward tasks

- **Task 019** may scope alpha-aware JetBundle after AlphaProbe typing
  patterns are known.
- **Task 020/021** solver work must NOT be drafted until AlphaProbe
  status/value shapes and transition rules are complete and demonstrated.
- The six missing V4-plan Layer 1 primitives (signed_difference,
  norm_state, stratified_sqrt, spectral_gap_state, projector_state,
  constraint_zero_state) likely become real dependencies during Task 019
  (norm_state for gradient_norm) and Task 020+ (signed_difference for
  residual observation, stratified_sqrt for fractional-α step shapes).
  Their schedule should be revisited after AlphaProbe lands.

### V3-shape Layer 2+ stance

Per the drift audit completed this session:

- `metrology`: candidate substrate (may be rebuilt later)
- `branch`: reference only (V3-shape, not authoritative)
- `refinery`: reference only
- `history`: candidate substrate
- `solver`: reference only

The future solver MVP (Task 020/021) depends only on certified Layer 1
primitives + projection + AlphaProbe. Branch fingerprint, refinery, and
history gates are added only after their Layer 2 substrate is rebuilt
cleanly. AlphaProbe must not depend on any Layer 2+ V3-shape module.
