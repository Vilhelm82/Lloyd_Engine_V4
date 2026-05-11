# Codex Task 006: BranchFingerprint Object and Slope-Flow Model Comparison

## Repository

Work in:

```text
/mnt/fast/Lloyd_Engine_V4
```

This is Lloyd Engine V4 clean-room work. V3 is reference evidence only. Do not import, call, bridge, compare against, adapt, or depend on V3 at runtime. Do not add legacy adapters, compatibility shims, downgrade modes, or cross-engine calls.

## Current verified baseline

Task 000 is complete. The M0 substrate exists: statuses, validity, conditioning, provenance, typed results/refusals, protocol validation, conservative status calculus, strict serialization, core errors, and architecture docs.

Task 001 is complete. `ProjectiveRatio(n, d)` exists as the first primitive. It preserves raw projective coordinates `[n:d]`, classifies exact projective strata without dividing by `d`, and scalarizes only through an explicit protocol that may refuse.

Task 002 is complete. `StratifiedQuadraticRoots` exists. `stratified_quadratic_roots(a, b, c)` returns a typed root-state result with raw coefficients, discriminant evidence, branch-labeled projective root coordinates, validity, conditioning, and provenance. `select_quadratic_root(result, branch)` is explicit and protocol-validated.

Task 003 is complete. `ProjectionResultV4` and the exact quadratic projection protocol exist. `exact_quadratic_projection(root_state_result, branch)` consumes validated Task 002 root-state results, calls Task 002 selection for selectable branches, and emits structured projection evidence with separate `root_exists`, `projection_defined`, `selected_root_valid`, and `advance_valid` flags.

Task 004 is complete. The Layer 2 metrology foundation exists under `src/lloyd_v4/metrology`. It implements declared and estimated `b_k` noise-floor evidence, limit-of-detection classification with explicit `identity_evidence`, pointwise `K_q` proxy calibration through ProjectiveRatio plus explicit scalarization, `proxy_uncalibrated(...)`, and `require_valid_proxy_calibration(...)`.

Task 005 is complete. `TypedResult` is now generic over value type and status enum family. Protocols infer or declare status families and reject wrong-family typed results. Named transition-rule machinery exists with canonical rules for ProjectiveRatio scalarization, quadratic root selection, quadratic projection, limit-of-detection classification, and valid `K_q` calibration. Existing runtime behavior and serialization are unchanged.

Task 005 verification baseline:

```text
Task 005 slice: 15 passed
Full suite: 110 passed
Clean-room, hidden-correction, dependency-direction, deferred-feature, and compatibility audits: no matches
```

## Task 006 goal

Implement the first BranchFingerprint substrate:

```text
BranchFingerprint object and slope-flow model comparison
```

Task 006 moves V4 from pointwise metrology into typed transfer/fingerprint evidence. It must consume the named transition rules from Task 005 rather than inventing local composition maps.

Task 006 should implement:

```text
1. a BranchFingerprint status family;
2. slope-flow sample/value/result objects;
3. finite-difference slope-flow computation in log-magnitude space;
4. explicit model-residual comparison against declared slope models;
5. proxy K_q slope-stability evidence using Task 004 calibration results;
6. a BranchFingerprint object that composes projection evidence, transfer slope-flow evidence, and optional proxy-calibration stability evidence;
7. serialization and reports for all new evidence.
```

Task 006 must not implement a domain consumer. It must not classify bearings, aerospace systems, betting scanners, physical branches, or any domain-specific object. It emits typed branch-fingerprint evidence only.

## Design principles

- Geometry precedes scalarization.
- Degeneracy is a stratum, not failure.
- Typed results compose by protocols.
- Mixed-status composition must use named transition rules.
- BranchFingerprint is evidence, not a domain classifier.
- Slope-flow comparison is explicit model evidence, not hidden branch selection.
- A proxy observable is guilty until calibrated.
- Pointwise `K_q` validity is not enough for proxy transfer claims; Task 006 must add `D log K_q` slope-stability evidence.
- Declared model bands are explicit policy evidence, not hidden rescue constants.
- No hidden epsilons, denominator floors, discriminant floors, clamps, log offsets, safe division, rescue constants, default branch policies, or compatibility modes.
- Metrology may annotate observability and proxy validity. It must not rewrite exact ProjectiveRatio, root, or projection strata.
- BranchFingerprint must preserve projection advance semantics. In particular, tangent contact remains not advance-valid.

