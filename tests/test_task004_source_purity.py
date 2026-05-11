from pathlib import Path

from _audit_helpers.precision_floor_allowance import is_allowed_precision_floor_comment_token


ROOT = Path(__file__).resolve().parents[1]


def _source_files(*roots: Path) -> list[Path]:
    return [path for root in roots for path in root.rglob("*.py") if path.is_file()]


def test_clean_room_source_audit() -> None:
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


def test_existing_layers_do_not_import_metrology_or_leak_metrology_terms() -> None:
    layer_files = _source_files(ROOT / "src" / "lloyd_v4" / "primitives", ROOT / "src" / "lloyd_v4" / "projection")
    forbidden = (
        "lloyd_v4.metrology",
        "from lloyd_v4.metrology",
        "import metrology",
        "noise" + "_floor",
        "b" + "_k",
        "K" + "_q",
        "calib" + "ration",
    )
    offenders = [
        f"{path.relative_to(ROOT)}:{token}"
        for path in layer_files
        for token in forbidden
        if token in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_task004_source_has_no_direct_kq_division_or_deferred_feature_terms() -> None:
    metrology_files = _source_files(ROOT / "src" / "lloyd_v4" / "metrology")
    forbidden = (
        "proxy_observable / transfer_observable",
        "branch" + "_fingerprint",
        "finger" + "print",
        "slope" + "_flow",
        "flow" + "_model",
        "finite" + "_eta",
        "domain" + "_consumer",
        "quantile",
        "smooth" + "ing",
    )
    offenders = [
        f"{path.relative_to(ROOT)}:{token}"
        for path in metrology_files
        for token in forbidden
        if token in path.read_text(encoding="utf-8")
    ]

    assert offenders == []
