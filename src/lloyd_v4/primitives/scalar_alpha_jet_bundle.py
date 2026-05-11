from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Sequence

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.status import AlphaProbeStatus, ConditioningStatus, ProtocolStatus, ScalarAlphaJetBundleStatus, TransferStatus
from lloyd_v4.core.validity import Validity
from lloyd_v4.primitives.directional_alpha_probe import AlphaProbeObservation, DeclaredAlphaModel, directional_alpha_probe
from lloyd_v4.primitives.typed_finite_difference import typed_finite_difference


SCALAR_ALPHA_JET_BUNDLE_SPACE = "ScalarAlphaJetBundleObservation"
SCALAR_ALPHA_JET_BUNDLE_STATUSES = frozenset(ScalarAlphaJetBundleStatus)
ACCEPTED_SCALAR_ALPHA_JET_BUNDLE_STATUSES = frozenset(
    {
        ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA,
        ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH,
        ScalarAlphaJetBundleStatus.SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY,
    }
)

SCALAR_ALPHA_JET_BUNDLE_PROTOCOL = ProducerProtocol(
    name="scalar_alpha_jet_bundle",
    emitted_statuses=SCALAR_ALPHA_JET_BUNDLE_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=ScalarAlphaJetBundleStatus,
)

SCALAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="scalar_alpha_jet_bundle_consumer",
    accepted_statuses=ACCEPTED_SCALAR_ALPHA_JET_BUNDLE_STATUSES,
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
    status_family=ScalarAlphaJetBundleStatus,
    refused_statuses=SCALAR_ALPHA_JET_BUNDLE_STATUSES - ACCEPTED_SCALAR_ALPHA_JET_BUNDLE_STATUSES,
)


@dataclass(frozen=True, slots=True)
class ScalarAlphaJetBundleObservation:
    point: float
    f_value: float | None
    probe_id: str
    function_label: str
    h_values: tuple[float, ...]
    eta: float
    alpha_probe_observation: AlphaProbeObservation | None
    alpha_probe_trace_id: str | None
    transfer_trace_ids: tuple[str, ...]
    slope_trace_id: str | None
    observed_slope: float | None
    observed_alpha: float | None
    alpha_status: AlphaProbeStatus | None
    derivative_at_point: float | None
    derivative_h: float | None
    derivative_transfer_trace_id: str | None
    declared_alpha_models: tuple[DeclaredAlphaModel, ...]
    declared_alpha_band: float | None
    selected_alpha_model: str | None
    matching_alpha_model_names: tuple[str, ...]
    expression_path: str

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe

        return {
            "point": self.point,
            "f_value": to_json_safe(self.f_value),
            "probe_id": self.probe_id,
            "function_label": self.function_label,
            "h_values": list(self.h_values),
            "eta": self.eta,
            "alpha_probe_observation": to_json_safe(self.alpha_probe_observation),
            "alpha_probe_trace_id": self.alpha_probe_trace_id,
            "transfer_trace_ids": list(self.transfer_trace_ids),
            "slope_trace_id": self.slope_trace_id,
            "observed_slope": to_json_safe(self.observed_slope),
            "observed_alpha": to_json_safe(self.observed_alpha),
            "alpha_status": self.alpha_status.value if self.alpha_status is not None else None,
            "derivative_at_point": to_json_safe(self.derivative_at_point),
            "derivative_h": to_json_safe(self.derivative_h),
            "derivative_transfer_trace_id": self.derivative_transfer_trace_id,
            "declared_alpha_models": [model.to_json_safe() for model in self.declared_alpha_models],
            "declared_alpha_band": to_json_safe(self.declared_alpha_band),
            "selected_alpha_model": self.selected_alpha_model,
            "matching_alpha_model_names": list(self.matching_alpha_model_names),
            "expression_path": self.expression_path,
        }


ScalarAlphaJetBundleResult = TypedResult[ScalarAlphaJetBundleObservation, ScalarAlphaJetBundleStatus]


