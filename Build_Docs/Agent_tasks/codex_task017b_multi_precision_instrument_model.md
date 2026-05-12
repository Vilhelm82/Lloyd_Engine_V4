# Codex Task 017b — Multi-Precision Confirmation of the IEEE 754 Instrument Model

## 1. Repository & Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4` (laptop).

**Pre-task baseline:**

```bash
cd ~/projects/V4/Lloyd_Engine_V4
source .venv/bin/activate
git status                                    # clean tree
git log -1 --format='%h %s'                   # last commit should be Task 024b
python -m pytest -q tests/ 2>&1 | tail -3     # 423 tests passing
```

Record post-024b test count in the completion report. Do not start if
baseline is dirty or any tests fail.

---

## 2. Task Goal

Confirm the IEEE 754 instrument model that emerged from Task 024b through
three independent tests:

- **Phase A (oracle comparison):** Test that V4's double-precision
  observations of the four-form Schwarzschild battery agree with a
  high-precision decimal reconstruction to within the chain's accumulated
  per-operation rounding envelope. This tests *instrument self-consistency*
  at the precision V4 actually runs on.

- **Phase B (multi-precision scaling):** Test that the IEEE 754 instrument
  response shifts predictably when machine epsilon changes. Run the
  four-form battery at `numpy.float32` (binary IEEE 754 single precision,
  eps ≈ 1.19e-7) and at native `float` / `numpy.float64` (binary IEEE 754
  double precision, eps ≈ 2.22e-16). Confirm F₄ magnitudes scale by a
  ratio close to eps_32 / eps_64 ≈ 5.4e8.

- **Phase C (calibration zero):** Test that the same-path form F₃ produces
  exactly zero at every precision tested. F₃ is the instrument's
  calibration zero; it must be precision-independent.

This task does **not** add primitives. It is a confirmation campaign,
analogous to Task 024b in scope and shape.

---

## 3. Source Labelling

**V4-surface:** existing primitives in `src/lloyd_v4/`. No new primitives,
no new status families.

**V4 reference fixture:** the four-form Schwarzschild battery introduced
in Task 024b. This task re-uses the existing
`src/lloyd_v4/evals/schwarzschild_four_form.py` module for the double-
precision pathway. Multi-precision pathways (float32, decimal) are added
as new sibling functions in a new module
`src/lloyd_v4/evals/multi_precision_four_form.py`.

**Mechanical-property reference (from V3 work):** the transfer function
exponent family and the four-form arithmetic path comparison — these
established the empirical pattern this task tests. V3 results are not
consulted in 017b's confirmation logic.

**Proposal evidence:** the IEEE 754 instrument model itself — that
roundoff is deterministic, precision-dependent, and predictable from the
spec. This task tests the model; the test outcome is the result, not a
target.

---

## 4. Design Principles

**No new primitives, no new status families, no new manifests.** Pure
confirmation campaign.

**Decimal is acceptable as substrate-precision arithmetic.** Per the
discussion that produced this task: `decimal.Decimal` is generic
arbitrary-precision arithmetic with no named mathematical content, no
hardcoded constants, no named theorems. It is used here as the algebraic
oracle for the IEEE 754 chain. This is substrate self-knowledge, not
named-content import. Axiom 11 considers and admits this usage; the spec
records the consideration explicitly.

**`numpy` is acceptable for type machinery only.** `numpy.float32` and
`numpy.float64` are typed numeric containers, not math content. No
`numpy.sqrt`, no `numpy.linalg`, no special functions. Use `** 0.5` for
square roots in all pathways.

**No `import math`.** Axiom 11 violation. The draft script's use of
`math.sqrt` and `math.ulp` is replaced with `** 0.5` and a hand-rolled
ULP helper using `struct.pack`/`struct.unpack` (V4 convention).

**Deterministic output.** Campaign output JSON must be byte-stable across
runs. No timestamps in payload, no random ids.

**Conclusion follows from data.** The completion report states what the
campaign measured. The model is confirmed if (and only if) the
quantitative tests pass within the declared tolerances. If they fail, the
report states that plainly — the conclusion is the data, not the
expectation.

---

## 5. Issues in the Draft (Pre-Task Reference)

The draft script `multi_precision_confirmation_017b.py` had three
structural problems and several surface problems. This section records
them so Codex does not reproduce them.

**Structural:**

1. **Hardcoded confirmation regardless of data.** The draft printed
   `Agreement (obs/exp): 2.500 (ideal ~1.0)` — a 150% deviation from
   prediction — and then wrote `"model_supported": true` to JSON
   unconditionally. The conclusion contradicted the data. This task's
   conclusion follows from the test outcomes.

