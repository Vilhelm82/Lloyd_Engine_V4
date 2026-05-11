"""Task 011 -- verify per-observation identity via Provenance.inputs."""

import json

from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.primitives import (
    projective_ratio,
    stratified_quadratic_roots,
    typed_collection,
    typed_value,
)


def test_provenance_inputs_field_exists_and_defaults_empty() -> None:
    p = Provenance(operation_id="test", expression_path="test")

    assert p.inputs == ()


def test_provenance_inputs_appears_in_serialization() -> None:
    p = Provenance(operation_id="test", expression_path="test", inputs=(1, 2.5, "x"))

    payload = p.to_json_safe()

    assert payload["inputs"] == [1, 2.5, "x"]


def test_provenance_inputs_changes_trace_id() -> None:
    p1 = Provenance(operation_id="op", expression_path="path", inputs=(1,))
    p2 = Provenance(operation_id="op", expression_path="path", inputs=(2,))

    assert p1.trace_id != p2.trace_id


def test_projective_ratio_distinct_inputs_distinct_trace_ids() -> None:
    r1 = projective_ratio(1, 2)
    r2 = projective_ratio(2, 4)
    r3 = projective_ratio(50, 100)

    trace_ids = {r1.provenance.trace_id, r2.provenance.trace_id, r3.provenance.trace_id}

    assert len(trace_ids) == 3


def test_projective_ratio_identical_inputs_identical_trace_ids() -> None:
    r1 = projective_ratio(3, 7)
    r2 = projective_ratio(3, 7)

    assert r1.provenance.trace_id == r2.provenance.trace_id


def test_stratified_quadratic_roots_distinct_inputs_distinct_trace_ids() -> None:
    q1 = stratified_quadratic_roots(1, -3, 2)
    q2 = stratified_quadratic_roots(1, -5, 6)
    q3 = stratified_quadratic_roots(2, -6, 4)

    trace_ids = {q1.provenance.trace_id, q2.provenance.trace_id, q3.provenance.trace_id}

    assert len(trace_ids) == 3


def test_typed_value_distinct_inputs_distinct_trace_ids() -> None:
    v1 = typed_value("alpha")
    v2 = typed_value("beta")
    v3 = typed_value(None)

    trace_ids = {v1.provenance.trace_id, v2.provenance.trace_id, v3.provenance.trace_id}

    assert len(trace_ids) == 3


def test_typed_collection_distinct_inputs_distinct_trace_ids() -> None:
    c1 = typed_collection([1, 2, 3])
    c2 = typed_collection([1, 2, 4])
    c3 = typed_collection([])

    trace_ids = {c1.provenance.trace_id, c2.provenance.trace_id, c3.provenance.trace_id}

    assert len(trace_ids) == 3


def test_primitive_inputs_populated_in_provenance() -> None:
    r = projective_ratio(7, 3)
    q = stratified_quadratic_roots(1.0, -3.0, 2.0)
    v = typed_value("hello")
    c = typed_collection([1, 2, 3])

    assert r.provenance.inputs == (7, 3)
    assert q.provenance.inputs == (1.0, -3.0, 2.0)
    assert v.provenance.inputs == ("hello",)
    assert c.provenance.inputs == ((1, 2, 3),)


def test_internal_operations_leave_inputs_empty() -> None:
    from lloyd_v4.primitives.projective_ratio import scalarize_projective_ratio
    from lloyd_v4.primitives.stratified_quadratic_roots import select_quadratic_root

    r = projective_ratio(3, 4)
    s = scalarize_projective_ratio(r)

    assert s.provenance.inputs == ()
    assert s.provenance.parents == (r.provenance.trace_id,)

    q = stratified_quadratic_roots(1, -3, 2)
    selected = select_quadratic_root(q, "minus")

    assert selected.provenance.inputs == ()
    assert q.provenance.trace_id in selected.provenance.parents


def test_trace_id_remains_in_serialization_round_trip() -> None:
    r = projective_ratio(1, 2)
    payload = to_json_safe(r)
    encoded = json.dumps(payload, allow_nan=False)
    decoded = json.loads(encoded)

    assert decoded["provenance"]["trace_id"] == r.provenance.trace_id
    assert decoded["provenance"]["inputs"] == [1, 2]