def scalar_alpha_jet_bundle(
    func: Callable[[float], float],
    x0: float,
    h_values: Sequence[float],
    *,
    probe_id: str,
    function_label: str,
    eta: float = 1e-6,
    declared_alpha_models: Sequence[DeclaredAlphaModel] = (),
    declared_alpha_band: float | None = None,
    precision: str = "raw_python",
    backend: str = "python",
    device: str = "cpu",
    measurement_resolution: Any | None = None,
    expression_path: str = "scalar_alpha_jet_local_probe",
) -> ScalarAlphaJetBundleResult:
    """Package local alpha evidence around a scalar point x0."""

    point, h_tuple = _validate_inputs(func, x0, h_values, eta, probe_id, function_label, declared_alpha_models, declared_alpha_band)
    models = tuple(declared_alpha_models)

    try:
        raw_f_at_x0 = func(point)
    except Exception as exc:
        return _result(
            ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED,
            point,
            None,
            probe_id,
            function_label,
            h_tuple,
            eta,
            None,
            (),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            models,
            declared_alpha_band,
            None,
            (),
            expression_path,
            precision,
            backend,
            device,
            measurement_resolution,
            f"f(x0) raised {type(exc).__name__}",
        )

    if not _is_numeric(raw_f_at_x0):
        return _result(
            ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED,
            point,
            None,
            probe_id,
            function_label,
            h_tuple,
            eta,
            None,
            (),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            models,
            declared_alpha_band,
            None,
            (),
            expression_path,
            precision,
            backend,
            device,
            measurement_resolution,
            f"f(x0) returned {type(raw_f_at_x0).__name__}",
        )

    f_at_x0 = float(raw_f_at_x0)
    if not math.isfinite(f_at_x0):
        return _result(
            ScalarAlphaJetBundleStatus.SCALAR_JET_NONFINITE,
            point,
            f_at_x0,
            probe_id,
            function_label,
            h_tuple,
            eta,
            None,
            (),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            models,
            declared_alpha_band,
            None,
            (),
            expression_path,
            precision,
            backend,
            device,
            measurement_resolution,
            "f(x0) was nonfinite",
        )

    def g_local(h: float) -> float:
        return func(point + h) - f_at_x0

    embedded_probe_id = f"{probe_id}__x0_{point!r}"
    embedded_function_label = f"{function_label}__local_at_{point!r}"
    alpha_probe_result = directional_alpha_probe(
        g_local,
        h_tuple,
        probe_id=embedded_probe_id,
        function_label=embedded_function_label,
        eta=eta,
        declared_alpha_models=models,
        declared_alpha_band=declared_alpha_band,
        precision=precision,
        backend=backend,
        device=device,
        measurement_resolution=measurement_resolution,
        expression_path="log_log_slope_fit",
    )

    derivative_at_point = None
    derivative_h = None
    derivative_transfer_trace_id = None
    for h_value in sorted(set(h_tuple)):
        transfer = typed_finite_difference(
            g_local,
            h_value,
            eta * h_value,
            function_label=embedded_function_label,
            precision=precision,
            backend=backend,
            device=device,
            measurement_resolution=measurement_resolution,
            expression_path="forward_difference",
        )
        if transfer.status is TransferStatus.TRANSFER_OBSERVED:
            derivative_at_point = transfer.value.transfer
            derivative_h = h_value
            derivative_transfer_trace_id = transfer.provenance.trace_id
            break

    status = _status_from_alpha_status(alpha_probe_result.status)
    alpha_value = alpha_probe_result.value
    return _result(
        status,
        point,
        f_at_x0,
        probe_id,
        function_label,
        h_tuple,
        eta,
        alpha_probe_result.provenance.trace_id,
        alpha_value.transfer_trace_ids,
        alpha_value.slope_trace_id,
        alpha_value.observed_slope,
        alpha_value.observed_alpha,
        alpha_probe_result.status,
        derivative_at_point,
        derivative_h,
        derivative_transfer_trace_id,
        models,
        declared_alpha_band,
        alpha_value.selected_alpha_model,
        alpha_value.matching_alpha_model_names,
        expression_path,
        precision,
        backend,
        device,
        measurement_resolution,
        f"alpha_status={alpha_probe_result.status.value}",
        alpha_probe_observation=alpha_probe_result.value,
    )


