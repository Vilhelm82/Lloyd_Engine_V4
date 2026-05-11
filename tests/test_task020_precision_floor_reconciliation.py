"""Task 020: Precision floor reconciliation regression tests.

Locks the precision_floor value and its derivation rationale. If a
future task wants to change the floor, this test forces explicit
acknowledgment that 2u (cancellation threshold of the subtraction) is
distinct from u (per-operand unit roundoff).
"""

import math
import sys

import pytest

from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.status import TransferStatus
from lloyd_v4.primitives.typed_finite_difference import _precision_floor, typed_finite_difference


class TestPrecisionFloorReconciliation:
    """Lock the precision floor value and its derivation rationale."""

    def test_raw_python_precision_floor_is_two_u(self) -> None:
        """The floor is 2u, not the per-operand unit roundoff u."""
        u = 2.0**-53
        floor = _precision_floor("raw_python")

        assert floor == 2.0 * u
        assert floor == 2.0**-52

    def test_raw_python_precision_floor_equals_machine_epsilon(self) -> None:
        """2u for double also equals sys.float_info.epsilon."""
        assert _precision_floor("raw_python") == sys.float_info.epsilon

    def test_raw_python_precision_floor_is_not_unit_roundoff(self) -> None:
        """The floor must not silently collapse to the per-operand u."""
        unit_roundoff = 2.0**-53
        floor = _precision_floor("raw_python")

        assert floor != unit_roundoff
        assert floor == 2.0 * unit_roundoff

    def test_unsupported_precision_raises(self) -> None:
        """No silent fallback for unsupported precisions."""
        with pytest.raises(ProtocolViolationError):
            _precision_floor("float32")
        with pytest.raises(ProtocolViolationError):
            _precision_floor("mpmath")
        with pytest.raises(ProtocolViolationError):
            _precision_floor("")

    def test_precision_floor_does_not_alter_observation_values(self) -> None:
        """Cancellation classification is status-only, not a value rescue."""
        result = typed_finite_difference(
            lambda x: 1.0 + 1e-20 * x,
            1.0,
            1e-3,
            function_label="near_constant_for_floor_check",
        )

        assert result.status is TransferStatus.TRANSFER_CANCELLATION_DOMINATED
        assert result.value.transfer is not None
        assert math.isfinite(result.value.transfer)
        assert result.value.delta_g is not None
        assert math.isfinite(result.value.delta_g)
        assert result.value.g_at_f is not None
        assert result.value.g_at_f_plus_delta is not None
        assert result.value.cancellation_ratio is not None
        assert result.value.cancellation_ratio < _precision_floor("raw_python")
        assert result.validity.selectable is False
        assert result.validity.advanceable is False
        assert result.validity.observable is True
