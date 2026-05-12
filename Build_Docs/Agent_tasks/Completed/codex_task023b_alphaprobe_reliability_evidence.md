# Task 023b — AlphaProbe Reliability Evidence for Zero Boundary and Nested-Window Drift

## Repository

`/mnt/fast/Lloyd_Engine_V4`

V3 is reference-only (Axiom 10). V1 / OG engine are also reference-only.
Layer 2+ artifacts (metrology, branch, refinery, history, solver) are
V3-shaped deferred-consumer first-drafts and MUST NOT shape this task.

## Current Verified Baseline

- 379 tests passing (`pytest -x tests/`) as of Task 023 completion.
- Both L1 sibling primitives operational:
  `scalar_alpha_jet_bundle` (Task 019) and
  `singular_alpha_jet_bundle` (Task 021).
- Discovery campaign (Task 023) surfaced two substrate gaps:
  - **Fixture D** (`f(x) = -log(x)` at `x₀ = 0+`): singular bundle
    emitted `singular_jet_negative_alpha_singularity` with observed
    α ≈ -5.97e-11. Mechanically correct (α < 0) but geometrically
    misleading — the magnitude is well within slope-fit noise and
    represents an alpha-zero logarithmic boundary, not a negative
    power law.
  - **Fixture E** (`f(x) = log(-log(x))` at `x₀ = 0+`): singular bundle
    emitted `singular_jet_fractional_alpha_branch` with observed
    α ≈ 0.077. This is a finite-window average over slow non-algebraic
    drift, not a stable algebraic exponent. V4 currently has no way
    to express "this finite-window α is not stable enough to consume
    as algebraic."
- The repository is under git control; standard `git diff --stat`
  verification applies.

## Task Goal

> **AlphaProbe must not export algebraic-looking alpha classifications
> unless the finite-window evidence is both numerically non-boundary
> and nested-window stable enough for downstream composition.**

This task extends the AlphaProbe primitive with:

1. Two new typed strata: `alpha_zero_boundary` (for the D-class
   alpha-near-zero case) and `alpha_unstable_window` (for the E-class
   nested-window drift case).
2. Nested-window stability evidence on every AlphaProbeObservation
   that reaches the slope-fit stage, exposing per-window slope/alpha
   point estimates and their standard errors.
3. Precision-aware zero-boundary classification using the existing
   `standard_error` field combined with a precision-tied numeric
   floor.
4. Significance-and-materiality-gated unstable-window classification
   using nested-window slope span propagated against the per-window
   standard errors.
5. 1:1 wrapper translation in both sibling bundles. No bundle-level
   policy. The primitive owns the observation.

The task does **not** introduce a substrate model for what kind of
non-algebraic drift is present. `alpha_unstable_window` states only
that finite-window α evidence is not stable enough for algebraic
consumption — not what flavor of non-algebraic behavior it is.

## Source Labelling

- **(Theorem-derived)** From the transfer function paper:
  - **Section 3 (Robust branch transfer law):** for `g(f) = c·f^α·L(f)`
    near `f → 0+` with α ≠ 0, the limiting log-log transfer slope is
    α-1. Standard error of an OLS fit on `log|transfer|` vs `log(h)`
    gives the slope uncertainty.
  - **Section 4 (Finite-step and finite-window corrections):**
    subleading powers produce slope drift on finite sweeps that
    decays as `h^ρ`. The drift correction near a clean α should
    shrink as the window moves inward.
  - **Section 5 (Non-algebraic singularities and slope-flow):**
    for `g(f) = log log(1/f)`, finite-window slope is `-1 + 1/t`
    where `t = log(1/f)`. The slope drifts toward -1 as t grows
    but high local R² is preserved at any finite t. Section 5 uses
    nested-window slopes with paired standard errors:
    `propagated_error_pair = sqrt(σ_j² + σ_{j+1}²)`.
    This is the formula the task uses for slope-difference
    propagation across nested windows.

- **(V4-surface evidence)** Task 023 discovery campaign:
  observed α = -5.97e-11 (Fixture D) and α = 0.077 (Fixture E).
  Both classified into status families that geometrically overstate
  the algebraic evidence. The campaign also confirmed A, B, C, F
  classify honestly; A and B agree across bundles where applicable.

- **(Architectural)** The decision to defer nested-window evidence
  was made in Task 018. Task 023 produced the empirical case for
  promoting it from deferred to required. This task implements that
  promotion at the AlphaProbe layer only — Layer 2+ remains
  reference-only.

## Design Principles

