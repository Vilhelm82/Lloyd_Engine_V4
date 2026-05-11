# Task 022 Summary - Precision Floor Audit Tightening

## Scope

Task 022 tightened the Task 020 source-purity allowance so the four precision-floor documentation tokens are allowed only when every occurrence in `typed_finite_difference.py` appears on a `#` comment line. The duplicated local helpers were replaced by one shared test helper under `tests/_audit_helpers/`. No files under `src/` were modified.

## Test Counts

- Pre-task baseline: 372 tests passing.
- Added tests: 7 in `tests/test_task022_audit_tightening.py`.
- Post-task collection: 379 tests.
- Full suite: `379 passed in 3.93s`.

## Files Changed

- `tests/_audit_helpers/precision_floor_allowance.py`: new shared helper for the tightened comment-line allowance.
- `tests/test_task001_source_purity.py`: imports the shared helper and removes the local duplicate.
- `tests/test_task002_source_purity.py`: imports the shared helper and removes the local duplicate.
- `tests/test_task003_source_purity.py`: imports the shared helper and removes the local duplicate.
- `tests/test_task004_source_purity.py`: imports the shared helper and removes the local duplicate.
- `tests/test_task005_source_purity.py`: imports the shared helper and removes the local duplicate.
- `tests/test_task006_source_purity.py`: imports the shared helper and removes the local duplicate.
- `tests/test_task007_source_purity.py`: imports the shared helper and removes the local duplicate.
- `tests/test_task008_source_purity.py`: imports the shared helper and removes the local duplicate.
- `tests/test_task009_source_purity.py`: imports the shared helper and removes the local duplicate.
- `tests/test_task009a_source_purity.py`: imports the shared helper and removes the local duplicate.
- `tests/test_task022_audit_tightening.py`: new regression tests for comment-line-only allowance behavior.
- `Build_Docs/Reports/task022_summary.md`: this report.

`tests/_audit_helpers/__init__.py` already existed and was left unchanged.

## Inventory

Before update, the old local helper appeared in:

```text
tests/test_task001_source_purity.py
tests/test_task002_source_purity.py
tests/test_task003_source_purity.py
tests/test_task004_source_purity.py
tests/test_task005_source_purity.py
tests/test_task006_source_purity.py
tests/test_task007_source_purity.py
tests/test_task008_source_purity.py
tests/test_task009_source_purity.py
tests/test_task009a_source_purity.py
```

## Helper Excerpt

```python
PRECISION_FLOOR_FILE = "src/lloyd_v4/primitives/typed_finite_difference.py"
PRECISION_FLOOR_COMMENT_TOKENS = frozenset({"epsilon", "eps", "guard", "cas"})


def is_allowed_precision_floor_comment_token(rel: str, text: str, token: str) -> bool:
    if rel != PRECISION_FLOOR_FILE:
        return False
    if token not in PRECISION_FLOOR_COMMENT_TOKENS:
        return False
    for line in text.splitlines():
        if token in line and not line.lstrip().startswith("#"):
            return False
    return True
```

The regression test `test_audit_would_catch_synthetic_non_comment_use` confirms that a synthetic file with a valid precision-floor comment and a non-comment `_eps_floor` function is flagged as an offender.

## Verification

- Pre-task baseline:
  - `PYTHONPATH=src python -m pytest -x tests/ -q`
  - exited cleanly with the Task 021 baseline suite.
- New regression tests:
  - `PYTHONPATH=src python -m pytest tests/test_task022_audit_tightening.py -v`
  - `7 passed in 0.02s`
- Source-purity audits:
  - `PYTHONPATH=src python -m pytest tests/test_task001_source_purity.py tests/test_task002_source_purity.py tests/test_task003_source_purity.py tests/test_task004_source_purity.py tests/test_task005_source_purity.py tests/test_task006_source_purity.py tests/test_task007_source_purity.py tests/test_task008_source_purity.py tests/test_task009_source_purity.py tests/test_task009a_source_purity.py -v`
  - `27 passed in 0.21s`
- Old helper removal:
  - `rg "_allowed_task020_precision_floor_comment" tests -n`
  - returned zero matches.
- Task 022 helper did not leak into source:
  - `rg "precision_floor_allowance|is_allowed_precision_floor_comment_token|test_task022_audit_tightening" src -n`
  - returned zero matches.
- Full suite:
  - `PYTHONPATH=src python -m pytest -x tests/`
  - `379 passed in 3.93s`

## Source Tree Check

The requested `git diff --stat src/` command could not be used because `/mnt/fast/Lloyd_Engine_V4` is not a git repository:

```text
fatal: not a git repository (or any parent up to mount point /mnt)
```

I also checked for `.git` under `/mnt/fast/Lloyd_Engine_V4` and found none. The task edits were confined to `tests/` and `Build_Docs/Reports/`; no `src/` files were patched.

## Boundary Notes

- No source under `src/` was modified.
- No forbidden tokens were added to or removed from existing audits.
- The allowance token set remains exactly `{"epsilon", "eps", "guard", "cas"}`.
- The existing precision-floor occurrence audit in `test_task001_source_purity.py` was not changed.
- No imports from `src/lloyd_v4/` were added to the new helper.
