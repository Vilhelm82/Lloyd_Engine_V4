# Codex Task 025 — Arithmetic Path Law Discovery

## 1. Repository & Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4` (laptop).

**Pre-task baseline:**

```bash
cd ~/projects/V4/Lloyd_Engine_V4
source .venv/bin/activate
git status                                    # clean tree
git log -1 --format='%h %s'                   # should be post-017b
python -m pytest -q tests/ 2>&1 | tail -3     # 431 tests passing
```

Do not start if baseline is dirty or any tests fail.

---

## 2. Task Goal

Treat the **path-response law** as the unknown to be discovered.

For an arithmetic path P and input x, define:

```
R_P(x, p)  =  fl_p(P)(x)  -  P_exact(x)
```

where `fl_p(P)` is the IEEE 754 evaluation of P at precision p and
`P_exact(x)` is the algebraic truth (here, identically 0 for the four-form
battery).

Find a law `L_P(x, p)` or envelope bound `E_P(x, p)` such that:

```
R_P(x, p) ≈ L_P(x, p)         (signed or structured law)
|R_P(x, p)| ≤ E_P(x, p)        (envelope bound)
```

The campaign **discovers** the law from observed residuals, a constrained
candidate term library, precision-scaling evidence, zero/sign masks, and
oracle comparison. No closed-form law is hand-wired into the discovery
machinery. The known result for F4 (`δf / (2·√f)`) serves as a
**rediscovery gate**: the discovery system must rank that term first
when applied to F4 data, or the candidate library / fitting machinery
needs adjustment before any law claims are trusted.

This is **not** an envelope-predictor task. It is law-discovery only.
Observation, fitting, and validation — no deconvolution, no correction,
no solver work.

---

## 3. Three Flavours of Closed Form

IEEE 754 rounding is deterministic but discontinuous and lattice-like.
"Closed form" can mean three different things, listed in order of
honesty:

1. **Exact bit-level replay law.** Run the same operation graph with
   IEEE rounding operators at each step. Bit-exact, but algorithmic and
   not pretty. This is what `decimal.Decimal` operating on the actual
   double bit-patterns approximates.

2. **First-order instrument envelope.** Predict the response scale from
   operation-chain sensitivities and unit roundoff:
   `R_P(x) ≈ Σᵢ Sᵢ(x) δᵢ` where `Sᵢ(x)` is the sensitivity of the final
   expression to the rounding perturbation `δᵢ` at operation i, with
   `|δᵢ|` bounded by the unit roundoff or a local ULP rule.

3. **Discovered asymptotic / path law.** A compact expression such as
   `δf / (2·√f)` inferred from observed residuals plus known variables
   plus chain structure. This is what the campaign is hunting for.

Task 025 fits flavour 3 with flavour 2 as the principled baseline.
Flavour 1 (decimal oracle) is the truth reference. Flavours 1 and 2 are
already characterised by Task 017b.

---

## 4. Source Labelling

**V4-surface:** existing primitives in `src/lloyd_v4/`, the four-form
fixture (Task 024b), and the multi-precision fixture (Task 017b). No new
primitives, no new status families.

**Mechanical-property reference:** the IEEE 754 specification's
correctly-rounded operations, standard first-order roundoff analysis
(Wilkinson-style — used as a method, not imported as a named result),
and the F4 closed-form `δf / (2·√f)` from V3 / Task 024b. The closed
form is used as the **rediscovery gate**, not pre-wired into the
fitting machinery.

**Proposal evidence:** the candidate-term library in §8 and the typed
`PathEnvelopeLawDiscovery` result shape in §11. These are the campaign's
contribution to the substrate's understanding of itself. Whether they
hold across forms is the empirical question.

---

## 5. Design Principles

**No new primitives, status families, or manifest entries.** The
`PathEnvelopeLawDiscovery` object exists only in the campaign output, not
yet as a V4 substrate observable. Promotion to substrate is a downstream
task informed by 025's findings.

**The law is the unknown.** The discovery machinery does not assume the
F4 closed form. It is given a candidate library and must rank the F4 law
from that library by fit quality, or report failure.

**Operator-structure constrains the candidate library.** Candidate terms
are derived from the actual operation graph — operand magnitudes, ULPs
of intermediates, path roundoffs, sensitivities. No arbitrary symbolic
content. No `log`, `sin`, `exp`, `gamma`, etc. The library is built from
what the IEEE 754 chain physically does.

