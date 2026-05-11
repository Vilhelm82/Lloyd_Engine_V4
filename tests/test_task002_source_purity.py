from pathlib import Path

from _audit_helpers.precision_floor_allowance import is_allowed_precision_floor_comment_token


ROOT = Path(__file__).resolve().parents[1]


def _source_files(*roots: Path) -> list[Path]:
    return [path for root in roots for path in root.rglob("*.py") if path.is_file()]


def test_source_only_forbidden_concept_audit() -> None:
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


def test_no_hidden_correction_names_in_core_or_primitives() -> None:
    forbidden = (
        "safe" + "_divide",
        "safe" + "_denominator",
        "denominator" + "_floor",
        "small" + "_denominator",
        "res" + "cue",
        "gu" + "ard",
    )
    files = _source_files(ROOT / "src" / "lloyd_v4" / "primitives", ROOT / "src" / "lloyd_v4" / "core")
    offenders = []
    for path in files:
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text and not is_allowed_precision_floor_comment_token(rel, text, token):
                offenders.append(f"{rel}:{token}")

    assert offenders == []


def test_no_discriminant_correction_names_in_core_or_primitives() -> None:
    forbidden = (
        "disc" + "_floor",
        "discriminant" + "_floor",
        "clamp" + "_discriminant",
        "safe" + "_sqrt",
        "sqrt" + "_gu" + "ard",
        "small" + "_discriminant",
        "toler" + "ance",
        "thresh" + "old",
    )
    files = _source_files(ROOT / "src" / "lloyd_v4" / "primitives", ROOT / "src" / "lloyd_v4" / "core")
    offenders = [
        f"{path.relative_to(ROOT)}:{token}"
        for path in files
        for token in forbidden
        if token in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_no_complex_root_path_in_task002_source() -> None:
    source = (ROOT / "src" / "lloyd_v4" / "primitives" / "stratified_quadratic_roots.py")
    text = source.read_text(encoding="utf-8") if source.exists() else ""

    assert "import cmath" not in text
    assert "from cmath" not in text
    assert "complex(" not in text

