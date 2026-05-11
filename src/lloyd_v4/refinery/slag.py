from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import BranchFingerprintStatus, ConditioningStatus, MetrologyStatus, ProjectionStatus, RefineryStatus
from lloyd_v4.refinery.observations import TypedResultSnapshot


DEFAULT_SLAG_DIMENSIONS = (
    "warning_count",
    "refusal_count",
    "indeterminate_count",
    "incomplete_count",
    "uncalibrated_count",
    "unstable_count",
    "max_model_residual",
    "max_kq_slope_abs",
)


@dataclass(frozen=True, slots=True)
class SlagVector:
    components: dict[str, int | float]
    unavailable_dimensions: tuple[str, ...] = ()

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "components": to_json_safe(self.components),
            "unavailable_dimensions": list(self.unavailable_dimensions),
        }


@dataclass(frozen=True, slots=True)
class SlagComparison:
    reference: SlagVector
    candidate: SlagVector
    componentwise: dict[str, str]
    lower_dimensions: tuple[str, ...]
    regressed_dimensions: tuple[str, ...]
    unavailable_dimensions: tuple[str, ...]

    @property
    def no_worse(self) -> bool:
        return not self.regressed_dimensions

    @property
    def strictly_lower(self) -> bool:
        return bool(self.lower_dimensions)

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "reference": self.reference.to_json_safe(),
            "candidate": self.candidate.to_json_safe(),
            "componentwise": self.componentwise,
            "lower_dimensions": list(self.lower_dimensions),
            "regressed_dimensions": list(self.regressed_dimensions),
            "unavailable_dimensions": list(self.unavailable_dimensions),
        }


def compute_slag_vector(
    snapshot: TypedResultSnapshot,
    *,
    declared_dimensions: Sequence[str] | None = None,
) -> SlagVector:
    requested = tuple(declared_dimensions) if declared_dimensions is not None else DEFAULT_SLAG_DIMENSIONS
    available = _available_components(snapshot)
    components = {name: available[name] for name in requested if name in available}
    unavailable = tuple(name for name in requested if name not in available)
    return SlagVector(components=components, unavailable_dimensions=unavailable)


def compare_slag_vectors(reference: SlagVector, candidate: SlagVector) -> SlagComparison:
    common = sorted(set(reference.components) & set(candidate.components))
    unavailable = tuple(sorted(set(reference.unavailable_dimensions) | set(candidate.unavailable_dimensions)))
    componentwise: dict[str, str] = {}
    lower: list[str] = []
    regressed: list[str] = []
    for name in common:
        reference_value = reference.components[name]
        candidate_value = candidate.components[name]
        if candidate_value < reference_value:
            componentwise[name] = "lower"
            lower.append(name)
        elif candidate_value > reference_value:
            componentwise[name] = "regressed"
            regressed.append(name)
        else:
            componentwise[name] = "equal"
    return SlagComparison(
        reference=reference,
        candidate=candidate,
        componentwise=componentwise,
        lower_dimensions=tuple(lower),
        regressed_dimensions=tuple(regressed),
        unavailable_dimensions=unavailable,
    )


def aggregate_slag_vectors(vectors: Sequence[SlagVector]) -> SlagVector:
    totals: dict[str, int | float] = {}
    unavailable: set[str] = set()
    for vector in vectors:
        unavailable.update(vector.unavailable_dimensions)
        for name, value in vector.components.items():
            totals[name] = totals.get(name, 0) + value
    return SlagVector(components=totals, unavailable_dimensions=tuple(sorted(unavailable)))


def _available_components(snapshot: TypedResultSnapshot) -> dict[str, int | float]:
    status = snapshot.status
    fingerprint = snapshot.value_fingerprint
    components: dict[str, int | float] = {
        "warning_count": 1 if snapshot.conditioning.get("status") == ConditioningStatus.WARNING.value else 0,
        "refusal_count": 1 if _is_refusal(snapshot) else 0,
        "indeterminate_count": 1 if _is_indeterminate(status) else 0,
        "incomplete_count": 1 if _is_incomplete(status) else 0,
        "uncalibrated_count": 1 if _is_uncalibrated(status) else 0,
        "unstable_count": 1 if _is_unstable(status) else 0,
    }
    residual = fingerprint.get("max_model_residual")
    if isinstance(residual, int | float):
        components["max_model_residual"] = float(residual)
    kq = fingerprint.get("max_kq_slope_abs")
    if isinstance(kq, int | float):
        components["max_kq_slope_abs"] = float(kq)
    return components


def _is_refusal(snapshot: TypedResultSnapshot) -> bool:
    if snapshot.status == ProjectionStatus.PROJECTION_SELECTION_REFUSED.value:
        return True
    return snapshot.protocol_identity.endswith("refusal")


def _is_indeterminate(status: str) -> bool:
    return status in {
        ProjectiveLike.INDETERMINATE,
        MetrologyStatus.INDETERMINATE.value,
        MetrologyStatus.NOISE_FLOOR_INDETERMINATE.value,
        MetrologyStatus.DETECTION_INDETERMINATE.value,
        MetrologyStatus.CALIBRATION_INDETERMINATE.value,
        BranchFingerprintStatus.SLOPE_FLOW_INDETERMINATE.value,
        BranchFingerprintStatus.KQ_FLOW_INDETERMINATE.value,
        RefineryStatus.REWRITE_INDETERMINATE_INSUFFICIENT_EVIDENCE.value,
        RefineryStatus.REWRITE_INDETERMINATE_UNHANDLED_STATUS.value,
    }


def _is_incomplete(status: str) -> bool:
    return status in {
        BranchFingerprintStatus.SLOPE_FLOW_INSUFFICIENT_SAMPLES.value,
        BranchFingerprintStatus.FINGERPRINT_INCOMPLETE.value,
    }


def _is_uncalibrated(status: str) -> bool:
    return status in {
        MetrologyStatus.UNCALIBRATED_PROXY.value,
        MetrologyStatus.PROXY_UNCALIBRATED.value,
        BranchFingerprintStatus.SLOPE_FLOW_PROXY_UNCALIBRATED.value,
        BranchFingerprintStatus.KQ_FLOW_UNCALIBRATED.value,
        BranchFingerprintStatus.FINGERPRINT_PROXY_UNCALIBRATED.value,
    }


def _is_unstable(status: str) -> bool:
    return status == BranchFingerprintStatus.KQ_FLOW_UNSTABLE.value


class ProjectiveLike:
    INDETERMINATE = "indeterminate"
