# Task 023 — Iterated Logarithm Discovery Campaign

## Repository

`/mnt/fast/Lloyd_Engine_V4`

V3 is reference-only (Axiom 10). V1 / OG engine are also reference-only.
Layer 2+ artifacts (metrology, branch, refinery, history, solver) are
V3-shaped deferred-consumer first-drafts and MUST NOT shape this task.

**This is a discovery campaign, not an implementation task.** The
deliverable is observation evidence and analysis, not new substrate.
No file in `src/` is modified. No new primitives, status families,
protocols, or transition rules are introduced. No existing tests are
modified.

## Current Verified Baseline

- 379 tests passing (`pytest -x tests/`) as of Task 022 completion.
- Both L1 sibling primitives operational:
  `scalar_alpha_jet_bundle` (Task 019, local-additive probe) and
  `singular_alpha_jet_bundle` (Task 021, singular-direct probe).
- Audit allowance tightened to comment-line-only (Task 022).
- Repository is now under git control (verified by Will between Task
  022 and 023; the previous non-git state recorded in the Task 022
  summary no longer applies).
- The `transfer_function_exponent_family_v2.pdf` Section 5
  ("Non-algebraic singularities and slope-flow comparison") is the
  theorem reference for the iterated logarithm case. V3 used
  slope-flow model comparison (algebraic vs logarithmic vs essential
  drift models, BIC margins) to discriminate.

## Task Goal

Run V4's L1 sibling primitives against a small, carefully chosen set of
fixtures that span the regime from clean algebraic behavior through
slow non-algebraic drift. Record what the typed strata actually emit
on each fixture. Compare to the theoretical expectation per the
transfer function paper. Produce a discovery report that:

1. Documents observed strata, observed α, and conditioning notes
   for each fixture across both bundles where applicable.
2. Identifies fixtures where V4's current substrate classifies
   honestly — typed result accurately characterizes the underlying
   geometry.
3. Identifies fixtures where V4's current substrate classifies
   imprecisely or fails to express what's happening — substrate gaps
   that may need future work.
4. Records sibling agreement / disagreement patterns: where both
   bundles observe the same geometry, do they emit consistent
   strata? Where they disagree, is the disagreement informative?
5. Recommends whether a follow-up substrate-extension task
   (provisionally "Task 023b") is needed before specifying the joint
   composer (Task 024). If so, articulates what the extension would
   address.

The campaign is observation-only. **Codex must not implement any
substrate fix even if a gap is observed.** Findings are findings;
implementation is a separate task.

## Source Labelling

- **(V4-surface evidence)** Both sibling primitives landed cleanly
  (Task 019 and Task 021 summaries). The full negative-α validation
  in Task 021 demonstrated that `SingularAlphaJetBundle` reaches
  strata `ScalarAlphaJetBundle` structurally cannot. The substrate
  for the regularity channel is in place; this task tests how well
  it characterizes cases beyond clean algebraic α.

- **(Theorem-derived)** From the transfer function paper:
  - **Section 3 (Robust branch transfer law):** for `g(f) = c·f^α·L(f)`
    near `f → 0+` with α ≠ 0 and L slowly varying, the limiting
    log-log transfer slope is α-1. The α-1 recovery is well-validated
    in V4 (Tasks 016, 018, 019).
  - **Section 4 (Finite-step and finite-window corrections):**
    subleading powers produce slope drift on finite sweeps.
    Specifically, for `g(f) = g_0 + c·f^α·(1 + a·f^ρ + O(f^(ρ+ε)))`,
    `D log |g'(f)| = α - 1 + (aρ(α+ρ)/α)·f^ρ + O(f^(2ρ))`.
  - **Section 5 (Non-algebraic singularities):** for `g(f) = log log(1/f)`,
    `|g'(f)| = 1/(f log(1/f))`, so
    `D log |g'(f)| = -1 + 1/log(1/f) = -1 + 1/t`,
    where `t = log(1/f)`. Asymptotic slope is -1 (observed α = 0),
    but at any finite t, slope is `-1 + 1/t` (observed α = 1/t,
    small positive). A fixed-threshold classifier mistakes this for
    a small algebraic exponent over a finite window. V3 used
    slope-flow model comparison to discriminate.

