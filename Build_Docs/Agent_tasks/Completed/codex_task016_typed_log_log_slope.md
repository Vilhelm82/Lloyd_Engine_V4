# Task 016 — Typed Log-Log Slope Estimator

## Repository

`/mnt/fast/Lloyd_Engine_V4`

V3 is reference-only (Axiom 10). V1 / OG engine are also reference-only.
Layer 2+ artifacts (metrology, branch, refinery, history, solver) are V3-shaped
deferred-consumer first-drafts and MUST NOT shape this task. Do not cite them
as evidence; do not coordinate fixes with them; do not import from them. This
task is at Layer 1 (primitives) and depends only on Layer 0 (core).

## Current Verified Baseline

- 272 tests passing (`pytest -x tests/`) as of Task 015 completion
- Layers: core, primitives, projection, plus deferred-consumer Layers 2/3
- Calibrated primitive operations: `typed_collection`, `typed_value`,
  `projective_ratio`, `stratified_quadratic_roots`, `typed_finite_difference`
  (5 total)
- Internal operations: `projective_ratio.scalarize`,
  `stratified_quadratic_roots.select`
- Status families at primitives: `CollectionStatus`, `ValueStatus`,
  `ProjectiveRatioStatus`, `QuadraticRootStatus`, `TransferStatus`
- Provenance carries content-addressed identity via `inputs` field (Task 011)

## Task Goal

Add the second capability primitive at Layer 1: `typed_log_log_slope`. This
primitive observes the leading-order log-log slope of a sequence of typed
transfer observations. It takes a `typed_collection` containing
`TransferObservationResult` items, filters to the OBSERVED stratum, and fits
`log|T(f)|` against `log f` using ordinary least squares to produce a typed
slope estimate with R², standard error, and stratum classification.

Per the α-1 transfer law (`transfer_function_exponent_family_revised.tex`,
Theorem 1), if `g(f)` has a controlled branch expansion with exponent α, the
limiting log-log slope of the transfer is α-1. This primitive is the
substrate's typed mechanism for estimating that slope. Together with Task 015,
it forms the minimum substrate capability needed to begin the
precision/path separation experiment that V4 was built to support.

## Source labelling

- **(V4-surface)** V4 currently has typed_finite_difference producing
  TransferObservationResult. To estimate the α-1 slope from such observations,
  V4 needs a fitting primitive. Without it, the typed observations are
  produced but cannot be aggregated into a slope estimate inside the type
  system. Confirmed by inspection of layer manifest after Task 015.
- **(theorem-derived, Theorem 1 of α-1 paper)** "If g has the controlled
  branch expansion `g(f) = g_0 + c f^α L(f)(1 + r(f))`, then
  `D log T_{δf}(f) → α - 1` as `f → 0+`." The slope of `log|T(f)|` vs `log f`
  IS the substrate's estimate of α-1. This task provides the typed mechanism
  for that estimate.
- **(geometric framing)** The slope is a geometric feature of the function's
  asymptotic behaviour — the leading-order exponent of its local-slope curve.
  Strata classify geometric outcomes (slope clean, insufficient data,
  degenerate sample distribution), not floating-point pathologies.

## Design Principles

- **Geometric measurement, not statistical wrapper.** This primitive observes
  one geometric feature: the leading-order log-log slope of a transfer-vs-base
  relationship. It is not a general-purpose linear regression utility. It
  consumes `TransferObservation` results only.
- **Strata are geometric in nature.** SLOPE_OBSERVED, SLOPE_INSUFFICIENT_DATA,
  SLOPE_DEGENERATE_INPUT — each is a meaningful observational state about the
  geometry of the input distribution.
- **Substrate observes; consumer interprets.** The primitive ALWAYS reports
  R² and standard error when ≥3 OBSERVED points are available. There is no
  R²-threshold gate that elevates SLOPE_OBSERVED into "failed" because the
  fit didn't meet a hidden quality bar. Consumers decide whether the reported
  R² and SE meet their needs.
- **Inputs are typed end-to-end (Axiom 8).** The collection input must contain
  `TransferObservationResult` items. Any other content is a hard
  ProtocolViolationError, not a typed refusal — heterogeneous collections are
  a programmer error, not a substrate observation.
- **Internal operation, not calibrated primitive.** This operation is a
  transformation of an existing typed input (a collection) into a derived
  typed output (a slope). Its identity is encoded in `parents`, not in
  `inputs`, matching the pattern of `scalarize_projective_ratio` and
  `select_quadratic_root`.

## Primitive-Sufficiency Gate

Per Axiom 12, every concept this task uses must already exist in a parent
layer. Verifying:

| Concept used | Provided by | Location |
|---|---|---|
| `TypedResult` | core | `core/result.py` |
| `Validity`, `Conditioning`, `Provenance` | core | `core/{validity,conditioning,provenance}.py` |
| `ProducerProtocol`, `ConsumerProtocol`, `validate_protocol` | core | `core/protocols.py` |
| `ProtocolStatus`, `ConditioningStatus`, `ProvenanceStatus` | core | `core/status.py` |
| `ProtocolViolationError` | core | `core/errors.py` |
| `TypedCollectionResult`, `TypedCollectionValue` | primitives | `primitives/typed_collection.py` |
| `TransferObservationResult`, `TransferObservation`, `TransferStatus.TRANSFER_OBSERVED` | primitives | `primitives/typed_finite_difference.py`, `core/status.py` |
| Pattern: internal operation taking typed input, producing typed output | primitives | `scalarize_projective_ratio`, `select_quadratic_root` |
| Pure-Python OLS regression (no numpy import) | n/a — reusable from V3 reference statically only | implemented inline in this task per Axiom 11 |

The new status family (`SlopeStatus`) is defined in `core/status.py` (the
existing pattern for primitive-layer enums). It is declared as a primitives
layer status family in the manifest.

Sufficiency gate **passes**. No prior parent-extension task required.

### Note on Axiom 11 (Epistemic Stance Only)

OLS regression is a named statistical procedure. Axiom 11 forbids importing
named mathematical content (`numpy`, `scipy.special`, etc.) but permits using
basic operational primitives. The implementation will:

- Implement the regression inline in pure Python (sums, means, products, square root)
- NOT import `numpy` or `scipy`
- Use `math.log`, `math.sqrt`, `math.isfinite` (consistent with the existing
  V4 pattern in `stratified_quadratic_roots.py` and `typed_finite_difference.py`,
  where `math.sqrt` and `math.isfinite` are treated as operational primitives,
  not as substrate building blocks)
- The procedure is standard textbook OLS, identical to V3's `_linregress` in
  `experiments/precision_path_separation.py`. It is "method evidence" only;
  V3 is not imported or called

## Required Deliverables

### 1. New status family in `src/lloyd_v4/core/status.py`

```python
class SlopeStatus(StrEnum):
    SLOPE_OBSERVED = "slope_observed"
    SLOPE_INSUFFICIENT_DATA = "slope_insufficient_data"
    SLOPE_DEGENERATE_INPUT = "slope_degenerate_input"
```

Add `SlopeStatus` to the `StatusCode` union at the bottom of `status.py`.

Stratum semantics:

- **SLOPE_OBSERVED**: The collection contained ≥3 items with status
  `TRANSFER_OBSERVED`, and the log-log distribution had positive variance in
  log(f). A slope, intercept, R², and SE were computed.

- **SLOPE_INSUFFICIENT_DATA**: After filtering to `TRANSFER_OBSERVED` items,
  fewer than 3 usable observations remained. OLS slope cannot be honestly
  estimated below 3 points (SE is undefined at n=2; slope is undefined at n=1).

- **SLOPE_DEGENERATE_INPUT**: ≥3 OBSERVED items remain after filtering, but
  all `f` values are identical (or all `|T|` values are identical). The
  log-log distribution has zero variance along one axis; OLS slope cannot be
  estimated.

### 2. New module `src/lloyd_v4/primitives/typed_log_log_slope.py`

#### Module-level constants

```python
LOG_LOG_SLOPE_SPACE = "LogLogSlopeObservation"
SLOPE_STATUSES = frozenset({
    SlopeStatus.SLOPE_OBSERVED,
    SlopeStatus.SLOPE_INSUFFICIENT_DATA,
    SlopeStatus.SLOPE_DEGENERATE_INPUT,
})

TYPED_LOG_LOG_SLOPE_PROTOCOL = ProducerProtocol(
    name="typed_log_log_slope",
    emitted_statuses=SLOPE_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=SlopeStatus,
)

LOG_LOG_SLOPE_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="log_log_slope_consumer",
    accepted_statuses=frozenset({SlopeStatus.SLOPE_OBSERVED}),
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
    status_family=SlopeStatus,
    refused_statuses=SLOPE_STATUSES - frozenset({SlopeStatus.SLOPE_OBSERVED}),
)
```

#### Value type

```python
@dataclass(frozen=True, slots=True)
class LogLogSlopeObservation:
    slope: float | None             # log-log slope (≈ α-1 if input is from a branch)
    intercept: float | None         # log|T| intercept at log(f)=0
    r_squared: float | None         # coefficient of determination (1.0 = perfect fit)
    standard_error: float | None    # SE of slope estimate
    n_input_observations: int       # total items in the input collection
    n_used: int                     # OBSERVED items after filtering
    log_f_min: float | None         # range of log(f) used in the fit
    log_f_max: float | None
    expression_path: str            # "ordinary_least_squares" by default

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe
        return {
            "slope": to_json_safe(self.slope),
            "intercept": to_json_safe(self.intercept),
            "r_squared": to_json_safe(self.r_squared),
            "standard_error": to_json_safe(self.standard_error),
            "n_input_observations": self.n_input_observations,
            "n_used": self.n_used,
            "log_f_min": to_json_safe(self.log_f_min),
            "log_f_max": to_json_safe(self.log_f_max),
            "expression_path": self.expression_path,
        }


LogLogSlopeResult = TypedResult[LogLogSlopeObservation, SlopeStatus]
```