- **The primitive owns the observation.** AlphaProbe is the layer
  that gains nested-window evidence, the zero-boundary check, and
  the two new strata. The bundles are wrappers that translate
  AlphaProbe statuses 1:1 into family-prefixed bundle statuses.
  No bundle-level policy. No re-classification at the bundle layer.

- **Conservative stratum naming.** The new strata are
  `alpha_zero_boundary` and `alpha_unstable_window`, not
  `alpha_non_algebraic_drift` or `alpha_logarithmic_divergence`.
  V4 reports what it can observe (slope near boundary, slope drifting
  beyond noise envelope) not what it can interpret (this is
  logarithmic, this is iterated-logarithmic). Axiom 11 compliance.

- **Materiality and significance both gate the unstable-window
  rule.** A drift must be both *material* (exceeds the consumer's
  declared band or the default materiality threshold) and
  *significant* (exceeds the propagated standard error of the slope
  span). Both conditions required. This prevents two failure modes:
  flagging statistical noise as drift, and flagging immaterial
  drift as substrate-breaking.

- **No new probe direction or fundamental geometry.** The slope fit
  remains the same. The h-grid handling remains the same. What
  changes is that the same fit is re-computed on sub-windows for
  stability evidence, and the classification logic uses the
  uncertainty fields it already had.

- **Precision-aware not magic-constant.** The zero-boundary envelope
  is `max(k * alpha_standard_error, alpha_numeric_floor)`. The
  numeric floor is a named precision-tied constant, not a free
  parameter. The k factor is documented in METROLOGY_PRINCIPLES.md
  with its derivation.

- **Guard fixtures lock the anti-overcorrection invariants.** Tiny
  stable exponents (`x^0.01`) must remain `fractional_branch`. Small
  stable negative exponents (`x^(-0.05)`) must remain
  `negative_singularity`. These cases become permanent regression
  tests at the bundle level.

- **Layer 2+ is not touched.** Manifests update for the new strata.
  STATUS_CALCULUS and METROLOGY_PRINCIPLES update for the new rules.
  Solver/branch/refinery/history are read-only.

## Substrate Changes

### 1. AlphaProbeObservation — new fields

Add the following fields to the existing
`AlphaProbeObservation` dataclass (location: same module as
`AlphaProbeStatus`; preserve `frozen=True, slots=True` and any
existing field ordering conventions):

- `nested_window_fits: tuple[AlphaWindowFit, ...] | None`
  - Tuple of per-window fit summaries. `None` when nested-window
    analysis was not performed (h-grid too short, or refused at an
    earlier stage). Tuple (possibly empty? no — non-None means at
    least the minimum number of windows ran).
- `alpha_window_min: float | None`
  - Minimum observed α across nested windows.
- `alpha_window_max: float | None`
  - Maximum observed α across nested windows.
- `alpha_window_span: float | None`
  - `alpha_window_max - alpha_window_min`. Float; non-negative.
- `propagated_window_error: float | None`
  - `sqrt(σ_min² + σ_max²)` where σ_min is the standard error of
    the window producing `alpha_window_min` and σ_max is the
    standard error of the window producing `alpha_window_max`.
  - This is the propagated standard error for the span statistic
    per transfer paper Section 5.
- `alpha_stability_status: AlphaWindowStabilityStatus`
  - Enum with values: `stable`, `unstable`, `not_tested`.
  - `stable` when nested-window analysis ran and the drift rule
    did not fire.
  - `unstable` when nested-window analysis ran and the drift rule
    fired.
  - `not_tested` when nested-window analysis was not performed.

When any nested-window field is `None`, all nested-window fields are
`None` (except `alpha_stability_status` which is `not_tested`).
When the analysis ran, all are populated. Codex must enforce this
invariant in a validation `__post_init__` or equivalent guard.

### 2. New auxiliary dataclass: AlphaWindowFit

Create a new frozen, slotted dataclass:

```python
@dataclass(frozen=True, slots=True)
class AlphaWindowFit:
    h_start: float
    h_end: float
    h_count: int
    observed_slope: float
    observed_alpha: float
    slope_standard_error: float
    alpha_standard_error: float  # equals slope_standard_error since alpha = slope + 1
    r_squared: float
```

Field semantics:
- `h_start`, `h_end`: smallest and largest h in this window.
- `h_count`: number of h-points used in the fit.
- `observed_slope`: OLS slope of `log|transfer|` vs `log(h)`.
- `observed_alpha`: `observed_slope + 1`.
- `slope_standard_error`: standard error of the OLS slope estimate.
- `alpha_standard_error`: equal to `slope_standard_error` (alpha is
  slope plus a constant). Stored for diagnostic readability.
- `r_squared`: OLS R² for this window's fit.

This dataclass lives in the same module as `AlphaProbeObservation`.
Export it from the primitives package alongside `AlphaProbeObservation`.