## Required package boundary

Create a new Layer 2 package for branch/fingerprint work.

Recommended files:

```text
src/lloyd_v4/branch/__init__.py
src/lloyd_v4/branch/slope_flow.py
src/lloyd_v4/branch/fingerprint.py
```

If the repository has an existing naming convention that is clearly better, use it, but do not place BranchFingerprint implementation inside primitives, projection, or metrology.

Expected core modification:

```text
src/lloyd_v4/core/status.py
```

Only add the new BranchFingerprint status family there. Do not add branch-specific algorithms to core.

Task 006 may import earlier layers in this direction:

```text
branch -> core
branch -> primitives/projective_ratio, if needed for slope ratios
branch -> projection
branch -> metrology
```

Earlier layers must not import branch:

```text
core must not import branch implementation modules
primitives must not import branch
projection must not import branch
metrology must not import branch
```

Branch package may consume public APIs and named transition rules from earlier tasks. It must not patch earlier task behavior.

## Required status family

Add a new status enum family. Recommended name:

```python
BranchFingerprintStatus
```

Required initial statuses:

```text
slope_flow_observed
slope_model_residuals
slope_model_unique_match
slope_model_ambiguous
slope_model_no_match
slope_flow_insufficient_samples
slope_flow_indeterminate
slope_flow_proxy_uncalibrated
kq_flow_stable
kq_flow_unstable
kq_flow_indeterminate
kq_flow_uncalibrated
fingerprint_complete
fingerprint_unidentified
fingerprint_incomplete
fingerprint_proxy_uncalibrated
```

These names may be adjusted only if the final report includes a status table proving the same semantic coverage.

### Status meanings

`slope_flow_observed`

Enough usable samples exist and segment slopes were computed, but no model set was supplied.

`slope_model_residuals`

Enough usable samples exist, model residuals were computed, and no declared model band was supplied. This is evidence, not model selection.

`slope_model_unique_match`

Enough usable samples exist, model residuals were computed, a finite nonnegative declared model band was supplied, and exactly one model lies inside that band.

`slope_model_ambiguous`

Enough usable samples exist, a declared model band was supplied, and more than one model lies inside that band.

`slope_model_no_match`

Enough usable samples exist, a declared model band was supplied, and no model lies inside that band.

`slope_flow_insufficient_samples`

Fewer than two usable samples remain after log-domain and optional limit-of-detection checks.

`slope_flow_indeterminate`

The slope-flow path cannot honestly scalarize, usually because a control/log denominator is zero, an observable is zero or non-finite, a log-domain requirement fails, or a ProjectiveRatio slope refuses to scalarize.

`slope_flow_proxy_uncalibrated`

A proxy slope-flow path was requested, but required pointwise proxy calibration evidence was missing or refused.

`kq_flow_stable`

A proxy `K_q` slope-flow stability check has enough valid pointwise calibration evidence, a finite nonnegative declared stability band, and every segment of `D log K_q` lies inside that band.

`kq_flow_unstable`

A proxy `K_q` slope-flow stability check has enough valid pointwise calibration evidence and a declared stability band, but at least one segment lies outside that band.

`kq_flow_indeterminate`

`K_q` slope-flow stability cannot be assessed honestly, for example due insufficient samples, log-domain failure, or missing declared stability band.

`kq_flow_uncalibrated`

At least one required pointwise `K_q` calibration result failed the `VALID_PROXY_CALIBRATION_PROTOCOL` path.

`fingerprint_complete`

Projection evidence is usable, transfer slope-flow evidence is defined, and proxy evidence is stable if the fingerprint uses a proxy observable. Complete means evidence-complete, not domain-classified.

`fingerprint_unidentified`

Projection and transfer evidence exist, but model comparison is ambiguous or no model matches the declared band. The fingerprint is observable but not selectable as a unique model decision.

`fingerprint_incomplete`

