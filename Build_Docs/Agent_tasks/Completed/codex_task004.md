# Codex Task 004: Metrology Foundation, b_k Noise Floor and K_q Proxy Calibration

## Repository

Work in:

```text
/mnt/fast/Lloyd_Engine_V4
```

This is Lloyd Engine V4 clean-room work. V3 is reference evidence only. Do not import, call, bridge, compare against, adapt, or depend on V3 at runtime. Do not add legacy adapters, compatibility shims, downgrade modes, or cross-engine calls.

## Current verified baseline

Task 000 is complete. The M0 core substrate exists: statuses, validity, conditioning, provenance, typed results/refusals, protocol validation, conservative status calculus, strict serialization, and core errors.

Task 001 is complete. `ProjectiveRatio(n, d)` exists as the first primitive. It preserves raw projective coordinates `[n:d]`, classifies exact projective strata without dividing by `d`, and scalarizes only through an explicit protocol that may refuse.

Task 002 is complete. `StratifiedQuadraticRoots` exists as the second Layer 1 primitive. `stratified_quadratic_roots(a, b, c)` returns a typed root-state result with raw coefficients, discriminant evidence, branch-labeled projective root coordinates, validity, conditioning, and provenance. `select_quadratic_root(result, branch)` is explicit and protocol-validated.

Task 003 is complete. `ProjectionResultV4` and the exact quadratic projection protocol exist under `src/lloyd_v4/projection`. `exact_quadratic_projection(root_state_result, branch)` consumes validated Task 002 root-state results, rejects raw tuples/scalars/unrelated typed results, calls Task 002 selection for selectable branches, and emits structured projection results with separate `root_exists`, `projection_defined`, `selected_root_valid`, and `advance_valid` flags.

Task 003 verification baseline:

```text
Task 003 slice: 19 passed
Full suite: 65 passed
Source audits: no matches
```

The existing Task 000 provenance field `measurement_resolution` is intentionally allowed as substrate metadata. Do not rename, remove, or work around it.

Task 004 now implements:

```text
Metrology foundation: b_k noise floor and K_q calibration
```

## Goal

Implement the first Layer 2 metrology foundation without changing exact algebraic behavior from Tasks 001 through 003.

Task 004 introduces typed evidence for finite-precision observability:

```text
b_k noise-floor evidence
declared or estimated limit-of-detection evidence
classification of scalar observables against that evidence
K_q proxy-calibration evidence through ProjectiveRatio
protocol-validated acceptance/refusal for calibrated proxy evidence
```

Metrology is evidence. It is not a rescue path.

Task 004 may say:

```text
this observable is detected
this observable is below the declared/estimated limit of detection
this observable is indeterminate
this zero is explicitly identity-zero because identity evidence was provided
this proxy calibration is pointwise valid
this proxy calibration is invalid
this proxy calibration is indeterminate
this proxy is uncalibrated
```

Task 004 must not say:

```text
therefore change the ProjectiveRatio stratum
therefore change the quadratic discriminant stratum
therefore rescue a denominator
therefore rescue a discriminant
therefore clamp a projection
therefore choose a branch
therefore emit a branch fingerprint
```

Metrology may testify. It may not rewrite the verdict.

## Design principles

- Geometry precedes scalarization.
- Degeneracy is a stratum, not failure.
- Metrology annotates observability; it does not alter exact algebraic strata.
- A declared measurement limit is allowed only when it is explicit input evidence and serialized in the result.
- An estimated noise floor is allowed only when the estimation method and observations are explicit and serialized.
- No hidden epsilons, hidden tolerances, denominator floors, discriminant floors, clamps, rescue constants, default margins, confidence multipliers, or correction constants.
- Zero is not automatically identity-zero. Identity-zero requires explicit identity evidence.
- Proxy observables are untrusted until calibrated.
- `K_q` is a projective ratio first and a scalar only after explicit ProjectiveRatio scalarization succeeds.
- `calibration_valid` in Task 004 means pointwise finite nonzero `K_q` evidence only. It does not mean slope-flow stability or branch-fingerprint validity.
- Typed results compose by protocols and preserve provenance through compact parent trace IDs.
- No domain consumers, no branch fingerprints, no slope-flow model comparison, no finite-eta correction, and no equation refinery in Task 004.

## Required package boundary

Use the existing metrology package boundary.

Expected files:

