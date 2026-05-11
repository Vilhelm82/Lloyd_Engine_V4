# Status Calculus

The status calculus defines how typed results compose. It is intentionally minimal in M0, but it is load-bearing: unknown or mixed status is never silently accepted.

## Status Categories

Domain status: Whether the input lies inside the mathematical domain of the primitive. Examples: `defined`, `undefined`, `out_of_domain`, `mixed`, `unknown`.

Stratum status: Which geometric region the point inhabits. Examples: regular region, boundary, degeneracy, or primitive-specific strata.

Validity status: Whether the result is usable for the requested operation. Validity is multi-field and includes defined, finite, selectable, advanceable, and observable.

Conditioning status: Whether the computation is well-conditioned, ill-conditioned, singular, warning-bearing, or unknown.

Metrology status: What finite observation can honestly say. Required zero vocabulary: `identity_zero`, `below_limit_of_detection`, `indeterminate`, and `detected_nonzero`.

Protocol status: Whether producer and consumer contracts are compatible. Examples: `ok`, `violation`, `uncertain`, `scalarization_refused`.

Provenance status: Whether path evidence is complete, compacted, lost, or unknown.

## Minimal Composition Rules

Undefined domain blocks scalarization. A consumer may still accept undefined domain if it is explicitly a domain-analysis consumer, but scalar output is refused by default.

Domain strata must not be silently converted into numeric values. Boundary, degeneracy, and out-of-domain states are statuses, not special floats.

Invalid input status propagates unless a primitive explicitly declares that it handles the invalid stratum and emits a new named status.

A consumer must declare accepted statuses. The declaration is part of the protocol, not an informal docstring.

Unhandled status produces `ProtocolViolation`. This includes status categories the consumer never listed and primitive-specific statuses it did not exhaustively handle.

Conditioning warnings propagate unless explicitly resolved. Resolution requires a named operation or policy and must be represented in provenance.

Measurement-resolution statuses are not mathematical degeneracies. `below_limit_of_detection` is not `identity_zero`; `indeterminate` is not proof of zero.

Status joins must be explicit and named. A mixed status join is rejected unless a named composition rule says how to combine those statuses.

Unknown or mixed status is not silently accepted. `unknown` may pass only to consumers that explicitly accept uncertainty.

## Early Abstract Examples

Ratio `n/d`:

- `finite_ratio`: `d` is detected or proven nonzero and scalarization may be available.
- `signed_zero`: `n` is zero under the declared metrology and `d` is nonzero, preserving sign where meaningful.
- `infinite_direction`: `d` is zero and `n` is nonzero, producing a projective direction rather than a scalar infinity.
- `indeterminate`: `n` and `d` are zero or unresolved in a way that prevents a unique scalar or direction.

Quadratic root strata:

- `two_real_roots`: the quadratic stratum has two real roots.
- `repeated_root`: the discriminant stratum collapses to a repeated real root.
- `no_real_root`: the real root protocol refuses scalar real roots.
- `linear_root`: the quadratic coefficient vanishes and the equation is linear.
- `constant_identity`: all coefficients vanish and every input satisfies the equation.
- `constant_no_solution`: the variable terms vanish and the constant term prevents a solution.

Transfer observation strata:

- `transfer_observed`: the local transfer was finite and not dominated by cancellation at the declared precision.
- `transfer_cancellation_dominated`: the finite endpoint difference is below the declared precision floor and is not selectable as a slope observation.
- `transfer_non_finite`: an endpoint or computed transfer is non-finite.
- `transfer_domain_refused`: the callable raised or returned a non-numeric value at a sampled point.
- `transfer_delta_indeterminate`: the perturbation is zero, so no finite-difference observation exists.

Log-log slope strata:

- `slope_observed`: enough transfer observations survived filtering and the log-log sample distribution was non-degenerate.
- `slope_insufficient_data`: fewer than three usable transfer observations were available after filtering.
- `slope_degenerate_input`: the usable log-log sample distribution had zero variance in the base coordinate or transfer coordinate.

Directional AlphaProbe strata:

- `alpha_regular_integer`: α was observed cleanly and matched a declared positive-integer regime.
- `alpha_fractional_branch`: α was observed cleanly and classified as a positive non-integer branch.
- `alpha_negative_singularity`: α was observed cleanly and is negative, indicating blow-up toward the branch point.
- `alpha_model_ambiguous`: α matched multiple caller-declared models.
- `alpha_model_no_match`: α matched no caller-declared model.
- `alpha_cancellation_dominated`: transfer observations were dominated by finite-precision cancellation before enough usable samples remained.
- `alpha_insufficient_data`: fewer than three usable transfer observations remained.
- `alpha_domain_refused`: the observable refused the domain for the dominant failure mode.
- `alpha_nonfinite`: non-finite transfer or slope evidence blocked finite α observation.
- `alpha_indeterminate`: the slope fit was geometrically degenerate.
- `alpha_zero_boundary`: observed α is inside the precision-aware zero-boundary envelope `max(K_BOUNDARY * standard_error, ALPHA_NUMERIC_FLOOR)`. This reports a slope indistinguishable from the α = 0 boundary, not a negative power law.
- `alpha_unstable_window`: nested-window α span is both material and significant: `span > materiality_threshold` and `span > K_DRIFT * propagated_window_error`. This reports that finite-window α evidence is not stable enough for algebraic consumption.

Directional AlphaProbe classification precedence is:

```text
pre-existing refusals
→ alpha_zero_boundary
→ alpha_unstable_window
→ declared model matching
→ sign/algebraic classification
```