Required projection or transfer evidence is missing, indeterminate, or insufficient. Raw evidence must be preserved.

`fingerprint_proxy_uncalibrated`

A proxy observable is used, but pointwise `K_q` calibration or `K_q` slope stability is missing, refused, indeterminate, or unstable.

## Validity mapping

Use the M0 validity fields consistently.

Recommended mapping:

```text
slope_flow_observed:              defined, finite, selectable, not advanceable, observable
slope_model_residuals:            defined, finite, selectable, not advanceable, observable
slope_model_unique_match:         defined, finite, selectable, not advanceable, observable
slope_model_ambiguous:            defined, finite, not selectable, not advanceable, observable
slope_model_no_match:             defined, finite, not selectable, not advanceable, observable
slope_flow_insufficient_samples:  not defined, not finite, not selectable, not advanceable, observable
slope_flow_indeterminate:         not defined, not finite, not selectable, not advanceable, observable
slope_flow_proxy_uncalibrated:    not defined, not finite, not selectable, not advanceable, observable
kq_flow_stable:                   defined, finite, selectable, not advanceable, observable
kq_flow_unstable:                 defined, finite, not selectable, not advanceable, observable
kq_flow_indeterminate:            not defined, not finite, not selectable, not advanceable, observable
kq_flow_uncalibrated:             not defined, not finite, not selectable, not advanceable, observable
fingerprint_complete:             defined, finite, selectable, not advanceable, observable
fingerprint_unidentified:         defined, finite, not selectable, not advanceable, observable
fingerprint_incomplete:           not defined, not finite, not selectable, not advanceable, observable
fingerprint_proxy_uncalibrated:   not defined, not finite, not selectable, not advanceable, observable
```

Task 006 must not use `advanceable=True`. BranchFingerprint evidence is not projection advancement, even if the source projection has `advance_valid=True`.

## Required value objects

Use frozen dataclasses unless the existing codebase uses a different immutable pattern.

Recommended objects:

```python
@dataclass(frozen=True)
class SlopeFlowSample:
    control: int | float
    observable: int | float
    source_trace_id: str | None = None
    detection_trace_id: str | None = None
    detection_status: str | None = None
```

```python
@dataclass(frozen=True)
class SlopeFlowModel:
    name: str
    expected_slope: int | float
```

```python
@dataclass(frozen=True)
class SlopeSegmentEvidence:
    left_index: int
    right_index: int
    delta_log_control: float
    delta_log_observable: float
    projective_slope_trace_id: str
    scalar_slope_trace_id: str | None
    slope: float | None
    refusal_reason: str | None
```

```python
@dataclass(frozen=True)
class SlopeModelResidual:
    model_name: str
    expected_slope: float
    segment_residuals: tuple[float, ...]
    max_abs_segment_residual: float | None
    within_declared_band: bool | None
```

```python
@dataclass(frozen=True)
class SlopeFlowComparisonValue:
    samples: tuple[SlopeFlowSample, ...]
    usable_sample_indices: tuple[int, ...]
    segment_evidence: tuple[SlopeSegmentEvidence, ...]
    models: tuple[SlopeFlowModel, ...]
    model_residuals: tuple[SlopeModelResidual, ...]
    declared_model_band: float | None
    selected_model_name: str | None
    comparison_kind: str
    source_trace_ids: tuple[str, ...]
```

```python
@dataclass(frozen=True)
class KqSlopeStabilityValue:
    control_values: tuple[float, ...]
    calibration_trace_ids: tuple[str, ...]
    calibration_statuses: tuple[str, ...]
    kq_values: tuple[float | None, ...]
    slope_flow_trace_id: str | None
    declared_stability_band: float | None
    stable: bool | None
    refusal_reasons: tuple[str, ...]
```

```python
@dataclass(frozen=True)
class BranchFingerprintValue:
    projection_trace_id: str
    projection_status: str
    requested_branch: str | None
    selected_branch: str | None
    projection_flags: dict[str, bool]
    transfer_flow_trace_id: str
    transfer_flow_status: str
    transfer_selected_model_name: str | None
    observable_kind: str
    kq_flow_trace_id: str | None
    kq_flow_status: str | None
    fingerprint_components: dict[str, object]
    source_trace_ids: tuple[str, ...]
```

Exact field names can vary if necessary, but the serialized evidence must preserve the same information.

Do not store only scalar slopes. Preserve segment-level evidence, model residual evidence, ProjectiveRatio trace IDs for slope ratios, and source trace IDs.

## Required result aliases

Expose concrete typed result aliases, following the Task 005 pattern:

```python
SlopeFlowComparisonResult = TypedResult[SlopeFlowComparisonValue, BranchFingerprintStatus]
KqSlopeStabilityResult = TypedResult[KqSlopeStabilityValue, BranchFingerprintStatus]
BranchFingerprintResult = TypedResult[BranchFingerprintValue, BranchFingerprintStatus]
```

Export them from the branch package.

## Required protocols

Define producer/consumer protocols for Task 006.

Recommended protocol names:

```text
SLOPE_FLOW_COMPARISON_PROTOCOL
KQ_SLOPE_STABILITY_PROTOCOL
BRANCH_FINGERPRINT_PROTOCOL
BRANCH_FINGERPRINT_CONSUMER_PROTOCOL
```

Protocols must be status-family aware and use Task 005 machinery.

Wrong-family typed results must fail explicitly. For example, a `MetrologyStatus.calibration_valid` result must not be mistaken for a BranchFingerprint slope-flow result just because it is selectable.

## Required transition rules

Add named transition rules for Task 006. They may live in the branch package and be exported publicly. Core must not import branch to register them.

Recommended rules:

```text
branch.slope_flow.model_comparison
branch.kq_flow.require_stable
branch.projection_to_fingerprint
branch.transfer_flow_to_fingerprint
branch.compose_fingerprint
```

The exact set may vary, but the report must document every rule and prove that BranchFingerprint composition uses named rules rather than local status if/else maps.

### Required semantic coverage

`branch.slope_flow.model_comparison` must cover every slope-flow/model status:

```text
slope_flow_observed
slope_model_residuals
slope_model_unique_match
slope_model_ambiguous
slope_model_no_match
slope_flow_insufficient_samples
slope_flow_indeterminate
slope_flow_proxy_uncalibrated
```

`branch.kq_flow.require_stable` must accept only:

```text
kq_flow_stable
```

and refuse:

```text
kq_flow_unstable
kq_flow_indeterminate
kq_flow_uncalibrated
```

`branch.projection_to_fingerprint` must consume `ProjectionStatus` and map:

```text
projection_transverse        -> usable projection evidence
projection_tangent_contact   -> usable projection evidence, but advance remains invalid
projection_linear            -> usable projection evidence
projection_no_real_root      -> incomplete fingerprint evidence
projection_identity          -> incomplete fingerprint evidence
projection_no_solution       -> incomplete fingerprint evidence
projection_selection_refused -> incomplete fingerprint evidence
```

Do not treat `projection_tangent_contact` as projection failure. It has a valid selected root but not a valid projection advance.

`branch.transfer_flow_to_fingerprint` must consume `BranchFingerprintStatus` from slope-flow comparison and map:

```text
slope_flow_observed          -> usable transfer evidence
slope_model_residuals        -> usable transfer evidence
slope_model_unique_match     -> usable transfer evidence with selected model
slope_model_ambiguous        -> unidentified fingerprint evidence
slope_model_no_match         -> unidentified fingerprint evidence
slope_flow_insufficient_samples -> incomplete fingerprint evidence
slope_flow_indeterminate     -> incomplete fingerprint evidence
slope_flow_proxy_uncalibrated -> proxy-uncalibrated fingerprint evidence
```

`branch.compose_fingerprint` must combine projection evidence, transfer evidence, and optional proxy stability evidence into one of:

```text
fingerprint_complete
fingerprint_unidentified
fingerprint_incomplete
fingerprint_proxy_uncalibrated
```

Generic `join_statuses(...)` must remain conservative. Task 006 must not add a universal mixed-family join.

## Required public APIs

Exact function names can vary if the package style requires, but Task 006 must expose equivalent APIs.

### 1. Direct slope-flow model comparison