- **(Architectural)** The campaign tests whether V4's current
  AlphaProbe strata
  (`alpha_regular_integer`, `alpha_fractional_branch`,
  `alpha_negative_singularity`, model-refused variants,
  `alpha_cancellation_dominated`, `alpha_insufficient_data`,
  `alpha_indeterminate`, `alpha_domain_refused`, `alpha_nonfinite`)
  cover slow non-algebraic drift honestly. The Task 018 spec
  explicitly deferred nested-window stability evidence and any
  `alpha_non_algebraic_drift` or `alpha_unstable_window` stratum.
  This campaign generates the evidence about whether those deferred
  features are actually needed.

## Design Principles

- **Observation-only.** No code in `src/` is modified. No new
  primitives. No new statuses. No new transition rules. No
  modifications to existing tests.

- **The script is reproducibility, not test coverage.** The discovery
  script runs the bundles against the fixtures and records typed
  results. It is not a pytest file. It does not assert pass/fail
  on observations. Its job is to produce a deterministic data
  artifact (`observations_data.md`) that anyone can regenerate by
  re-running the script.

- **Theoretical expectation is the reference, not the verdict.** For
  each fixture, the spec records what the transfer function paper
  predicts. The discovery report records what V4 actually emits. The
  comparison is *characterization*: where V4 matches expectation,
  the substrate is honest for that case; where it doesn't, that's a
  finding worth examining, not necessarily a bug.

- **Findings before fixes.** If a fixture surfaces a gap (e.g.,
  V4 emits `alpha_indeterminate` where the theoretical expectation
  would be a recognizable non-algebraic-drift classification), the
  finding is recorded with full evidence. The fix is a separate
  task that this campaign may or may not recommend, depending on
  whether the gap is structurally significant.

- **Sibling comparison where applicable.** For fixtures where both
  bundles can probe (i.e., f is finite at x₀), both are run and
  their typed results are compared. For fixtures where only the
  singular bundle is meaningful (f singular at x₀), the singular
  bundle is the only meaningful arm; the scalar bundle's expected
  `SCALAR_JET_DOMAIN_REFUSED` is recorded for completeness.

- **The campaign closes a question, not opens a refactor.** At the
  end of the campaign, the joint composer (Task 024) should be
  either (a) ready to spec on the current substrate, or (b) blocked
  on a clearly-identified substrate extension. The findings make
  this call explicit.

## Fixtures

Six fixtures, ordered from cleanest to most complex. Codex implements
each in the discovery script.

### Fixture A: Pure algebraic positive (regular fractional branch)

- **Function:** `f(x) = x**0.5`
- **Point:** `x₀ = 0.0`
- **h-grid:** `[1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]`
- **Theoretical:** α = 0.5; clean fractional branch; both bundles
  should classify cleanly.
- **Purpose:** Baseline. Both bundles agree on a known clean case.
  If this disagrees with theory, something is wrong with the
  baseline, not with V4's discovery capability.

### Fixture B: Pure algebraic negative (negative singularity)

- **Function:** `f(x) = 1.0 / x` (with explicit handling: callable
  raises `ZeroDivisionError` at x=0)
- **Point:** `x₀ = 0.0`
- **h-grid:** `[1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]`
- **Theoretical:** α = -1; pure negative singularity. Scalar bundle
  structurally cannot reach (f(x₀) raises); singular bundle should
  classify as `SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY` with α ≈ -1.
- **Purpose:** Canonical sibling-disagreement case. Disagreement is
  *informative*: scalar refuses, singular observes. This is the
  pattern the joint composer must surface honestly.

### Fixture C: Slow algebraic drift

- **Function:** `f(x) = x**0.5 * (1 + 0.1 * x**0.1)`
- **Point:** `x₀ = 0.0`
- **h-grid:** `[10**(-i) for i in range(2, 9)]` (1e-2 down to 1e-8)
- **Theoretical:** Leading α = 0.5 with subleading power drift
  (ρ = 0.1, a = 0.1). Per Section 4 of the transfer paper, slope
  is `α - 1 + (aρ(α+ρ)/α) * h^ρ + ...` = `-0.5 + 0.06 * h^0.1 + ...`.
  At h = 1e-2, drift correction ≈ 0.06 * 0.63 ≈ 0.038. At h = 1e-8,
  correction ≈ 0.06 * 0.158 ≈ 0.01. Observed α drifts from ~0.54 at
  h=1e-2 toward ~0.51 at h=1e-8.
