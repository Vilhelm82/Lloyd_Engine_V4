# Task 011 — Provenance Identity (inputs field, content-addressed trace_id)

## Intent

Fix the per-observation identity gap exposed by Stress Test Finding 1:
`projective_ratio(1, 2)`, `projective_ratio(2, 4)`, and `projective_ratio(50, 100)`
all produce the same `trace_id` (`792d03b3bd8e1521`) because the current trace_id
derivation hashes operation/expression/precision/backend/device/measurement_resolution/
parents/status — but not the actual inputs to the invocation.

This violates **Axiom 5** ("numerical representation is a path, not the object"):
the path is the inputs + operation + parents, and the trace_id should reflect that.

The fix: add an `inputs: tuple[Any, ...] = ()` field to `Provenance`, populate it
in calibrated primitives (which are the only operations that produce path information
not already encoded in parents), and include it in the trace_id hash payload.

## Source labelling

- **(V4-surface)** Bug observable from running V4 against its own primitives. See
  `tests/_audit_helpers/lineage.py::build_trace_id_index` for where collisions
  silently overwrite, and `/mnt/user-data/outputs/v4_stress_test_output.txt` for
  the demonstration.
- **(theorem-derived)** Axiom 5 mandates path information not be dropped.
- **(design-aligned)** PROVENANCE_MODEL.md describes trace_id as identity, with
  equivalence classes as a separate protocol-defined layer. Content-addressing
  trace_id by inputs+operation+parents is consistent with this separation.

## Pre-task evidence (must reproduce before modifying anything)

Run from `/mnt/fast/Lloyd_Engine_V4`:

```bash
python -c "
from lloyd_v4.primitives import projective_ratio
print(projective_ratio(1, 2).provenance.trace_id)
print(projective_ratio(2, 4).provenance.trace_id)
print(projective_ratio(50, 100).provenance.trace_id)
"
```

Expected output (current behaviour, the bug):
```
792d03b3bd8e1521
792d03b3bd8e1521
792d03b3bd8e1521
```

This collision must be reproduced before the task starts. After the task, all
three trace_ids must be distinct.

## Scope

In scope:
- `src/lloyd_v4/core/provenance.py` — add `inputs` field, extend hash payload, extend serialization
- `src/lloyd_v4/primitives/projective_ratio.py` — populate inputs in primitive call (NOT in `scalarize_projective_ratio`)
- `src/lloyd_v4/primitives/stratified_quadratic_roots.py` — populate inputs in primitive call (NOT in `select_quadratic_root`)
- `src/lloyd_v4/primitives/typed_value.py` — populate inputs
- `src/lloyd_v4/primitives/typed_collection.py` — populate inputs
- New test file: `tests/test_task011_provenance_inputs.py`

Out of scope:
- Conditioning honesty (Stress Test Finding 3) — separate task
- Validity dishonesty under overflow (Stress Test Finding 2) — separate task
- Equivalence-class observation (Stress Test Findings 4, 5) — separate task, deferred to discovery
- Composite/internal operation provenance — left empty inputs=() because parents transitively encode their path

Layer manifest changes: none. `Provenance` is declared at the type level in
`core.value_types`, and adding an optional field is field-internal. The manifest
machinery (`tests/test_task010a_layer_manifest_machine_readable.py`,
`tests/test_task010b_*`) does not introspect dataclass fields.

## File-by-file changes

### `src/lloyd_v4/core/provenance.py`

Add the `inputs` field after `measurement_resolution` and before `parents` (keeps
path-metadata fields grouped before reference-metadata fields):

```python
@dataclass(frozen=True, slots=True)
class Provenance:
    operation_id: str
    expression_path: str
    precision: str = "unspecified"
    backend: str = "python"
    device: str = "cpu"
    measurement_resolution: Any | None = None
    inputs: tuple[Any, ...] = ()  # NEW — canonical inputs to this invocation
    parents: tuple[str, ...] = ()
    trace_id: str | None = None
    status: ProvenanceStatus = ProvenanceStatus.COMPLETE
```

Extend `_derive_trace_id` to include `inputs` in the hash payload:

```python
def _derive_trace_id(self) -> str:
    payload = {
        "operation_id": self.operation_id,
        "expression_path": self.expression_path,
        "precision": self.precision,
        "backend": self.backend,
        "device": self.device,
        "measurement_resolution": to_json_safe(self.measurement_resolution),
        "inputs": to_json_safe(list(self.inputs)),  # NEW
        "parents": list(self.parents),
        "status": self.status.value,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]
```

