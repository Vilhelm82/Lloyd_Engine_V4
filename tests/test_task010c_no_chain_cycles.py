from _audit_helpers.lineage import LineageCycleError, build_trace_id_index, collected_instances, walk_chain


def test_runtime_lineage_chains_have_no_cycles() -> None:
    instances = collected_instances()
    index = build_trace_id_index(instances)
    cycles = []

    for instance in instances:
        try:
            tuple(walk_chain(instance, index))
        except LineageCycleError as exc:
            cycles.append(f"{instance.provenance.trace_id}: cycle at {exc.trace_id}")

    assert not cycles, "\n".join(cycles)
