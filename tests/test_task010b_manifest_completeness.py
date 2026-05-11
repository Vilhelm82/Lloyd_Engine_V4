from _audit_helpers.manifest import load_manifest


EXPECTED_LAYERS = (
    "core",
    "primitives",
    "projection",
    "metrology",
    "branch",
    "refinery",
    "history",
    "solver",
)

PROVIDES_KEYS = (
    "status_families",
    "value_types",
    "protocol_types",
    "transition_types",
    "errors_and_utilities",
    "operations",
    "calibrated_primitive_operations",
    "internal_operations",
    "all_exports",
)


def test_manifest_has_complete_categorised_schema() -> None:
    manifest = load_manifest()
    assert tuple(layer.name for layer in manifest.layers) == EXPECTED_LAYERS

    declared = set()
    for layer in manifest.layers:
        assert layer.name
        assert layer.description
        assert isinstance(layer.parents, tuple)
        assert tuple(layer.provides) == PROVIDES_KEYS
        for key in PROVIDES_KEYS:
            assert isinstance(layer.provides[key], tuple)

        if layer.name == "core":
            assert layer.parents == ()
        else:
            assert layer.parents

        assert set(layer.parents).issubset(declared)
        declared.add(layer.name)


def test_manifest_parent_graph_is_acyclic() -> None:
    manifest = load_manifest()
    by_name = manifest.by_name

    def visit(layer_name: str, stack: tuple[str, ...]) -> None:
        assert layer_name not in stack, f"cycle detected: {stack + (layer_name,)}"
        for parent in by_name[layer_name].parents:
            visit(parent, stack + (layer_name,))

    for layer in manifest.layers:
        visit(layer.name, ())