**Sparse fits only.** A "law" is at most a small sum (≤ 3 terms in
this campaign) of weighted candidate terms. Anything richer is flagged
as `path_law_overfit`. Beauty and parsimony are protections against
fitting noise as structure.

**Validation is multi-axis.** A candidate law survives only if it is
consistent across: precision (float32/float64), region (near/middle/far),
zero mask, sign mask, and per-form fit quality. A law that fits F4
beautifully at float64 but breaks under float32 scaling is not a law —
it's an artefact.

**Decimal is admitted** as substrate-precision arithmetic for the oracle
pathway. `numpy.float32` / `numpy.float64` as type containers.
`numpy.linalg.lstsq` is admitted for sparse OLS regression — it is
generic linear algebra over arrays, no named mathematical content. No
`import math`, no `numpy.sqrt`, no `scipy.stats`, no `scipy.optimize`,
no `sklearn`, no `sympy`, no `mpmath`.

**No retro-fitting.** If the F4 law is not rediscovered by the
machinery, the failure is the finding. Do not enrich the candidate
library mid-flight to make F4 work.

---

## 6. Primitive-Sufficiency Gate

| Concept | Source | Notes |
|---|---|---|
| Four-form fixture | `lloyd_v4.evals.schwarzschild_four_form` | Re-used. |
| Multi-precision fixtures | `lloyd_v4.evals.multi_precision_four_form` | Re-used. |
| Chain envelope helper | same module | Re-used as one candidate term. |
| Decimal oracle | `decimal.Decimal` (stdlib) | Truth reference. |
| OLS regression | `numpy.linalg.lstsq` | Substrate utility, not named math. |
| Existing typed primitives | `lloyd_v4.primitives.*` | Used for AlphaProbe / transfer status per form (descriptive evidence only). |

No new substrate concepts are introduced.

---

## 7. Mathematical Framing

### 7.1 Residual definition

For each form k ∈ {1,2,3,4}, precision p ∈ {float32, float64}, and r in
the V3 sweep:

```
R_{k,p}(r) = F_k_obs_{p}(r) - F_k_truth(r)
```

For the four-form battery, `F_k_truth(r) = 0` algebraically. The
operational truth is `F_k_decimal_50(r)`, computed via the existing
017b decimal oracle. Residuals are reported relative to the decimal
oracle, not relative to algebraic zero, to keep the comparison
substrate-honest (the oracle itself may carry small representation
artefacts).

### 7.2 First-order sensitivity expansion

For an operation graph G = (op_1, op_2, ..., op_n) producing F_k(r):

```
R_{k,p}(r) ≈ Σ_{i=1}^{n} S_i(r) · δ_i
```

where:
- `δ_i` is the rounding perturbation at operation i, with `|δ_i| ≤ u_p`
  (the unit roundoff for precision p, e.g. `u_64 = 2^-53`).
- `S_i(r)` is the sensitivity ∂F_k / ∂(intermediate_i) evaluated at the
  exact arithmetic path.

The first-order envelope is:

```
E_{k,p}^{(1)}(r) = u_p · Σ_i |S_i(r)| · |intermediate_i(r)|
```

This is a conservative upper bound. A tighter law `L_{k,p}(r)` can
sometimes be written as a signed combination of dominant `S_i(r)`
terms — that is what 025 hunts for.

### 7.3 Candidate law shape

A candidate law has the form:

```
L_{k}(r) = Σ_{j=1}^{m} c_j · T_j(r)
```

where:
- `T_j(r)` is a term drawn from the candidate library (§8).
- `c_j` is a fitted coefficient (real, OLS-fitted).
- `m ≤ 3` (sparse fit).

Precision dependence enters through `u_p`: a single fitted `L_k(r)` is
then validated against multiple precisions by scaling.

---

## 8. Candidate Term Library

The library is operator-structure-derived. Each term is a function of
known variables computed in float64 (the substrate precision):

### 8.1 Operand magnitudes

- `T_1(r) = 1`
- `T_2(r) = f(r) = 1 - 2/r`
- `T_3(r) = R(r) = √f(r)`
- `T_4(r) = √f(r)` (alias of T_3 for fitting clarity)
- `T_5(r) = 1 / √f(r)`
- `T_6(r) = 1/r`
- `T_7(r) = r - 2`
- `T_8(r) = (r - 2) / r`

### 8.2 Operand ULPs

- `T_9(r) = ulp(f(r))` — ULP spacing at f
- `T_10(r) = ulp(R(r))` — ULP spacing at √f
- `T_11(r) = ulp(2/r)`

### 8.3 Path roundoff residuals