def _validate_inputs(
    func: Callable[[float], float],
    x0: float,
    h_values: Sequence[float],
    eta: float,
    probe_id: str,
    function_label: str,
    declared_alpha_models: Sequence[DeclaredAlphaModel],
    declared_alpha_band: float | None,
) -> tuple[float, tuple[float, ...]]:
    if not callable(func):
        raise ProtocolViolationError("func must be callable")
    if isinstance(x0, bool) or not isinstance(x0, int | float) or not math.isfinite(x0):
        raise ProtocolViolationError("x0 must be a finite real scalar")
    try:
        h_tuple = tuple(h_values)
    except TypeError as exc:
        raise ProtocolViolationError("h_values must be a sequence of finite positive real scalars") from exc
    if not h_tuple:
        raise ProtocolViolationError("h_values must not be empty")
    for value in h_tuple:
        if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value) or value <= 0:
            raise ProtocolViolationError("h_values must contain only finite positive real scalars")
    if isinstance(eta, bool) or not isinstance(eta, int | float) or not math.isfinite(eta) or eta == 0:
        raise ProtocolViolationError("eta must be a finite non-zero real scalar")
    if not isinstance(probe_id, str) or probe_id == "":
        raise ProtocolViolationError("probe_id must be a non-empty string")
    if not isinstance(function_label, str) or function_label == "":
        raise ProtocolViolationError("function_label must be a non-empty string")
    if declared_alpha_band is not None and (
        isinstance(declared_alpha_band, bool)
        or not isinstance(declared_alpha_band, int | float)
        or not math.isfinite(declared_alpha_band)
        or declared_alpha_band <= 0
    ):
        raise ValueError("declared_alpha_band must be finite and positive")
    names: set[str] = set()
    for model in declared_alpha_models:
        if not isinstance(model, DeclaredAlphaModel):
            raise ProtocolViolationError("declared_alpha_models must contain DeclaredAlphaModel instances")
        if model.name == "" or model.name in names:
            raise ProtocolViolationError("declared alpha model names must be non-empty and unique")
        names.add(model.name)
        if not math.isfinite(model.alpha) or not math.isfinite(model.band) or model.band <= 0:
            raise ProtocolViolationError("declared alpha model alpha and band must be finite, with positive band")
    return float(x0), tuple(float(value) for value in h_tuple)


def _is_numeric(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, int | float)


def _status_from_alpha_status(status: AlphaProbeStatus) -> ScalarAlphaJetBundleStatus:
    if status is AlphaProbeStatus.ALPHA_REGULAR_INTEGER:
        return ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA
    if status is AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH:
        return ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH
    if status is AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY:
        return ScalarAlphaJetBundleStatus.SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY
    if status in {AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS, AlphaProbeStatus.ALPHA_MODEL_NO_MATCH}:
        return ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_MODEL_REFUSED
    if status is AlphaProbeStatus.ALPHA_CANCELLATION_DOMINATED:
        return ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_CANCELLATION_DOMINATED
    if status in {AlphaProbeStatus.ALPHA_INSUFFICIENT_DATA, AlphaProbeStatus.ALPHA_INDETERMINATE}:
        return ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_INDETERMINATE
    if status is AlphaProbeStatus.ALPHA_ZERO_BOUNDARY:
        return ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_ZERO_BOUNDARY
    if status is AlphaProbeStatus.ALPHA_UNSTABLE_WINDOW:
        return ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_UNSTABLE_WINDOW
    if status is AlphaProbeStatus.ALPHA_DOMAIN_REFUSED:
        return ScalarAlphaJetBundleStatus.SCALAR_JET_DOMAIN_REFUSED
    if status is AlphaProbeStatus.ALPHA_NONFINITE:
        return ScalarAlphaJetBundleStatus.SCALAR_JET_NONFINITE
    return ScalarAlphaJetBundleStatus.SCALAR_JET_PROTOCOL_REFUSED