### 3. New auxiliary enum: AlphaWindowStabilityStatus

```python
class AlphaWindowStabilityStatus(StrEnum):
    stable = "stable"
    unstable = "unstable"
    not_tested = "not_tested"
```

Lives in the same module. Exported alongside `AlphaProbeStatus`.

### 4. AlphaProbeStatus — new strata

Add two members to `AlphaProbeStatus`:

- `alpha_zero_boundary = "alpha_zero_boundary"`
  - Fires when the observed α is within the precision-aware
    boundary envelope of zero. See classification logic below.
- `alpha_unstable_window = "alpha_unstable_window"`
  - Fires when nested-window slope span is both material and
    significant. See classification logic below.

Preserve existing member ordering and any existing string values.
The new members are appended.

### 5. Classification logic changes

Modify the existing AlphaProbe entry point (the function or method
that produces `AlphaProbeObservation` from a slope fit). The
classification precedence becomes:

1. **Pre-existing refusals first.** All current early-exit refusals
   stay in place and run before the new checks:
   - Insufficient data
   - Cancellation-dominated
   - Non-finite slope or NaN inputs
   - Domain refusal (if applicable at this layer)
2. **Nested-window analysis runs after the primary slope fit.**
   Compute the nested-window fits using the strategy specified in
   Section 6 below. Populate `nested_window_fits`,
   `alpha_window_min`, `alpha_window_max`, `alpha_window_span`,
   `propagated_window_error`.
3. **Zero-boundary check.**
   - Compute `alpha_boundary_envelope = max(K_BOUNDARY * observation.standard_error, ALPHA_NUMERIC_FLOOR)`.
   - If `abs(observation.observed_alpha) <= alpha_boundary_envelope`,
     status becomes `alpha_zero_boundary`. `alpha_stability_status`
     is set per the nested-window analysis (typically `stable` for
     a clean boundary, but record what the analysis actually
     produced — do not override).
   - Boundary check has precedence over the unstable-window check.
     Rationale: a slope numerically indistinguishable from -1 is at
     a boundary regardless of nested-window behavior, and reporting
     boundary is more informative for downstream consumers than
     reporting instability around a boundary point.
4. **Unstable-window check.**
   - Only runs if the zero-boundary check did not fire and nested-
     window analysis produced valid fits.
   - Drift rule: status becomes `alpha_unstable_window` if BOTH:
     - `alpha_window_span > materiality_threshold`, where
       `materiality_threshold` is `declared_alpha_band` if the
       caller provided one, else `DEFAULT_ALPHA_MATERIALITY`.
     - `alpha_window_span > K_DRIFT * propagated_window_error`.
   - Both conditions required. Either alone leaves the existing
     classification in place.
5. **Existing sign/algebraic strata.** If neither of the new
   checks fired, fall through to the existing classification logic
   (`alpha_regular_integer`, `alpha_fractional_branch`,
   `alpha_negative_singularity`, model-refused variants).
6. **Declared model matching, if applicable.** Existing behavior;
   runs after the algebraic stratum is selected.

`alpha_stability_status` is populated for all observations that
reached the slope-fit stage. For observations that exited at an
earlier refusal, `alpha_stability_status` is `not_tested`.

### 6. Nested-window construction strategy

The nested-window strategy is **sequential-from-top**: starting
from the full h-grid, progressively drop the largest h-value. Each
resulting sub-grid produces one `AlphaWindowFit`.

Constraints:
- Minimum h-points per window: `MIN_WINDOW_POINTS = 3` (need at
  least 3 points for a meaningful OLS slope plus standard error).
- Minimum number of windows: `MIN_WINDOW_COUNT = 3`.
- If the input h-grid has fewer than
  `MIN_WINDOW_POINTS + MIN_WINDOW_COUNT - 1` points
  (i.e., fewer than 5 with the defaults), nested-window analysis is
  skipped. `nested_window_fits = None`, all related fields are
  `None`, `alpha_stability_status = not_tested`. A conditioning
  note records `"nested_window_skipped: h_grid_too_short"`.
- The maximum number of windows is bounded only by the h-grid
  length; with 7 points and `MIN_WINDOW_POINTS=3`, you get 5
  windows (full, drop-1, drop-2, drop-3, drop-4, with 7, 6, 5, 4, 3
  points).

The full h-grid fit (window with all points) is included as one of
the nested-window fits, not as a separate top-level fit. The
"primary" `observed_slope` and `observed_alpha` on the
`AlphaProbeObservation` are equal to the full-grid window's values
(i.e., the first entry of `nested_window_fits` when sorted by
h_count descending).