- `T_12(r) = δf(r) = (1 - 2/r) - (r - 2)/r` — the V3 path-roundoff on f
- `T_13(r) = δR(r) = √(1 - 2/r) - √((r - 2)/r)` (this is F4 itself; only
  used in a separate validation pass, not in fitting F4)

### 8.4 Composite terms (operator-derivative-motivated)

- `T_14(r) = δf(r) / √f(r)`
- `T_15(r) = δf(r) / (2 · √f(r))` — **the F4 closed-form candidate**
- `T_16(r) = δf(r) · √f(r)`

### 8.5 Chain envelope

- `T_17(r) = chain_envelope(r)` — the 017b operand-scale envelope.

The library has 17 terms. Sparse OLS over subsets of size ≤ 3 from this
library gives a search space of `C(17,1) + C(17,2) + C(17,3) = 17 + 136 +
680 = 833` candidate laws per form. Tractable by exhaustive search.

For F4, the rediscovery gate requires T_15 to appear in the top-ranked
1-term fit. For F1, F2, F3 there are no pre-named candidates; the
algorithm reports what it finds.

---

## 9. Fitting Machinery

### 9.1 Fit procedure (per form, per precision)

For each form k and precision p, and each candidate subset S ⊆ library
with |S| ≤ 3:

1. Build the regression matrix X with columns T_j(r) for j ∈ S, rows
   indexed by r in the sweep, restricted to rows where R_{k,p}(r) is
   non-zero (degenerate-row exclusion).
2. Build the target vector y with entries R_{k,p}(r) at those rows.
3. Solve `c = numpy.linalg.lstsq(X, y, rcond=None)[0]`.
4. Compute fit quality:
   - Residual RMS: `sqrt(mean((X @ c - y)**2))`
   - R²: `1 - sum((y - X@c)**2) / sum((y - mean(y))**2)`
   - Coefficient magnitudes: `|c_j|`
   - Conditioning: condition number of X
5. Rank fits by R², then by parsimony (smaller |S| preferred at equal R²
   within tolerance 0.01).

### 9.2 Coefficient validation

For each top-ranked fit, the coefficients `c_j` must be:

- **Real and finite** (no NaN, no Inf)
- **O(1) or O(u_p)** in magnitude (a coefficient of 1e15 indicates the
  fit is exploiting numerical noise; reject)
- **Stable under bootstrap** — re-fit on random 80% subsets 20 times and
  confirm coefficient signs and magnitudes are consistent

A fit that passes all three is admissible. Otherwise: `path_law_overfit`
or `path_law_rejected`.

### 9.3 Precision-scaling validation

For each admissible fit at float64, predict the float32 residuals using
the same fitted coefficients (with `u_p` rescaled appropriately if the
fit involves a u_p-dependent term, otherwise unchanged). Compare to
observed float32 residuals.

- If predicted float32 / observed float32 ratio has median in [0.2, 5.0]:
  `precision_scaling_supported`
- Otherwise: `precision_scaling_failed`

A law that passes float64 fit but fails precision scaling is **not a
law** — it is a float64-specific artefact. Status downgrades from
`path_law_supported_closed_form` to `path_law_precision_scaled` only if
scaling holds.

### 9.4 F4 rediscovery gate

A specific validation step: when fitting F4 over the full candidate
library at float64, the 1-term fit with the highest R² **must** select
T_15 (`δf / (2·√f)`). If the top-ranked 1-term fit selects a different
term, the campaign records this as a failure of the rediscovery gate
and the overall campaign status is downgraded. F4's law claim is then
not trusted regardless of how well anything else fitted.

---

## 10. Validation Axes

Each emitted law is validated against:

- **Axis A — Run-repeat determinism.** Bit-exact re-run.
- **Axis B — Precision scaling.** Float32 vs float64 (§9.3).
- **Axis C — Oracle agreement.** Predicted L_k(r) vs decimal-50 residuals
  for the algebraic-zero baseline.
- **Axis D — Regional consistency.** Fit holds in near, middle, far
  regions separately (re-fit per region; coefficients should be
  consistent up to a stated tolerance).
- **Axis E — Zero-mask consistency.** The law correctly predicts zero
  where the observed residual is zero (sign agreement on the zero mask).
- **Axis F — Sign-pattern consistency.** The signed law matches observed
  signs at non-zero points within a declared threshold (e.g. ≥ 80% of
  non-zero points have matching sign).

---

## 11. The PathEnvelopeLawDiscovery Result Shape

This is the typed object emitted per form in the campaign output. It is
not a substrate observable in V4 (yet). It is a result schema for the
discovery campaign.

### 11.1 Statuses

| Status | Meaning |
|--------|---------|
| `path_law_exact_zero` | All observed residuals are exactly 0; law is L_k(r) = 0. Calibration zero. |
| `path_law_supported_closed_form` | A sparse closed-form law fits with R² ≥ 0.95 AND passes all six validation axes. |
| `path_law_supported_envelope` | The chain-envelope bound holds (|R| ≤ E with margin) but no closed-form law passes thresholds. |
| `path_law_lattice_structured` | Residuals are non-zero but quantised at integer-ULP levels with predictable lattice structure. No smooth fit; structure is discrete. |
| `path_law_piecewise_supported` | Different laws fit different regions; per-region fits pass thresholds but no global law does. |
| `path_law_precision_scaled` | Float64 fit succeeded but precision scaling failed; the fit is artefact, not law. |
| `path_law_indeterminate` | No fit passes thresholds; insufficient structure to classify. |
| `path_law_rejected` | Best fit produces unstable / non-finite / O(huge) coefficients. |
| `path_law_overfit` | Best fit uses ≥ 3 terms with R² gain over 1-term fit below tolerance — flagged as overfitting noise. |

### 11.2 Value shape

```python
@dataclass(frozen=True)
class PathEnvelopeLawValue:
    path_id: str                          # "F1", "F2", "F3", "F4"
    expression_family: str                # "schwarzschild_four_form"
    variables_used: tuple[str, ...]       # ("r", "f", "R", "delta_f")
    precision_set: tuple[str, ...]        # ("float32", "float64", "decimal_50")
    oracle_path: str                      # "decimal_50"
    residual_summary: dict                # min, median, max, IQR per precision
    candidate_terms_evaluated: int        # 833
    selected_law: dict | None             # {"terms": [...], "coefficients": [...], "r_squared": ...}
    envelope_bound: dict | None           # {"formula": "...", "max_residual_over_bound": ...}
    ratio_statistics: dict                # F_obs / L_predicted by region
    zero_mask_signature: dict             # zero-mask agreement axis E
    sign_signature: dict                  # sign-agreement axis F
    region_summaries: dict                # axis D
    validation_results: dict              # per-axis pass/fail
    rediscovery_gate: dict | None         # F4 only: did T_15 win the 1-term fit?
```

The campaign output is a dict keyed by form name, each value matching
this shape. Serialisable to JSON.

---

## 12. Module Layout

### 12.1 New module: `src/lloyd_v4/evals/path_law_discovery.py`

Provides:

```python
def build_candidate_library() -> List[CandidateTerm]: ...
def evaluate_terms(library, r_values) -> np.ndarray: ...  # shape (n_r, n_terms)
def fit_sparse_ols(X, y, max_terms=3) -> List[FitCandidate]: ...
def rank_fits(fits, parsimony_tolerance=0.01) -> List[FitCandidate]: ...
def validate_fit_axis_A(fit) -> AxisResult: ...
def validate_fit_axis_B(fit, residuals_32, residuals_64) -> AxisResult: ...
def validate_fit_axis_C(fit, residuals_oracle) -> AxisResult: ...
def validate_fit_axis_D(fit, region_residuals) -> AxisResult: ...
def validate_fit_axis_E(fit, zero_mask) -> AxisResult: ...
def validate_fit_axis_F(fit, sign_mask) -> AxisResult: ...
def classify_law(fit, axis_results, rediscovery_gate=None) -> PathLawStatus: ...
def discover_path_law_for_form(form_id, r_values, residuals_dict) -> PathEnvelopeLawValue: ...
```

### 12.2 New module: `src/lloyd_v4/evals/path_law_campaign.py`

Campaign driver. Runs discovery per form, applies the F4 rediscovery
gate, aggregates results into the campaign output JSON.

Output to:
`Build_Docs/Reports/task025_path_law_discovery/campaign_output.json`

### 12.3 Output directory

`Build_Docs/Reports/task025_path_law_discovery/`
- `campaign_output.json`
- `README.md`

Plus `Build_Docs/Reports/task025_summary.md` — completion report.

---

## 13. Required Tests

`tests/test_task025_path_law_discovery.py`:

### 13.1 Module symbol availability and call signatures

All public symbols importable and callable as documented.

### 13.2 Candidate library structure

`build_candidate_library()` returns exactly 17 terms with the names from
§8.

### 13.3 Term evaluation correctness