Nested-window evidence is generated by sequentially dropping the largest h-value from the fitted h-grid while at least three h-points remain. The primitive records `AlphaWindowFit` entries, alpha min/max/span, propagated window error, and an `AlphaWindowStabilityStatus` of `stable`, `unstable`, or `not_tested`.

Scalar AlphaJetBundle strata:

- `scalar_jet_regular_integer_alpha`: the embedded AlphaProbe emitted `alpha_regular_integer`; the local probe is compatible with integer-power behavior at the scalar point.
- `scalar_jet_fractional_alpha_branch`: the embedded AlphaProbe emitted `alpha_fractional_branch`; the local probe is compatible with fractional-power behavior.
- `scalar_jet_negative_alpha_singularity`: the embedded AlphaProbe emitted `alpha_negative_singularity`; this is inherited by explicit mapping, though genuine finite-point local probes normally tend to zero and may not realize negative α directly.
- `scalar_jet_alpha_model_refused`: the embedded AlphaProbe emitted `alpha_model_ambiguous` or `alpha_model_no_match`; declared models conflict with observed α evidence.
- `scalar_jet_alpha_cancellation_dominated`: the embedded AlphaProbe emitted `alpha_cancellation_dominated`; the h-grid and eta are below finite-precision observability for enough transfers.
- `scalar_jet_alpha_indeterminate`: the embedded AlphaProbe emitted `alpha_insufficient_data` or `alpha_indeterminate`; the h-grid is too short or degenerate.
- `scalar_jet_alpha_zero_boundary`: the embedded AlphaProbe emitted `alpha_zero_boundary`; the local probe reached the α = 0 boundary envelope and is not selectable as algebraic evidence.
- `scalar_jet_alpha_unstable_window`: the embedded AlphaProbe emitted `alpha_unstable_window`; nested-window evidence was not stable enough for algebraic consumption.
- `scalar_jet_domain_refused`: f(x0) refused evaluation, returned non-numeric, or the embedded AlphaProbe emitted `alpha_domain_refused`.
- `scalar_jet_nonfinite`: f(x0) was non-finite or the embedded AlphaProbe emitted `alpha_nonfinite`.
- `scalar_jet_protocol_refused`: reserved for recoverable downstream protocol refusal.

Scalar AlphaJetBundle uses the explicit AlphaProbeStatus to ScalarAlphaJetBundleStatus mapping above. It does not reclassify by inspecting observed α directly.

Singular AlphaJetBundle strata:

- `singular_jet_regular_integer_alpha`: the embedded AlphaProbe emitted `alpha_regular_integer`; the singular-direct probe `g_singular(h)=f(x0+h)` is compatible with integer-power behavior at the probed boundary.
- `singular_jet_fractional_alpha_branch`: the embedded AlphaProbe emitted `alpha_fractional_branch`; the singular-direct probe is compatible with fractional-power behavior.
- `singular_jet_negative_alpha_singularity`: the embedded AlphaProbe emitted `alpha_negative_singularity`; the singular-direct probe observed blow-up toward `x0`.
- `singular_jet_alpha_model_refused`: the embedded AlphaProbe emitted `alpha_model_ambiguous` or `alpha_model_no_match`; declared models conflict with observed α evidence.
- `singular_jet_alpha_cancellation_dominated`: the embedded AlphaProbe emitted `alpha_cancellation_dominated`; the h-grid and eta are below finite-precision observability for enough transfers.
- `singular_jet_alpha_indeterminate`: the embedded AlphaProbe emitted `alpha_insufficient_data` or `alpha_indeterminate`; the h-grid is too short or degenerate.
- `singular_jet_alpha_zero_boundary`: the embedded AlphaProbe emitted `alpha_zero_boundary`; the singular-direct probe reached the α = 0 boundary envelope and is not selectable as algebraic evidence.
- `singular_jet_alpha_unstable_window`: the embedded AlphaProbe emitted `alpha_unstable_window`; nested-window evidence was not stable enough for algebraic consumption.
- `singular_jet_domain_refused`: the embedded AlphaProbe emitted `alpha_domain_refused`; all usable singular-direct samples were refused before α evidence could be observed.
- `singular_jet_nonfinite`: the embedded AlphaProbe emitted `alpha_nonfinite`; non-finite transfer or slope evidence blocked finite α observation.
- `singular_jet_protocol_refused`: reserved for recoverable downstream protocol refusal.

Singular AlphaJetBundle is a Layer 1 sibling of Scalar AlphaJetBundle, not a mode of it. It constructs only the singular-direct callable `g_singular(h)=f(x0+h)`, never evaluates `f(x0)`, and delegates α measurement to Directional AlphaProbe. It uses the explicit AlphaProbeStatus to SingularAlphaJetBundleStatus mapping above and does not reclassify by inspecting observed α directly. No structurally unreachable status cases are introduced by this primitive; reserved protocol refusal remains available for future typed consumers.

Both AlphaJetBundle siblings map AlphaProbe statuses 1:1 into their family-prefixed status spaces. They introduce no policy for zero-boundary or unstable-window evidence; AlphaProbe owns that observation.

Proxy observable:

- Calibrated proxy: `K_q` has been measured against a direct transfer observable and its stability condition is accepted by protocol.
- Uncalibrated proxy: the proxy is present but cannot be consumed as direct transfer evidence.
- Protocol result: a direct-transfer consumer must reject uncalibrated proxy status with `ProtocolViolation` or `ProtocolUncertain`.