### 7. Configuration constants

Add to a new module-private section (alongside existing AlphaProbe
constants) with explicit names and docstrings:

```python
# Standard-error multiplier for the zero-boundary envelope.
# 2.0 corresponds to roughly the 95% confidence interval for the
# slope-fit standard error, treating the slope estimate as normally
# distributed around the true slope.
K_BOUNDARY: Final[float] = 2.0

# Standard-error multiplier for the unstable-window significance
# check. Conservative enough to avoid false positives on tight
# algebraic fits; loose enough to catch nested-window drift that
# exceeds typical statistical noise. Derivation: transfer paper
# Section 5 uses z_{1-γ/2} for the slope-difference test; at γ=0.05
# this gives ~1.96. K_DRIFT = 2.0 rounds this conservatively.
K_DRIFT: Final[float] = 2.0

# Precision-tied absolute floor for the zero-boundary envelope.
# Below this magnitude, alpha values are within machine precision
# of zero regardless of slope-fit standard error. Tied to the
# typed_finite_difference precision floor (2u with u = 2^-53)
# scaled by a small headroom factor.
ALPHA_NUMERIC_FLOOR: Final[float] = 1e-9

# Default materiality threshold for the unstable-window check when
# the caller does not provide a declared_alpha_band. Calibrated to
# be larger than typical algebraic drift (Fixture C span ~0.03) and
# smaller than iterated-logarithmic drift (Fixture E span ~0.18).
# Roughly the resolution at which "fractional branch" is
# meaningfully distinct from a clean integer alpha.
DEFAULT_ALPHA_MATERIALITY: Final[float] = 0.05

# Minimum number of h-points required for a single nested-window fit.
MIN_WINDOW_POINTS: Final[int] = 3

# Minimum number of nested windows required for stability analysis.
MIN_WINDOW_COUNT: Final[int] = 3
```

These constants live in the AlphaProbe module. They are
intentionally exposed (not underscore-prefixed) so tests can
import and reference them. They are NOT user-configurable per call;
the per-call knob is `declared_alpha_band`.

### 8. Optional declared_alpha_band parameter

If `directional_alpha_probe` (or the equivalent entry point) does
not already accept `declared_alpha_band`, add it as an optional
keyword parameter:

```python
declared_alpha_band: float | None = None
```

If provided and positive, it overrides `DEFAULT_ALPHA_MATERIALITY`
in the unstable-window check. If `None`, the default is used.
If provided and non-positive (≤ 0), raise `ValueError` — a
non-positive band is meaningless.

If a `declared_alpha_model` parameter already exists and implies a
band (e.g., regular-integer-with-tolerance), that band may be used.
In any conflict between an explicitly-passed `declared_alpha_band`
and a model-derived band, the explicit value wins.

### 9. ScalarAlphaJetBundleStatus — new strata

Add to `ScalarAlphaJetBundleStatus`:

- `scalar_jet_alpha_zero_boundary = "scalar_jet_alpha_zero_boundary"`
- `scalar_jet_alpha_unstable_window = "scalar_jet_alpha_unstable_window"`

### 10. SingularAlphaJetBundleStatus — new strata

Add to `SingularAlphaJetBundleStatus`:

- `singular_jet_alpha_zero_boundary = "singular_jet_alpha_zero_boundary"`
- `singular_jet_alpha_unstable_window = "singular_jet_alpha_unstable_window"`

### 11. Bundle status mapping updates

In both bundles, the status mapping function (e.g.,
`_map_alpha_status_to_bundle_status` or whatever the existing
helper is called) must add explicit cases for the two new
`AlphaProbeStatus` members:

- `AlphaProbeStatus.alpha_zero_boundary` →
  `ScalarAlphaJetBundleStatus.scalar_jet_alpha_zero_boundary`
  (and singular analog)
- `AlphaProbeStatus.alpha_unstable_window` →
  `ScalarAlphaJetBundleStatus.scalar_jet_alpha_unstable_window`
  (and singular analog)

No bundle-level policy is introduced. The mapping is a pure 1:1
translation. The bundle's typed result continues to expose the full
`AlphaProbeObservation` via the existing field (so the nested
window evidence reaches downstream consumers).

## Documentation Changes

### 1. STATUS_CALCULUS.md

Add a new section documenting:
- The two new AlphaProbe strata, their semantics, and the conditions
  under which they fire.
- The precedence order (refusals → zero-boundary → unstable-window
  → sign/algebraic → declared model).
- The bundle status mapping for both sibling primitives.
- A brief statement that bundles map AlphaProbe statuses 1:1 with
  no policy.

### 2. METROLOGY_PRINCIPLES.md

