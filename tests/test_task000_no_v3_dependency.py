from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = [ROOT / "src"]


def _source_files() -> list[Path]:
    files: list[Path] = []
    for source_root in SOURCE_ROOTS:
        if source_root.exists():
            files.extend(
                path
                for path in source_root.rglob("*")
                if path.is_file() and path.suffix in {".py", ".md", ".toml"}
            )
    return files


def test_no_v3_runtime_dependency_or_legacy_modes() -> None:
    forbidden = (
        "lloyd" + "_v3",
        'projection_mode="' + "legacy" + '"',
        "legacy" + "_compat",
    )
    offenders: list[str] = []

    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                offenders.append(f"{path.relative_to(ROOT)}:{token}")

    assert offenders == []


def test_legacy_universal_mask_not_defined_in_source() -> None:
    offenders: list[str] = []
    token = "safe" + "_mask"

    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        if token in text:
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []
