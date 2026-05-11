import json

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.primitives import stratified_quadratic_roots
from lloyd_v4.projection import BranchSelection, branch_selection, exact_quadratic_projection


def _project(a, b, c, branch: BranchSelection):
    return exact_quadratic_projection(stratified_quadratic_roots(a, b, c), branch_selection(branch))


def test_successful_projection_serializes_without_flags_or_value_refusal() -> None:
    projection = _project(1, -3, 2, BranchSelection.MINUS)

    payload = to_json_safe(projection)
    encoded = json.dumps(payload, allow_nan=False)

    assert payload["status"] == "projection_transverse"
    assert payload["value"]["source_status"] == "two_real_roots"
    assert payload["value"]["requested_branch"] == "minus"
    assert payload["value"]["selected_branch"] == "minus"
    assert payload["value"]["selected_root_value"] == 1.0
    assert "flags" not in payload["value"]
    assert "refusal" not in payload["value"]
    assert "NaN" not in encoded
    assert "Infinity" not in encoded


def test_selection_refusal_serializes_canonical_typed_result_refusal() -> None:
    projection = _project(1, -3, 2, BranchSelection.LINEAR)

    payload = to_json_safe(projection)

    assert payload["status"] == "projection_selection_refused"
    assert payload["value"]["requested_branch"] == "linear"
    assert "refusal" not in payload["value"]
    assert payload["refusal"]["details"]["branch"] == "linear"
