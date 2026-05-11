# Task 020 — Precision Floor Reconciliation in typed_finite_difference

## Repository

`/mnt/fast/Lloyd_Engine_V4`

V3 is reference-only (Axiom 10). V1 / OG engine are also reference-only.
Layer 2+ artifacts (metrology, branch, refinery, history, solver) are
V3-shaped deferred-consumer first-drafts and MUST NOT shape this task.
This is a documentation reconciliation and discipline lock-in for a
Layer 1 primitive. No new statuses, no new value types, no new protocols,
no new computation paths.

## Current Verified Baseline

- 344 tests passing (`pytest -x tests/`) as of Task 019 completion.
- `typed_finite_difference` (Task 015) has `_precision_floor("raw_python")`
  returning `2.0**-52`.
- `Build_Docs/Architecture/METROLOGY_PRINCIPLES.md` currently describes this
  floor as the "unit roundoff for the declared precision."
- These two statements disagree by a factor of 2: the unit roundoff of a
  single IEEE 754 double operand under round-to-nearest is `u = 2^-53`,
  not `2^-52`.
- The precision-floor audit pattern landed in Task 018:
  `tests/test_task001_source_purity.py` confines `2.0**-52` and related
  patterns to allowed locations.
- The inconsistency was documented honestly during Task 018 and
  intentionally left unresolved at that time.

## Task Goal

Reconcile the documented contract for `_precision_floor` with its
implementation. The current value `2.0**-52` is correct under worst-case
round-off analysis of forward-difference subtraction (it is `2u`, the
worst-case relative cancellation envelope). The documentation's term
"unit roundoff" is imprecise — the unit roundoff `u` is per-operand and
equals `2^-53`. The fix is documentation-shaped, not behaviour-shaped.

**This task does NOT change the numerical value of the floor.** No existing
classification flips. No α-recovery fixtures re-baseline. No downstream
primitive (`directional_alpha_probe`, `scalar_alpha_jet_bundle`) is touched.

The task converts an incidental-feeling value into an explicitly-derived
one, with rationale recorded in METROLOGY_PRINCIPLES, a citation comment
in source, and a regression test that locks the choice. If a future task
wants to revisit the floor, the locked-in test forces explicit acknowledgment.

## Source Labelling

- **(V4-surface evidence)** Session handoff:
  > "eps vs eps/2 inconsistency in `typed_finite_difference`'s raw_python
  > precision floor. Documented honestly, not resolved."

  This task resolves it.

- **(Numerical-analysis derivation, derived in V4 — not imported)** Forward
  finite difference `delta_g = g(f+delta_f) - g(f)` in IEEE 754 double under
  round-to-nearest:
  - Each evaluation of `g` carries relative round-off bounded by `u = 2^-53`
    (the unit roundoff for round-to-nearest).
  - Under worst-case independent operand errors, the absolute round-off in
    `delta_g` is bounded by approximately `2u * max(|g_f|, |g_f_plus|)`.
  - The relative cancellation ratio `|delta_g| / max(|g_f|, |g_f_plus|)` is
    therefore classifiable as round-off-dominated when it falls below
    `2u = 2^-52`, which also happens to equal `sys.float_info.epsilon`
    (the relative spacing of floats at 1.0).
  - The current code value `2.0**-52` is correct under this derivation;
    the documentation's "unit roundoff" naming was the source of the
    inconsistency.

- **(Architectural)** Path B (lowering the floor to `2.0**-53` to literally
  match the "unit roundoff" wording) was considered and rejected:
  - It would re-classify a measurable set of currently-OBSERVED transfers
    as `TRANSFER_CANCELLATION_DOMINATED`, propagating through
    `directional_alpha_probe` and `scalar_alpha_jet_bundle` and requiring
    re-baselining of α-recovery fixtures.
  - `2u` is the correct worst-case threshold for the *subtraction*
    `g(f+delta_f) - g(f)`. The per-operand `u` would be the right floor
    only if comparing the magnitude of a single operand against round-off,
    which is not what cancellation classification does.
  - The doc fix is cheaper, more accurate, and changes no behaviour.

## Design Principles

- **No numerical change.** `_precision_floor("raw_python")` continues to
  return `2.0**-52`. Existing tests, α-recovery fixtures, and AlphaProbe
  / ScalarAlphaJetBundle classifications are unaffected.
- **Documented derivation, not appeal to authority.** METROLOGY_PRINCIPLES.md
  gains a short derivation from operand round-off bounds. No external
  citation required; the derivation stands on its own.
- **Source comment is precise.** The `return 2.0**-52` line gets a comment
  citing the derivation in a few lines.
