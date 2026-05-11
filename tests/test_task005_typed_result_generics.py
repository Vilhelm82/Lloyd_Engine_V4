from typing import get_args, get_origin

from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import MetrologyStatus, ProjectionStatus, ProjectiveRatioStatus, QuadraticRootStatus
from lloyd_v4.metrology import (
    LimitOfDetectionResult,
    LimitOfDetectionValue,
    NoiseFloorResult,
    NoiseFloorValue,
    ProxyCalibrationResult,
    ProxyCalibrationValue,
)
from lloyd_v4.primitives.projective_ratio import ProjectiveRatioResult, ProjectiveRatioValue, projective_ratio
from lloyd_v4.primitives.stratified_quadratic_roots import (
    QuadraticRootStateResult,
    StratifiedQuadraticRootValue,
)
from lloyd_v4.projection.exact_projection import ProjectionResultV4, ProjectionResultValue


def test_typed_result_is_parameterizable_and_existing_construction_still_serializes() -> None:
    parameterized = TypedResult[ProjectiveRatioValue, ProjectiveRatioStatus]
    result = projective_ratio(1, 2)
    payload = to_json_safe(result)

    assert get_origin(parameterized) is TypedResult
    assert payload["status"] == "finite_ratio"
    assert "__orig_class__" not in payload
    assert "TypeVar" not in str(payload)


def test_family_specific_aliases_are_parameterized() -> None:
    assert get_origin(ProjectiveRatioResult) is TypedResult
    assert get_args(ProjectiveRatioResult) == (ProjectiveRatioValue, ProjectiveRatioStatus)

    assert get_origin(QuadraticRootStateResult) is TypedResult
    assert get_args(QuadraticRootStateResult) == (StratifiedQuadraticRootValue, QuadraticRootStatus)

    assert get_origin(ProjectionResultV4) is TypedResult
    assert get_args(ProjectionResultV4) == (ProjectionResultValue, ProjectionStatus)

    assert get_origin(NoiseFloorResult) is TypedResult
    assert get_args(NoiseFloorResult) == (NoiseFloorValue, MetrologyStatus)

    assert get_origin(LimitOfDetectionResult) is TypedResult
    assert get_args(LimitOfDetectionResult) == (LimitOfDetectionValue, MetrologyStatus)

    assert get_origin(ProxyCalibrationResult) is TypedResult
    assert get_args(ProxyCalibrationResult) == (ProxyCalibrationValue, MetrologyStatus)