The value type captures the slope-fit result and diagnostics. Consumers can
read `.slope` for the α-1 estimate; auditors can read R² and SE for confidence;
diagnostic consumers can read `n_used` to see how many points survived
filtering.

#### Public function

```python
def typed_log_log_slope(
    observations: TypedCollectionResult,
    *,
    precision: str = "raw_python",
    backend: str = "python",
    device: str = "cpu",
    measurement_resolution: Any | None = None,
    expression_path: str = "ordinary_least_squares",
) -> LogLogSlopeResult:
    """Observe the leading-order log-log slope of a transfer collection.

    Inputs:
        observations: TypedCollectionResult whose items must each be
                      TransferObservationResult instances. Mixed-type
                      collections raise ProtocolViolationError.
        precision, backend, device, measurement_resolution, expression_path:
                      path metadata. expression_path defaults to
                      "ordinary_least_squares"; future tasks may add weighted
                      or robust fits as alternative paths.

    Returns:
        TypedResult[LogLogSlopeObservation, SlopeStatus] classified into one
        of three strata. Always returns; never raises except for input-level
        ProtocolViolationError (wrong input type, items of wrong type).
    """
```

#### Input validation

Raise `ProtocolViolationError` BEFORE any TypedResult construction for:

- `observations` is not a TypedResult, or its `value` is not a
  `TypedCollectionValue`.
- Any item in `observations.value.items` is not a `TransferObservationResult`
  (i.e., not a TypedResult whose status is a `TransferStatus`).

Note: an empty collection or a collection containing all-non-OBSERVED items
is NOT a hard refusal; it is classified as `SLOPE_INSUFFICIENT_DATA`.

#### Algorithm

```
1. Validate input type (raise on mismatched input or wrong item type).

2. Extract the items tuple from observations.value.items.
   Record n_input_observations = len(items).

3. Filter to items with status == TransferStatus.TRANSFER_OBSERVED.
   Record n_used = len(filtered).

4. If n_used < 3:
   return SLOPE_INSUFFICIENT_DATA with LogLogSlopeObservation populated:
     slope=None, intercept=None, r_squared=None, standard_error=None,
     n_input_observations, n_used, log_f_min=None, log_f_max=None,
     expression_path.
   parents includes the collection trace_id AND each filtered observation's
   trace_id (even though there are <3 of them — the lineage is still real).

5. For each filtered observation, extract:
     f_i = obs.provenance.inputs[0]   # the f value passed to typed_finite_difference
     T_i = obs.value.transfer
   Skip any with non-finite or non-positive f or T (defensive — should not
   occur for OBSERVED, but cheap to check).

6. If any extraction failed (non-finite/non-positive f or T sneaks through),
   reduce n_used accordingly. Re-check n_used >= 3.

7. Compute log_f_i = log(f_i) and log_T_i = log(|T_i|) for each pair.

8. If max(log_f_i) - min(log_f_i) == 0  (all log_f identical):
   return SLOPE_DEGENERATE_INPUT with the LogLogSlopeObservation populated
   except slope/intercept/r_squared/standard_error which are None.
   log_f_min and log_f_max ARE populated (they're equal in this case).

9. Run pure-Python OLS:
     n = len(pairs)
     mean_x = sum(log_f_i) / n
     mean_y = sum(log_T_i) / n
     sxx = sum((log_f_i - mean_x)**2 for i)
     sxy = sum((log_f_i - mean_x)*(log_T_i - mean_y) for i)
     slope = sxy / sxx
     intercept = mean_y - slope * mean_x
     residuals = [log_T_i - (slope * log_f_i + intercept) for i]
     ss_res = sum(r**2 for r in residuals)
     ss_tot = sum((log_T_i - mean_y)**2 for i)
     r_squared = 1.0 if ss_tot == 0 else 1.0 - ss_res / ss_tot
     standard_error = sqrt(ss_res / (n - 2) / sxx) if n > 2 and sxx > 0 else None

10. Return SLOPE_OBSERVED with full LogLogSlopeObservation.
```

#### Validity per stratum

| Stratum | defined | finite | selectable | advanceable | observable |
|---|---|---|---|---|---|
| SLOPE_OBSERVED | True | True | True | True | True |
| SLOPE_INSUFFICIENT_DATA | False | False | False | False | True |
| SLOPE_DEGENERATE_INPUT | False | False | False | False | True |

#### Conditioning per stratum

- **SLOPE_OBSERVED**: `Conditioning(WELL_CONDITIONED, notes=(f"r_squared={r2:.6g}", f"standard_error={se:.3e}", f"n_used={n_used}"))`.
  R² and SE are surfaced as quantitative observations; consumers can read
  them and decide whether the fit is good enough for their purpose.
- **SLOPE_INSUFFICIENT_DATA**: `Conditioning(WARNING, notes=(f"n_used={n_used}", "n_used_below_minimum_3",))`.
- **SLOPE_DEGENERATE_INPUT**: `Conditioning(WARNING, notes=("zero_variance_in_log_f",))`.

(Same as Task 015: conditioning is left as WARNING for non-OBSERVED strata.
Task 013 may later refine conditioning into a continuous-or-stratified
observation; this task does not preempt that work.)

#### Provenance

```python
parents = (observations.provenance.trace_id,) + tuple(
    obs.provenance.trace_id for obs in observations.value.items
    if isinstance(obs, TypedResult)
)

provenance = Provenance(
    operation_id="typed_log_log_slope",
    expression_path=expression_path,  # default "ordinary_least_squares"
    precision=precision,
    backend=backend,
    device=device,
    measurement_resolution=measurement_resolution,
    inputs=(),  # internal operation; lineage flows through parents
    parents=parents,
)
```

The collection's trace_id AND each item's trace_id appear in parents. This
makes the lineage walkable through every input observation. Cost is bounded
by the collection size (parents tuple is `1 + N` strings, each 16 chars =
17 × 16 = 272 bytes for N=16, or ~1.5KB for N=96 PPS-scale collections).

`inputs=()` because typed_log_log_slope is an internal operation. Its identity
is fully determined by parents (which transitively encode all input data via
content-addressed identity).

### 3. Update `src/lloyd_v4/primitives/__init__.py`

Add the new exports:

```python
from .typed_log_log_slope import (
    TYPED_LOG_LOG_SLOPE_PROTOCOL,
    LOG_LOG_SLOPE_CONSUMER_PROTOCOL,
    LOG_LOG_SLOPE_SPACE,
    LogLogSlopeObservation,
    LogLogSlopeResult,
    typed_log_log_slope,
)
```

And add them to `__all__`.

### 4. Update `Build_Docs/Architecture/layer_manifest.json`

In the `primitives` layer entry:

- Add `"SlopeStatus"` to `status_families`
- Add `"LogLogSlopeObservation"`, `"LogLogSlopeResult"` to `value_types`
- Add `"TYPED_LOG_LOG_SLOPE_PROTOCOL"`, `"LOG_LOG_SLOPE_CONSUMER_PROTOCOL"` to `protocol_types`
- Add `"LOG_LOG_SLOPE_SPACE"` to `errors_and_utilities`
- Add `"typed_log_log_slope"` to `operations` and `internal_operations`
  (NOT `calibrated_primitive_operations` — see Design Principles)
- Add all the above to `all_exports` (alphabetically)

### 5. Update `Build_Docs/Architecture/LAYER_MANIFEST.md`

Mirror the JSON changes in the human-readable manifest under the `primitives` section.

### 6. New test file `tests/test_task016_typed_log_log_slope.py`

See Required Tests section below.

### 7. Optional: Update `Build_Docs/Architecture/STATUS_CALCULUS.md`

If this doc enumerates status families and their semantics, append a section
on `SlopeStatus`. If it doesn't, skip.

## Required Tests

New file: `tests/test_task016_typed_log_log_slope.py`. The test file must
verify, at minimum:

### Pre-task evidence

```python
def test_typed_log_log_slope_does_not_yet_exist() -> None:
    """Pre-task evidence: importing the primitive fails before this task.
    Remove this stub during implementation."""
    pass
```

### Stratum coverage tests