def _result(
    status: ScalarAlphaJetBundleStatus,
    point: float,
    f_value: float | None,
    probe_id: str,
    function_label: str,
    h_values: tuple[float, ...],
    eta: float,
    alpha_probe_trace_id: str | None,
    transfer_trace_ids: tuple[str, ...],
    slope_trace_id: str | None,
    observed_slope: float | None,
    observed_alpha: float | None,
    alpha_status: AlphaProbeStatus | None,
    derivative_at_point: float | None,
    derivative_h: float | None,
    derivative_transfer_trace_id: str | None,
    declared_alpha_models: tuple[DeclaredAlphaModel, ...],
    declared_alpha_band: float | None,
    selected_alpha_model: str | None,
    matching_alpha_model_names: tuple[str, ...],
    expression_path: str,
    precision: str,
    backend: str,
    device: str,
    measurement_resolution: Any | None,
    reason: str,
    alpha_probe_observation: AlphaProbeObservation | None = None,
) -> ScalarAlphaJetBundleResult:
    value = ScalarAlphaJetBundleObservation(
        point=point,
        f_value=f_value,
        probe_id=probe_id,
        function_label=function_label,
        h_values=h_values,
        eta=eta,
        alpha_probe_observation=alpha_probe_observation,
        alpha_probe_trace_id=alpha_probe_trace_id,
        transfer_trace_ids=transfer_trace_ids,
        slope_trace_id=slope_trace_id,
        observed_slope=observed_slope,
        observed_alpha=observed_alpha,
        alpha_status=alpha_status,
        derivative_at_point=derivative_at_point,
        derivative_h=derivative_h,
        derivative_transfer_trace_id=derivative_transfer_trace_id,
        declared_alpha_models=declared_alpha_models,
        declared_alpha_band=declared_alpha_band,
        selected_alpha_model=selected_alpha_model,
        matching_alpha_model_names=matching_alpha_model_names,
        expression_path=expression_path,
    )
    parents = () if alpha_probe_trace_id is None else (alpha_probe_trace_id,)
    return TypedResult(
        value=value,
        space=SCALAR_ALPHA_JET_BUNDLE_SPACE,
        status=status,
        validity=_validity_for_status(status),
        conditioning=_conditioning_for_status(status, value, reason),
        provenance=Provenance(
            operation_id="scalar_alpha_jet_bundle",
            expression_path=expression_path,
            precision=precision,
            backend=backend,
            device=device,
            measurement_resolution=measurement_resolution,
            inputs=(probe_id, function_label, point, h_values, eta),
            parents=parents,
        ),
        protocol=ProtocolStatus.OK,
    )


def _validity_for_status(status: ScalarAlphaJetBundleStatus) -> Validity:
    if status in {
        ScalarAlphaJetBundleStatus.SCALAR_JET_REGULAR_INTEGER_ALPHA,
        ScalarAlphaJetBundleStatus.SCALAR_JET_FRACTIONAL_ALPHA_BRANCH,
    }:
        return Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True)
    if status is ScalarAlphaJetBundleStatus.SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY:
        return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
    if status in {
        ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_MODEL_REFUSED,
        ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_ZERO_BOUNDARY,
        ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_UNSTABLE_WINDOW,
    }:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    if status is ScalarAlphaJetBundleStatus.SCALAR_JET_NONFINITE:
        return Validity(defined=True, finite=False, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning_for_status(status: ScalarAlphaJetBundleStatus, value: ScalarAlphaJetBundleObservation, reason: str) -> Conditioning:
    if status in ACCEPTED_SCALAR_ALPHA_JET_BUNDLE_STATUSES:
        return Conditioning(
            status=ConditioningStatus.WELL_CONDITIONED,
            notes=(
                f"observed_alpha={_format_optional(value.observed_alpha, '.6g')}",
                f"alpha_status={value.alpha_status.value if value.alpha_status is not None else 'pre_probe_refusal'}",
                f"derivative_at_point={_format_optional(value.derivative_at_point, '.3e')}",
                f"h_used={_format_optional(value.derivative_h, '.3e')}",
            ),
        )
    if status in {
        ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_MODEL_REFUSED,
        ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_ZERO_BOUNDARY,
        ScalarAlphaJetBundleStatus.SCALAR_JET_ALPHA_UNSTABLE_WINDOW,
    }:
        return Conditioning(
            status=ConditioningStatus.WARNING,
            notes=(
                f"alpha_status={value.alpha_status.value if value.alpha_status is not None else 'pre_probe_refusal'}",
                f"matching_models={list(value.matching_alpha_model_names)}",
            ),
        )
    return Conditioning(
        status=ConditioningStatus.WARNING,
        notes=(
            f"alpha_status={value.alpha_status.value if value.alpha_status is not None else 'pre_probe_refusal'}",
            f"reason={reason}",
        ),
    )


def _format_optional(value: float | None, spec: str) -> str:
    if value is None:
        return "none"
    return format(value, spec)