- **Locked-in test.** A regression test asserts the value is `2.0**-52`,
  asserts it equals `2 * 2.0**-53` (twice the unit roundoff), asserts it
  equals `sys.float_info.epsilon`, and asserts it is NOT `2.0**-53` (the
  per-operand unit roundoff). If a future task wants to change the floor,
  that test forces explicit acknowledgment.
- **No new imports into source.** Axiom 11 still applies.
  `sys.float_info.epsilon` is allowed in tests as observational evidence
  about the runtime; it must not enter source.
- **Status-only invariant is reasserted.** A regression test confirms that
  `TRANSFER_CANCELLATION_DOMINATED` observations still carry the
  computed transfer value (not None, not clamped). The floor remains a
  classification threshold, never a value rescue.

## Primitive-Sufficiency Gate

| Concept used | Provided by | Location |
|---|---|---|
| `_precision_floor` (private function) | primitives | `typed_finite_difference.py` (comment only) |
| `typed_finite_difference` | primitives | `typed_finite_difference.py` (no change) |
| `TransferStatus` | core | `core/status.py` (no change) |
| `ProtocolViolationError` | core | `core/errors.py` (no change) |
| Runtime float characteristics for cross-reference | Python stdlib | `sys.float_info.epsilon` (tests only) |

Sufficiency gate **passes**. This is documentation, a source comment, and
a test. No new substrate.

## Required Deliverables

### 1. Source comment in `src/lloyd_v4/primitives/typed_finite_difference.py`

Update `_precision_floor` to include a derivation comment. The behavior
of the function is unchanged.

```python
def _precision_floor(precision: str) -> float:
    if precision == "raw_python":
        # raw_python uses IEEE 754 double under round-to-nearest.
        # Per-operand unit roundoff: u = 2^-53.
        # For forward finite difference delta_g = g(f+delta_f) - g(f),
        # worst-case absolute round-off in delta_g is approximately
        # 2u * max(|g_f|, |g_f_plus|). The relative cancellation ratio
        # |delta_g| / max(|g_f|, |g_f_plus|) is classifiable as
        # round-off-dominated when it falls below 2u = 2^-52, which also
        # equals sys.float_info.epsilon (relative spacing of floats at 1.0).
        # Status-only: this floor never alters the computed transfer value;
        # it only classifies the stratum. See METROLOGY_PRINCIPLES.md and
        # Axiom 3 (no hidden guard rails).
        return 2.0**-52
    raise ProtocolViolationError(
        f"unsupported precision {precision!r}; raw_python is the only currently-supported value"
    )
```

The exact wording of the comment is flexible; the *content* (per-operand
`u = 2^-53`, subtraction worst-case `2u = 2^-52`, equals
`sys.float_info.epsilon`, status-only) must be present.

No other lines in `typed_finite_difference.py` change.

### 2. Update `Build_Docs/Architecture/METROLOGY_PRINCIPLES.md`

Replace the section currently titled
`## precision_floor as finite-precision observability evidence` with the
following. The rest of the file (Finite-Precision Observation, Declared
Measurement Resolution, Precision and Path Attribution, Noise Floor and
Limit of Detection, Proxy Calibration, Finite-Window and Finite-Step Bias,
Direct Transfer Versus Proxy Observable) remains unchanged.

````markdown
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

V4 treats finite-precision observation as part of the computation. The
engine distinguishes mathematical structure from what the chosen
instrument can observe.
````

### 3. New test file `tests/test_task020_precision_floor_reconciliation.py`

