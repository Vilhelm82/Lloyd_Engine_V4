from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "Build_Docs" / "Architecture" / "layer_manifest.json"
SRC_ROOT = ROOT / "src" / "lloyd_v4"


@dataclass(frozen=True)
class LayerEntry:
    name: str
    description: str
    parents: tuple[str, ...]
    provides: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class Manifest:
    layers: tuple[LayerEntry, ...]

    @property
    def by_name(self) -> Mapping[str, LayerEntry]:
        return {layer.name: layer for layer in self.layers}


@dataclass(frozen=True)
class ImportRecord:
    module_path: str
    lineno: int


def load_manifest() -> Manifest:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    layers = []
    for item in payload["layers"]:
        provides = {
            key: tuple(value)
            for key, value in item["provides"].items()
        }
        layers.append(
            LayerEntry(
                name=item["name"],
                description=item["description"],
                parents=tuple(item["parents"]),
                provides=provides,
            )
        )
    return Manifest(layers=tuple(layers))


def parents_for_layer(manifest: Manifest, layer_name: str) -> tuple[str, ...]:
    return manifest.by_name[layer_name].parents


def all_exports_for_layer(manifest: Manifest, layer_name: str) -> tuple[str, ...]:
    return manifest.by_name[layer_name].provides["all_exports"]


def status_families_for_layer(manifest: Manifest, layer_name: str) -> tuple[str, ...]:
    return manifest.by_name[layer_name].provides["status_families"]


def owning_layer_for_status_family(manifest: Manifest, family_name: str) -> str:
    owners = [
        layer.name
        for layer in manifest.layers
        if family_name in layer.provides["status_families"]
    ]
    if len(owners) != 1:
        raise KeyError(f"status family {family_name!r} has owners {owners!r}")
    return owners[0]


def descendants_of_layer(manifest: Manifest, layer_name: str) -> frozenset[str]:
    descendants: set[str] = set()
    changed = True
    while changed:
        changed = False
        for layer in manifest.layers:
            if layer.name == layer_name or layer.name in descendants:
                continue
            if layer_name in layer.parents or descendants.intersection(layer.parents):
                descendants.add(layer.name)
                changed = True
    return frozenset(descendants)


def extract_lloyd_v4_imports(source_path: Path) -> tuple[str, ...]:
    return tuple(record.module_path for record in extract_lloyd_v4_import_records(source_path))


def extract_lloyd_v4_import_records(source_path: Path) -> tuple[ImportRecord, ...]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    records: list[ImportRecord] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("lloyd_v4."):
                    records.append(ImportRecord(module_path=alias.name, lineno=node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("lloyd_v4."):
                records.append(ImportRecord(module_path=node.module, lineno=node.lineno))
    return tuple(records)


def actual_all_exports(layer_name: str) -> tuple[str, ...]:
    init_path = SRC_ROOT / layer_name / "__init__.py"
    tree = ast.parse(init_path.read_text(encoding="utf-8"), filename=str(init_path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                return _literal_string_sequence(node.value)
    raise AssertionError(f"{init_path} does not declare __all__")


def iter_layer_source_files(layer_name: str) -> Iterable[Path]:
    layer_root = SRC_ROOT / layer_name
    for path in sorted(layer_root.rglob("*.py")):
        if "__pycache__" not in path.parts:
            yield path


def find_status_family_references(layer_name: str) -> Mapping[str, list[Path]]:
    manifest = load_manifest()
    families = tuple(
        family
        for layer in manifest.layers
        for family in layer.provides["status_families"]
    )
    references: dict[str, list[Path]] = {family: [] for family in families}
    for path in iter_layer_source_files(layer_name):
        if path == SRC_ROOT / "core" / "status.py":
            continue
        text = path.read_text(encoding="utf-8")
        candidates = [family for family in families if family in text]
        if not candidates:
            continue
        tree = ast.parse(text, filename=str(path))
        seen = set(_referenced_names(tree))
        for family in candidates:
            if family in seen or family in text:
                references[family].append(path)
    return {family: paths for family, paths in references.items() if paths}


def _literal_string_sequence(node: ast.AST) -> tuple[str, ...]:
    if not isinstance(node, (ast.List, ast.Tuple)):
        raise AssertionError("__all__ must be a literal list or tuple")
    values = []
    for item in node.elts:
        if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
            raise AssertionError("__all__ entries must be literal strings")
        values.append(item.value)
    return tuple(values)


def _referenced_names(tree: ast.AST) -> Iterable[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            yield node.id
        elif isinstance(node, ast.Attribute):
            yield node.attr