```python
def compare_slope_flow_to_models(
    samples: Sequence[SlopeFlowSample],
    models: Sequence[SlopeFlowModel] = (),
    *,
    declared_model_band: float | None = None,
    comparison_kind: str = "direct_transfer",
) -> SlopeFlowComparisonResult:
    ...
```

Behavior:

```text
- Accept finite scalar samples only.
- Each sample has a finite positive control value.
- Each usable sample has a finite nonzero observable magnitude.
- If a sample carries limit-of-detection evidence, only detected evidence is usable for slope computation.
- below_limit_of_detection, detection_indeterminate, and identity_zero samples remain observable evidence but are not loggable slope samples.
- At least two usable samples are required.
- Segment slopes are finite-difference slopes in log-magnitude space:
  delta_log_observable / delta_log_control
- The ratio above must be represented through ProjectiveRatio and explicit scalarization, not direct division.
- If ProjectiveRatio scalarization refuses, the slope-flow result is typed as indeterminate and preserves refusal evidence.
- If no models are provided, emit slope_flow_observed.
- If models are provided and declared_model_band is None, emit slope_model_residuals.
- If models and a declared_model_band are provided, compare each model by max absolute segment residual.
- A model is inside the band only if every segment residual is inside the declared band.
- Exactly one in-band model emits slope_model_unique_match.
- More than one in-band model emits slope_model_ambiguous.
- No in-band model emits slope_model_no_match.
```

`declared_model_band` must be finite and nonnegative when supplied. It must be stored in the value. It is explicit model policy evidence, not a hidden correction constant.

For float inputs, Task 006 uses finite Python host arithmetic. `math.log`, subtraction, absolute value, and ProjectiveRatio scalarization are not symbolic algebra and are not arbitrary precision.

### 2. Proxy `K_q` slope-stability check

```python
def compare_kq_slope_stability(
    control_values: Sequence[int | float],
    calibration_results: Sequence[ProxyCalibrationResult],
    *,
    declared_stability_band: float | None,
) -> KqSlopeStabilityResult:
    ...
```

Behavior:

```text
- control_values and calibration_results must have the same length.
- control values must be finite positive scalars.
- Each calibration result must be validated through the existing valid-proxy-calibration protocol or the canonical Task 005 transition rule.
- Do not locally reimplement calibration validity rules.
- If any calibration result is invalid, indeterminate, uncalibrated, wrong-family, or refused, emit kq_flow_uncalibrated and preserve refusal evidence.
- Extract scalar K_q values only from valid calibration evidence.
- K_q values must be finite and nonzero to enter log-magnitude slope flow.
- Compute finite-difference slopes of log|K_q| against log control.
- Each segment slope must use ProjectiveRatio and explicit scalarization.
- declared_stability_band is required to emit kq_flow_stable or kq_flow_unstable.
- If declared_stability_band is missing, emit kq_flow_indeterminate while preserving computed residual evidence if available.
- Emit kq_flow_stable only when every segment of D log K_q is inside the declared stability band around zero.
- Emit kq_flow_unstable when at least one segment lies outside the declared stability band.
- Emit kq_flow_indeterminate for insufficient samples or honest scalarization/log-domain failure.
```

This is the first implementation of the `D log K_q -> 0` proxy-stability requirement. It is still scalar and point-sequence based. No continuous calculus, symbolic derivatives, or adaptive sampling.

### 3. BranchFingerprint composition

```python
def build_branch_fingerprint(
    projection_result: ProjectionResultV4,
    transfer_flow_result: SlopeFlowComparisonResult,
    *,
    observable_kind: str = "direct_transfer",
    kq_flow_result: KqSlopeStabilityResult | None = None,
) -> BranchFingerprintResult:
    ...
```

Allowed observable kinds:

```text
direct_transfer
proxy
```

Behavior:

```text
- Validate projection_result against the projection status family/protocol.
- Validate transfer_flow_result against the BranchFingerprint slope-flow status family/protocol.
- For observable_kind="direct_transfer", do not require K_q stability evidence.
- For observable_kind="proxy", require kq_flow_result and require kq_flow_stable through the named transition rule.
- If proxy evidence is missing, refused, unstable, indeterminate, or uncalibrated, emit fingerprint_proxy_uncalibrated.
- Use named transition rules for projection evidence, transfer-flow evidence, and proxy-stability evidence.
- Do not recompute roots, projection, calibration, or ProjectiveRatio values.
- Do not choose a branch. Preserve the branch already requested/selected by projection evidence.
- Do not reinterpret projection advance semantics. Tangent contact remains not advance-valid.
- Preserve source trace IDs for projection, transfer flow, K_q flow, ProjectiveRatio slope ratios, and calibration evidence.
```

Composition status:

```text
fingerprint_complete:
  usable projection evidence + usable transfer-flow evidence + stable proxy evidence if proxy mode

fingerprint_unidentified:
  usable projection evidence + transfer-flow evidence exists but model comparison is ambiguous or no model matches

fingerprint_incomplete:
  projection evidence or transfer-flow evidence is incomplete or indeterminate

fingerprint_proxy_uncalibrated:
  proxy observable mode without stable K_q flow evidence
```

`fingerprint_complete` is not a domain branch identity. It is a complete generic fingerprint evidence object.

## Slope-flow mathematics

For usable adjacent samples `(x_i, y_i)` and `(x_j, y_j)`:

```text
x_i > 0
x_j > 0
y_i != 0
y_j != 0
```

Compute:

```text
delta_log_control = log(x_j) - log(x_i)
delta_log_observable = log(abs(y_j)) - log(abs(y_i))
slope_projective = ProjectiveRatio(delta_log_observable, delta_log_control)
slope_scalar = scalarize_projective_ratio(slope_projective)
```

If scalarization refuses, the segment is not an honest finite slope. The result must preserve ProjectiveRatio and refusal trace evidence.

Do not compute:

```text
delta_log_observable / delta_log_control
log(abs(y) + eps)
log1p(...)
clamped logs
safe denominators
fallback slopes
```

A repeated control value creates zero `delta_log_control`. That is a projective slope stratum, not something to patch.

## Declared bands

Task 006 may use explicit declared bands:

```text
declared_model_band
declared_stability_band
```

These are policy/evidence fields. They must be:

```text
finite
nonnegative
stored in the result value
visible in serialization
```

They must not be defaulted to a hidden nonzero value.

Recommended defaults:

```text
declared_model_band=None
declared_stability_band=None
```

When a band is absent, report residual evidence but do not claim unique model identification or K_q stability.

Do not use the words or concepts `epsilon`, `eps`, `tolerance`, or `threshold` in source code for this behavior. The explicit field is a declared band.

## Serialization requirements

All new values must serialize strictly through existing V4 serialization.

Serialization must preserve:

```text
status
status family/protocol identity where existing serialization already preserves it
validity fields
conditioning status
provenance
samples
usable sample indices
segment slopes and refusals
ProjectiveRatio trace IDs for slope ratios
model definitions
model residuals
declared bands
selected model name, if any
K_q calibration trace IDs
K_q flow status
projection status and flags
source trace IDs
```

No `inf`, `nan`, scalar sentinel, or stringified exception should appear as a numeric value.

## Conditioning requirements

Recommended conditioning mapping:

```text
well-conditioned:
  slope_flow_observed
  slope_model_residuals
  slope_model_unique_match
  kq_flow_stable
  fingerprint_complete

warning:
  slope_model_ambiguous
  slope_model_no_match
  slope_flow_insufficient_samples
  slope_flow_indeterminate
  slope_flow_proxy_uncalibrated
  kq_flow_unstable
  kq_flow_indeterminate
  kq_flow_uncalibrated
  fingerprint_unidentified
  fingerprint_incomplete
  fingerprint_proxy_uncalibrated
```

If the existing code uses different conditioning enum names, map these semantics to the existing enum.

## Required tests

Create Task 006 tests under `tests/`. Recommended files:

```text
tests/test_task006_slope_flow_direct.py
tests/test_task006_kq_slope_stability.py
tests/test_task006_branch_fingerprint.py
tests/test_task006_transition_rules.py
tests/test_task006_serialization.py
tests/test_task006_source_purity.py
```