Extend `to_json_safe` to surface `inputs`:

```python
def to_json_safe(self) -> dict[str, Any]:
    return {
        "operation_id": self.operation_id,
        "expression_path": self.expression_path,
        "precision": self.precision,
        "backend": self.backend,
        "device": self.device,
        "measurement_resolution": to_json_safe(self.measurement_resolution),
        "inputs": to_json_safe(list(self.inputs)),  # NEW
        "parents": list(self.parents),
        "trace_id": self.trace_id,
        "status": self.status.value,
    }
```

### `src/lloyd_v4/primitives/projective_ratio.py`

In `projective_ratio(...)`, populate inputs with the unwrapped raw scalars:

```python
return TypedResult(
    value=ProjectiveRatioValue(raw_numerator, raw_denominator),
    space=PROJECTIVE_RATIO_SPACE,
    status=status,
    validity=validity,
    conditioning=Conditioning(status=ConditioningStatus.WELL_CONDITIONED),
    provenance=Provenance(
        operation_id="projective_ratio",
        expression_path="canonical_projective_ratio",
        precision=precision,
        backend=backend,
        device=device,
        measurement_resolution=measurement_resolution,
        inputs=(raw_numerator, raw_denominator),  # NEW
        parents=parents,
    ),
    protocol=ProtocolStatus.OK,
)
```

In `scalarize_projective_ratio(...)`: leave inputs as default (empty). The
`scalar_provenance` and the refusal-path `Provenance` both keep `parents=(...)`
referring to the input ratio's trace_id; this is sufficient.

### `src/lloyd_v4/primitives/stratified_quadratic_roots.py`

In `stratified_quadratic_roots(...)`, populate inputs with `(a, b, c)`:

```python
return TypedResult(
    value=StratifiedQuadraticRootValue(...),
    ...
    provenance=Provenance(
        operation_id="stratified_quadratic_roots",
        expression_path="direct_quadratic_formula",
        precision=precision,
        backend=backend,
        device=device,
        measurement_resolution=measurement_resolution,
        inputs=(a, b, c),  # NEW
    ),
    protocol=ProtocolStatus.OK,
)
```

In `select_quadratic_root(...)`: leave inputs as default (empty) for both the
`_selection_provenance` (refusal path) and the success-path constructed
Provenance. Parents already capture the path.

### `src/lloyd_v4/primitives/typed_value.py`

In `typed_value(value)`, populate inputs with `(value,)`:

```python
provenance=Provenance(
    operation_id="typed_value",
    expression_path="typed_value_construction",
    inputs=(value,),  # NEW
    parents=(),
),
```

### `src/lloyd_v4/primitives/typed_collection.py`

In `typed_collection(items)`, populate inputs with the items tuple:

```python
provenance=Provenance(
    operation_id="typed_collection",
    expression_path="typed_collection_construction",
    inputs=(items_tuple,),  # NEW — single-element tuple wrapping the items tuple
    parents=(),
),
```

Rationale for wrapping in a single-element tuple: `inputs` is `tuple[Any, ...]`
representing positional arguments. `typed_collection` takes one positional argument
(`items: Iterable[Any]`), so the inputs tuple has one element which is the
items tuple itself.

## Test additions

New file: `tests/test_task011_provenance_inputs.py`

