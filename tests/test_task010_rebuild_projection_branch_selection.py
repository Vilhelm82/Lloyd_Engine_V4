import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import validate_protocol
from lloyd_v4.core.status import ValueStatus
from lloyd_v4.projection import (
    BRANCH_SELECTION_CONSUMER_PROTOCOL,
    BRANCH_SELECTION_PROTOCOL,
    BranchSelection,
    BranchSelectionValue,
    branch_selection,
)


def test_branch_selection_wraps_enum_as_typed_value_composite() -> None:
    result = branch_selection(BranchSelection.MINUS)

    assert result.status is ValueStatus.VALUE_OBSERVED
    assert result.value == BranchSelectionValue(branch=BranchSelection.MINUS)
    assert result.space == "BranchSelection"
    assert result.validity.selectable is True
    assert result.provenance.operation_id == "branch_selection"
    assert result.provenance.expression_path == "branch_selection_construction"
    assert len(result.provenance.parents) == 1


def test_branch_selection_rejects_raw_string_programmer_error() -> None:
    with pytest.raises(ProtocolViolationError):
        branch_selection("minus")


def test_branch_selection_protocols_are_value_status_protocols() -> None:
    result = branch_selection(BranchSelection.LINEAR)
    check = validate_protocol(result, BRANCH_SELECTION_CONSUMER_PROTOCOL)

    assert BRANCH_SELECTION_PROTOCOL.status_family is ValueStatus
    assert BRANCH_SELECTION_CONSUMER_PROTOCOL.status_family is ValueStatus
    assert check.ok is True
    assert result.value.to_json_safe() == {"branch": "linear"}