```python
def test_observed_stratum_recovers_alpha_minus_one_for_quadratic():
    """g(f) = f^2 has analytical slope α-1 = 1.
    Sample at log-spaced f values, fit log|T| vs log f, expect slope ≈ 1."""
    g = lambda x: x * x
    f_values = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3]
    delta = 1e-6
    obs_results = [
        typed_finite_difference(g, f, delta * f, function_label="square")
        for f in f_values
    ]
    collection = typed_collection(obs_results)
    slope_result = typed_log_log_slope(collection)

    assert slope_result.status is SlopeStatus.SLOPE_OBSERVED
    assert abs(slope_result.value.slope - 1.0) < 1e-3
    assert slope_result.value.r_squared > 0.999
    assert slope_result.value.n_used == len(f_values)
    assert slope_result.value.n_input_observations == len(f_values)


def test_observed_stratum_recovers_slope_for_alpha_one_half():
    """g(f) = sqrt(f), analytical slope = α-1 = -0.5."""
    import math as _m
    g = lambda x: _m.sqrt(x)
    f_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    delta = 1e-6
    obs_results = [
        typed_finite_difference(g, f, delta * f, function_label="sqrt")
        for f in f_values
    ]
    collection = typed_collection(obs_results)
    slope_result = typed_log_log_slope(collection)

    assert slope_result.status is SlopeStatus.SLOPE_OBSERVED
    assert abs(slope_result.value.slope - (-0.5)) < 1e-3


def test_insufficient_data_stratum_empty_collection():
    """Empty collection produces SLOPE_INSUFFICIENT_DATA."""
    collection = typed_collection([])
    slope_result = typed_log_log_slope(collection)

    assert slope_result.status is SlopeStatus.SLOPE_INSUFFICIENT_DATA
    assert slope_result.value.slope is None
    assert slope_result.value.n_used == 0
    assert slope_result.value.n_input_observations == 0


def test_insufficient_data_stratum_too_few_observations():
    """Two observations (need ≥3 for slope SE)."""
    g = lambda x: x * x
    obs_results = [
        typed_finite_difference(g, 0.01, 1e-6, function_label="square"),
        typed_finite_difference(g, 0.1, 1e-6, function_label="square"),
    ]
    collection = typed_collection(obs_results)
    slope_result = typed_log_log_slope(collection)

    assert slope_result.status is SlopeStatus.SLOPE_INSUFFICIENT_DATA
    assert slope_result.value.n_input_observations == 2
    assert slope_result.value.n_used == 2


def test_insufficient_data_stratum_filters_non_observed():
    """Collection with mostly non-OBSERVED items, leaving <3 OBSERVED."""
    g = lambda x: x * x
    obs_results = [
        typed_finite_difference(g, 0.01, 1e-6, function_label="square"),  # OBSERVED
        typed_finite_difference(g, 0.1, 0.0, function_label="square"),    # DELTA_INDETERMINATE
        typed_finite_difference(lambda x: float("inf"), 0.5, 1e-6, function_label="inf"),  # NON_FINITE
    ]
    collection = typed_collection(obs_results)
    slope_result = typed_log_log_slope(collection)

    assert slope_result.status is SlopeStatus.SLOPE_INSUFFICIENT_DATA
    assert slope_result.value.n_input_observations == 3
    assert slope_result.value.n_used == 1


def test_degenerate_input_stratum_all_same_f():
    """All observations at the same f: log_f variance is zero."""
    g = lambda x: x * x
    obs_results = [
        typed_finite_difference(g, 0.01, 1e-7, function_label="a"),
        typed_finite_difference(g, 0.01, 2e-7, function_label="b"),
        typed_finite_difference(g, 0.01, 3e-7, function_label="c"),
    ]
    # Note: function_labels differ so trace_ids differ; f is the same.
    collection = typed_collection(obs_results)
    slope_result = typed_log_log_slope(collection)

    assert slope_result.status is SlopeStatus.SLOPE_DEGENERATE_INPUT
    assert slope_result.value.n_used == 3
    assert slope_result.value.log_f_min == slope_result.value.log_f_max
```

### Mixed-stratum filtering tests

```python
def test_mixed_collection_filters_to_observed_and_fits():
    """Collection with 4 OBSERVED + 2 non-OBSERVED. Slope fits on OBSERVED only."""
    g = lambda x: x * x
    obs_results = [
        typed_finite_difference(g, 0.001, 1e-7, function_label="square"),  # OBS
        typed_finite_difference(g, 0.01, 1e-7, function_label="square"),   # OBS
        typed_finite_difference(g, 0.1, 0.0, function_label="square"),     # DELTA_INDET
        typed_finite_difference(g, 0.05, 1e-7, function_label="square"),   # OBS
        typed_finite_difference(lambda x: float("inf"), 0.2, 1e-7, function_label="inf"),  # NON_FIN
        typed_finite_difference(g, 0.5, 1e-7, function_label="square"),    # OBS
    ]
    collection = typed_collection(obs_results)
    slope_result = typed_log_log_slope(collection)

    assert slope_result.status is SlopeStatus.SLOPE_OBSERVED
    assert slope_result.value.n_input_observations == 6
    assert slope_result.value.n_used == 4
    assert abs(slope_result.value.slope - 1.0) < 1e-2
```

### Input validation tests

```python
def test_non_typed_result_input_raises():
    with pytest.raises(ProtocolViolationError):
        typed_log_log_slope([1, 2, 3])  # raw list, not a TypedCollectionResult


def test_collection_of_wrong_type_raises():
    g = lambda x: x
    bad_collection = typed_collection([projective_ratio(1, 2), projective_ratio(3, 4)])
    with pytest.raises(ProtocolViolationError):
        typed_log_log_slope(bad_collection)


def test_collection_with_mixed_types_raises():
    g = lambda x: x
    bad_collection = typed_collection([
        typed_finite_difference(g, 0.01, 1e-6, function_label="x"),
        projective_ratio(1, 2),  # wrong type
    ])
    with pytest.raises(ProtocolViolationError):
        typed_log_log_slope(bad_collection)
```

