from _audit_helpers.lineage import build_trace_id_index, chain_terminals, collected_instances
from _audit_helpers.manifest import load_manifest


def test_lineage_terminals_are_calibrated_primitives() -> None:
    manifest = load_manifest()
    calibrated = {
        operation_id
        for layer in manifest.layers
        for operation_id in layer.provides["calibrated_primitive_operations"]
    }
    instances = collected_instances()
    index = build_trace_id_index(instances)
    violations = []

    for instance in instances:
        for terminal in chain_terminals(instance, index):
            operation_id = terminal.provenance.operation_id
            if operation_id not in calibrated:
                violations.append(
                    f"{terminal.provenance.trace_id}: operation_id {operation_id} is not a calibrated primitive"
                )

    assert not violations, "\n".join(sorted(set(violations)))