Add a new section documenting:
- The zero-boundary envelope formula:
  `max(K_BOUNDARY * standard_error, ALPHA_NUMERIC_FLOOR)`.
- The unstable-window drift rule:
  `span > materiality AND span > K_DRIFT * propagated_window_error`.
- The propagated window error formula:
  `sqrt(σ_min² + σ_max²)` per transfer paper Section 5.
- The nested-window strategy: sequential-from-top, minimum 3
  windows of minimum 3 points each.
- The role of `declared_alpha_band` and the fallback to
  `DEFAULT_ALPHA_MATERIALITY` when no band is provided.

### 3. Manifests

Update the relevant primitive manifests:
- AlphaProbe: list new strata, new observation fields, new
  auxiliary dataclass `AlphaWindowFit`, new enum
  `AlphaWindowStabilityStatus`.
- ScalarAlphaJetBundle: list new strata.
- SingularAlphaJetBundle: list new strata.

Manifests preserve the existing format and ordering conventions.

### 4. DISCOVERY_PHILOSOPHY.md

No changes required. The philosophy "no failures, only observations
of varying refinement" already accommodates this task's
contribution: nested-window evidence refines what observations can
say.

## Required Tests

Tests live in `tests/test_task023b_alphaprobe_reliability.py` plus
extensions to existing fixture coverage. Total expected new tests:
approximately 35-50.

### AlphaProbe-level unit tests

- `AlphaWindowFit` dataclass: constructable with required fields,
  frozen, slots-correct, equality semantics.
- `AlphaWindowStabilityStatus` enum: three members with correct
  string values.
- New `AlphaProbeStatus` members: present, correct string values.
- `AlphaProbeObservation` invariants:
  - When nested-window analysis ran: all nested fields populated.
  - When nested-window analysis skipped:
    `nested_window_fits is None`, all span/error fields are `None`,
    `alpha_stability_status == not_tested`.
  - Validation guard rejects partial population.
- Nested-window construction:
  - With 7 h-points, produces 5 windows of sizes 7, 6, 5, 4, 3.
  - With 4 h-points and MIN_WINDOW_POINTS=3, produces 2 windows of
    sizes 4 and 3 — which is below MIN_WINDOW_COUNT=3, so
    analysis is skipped.
  - With exactly 5 h-points, produces 3 windows of sizes 5, 4, 3.
  - Window slopes correctly fit on `log|transfer|` vs `log(h)`
    for each sub-grid.
- Propagated window error:
  - Equal to `sqrt(σ_min² + σ_max²)` for the windows producing
    `alpha_window_min` and `alpha_window_max`.
  - Numerical check on a hand-computed example.
- Zero-boundary envelope:
  - With `standard_error = 0.01`, envelope = `max(0.02, 1e-9)` = 0.02.
  - With `standard_error = 1e-15`, envelope = `1e-9`.
  - `K_BOUNDARY = 2.0` confirmed.
- Zero-boundary classification:
  - Synthetic case: `observed_alpha = 1e-12`, `standard_error = 1e-8`
    → envelope = `2e-8`, `|1e-12| < 2e-8` → status =
    `alpha_zero_boundary`.
  - Synthetic case: `observed_alpha = 0.01`, `standard_error = 1e-3`
    → envelope = `2e-3`, `|0.01| > 2e-3` → status remains
    sign-based (`alpha_fractional_branch` or similar).
- Unstable-window classification:
  - Synthetic case: span = 0.2, propagated_error = 0.01,
    no declared band → span > 0.05 AND span > 0.02 → status =
    `alpha_unstable_window`.
  - Synthetic case: span = 0.04, propagated_error = 0.01,
    no declared band → span < 0.05 → existing classification holds.
  - Synthetic case: span = 0.1, propagated_error = 0.06,
    no declared band → span > 0.05 BUT span < 0.12 → existing
    classification holds (significance fails).
  - Synthetic case: span = 0.04, propagated_error = 0.01,
    `declared_alpha_band = 0.02` → span > 0.02 AND span > 0.02
    → status = `alpha_unstable_window`.
- Precedence:
  - When both zero-boundary and unstable-window conditions hold,
    `alpha_zero_boundary` wins.
  - When refusals trigger, neither new check runs.
- `declared_alpha_band` validation:
  - `None` accepted, uses default.
  - Positive float accepted, used.
  - Zero or negative raises `ValueError`.

### Fixture-level regression tests

Re-run the six discovery fixtures (A through F) and one additional
fixture missing from the original campaign, plus two guard fixtures.

For each fixture, assert the expected status under 023b. These are
permanent tests, not discovery script outputs.