### Provenance and identity tests

```python
def test_inputs_field_is_empty_for_internal_operation():
    """typed_log_log_slope is internal; lineage flows through parents."""
    g = lambda x: x * x
    obs = [typed_finite_difference(g, 10**i * 1e-3, 1e-7, function_label="sq")
           for i in range(6)]
    collection = typed_collection(obs)
    result = typed_log_log_slope(collection)
    assert result.provenance.inputs == ()


def test_parents_includes_collection_and_each_observation():
    g = lambda x: x * x
    obs = [typed_finite_difference(g, 10**i * 1e-3, 1e-7, function_label="sq")
           for i in range(4)]
    collection = typed_collection(obs)
    result = typed_log_log_slope(collection)

    parents_set = set(result.provenance.parents)
    assert collection.provenance.trace_id in parents_set
    for o in obs:
        assert o.provenance.trace_id in parents_set
    assert len(result.provenance.parents) == 1 + len(obs)


def test_distinct_input_collections_distinct_trace_ids():
    """Different input observations -> different slope trace_ids."""
    g = lambda x: x * x
    obs_a = [typed_finite_difference(g, 0.01, 1e-7, function_label="a")
             for _ in range(3)]
    obs_b = [typed_finite_difference(g, 0.02, 1e-7, function_label="a")
             for _ in range(3)]
    slope_a = typed_log_log_slope(typed_collection(obs_a))
    slope_b = typed_log_log_slope(typed_collection(obs_b))
    assert slope_a.provenance.trace_id != slope_b.provenance.trace_id


def test_same_input_collection_identical_trace_ids():
    """Content-addressed: identical inputs -> identical trace_ids."""
    g = lambda x: x * x
    obs = [typed_finite_difference(g, 10**i * 1e-3, 1e-7, function_label="sq")
           for i in range(4)]
    c1 = typed_collection(obs)
    c2 = typed_collection(obs)  # different collection instance, identical content
    s1 = typed_log_log_slope(c1)
    s2 = typed_log_log_slope(c2)
    assert s1.provenance.trace_id == s2.provenance.trace_id


def test_provenance_records_path_metadata():
    g = lambda x: x * x
    obs = [typed_finite_difference(g, 10**i * 1e-3, 1e-7, function_label="sq")
           for i in range(4)]
    result = typed_log_log_slope(typed_collection(obs))
    assert result.provenance.operation_id == "typed_log_log_slope"
    assert result.provenance.expression_path == "ordinary_least_squares"
    assert result.provenance.precision == "raw_python"
```

### Lineage walk test

```python
def test_lineage_walks_through_collection_to_observations():
    """Audit machinery should be able to walk from slope -> collection -> obs."""
    from _audit_helpers.lineage import build_trace_id_index, walk_chain
    g = lambda x: x * x
    obs = [typed_finite_difference(g, 10**i * 1e-3, 1e-7, function_label="sq")
           for i in range(4)]
    collection = typed_collection(obs)
    slope = typed_log_log_slope(collection)

    instances = (slope, collection) + tuple(obs)
    index = build_trace_id_index(instances)
    walked = list(walk_chain(slope, index))
    walked_ids = {item.provenance.trace_id for item in walked}

    assert slope.provenance.trace_id in walked_ids
    assert collection.provenance.trace_id in walked_ids
    for o in obs:
        assert o.provenance.trace_id in walked_ids
```

### Serialization round-trip

```python
def test_serialization_round_trip_observed():
    import json
    from lloyd_v4.core.serialization import to_json_safe
    g = lambda x: x * x
    obs = [typed_finite_difference(g, 10**i * 1e-3, 1e-7, function_label="sq")
           for i in range(4)]
    result = typed_log_log_slope(typed_collection(obs))
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    decoded = json.loads(encoded)
    assert decoded["status"] == "slope_observed"
    assert decoded["value"]["slope"] is not None
    assert decoded["value"]["r_squared"] is not None


def test_serialization_round_trip_insufficient():
    import json
    from lloyd_v4.core.serialization import to_json_safe
    result = typed_log_log_slope(typed_collection([]))
    payload = to_json_safe(result)
    encoded = json.dumps(payload, allow_nan=False)
    assert "Infinity" not in encoded
    assert "NaN" not in encoded
```

### Protocol validation

```python
def test_consumer_protocol_accepts_observed():
    g = lambda x: x * x
    obs = [typed_finite_difference(g, 10**i * 1e-3, 1e-7, function_label="sq")
           for i in range(4)]
    result = typed_log_log_slope(typed_collection(obs))
    check = validate_protocol(result, LOG_LOG_SLOPE_CONSUMER_PROTOCOL)
    assert check.ok


def test_consumer_protocol_refuses_insufficient_data():
    result = typed_log_log_slope(typed_collection([]))
    check = validate_protocol(result, LOG_LOG_SLOPE_CONSUMER_PROTOCOL)
    assert not check.ok
```

