from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.core.status import BranchFingerprintStatus, ConditioningStatus, MetrologyStatus, ProtocolStatus
from lloyd_v4.core.transitions import StatusTransitionRule
from lloyd_v4.core.validity import Validity
from lloyd_v4.primitives.projective_ratio import projective_ratio, scalarize_projective_ratio


SLOPE_FLOW_STATUSES = frozenset(
    {
        BranchFingerprintStatus.SLOPE_FLOW_OBSERVED,
        BranchFingerprintStatus.SLOPE_MODEL_RESIDUALS,
        BranchFingerprintStatus.SLOPE_MODEL_UNIQUE_MATCH,
        BranchFingerprintStatus.SLOPE_MODEL_AMBIGUOUS,
        BranchFingerprintStatus.SLOPE_MODEL_NO_MATCH,
        BranchFingerprintStatus.SLOPE_FLOW_INSUFFICIENT_SAMPLES,
        BranchFingerprintStatus.SLOPE_FLOW_INDETERMINATE,
        BranchFingerprintStatus.SLOPE_FLOW_PROXY_UNCALIBRATED,
    }
)

SLOPE_FLOW_COMPARISON_PROTOCOL = ProducerProtocol(
    name="slope_flow_comparison",
    emitted_statuses=SLOPE_FLOW_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
)

SLOPE_FLOW_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="slope_flow_consumer",
    accepted_statuses=SLOPE_FLOW_STATUSES,
    required_validity_fields=frozenset({"observable"}),
)

SLOPE_FLOW_MODEL_COMPARISON_TRANSITION_RULE = StatusTransitionRule(
    rule_id="branch.slope_flow.model_comparison",
    input_status_family=BranchFingerprintStatus,
    output_status_family=BranchFingerprintStatus,
    input_protocol_id=SLOPE_FLOW_COMPARISON_PROTOCOL.name,
    output_protocol_id=SLOPE_FLOW_CONSUMER_PROTOCOL.name,
    accepted_input_statuses=frozenset(
        {
            BranchFingerprintStatus.SLOPE_FLOW_OBSERVED,
            BranchFingerprintStatus.SLOPE_MODEL_RESIDUALS,
            BranchFingerprintStatus.SLOPE_MODEL_UNIQUE_MATCH,
            BranchFingerprintStatus.SLOPE_MODEL_AMBIGUOUS,
            BranchFingerprintStatus.SLOPE_MODEL_NO_MATCH,
        }
    ),
    refused_input_statuses=frozenset(
        {
            BranchFingerprintStatus.SLOPE_FLOW_INSUFFICIENT_SAMPLES,
            BranchFingerprintStatus.SLOPE_FLOW_INDETERMINATE,
            BranchFingerprintStatus.SLOPE_FLOW_PROXY_UNCALIBRATED,
        }
    ),
    mapped_statuses={},
    description="Classifies slope-flow comparison evidence for fingerprint composition.",
    emitted_input_statuses=SLOPE_FLOW_STATUSES,
)


@dataclass(frozen=True, slots=True)
class SlopeFlowSample:
    control: int | float
    observable: int | float
    source_trace_id: str | None = None
    detection_trace_id: str | None = None
    detection_status: str | None = None

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "control": to_json_safe(self.control),
            "observable": to_json_safe(self.observable),
            "source_trace_id": self.source_trace_id,
            "detection_trace_id": self.detection_trace_id,
            "detection_status": self.detection_status,
        }


@dataclass(frozen=True, slots=True)
class SlopeFlowModel:
    name: str
    expected_slope: int | float

    def to_json_safe(self) -> dict[str, Any]:
        return {"name": self.name, "expected_slope": to_json_safe(self.expected_slope)}


@dataclass(frozen=True, slots=True)
class SlopeSegmentEvidence:
    left_index: int
    right_index: int
    delta_log_control: float
    delta_log_observable: float
    projective_slope_trace_id: str
    scalar_slope_trace_id: str | None
    slope: float | None
    refusal_reason: str | None

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "left_index": self.left_index,
            "right_index": self.right_index,
            "delta_log_control": to_json_safe(self.delta_log_control),
            "delta_log_observable": to_json_safe(self.delta_log_observable),
            "projective_slope_trace_id": self.projective_slope_trace_id,
            "scalar_slope_trace_id": self.scalar_slope_trace_id,
            "slope": to_json_safe(self.slope),
            "refusal_reason": self.refusal_reason,
        }


