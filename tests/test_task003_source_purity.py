from pathlib import Path

from _audit_helpers.precision_floor_allowance import is_allowed_precision_floor_comment_token


ROOT = Path(__file__).resolve().parents[1]


def _source_files(*roots: Path) -> list[Path]:
    return [path for root in roots for path in root.rglob("*.py") if path.is_file()]


def test_source_forbidden_terms_are_absent() -> None:
    forbidden = (
        "lloyd" + "_v3",
        "safe" + "_mask",
        'projection_mode="' + "legacy" + '"',
        "legacy" + "_compat",
        "clamp" + "_min",
        "epsilon",
        "eps",
    )
    offenders = []
    for path in _source_files(ROOT / "src"):
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text and not is_allowed_precision_floor_comment_token(rel, text, token):
                offenders.append(f"{rel}:{token}")

    assert offenders == []


def test_no_correction_or_branch_policy_terms_in_source() -> None:
    forbidden = (
        "safe" + "_divide",
        "safe" + "_denominator",
        "denominator" + "_floor",
        "small" + "_denominator",
        "res" + "cue",
        "gu" + "ard",
        "principal" + "_root",
        "nearest" + "_root",
        "default" + "_branch",
        "auto" + "_branch",
        "root" + "_policy",
        "advance" + "_policy",
        "projection" + "_fallback",
        "fallback" + "_branch",
    )
    offenders = []
    for path in _source_files(ROOT / "src" / "lloyd_v4"):
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text and not is_allowed_precision_floor_comment_token(rel, text, token):
                offenders.append(f"{rel}:{token}")

    assert offenders == []


def test_no_discriminant_or_metrology_terms_in_projection_paths() -> None:
    forbidden = (
        "disc" + "_floor",
        "discriminant" + "_floor",
        "clamp" + "_discriminant",
        "safe" + "_sqrt",
        "sqrt" + "_gu" + "ard",
        "small" + "_discriminant",
        "toler" + "ance",
        "thresh" + "old",
        "b" + "_k",
        "K" + "_q",
        "branch" + "_fingerprint",
        "finger" + "print",
        "noise" + "_floor",
        "calib" + "ration",
    )
    roots = [
        ROOT / "src" / "lloyd_v4" / "projection",
        ROOT / "src" / "lloyd_v4" / "primitives",
    ]
    offenders = [
        f"{path.relative_to(ROOT)}:{token}"
        for path in _source_files(*roots)
        for token in forbidden
        if token in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_task003_source_does_not_recompute_formula_or_divide_coordinates() -> None:
    source = ROOT / "src" / "lloyd_v4" / "projection" / "exact_projection.py"
    text = source.read_text(encoding="utf-8") if source.exists() else ""

    assert "b * b" not in text
    assert "sqrt" not in text
    assert ".numerator /" not in text