### α-1 paper validation

```python
def test_alpha_minus_one_law_recovers_slope_for_known_alphas():
    """Theorem 1 of α-1 paper: slope of log|T| vs log f → α-1.
    Test multiple α values; verify recovered slope matches α-1."""
    import math as _m
    test_cases = [
        (2.0, 1.0),    # g(f) = f^2, expected slope = 1
        (0.5, -0.5),   # g(f) = sqrt(f), expected slope = -0.5
        (3.0, 2.0),    # g(f) = f^3, expected slope = 2
        (1.5, 0.5),    # g(f) = f^1.5, expected slope = 0.5
    ]
    f_values = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    delta_ratio = 1e-6

    for alpha, expected_slope in test_cases:
        g = lambda x, a=alpha: x ** a
        obs = [typed_finite_difference(g, f, delta_ratio * f,
                                       function_label=f"power_{alpha}")
               for f in f_values]
        result = typed_log_log_slope(typed_collection(obs))
        assert result.status is SlopeStatus.SLOPE_OBSERVED, (
            f"alpha={alpha}: expected SLOPE_OBSERVED, got {result.status.value}")
        assert abs(result.value.slope - expected_slope) < 1e-2, (
            f"alpha={alpha}: expected slope {expected_slope}, "
            f"got {result.value.slope}")
        assert result.value.r_squared > 0.999, (
            f"alpha={alpha}: expected R^2 > 0.999, got {result.value.r_squared}")
```

This test is the substantive validation: V4 should now be able to recover the
α-1 slope for known controlled branches at substrate fidelity. If this test
passes, the V4 substrate has demonstrated it can do what V3's PPS demonstrated,
at least for the noise-free synthetic case.

## Required Commands

```bash
# Pre-task: confirm gap exists.
python -c "from lloyd_v4.primitives import typed_log_log_slope" 2>&1
# Expected: ImportError or AttributeError before task begins.

# Green slice (during implementation):
pytest -x tests/test_task016_typed_log_log_slope.py -v

# Full suite:
pytest -x tests/

# Source audits (must continue to pass):
pytest -x tests/test_task010a_layer_manifest_machine_readable.py
pytest -x tests/test_task010b_export_drift.py
pytest -x tests/test_task010b_manifest_completeness.py
pytest -x tests/test_task010c_no_unregistered_operations.py
pytest -x tests/test_task010c_lineage_terminates_in_primitive.py
pytest -x tests/test_task010c_no_chain_cycles.py
```

## Non-Goals

This task explicitly does NOT:

- Add multi-precision execution. `precision="raw_python"` is the only
  supported value, inherited from typed_finite_difference. Future tasks add
  numpy/mpmath backends.
- Add nested-window slope drift analysis (V3 PPS reports slope drift to
  distinguish algebraic from non-algebraic branches via BIC). That's Task 018.
- Add weighted regression, robust regression, or any alternative fit method.
  `expression_path="ordinary_least_squares"` is the only supported path;
  alternative paths are forward tasks.
- Add the multi-precision/multi-path amplitude separation
  `c_hat[p,k] = a + u_p · b_k`. That's Task 020 (PPS milestone), which
  composes 015–019.
- Resolve Stress Test Findings 2 (validity dishonesty) or 3 (conditioning
  honesty) at other primitives. Those remain as backlog tasks 012 and 013.
  This task introduces observation-honest validity AT THIS PRIMITIVE,
  consistent with Task 015's pattern.

## Completion Report

Generate `Build_Docs/Reports/task016_summary.md` with:

- Number of tests added in `test_task016_*` (target: ~16)
- Number of tests passing in full suite (must be 272 + new test count)
- Sample output: `typed_log_log_slope` result for `g(f) = f^2` shown serialized
- Each of the 3 strata demonstrated with one example
- The α-1 paper validation: recovered slope for α ∈ {0.5, 1.5, 2.0, 3.0}
  reported alongside expected `α - 1`. This is the headline empirical
  evidence that V4's substrate can now reproduce V3's PPS slope recovery
  for clean synthetic cases.
- Confirmation that the layer manifest update was reflected in
  `LAYER_MANIFEST.md` and `layer_manifest.json`
- Trace_id uniqueness sanity: distinct input collections produce distinct
  slope trace_ids; identical content reproduces identical trace_ids
- Honest note on what `typed_log_log_slope` cannot yet do: no nested-window
  drift analysis, no multi-precision (still single-precision raw_python),
  no weighted regression, no path-attribution amplitude separation. These
  are the forward tasks toward the PPS milestone.

## Acceptance Criteria

1. `SlopeStatus` enum exists in `core/status.py` with three strata.
2. `SlopeStatus` is added to the `StatusCode` union.
3. New module `src/lloyd_v4/primitives/typed_log_log_slope.py` exists with
   `LogLogSlopeObservation` value type, `TYPED_LOG_LOG_SLOPE_PROTOCOL`,
   `LOG_LOG_SLOPE_CONSUMER_PROTOCOL`, `LogLogSlopeResult`, and the public
   `typed_log_log_slope` function.
