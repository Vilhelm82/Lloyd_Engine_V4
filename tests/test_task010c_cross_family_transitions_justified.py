from _audit_helpers.lineage import (
    build_trace_id_index,
    collected_instances,
    family_of,
    is_transition_edge,
    transition_rule_registry,
    walk_chain,
)


def test_cross_family_transitions_have_registered_status_rules() -> None:
    instances = collected_instances()
    index = build_trace_id_index(instances)
    registry = transition_rule_registry()
    violations = []

    for child in instances:
        for parent_id in child.provenance.parents:
            parent = index[parent_id]
            parent_family = family_of(parent)
            child_family = family_of(child)
            if parent_family is child_family:
                continue
            if not is_transition_edge(parent, child):
                continue
            if (parent_family, child_family) not in registry:
                violations.append(
                    f"{parent.provenance.trace_id} ({parent_family.__name__}) -> "
                    f"{child.provenance.trace_id} ({child_family.__name__}): "
                    "no registered StatusTransitionRule"
                )
        tuple(walk_chain(child, index))

    assert not violations, "\n".join(sorted(set(violations)))