```text
src/lloyd_v4/metrology/__init__.py
src/lloyd_v4/metrology/noise_floor.py
src/lloyd_v4/metrology/proxy_calibration.py
```

Modify core status/protocol modules only as needed to register metrology statuses and protocols in the same style used by Tasks 001 through 003.

Likely supporting changes:

```text
src/lloyd_v4/core/status.py
src/lloyd_v4/core/protocols.py
```

Do not place metrology machinery under:

```text
src/lloyd_v4/primitives/
src/lloyd_v4/projection/
```

Earlier layers may be consumed by metrology. Earlier layers must not import metrology.

## Required public API

Export these from `src/lloyd_v4/metrology/__init__.py`.

Names may vary if the existing codebase naming style strongly requires alternatives, but the public behavior must exist and any naming deviation must be documented in the Task 004 report.

```python
declare_bk_noise_floor(
    noise_floor: int | float,
    *,
    label: str = "b_k",
    unit: str | None = None,
    measurement_resolution: int | float | None = None,
) -> TypedResult
```

```python
estimate_bk_noise_floor(
    observations,
    *,
    label: str = "b_k",
    unit: str | None = None,
    measurement_resolution: int | float | None = None,
    method: str = "max_abs_observed",
) -> TypedResult
```

```python
classify_against_noise_floor(
    observable: int | float,
    noise_floor_result: TypedResult,
    *,
    observable_label: str = "observable",
    identity_evidence: bool = False,
) -> TypedResult
```

```python
calibrate_proxy_kq(
    proxy_observable: int | float,
    transfer_observable: int | float,
    *,
    proxy_label: str = "Y_q",
    transfer_label: str = "T",
    frequency_label: str | None = None,
) -> TypedResult
```

```python
proxy_uncalibrated(
    *,
    proxy_label: str = "Y_q",
    reason: str = "missing_calibration_evidence",
) -> TypedResult
```

```python
require_valid_proxy_calibration(calibration_result: TypedResult) -> TypedResult
```

Recommended frozen value objects, names may vary if the existing style suggests better names:

```python
NoiseFloorValue
LimitOfDetectionValue
ProxyCalibrationValue
```

The values must be structured immutable dataclasses or equivalent typed carriers. Do not return raw dictionaries, tuples, booleans, scalar-only values, or plain strings as the result value.

## Input contract

Task 004 remains scalar-only.

All numeric inputs must be finite real Python `int` or `float` values. Reject `nan`, `inf`, `-inf`, complex numbers, strings, arrays, tensors, and arbitrary numeric objects with `ProtocolViolationError` or the existing equivalent core validation error.

For float inputs, exact comparisons are exact with respect to the provided finite Python float values under host arithmetic. Task 004 does not attempt symbolic, arbitrary-precision, interval, or exact-real classification.

`noise_floor` and `measurement_resolution`, when provided as numeric evidence, must be finite and nonnegative.

No default noise floor is allowed for `declare_bk_noise_floor(...)`.

`estimate_bk_noise_floor(...)` supports only `method="max_abs_observed"` in Task 004. Do not add sample fitting, smoothing, robust statistics, multipliers, quantiles, confidence factors, or inferred margins.

`classify_against_noise_floor(...)` must accept only typed noise-floor results emitted by `declare_bk_noise_floor(...)` or `estimate_bk_noise_floor(...)`. Reject raw numeric floors and unrelated typed results through protocol validation.

## Required metrology statuses

Add a metrology status enum or status constants consistent with `core/status.py` style.

Task 004 metrology-producing functions must emit only these statuses after input validation succeeds:

```text
noise_floor_declared
noise_floor_estimated
noise_floor_indeterminate
detected
below_limit_of_detection
detection_indeterminate
identity_zero
calibration_valid
calibration_invalid
calibration_indeterminate
proxy_uncalibrated
```

Core protocol validation failures may use existing core refusal/error machinery. The eleven-status limit applies to validated Task 004 metrology results, not to unrelated invalid inputs.

## Noise-floor declaration semantics

`declare_bk_noise_floor(...)` records a caller-declared nonnegative finite noise floor.

Classification:

```text
finite noise_floor >= 0 -> noise_floor_declared
negative noise_floor    -> ProtocolViolationError
non-finite noise_floor  -> ProtocolViolationError
non-real noise_floor    -> ProtocolViolationError
```

