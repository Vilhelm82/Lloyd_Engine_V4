from _audit_helpers.lineage import (
    all_operation_ids_in_corpus,
    collected_instances,
    manifest_operation_id_registry,
    static_operation_id_registry,
)
from _audit_helpers.manifest import load_manifest


def test_runtime_operation_ids_are_registered_in_manifest_and_source() -> None:
    manifest = load_manifest()
    manifest_registry = manifest_operation_id_registry(manifest)
    static_registry = static_operation_id_registry()
    runtime_ids = all_operation_ids_in_corpus(collected_instances())

    missing_from_manifest = sorted(runtime_ids - set(manifest_registry))
    untraceable_in_source = sorted(operation_id for operation_id in runtime_ids if operation_id not in static_registry)

    assert not untraceable_in_source, f"operation_ids not declared in source: {untraceable_in_source}"
    assert not missing_from_manifest, (
        "operation_ids declared in source but missing from manifest: "
        + ", ".join(
            f"{operation_id} ({static_registry[operation_id]})"
            for operation_id in missing_from_manifest
        )
    )