For each term T_j, evaluate at a known r (e.g. r=4.0) and compare to a
hand-computed value to within 1 ULP. This catches typos in the term
definitions, which would silently corrupt the discovery.

### 13.4 OLS regression sanity

Hand-construct a synthetic regression problem with known coefficients
(e.g. y = 2·T_15(r) + 1e-18 * gaussian noise). Run `fit_sparse_ols`. The
top-ranked 1-term fit must select T_15 with coefficient near 2 (within
1%). If this fails, the regression machinery itself is broken.

### 13.5 F3 must classify as exact_zero

`discover_path_law_for_form("F3", ...)` returns
`status == "path_law_exact_zero"`. This is non-negotiable — F3 is the
calibration zero, and any other classification invalidates the
discovery machinery.

### 13.6 F4 rediscovery gate

`discover_path_law_for_form("F4", ...)`:
- Top-ranked 1-term fit must select T_15 (`δf / (2·√f)`).
- `value.rediscovery_gate["winning_term"] == "T_15"`.
- `value.rediscovery_gate["passed"] == True`.

If this fails, the campaign records the failure prominently and the
other forms' law claims are quarantined as untrusted.

### 13.7 Coefficient sanity for F4

The fitted coefficient for T_15 in F4's law should be near 1.0 (the V3
transfer law has no numerical prefactor other than the 1/2 already
absorbed into the term). Allowed range: [0.5, 2.0]. Outside that range
indicates the term is being misused by the fitter.

### 13.8 Precision-scaling validation runs

For F4, axis B (precision scaling) must run to completion and emit a
pass/fail. The test does not require pass — the result is the finding.

### 13.9 Determinism

Run the campaign twice in separate processes, assert byte-equal output.

### 13.10 Source purity

No `import math`, no `numpy.sqrt`, no `scipy`, no `sympy`, no `sklearn`,
no `mpmath`, no `lloyd_v3`. `numpy.linalg.lstsq` is admitted. `decimal`
is admitted in the oracle pathway only.

### 13.11 Manifest non-regression

`len(lloyd_v4.primitives.__all__)` unchanged from post-017b baseline.

---

## 14. Required Commands

```bash
# Pre-task baseline
git status                                            # clean tree
python -m pytest -q tests/ 2>&1 | tail -3             # 431 passing

# Implementation
# ... discovery module, campaign module, test file, report directory ...

# Verification
python -m pytest -q tests/test_task025_path_law_discovery.py
python -m pytest -q tests/                            # full suite still green
python -m pytest -q tests/test_task001_source_purity.py

# Run the campaign
PYTHONPATH=src python -m lloyd_v4.evals.path_law_campaign

# Determinism verification
PYTHONPATH=src python -m lloyd_v4.evals.path_law_campaign \
    --output /tmp/path_law_repeat.json
diff Build_Docs/Reports/task025_path_law_discovery/campaign_output.json \
     /tmp/path_law_repeat.json

# Manifest audits
python -m pytest -q \
    tests/test_task010a_layer_manifest_machine_readable.py \
    tests/test_task010b_export_drift.py \
    tests/test_task010b_manifest_completeness.py \
    tests/test_task010c_no_unregistered_operations.py \
    tests/test_task010c_lineage_terminates_in_primitive.py \
    tests/test_task010c_no_chain_cycles.py

# Commit and push
git add -A
git status
git commit -m "Task 025: Arithmetic path law discovery campaign"
git push origin main
```

---

## 15. Non-Goals

- **No envelope predictor.** Law discovery only. The predictor is a
  downstream task informed by 025's findings.
- **No deconvolution.** No correction of observed residuals using
  fitted laws.
- **No solver behavior.** No equation-solving, no root-finding.
- **No new primitives, status families, or manifest entries.** The
  `PathEnvelopeLawDiscovery` shape exists in the campaign output only.
- **No correction of computed observations.** R_{k,p}(r) is what it is.
- **No expansion of the candidate library mid-flight.** If F4 fails to
  rediscover, the failure is the finding. Do not enrich.
- **No symbolic regression with arbitrary functions.** `log`, `sin`,
  `exp`, `gamma`, fractional powers other than √ — all out. The library
  is operator-structure-constrained.
- **No SR or Bell fixtures** — those are future 024c, 024d work.
- **No multi-precision execution beyond float32 / float64 / decimal**.
- **No claim that "the substrate model is confirmed" or "rejected"** —
  the campaign produces typed law-discovery results per form. Higher-level
  interpretation is downstream.

