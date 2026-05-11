"""Task 022: regression tests for the tightened precision-floor allowance."""

from _audit_helpers.precision_floor_allowance import (
    PRECISION_FLOOR_COMMENT_TOKENS,
    PRECISION_FLOOR_FILE,
    is_allowed_precision_floor_comment_token,
)


class TestPrecisionFloorAllowance:
    """Lock the tightened allowance behavior."""

    def test_comment_line_eps_is_allowed(self) -> None:
        text = "# eps is documented here\nreturn 2.0**-52\n"

        assert is_allowed_precision_floor_comment_token(PRECISION_FLOOR_FILE, text, "eps")

    def test_non_comment_eps_alongside_comment_is_not_allowed(self) -> None:
        text = "# eps in comment\n_eps_floor = 2.0**-52  # but here eps is used in code\n"

        assert not is_allowed_precision_floor_comment_token(PRECISION_FLOOR_FILE, text, "eps")

    def test_only_non_comment_eps_is_not_allowed(self) -> None:
        text = "x = 1\n_eps = 2.0**-52\n"

        assert not is_allowed_precision_floor_comment_token(PRECISION_FLOOR_FILE, text, "eps")

    def test_other_file_not_allowed(self) -> None:
        text = "# eps in comment\n"

        assert not is_allowed_precision_floor_comment_token("src/lloyd_v4/primitives/directional_alpha_probe.py", text, "eps")
        assert not is_allowed_precision_floor_comment_token("src/lloyd_v4/some_other_file.py", text, "eps")

    def test_unlisted_token_not_allowed(self) -> None:
        text = "# clamp_min in a comment\n"

        assert not is_allowed_precision_floor_comment_token(PRECISION_FLOOR_FILE, text, "clamp_min")
        assert not is_allowed_precision_floor_comment_token(PRECISION_FLOOR_FILE, text, "safe_mask")
        assert not is_allowed_precision_floor_comment_token(PRECISION_FLOOR_FILE, text, "rescue")

    def test_indented_comment_still_allowed(self) -> None:
        text = (
            "def f():\n"
            "    if True:\n"
            "        # eps inside indented comment\n"
            "        return 1\n"
        )

        assert is_allowed_precision_floor_comment_token(PRECISION_FLOOR_FILE, text, "eps")

    def test_audit_would_catch_synthetic_non_comment_use(self) -> None:
        synthetic_text = (
            "# Per-operand unit roundoff: u = 2^-53.\n"
            "# This comment legitimately references eps and guard.\n"
            "def _precision_floor(precision):\n"
            "    return 2.0**-52\n"
            "\n"
            "def _eps_floor():  # function name is non-comment use of 'eps'\n"
            "    return 2.0**-52\n"
        )

        assert PRECISION_FLOOR_COMMENT_TOKENS == frozenset({"epsilon", "eps", "guard", "cas"})
        assert not is_allowed_precision_floor_comment_token(PRECISION_FLOOR_FILE, synthetic_text, "eps")
        token_present = "eps" in synthetic_text
        token_allowed = is_allowed_precision_floor_comment_token(PRECISION_FLOOR_FILE, synthetic_text, "eps")
        would_be_offender = token_present and not token_allowed
        assert would_be_offender