4. `primitives/__init__.py` exports the new symbols and updates `__all__`.
5. `layer_manifest.json` declares `SlopeStatus`, `LogLogSlopeObservation`,
   `LogLogSlopeResult`, the new protocols, `LOG_LOG_SLOPE_SPACE`, and the
   `typed_log_log_slope` operation as INTERNAL (not calibrated primitive).
6. `LAYER_MANIFEST.md` mirrors the JSON manifest changes.
7. All three strata are produced by appropriately-constructed inputs and
   verified by tests.
8. The α-1 paper validation test passes: recovered slope for at least four
   α values matches the analytical α-1 to within 1e-2 absolute, with R²
   above 0.999.
9. Mixed-stratum filtering works: a collection with non-OBSERVED items
   produces SLOPE_OBSERVED if ≥3 OBSERVED items remain after filtering.
10. Trace_id uniqueness tests pass: distinct input collections produce
    distinct slope trace_ids; identical content produces identical trace_ids.
11. Lineage walk test passes: audit machinery can walk from slope through
    collection to individual observations via `parents`.
12. Serialization round-trip works for all three strata; `json.dumps(allow_nan=False)`
    succeeds.
13. Consumer protocol validation: `LOG_LOG_SLOPE_CONSUMER_PROTOCOL` accepts
    OBSERVED status, refuses other strata.
14. All existing 272 tests continue to pass.
15. Source-purity audits pass (no `eps`/`epsilon` literals, no forbidden imports).
16. `tests/test_task010c_*` pass: new operation_id `typed_log_log_slope` is
    registered in source AND manifest; lineage chains have no cycles;
    lineage terminates in calibrated primitives.
17. Completion report at `Build_Docs/Reports/task016_summary.md` is written.

## Open implementation decisions

These should be resolved during implementation rather than presupposed in the spec:

1. **Where to source `f_i` and `T_i`.** The spec says extract `f_i` from
   `obs.provenance.inputs[0]` and `T_i` from `obs.value.transfer`. This relies
   on Task 015's input ordering (f, delta_f, function_label). If the implementer
   prefers, they can extract differently — what matters is that the (f, T)
   pair is recovered honestly.

2. **`math.log` vs alternative.** Using `math.log` for the natural logarithm
   follows the existing pattern (`math.sqrt`, `math.isfinite`). If the
   source-purity audit fires on `math.log`, the implementer can compute it
   via `math.log` is a primitive operation; if a different idiom satisfies
   the audit, use that. (The audit's job is to catch named theorems and
   constants, not basic transcendental operations.)

3. **Filtering edge cases.** A `TRANSFER_OBSERVED` observation should always
   have a finite, non-zero `transfer` value (per Task 015's strata
   semantics), so `log|T|` should always be defined. The defensive check in
   step 6 of the algorithm handles any unexpected case where this assumption
   breaks; if the implementer can prove the check is unreachable, it can be
   omitted. Recommend keeping it for robustness.

4. **R² when all log_T values are identical.** If all observations have
   exactly the same `|T|`, ss_tot = 0. The formula sets r_squared=1.0 in this
   case. This is mathematically defensible (the slope is exactly 0 and the
   fit is exact) but worth documenting in the value type's notes.

## Discipline notes

- This task derives from V4's own surface (Task 015 produced
  TransferObservationResult; this task aggregates them) and theorem-derived
  constraints (Theorem 1 of `transfer_function_exponent_family_revised.tex`).
- No V3 reference required at runtime. V3's `experiments/precision_path_separation.py`
  contains an inline `_linregress` that is method evidence (the same OLS formula
  used here is standard textbook); V4 implements it independently in pure
  Python without any V3 import.
- No metrology, branch, refinery, or any Layer 2+ artifact is referenced or
  coordinated with.

## Subsequent tasks (forward references, not part of 016)

- **Task 017**: Add multi-precision support — extend `_precision_floor`
  dispatch in typed_finite_difference to handle "float32", "float64",
  "longdouble", and mpmath modes; add execution backends.
- **Task 018**: Add `typed_window_drift` — slope estimation across nested
  windows of a typed_collection of observations, BIC-based model comparison
  for algebraic-vs-non-algebraic branch (V3 PPS's "slope_window" analysis).
- **Task 019**: Add multi-path expression variants (`central_difference`,
  alternative algebraic paths for the same observable, `direct_power` vs
  `exp_log_power`).
- **Task 020 (PPS milestone)**: Compose 015–019 to run the full
  precision/path separation experiment; add typed amplitude separation
  primitive that fits `c_hat[p,k] = a + u_p · b_k` across cells; reproduce
  V3's PPS report at V4 fidelity.
