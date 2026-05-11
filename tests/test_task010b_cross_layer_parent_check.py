from _audit_helpers.manifest import (
    extract_lloyd_v4_import_records,
    iter_layer_source_files,
    load_manifest,
    parents_for_layer,
)


def test_cross_layer_imports_only_target_declared_parents() -> None:
    manifest = load_manifest()
    layer_names = {layer.name for layer in manifest.layers}
    violations = []

    for layer in manifest.layers:
        parents = set(parents_for_layer(manifest, layer.name))
        for source_path in iter_layer_source_files(layer.name):
            for record in extract_lloyd_v4_import_records(source_path):
                parts = record.module_path.split(".")
                if len(parts) < 2:
                    continue
                targeted_layer = parts[1]
                if targeted_layer not in layer_names:
                    continue
                if targeted_layer == layer.name or targeted_layer in parents:
                    continue
                violations.append(
                    f"{source_path}:{record.lineno}: imports from {targeted_layer} "
                    f"but {layer.name}'s parents are {tuple(sorted(parents))}"
                )

    assert not violations, "\n".join(violations)