```python
"""Task 020: Precision floor reconciliation regression tests.

Locks the precision_floor value and its derivation rationale. If a
future task wants to change the floor, this test forces explicit
acknowledgment that 2u (cancellation threshold of the subtraction) is
distinct from u (per-operand unit roundoff).
"""
import math
import sys

import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import TransferStatus
from lloyd_v4.primitives.typed_finite_difference import (
    _precision_floor,
    typed_finite_difference,
)


class TestPrecisionFloorReconciliation:
    """Lock the precision floor value and its derivation rationale."""

    def test_raw_python_precision_floor_is_two_u(self):
        """The floor is 2u (worst-case forward-difference cancellation
        threshold), NOT u (per-operand unit roundoff)."""
        u = 2.0**-53
        floor = _precision_floor("raw_python")
        assert floor == 2.0 * u
        assert floor == 2.0**-52

    def test_raw_python_precision_floor_equals_machine_epsilon(self):
        """2u for double also equals sys.float_info.epsilon (the relative
        spacing of floats at 1.0). This is an observational fact about
        the runtime, asserted here for cross-reference clarity."""
        assert _precision_floor("raw_python") == sys.float_info.epsilon

    def test_raw_python_precision_floor_is_not_unit_roundoff(self):
        """Discipline test: the floor must NOT be 2^-53 (the per-operand
        unit roundoff). If this changes, the derivation in
        METROLOGY_PRINCIPLES.md must change with it, and the source
        comment in _precision_floor must be updated."""
        unit_roundoff = 2.0**-53
        floor = _precision_floor("raw_python")
        assert floor != unit_roundoff
        assert floor == 2.0 * unit_roundoff

    def test_unsupported_precision_raises(self):
        """No silent fallback for unsupported precisions."""
        with pytest.raises(ProtocolViolationError):
            _precision_floor("float32")
        with pytest.raises(ProtocolViolationError):
            _precision_floor("mpmath")
        with pytest.raises(ProtocolViolationError):
            _precision_floor("")

    def test_precision_floor_does_not_alter_observation_values(self):
        """Regression: precision_floor is status-only.

        A transfer that classifies as TRANSFER_CANCELLATION_DOMINATED
        must still carry the computed transfer value, delta_g, and
        cancellation_ratio. The floor classifies but does not rescue
        or clamp."""
        # Near-constant callable: delta_g is tiny relative to g
        result = typed_finite_difference(
            lambda x: 1.0 + 1e-20 * x,
            1.0,
            1e-3,
            function_label="near_constant_for_floor_check",
        )
        assert result.status is TransferStatus.TRANSFER_CANCELLATION_DOMINATED

        # Computed values are preserved
        assert result.value.transfer is not None
        assert math.isfinite(result.value.transfer)
        assert result.value.delta_g is not None
        assert math.isfinite(result.value.delta_g)
        assert result.value.g_at_f is not None
        assert result.value.g_at_f_plus_delta is not None

        # The cancellation_ratio is below the floor — that is why we
        # reached this stratum
        assert result.value.cancellation_ratio is not None
        assert result.value.cancellation_ratio < _precision_floor("raw_python")

        # Validity reflects status, not rescue
        assert result.validity.selectable is False
        assert result.validity.advanceable is False
        assert result.validity.observable is True
```

### 4. Source-purity audit verification (no change expected)

`tests/test_task001_source_purity.py` already confines `precision_floor`
and `2.0**-52` patterns to allowed locations. After this task:

- `typed_finite_difference.py` will have an additional comment block
  containing the literal `2^-53` and `2^-52` in human-readable text. If
  the existing audit's regex catches the `2^-53` reference and the audit
  framework treats `typed_finite_difference.py` as an allowed location
  (which it does, per Task 018's confinement), no audit update is needed.
- If the audit DOES flag the new comment as a source-side match outside
  allowed locations, narrow the audit accordingly — but verify the
  existing confinement first.

Codex: do not modify the audit unless it actually fails. If it passes
unchanged, leave it.

## Required Tests

### Pre-task evidence

```python
def test_task020_marker_not_yet_complete() -> None:
    """Pre-task evidence; remove during implementation."""
    pass
```

Add this to the new test file, then remove before completion.

### Locked-in regression tests

See Deliverable 3 above. Five tests:

1. `test_raw_python_precision_floor_is_two_u`
2. `test_raw_python_precision_floor_equals_machine_epsilon`
3. `test_raw_python_precision_floor_is_not_unit_roundoff`
4. `test_unsupported_precision_raises`
5. `test_precision_floor_does_not_alter_observation_values`

### Discipline tests

The five locked-in tests in Deliverable 3 ARE the discipline tests. They
lock:

- the numerical value
- its relation to `sys.float_info.epsilon`
- its non-equality with the per-operand unit roundoff
- the status-only behavior (computed value is preserved, not rescued)
- the no-silent-fallback behavior for unsupported precisions

### Serialization

No new serializable types. Existing `TransferObservation` serialization
is unaffected and not re-tested here.

### Protocol validation

No new protocols. `TYPED_FINITE_DIFFERENCE_PROTOCOL` and
`TRANSFER_OBSERVATION_CONSUMER_PROTOCOL` are unaffected and not re-tested
here.

## Required Commands

```bash
# Pre-task baseline
python -m pytest -x tests/ -q

# Targeted test for this task
python -m pytest tests/test_task020_precision_floor_reconciliation.py -v

# Source-purity audit must still pass
python -m pytest tests/test_task001_source_purity.py -v

# Full suite after implementation
python -m pytest -x tests/ -q

# Confirm precision_floor pattern audit produces no surprises
rg "precision_floor|roundoff_floor|unit_roundoff|machine_epsilon|cancellation_ratio|2\\.0\\s*\\*\\*\\s*-52|2\\.0\\s*\\*\\*\\s*-53|sys\\.float_info\\.epsilon|np\\.finfo" src tests Build_Docs -n
```

Expected source-side matches after this task:

- `src/lloyd_v4/primitives/typed_finite_difference.py`: the existing
  `return 2.0**-52` line plus the new comment (which may reference
  `2^-53` and `2^-52` in prose).

Expected test-side matches:

- `tests/test_task020_precision_floor_reconciliation.py`: explicit
  references to `2.0**-52`, `2.0**-53`, and `sys.float_info.epsilon`.
- `tests/test_task001_source_purity.py`: unchanged audit pattern.

Expected docs-side matches:

- `Build_Docs/Architecture/METROLOGY_PRINCIPLES.md`: the new derivation
  paragraph references `2^-53`, `2u`, `2^-52`, and
  `sys.float_info.epsilon` in prose.

No matches should appear in any other location.

## Non-Goals (loud and explicit)

- **Do NOT change the numerical value of `_precision_floor("raw_python")`.**
  It stays at `2.0**-52`.
- **Do NOT introduce a new precision mode.** No `"float32"`, no `"mpmath"`,
  no `"high_precision"`. The unsupported-precision branch keeps raising
  `ProtocolViolationError`.
- **Do NOT alter `typed_finite_difference`'s computation path.** No new
  branches, no new statuses, no new fields on `TransferObservation`. Only
  the comment is added.
- **Do NOT change `directional_alpha_probe`, `scalar_alpha_jet_bundle`, or
  any other primitive.** They inherit the floor unchanged.
- **Do NOT touch Layer 2+ modules** (metrology, branch, refinery, history,
  solver). They remain reference-only.
- **Do NOT introduce `sys.float_info.epsilon` into source.** Tests only.
- **Do NOT add a separate "unit roundoff" named constant.** If future
  precision modes need it, they introduce it then.
- **Do NOT re-baseline any existing α-recovery test.** If any existing
  test re-classifies as a result of this change, STOP — that is evidence
  the rest of the system was implicitly depending on the inconsistency,
  which would be a discovery worth flagging rather than papering over.

## Completion Report

Create `Build_Docs/Reports/task020_summary.md` with:

- **Scope summary** (one paragraph).
- **Test counts.** Expected: pre 344, post 349 (five new tests, no removals).
  If different, explain.
- **Files changed**, with one-line description per file. Expected:
  - `src/lloyd_v4/primitives/typed_finite_difference.py` (comment only)
  - `Build_Docs/Architecture/METROLOGY_PRINCIPLES.md` (first section replaced)
  - `tests/test_task020_precision_floor_reconciliation.py` (new)
  - `Build_Docs/Reports/task020_summary.md` (new)
- **Excerpt** of the new derivation paragraph in METROLOGY_PRINCIPLES.md.
- **Excerpt** of the source comment in `_precision_floor`.
- **Locked-in test assertions** quoted (the five `assert` statements that
  carry the discipline content).
- **Confirmation** that no existing observation re-classifies (the full
  suite remaining green is sufficient evidence; flag any test that needed
  modification).
- **Source-purity audit result** (pass / fail / required adjustment).

## Acceptance Criteria

- `_precision_floor("raw_python")` returns `2.0**-52` (unchanged value).
- Source comment in `_precision_floor` cites the derivation (per-operand
  `u = 2^-53`, subtraction worst-case `2u = 2^-52`, equals
  `sys.float_info.epsilon`, status-only).
- METROLOGY_PRINCIPLES.md no longer describes the floor as "unit roundoff";
  uses the worst-case-subtraction derivation instead.
- All five locked-in tests pass.
- Full suite passes (344 + 5 new = 349 passing).
- Source-purity audit produces no unexpected matches; only the documented
  expected matches per Required Commands.
- No existing test required modification. If any did, flag prominently in
  the summary as a discovery requiring follow-up.

## Discipline Notes

- **The fix is documentation-shaped, not behaviour-shaped.** This is the
  cleanest version of a substrate decision: name the right thing, lock
  the choice with a test, move on.
- **Path B (changing the floor to `2.0**-53`) was deliberately rejected.**
  The derivation in METROLOGY_PRINCIPLES.md now makes the rejected path
  inconsistent rather than just unchosen. If a future task wants Path B,
  the documented derivation has to be revisited, not just the line.
- **Forward reference (`SingularAlphaJetBundle`, candidate next L1 task).**
  That primitive will reuse `typed_finite_difference` through
  `directional_alpha_probe`, so it inherits the floor unchanged. No
  coordination needed beyond confirming this task lands cleanly first.
  The next task should be specified separately after this lands.
- **Sibling reference (multi-precision execution, banked as Task 017b
  conditional).** Introducing new precision modes will introduce new
  floors. Each new mode must derive its own floor from operand round-off
  bounds in the same shape this task documents for `raw_python`. The
  pattern is: name the per-operand unit roundoff `u`, derive the
  subtraction cancellation floor `2u`, document the derivation, lock with
  a test.
- **No Layer 2+ V3-shape consultation required.** Metrology, branch,
  refinery, history, and solver modules MUST NOT be cited as evidence for
  any choice in this task. The derivation stands on Layer 0/1 substrate
  and operand-error analysis alone.