Test file structure: one test class per fixture, with sub-tests for
scalar bundle, singular bundle, embedded AlphaProbe observation,
and nested-window evidence presence.

| Fixture | Function | Expected Scalar | Expected Singular | Nested Evidence |
|---------|----------|-----------------|-------------------|-----------------|
| A | `x**0.5` | `scalar_jet_fractional_alpha_branch` | `singular_jet_fractional_alpha_branch` | stable |
| B | `1/x` | `scalar_jet_domain_refused` | `singular_jet_negative_alpha_singularity` | stable (singular) |
| C | `x**0.5 * (1 + 0.1*x**0.1)` | `scalar_jet_fractional_alpha_branch` | `singular_jet_fractional_alpha_branch` | stable (drift below default materiality) |
| D | `-log(x)` | `scalar_jet_domain_refused` | `singular_jet_alpha_zero_boundary` | (varies; see note) |
| E | `log(-log(x))` | `scalar_jet_domain_refused` | `singular_jet_alpha_unstable_window` | unstable |
| F | `exp(-1/x**2)` | `scalar_jet_alpha_indeterminate` | `singular_jet_alpha_indeterminate` | not_tested (refused before slope fit) |
| G1 (guard) | `x**0.01` | `scalar_jet_fractional_alpha_branch` | `singular_jet_fractional_alpha_branch` | stable |
| G2 (guard) | `x**(-0.05)` | `scalar_jet_domain_refused` | `singular_jet_negative_alpha_singularity` | stable |

**Note on Fixture C stability.** The test asserts C remains
`alpha_fractional_branch` with `alpha_stability_status == stable`
under the default materiality threshold (`DEFAULT_ALPHA_MATERIALITY
= 0.05`). If empirical drift exceeds this, the test will fail and
the calibration of `DEFAULT_ALPHA_MATERIALITY` needs adjustment.
This is a deliberate calibration check.

**Note on Fixture D stability.** The boundary check fires regardless
of nested-window stability. The test asserts
`alpha_stability_status` is whatever the analysis actually
produced — likely `stable` since the slope is approximately -1
across all sub-windows. Codex records the observed value and the
test asserts the recorded value, with a conditioning note
explaining the expectation.

**Note on Fixture E.** This is the headline win for the task. The
test asserts:
- `singular_jet_alpha_unstable_window`
- Embedded `AlphaProbeStatus.alpha_unstable_window`
- `alpha_window_span > DEFAULT_ALPHA_MATERIALITY`
- `alpha_window_span > K_DRIFT * propagated_window_error`
- Nested-window fits show a monotonic-or-near-monotonic slope
  drift across windows.

### Guard-fixture rationale tests

The guards (G1: `x**0.01`, G2: `x**(-0.05)`) prevent the new strata
from over-firing on legitimately small algebraic exponents:

- G1: leading α = 0.01. observed_alpha is small but stable
  across nested windows. The zero-boundary check must NOT fire if
  `|0.01|` exceeds the envelope. With `standard_error` on the
  order of 1e-4 (typical for tight fits), envelope ≈ 2e-4, so
  `|0.01| > 2e-4` and the check correctly skips. Status remains
  `fractional_branch`.
- G2: leading α = -0.05. observed_alpha is small-negative but
  stable. Similar logic — envelope is much smaller than 0.05, so
  zero-boundary correctly skips. Status remains
  `negative_singularity` (singular bundle only; scalar refuses at
  the singular point).

If either guard fails, the boundary check is too aggressive and
`K_BOUNDARY` or `ALPHA_NUMERIC_FLOOR` needs adjustment.

### Bundle wrapper-translation tests

For each new AlphaProbe stratum:
- The scalar bundle, when receiving an `AlphaProbeObservation` with
  status `alpha_zero_boundary`, maps to
  `scalar_jet_alpha_zero_boundary`. Synthesizable in a unit test
  by mocking the AlphaProbe call or constructing the observation
  directly.
- Same for `alpha_unstable_window`.
- Singular bundle analogs.
- The bundle's typed result exposes the full
  `AlphaProbeObservation` including new nested-window fields.

### Audit hygiene

If any new module-level constants in source files require purity-
audit allowance for occurring outside comments (e.g., the docstrings
referencing `epsilon` or `eps`), reuse the existing helper
`is_allowed_precision_floor_comment_token` from Task 022. Do not
introduce a new audit helper unless a new category of allowance is
needed. If a new allowance category is genuinely required (e.g.,
references to `standard_error` outside comments), follow the Task
022 pattern: create a narrowly-scoped helper, write its purity
test, and add a follow-up tightening ticket to the next task.

### `to_json_safe` coverage

