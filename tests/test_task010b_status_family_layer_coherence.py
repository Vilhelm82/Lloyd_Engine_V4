from _audit_helpers.manifest import (
    descendants_of_layer,
    find_status_family_references,
    load_manifest,
    owning_layer_for_status_family,
)


def test_status_family_references_respect_semantic_ownership() -> None:
    manifest = load_manifest()
    layer_names = tuple(layer.name for layer in manifest.layers)
    families = tuple(
        family
        for layer in manifest.layers
        for family in layer.provides["status_families"]
    )
    references_by_layer = {
        layer_name: find_status_family_references(layer_name)
        for layer_name in layer_names
    }
    violations = []

    for family in families:
        owning_layer = owning_layer_for_status_family(manifest, family)
        allowed_layers = {owning_layer, *descendants_of_layer(manifest, owning_layer)}
        for referring_layer in layer_names:
            if referring_layer in allowed_layers:
                continue
            for source_path in references_by_layer[referring_layer].get(family, []):
                violations.append(
                    f"{source_path}: references {family} but {referring_layer} "
                    f"is not {owning_layer} nor a descendant"
                )

    assert not violations, "\n".join(violations)