2. **Decimal precision floor masquerading as a measurement.** The draft's
   100-digit decimal run reported max |F4| = 1.0e-100 — exactly the
   decimal precision limit, not a meaningful F4 value. Pinning at the
   precision floor means the run was measuring decimal's own
   representation cutoff, not the IEEE 754 instrument response. This task
   uses decimal at 50 digits as an *oracle* for the chain's algebraic
   truth, not as a "higher-precision IEEE 754."

3. **Decimal ≠ IEEE 754 at higher precision.** Decimal arithmetic and
   IEEE 754 binary arithmetic are different systems. Testing
   precision-scaling of *the same arithmetic system* requires float32 vs
   float64 (both binary IEEE 754). This task uses both — decimal for
   Phase A (oracle), float32/float64 for Phase B (scaling).

**Surface:**

4. `import math` (math.sqrt, math.ulp) — Axiom 11 violation, replaced
   with `** 0.5` and a hand-rolled ULP helper.

5. Hardcoded output path `/home/workdir/artifacts/` — replaced with V4
   repo convention under `Build_Docs/Reports/`.

6. No V4 substrate integration — this task lives in `src/lloyd_v4/evals/`
   alongside the 024b fixture, following established convention.

7. Sample size mismatch (137 vs 50) — this task uses the same r-grid
   across all precisions for direct point-by-point comparison.

---

## 6. Primitive-Sufficiency Gate

| Concept | Source layer | Notes |
|---|---|---|
| Square-root | language operator `** 0.5` | Available at all precisions tested. |
| ULP helper | hand-rolled via `struct` | V4 convention; no `math.ulp`. |
| Decimal arithmetic | `decimal.Decimal` (stdlib) | Substrate-precision arithmetic, no named content. |
| Float32 / Float64 | `numpy.float32` / `numpy.float64` | Type containers, not math. |
| Four-form battery | existing 024b fixture | Re-used; not duplicated. |

No new substrate concepts are introduced.

---

## 7. Module Layout

### 7.1 New module: `src/lloyd_v4/evals/multi_precision_four_form.py`

Provides three pathways for the four-form battery plus utilities:

```python
def four_form_float32(r: float) -> Dict[str, float]:
    """Evaluate F1, F2, F3, F4 at numpy.float32 precision.
    Inputs are explicitly cast to float32; all arithmetic happens in float32.
    Returns the four values as Python floats (cast back from float32 for
    JSON serialisation)."""

def four_form_float64(r: float) -> Dict[str, float]:
    """Evaluate F1, F2, F3, F4 at numpy.float64 precision.
    Equivalent to native Python float arithmetic on most platforms.
    Re-uses the existing Task 024b fixture for cross-check determinism."""

def four_form_decimal_oracle(r: float, precision: int = 50) -> Dict[str, float]:
    """Evaluate F1, F2, F3, F4 using decimal.Decimal at the requested
    precision. Inputs are converted to Decimal from the EXACT double-
    precision representation of r (so the chain operates on the same
    initial bit pattern V4 uses, but with subsequent ops in decimal).
    Returns the four values as Python floats."""

def ulp_of_double(x: float) -> float:
    """Hand-rolled ULP computation via struct.pack/unpack.
    No math.ulp dependency."""

def predicted_chain_envelope(r: float, n_ops: int = 7) -> float:
    """First-order prediction of the F4 chain envelope:
        envelope = n_ops * 0.5 * ulp(F4_observed)
    n_ops is the count of correctly-rounded operations in the F4 chain
    (typically 7 for: 2/r, 1-(2/r), sqrt, r-2, (r-2)/r, sqrt, subtraction)."""
```

### 7.2 New module: `src/lloyd_v4/evals/multi_precision_campaign.py`

Campaign driver. Runs the three phases:

- **Phase A:** For each r in the V3 sweep (137 points), compute F_k at
  float64 and at decimal-50. Compute residual = F_k_float64 − F_k_decimal.
  Compute the predicted envelope per point. Record: residuals, envelopes,
  agreement (residual / envelope per point).

- **Phase B:** For each r in the V3 sweep, compute F_k at float32 and
  float64. Record F₄ magnitudes at each precision. Compute the ratio
  F4_float32 / F4_float64 across points where both are non-zero. Compare
  to expected ratio eps_32 / eps_64.

- **Phase C:** For each r in the V3 sweep, confirm F₃ is exactly zero at
  float32, float64, and decimal-50. Any non-zero F₃ at any precision is
  recorded explicitly with the precision and r at which it occurred.

Output to:
`Build_Docs/Reports/task017b_multi_precision_instrument_model/campaign_output.json`

The output JSON must be deterministic: sort all object keys, no
timestamps, no random ids.

### 7.3 Output directory

`Build_Docs/Reports/task017b_multi_precision_instrument_model/`
- `campaign_output.json` — campaign output
- `README.md` — short description and reproduction instructions

Plus top-level `Build_Docs/Reports/task017b_summary.md` — completion
report (alongside `task024b_summary.md` per existing convention).

---

## 8. Required Tests

`tests/test_task017b_multi_precision_instrument_model.py`:

### 8.1 Module symbol availability

All public symbols of the multi-precision module are importable and
callable.

### 8.2 Float32 vs float64 produces different F4 magnitudes

For at least 10 r values in the sweep, `abs(F4_float32(r)) >
abs(F4_float64(r))` strictly. This confirms the two pathways are using
different precisions and that float32 has larger roundoff residuals as
expected.

### 8.3 Decimal oracle agrees with float64 within envelope

Phase A test: for every r in the sweep where F₄_float64 is non-zero,
`abs(F4_float64(r) - F4_decimal_50(r)) <= 10 * ulp(F4_float64(r))`. The
factor of 10 is conservative; the chain has ~7 correctly-rounded ops so
the worst-case envelope is ~3.5 ULPs. We allow 10x for second-order
effects and decimal-to-binary conversion overhead. If this test fails, it
means the oracle does not agree with the doubles, which would indicate
either a chain enumeration error or a deeper instrument inconsistency.

### 8.4 F3 is exactly zero at all precisions (calibration zero)

For every r in the sweep:
- `four_form_float32(r)['F3'] == 0.0`
- `four_form_float64(r)['F3'] == 0.0`
- `four_form_decimal_oracle(r, 50)['F3'] == 0.0`

Any failure here invalidates the calibration-zero claim and should be
reported with the specific r value.

### 8.5 Scaling ratio test (Phase B)

For r values where both float32 and float64 produce non-zero F₄, compute
the median of `abs(F4_float32 / F4_float64)`. The expected ratio is
`eps_32 / eps_64 = (2^-23) / (2^-52) = 2^29 ≈ 5.37e8`. The test asserts
the observed median ratio is within a factor of 5 of the expected ratio
(i.e., `0.2 * expected <= observed <= 5.0 * expected`).

The wide tolerance reflects that this is a *scaling* test, not a
precision test — the goal is to confirm order-of-magnitude scaling, not
exact agreement. A 5x tolerance still rules out the null hypothesis
(precision has no effect on F4 magnitude).

### 8.6 Determinism

Run the campaign twice in-test, assert the two output JSONs are equal
byte-for-byte after key sorting.

### 8.7 Source purity

The new modules do not import `math`, `scipy`, `sympy`, `mpmath`,
`numpy.linalg`, `numpy.sqrt`, or `lloyd_v3`. Decimal is admitted only in
the oracle pathway (assert decimal usage is confined to the oracle
function).

### 8.8 Manifest non-regression

The campaign adds no new exports to `lloyd_v4`. Assert
`len(lloyd_v4.primitives.__all__)` is unchanged from the post-024b
baseline.

---

## 9. Required Commands

Run from `~/projects/V4/Lloyd_Engine_V4` with `.venv` activated.

```bash
# Pre-task baseline
git status                                            # clean tree
python -m pytest -q tests/ 2>&1 | tail -3             # 423 passing

# Implementation
# ... fixture module, campaign module, test file, report directory ...

# Verification
python -m pytest -q tests/test_task017b_multi_precision_instrument_model.py
python -m pytest -q tests/                            # full suite still green
python -m pytest -q tests/test_task001_source_purity.py

# Run the campaign
PYTHONPATH=src python -m lloyd_v4.evals.multi_precision_campaign

# Determinism verification
PYTHONPATH=src python -m lloyd_v4.evals.multi_precision_campaign \
    --output /tmp/multi_precision_repeat.json
diff Build_Docs/Reports/task017b_multi_precision_instrument_model/campaign_output.json \
     /tmp/multi_precision_repeat.json

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
git commit -m "Task 017b: Multi-precision confirmation of IEEE 754 instrument model"
git push origin main
```

The final commit and push are non-negotiable.

---

## 10. Non-Goals

- **No new primitives, no new status families, no new manifest entries.**
- **No SR or Bell fixtures** (those are 024c, 024d candidates).
- **No imported math content beyond `decimal` and `numpy` type containers.**
  No `math.sqrt`, no `math.ulp`, no `numpy.sqrt`, no `scipy`, no `mpmath`.
- **No hardcoded "model confirmed" assertions.** The test outcomes
  determine confirmation. If the data fails any of the three phase tests,
  the report says so plainly.
- **No claim that decimal-N is "higher precision IEEE 754."** Decimal is
  decimal arithmetic; the test is honest about this distinction.
