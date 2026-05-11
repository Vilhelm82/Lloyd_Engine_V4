# Task 023 Iterated Logarithm Discovery Report

## Section 1: Campaign overview

Task 023 ran an observation-only discovery campaign against the existing
Layer 1 sibling primitives `scalar_alpha_jet_bundle` and
`singular_alpha_jet_bundle`. No source files, tests, status families,
protocols, or transition rules were modified.

The campaign used six fixtures:

| fixture | function | purpose |
|---|---|---|
| A | `x**0.5` | clean positive algebraic fractional branch |
| B | `1 / x` | clean negative algebraic singularity |
| C | `x**0.5 * (1 + 0.1 * x**0.1)` | algebraic leading exponent with finite-window drift |
| D | `-log(x)` | zero-alpha logarithmic divergence |
| E | `log(-log(x))` | canonical iterated-log non-algebraic drift |
| F | `exp(-1 / (x*x))`, with `f(0) = 0` | essential flat-function stress test |

For each fixture, the script ran both bundles with the h-grid specified
in the task and recorded the full typed results in
`observations_data.md`. The script is reproducible and emits no test
assertions. The analysis below treats the transfer-paper expectation as
the reference and classifies each result as an honest classification,
honest refusal, or misleading classification.

## Section 2: Fixture-by-fixture observations

### Fixture A: pure algebraic positive

**Theoretical prediction.** `f(x) = sqrt(x)` has alpha `0.5`.
Both bundles should report a clean fractional branch.

**Scalar bundle observation.** Status
`scalar_jet_fractional_alpha_branch`; embedded AlphaProbe status
`alpha_fractional_branch`; observed alpha
`0.49999999997887246`; conditioning notes include
`observed_alpha=0.5`.

**Singular bundle observation.** Status
`singular_jet_fractional_alpha_branch`; embedded AlphaProbe status
`alpha_fractional_branch`; observed alpha
`0.49999999997887246`; conditioning notes include
`observed_alpha=0.5`.

**Sibling comparison.** The siblings agree on embedded
`alpha_fractional_branch` and have distinct AlphaProbe trace IDs.

**Honesty assessment.** Honest classification. V4 identifies the clean
algebraic fractional branch exactly as expected.

### Fixture B: pure algebraic negative

**Theoretical prediction.** `f(x) = 1 / x` has alpha `-1` on the
right-hand singular probe. The scalar bundle should refuse because
`f(0)` raises.

**Scalar bundle observation.** Status `scalar_jet_domain_refused`;
no embedded AlphaProbe result; conditioning notes record
`reason=f(x0) raised ZeroDivisionError`.

**Singular bundle observation.** Status
`singular_jet_negative_alpha_singularity`; embedded AlphaProbe status
`alpha_negative_singularity`; observed alpha
`-0.9999999999985296`; conditioning notes include
`observed_alpha=-1`.

**Sibling comparison.** Informative disagreement: scalar refuses the
undefined point value, while singular observes the singular-direct
geometry.

**Honesty assessment.** Honest classification. The sibling disagreement
is structurally meaningful and matches the theory.

### Fixture C: slow algebraic drift

**Theoretical prediction.** The leading alpha is `0.5`, with finite
window drift from the subleading `x**0.1` factor. The task expected the
campaign to reveal whether V4 exposes that drift.

**Scalar bundle observation.** Status
`scalar_jet_fractional_alpha_branch`; embedded AlphaProbe status
`alpha_fractional_branch`; observed alpha
`0.5038604145993733`; conditioning notes include
`observed_alpha=0.50386`.

**Singular bundle observation.** Status
`singular_jet_fractional_alpha_branch`; embedded AlphaProbe status
`alpha_fractional_branch`; observed alpha
`0.5038604145993733`; conditioning notes include
`observed_alpha=0.50386`.

**Sibling comparison.** The siblings agree on the embedded alpha
status and have distinct AlphaProbe trace IDs.

**Honesty assessment.** Misleading classification. The leading exponent
is in the right neighborhood, but the result is a clean-looking
fractional-branch stratum with no nested-window or finite-window drift
evidence. V4 currently compresses "fractional branch with slow drift"
into the same surface status as Fixture A.

### Fixture D: logarithmic divergence

**Theoretical prediction.** `f(x) = -log(x)` has log-log transfer slope
`-1`, so observed alpha is `0`. The AlphaProbe doctrine excludes alpha
zero from the controlled algebraic branch theorem.

**Scalar bundle observation.** Status `scalar_jet_domain_refused`;
no embedded AlphaProbe result; conditioning notes record
`reason=f(x0) raised ValueError`.

**Singular bundle observation.** Status
`singular_jet_negative_alpha_singularity`; embedded AlphaProbe status
`alpha_negative_singularity`; observed alpha
`-5.969646998948974e-11`; observed slope
`-1.0000000000596965`.

**Sibling comparison.** Informative disagreement at the bundle level:
scalar refuses the undefined point value, while singular reaches a
near-zero alpha classification.

**Honesty assessment.** Misleading classification. The measured slope
is the expected logarithmic boundary case, but V4 has no zero-alpha or
logarithmic-divergence stratum. A tiny negative roundoff-side alpha is
accepted as a negative singularity.

### Fixture E: iterated logarithmic divergence

**Theoretical prediction.** `f(x) = log(-log(x))` has finite-window
slope `-1 + 1 / log(1/x)`, so observed alpha drifts slowly toward zero.
A finite log-log fit can look convincing while still representing
non-algebraic drift.