- **Purpose:** Test whether V4's current strata can express
  "classification is X *with* finite-window drift evidence." V3
  used nested-window comparison; V4 currently has nothing
  equivalent in the typed result. Findings here inform whether
  AlphaProbe needs nested-window evidence promoted from deferred
  to required.

### Fixture D: Logarithmic divergence

- **Function:** `f(x) = -log(x)` (equivalent to `log(1/x)` for x > 0;
  use `math.log` and negate, since `log(1/x)` would compute `1/x`
  first and lose precision near zero)
- **Point:** `x₀ = 0.0` (approached from the right via positive h)
- **h-grid:** `[10**(-i) for i in range(2, 10)]` (1e-2 down to 1e-9)
- **Theoretical:** `f(x) = -log(x)` diverges to +∞ as x → 0+.
  Per Section 5: `D log|g'(f)| = -1` exactly (no drift). So observed
  log-log slope is -1, observed α = 0. **But α = 0 is excluded from
  `alpha_regular_integer` per AlphaProbe doctrine (the controlled
  branch theorem requires α ≠ 0).**
- **Purpose:** Probe how AlphaProbe handles the case where observed
  α is approximately zero. Does it classify as
  `alpha_negative_singularity` (slope is negative), as
  `alpha_regular_integer` (α near 1 if interpreted differently), or
  as `alpha_indeterminate`? This is a primary discovery question.
- **Note:** Scalar bundle expected to return
  `SCALAR_JET_DOMAIN_REFUSED` (f(0) raises in standard math.log).

### Fixture E: Iterated logarithmic (the canonical case)

- **Function:** `f(x) = math.log(-math.log(x))` for `0 < x < 1`
  (rises to +∞ as x → 0+; for x near 1, log(-log(x)) → -∞ as
  -log(x) → 0+; restrict h-grid to keep -log(x₀+h) > 1, i.e.
  x₀+h < 1/e ≈ 0.368)
- **Point:** `x₀ = 0.0`
- **h-grid:** `[10**(-i) for i in range(2, 12)]` (1e-2 down to 1e-11)
- **Theoretical:** Per Section 5, `D log|g'(f)| = -1 + 1/t` where
  `t = -log(f)`. At h = 1e-2, t ≈ 4.6, slope ≈ -1 + 0.217 ≈ -0.78,
  observed α ≈ 0.22. At h = 1e-11, t ≈ 25.3, slope ≈ -1 + 0.040 ≈
  -0.96, observed α ≈ 0.04. The observed α drifts toward 0 as h
  shrinks. **The R² of the log-log fit will be high over a finite
  window — the drift is slow enough that the linear fit looks
  good locally even though the slope is changing.**
- **Purpose:** **The primary discovery question.** Does V4 emit:
  - a misleading `alpha_fractional_branch` (small positive α with
    high R²)?
  - `alpha_indeterminate` (slope fit geometrically degenerate)?
  - `alpha_negative_singularity` (slope is negative)?
  - some other stratum?
  - Different strata at different h-grid ranges?
- **Note:** Scalar bundle expected to return
  `SCALAR_JET_DOMAIN_REFUSED`. Singular bundle is the meaningful arm.

### Fixture F: Essential singularity (stress test)

- **Function:** `f(x) = math.exp(-1.0 / (x*x))` for x ≠ 0 (define
  to return 0 at x=0; finite and infinitely differentiable but not
  analytic at 0)
- **Point:** `x₀ = 0.0`
- **h-grid:** `[1e-3, 1e-2, 1e-1, 0.5]` (deliberately coarse; tighter
  grids will hit cancellation immediately)
- **Theoretical:** All derivatives at x=0 are zero. The Taylor
  series is identically zero, so no α captures the behavior. V4
  should classify as `alpha_cancellation_dominated` (transfer values
  are below precision floor) or `alpha_indeterminate` (slope fit
  degenerate).
- **Purpose:** Stress test the cancellation/indeterminate strata
  on a function with no power-law behavior. Confirm that V4
  correctly refuses to claim α evidence rather than producing a
  misleading-looking classification.

## Required Deliverables

### 1. Discovery script

Location: `Build_Docs/Reports/task023_iterated_logarithm_discovery/discovery_script.py`

The script:

- Imports `scalar_alpha_jet_bundle` and `singular_alpha_jet_bundle`
  from `lloyd_v4.primitives`, plus relevant status enums.
- Defines each of the six fixtures (function, x₀, h-grid, label).
- For each fixture, runs both bundles (scalar and singular).
- Collects typed results.
- Writes `observations_data.md` with one section per fixture,
  containing:
  - Fixture label and description
  - Scalar bundle result: status, observed_alpha, alpha_status,
    conditioning notes summary, alpha_probe_trace_id
  - Singular bundle result: same fields
  - Brief comparison summary (do they agree? disagree informatively?
    only one meaningful?)
- Uses `to_json_safe` for the value serialization where needed.
- Is runnable as `python -m Build_Docs.Reports.task023_iterated_logarithm_discovery.discovery_script`
  OR as a standalone script invocation that documents required
  PYTHONPATH.
- Does NOT add to the test suite. It is a one-time reproducible
  experiment.
- Does NOT modify any state in `src/` or `tests/`.

### 2. Raw observations data

Location: `Build_Docs/Reports/task023_iterated_logarithm_discovery/observations_data.md`

Generated by the script. One section per fixture. Includes the JSON
representation of each bundle's typed result (or a faithful summary
if full JSON is too verbose for readability).

### 3. Discovery report

Location: `Build_Docs/Reports/task023_iterated_logarithm_discovery/discovery_report.md`

Human-written analysis (i.e., Codex writes it per this spec, drawing
on the observations data). Structure:

#### Section 1: Campaign overview

- Purpose, scope, methodology (per the spec).
- The six fixtures and why they were chosen.
- The disciplines that constrained the campaign (observation-only,
  no fixes, findings before implementation).

#### Section 2: Fixture-by-fixture observations

For each fixture, in order A through F:

- **Theoretical prediction.** What the transfer paper says the
  asymptotic behavior is.
- **Scalar bundle observation.** Status emitted, observed α (if
  any), key conditioning notes, brief interpretation.
- **Singular bundle observation.** Same.
- **Sibling comparison.** Agree? Disagree informatively? Only one
  meaningful? Distinct trace_ids confirmed?
- **Honesty assessment.** Does the typed result accurately
  characterize what's happening, given the theoretical prediction?
  Three possible verdicts:
  - *Honest classification.* Typed result matches theoretical
    expectation; substrate is doing its job for this case.
  - *Honest refusal.* Typed result refuses to claim α evidence
    (`indeterminate`, `cancellation_dominated`, etc.) where theory
    predicts no clean α; substrate is honest about its limits.
  - *Misleading classification.* Typed result emits a confident-
    looking α stratum (e.g., `regular_integer` or
    `fractional_branch`) for a case where the theoretical
    expectation is non-algebraic drift. This is a substrate gap.

#### Section 3: Cross-fixture patterns

- Do all clean algebraic cases (A, B) classify as expected?
- Does the slow-drift case (C) show evidence of drift in
  conditioning notes, or does it produce a clean-looking
  classification that hides the drift?
- How does V4 handle the α ≈ 0 case (D)? Which stratum, and is the
  choice defensible?
- How does V4 handle the non-algebraic drift case (E)? Which
  stratum, and is the choice misleading or defensible?
- How does V4 handle the essential singularity case (F)? Does it
  refuse honestly?

#### Section 4: Findings

A numbered list of specific findings, each labeled by significance:

- **Substrate-honest finding:** V4 handles case X correctly per the
  theoretical expectation.
- **Strata-gap finding:** V4 emits stratum Y for case X where the
  theoretical expectation is type Z; the substrate cannot currently
  express type Z honestly.
- **AlphaProbe-extension finding:** Case X would benefit from
  nested-window stability evidence (deferred per Task 018) or from
  a new stratum (e.g., `alpha_non_algebraic_drift`,
  `alpha_unstable_window`).
- **Discovery-instrument finding:** Observation about how V4
  performs as a research instrument, not as a solver.

Each finding cites the fixture(s) it derives from and quotes the
relevant typed-result evidence from `observations_data.md`.

