# Task 022 — Precision Floor Audit Tightening (Task 020 follow-up)

## Repository

`/mnt/fast/Lloyd_Engine_V4`

V3 is reference-only (Axiom 10). V1 / OG engine are also reference-only.
Layer 2+ artifacts (metrology, branch, refinery, history, solver) are
V3-shaped deferred-consumer first-drafts and MUST NOT shape this task.
This task is tests-only. No source code in `src/` is modified.

## Current Verified Baseline

- 372 tests passing (`pytest -x tests/`) as of Task 021 completion.
- Task 020 introduced a local helper
  `_allowed_task020_precision_floor_comment(rel: str, token: str) -> bool`
  in `tests/test_task001_source_purity.py`. The Task 020 summary states
  this allowance was added to source-purity tests
  `test_task001_source_purity.py` through `test_task009a_source_purity.py`
  (up to 10 files; Codex must inventory which actually contain it).
- The current allowance is shaped as:
  ```python
  def _allowed_task020_precision_floor_comment(rel: str, token: str) -> bool:
      return rel == "src/lloyd_v4/primitives/typed_finite_difference.py" and token in {
          "epsilon",
          "eps",
          "guard",
          "cas",
      }
  ```
- This allowance fires on **any** occurrence of those tokens in the
  precision-floor file. A hypothetical future addition like
  `def _eps_floor(): return 2.0**-52` in `typed_finite_difference.py`
  would silently pass the audit because the file is allowed and the
  token is allowed, regardless of where in the file the token appears.

## Task Goal

Tighten the Task 020 audit allowance so it fires only when the
allowance tokens appear inside **comment lines** (lines whose first
non-whitespace character is `#`). A non-comment use of any allowance
token in the same file must be caught by the audit.

Move the helper to `tests/_audit_helpers/` so it isn't duplicated across
the source-purity files. Add a small regression test suite that proves
the tightened audit catches synthetic non-comment uses.

This is tests-only infrastructure work. No source under `src/` is
modified. The actual precision-floor comment block in
`typed_finite_difference.py` uses `#`-style line comments throughout
(verified in Task 020), so the live audit will continue to pass under
the tightened allowance.

## Source Labelling

- **(V4-surface evidence)** Task 020 summary:
  > "older broad grep audits caught epsilon, eps, guard, and cas inside
  > the mandated comment text. The allowance is limited to
  > src/lloyd_v4/primitives/typed_finite_difference.py."
- **(Architectural follow-up)** Task 020 review flag:
  > "scoped to one file and four tokens — better than a blanket file
  > pass, but looser than ideal. If someone later adds a real
  > `_guard()` or `_eps_floor()` to that file (not just in a comment),
  > this audit would let it through. The third audit in the same file
  > (`test_precision_floor_occurrences_are_declared_observability_evidence`)
  > uses the tighter pattern: `(rel, token)` tuple membership against
  > an explicit `allowed` set. That's the shape the first two audits
  > should eventually use as well."
- **(Cleanliness)** The helper is duplicated across multiple
  source-purity files. Shared location in `tests/_audit_helpers/` is
  the cleaner pattern; the directory already exists for shared test
  helpers (Task 019 references
  `from _audit_helpers.lineage import ...`).
- **(Cadence)** Task 020 → Task 022 establishes the pattern: when an
  audit allowance is needed to land substantive work, the allowance
  can be permitted; a follow-up ticket tightens the allowance to its
  minimum necessary form. Codify this in discipline notes for future
  reference.

## Design Principles

- **Allowance is for documentation, not implementation.** Tokens like
  `eps`, `guard`, `epsilon`, and `cas` (as a substring match) appear
  legitimately inside the precision-floor reconciliation comment block
  because that comment *documents* the worst-case-2u derivation and
  the Axiom 3 "no hidden guard rails" reference. Any non-comment use
  of these tokens in the same file would be substantive code, not
  documentation, and must be caught.

