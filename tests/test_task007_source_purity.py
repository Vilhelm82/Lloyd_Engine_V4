from pathlib import Path

from _audit_helpers.precision_floor_allowance import is_allowed_precision_floor_comment_token


ROOT = Path(__file__).resolve().parents[1]


def _source_files(*roots: Path) -> list[Path]:
    return [path for root in roots for path in root.rglob("*.py") if path.is_file()]


def test_task007_source_audits() -> None:
    checks = [
        (ROOT / "src", ("lloyd" + "_v3", "safe" + "_mask", 'projection_mode="' + "legacy" + '"', "legacy" + "_compat", "clamp" + "_min", "epsilon", "eps")),
        (ROOT / "src" / "lloyd_v4", ("safe" + "_divide", "safe" + "_denominator", "denominator" + "_floor", "small" + "_denominator", "res" + "cue", "gu" + "ard", "clamp", "stabilized" + "_log", "log" + "_offset", "log1p", "isclose", "allclose", "thresh" + "old", "toler" + "ance", "confidence" + "_score", "weighted" + "_score")),
        (ROOT / "src" / "lloyd_v4", ("finite" + "_eta", "history" + "_trace", "domain" + "_consumer", "domain" + "_classifier", "bearing", "aerospace", "betting", "scanner", "flow" + "_integrator", "symbolic" + "_simplifier", "cas", "parser")),
        (ROOT / "src" / "lloyd_v4", ("adapter", "bridge", "compatibility" + "_shim", "downgrade", "legacy" + "_mode", "cross" + "_engine")),
    ]
    offenders = []
    for root, tokens in checks:
        for path in _source_files(root):
            text = path.read_text(encoding="utf-8")
            for token in tokens:
                if token == "history" + "_trace" and (
                    path == ROOT / "src" / "lloyd_v4" / "core" / "status.py"
                    or ROOT / "src" / "lloyd_v4" / "history" in path.parents
                ):
                    continue
                rel = str(path.relative_to(ROOT))
                if token in text and not is_allowed_precision_floor_comment_token(rel, text, token):
                    offenders.append(f"{path.relative_to(ROOT)}:{token}")

    assert offenders == []


def test_refinery_dependency_direction_remains_one_way() -> None:
    offenders = []
    earlier_roots = [
        ROOT / "src" / "lloyd_v4" / "core",
        ROOT / "src" / "lloyd_v4" / "primitives",
        ROOT / "src" / "lloyd_v4" / "projection",
        ROOT / "src" / "lloyd_v4" / "metrology",
        ROOT / "src" / "lloyd_v4" / "branch",
    ]
    for path in _source_files(*earlier_roots):
        text = path.read_text(encoding="utf-8")
        for token in ("lloyd_v4.refinery", "from lloyd_v4.refinery", "import refinery"):
            if token in text:
                offenders.append(f"{path.relative_to(ROOT)}:{token}")

    assert offenders == []


def test_earlier_layers_do_not_use_refinery_terms() -> None:
    roots = [
        ROOT / "src" / "lloyd_v4" / "primitives",
        ROOT / "src" / "lloyd_v4" / "projection",
        ROOT / "src" / "lloyd_v4" / "metrology",
        ROOT / "src" / "lloyd_v4" / "branch",
    ]
    offenders = [
        f"{path.relative_to(ROOT)}:{token}"
        for path in _source_files(*roots)
        for token in ("equation" + "_refinery", "refinery", "rewrite" + "_candidate", "same" + "_geometry", "lower" + "_slag", "slag")
        if token in path.read_text(encoding="utf-8")
    ]

    assert offenders == []