- **No retry-tuning of tolerances to force a pass.** The 10x envelope
  factor in §8.3 and the 5x scaling tolerance in §8.5 are declared up
  front. If the data falls outside them, that is the finding.
- **No deconvolution primitive.** That is a downstream task (L2/L3 in the
  instrument reframe roadmap). 017b only tests the instrument model;
  it does not modify any V4 primitive.

---

## 11. Completion Report Template

`Build_Docs/Reports/task017b_summary.md` must contain:

### Scope

One paragraph describing the three phases and what each tested.

### Test count

Pre-task baseline (post-024b): 423 tests passing.
Post-Task 017b: 423 + N tests passing.

### Files changed

Bulleted list of every file created, modified, or moved.

### Phase A — Instrument self-consistency

For each form (F1, F2, F3, F4) and the float64 vs decimal-50 comparison:

- Count of points where float64 was non-zero
- Median residual = |F_float64 − F_decimal_50|
- Median predicted envelope at those points
- Median ratio residual / envelope (target: ≤ 1, allowed up to 10x)
- Number of points where residual exceeded envelope
- Pass / fail per form

### Phase B — Multi-precision scaling

- Count of points where both float32 and float64 produced non-zero F4
- Median ratio F4_float32 / F4_float64
- Expected ratio eps_32 / eps_64
- Observed / expected (target: 0.2 ≤ ratio ≤ 5.0)
- Pass / fail

### Phase C — Calibration zero

- F3 at float32, float64, decimal-50 across all r values
- Any non-zero F3 at any precision: list with r and precision
- Pass (all zero) / fail (any non-zero)

### Honest observations

Anything that didn't match the design-time prediction. Specifically:

- If Phase A residuals exceed envelope for any form, document which and
  by how much. Propose an explanation (chain enumeration error?
  second-order effect?).
- If Phase B scaling is outside 0.2–5.0 of expected, document the
  observed ratio and propose an explanation.
- If Phase C is ever non-zero, that is a major finding and must be
  documented prominently — the calibration-zero claim is load-bearing.

### Limits

- This task only tests Schwarzschild four-form. SR and Bell remain
  untested at multi-precision (future 017c, 017d if motivated).
- Decimal is the oracle for Phase A. Decimal arithmetic is *not* IEEE 754
  at higher precision; it is a different arithmetic system used as a
  ground-truth reference. The Phase A claim is: "doubles agree with
  decimal within the predicted envelope" — not "decimal is the
  higher-precision IEEE 754."
- Phase B uses float32 vs float64; this is the only real multi-precision
  IEEE 754 comparison available in pure Python without platform-specific
  long-double support.

### Audits

- pytest counts, source purity, manifest non-regression, determinism diff
- git commit hash, git push confirmation

---

## 12. Acceptance Criteria

1. Pre-task baseline confirmed (423 tests green).
2. New fixture and campaign modules exist at the agreed paths.
3. `tests/test_task017b_multi_precision_instrument_model.py` exists and
   all tests in it pass.
4. The full test suite passes with no regressions.
5. The campaign script runs cleanly and produces a deterministic
   `campaign_output.json`.
6. The three phase tests (instrument self-consistency, multi-precision
   scaling, calibration zero) all pass within their declared tolerances.
7. The completion report `task017b_summary.md` is filled per the template.
8. All changes are committed and pushed to `origin/main`.

If any of the three phase tests fail, the task is still complete — but
the completion report must document the failure clearly and propose
follow-up tasks. Failed tests on real data are findings, not bugs.

---

## 13. Discipline Notes (Forward References)

### What this task does not depend on

This task does not introduce a deconvolution primitive. It does not
modify any existing V4 primitive. It does not add typed observation
fields. Those are downstream possibilities that would be informed by
017b's findings — but they are separate substrate-extension tasks (L2 or
L3 in the IEEE 754 instrument reframe roadmap), not 017b.

### What 017b finding informs

If 017b confirms the instrument model (all three phases pass), the next
natural step is an `ieee754_chain_predictor` utility module that takes a
declared expression chain and computes its predicted IEEE 754 envelope.
That would be a Task 026 or similar. Do not draft that in 017b.

If 017b reveals a precision dependence we did not predict, the finding
itself is the deliverable and no follow-up task should be drafted until
the implication is understood.

### Why this task is 017b and not 025+

The "017" series was reserved for multi-precision execution work in the
original V4 roadmap. The "b" suffix marks it as the confirmation-test
variant of that work, distinct from a hypothetical 017a that would have
added multi-precision as substrate execution. 017b is testing only; it
does not commit V4 to multi-precision execution as a substrate feature.

---

*End of Codex Task 017b specification.*