- **Comment-line check is by line parsing.** A line is a comment line
  iff `line.lstrip().startswith("#")`. Simple, robust, easy to read.
  No regex required. The check operates on the full file text by
  iterating over `text.splitlines()`.

- **Docstrings are not comments.** A triple-quoted docstring is
  runtime executable code that creates a string object; it is not a
  comment. The current precision-floor comment uses `#`-style line
  comments (verified Task 020), so this distinction is moot in
  practice. The discipline matters for future drift: if someone
  changes the comment to a docstring, the audit will correctly catch
  the change rather than silently permit it.

- **Allowance token set is preserved verbatim.** `{"epsilon", "eps",
  "guard", "cas"}` stays as the allowance set. The tightening is about
  *scope* (must appear in comment line), not *membership*. Changing
  the allowance set is a different decision that requires its own
  justification.

- **Shared helper location.** Put it in
  `tests/_audit_helpers/precision_floor_allowance.py`. Source-purity
  tests import from there. No duplication.

- **Regression tests prove the tightening works.** Construct synthetic
  text in memory (never written to disk) and verify the helper
  correctly distinguishes comment-line uses from non-comment uses.

## Primitive-Sufficiency Gate

| Concept used | Provided by | Location |
|---|---|---|
| `tests/_audit_helpers/` directory and pattern | tests | existing; Task 019 references `_audit_helpers.lineage` |
| `pathlib.Path`, `str.splitlines()`, `str.lstrip()`, `str.startswith()` | Python stdlib | builtin |

Sufficiency gate **passes**. Tests-only infrastructure. No primitives,
protocols, status families, or substrate concepts touched.

## Required Deliverables

### 1. New shared helper `tests/_audit_helpers/precision_floor_allowance.py`

```python
"""Audit allowance helper for the Task 020 precision-floor
reconciliation comment in
`src/lloyd_v4/primitives/typed_finite_difference.py`.

The substrings 'epsilon', 'eps', 'guard', and 'cas' appear legitimately
inside the documented derivation block of `_precision_floor` (the
worst-case-2u cancellation threshold; see METROLOGY_PRINCIPLES.md and
the Task 020 summary). Source-purity audits that scan for those
substrings as forbidden tokens must use this helper to allow
comment-line occurrences while still catching any non-comment code
that would actually use the forbidden patterns.

The allowance applies only when:
  - the file path is the precision-floor file, AND
  - the token is one of the four allowance tokens, AND
  - every occurrence of the token in the file text is inside a comment
    line (line whose first non-whitespace character is `#`).
"""

PRECISION_FLOOR_FILE = "src/lloyd_v4/primitives/typed_finite_difference.py"
PRECISION_FLOOR_COMMENT_TOKENS = frozenset({"epsilon", "eps", "guard", "cas"})


def is_allowed_precision_floor_comment_token(rel: str, text: str, token: str) -> bool:
    """Return True iff every occurrence of `token` in `text` is inside
    a comment line of the precision-floor file.

    A line is a comment line iff its first non-whitespace character is `#`.

    Returns False if:
      - `rel` is not the precision-floor file path,
      - `token` is not in the allowance set, OR
      - any occurrence of `token` in `text` appears in a non-comment line.
    """
    if rel != PRECISION_FLOOR_FILE:
        return False
    if token not in PRECISION_FLOOR_COMMENT_TOKENS:
        return False
    for line in text.splitlines():
        if token in line:
            stripped = line.lstrip()
            if not stripped.startswith("#"):
                return False
    return True
```

Ensure `tests/_audit_helpers/__init__.py` exists (create if missing).

### 2. Update all source-purity test files that use the old helper

For each file matching `tests/test_task*_source_purity.py`:

- Check whether the file contains
  `_allowed_task020_precision_floor_comment`.
- If yes:
  - Add the import near the top:
    ```python
    from _audit_helpers.precision_floor_allowance import (
        is_allowed_precision_floor_comment_token,
    )
    ```
  - Update each call site:
    ```python
    # Before:
    if token in text and not _allowed_task020_precision_floor_comment(rel, token):
        offenders.append(f"{rel}:{token}")

    # After:
    if token in text and not is_allowed_precision_floor_comment_token(rel, text, token):
        offenders.append(f"{rel}:{token}")
    ```
  - Remove the local helper definition.
- If no: leave the file alone.

Codex: inventory which files actually contain the old helper before
making changes, and report the inventory in the completion report.

After updates, verify by grep:

```bash
rg "_allowed_task020_precision_floor_comment" tests -n
```

This must return zero matches.

### 3. New test file `tests/test_task022_audit_tightening.py`

```python
"""Task 022: Regression tests for the tightened precision-floor
allowance.

