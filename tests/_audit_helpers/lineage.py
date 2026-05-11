from __future__ import annotations

import ast
import inspect
import importlib
from enum import StrEnum
from pathlib import Path
from typing import Iterable, Mapping

from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.transitions import StatusTransitionRule

from _audit_helpers.manifest import Manifest, SRC_ROOT, iter_layer_source_files, load_manifest


_collected_instances: list[TypedResult] = []
_collector_installed = False
_original_typed_result_init = None


class LineageCycleError(RuntimeError):
    def __init__(self, trace_id: str):
        super().__init__(f"cycle detected at trace_id {trace_id}")
        self.trace_id = trace_id


def install_collector() -> None:
    global _collector_installed, _original_typed_result_init
    if _collector_installed:
        return

    _original_typed_result_init = TypedResult.__init__

    def collecting_init(self, *args, **kwargs):
        _original_typed_result_init(self, *args, **kwargs)
        if _constructed_from_substrate_source():
            _collected_instances.append(self)

    TypedResult.__init__ = collecting_init
    _collector_installed = True


def collected_instances() -> tuple[TypedResult, ...]:
    return tuple(_collected_instances)


def build_trace_id_index(instances: Iterable[TypedResult]) -> dict[str, TypedResult]:
    index: dict[str, TypedResult] = {}
    for instance in instances:
        index[instance.provenance.trace_id] = instance
    return index


def walk_chain(instance: TypedResult, index: Mapping[str, TypedResult]) -> Iterable[TypedResult]:
    seen: set[str] = set()

    def visit(node: TypedResult) -> Iterable[TypedResult]:
        trace_id = node.provenance.trace_id
        if trace_id in seen:
            raise LineageCycleError(trace_id)
        seen.add(trace_id)
        yield node
        for parent_id in node.provenance.parents:
            parent = index.get(parent_id)
            if parent is None:
                raise KeyError(f"missing parent trace_id {parent_id} for {trace_id}")
            yield from visit(parent)
        seen.remove(trace_id)

    yield from visit(instance)


def chain_terminals(instance: TypedResult, index: Mapping[str, TypedResult]) -> tuple[TypedResult, ...]:
    terminals: list[TypedResult] = []

    def visit(node: TypedResult, seen: set[str]) -> None:
        trace_id = node.provenance.trace_id
        if trace_id in seen:
            raise LineageCycleError(trace_id)
        if not node.provenance.parents:
            terminals.append(node)
            return
        next_seen = {*seen, trace_id}
        for parent_id in node.provenance.parents:
            parent = index.get(parent_id)
            if parent is None:
                raise KeyError(f"missing parent trace_id {parent_id} for {trace_id}")
            visit(parent, next_seen)

    visit(instance, set())
    return tuple(terminals)


def family_of(instance: TypedResult) -> type[StrEnum]:
    return type(instance.status)


def operation_id_of(instance: TypedResult) -> str:
    return instance.provenance.operation_id


def all_operation_ids_in_corpus(instances: Iterable[TypedResult]) -> frozenset[str]:
    return frozenset(operation_id_of(instance) for instance in instances)


def static_operation_id_registry() -> Mapping[str, str]:
    registry: dict[str, str] = {}
    manifest = load_manifest()
    for layer in manifest.layers:
        for source_path in iter_layer_source_files(layer.name):
            tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                for keyword in node.keywords:
                    if keyword.arg != "operation_id":
                        continue
                    if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                        registry[keyword.value.value] = layer.name
    return registry


def manifest_operation_id_registry(manifest: Manifest) -> Mapping[str, str]:
    registry: dict[str, str] = {}
    categories = ("operations", "calibrated_primitive_operations", "internal_operations")
    for layer in manifest.layers:
        for category in categories:
            for operation_id in layer.provides[category]:
                registry[operation_id] = layer.name
    return registry


def transition_rule_registry() -> dict[tuple[type, type], list[StatusTransitionRule]]:
    registry: dict[tuple[type, type], list[StatusTransitionRule]] = {}
    manifest = load_manifest()
    for layer in manifest.layers:
        module = importlib.import_module(f"lloyd_v4.{layer.name}")
        for export_name in getattr(module, "__all__", ()):
            value = getattr(module, export_name)
            _collect_transition_rules(value, registry)
    return registry


def is_transition_edge(parent: TypedResult, child: TypedResult) -> bool:
    parent_family = family_of(parent)
    child_family = family_of(child)
    if parent_family is child_family:
        return False
    return (parent_family, child_family) in transition_rule_registry()


def _collect_transition_rules(value: object, registry: dict[tuple[type, type], list[StatusTransitionRule]]) -> None:
    if isinstance(value, StatusTransitionRule):
        if value.output_status_family is not None:
            registry.setdefault((value.input_status_family, value.output_status_family), []).append(value)
        return
    if isinstance(value, Mapping):
        for item in value.values():
            _collect_transition_rules(item, registry)


def _constructed_from_substrate_source() -> bool:
    src_root = SRC_ROOT.resolve()
    for frame in inspect.stack()[2:]:
        try:
            path = Path(frame.filename).resolve()
        except OSError:
            continue
        if path.is_relative_to(src_root):
            return True
    return False