---

## 16. Completion Report Template

`Build_Docs/Reports/task025_summary.md` must contain:

### Scope

The three-flavor framing, the candidate-library, and what was attempted.

### Test count

Pre-task baseline (post-017b): 431.
Post-Task 025: 431 + N.

### Files changed

Bulleted list.

### Per-form discovery results

A table with one row per form, columns:
- Status (one of the §11.1 enum values)
- Top-ranked 1-term fit (term name + coefficient)
- Top-ranked 2-term fit (terms + coefficients)
- R² of top fit
- Axes passed (A–F)
- Notable observations

### F4 rediscovery gate result

A clearly-marked subsection. Pass / fail. If pass: the winning term,
coefficient, R², and confirmation that the discovery machinery is
trustworthy. If fail: what term won instead, why the gate failed, and
the consequent quarantine status on all other form claims.

### F1, F2 honest classifications

The most likely outcome is `path_law_lattice_structured` or
`path_law_piecewise_supported` for F1/F2. Whatever the classification,
record:
- Why this classification (which axes passed, which failed)
- Whether any candidate term ranked usefully
- Whether a piecewise fit was attempted

### F3 calibration-zero confirmation

Trivial but load-bearing.

### Precision-scaling results

For each form's top fit, the precision-scaling axis B result: predicted
float32 from float64 fit, observed float32, median ratio,
pass / fail.

### Honest observations

- Any term that ranked unexpectedly highly across multiple forms
  (cross-form invariants are very interesting).
- Any term that was expected to rank highly but did not.
- Any fit that passed R² thresholds but failed bootstrap / precision /
  region consistency.
- Edge cases at the sweep boundaries.

### Limits

- Schwarzschild only.
- Library size 17, sparse fits to 3 terms.
- 833 candidate fits per form.
- Decimal-50 oracle, float32/float64 IEEE 754.
- No long double, no mpmath.

### Audits

Standard.

---

## 17. Acceptance Criteria

1. Pre-task baseline confirmed (431 tests green).
2. New modules at `src/lloyd_v4/evals/path_law_discovery.py` and
   `path_law_campaign.py`.
3. `tests/test_task025_path_law_discovery.py` exists; all tests pass.
4. Full test suite green.
5. Campaign produces deterministic `campaign_output.json`.
6. F3 classified as `path_law_exact_zero`.
7. **F4 rediscovery gate passes** (top-ranked 1-term fit selects
   T_15 = `δf / (2·√f)` with coefficient in [0.5, 2.0]).
8. F1, F2 receive an honest classification from §11.1 (not `indeterminate`
   unless genuinely indeterminate — but `indeterminate` is acceptable).
9. Precision-scaling axis runs to completion for every admissible fit.
10. Completion report filled per §16.
11. All changes committed and pushed.

If F4's rediscovery gate fails, the task is still **complete** — but the
completion report must document the failure prominently and quarantine
F1/F2 results until the discovery machinery is reviewed. A failed
rediscovery gate is a substrate-honest finding, not a bug.

---

## 18. Discipline Notes (Forward References)

### What this campaign's findings inform

- **Typed promotion of `PathEnvelopeLawDiscovery` to substrate.** A
  downstream task could promote this result shape to a V4-substrate
  typed observable with status family, primitive operation, manifest
  entry, and protocol. Not 025.

- **Envelope predictor utility.** Now properly downstream: 025 must
  produce confirmed laws before a predictor that USES those laws can be
  built honestly. Not 025.

- **Cross-form invariants.** If a single candidate term ranks usefully
  across F1, F2, F4 (F3 excluded as zero), that term is an exceptionally
  interesting promotion candidate.

### What this task explicitly does not do

- No deconvolution, no correction, no solver work.
- No promotion to substrate — the typed shape lives in campaign output
  only.
- No claim that V4's instrument model is "confirmed" or "rejected"
  globally. Per-form law discovery is the campaign's scope.

### The deeper claim this task tests

IEEE 754 is deterministic, so each arithmetic path has an invariant
response signature. V4 can learn that signature from observable
substrate evidence + a constrained candidate library. The F4 rediscovery
gate tests whether the learning machinery actually works on a known
case. If it does, the same machinery can be applied to unknown paths
and trusted within its declared validation envelope. If it does not,
the machinery needs work before any unknown-path claims can be made.

The task succeeds whether the gate passes or fails. What it cannot do is
declare an unknown law trustworthy without the gate having passed on the
known law first.

---

*End of Codex Task 025 specification.*
