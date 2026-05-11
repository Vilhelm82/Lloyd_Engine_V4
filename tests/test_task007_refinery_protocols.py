from dataclasses import replace

from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.status import ProjectiveRatioStatus, ProtocolStatus, RefineryStatus
from lloyd_v4.primitives.projective_ratio import projective_ratio
from lloyd_v4.refinery import (
    REFINERY_ACCEPTED_REWRITE_PROTOCOL,
    REFINERY_DECISION_PROTOCOL,
    RefineryDecisionValue,
    RefineryScenarioComparison,
    compare_refinery_scenario,
    evaluate_rewrite_candidate,
    require_accepted_rewrite,
    snapshot_typed_result,
)


def _decision(status: RefineryStatus):
    snapshot = snapshot_typed_result(projective_ratio(1, 2), label="reference", scenario_id="s")
    comparison = compare_refinery_scenario(snapshot, replace(snapshot, label="candidate"))
    result = evaluate_rewrite_candidate([snapshot], [replace(snapshot, label="candidate")], candidate_name="candidate")
    return replace(
        result,
        status=status,
        value=replace(result.value, accepted=status is RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG),
    )


def test_refinery_decision_protocol_is_status_family_aware() -> None:
    result = _decision(RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT)
    wrong_family = replace(result, status=ProjectiveRatioStatus.FINITE_RATIO)

    assert validate_protocol(result, REFINERY_DECISION_PROTOCOL).ok is True
    assert validate_protocol(wrong_family, REFINERY_DECISION_PROTOCOL).ok is False


def test_accepted_rewrite_protocol_accepts_only_accepted_status() -> None:
    accepted = _decision(RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG)
    equivalent = _decision(RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT)

    assert validate_protocol(accepted, REFINERY_ACCEPTED_REWRITE_PROTOCOL).ok is True
    assert validate_protocol(equivalent, REFINERY_ACCEPTED_REWRITE_PROTOCOL).ok is False


def test_require_accepted_rewrite_returns_typed_refusal_for_nonaccepted_statuses() -> None:
    for status in RefineryStatus:
        result = require_accepted_rewrite(_decision(status))
        if status is RefineryStatus.REWRITE_ACCEPTED_SAME_GEOMETRY_LOWER_SLAG:
            assert result.protocol is ProtocolStatus.OK
            assert result.refusal is None
        else:
            assert result.protocol is ProtocolStatus.SCALARIZATION_REFUSED
            assert result.refusal is not None


def test_require_accepted_rewrite_fails_wrong_family_explicitly() -> None:
    wrong_family = replace(_decision(RefineryStatus.REWRITE_EQUIVALENT_NO_IMPROVEMENT), status=ProjectiveRatioStatus.FINITE_RATIO)

    result = require_accepted_rewrite(wrong_family)

    assert result.protocol is ProtocolStatus.SCALARIZATION_REFUSED
    assert "status family mismatch" in result.refusal.reason