@dataclass(frozen=True, slots=True)
class SlopeModelResidual:
    model_name: str
    expected_slope: float
    segment_residuals: tuple[float, ...]
    max_abs_segment_residual: float | None
    within_declared_band: bool | None

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "expected_slope": to_json_safe(self.expected_slope),
            "segment_residuals": to_json_safe(self.segment_residuals),
            "max_abs_segment_residual": to_json_safe(self.max_abs_segment_residual),
            "within_declared_band": self.within_declared_band,
        }


@dataclass(frozen=True, slots=True)
class SlopeFlowComparisonValue:
    samples: tuple[SlopeFlowSample, ...]
    usable_sample_indices: tuple[int, ...]
    segment_evidence: tuple[SlopeSegmentEvidence, ...]
    models: tuple[SlopeFlowModel, ...]
    model_residuals: tuple[SlopeModelResidual, ...]
    declared_model_band: float | None
    selected_model_name: str | None
    comparison_kind: str
    source_trace_ids: tuple[str, ...]

    def to_json_safe(self) -> dict[str, Any]:
        return {
            "samples": [sample.to_json_safe() for sample in self.samples],
            "usable_sample_indices": list(self.usable_sample_indices),
            "segment_evidence": [segment.to_json_safe() for segment in self.segment_evidence],
            "models": [model.to_json_safe() for model in self.models],
            "model_residuals": [residual.to_json_safe() for residual in self.model_residuals],
            "declared_model_band": to_json_safe(self.declared_model_band),
            "selected_model_name": self.selected_model_name,
            "comparison_kind": self.comparison_kind,
            "source_trace_ids": list(self.source_trace_ids),
        }


SlopeFlowComparisonResult = TypedResult[SlopeFlowComparisonValue, BranchFingerprintStatus]


def compare_slope_flow_to_models(
    samples: Sequence[SlopeFlowSample],
    models: Sequence[SlopeFlowModel] = (),
    *,
    declared_model_band: float | None = None,
    comparison_kind: str = "direct_transfer",
) -> TypedResult:
    band = _optional_nonnegative(declared_model_band, "declared_model_band")
    sample_tuple = tuple(_validate_sample(sample) for sample in samples)
    model_tuple = tuple(_validate_model(model) for model in models)
    usable = tuple(index for index, sample in enumerate(sample_tuple) if _is_loggable(sample))
    source_trace_ids = tuple(sample.source_trace_id for sample in sample_tuple if sample.source_trace_id is not None)

    if len(usable) < 2:
        return _slope_result(
            sample_tuple,
            usable,
            (),
            model_tuple,
            (),
            band,
            None,
            comparison_kind,
            source_trace_ids,
            BranchFingerprintStatus.SLOPE_FLOW_INSUFFICIENT_SAMPLES,
        )

    segments = tuple(_segment(sample_tuple, left, right) for left, right in zip(usable, usable[1:]))
    if any(segment.slope is None for segment in segments):
        return _slope_result(
            sample_tuple,
            usable,
            segments,
            model_tuple,
            (),
            band,
            None,
            comparison_kind,
            source_trace_ids,
            BranchFingerprintStatus.SLOPE_FLOW_INDETERMINATE,
        )

    residuals = tuple(_residual(model, segments, band) for model in model_tuple)
    selected = None
    if not model_tuple:
        status = BranchFingerprintStatus.SLOPE_FLOW_OBSERVED
    elif band is None:
        status = BranchFingerprintStatus.SLOPE_MODEL_RESIDUALS
    else:
        inside = [residual.model_name for residual in residuals if residual.within_declared_band]
        if len(inside) == 1:
            status = BranchFingerprintStatus.SLOPE_MODEL_UNIQUE_MATCH
            selected = inside[0]
        elif len(inside) > 1:
            status = BranchFingerprintStatus.SLOPE_MODEL_AMBIGUOUS
        else:
            status = BranchFingerprintStatus.SLOPE_MODEL_NO_MATCH
    return _slope_result(
        sample_tuple,
        usable,
        segments,
        model_tuple,
        residuals,
        band,
        selected,
        comparison_kind,
        source_trace_ids,
        status,
    )