Required `NoiseFloorValue` fields:

```text
label
noise_floor
method
unit
measurement_resolution
sample_count
observations
```

For declared values:

```text
method = declared
sample_count = 0
observations = ()
```

The declared value is evidence, not a correction constant.

## Noise-floor estimation semantics

`estimate_bk_noise_floor(...)` records an explicit estimate from scalar observations.

Task 004 supports only:

```text
method = max_abs_observed
```

Classification:

```text
non-empty finite observations -> noise_floor_estimated
empty observations            -> noise_floor_indeterminate
invalid method                -> ProtocolViolationError
non-finite observation         -> ProtocolViolationError
non-real observation           -> ProtocolViolationError
```

For non-empty observations:

```python
noise_floor = max(abs(x) for x in observations)
```

Do not add multipliers, confidence factors, inferred margins, hidden epsilons, or statistical rescue constants.

If all observations are exactly zero under host arithmetic, the estimated noise floor is exactly zero under host arithmetic. That is recorded evidence, not proof of perfect instrumentation.

Required `NoiseFloorValue` fields:

```text
label
noise_floor
method
unit
measurement_resolution
sample_count
observations
```

For indeterminate empty-observation evidence:

```text
noise_floor = None
method = max_abs_observed
sample_count = 0
observations = ()
```

## Limit-of-detection classification semantics

`classify_against_noise_floor(...)` classifies a finite scalar observable against typed noise-floor evidence.

Let:

```text
m = abs(observable)
L = noise_floor_result.value.noise_floor
```

If the noise-floor result is `noise_floor_indeterminate`, return `detection_indeterminate` and preserve the noise-floor trace ID.

If `identity_evidence=True`, then:

```text
observable == 0 -> identity_zero
observable != 0 -> ProtocolViolationError
```

If `identity_evidence=False`, then:

```text
m > L                 -> detected
m <= L and L > 0      -> below_limit_of_detection
m == 0 and L == 0     -> detection_indeterminate
```

Do not return `identity_zero` unless `identity_evidence=True`.

Required `LimitOfDetectionValue` fields:

```text
observable_label
observable_value
absolute_observable
noise_floor
noise_floor_trace_id
comparison
unit
identity_evidence
```

Required comparison labels:

```text
above_limit
below_limit
on_limit
exact_zero_without_identity_evidence
identity_zero_evidence
indeterminate_floor
```

Do not use `math.isclose`, `numpy.isclose`, `allclose`, relative tolerance, absolute tolerance, hidden epsilon, threshold, or margin logic.

## K_q proxy-calibration semantics

`calibrate_proxy_kq(...)` evaluates pointwise proxy calibration evidence.

The conceptual relation is:

```text
K_q = Y_q / T
```

where:

```text
Y_q = proxy_observable
T   = transfer_observable
```

Task 004 must represent `K_q` as a ProjectiveRatio first:

```python
kq_projective = projective_ratio(proxy_observable, transfer_observable)
```

Then scalarize explicitly through Task 001:

```python
kq_scalar = scalarize_projective_ratio(kq_projective)
```

Do not compute:

```python
proxy_observable / transfer_observable
```

inside Task 004.

Classification:

```text
Y_q != 0 and T != 0 -> calibration_valid
Y_q == 0 and T != 0 -> calibration_invalid
Y_q != 0 and T == 0 -> calibration_invalid
Y_q == 0 and T == 0 -> calibration_indeterminate
```

Rationale:

```text
finite nonzero K_q              -> pointwise valid calibration evidence
zero proxy against nonzero T     -> finite scalar ratio, but invalid multiplicative proxy evidence
nonzero proxy against zero T     -> infinite-direction ProjectiveRatio evidence, invalid calibration
zero proxy against zero T        -> indeterminate ProjectiveRatio evidence, indeterminate calibration
```

`calibration_valid` in Task 004 means pointwise finite nonzero `K_q` only. It does not mean `D log K_q -> 0`, slope-flow stability, branch-fingerprint validity, or transfer-exponent identification. Those belong to later tasks.

Required `ProxyCalibrationValue` fields:

```text
proxy_label
transfer_label
proxy_observable
transfer_observable
frequency_label
kq_projective_coordinates
kq_projective_trace_id
kq_projective_status
kq_scalar_value
kq_scalar_trace_id
calibration_reason
refusal_evidence
```

Rules:

```text
kq_projective_coordinates must preserve [Y_q:T]
kq_projective_trace_id is always present
kq_projective_status is always present
kq_scalar_value may be present only for calibration_valid
kq_scalar_trace_id may be present only when ProjectiveRatio scalarization succeeds
refusal_evidence is present when ProjectiveRatio scalarization refuses
```

If ProjectiveRatio scalarization refuses, do not produce scalar infinity, NaN, or a numeric sentinel.

## Uncalibrated proxy semantics

`proxy_uncalibrated(...)` returns a typed metrology result for missing calibration evidence.

Behavior:

```text
status = proxy_uncalibrated
value.reason = provided reason
validity.defined = False
validity.observable = True
```

Do not raise merely because calibration evidence is missing. Missing calibration is a typed state.

## Requiring valid proxy calibration

`require_valid_proxy_calibration(...)` is a protocol consumer.

Behavior:

```text
calibration_valid         -> accepted child TypedResult
calibration_invalid       -> typed refusal
calibration_indeterminate -> typed refusal
proxy_uncalibrated        -> typed refusal
unrelated typed result    -> ProtocolViolationError
raw scalar/object         -> ProtocolViolationError
```

The accepted child result must preserve the parent calibration trace ID.

## Protocols

Define protocol contracts using the existing V4 protocol machinery.

Suggested names:

```text
B_K_NOISE_FLOOR_PROTOCOL
LIMIT_OF_DETECTION_PROTOCOL
KQ_PROXY_CALIBRATION_PROTOCOL
VALID_PROXY_CALIBRATION_PROTOCOL
METROLOGY_RESULT_PROTOCOL
```

Producer protocols should emit only the Task 004 metrology statuses listed above.

`VALID_PROXY_CALIBRATION_PROTOCOL` accepts only:

```text
calibration_valid
```

and refuses:

```text
calibration_invalid
calibration_indeterminate
proxy_uncalibrated
```

Unhandled statuses must fail explicitly through the protocol path.

## Validity mapping

Use the existing `Validity` fields conservatively. Raw evidence should remain observable even when the metrology claim is not accepted.

Suggested mapping:

```text
noise_floor_declared:       defined=True,  finite=True,  selectable=True,  advanceable=False, observable=True
noise_floor_estimated:      defined=True,  finite=True,  selectable=True,  advanceable=False, observable=True
noise_floor_indeterminate:  defined=False, finite=False, selectable=False, advanceable=False, observable=True
detected:                   defined=True,  finite=True,  selectable=True,  advanceable=False, observable=True
below_limit_of_detection:   defined=True,  finite=True,  selectable=False, advanceable=False, observable=True
detection_indeterminate:    defined=False, finite=True,  selectable=False, advanceable=False, observable=True
identity_zero:              defined=True,  finite=True,  selectable=True,  advanceable=False, observable=True
calibration_valid:          defined=True,  finite=True,  selectable=True,  advanceable=False, observable=True
calibration_invalid:        defined=True,  finite=False, selectable=False, advanceable=False, observable=True
calibration_indeterminate:  defined=False, finite=False, selectable=False, advanceable=False, observable=True
proxy_uncalibrated:         defined=False, finite=False, selectable=False, advanceable=False, observable=True
```

For Task 004, `selectable=True` means future metrology/transfer consumers may consume the evidence. It does not mean scalar root selection or projection advance.

## Conditioning

Use conservative conditioning labels.

Suggested mapping:

```text
noise_floor_declared       -> well-conditioned or equivalent baseline state
noise_floor_estimated      -> warning or equivalent, because sample evidence may be limited
noise_floor_indeterminate  -> warning or indeterminate-equivalent state
detected                   -> well-conditioned or equivalent if floor evidence is valid
below_limit_of_detection   -> warning or equivalent limited-observability state
detection_indeterminate    -> warning or indeterminate-equivalent state
identity_zero              -> well-conditioned only when identity_evidence=True
calibration_valid          -> well-conditioned or equivalent if ProjectiveRatio scalarization succeeds
calibration_invalid        -> warning or equivalent unusable-calibration state
calibration_indeterminate  -> warning or indeterminate-equivalent state
proxy_uncalibrated         -> warning or refusal-appropriate state
```

Do not invent numeric condition estimates in Task 004.

## Provenance

Metrology provenance must include:

```text
operation_id
expression_path
precision
backend
device
measurement_resolution when available
parent trace IDs
metrology status
source operation identity
```

Specific provenance requirements:

```text
declare_bk_noise_floor        -> operation_id = declare_bk_noise_floor, expression_path = declared_bk_noise_floor
estimate_bk_noise_floor       -> operation_id = estimate_bk_noise_floor, expression_path = max_abs_observed_bk_noise_floor
classify_against_noise_floor  -> parent trace ID of the noise-floor result
calibrate_proxy_kq            -> parent trace ID of the ProjectiveRatio result, and scalarization child trace ID when scalarization succeeds
require_valid_proxy_calibration -> parent trace ID of the calibration result
```

Use compact parent trace IDs, not recursive parent result objects.

Do not rename, remove, or work around the existing Task 000 `measurement_resolution` provenance field.

## Serialization

Strict serialization must preserve:

```text
metrology status
noise-floor value
method
unit
measurement_resolution
sample count
observations
observable value
absolute observable
noise-floor trace ID
identity evidence
proxy observable
transfer observable
frequency label
projective K_q coordinates
ProjectiveRatio status
scalar K_q only when calibration_valid
validity fields
conditioning field
provenance fields
parent trace IDs
typed refusal evidence when applicable
```

Serialization must distinguish all Task 004 statuses.

Do not serialize metrology as only a boolean, confidence score, or scalar correction factor.

Do not serialize raw `nan`, `inf`, `-inf`, or non-JSON-safe values.

## Hard non-goals

Do not implement:

```text
branch fingerprints
slope-flow model comparison
D log K_q stability checks
transfer exponent fitting
finite_eta correction
history-aware status traces
protocol-aware equation refinery
domain consumers
spatial projection
flow integration
positive-time policies
nearest/principal/default branch policies
root-selection policy changes
projection advance policy changes
discriminant correction
denominator correction
automatic arbitrary precision
symbolic algebra
interval arithmetic
arrays or tensors
robust statistics
quantile estimators
smoothing
model fitting
hidden tolerance or hidden correction paths
V3 fixtures
V3 comparison tests
adapters
bridges
shims
compatibility modes
```

Task 004 is allowed to add `K_q` pointwise calibration evidence. It is not allowed to add a `BranchFingerprint` object or infer branch identity from calibration evidence.

## Required tests

Add tests under `tests/` with names similar to:

```text
tests/test_task004_bk_noise_floor.py
tests/test_task004_kq_calibration.py
tests/test_task004_metrology_protocols.py
tests/test_task004_metrology_serialization.py
tests/test_task004_no_reclassification.py
tests/test_task004_source_purity.py
```

Before implementation, the Task 004 slice should fail during collection because the metrology APIs/statuses do not exist.

After implementation, the Task 004 slice and full suite must pass.

### Noise-floor tests

Minimum tests:

```text
declare_bk_noise_floor(1e-6) -> noise_floor_declared
estimate_bk_noise_floor([1e-7, -2e-7, 5e-8]) -> noise_floor_estimated with noise_floor=2e-7
estimate_bk_noise_floor([]) -> noise_floor_indeterminate
negative declared noise_floor -> ProtocolViolationError
non-finite declared noise_floor -> ProtocolViolationError
non-finite observation -> ProtocolViolationError
invalid estimator method -> ProtocolViolationError
all-zero observations estimate zero but do not certify identity_zero
```

### Limit-of-detection tests

Minimum tests:

```text
observable=2e-6 with noise_floor=1e-6 -> detected
observable=5e-7 with noise_floor=1e-6 -> below_limit_of_detection
observable=1e-6 with noise_floor=1e-6 -> below_limit_of_detection
observable=0.0 with noise_floor=1e-6 and identity_evidence=False -> below_limit_of_detection
observable=0.0 with noise_floor=0.0 and identity_evidence=False -> detection_indeterminate
observable=0.0 with identity_evidence=True -> identity_zero
observable=2.0 with identity_evidence=True -> ProtocolViolationError
classify_against_noise_floor refuses or errors on unrelated typed results
classify_against_noise_floor rejects raw numeric noise floors
```

### K_q calibration tests

Minimum tests:

```text
calibrate_proxy_kq(6.0, 3.0) -> calibration_valid with scalar K_q=2.0 through ProjectiveRatio scalarization
calibrate_proxy_kq(0.0, 3.0) -> calibration_invalid and preserves ProjectiveRatio signed_zero status
calibrate_proxy_kq(6.0, 0.0) -> calibration_invalid and preserves ProjectiveRatio infinite_direction status
calibrate_proxy_kq(0.0, 0.0) -> calibration_indeterminate and preserves ProjectiveRatio indeterminate status
proxy_uncalibrated() -> proxy_uncalibrated
non-finite proxy or transfer observable -> ProtocolViolationError
frequency_label is preserved in calibration evidence
```

ProjectiveRatio composition tests:

```text
K_q calibration creates a ProjectiveRatio parent result
valid K_q calibration scalarizes only through the ProjectiveRatio scalarization protocol
invalid or indeterminate K_q calibration does not emit scalar infinity, NaN, or a numeric sentinel
K_q calibration does not directly divide proxy_observable by transfer_observable in Task 004 source
```

### Valid proxy calibration protocol tests

Minimum tests:

```text
require_valid_proxy_calibration(calibration_valid_result) -> accepted child TypedResult
require_valid_proxy_calibration(calibration_invalid_result) -> typed refusal
require_valid_proxy_calibration(calibration_indeterminate_result) -> typed refusal
require_valid_proxy_calibration(proxy_uncalibrated_result) -> typed refusal
require_valid_proxy_calibration(raw_scalar_or_unrelated_result) -> ProtocolViolationError
```

### No-reclassification tests

Task 004 must not alter prior exact strata.

Test representative results before and after metrology calls:

```text
projective_ratio(1.0, 0.0) remains infinite_direction
projective_ratio(0.0, 0.0) remains indeterminate
stratified_quadratic_roots(1.0, 0.0, 1.0) remains no_real_root
stratified_quadratic_roots(1.0, 2.0, 1.0) remains repeated_root
exact_quadratic_projection(repeated_root_result, "repeated") remains projection_tangent_contact
```

No metrology function may be used inside Tasks 001, 002, or 003 during Task 004.

### Serialization tests

Minimum tests:

```text
noise_floor_declared serializes raw declared floor and measurement_resolution
noise_floor_estimated serializes method, sample_count, and observations
noise_floor_indeterminate serializes empty observation evidence distinctly
detected serializes observable, floor, comparison, and parent trace
below_limit_of_detection serializes observable, floor, comparison, and parent trace
detection_indeterminate serializes exact-zero-without-identity evidence
identity_zero serializes identity_evidence=True
calibration_valid serializes ProjectiveRatio coordinates, ProjectiveRatio trace, scalarization trace, and scalar K_q
calibration_invalid serializes ProjectiveRatio status and does not emit scalar infinity
calibration_indeterminate serializes ProjectiveRatio refusal evidence and does not emit NaN
proxy_uncalibrated serializes reason
strict serialization rejects non-finite scalar payloads as in M0
```

## Required commands

Run the Task 004 red slice before implementation:

```bash
python -m pytest tests/test_task004_bk_noise_floor.py tests/test_task004_kq_calibration.py tests/test_task004_metrology_protocols.py tests/test_task004_metrology_serialization.py tests/test_task004_no_reclassification.py tests/test_task004_source_purity.py -q
```

After implementation, run:

```bash
python -m pytest tests/test_task004_bk_noise_floor.py tests/test_task004_kq_calibration.py tests/test_task004_metrology_protocols.py tests/test_task004_metrology_serialization.py tests/test_task004_no_reclassification.py tests/test_task004_source_purity.py -q
python -m pytest tests -q
```

Run the source-only clean-room audit:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
```

Expected result: no matches.

Run hidden-correction audits over existing algebra/projection layers:

```bash
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection -n
rg "disc_floor|discriminant_floor|clamp_discriminant|safe_sqrt|sqrt_guard|small_discriminant|threshold|tolerance" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Expected result: no matches.

Run the dependency-direction audit:

```bash
rg "lloyd_v4\.metrology|from lloyd_v4\.metrology|import .*metrology" src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Expected result: no matches.

Run the Task 004 branch-fingerprint and flow audit:

```bash
rg "branch_fingerprint|fingerprint|slope_flow|flow_model|finite_eta|domain_consumer" src/lloyd_v4/metrology src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Expected result: no matches.

Run the metrology-term leakage audit:

```bash
rg "b_k|K_q|noise_floor|calibration" src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Expected result: no matches.

Important:

```text
noise_floor, b_k, K_q, and calibration are legitimate Task 004 terms inside src/lloyd_v4/metrology.
measurement_resolution is legitimate substrate metadata in core provenance and must remain allowed.
```

## Required reports

Create:

```text
Build_Docs/Reports/task004/task004_summary.md
Build_Docs/Reports/task004/metrology_status_table.md
Build_Docs/Reports/task004/design_decisions.md
```

`task004_summary.md` must include:

```text
files created
files modified
behavior summary
red test result
Task 004 slice result
full suite result
source-audit results
deviations, if any
Task 005 readiness
```

`metrology_status_table.md` must include:

```text
status
input condition
value shape
validity mapping
conditioning behavior
protocol behavior
refusal/indeterminate behavior
```

`design_decisions.md` must document at least:

```text
Declared and estimated limits classify observability only.
Metrology does not reclassify exact geometric strata.
Zero is not identity-zero without explicit identity evidence.
K_q uses ProjectiveRatio and explicit scalarization rather than direct division.
Task 004 pointwise calibration does not claim slope-flow stability.
BranchFingerprint and slope-flow comparison are deferred.
Existing measurement_resolution provenance metadata remains unchanged.
```

## Expected files created

Likely created:

```text
src/lloyd_v4/metrology/noise_floor.py
src/lloyd_v4/metrology/proxy_calibration.py
tests/test_task004_bk_noise_floor.py
tests/test_task004_kq_calibration.py
tests/test_task004_metrology_protocols.py
tests/test_task004_metrology_serialization.py
tests/test_task004_no_reclassification.py
tests/test_task004_source_purity.py
Build_Docs/Reports/task004/task004_summary.md
Build_Docs/Reports/task004/metrology_status_table.md
Build_Docs/Reports/task004/design_decisions.md
```

Likely modified:

```text
src/lloyd_v4/core/status.py
src/lloyd_v4/core/protocols.py
src/lloyd_v4/metrology/__init__.py
```

Modify only what is necessary.

## Acceptance criteria

Task 004 is accepted when:

1. The metrology package exports noise-floor, limit-of-detection, K_q calibration, proxy-uncalibrated, and valid-calibration protocol APIs.
2. `declare_bk_noise_floor(...)` emits typed declared noise-floor evidence.
3. `estimate_bk_noise_floor(...)` emits typed estimated or indeterminate noise-floor evidence using only `max_abs_observed`.
4. `classify_against_noise_floor(...)` consumes validated typed noise-floor evidence and emits detected, below-limit, indeterminate, or explicit identity-zero statuses.
5. `observable == 0` is not treated as `identity_zero` unless `identity_evidence=True`.
6. `calibrate_proxy_kq(...)` emits typed K_q calibration evidence with statuses `calibration_valid`, `calibration_invalid`, or `calibration_indeterminate`.
7. `proxy_uncalibrated(...)` emits typed missing-calibration evidence.
8. `require_valid_proxy_calibration(...)` accepts only `calibration_valid` and returns typed refusals for invalid, indeterminate, and uncalibrated proxy evidence.
9. K_q calibration uses ProjectiveRatio and explicit scalarization rather than direct division.
10. Invalid and indeterminate K_q calibration never emits scalar infinity, NaN, or a numeric sentinel.
11. All Task 004 outputs preserve structured values, validity, conditioning, provenance, and parent trace IDs.
12. Existing `measurement_resolution` provenance remains unchanged.
13. Task 004 does not reclassify ProjectiveRatio, StratifiedQuadraticRoots, or ProjectionResultV4 outputs.
14. No hidden epsilon, tolerance rescue, denominator floor, discriminant floor, clamp, branch fallback, or legacy path is added.
15. No branch fingerprint, slope-flow model comparison, finite-eta correction, domain consumer, or equation refinery logic is added.
16. No V3 runtime dependency, fixture comparison, adapter, bridge, shim, or compatibility mode is added.
17. Existing Task 000 through Task 003 behavior remains green.
18. Task 004 reports are written under `Build_Docs/Reports/task004/`.
19. Task-specific tests, full-suite tests, and source-only audits all pass.

## Task 005 readiness

If Task 004 lands cleanly, Task 005 should be scoped as:

```text
BranchFingerprint object and slope-flow model comparison
```

Do not start Task 005 work in this ticket.