**Scalar bundle observation.** Status `scalar_jet_domain_refused`;
no embedded AlphaProbe result; conditioning notes record
`reason=f(x0) raised ValueError`.

**Singular bundle observation.** Status
`singular_jet_fractional_alpha_branch`; embedded AlphaProbe status
`alpha_fractional_branch`; observed alpha
`0.07735536576079116`; observed slope `-0.9226446342392088`.

**Sibling comparison.** Informative disagreement at the bundle level:
scalar refuses the undefined point value, while singular emits an
accepted positive fractional-branch classification.

**Honesty assessment.** Misleading classification. This is the central
substrate gap surfaced by the campaign. V4 reports a small positive
fractional alpha, but the theoretical expectation is non-algebraic
drift toward the zero-alpha boundary. Current AlphaProbe output lacks
the nested-window evidence or a non-algebraic-drift stratum needed to
express that distinction.

### Fixture F: essential singularity stress test

**Theoretical prediction.** `exp(-1 / x^2)` with `f(0) = 0` is flat at
the origin and has no power-law alpha. A good typed result should refuse
or mark the alpha evidence indeterminate/cancellation-dominated.

**Scalar bundle observation.** Status `scalar_jet_alpha_indeterminate`;
embedded AlphaProbe status `alpha_insufficient_data`; observed alpha
`None`.

**Singular bundle observation.** Status
`singular_jet_alpha_indeterminate`; embedded AlphaProbe status
`alpha_insufficient_data`; observed alpha `None`.

**Sibling comparison.** The siblings agree on embedded
`alpha_insufficient_data` and have distinct AlphaProbe trace IDs.

**Honesty assessment.** Honest refusal. V4 does not claim an alpha for
the flat essential case under this grid.

## Section 3: Cross-fixture patterns

Clean algebraic fixtures classify as expected. Fixture A gives matching
fractional branches, and Fixture B gives the intended scalar refusal
plus singular negative-singularity observation.

The slow algebraic drift case exposes missing reliability context. Both
bundles emit a clean fractional branch with alpha about `0.50386`, but
there is no typed record of the finite-window drift that distinguishes
Fixture C from Fixture A.

The alpha-near-zero logarithmic case is not expressed honestly by the
current strata. Fixture D is measured at the correct slope boundary, but
roundoff places observed alpha slightly negative and the accepted status
becomes `alpha_negative_singularity`.

The canonical iterated-log case shows the strongest gap. Fixture E
emits `alpha_fractional_branch` with observed alpha about `0.07736`.
That is a plausible finite-window slope, but it hides the theoretical
fact that the apparent exponent is drifting slowly toward zero and is
not an algebraic branch exponent.

The essential singularity stress test is handled conservatively:
Fixture F emits `alpha_insufficient_data` through both bundles and does
not produce a misleading alpha.

Overall, not all six fixtures produced honest typed results. Fixtures
C, D, and E are the problematic cluster, and all point to the same
AlphaProbe-level limitation: current output is a single-window alpha
classification without nested-window drift evidence or a dedicated
zero-alpha/non-algebraic-drift stratum.

## Section 4: Findings

1. **Substrate-honest finding:** Fixtures A and B confirm that V4
   handles clean algebraic positive and negative alpha cases correctly.
   Fixture A emits `alpha_fractional_branch` with alpha `0.5`; Fixture
   B emits scalar domain refusal and singular `alpha_negative_singularity`
   with alpha `-1`.

2. **Substrate-honest finding:** Fixture F confirms that V4 can refuse
   an alpha claim for a flat essential case under the tested grid. Both
   bundles emit `alpha_insufficient_data` and no observed alpha.

3. **AlphaProbe-extension finding:** Fixture C needs finite-window or
   nested-window drift evidence. The emitted alpha `0.5038604145993733`
   is reasonable as a single fitted exponent, but the typed result does
   not distinguish it from the clean Fixture A fractional branch.

4. **Strata-gap finding:** Fixture D needs a zero-alpha boundary or
   logarithmic-divergence classification. The observed alpha
   `-5.969646998948974e-11` is effectively zero, but V4 emits
   `alpha_negative_singularity`.

5. **Strata-gap finding:** Fixture E needs a non-algebraic-drift or
   unstable-window classification. V4 emits `alpha_fractional_branch`
   with observed alpha `0.07735536576079116`, which is a misleading
   accepted stratum for the iterated-log drift case.

6. **Discovery-instrument finding:** The sibling architecture is useful.
   In B, D, and E, scalar refusal plus singular observation clearly
   separates undefined-at-origin behavior from right-hand singular
   geometry.

## Section 5: Recommendation for Task 023b and Task 024

**Recommendation: Task 023b before Task 024.**

The gap is AlphaProbe-level. Current V4 alpha evidence is a single
log-log fit mapped into the existing alpha strata. That is sufficient
for clean algebraic cases, but it cannot honestly express:

- finite-window algebraic drift in Fixture C,
- alpha-zero logarithmic boundary behavior in Fixture D,
- non-algebraic drift toward zero in Fixture E.

Task 023b should extend AlphaProbe evidence before any joint composer is
specified. The minimal useful extension is nested-window stability
evidence promoted into the typed result. Depending on the design, the
extension may also need one or more explicit strata such as
`alpha_zero_boundary`, `alpha_non_algebraic_drift`, or
`alpha_unstable_window`.

Task 024 should wait until this is represented in the substrate. A
composer built on the current statuses would inherit the misleading
Fixture E classification and would have no typed way to distinguish a
clean fractional branch from iterated-log drift.