Verifies that:
- Comment-line uses of allowance tokens are permitted.
- Non-comment uses of allowance tokens are caught, even when a
  legitimate comment-line use is also present.
- Tokens not in the allowance set are never permitted.
- Files other than the precision-floor file are never permitted.
- Indented comments (inside functions, inside conditional blocks) are
  still recognized as comments.
- A synthetic file with a real precision-floor comment AND a
  non-comment use of the same token is correctly flagged.
"""

from _audit_helpers.precision_floor_allowance import (
    PRECISION_FLOOR_COMMENT_TOKENS,
    PRECISION_FLOOR_FILE,
    is_allowed_precision_floor_comment_token,
)


class TestPrecisionFloorAllowance:
    """Lock the tightened allowance behavior."""

    def test_comment_line_eps_is_allowed(self):
        """A token in a `#`-style comment line is permitted."""
        text = "# eps is documented here\nreturn 2.0**-52\n"
        assert is_allowed_precision_floor_comment_token(
            PRECISION_FLOOR_FILE, text, "eps"
        )

    def test_non_comment_eps_alongside_comment_is_not_allowed(self):
        """A token appearing in both a comment line and a non-comment
        line is NOT permitted. The non-comment occurrence is the
        deciding case."""
        text = "# eps in comment\n_eps_floor = 2.0**-52  # but here eps is used in code\n"
        assert not is_allowed_precision_floor_comment_token(
            PRECISION_FLOOR_FILE, text, "eps"
        )

    def test_only_non_comment_eps_is_not_allowed(self):
        """A token appearing only in non-comment lines is NOT permitted."""
        text = "x = 1\n_eps = 2.0**-52\n"
        assert not is_allowed_precision_floor_comment_token(
            PRECISION_FLOOR_FILE, text, "eps"
        )

    def test_other_file_not_allowed(self):
        """The allowance is scoped to the precision-floor file only."""
        text = "# eps in comment\n"
        assert not is_allowed_precision_floor_comment_token(
            "src/lloyd_v4/primitives/directional_alpha_probe.py", text, "eps"
        )
        assert not is_allowed_precision_floor_comment_token(
            "src/lloyd_v4/some_other_file.py", text, "eps"
        )

    def test_unlisted_token_not_allowed(self):
        """Only the four allowance tokens are eligible. Other forbidden
        tokens are never permitted regardless of where they appear."""
        text = "# clamp_min in a comment\n"
        assert not is_allowed_precision_floor_comment_token(
            PRECISION_FLOOR_FILE, text, "clamp_min"
        )
        assert not is_allowed_precision_floor_comment_token(
            PRECISION_FLOOR_FILE, text, "safe_mask"
        )
        assert not is_allowed_precision_floor_comment_token(
            PRECISION_FLOOR_FILE, text, "rescue"
        )

    def test_indented_comment_still_allowed(self):
        """Comments inside function bodies or conditional blocks (which
        are indented) still count as comments."""
        text = (
            "def f():\n"
            "    if True:\n"
            "        # eps inside indented comment\n"
            "        return 1\n"
        )
        assert is_allowed_precision_floor_comment_token(
            PRECISION_FLOOR_FILE, text, "eps"
        )

    def test_audit_would_catch_synthetic_non_comment_use(self):
        """Integration: construct a synthetic file with a real
        precision-floor-style comment AND a non-comment use of the same
        token. The audit must refuse the allowance."""
        synthetic_text = (
            "# Per-operand unit roundoff: u = 2^-53.\n"
            "# This comment legitimately references eps and guard.\n"
            "def _precision_floor(precision):\n"
            "    return 2.0**-52\n"
            "\n"
            "def _eps_floor():  # function name is non-comment use of 'eps'\n"
            "    return 2.0**-52\n"
        )
        # Even with a legitimate comment in the same file, the
        # non-comment use prevents the allowance.
        assert not is_allowed_precision_floor_comment_token(
            PRECISION_FLOOR_FILE, synthetic_text, "eps"
        )
        # And the audit logic itself (token-in-text + helper) would
        # correctly flag the file:
        token_present = "eps" in synthetic_text
        token_allowed = is_allowed_precision_floor_comment_token(
            PRECISION_FLOOR_FILE, synthetic_text, "eps"
        )
        would_be_offender = token_present and not token_allowed
        assert would_be_offender, (
            "synthetic non-comment use of 'eps' should have been flagged"
        )
```

### 4. Verify the live audit still passes after tightening

The actual `typed_finite_difference.py` file's tokens all appear in
`#`-style comment lines (the Task 020 comment block). The full
source-purity audit suite must continue to pass.

Codex: confirm by running the full source-purity test suite after the
helper migration. If any audit fails, that is evidence either that
(a) the live comment is not strictly `#`-style, or (b) a token appears
somewhere outside the comment block. Either is a finding worth
flagging in the completion report; STOP and report rather than
papering over.

## Required Commands

```bash
# Pre-task baseline
python -m pytest -x tests/ -q

# Inventory which source-purity files contain the old helper
rg "_allowed_task020_precision_floor_comment" tests -n

# Verify _audit_helpers directory and existing helpers
ls tests/_audit_helpers/

# After implementation: verify new helper exists and works
python -m pytest tests/test_task022_audit_tightening.py -v

# Source-purity audits should still pass under the tightened allowance
python -m pytest tests/test_task001_source_purity.py \
                 tests/test_task002_source_purity.py \
                 tests/test_task003_source_purity.py \
                 tests/test_task004_source_purity.py \
                 tests/test_task005_source_purity.py \
                 tests/test_task006_source_purity.py \
                 tests/test_task007_source_purity.py \
                 tests/test_task008_source_purity.py \
                 tests/test_task009_source_purity.py \
                 tests/test_task009a_source_purity.py -v

# Confirm no duplicated helper functions remain
rg "_allowed_task020_precision_floor_comment" tests -n
# Should return zero matches

# Confirm no source file in src/ was modified
git diff --stat src/

# Full suite
python -m pytest -x tests/ -q
```

Expected: full suite passes with 372 + 7 new tests = 379 passing.

## Non-Goals (loud and explicit)

- **Do NOT modify any file in `src/`.** This is tests-infrastructure
  only. The actual precision-floor comment in
  `typed_finite_difference.py` is unchanged.
- **Do NOT change the underlying audit logic** beyond replacing the
  local helper with the shared one. The forbidden token lists in
  `test_source_only_forbidden_concept_audit` and
  `test_no_hidden_denominator_correction_names_in_core_or_primitives`
  stay exactly as they are.
- **Do NOT add or remove tokens from the allowance set.** The set
  `{"epsilon", "eps", "guard", "cas"}` is preserved verbatim.
  Changing it is a different decision with its own justification.
- **Do NOT touch the third audit
  (`test_precision_floor_occurrences_are_declared_observability_evidence`).**
  Its allowance was already correctly tightened in Task 020 using the
  `(rel, token)` tuple pattern.
- **Do NOT touch any test file that doesn't contain the old helper.**
  Inventory first; touch only what needs touching.
- **Do NOT introduce dependencies on Layer 2+ modules** or import
  anything from `src/lloyd_v4/`. The helper is pure Python stdlib.
- **Do NOT add new audit categories or expand audit scope.** The
  tightening narrows what the existing allowance permits; it does
  not introduce new checks.

## Completion Report

Create `Build_Docs/Reports/task022_summary.md` with:

- **Scope summary** (one paragraph).
- **Test counts.** Expected: pre 372, post 379.
- **Files changed**, with one-line description per file. Expected:
  - `tests/_audit_helpers/precision_floor_allowance.py` (new)
  - `tests/_audit_helpers/__init__.py` (new if not present, otherwise
    unchanged)
  - Each `tests/test_task*_source_purity.py` that contained the old
    helper (list explicitly which ones; the Task 020 summary said
    "test_task001 through test_task009a" but Codex's actual inventory
    should be reported)
  - `tests/test_task022_audit_tightening.py` (new)
  - `Build_Docs/Reports/task022_summary.md` (new)
- **Inventory** of source-purity files that contained the old helper,
  before update.
- **Excerpt** of the new shared helper.
- **Confirmation** that the synthetic-violation regression test
  catches a hypothetical non-comment use.
- **Confirmation** that `rg "_allowed_task020_precision_floor_comment"
  tests -n` returns zero matches.
- **Confirmation** that `git diff --stat src/` returns no changes.
- **Source-purity audit result** (all 10 pass under tightened
  allowance).

## Acceptance Criteria

- `tests/_audit_helpers/precision_floor_allowance.py` exists and
  exports `is_allowed_precision_floor_comment_token`,
  `PRECISION_FLOOR_FILE`, `PRECISION_FLOOR_COMMENT_TOKENS`.
- Every source-purity test file that contained the old local helper
  now imports the shared helper instead. The old local helper
  definitions are removed.
- `rg "_allowed_task020_precision_floor_comment" tests -n` returns
  zero matches.
- Seven regression tests in `tests/test_task022_audit_tightening.py`
  pass.
- All source-purity audits still pass (the live comment in
  `typed_finite_difference.py` legitimately uses these tokens in
  comment lines only).
- Full suite passes (expected 379).
- `git diff --stat src/` shows no changes to any file under `src/`.
- No new forbidden tokens added to any audit; no existing tokens
  removed.

## Discipline Notes

- **The tightening is precautionary.** No actual non-comment use of
  the allowance tokens exists in `typed_finite_difference.py` today.
  The tightening protects against future drift, not a current
  violation.

- **The cadence is the pattern.** When a substantive task needs an
  audit allowance to land, the allowance can be permitted in the
  same task; a follow-up ticket tightens the allowance to its
  minimum necessary form. Task 020 → Task 022 is the first
  instance of this cadence. Codify it: every audit allowance has a
  follow-up ticket to tighten. Future tasks introducing allowances
  should explicitly schedule the tightening as part of the same
  cleanup cadence.

- **The four-token allowance set is itself a cleanup candidate
  but not for this task.** `"cas"` was added because at least one
  audit's substring match catches it inside the comment; the
  specific audit and forbidden pattern that match it should be
  identified in a future cleanup if anyone wants to remove `"cas"`
  from the allowance set. Out of scope here.

- **Forward reference (Task 023 — iterated logarithm discovery
  campaign).** Task 023 will add test code and possibly
  substrate-extension code. Starting from a tight audit baseline
  ensures any new allowances Task 023 might need stand out
  cleanly rather than getting absorbed into existing looseness.

- **Forward reference (Task 024 — joint composer).** Same reasoning
  — clean audit baseline before substantial new substrate work.

- **Layer 2+ remains reference-only.** Tests-only task; no
  consultation needed.
