"""Audit allowance for the Task 020 precision-floor comment."""

PRECISION_FLOOR_FILE = "src/lloyd_v4/primitives/typed_finite_difference.py"
PRECISION_FLOOR_COMMENT_TOKENS = frozenset({"epsilon", "eps", "guard", "cas"})


def is_allowed_precision_floor_comment_token(rel: str, text: str, token: str) -> bool:
    """Return True iff every token occurrence is in a comment line."""
    if rel != PRECISION_FLOOR_FILE:
        return False
    if token not in PRECISION_FLOOR_COMMENT_TOKENS:
        return False
    for line in text.splitlines():
        if token in line and not line.lstrip().startswith("#"):
            return False
    return True