### Red test expectation

Before implementation, the Task 006 slice should fail during collection because `lloyd_v4.branch` and/or `BranchFingerprintStatus` do not exist.

### Direct slope-flow tests

Test at least:

```text
- finite positive controls and nonzero observables emit slope_flow_observed when no models are supplied;
- supplied models without declared_model_band emit slope_model_residuals and no selected model;
- a declared_model_band with exactly one in-band model emits slope_model_unique_match;
- a declared_model_band with multiple in-band models emits slope_model_ambiguous;
- a declared_model_band with no in-band models emits slope_model_no_match;
- fewer than two usable samples emits slope_flow_insufficient_samples;
- repeated control values produce slope_flow_indeterminate through ProjectiveRatio scalarization/refusal, not division by zero;
- zero observable without identity handling is not log-smoothed and emits an indeterminate or insufficient result;
- limit-of-detection results marked below_limit_of_detection, detection_indeterminate, or identity_zero are preserved but not used as loggable slope samples.
```

### K_q slope-stability tests

Test at least:

```text
- valid pointwise calibration results with constant K_q and declared_stability_band emit kq_flow_stable;
- valid pointwise calibration results with changing K_q outside the declared band emit kq_flow_unstable;
- missing declared_stability_band emits kq_flow_indeterminate, not stable;
- invalid, indeterminate, or proxy_uncalibrated Task 004 calibration results emit kq_flow_uncalibrated;
- wrong-family typed results are rejected explicitly;
- K_q slope segments preserve calibration trace IDs and ProjectiveRatio slope trace IDs;
- calibration validity uses the existing Task 004/Task 005 protocol/transition path rather than local status checks.
```

### BranchFingerprint tests

Test at least:

```text
- projection_transverse + usable direct transfer flow emits fingerprint_complete;
- projection_linear + usable direct transfer flow emits fingerprint_complete;
- projection_tangent_contact + usable direct transfer flow emits fingerprint_complete while preserving advance_valid=False;
- projection_no_real_root, projection_identity, projection_no_solution, or projection_selection_refused produce fingerprint_incomplete;
- ambiguous or no-match model evidence produces fingerprint_unidentified;
- proxy observable mode without kq_flow_result emits fingerprint_proxy_uncalibrated;
- proxy observable mode with kq_flow_unstable, kq_flow_indeterminate, or kq_flow_uncalibrated emits fingerprint_proxy_uncalibrated;
- proxy observable mode with kq_flow_stable and usable projection/transfer evidence emits fingerprint_complete;
- BranchFingerprint preserves requested/selected projection branch labels and does not choose a new branch.
```

### Transition-rule tests

Test at least:

```text
- Task 006 transition rules are exported and importable;
- every BranchFingerprintStatus used by slope-flow is accepted, mapped, or explicitly refused by the relevant transition rule;
- ProjectionStatus to fingerprint composition uses the named transition rule;
- kq_flow require-stable accepts only kq_flow_stable;
- generic join_statuses remains conservative for mixed families;
- no local composition map can bypass named rules in build_branch_fingerprint.
```

### Serialization tests

Test at least:

```text
- slope-flow comparison serializes samples, segment evidence, model residuals, declared bands, selected model, validity, conditioning, and provenance;
- kq-flow stability serializes calibration traces, scalar K_q values, declared stability band, and stable/unstable/indeterminate evidence;
- BranchFingerprint serializes projection flags, transfer-flow summary, proxy stability summary, source trace IDs, validity, conditioning, and provenance;
- typed refusals or indeterminate values serialize without numeric sentinels.
```

### Existing-flow regression

Run full suite and ensure all previous Task 001 through Task 005 tests still pass.

Task 006 must not alter existing behavior or serialization for ProjectiveRatio, StratifiedQuadraticRoots, ProjectionResultV4, metrology, or core transition rules.

## Source-purity audits

Run these audits after implementation. Adjust only for actual package names if they differ.

Clean-room and legacy audit:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
```

Hidden correction audit:

```bash
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance" src/lloyd_v4/branch src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Dependency-direction audit:

```bash
rg "lloyd_v4\.branch|from lloyd_v4\.branch|import .*branch" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology -n
```