#### Section 5: Recommendation for Task 023b and Task 024

Based on the findings, one of:

- **Recommendation: proceed directly to Task 024 (joint composer).**
  The substrate is sufficient. The joint composer can be specified
  on the current AlphaProbe strata. Justify why the findings do
  not require substrate extension before composition.

- **Recommendation: Task 023b before Task 024.** A substrate gap
  was surfaced that should be addressed before the composer is
  specified. Articulate:
  - What the gap is (which strata, which case).
  - What extension is needed (new stratum, nested-window evidence,
    AlphaProbe extension).
  - Why the joint composer cannot honestly express the gap without
    the extension (i.e., the composer would inherit the misleading
    classification).

- **Recommendation: pause and discuss.** The findings are
  ambiguous; substantive design discussion is needed before
  committing to either path.

### 4. Task summary

Location: `Build_Docs/Reports/task023_summary.md`

Standard task-summary file:

- Scope (one paragraph)
- Test counts (pre/post; expected: 379/379 — no test changes)
- Files added: the four under
  `Build_Docs/Reports/task023_iterated_logarithm_discovery/` plus the
  summary itself.
- Confirmation that no `src/` files were modified
  (`git diff --stat src/` should show no changes; the repo is now
  under git, per Will's note).
- Brief synthesis: which recommendation was reached.
- Pointer to the full discovery report.

## Required Observations

For each fixture, the discovery script records:

- Fixture label, function source (as a string for the report),
  x₀, h-grid.
- Scalar bundle: full TypedResult, with at minimum:
  status (string value), observed_alpha (or null),
  alpha_status (string value or null), alpha_probe_trace_id,
  conditioning notes (the tuple of strings), validity fields.
- Singular bundle: same.
- Sibling trace distinctness: confirmation that the two
  alpha_probe_trace_ids differ when both arms emit a result.

## Required Analysis

In `discovery_report.md`, for each fixture, Codex provides:

- Honesty assessment per Section 2 above (one of: honest
  classification, honest refusal, misleading classification).
- One-paragraph interpretation of what the typed result tells
  us about V4's substrate capability for this case.

The cross-fixture synthesis (Section 3) explicitly addresses:

- Whether all six fixtures produced honest typed results (under
  the three-verdict framework).
- Which fixtures, if any, produced misleading classifications.
- Whether the misleading classifications cluster around a
  specific gap (e.g., "all non-algebraic-drift cases classify as
  X when theoretical expectation is Y").

## Required Commands

```bash
# Pre-task baseline
python -m pytest -x tests/ -q

# Verify git is now in place
git status

# After implementation: run the discovery script
PYTHONPATH=src python Build_Docs/Reports/task023_iterated_logarithm_discovery/discovery_script.py

# Confirm no src/ changes
git diff --stat src/

# Confirm no test changes
git diff --stat tests/

# Full suite (must remain unchanged)
python -m pytest -x tests/ -q
```

Expected: full suite passes at 379 tests (unchanged from baseline).
No files in `src/` modified. No tests in `tests/` modified.

## Non-Goals (loud and explicit)

- **Do NOT modify any file in `src/`.** Discovery-only task.
- **Do NOT modify any existing test file.** No new test code; the
  discovery script is not a test.
- **Do NOT add any pytest file under `tests/`.** The script lives
  under `Build_Docs/Reports/task023_iterated_logarithm_discovery/`,
  not `tests/`. It is run manually as part of the campaign.
- **Do NOT implement any substrate fix, even if a gap is observed.**
  Findings are findings. The follow-up implementation (if any) is
  a separate task to be specified after this campaign's findings
  are reviewed.
- **Do NOT extend AlphaProbe, even with a new stratum.** If the
  findings recommend a new stratum, that's a recommendation for
  Task 023b, not a deliverable of this task.
- **Do NOT modify METROLOGY_PRINCIPLES.md, STATUS_CALCULUS.md, or
  any architectural document.** The findings may reference these,
  but they are read-only for this task.
- **Do NOT introduce nested-window evidence or window-stability
  analysis** even if the findings strongly recommend it. That's
  Task 023b territory.
- **Do NOT consult Layer 2+ modules** (metrology, branch, refinery,
  history, solver) for any evidence. They remain reference-only.
- **Do NOT cite V3 or V1 implementations as evidence of what V4
  should observe.** The theoretical reference is the transfer
  function paper, not the V3 codebase.

## Completion Report

Create `Build_Docs/Reports/task023_summary.md` with:

- **Scope summary** (one paragraph): what the campaign did.
- **Test counts.** Expected: pre 379, post 379 (no test changes).
- **Files added.** Expected list:
  - `Build_Docs/Reports/task023_iterated_logarithm_discovery/discovery_script.py`
  - `Build_Docs/Reports/task023_iterated_logarithm_discovery/observations_data.md`
  - `Build_Docs/Reports/task023_iterated_logarithm_discovery/discovery_report.md`
  - `Build_Docs/Reports/task023_summary.md`
- **Headline finding** (one-sentence summary of the most significant
  observation).
- **Recommendation** (one of the three Section-5 options).
- **Confirmation** that `git diff --stat src/` shows no changes.
- **Confirmation** that `git diff --stat tests/` shows no changes.
- **Pointer** to the discovery report for the full analysis.

## Acceptance Criteria

- The discovery script is runnable and produces
  `observations_data.md` deterministically.
- All six fixtures (A through F) are observed by both bundles
  where applicable; the singular-only cases (D, E) document the
  scalar bundle's expected refusal.
- The discovery report contains all five sections (overview,
  fixture-by-fixture observations, cross-fixture patterns,
  findings, recommendation).
- Each fixture's honesty assessment is one of the three defined
  verdicts (honest classification / honest refusal / misleading
  classification).
- A recommendation is made for Task 024's specifiability.
- Full test suite passes at 379 (unchanged baseline).
- No file in `src/` is modified.
- No file in `tests/` is modified.
- The repository remains under git control with no unintended
  changes outside `Build_Docs/Reports/task023_iterated_logarithm_discovery/`
  and the summary file.

## Discipline Notes

- **The campaign is a research instrument exercise, not solver
  development.** Per DISCOVERY_PHILOSOPHY.md: "The engine produces
  no failures, only observations of varying refinement." Each
  fixture produces an observation of some refinement level. A
  fixture where V4 emits a misleading classification is *not* a
  failure of V4 — it is a refined observation about where the
  substrate currently expresses geometry honestly and where it
  doesn't. Both kinds of observations are valuable. The campaign
  exists to make the distinction explicit.

- **The recommendation matters more than the headline.** The
  campaign's deliverable is not "V4 passes" or "V4 fails." The
  deliverable is a clean recommendation about whether the joint
  composer can be specified on the current substrate. That
  recommendation will be either yes-proceed-to-024, no-need-023b-
  first, or pause-and-discuss. All three are valid outcomes.

- **AlphaProbe is the load-bearing primitive under examination.**
  The two bundles delegate to AlphaProbe; if AlphaProbe's strata
  are insufficient for non-algebraic-drift cases, both bundles
  inherit the insufficiency. Any substrate extension recommended
  would likely be AlphaProbe-level, not bundle-level.

- **The transfer paper Section 5 is the theoretical reference.**
  V3's slope-flow model comparison machinery is *not* a reference
  for what V4 should do. V4 may end up doing something
  structurally different (e.g., emitting a typed
  non-algebraic-drift stratum rather than running BIC comparison
  internally). The V3 approach is mechanical-property guidance
  per the reference-hygiene rules; the V4 derivation, if any, must
  stand on its own.

- **Forward reference (Task 023b, conditional).** If the campaign
  recommends a substrate extension, the next task is 023b. Its
  shape will be informed by the specific gap surfaced — likely
  either:
  - A new AlphaProbe stratum (e.g., `alpha_non_algebraic_drift`)
    derived from explicit slope-flow evidence within AlphaProbe.
  - Promotion of nested-window stability evidence from deferred
    to required.
  - Both.
  - Something else surfaced by the campaign that isn't obvious from
    the spec.

- **Forward reference (Task 024).** The joint composer is the
  destination. Whether 023 leads directly to 024 or via 023b
  depends on the findings. Do not specify 024 within this task
  even tentatively; the composer's shape must be informed by
  whatever the post-discovery substrate looks like.

- **Layer 2+ remains reference-only.** No consultation, no imports,
  no citations as evidence for V4 behavior.