The expanded `AlphaProbeObservation` and new `AlphaWindowFit`
dataclass must serialize cleanly through `to_json_safe` (or
whatever the existing typed serialization helper is named). Add
tests confirming:
- Round-trip serialization preserves all new fields.
- `None` values for skipped-analysis cases serialize correctly.
- `AlphaWindowStabilityStatus` serializes to its string value.

## Required Commands

```bash
# Pre-task baseline
python -m pytest -x tests/ -q

# After implementation
python -m pytest -x tests/test_task023b_alphaprobe_reliability.py -v

# Full suite
python -m pytest -x tests/ -q

# Diff verification
git diff --stat src/
git diff --stat tests/
git diff --stat Build_Docs/
```

Expected: full suite passes at approximately 414-429 tests
(379 baseline + 35-50 new tests). `src/` shows AlphaProbe-related
changes plus both bundle status enum and mapping updates. `tests/`
shows the new test file. `Build_Docs/` shows STATUS_CALCULUS.md,
METROLOGY_PRINCIPLES.md, manifests, and the task summary.

## Non-Goals

- **Do NOT implement Task 024 (joint composer).** This task ends
  when AlphaProbe reliably exports honest classifications.
- **Do NOT introduce symbolic detection** of logarithmic, iterated-
  logarithmic, or essential-singularity behavior. V4's contribution
  is "this finite-window α is not stable," not "this is a logarithm."
- **Do NOT port V3's slope-flow model-comparison machinery** (BIC
  margins, algebraic-vs-logarithmic model selection, etc.). V3 is
  reference-only. The derivation here uses nested-window slope
  span and propagated standard error — not multi-model BIC
  comparison.
- **Do NOT change the clean A/B/F behaviors** except by adding
  evidence fields. A remains `fractional_branch`. B remains
  `negative_singularity` (singular). F remains
  `alpha_insufficient_data`.
- **Do NOT add bundle-level policy.** Both bundles map AlphaProbe
  statuses 1:1 to their family-prefixed counterparts. No
  bundle-side reclassification, no bundle-side override of
  AlphaProbe's decision.
- **Do NOT introduce `alpha_non_algebraic_drift`** or any stratum
  that names a specific kind of non-algebraic behavior. The
  V4-honest claim is "unstable window," not "logarithmic drift."
- **Do NOT modify any Layer 2+ module** (metrology, branch,
  refinery, history, solver). They remain V3-shaped, deferred,
  reference-only.
- **Do NOT modify the existing scalar/singular probe constructors**
  beyond what's needed for the new strata mapping. The probe
  functions (`g_local`, `g_singular`) and the typed finite-
  difference path remain unchanged.

## Completion Report

Create `Build_Docs/Reports/task023b_summary.md` with:

- **Scope summary** (one paragraph): what the task added.
- **Test counts.** Expected: pre 379, post approximately 414-429.
- **Files modified.** Expected:
  - `src/lloyd_v4/primitives/<alpha_probe module>.py` (AlphaProbe
    extension)
  - `src/lloyd_v4/primitives/scalar_alpha_jet_bundle.py` (status
    enum + mapping)
  - `src/lloyd_v4/primitives/singular_alpha_jet_bundle.py` (status
    enum + mapping)
  - `Build_Docs/Architecture/STATUS_CALCULUS.md`
  - `Build_Docs/Architecture/METROLOGY_PRINCIPLES.md`
  - `Build_Docs/Manifests/<relevant manifests>`
  - `tests/test_task023b_alphaprobe_reliability.py` (new)
  - `Build_Docs/Reports/task023b_summary.md` (this file)
- **Empirical calibration record.** For Fixtures D and E, record
  the actual values of:
  - `observed_alpha`, `standard_error`, `alpha_boundary_envelope`
    (for D)
  - `alpha_window_span`, `propagated_window_error`,
    `materiality_threshold` (for E)
  - This is the evidence that the calibration constants
    (K_BOUNDARY, K_DRIFT, DEFAULT_ALPHA_MATERIALITY,
    ALPHA_NUMERIC_FLOOR) are correctly tuned for the surfaced
    cases.
- **Guard-fixture confirmation.** For Fixtures G1 (`x**0.01`) and
  G2 (`x**(-0.05)`):
  - Observed α, standard_error, boundary envelope.
  - Confirmation that the new strata did NOT fire.
- **Audit allowance status.** If a new audit helper was introduced,
  flag it for a follow-up tightening ticket (Task 023b's analog of
  Task 022).
- **Forward pointer.** Confirmation that Task 024 (joint composer)
  can now be specified against the updated substrate.
- **Diff confirmation.** Output of `git diff --stat src/`,
  `git diff --stat tests/`, `git diff --stat Build_Docs/`.

