from pathlib import Path
import re

from _audit_helpers.precision_floor_allowance import is_allowed_precision_floor_comment_token


ROOT = Path(__file__).resolve().parents[1]


def _src_text() -> list[tuple[Path, str]]:
    return [
        (path, path.read_text(encoding="utf-8"))
        for path in (ROOT / "src").rglob("*.py")
        if path.is_file()
    ]


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
    for path, text in _src_text():
        rel = str(path.relative_to(ROOT))
        for token in forbidden:
            if token in text and not is_allowed_precision_floor_comment_token(rel, text, token):
                offenders.append(f"{rel}:{token}")

    assert offenders == []


def test_no_hidden_denominator_correction_names_in_core_or_primitives() -> None:
    forbidden = (
        "safe" + "_divide",
        "safe" + "_denominator",
        "denominator" + "_floor",
        "small" + "_denominator",
        "res" + "cue",
        "gu" + "ard",
    )
    roots = [ROOT / "src" / "lloyd_v4" / "core", ROOT / "src" / "lloyd_v4" / "primitives"]
    files = [path for root in roots for path in root.rglob("*.py")]
    offenders = []
    for path in files:
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text and not is_allowed_precision_floor_comment_token(rel, text, token):
                offenders.append(f"{rel}:{token}")

    assert offenders == []


def test_precision_floor_occurrences_are_declared_observability_evidence() -> None:
    pattern = re.compile(
        "|".join(
            [
                "precision" + "_floor",
                "roundoff" + "_floor",
                "unit" + "_roundoff",
                "machine" + "_epsilon",
                "cancellation" + "_ratio",
                r"2\.0\s*\*\*\s*-52",
                r"sys\.float_info\.epsilon",
                r"np\.finfo",
            ]
        )
    )
    allowed = {
        ("src/lloyd_v4/primitives/typed_finite_difference.py", "precision_floor"),
        ("src/lloyd_v4/primitives/typed_finite_difference.py", "cancellation_ratio"),
        ("src/lloyd_v4/primitives/typed_finite_difference.py", "2.0**-52"),
        ("src/lloyd_v4/primitives/typed_finite_difference.py", "sys.float_info.epsilon"),
    }
    offenders = []
    for path, text in _src_text():
        rel = str(path.relative_to(ROOT))
        for match in pattern.finditer(text):
            token = re.sub(r"\s+", "", match.group(0))
            if (rel, token) not in allowed:
                offenders.append(f"{rel}:{match.group(0)}")

    assert offenders == []

