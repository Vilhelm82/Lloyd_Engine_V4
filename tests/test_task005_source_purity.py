from pathlib import Path

from _audit_helpers.precision_floor_allowance import is_allowed_precision_floor_comment_token


ROOT = Path(__file__).resolve().parents[1]


def _source_files(*roots: Path) -> list[Path]:
    return [path for root in roots for path in root.rglob("*.py") if path.is_file()]


def test_source_audits_remain_clean() -> None:
    checks = [
        (ROOT / "src", ("lloyd" + "_v3", "safe" + "_mask", 'projection_mode="' + "legacy" + '"', "legacy" + "_compat", "clamp" + "_min", "epsilon", "eps")),
        (ROOT / "src" / "lloyd_v4", ("safe" + "_divide", "safe" + "_denominator", "denominator" + "_floor", "small" + "_denominator", "res" + "cue", "gu" + "ard")),
        (ROOT / "src" / "lloyd_v4", ("finite" + "_eta", "domain" + "_consumer", "equation" + "_refinery")),
        (ROOT / "src" / "lloyd_v4", ("adapter", "bridge", "compatibility" + "_shim", "downgrade", "legacy" + "_mode", "cross" + "_engine")),
    ]
    offenders = []
    for root, tokens in checks:
        for path in _source_files(root):
            rel = str(path.relative_to(ROOT))
            text = path.read_text(encoding="utf-8")
            for token in tokens:
                if token in text and not is_allowed_precision_floor_comment_token(rel, text, token):
                    offenders.append(f"{rel}:{token}")

    assert offenders == []


def test_dependency_direction_remains_clean() -> None:
    offenders = []
    for path in _source_files(ROOT / "src" / "lloyd_v4" / "primitives", ROOT / "src" / "lloyd_v4" / "projection"):
        text = path.read_text(encoding="utf-8")
        for token in ("lloyd_v4.metrology", "from lloyd_v4.metrology", "import metrology"):
            if token in text:
                offenders.append(f"{path.relative_to(ROOT)}:{token}")
    for path in _source_files(ROOT / "src" / "lloyd_v4" / "primitives"):
        text = path.read_text(encoding="utf-8")
        for token in ("lloyd_v4.projection", "from lloyd_v4.projection", "import projection"):
            if token in text:
                offenders.append(f"{path.relative_to(ROOT)}:{token}")

    assert offenders == []