## Acceptance Criteria

- AlphaProbe emits `alpha_zero_boundary` for Fixture D.
- AlphaProbe emits `alpha_unstable_window` for Fixture E.
- AlphaProbe preserves existing strata for Fixtures A, B, C, F.
- Both bundles map AlphaProbe's new strata 1:1.
- Guard fixtures G1 (`x**0.01`) and G2 (`x**(-0.05)`) preserve
  their pre-existing algebraic classifications.
- `AlphaProbeObservation` exposes:
  - `nested_window_fits` (tuple of `AlphaWindowFit` or `None`)
  - `alpha_window_min`, `alpha_window_max`, `alpha_window_span`,
    `propagated_window_error`, `alpha_stability_status`
- Validation enforces all-or-none population of nested-window fields.
- Sequential-from-top windowing with `MIN_WINDOW_POINTS=3` and
  `MIN_WINDOW_COUNT=3`. h-grids shorter than the minimum skip
  analysis with `alpha_stability_status == not_tested` and a
  conditioning note.
- The zero-boundary envelope is `max(K_BOUNDARY * standard_error,
  ALPHA_NUMERIC_FLOOR)`. The unstable-window drift rule is
  `span > materiality AND span > K_DRIFT * propagated_window_error`.
- The precedence order is: refusals → zero-boundary →
  unstable-window → sign/algebraic → declared model.
- `declared_alpha_band` is an optional positive float;
  non-positive values raise `ValueError`.
- STATUS_CALCULUS.md and METROLOGY_PRINCIPLES.md document the new
  strata, rules, and constants.
- All manifests updated to list new strata, fields, and auxiliary
  types.
- Bundles map statuses 1:1 with no policy.
- Full test suite passes.
- `to_json_safe` serializes the expanded observation cleanly.
- No Layer 2+ module is modified.

## Discipline Notes

- **The contract sentence is the anchor.** "AlphaProbe must not
  export algebraic-looking alpha classifications unless the finite-
  window evidence is both numerically non-boundary and
  nested-window stable enough for downstream composition." If a
  proposed implementation detail conflicts with this contract,
  the contract wins.

- **Calibration is empirical and recorded.** The calibration
  constants (K_BOUNDARY, K_DRIFT, DEFAULT_ALPHA_MATERIALITY,
  ALPHA_NUMERIC_FLOOR) are tuned against Fixtures D, E, C, G1, G2.
  The completion report records the actual observed values that
  justify each constant's setting. If a calibration constant
  needs adjustment to make the fixtures pass, that adjustment is
  in scope — but it must be recorded in the report with reasoning,
  not silently changed.

- **The guard fixtures are not optional.** G1 and G2 lock the
  anti-overcorrection invariant. Without them, the new strata
  could quietly start eating legitimate small-exponent algebraic
  cases on future code changes.

- **The unstable-window check does not interpret drift.** It
  reports that the slope migrated beyond noise and materiality. It
  does not say what kind of function produced the migration. Any
  language in the implementation, comments, or documentation
  suggesting otherwise (e.g., "logarithmic detection," "iterated-log
  classifier") should be removed or refused. The honest statement
  is "finite-window α not stable enough for algebraic consumption."

- **The boundary check is for α near zero, not slope near zero.**
  In the existing convention, `observed_alpha = observed_slope + 1`.
  "α near zero" corresponds to "slope near -1." The check is
  written in α-space for readability:
  `abs(observed_alpha) <= envelope`. Implementation in slope-space
  (`abs(observed_slope + 1) <= envelope`) is mathematically
  identical and acceptable if the existing code organization
  prefers it.

- **The propagated window error formula has theorem backing.**
  `sqrt(σ_min² + σ_max²)` is the standard error of the slope
  difference between two independent OLS fits (transfer paper
  Section 5). The independence assumption is approximately
  satisfied for nested windows of different sizes; the
  approximation is conservative (correlated errors would reduce
  the variance). Codex should not invent a different propagation
  rule.

- **Bundle wrapping is sovereign.** The bundle status mapping is a
  pure function from `AlphaProbeStatus` to bundle status enum.
  No conditional logic based on bundle context, no overrides, no
  policy. If a future task wants bundle-level policy, that's a
  separate architectural decision that this task does not
  pre-authorize.

- **Forward reference (Task 024).** Once 023b lands and the
  fixtures pass with honest classifications, Task 024 (joint
  composer) can be specified. The composer will consume both
  `AlphaProbeStatus` and the nested-window stability evidence to
  produce joint geometric observations. The composer is not
  pre-specified in this task; its shape depends on what the
  post-023b substrate looks like in practice.