```python
"""Task 011 — verify per-observation identity via Provenance.inputs."""

from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.primitives import (
    projective_ratio,
    stratified_quadratic_roots,
    typed_value,
    typed_collection,
)


def test_provenance_inputs_field_exists_and_defaults_empty() -> None:
    p = Provenance(operation_id="test", expression_path="test")
    assert p.inputs == ()


def test_provenance_inputs_appears_in_serialization() -> None:
    p = Provenance(
        operation_id="test",
        expression_path="test",
        inputs=(1, 2.5, "x"),
    )
    payload = p.to_json_safe()
    assert payload["inputs"] == [1, 2.5, "x"]


def test_provenance_inputs_changes_trace_id() -> None:
    p1 = Provenance(operation_id="op", expression_path="path", inputs=(1,))
    p2 = Provenance(operation_id="op", expression_path="path", inputs=(2,))
    assert p1.trace_id != p2.trace_id


def test_projective_ratio_distinct_inputs_distinct_trace_ids() -> None:
    """Stress Test Finding 1 regression: same operation, different inputs,
    different trace_ids."""
    r1 = projective_ratio(1, 2)
    r2 = projective_ratio(2, 4)
    r3 = projective_ratio(50, 100)
    trace_ids = {
        r1.provenance.trace_id,
        r2.provenance.trace_id,
        r3.provenance.trace_id,
    }
    assert len(trace_ids) == 3, (
        f"expected three distinct trace_ids, got {trace_ids}"
    )


def test_projective_ratio_identical_inputs_identical_trace_ids() -> None:
    """Content-addressed identity: same inputs + same operation = same trace_id."""
    r1 = projective_ratio(3, 7)
    r2 = projective_ratio(3, 7)
    assert r1.provenance.trace_id == r2.provenance.trace_id


def test_stratified_quadratic_roots_distinct_inputs_distinct_trace_ids() -> None:
    q1 = stratified_quadratic_roots(1, -3, 2)
    q2 = stratified_quadratic_roots(1, -5, 6)
    q3 = stratified_quadratic_roots(2, -6, 4)
    trace_ids = {
        q1.provenance.trace_id,
        q2.provenance.trace_id,
        q3.provenance.trace_id,
    }
    assert len(trace_ids) == 3


def test_typed_value_distinct_inputs_distinct_trace_ids() -> None:
    v1 = typed_value("alpha")
    v2 = typed_value("beta")
    v3 = typed_value(None)
    trace_ids = {
        v1.provenance.trace_id,
        v2.provenance.trace_id,
        v3.provenance.trace_id,
    }
    assert len(trace_ids) == 3


def test_typed_collection_distinct_inputs_distinct_trace_ids() -> None:
    c1 = typed_collection([1, 2, 3])
    c2 = typed_collection([1, 2, 4])
    c3 = typed_collection([])
    trace_ids = {
        c1.provenance.trace_id,
        c2.provenance.trace_id,
        c3.provenance.trace_id,
    }
    assert len(trace_ids) == 3


def test_primitive_inputs_populated_in_provenance() -> None:
    """Verify inputs field carries the expected scalar inputs after primitive call."""
    r = projective_ratio(7, 3)
    assert r.provenance.inputs == (7, 3)

    q = stratified_quadratic_roots(1.0, -3.0, 2.0)
    assert q.provenance.inputs == (1.0, -3.0, 2.0)

    v = typed_value("hello")
    assert v.provenance.inputs == ("hello",)


def test_internal_operations_leave_inputs_empty() -> None:
    """Composite/internal operations rely on parents to encode path; inputs is empty."""
    from lloyd_v4.primitives.projective_ratio import scalarize_projective_ratio
    from lloyd_v4.primitives.stratified_quadratic_roots import select_quadratic_root

    r = projective_ratio(3, 4)
    s = scalarize_projective_ratio(r)
    assert s.provenance.inputs == ()
    assert s.provenance.parents == (r.provenance.trace_id,)

    q = stratified_quadratic_roots(1, -3, 2)
    selected = select_quadratic_root(q, "minus")
    assert selected.provenance.inputs == ()
    # parents on a successful selection contains: root_state, ratio, scalar
    assert q.provenance.trace_id in selected.provenance.parents


def test_trace_id_remains_in_serialization_round_trip() -> None:
    """Existing serialization invariant must hold."""
    import json
    r = projective_ratio(1, 2)
    payload = to_json_safe(r)
    encoded = json.dumps(payload, allow_nan=False)
    decoded = json.loads(encoded)
    assert decoded["provenance"]["trace_id"] == r.provenance.trace_id
    assert decoded["provenance"]["inputs"] == [1, 2]
```

## Audit invariants that should hold post-change

These should pass automatically without modification — the test logic is unchanged,
but the underlying structure becomes rigorous:

- `tests/test_task010c_no_chain_cycles.py::test_runtime_lineage_chains_have_no_cycles`
- `tests/test_task010c_lineage_terminates_in_primitive.py::test_lineage_terminals_are_calibrated_primitives`
- `tests/test_task010c_no_unregistered_operations.py::test_runtime_operation_ids_are_registered_in_manifest_and_source`

After the change, `build_trace_id_index` should no longer experience silent
overwrites because primitives with different inputs now produce different trace_ids.
This isn't asserted by the existing tests but can optionally be verified with a
new audit:

```python
def test_runtime_trace_ids_are_unique_per_observation() -> None:
    """Sanity: post-fix, no two distinct TypedResults share a trace_id."""
    from _audit_helpers.lineage import collected_instances
    instances = collected_instances()
    by_trace_id: dict[str, list] = {}
    for instance in instances:
        by_trace_id.setdefault(instance.provenance.trace_id, []).append(instance)
    collisions = {tid: items for tid, items in by_trace_id.items() if len(items) > 1}
    # Allow content-addressed collisions (same inputs+operation+parents): if so,
    # the colliding instances are by definition the same observation.
    spurious_collisions = {}
    for tid, items in collisions.items():
        first = items[0]
        for other in items[1:]:
            if (other.provenance.inputs != first.provenance.inputs
                or other.provenance.operation_id != first.provenance.operation_id
                or other.provenance.parents != first.provenance.parents):
                spurious_collisions[tid] = items
                break
    assert not spurious_collisions, (
        f"distinct observations share trace_id: "
        f"{[(tid, len(items)) for tid, items in spurious_collisions.items()]}"
    )
```

This audit is OPTIONAL for Task 011. It documents the invariant but doesn't gate
acceptance. Suggest adding it as `tests/test_task011_runtime_trace_id_uniqueness.py`.

## Validation checklist

Before marking the task complete:

- [ ] Pre-task evidence reproduces (three identical trace_ids on `projective_ratio(1,2)`, `(2,4)`, `(50,100)`)
- [ ] Provenance dataclass has the new `inputs` field with default `()`
- [ ] `_derive_trace_id` includes `inputs` in hash payload
- [ ] `to_json_safe` surfaces `inputs` in serialized output
- [ ] All four calibrated primitives populate `inputs` correctly
- [ ] Internal operations (`scalarize_projective_ratio`, `select_quadratic_root`) keep `inputs=()` and rely on `parents`
- [ ] Post-task: the three trace_ids in pre-task evidence are now distinct
- [ ] All new `test_task011_*` tests pass
- [ ] All existing tests continue to pass (no regressions)
- [ ] `pytest -x tests/` runs clean

## Open implementation decisions

These should be resolved during implementation rather than presupposed in the spec:

1. **Signed-zero handling.** `+0.0` and `-0.0` are different float bit patterns
   that JSON serializes differently (`"0.0"` vs `"-0.0"`). With this change,
   `projective_ratio(0.0, 1)` and `projective_ratio(-0.0, 1)` will get different
   trace_ids despite both being SIGNED_ZERO stratum. Decision: keep them distinct
   (the path differs at the bit level), and surface this as a known property of
   content-addressing. Document in the task summary, no code change.

2. **NaN inputs.** `projective_ratio` doesn't currently reject NaN inputs at the
   primitive level. If a NaN reaches `_derive_trace_id`, `json.dumps(allow_nan=False)`
   will raise. This is fail-loud behaviour consistent with V4's no-silent-corrections
   principle. Decision: accept the fail-loud as correct, document as a side-effect of
   the change. If primitives should reject NaN before construction, that's a separate
   task on input validation.

3. **`measurement_resolution` interaction.** `measurement_resolution: Any | None`
   already participates in the trace_id hash. Confirming that `inputs` and
   `measurement_resolution` are orthogonal (one captures the call's arguments,
   the other captures observation-policy metadata) — they should be.

## Subsequent tasks (forward references, not part of 011)

- **Task 012** — Validity honesty under overflow (Stress Test Finding 2). Prevent
  scalarize_projective_ratio from returning `value=inf` with `validity.finite=True`.
- **Task 013** — Conditioning honesty (Stress Test Findings 3, 6). Make `Conditioning`
  observe numerical regimes (proximity to overflow, cancellation magnitude, near-degeneracy)
  rather than acting as a stratum tag.

## Notes on discipline

- This task is a substrate fix. It derives entirely from V4's own surface (the
  bug was found by running V4 against its own primitives) plus theorem-derived
  constraint (Axiom 5). No V3 reference required.
- The change does not import from V3, does not assume V3-shaped consumers will
  exist, and does not pre-build for hypothetical future layers. It fixes a present
  inconsistency between V4's behaviour and V4's axioms.
- Task 010G (Synthesis Protocol formalisation) remains a forward reference and
  is not gated by Task 011.