def _segment(samples: tuple[SlopeFlowSample, ...], left_index: int, right_index: int) -> SlopeSegmentEvidence:
    left = samples[left_index]
    right = samples[right_index]
    delta_control = math.log(right.control) - math.log(left.control)
    delta_observable = math.log(abs(right.observable)) - math.log(abs(left.observable))
    ratio = projective_ratio(delta_observable, delta_control)
    scalar = scalarize_projective_ratio(ratio)
    return SlopeSegmentEvidence(
        left_index=left_index,
        right_index=right_index,
        delta_log_control=delta_control,
        delta_log_observable=delta_observable,
        projective_slope_trace_id=ratio.provenance.trace_id,
        scalar_slope_trace_id=None if scalar.refusal is not None else scalar.provenance.trace_id,
        slope=None if scalar.refusal is not None else scalar.value,
        refusal_reason=None if scalar.refusal is None else scalar.refusal.reason,
    )


def _residual(model: SlopeFlowModel, segments: tuple[SlopeSegmentEvidence, ...], band: float | None) -> SlopeModelResidual:
    residuals = tuple(segment.slope - model.expected_slope for segment in segments if segment.slope is not None)
    max_abs = max(abs(value) for value in residuals) if residuals else None
    within = None if band is None or max_abs is None else max_abs <= band
    return SlopeModelResidual(model.name, float(model.expected_slope), residuals, max_abs, within)


def _slope_result(
    samples: tuple[SlopeFlowSample, ...],
    usable: tuple[int, ...],
    segments: tuple[SlopeSegmentEvidence, ...],
    models: tuple[SlopeFlowModel, ...],
    residuals: tuple[SlopeModelResidual, ...],
    band: float | None,
    selected: str | None,
    comparison_kind: str,
    source_trace_ids: tuple[str, ...],
    status: BranchFingerprintStatus,
) -> TypedResult:
    value = SlopeFlowComparisonValue(samples, usable, segments, models, residuals, band, selected, comparison_kind, source_trace_ids)
    return TypedResult(
        value=value,
        space="SlopeFlowComparison",
        status=status,
        validity=_validity(status),
        conditioning=_conditioning(status),
        provenance=Provenance(
            operation_id="compare_slope_flow_to_models",
            expression_path="log_magnitude_projective_slope_flow",
            parents=tuple(segment.projective_slope_trace_id for segment in segments) + source_trace_ids,
        ),
        protocol=ProtocolStatus.OK,
    )


def _is_loggable(sample: SlopeFlowSample) -> bool:
    return sample.control > 0 and sample.observable != 0 and sample.detection_status in {None, MetrologyStatus.DETECTED.value}


def _validate_sample(sample: SlopeFlowSample) -> SlopeFlowSample:
    if not isinstance(sample, SlopeFlowSample):
        raise ProtocolViolationError("slope-flow samples must be SlopeFlowSample objects")
    _positive(sample.control, "control")
    _finite(sample.observable, "observable")
    return sample


def _validate_model(model: SlopeFlowModel) -> SlopeFlowModel:
    if not isinstance(model, SlopeFlowModel):
        raise ProtocolViolationError("slope-flow models must be SlopeFlowModel objects")
    _finite(model.expected_slope, "expected_slope")
    return model


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        raise ProtocolViolationError(f"{name} must be a finite scalar")
    return float(value)


def _positive(value: Any, name: str) -> float:
    number = _finite(value, name)
    if number <= 0:
        raise ProtocolViolationError(f"{name} must be positive")
    return number


def _optional_nonnegative(value: Any | None, name: str) -> float | None:
    if value is None:
        return None
    number = _finite(value, name)
    if number < 0:
        raise ProtocolViolationError(f"{name} must be nonnegative")
    return number


def _validity(status: BranchFingerprintStatus) -> Validity:
    if status in {
        BranchFingerprintStatus.SLOPE_FLOW_OBSERVED,
        BranchFingerprintStatus.SLOPE_MODEL_RESIDUALS,
        BranchFingerprintStatus.SLOPE_MODEL_UNIQUE_MATCH,
    }:
        return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
    if status in {BranchFingerprintStatus.SLOPE_MODEL_AMBIGUOUS, BranchFingerprintStatus.SLOPE_MODEL_NO_MATCH}:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning(status: BranchFingerprintStatus) -> Conditioning:
    if status in {
        BranchFingerprintStatus.SLOPE_FLOW_OBSERVED,
        BranchFingerprintStatus.SLOPE_MODEL_RESIDUALS,
        BranchFingerprintStatus.SLOPE_MODEL_UNIQUE_MATCH,
    }:
        return Conditioning(status=ConditioningStatus.WELL_CONDITIONED)
    return Conditioning(status=ConditioningStatus.WARNING)
