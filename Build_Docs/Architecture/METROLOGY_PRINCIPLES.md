# Metrology Principles

## precision_floor as finite-precision observability evidence

The `_precision_floor` lookup in `typed_finite_difference` returns the
worst-case relative round-off envelope of forward-difference subtraction
for the declared precision. For `raw_python` (IEEE 754 double under
round-to-nearest), the floor is `2.0**-52`, derived from the per-operand
unit roundoff `u = 2^-53`:

```text
delta_g = g(f + delta_f) - g(f)
relative round-off in each operand <= u = 2^-53
worst-case absolute round-off in delta_g <= 2u * max(|g(f)|, |g(f+delta_f)|)
relative cancellation ratio |delta_g| / max(|g(f)|, |g(f+delta_f)|)
  is round-off-dominated when < 2u = 2^-52
```

`2u = 2^-52` also equals `sys.float_info.epsilon` (the relative spacing of
floats at 1.0). The floor is used solely to classify a transfer observation
as `TRANSFER_CANCELLATION_DOMINATED` when
`|delta_g| / max(|g(f)|, |g(f+delta_f)|) < precision_floor`.

Earlier text described this as the "unit roundoff"; that wording was
imprecise. The unit roundoff `u` is the per-operand bound. The floor used
here is `2u`, the cancellation threshold of the *subtraction*. The
distinction matters: `u` would be the right comparand against the magnitude
of a single operand; `2u` is the right comparand against the magnitude of
the difference.

The precision_floor IS:

- declared finite-precision observability evidence per Axiom 3
- status-only: it determines stratum classification, never computed values

The precision_floor IS NOT:

- a denominator floor
- a rescue constant
- a clamp
- a hidden tolerance

A transfer observation reaching `TRANSFER_CANCELLATION_DOMINATED` carries
the same numerical transfer value it would have without the floor; only
the stratum classification changes. Downstream consumers refuse the value
based on its `selectable=False` validity, not its number.

V4 treats finite-precision observation as part of the computation. The engine distinguishes mathematical structure from what the chosen instrument can observe.

## Finite-Precision Observation

Every numeric result is observed through a precision, backend, device, and expression path. These fields belong in provenance so later consumers can decide whether a result is adequate for their protocol.

## Declared Measurement Resolution

Measurement resolution may affect typed status resolution. It must not rescue an invalid value into a valid scalar. A tolerance is legitimate only when it changes a reported status under a declared instrument model, not when it hides invalid geometry.

## Precision and Path Attribution

Future metrology work will estimate precision/path effects using forms such as:

```text
C_{p,k} = a + u_p b_k
```

Task 000 only records the fields needed for this attribution.

## Noise Floor and Limit of Detection

`b_k` represents path-dependent finite-precision effects that may fall below the limit of detection. V4 must distinguish:

- `identity_zero`: mathematically proven or structurally exact zero
- `below_limit_of_detection`: not detected by the declared instrument
- `indeterminate`: available evidence cannot classify the quantity
- `detected_nonzero`: observed nonzero under the declared instrument

## Proxy Calibration

A proxy observable is not a direct transfer observable until calibrated. Calibration may use a factor such as:

```text
K_q(f) = Y_q(f) / T(f)
```

and a stability check such as `D log K_q(f)`. Until accepted by protocol, the proxy remains uncalibrated.

## Finite-Window and Finite-Step Bias

Window length, step size, sweep resolution, and sampling path can create observable bias. These are metrology properties and must be represented in provenance or status rather than hidden in implementation.

## AlphaProbe Boundary And Window Reliability

Directional AlphaProbe classifies an observed alpha as a zero-boundary
case when:

```text
abs(observed_alpha) <= max(K_BOUNDARY * standard_error, ALPHA_NUMERIC_FLOOR)
```

`K_BOUNDARY = 2.0` is the standard-error multiplier for the slope fit,
and `ALPHA_NUMERIC_FLOOR = 1e-9` is the precision-tied absolute floor
for alpha-near-zero observations. The boundary check is in alpha-space:
alpha near zero corresponds to log-log transfer slope near `-1`.

Nested-window reliability uses sequential-from-top windows. The full
h-grid is fit first; then the largest h-value is dropped and the fit is
recomputed until fewer than three h-points remain. At least three
windows of at least three points each are required. Shorter grids record
`alpha_stability_status = not_tested`.

For tested windows, AlphaProbe records:

```text
alpha_window_span = alpha_window_max - alpha_window_min
propagated_window_error = sqrt(sigma_min^2 + sigma_max^2)
```

Here `sigma_min` and `sigma_max` are the alpha standard errors of the
windows producing `alpha_window_min` and `alpha_window_max`. This is the
paired slope-difference propagation used in the transfer-paper
Section 5 reliability comparison.

The unstable-window rule fires only when both materiality and
significance hold:

```text
alpha_window_span > materiality_threshold
alpha_window_span > K_DRIFT * propagated_window_error
```

`K_DRIFT = 2.0`. The materiality threshold is the caller's
`declared_alpha_band` when provided; otherwise it is
`DEFAULT_ALPHA_MATERIALITY = 0.05`. Task 023b calibrated the default
against the actual sequential-from-top evidence: Fixture C stayed stable
with span about `1.5e-3`, while the iterated-log fixture on the
`1e-1..1e-7` grid became unstable with span about `5.95e-2`.

## Direct Transfer Versus Proxy Observable

Direct transfer evidence and proxy evidence are different statuses. A consumer requiring direct transfer must reject uncalibrated proxy results or mark them uncertain.
