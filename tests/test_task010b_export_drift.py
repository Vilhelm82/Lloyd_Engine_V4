from _audit_helpers.manifest import actual_all_exports, all_exports_for_layer, load_manifest


def test_manifest_all_exports_match_layer_init_all() -> None:
    manifest = load_manifest()
    mismatches = []
    for layer in manifest.layers:
        actual = set(actual_all_exports(layer.name))
        declared = set(all_exports_for_layer(manifest, layer.name))
        missing_from_source = sorted(declared - actual)
        missing_from_manifest = sorted(actual - declared)
        if missing_from_source or missing_from_manifest:
            mismatches.append(
                f"{layer.name}: manifest_only={missing_from_source}, source_only={missing_from_manifest}"
            )

    assert not mismatches, "\n".join(mismatches)
