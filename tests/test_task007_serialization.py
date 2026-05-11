import json
from dataclasses import replace

from lloyd_v4.core.status import RefineryStatus
from lloyd_v4.primitives.projective_ratio import projective_ratio
from lloyd_v4.refinery import evaluate_rewrite_candidate, require_accepted_rewrite, snapshot_typed_result


def test_refinery_decision_result_serializes_required_evidence() -> None:
    reference = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    candidate = replace(reference, label="candidate", expression_path="rewritten_path")

    result = evaluate_rewrite_candidate([reference], [candidate], candidate_name="candidate")
    payload = result.to_json_safe()

    assert payload["status"] == RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT.value
    assert payload["value"]["reference_name"] == "reference"
    assert payload["value"]["candidate_name"] == "candidate"
    assert payload["value"]["scenario_comparisons"][0]["scenario_id"] == "s"
    assert payload["value"]["scenario_comparisons"][0]["reference_snapshot"]["expression_path"] != payload["value"]["scenario_comparisons"][0]["candidate_snapshot"]["expression_path"]
    assert "aggregate_reference_slag" in payload["value"]
    assert "componentwise_comparison" in payload["value"]
    assert payload["provenance"]["parents"]
    json.dumps(payload, allow_nan=False)


def test_refinery_refusal_serializes_without_sentinels_or_callables() -> None:
    reference = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    result = evaluate_rewrite_candidate([reference], [replace(reference, label="candidate")], candidate_name="candidate")
    refused = require_accepted_rewrite(result).to_json_safe()
    encoded = json.dumps(refused, allow_nan=False)

    assert refused["protocol"] == "scalarization_refused"
    assert "callable" not in encoded
    assert "nonfinite_float" not in encoded
