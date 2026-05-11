import json

from lloyd_v4.branch import SlopeFlowModel, SlopeFlowSample, build_branch_fingerprint, compare_kq_slope_stability, compare_slope_flow_to_models
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.metrology import calibrate_proxy_kq
from lloyd_v4.primitives.stratified_quadratic_roots import stratified_quadratic_roots
from _projection_branch import project_with_branch


def test_branch_outputs_serialize_without_numeric_sentinels() -> None:
    flow = compare_slope_flow_to_models(
        [SlopeFlowSample(1.0, 1.0), SlopeFlowSample(2.0, 4.0)],
        [SlopeFlowModel("square", 2.0)],
        declared_model_band=0.1,
    )
    kq = compare_kq_slope_stability(
        [1.0, 2.0],
        [calibrate_proxy_kq(2.0, 1.0), calibrate_proxy_kq(4.0, 2.0)],
        declared_stability_band=0.01,
    )
    projection = project_with_branch(stratified_quadratic_roots(1, -3, 2), "minus")
    fingerprint = build_branch_fingerprint(projection, flow, observable_kind="proxy", kq_flow_result=kq)

    for result in [flow, kq, fingerprint]:
        payload = to_json_safe(result)
        encoded = json.dumps(payload, allow_nan=False)
        assert "NaN" not in encoded
        assert "Infinity" not in encoded

    fingerprint_payload = to_json_safe(fingerprint)
    assert "projection_flags" not in fingerprint_payload["value"]
    assert fingerprint_payload["value"]["transfer_flow_status"] == "slope_model_unique_match"
    assert fingerprint_payload["value"]["kq_flow_status"] == "kq_flow_stable"
    assert projection.provenance.trace_id in fingerprint_payload["provenance"]["parents"]