Earlier-layer leakage audit:

```bash
rg "branch_fingerprint|fingerprint|slope_flow|flow_model" src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology -n
```

Metrology/projection dependency audit:

```bash
rg "lloyd_v4\.metrology|from lloyd_v4\.metrology|import .*metrology" src/lloyd_v4/primitives src/lloyd_v4/projection -n
rg "lloyd_v4\.projection|from lloyd_v4\.projection|import .*projection" src/lloyd_v4/primitives src/lloyd_v4/metrology -n
```

Deferred-feature audit:

```bash
rg "finite_eta|equation_refinery|refinery|history_trace|domain_consumer|domain_classifier|bearing|aerospace|betting|scanner" src/lloyd_v4 -n
```

Compatibility audit:

```bash
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

If an audit catches an intended Task 006 identifier, narrow the audit path rather than renaming architectural concepts into nonsense. Do not rename existing core provenance fields.

## Required reports

Create Task 006 reports under:

```text
Build_Docs/Reports/task006/
```

Required files:

```text
Build_Docs/Reports/task006/task006_summary.md
Build_Docs/Reports/task006/branch_fingerprint_status_table.md
Build_Docs/Reports/task006/status_transition_rules.md
Build_Docs/Reports/task006/design_decisions.md
```

### task006_summary.md

Include:

```text
files created
files modified
behavior summary
red test result
task slice result
full suite result
source audit results
deviations
Task 007 readiness
```

### branch_fingerprint_status_table.md

Include a table with:

```text
status
input condition
value shape
validity mapping
conditioning behavior
protocol behavior
refusal/indeterminate behavior
```

### status_transition_rules.md

Document all Task 006 transition rules, including:

```text
input protocol
output protocol
input status family
output status family
accepted statuses
refused statuses
mapped statuses
context keys
notes
```

### design_decisions.md

Document at least:

```text
why slope ratios use ProjectiveRatio
why model bands are explicit evidence
why K_q pointwise validity is not enough
why BranchFingerprint is not a domain classifier
why tangent contact remains not advance-valid
why no hidden log offset or stabilization is allowed
why BranchFingerprint composes through named transition rules
```

## Non-goals

Do not implement:

```text
finite-eta correction
a protocol-aware equation refinery
history-aware status traces
a domain consumer
a branch classifier for any named real-world domain
a flow integrator
spatial projection
adaptive sampling
symbolic differentiation
arbitrary-precision arithmetic
complex roots
new quadratic formulas
new projection policies
a nearest/principal/default branch policy
K_G as engine identity
V3 fixtures or V3 comparison tests
adapters, bridges, compatibility shims, downgrade modes, or cross-engine calls
```

Task 006 may compare observed slope-flow evidence to declared models. It must not claim domain branch identity.

## Acceptance criteria

Task 006 is complete when:

```text
1. BranchFingerprintStatus exists with the required semantic coverage.
2. A branch package exists and exposes slope-flow, K_q stability, and BranchFingerprint APIs.
3. Slope-flow segment ratios use ProjectiveRatio and explicit scalarization.
4. Direct slope-flow comparison emits typed results for observed, residuals, unique model, ambiguous model, no match, insufficient samples, and indeterminate cases.
5. K_q slope-stability consumes Task 004 calibration results through existing validation/transition paths.
6. Proxy fingerprints require stable K_q flow evidence.
7. BranchFingerprint composition consumes ProjectionResultV4 and slope-flow typed results through named transition rules.
8. Tangent contact remains valid evidence but not advance-valid.
9. BranchFingerprint preserves source trace IDs and branch labels.
10. No previous Task 001 through Task 005 behavior changes.
11. New serialization tests pass.
12. New transition-rule coverage tests pass.
13. Source audits return no matches.
14. Full test suite passes.
15. Task 006 reports are written under Build_Docs/Reports/task006.
```

## Task 007 readiness

Task 007 should be scoped as:

```text
Protocol-aware equation refinery
```

Task 007 may consume BranchFingerprint evidence to test status-preserving, protocol-preserving rewrite acceptance. It must not be implemented in Task 006.
