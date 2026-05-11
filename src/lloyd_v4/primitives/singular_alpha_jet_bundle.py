from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Sequence

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.status import AlphaProbeStatus, ConditioningStatus, ProtocolStatus, SingularAlphaJetBundleStatus
from lloyd_v4.core.validity import Validity
from lloyd_v4.primitives.directional_alpha_probe import DeclaredAlphaModel, directional_alpha_probe


SINGULAR_ALPHA_JET_BUNDLE_SPACE = "SingularAlphaJetBundleObservation"
SINGULAR_ALPHA_JET_BUNDLE_STATUSES = frozenset(SingularAlphaJetBundleStatus)
ACCEPTED_SINGULAR_ALPHA_JET_BUNDLE_STATUSES = frozenset(
    {
        SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA,
        SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH,
        SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY,
    }
)

SINGULAR_ALPHA_JET_BUNDLE_PROTOCOL = ProducerProtocol(
    name="singular_alpha_jet_bundle",
    emitted_statuses=SINGULAR_ALPHA_JET_BUNDLE_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=SingularAlphaJetBundleStatus,
)

SINGULAR_ALPHA_JET_BUNDLE_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="singular_alpha_jet_bundle_consumer",
    accepted_statuses=ACCEPTED_SINGULAR_ALPHA_JET_BUNDLE_STATUSES,
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
    status_family=SingularAlphaJetBundleStatus,
    refused_statuses=SINGULAR_ALPHA_JET_BUNDLE_STATUSES - ACCEPTED_SINGULAR_ALPHA_JET_BUNDLE_STATUSES,
)


@dataclass(frozen=True, slots=True)
class SingularAlphaJetBundleObservation:
    point: float
    probe_id: str
    function_label: str
    h_values: tuple[float, ...]
    eta: float
    alpha_probe_trace_id: str | None
    transfer_trace_ids: tuple[str, ...]
    slope_trace_id: str | None
    observed_slope: float | None
    observed_alpha: float | None
    alpha_status: AlphaProbeStatus | None
    declared_alpha_models: tuple[DeclaredAlphaModel, ...]
    declared_alpha_band: float | None
    selected_alpha_model: str | None
    matching_alpha_model_names: tuple[str, ...]
    expression_path: str

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe

        return {
            "point": self.point,
            "probe_id": self.probe_id,
            "function_label": self.function_label,
            "h_values": list(self.h_values),
            "eta": self.eta,
            "alpha_probe_trace_id": self.alpha_probe_trace_id,
            "transfer_trace_ids": list(self.transfer_trace_ids),
            "slope_trace_id": self.slope_trace_id,
            "observed_slope": to_json_safe(self.observed_slope),
            "observed_alpha": to_json_safe(self.observed_alpha),
            "alpha_status": self.alpha_status.value if self.alpha_status is not None else None,
            "declared_alpha_models": [model.to_json_safe() for model in self.declared_alpha_models],
            "declared_alpha_band": to_json_safe(self.declared_alpha_band),
            "selected_alpha_model": self.selected_alpha_model,
            "matching_alpha_model_names": list(self.matching_alpha_model_names),
            "expression_path": self.expression_path,
        }


SingularAlphaJetBundleResult = TypedResult[SingularAlphaJetBundleObservation, SingularAlphaJetBundleStatus]


def singular_alpha_jet_bundle(
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
    expression_path: str = "singular_alpha_jet_singular_probe",
) -> SingularAlphaJetBundleResult:
    point, h_tuple = _validate_inputs(func, x0, h_values, eta, probe_id, function_label, declared_alpha_models, declared_alpha_band)
    models = tuple(declared_alpha_models)

    def g_singular(h: float) -> float:
        return func(point + h)

    embedded_probe_id = f"{probe_id}__x0_{point!r}"
    embedded_function_label = f"{function_label}__singular_at_{point!r}"
    alpha_probe_result = directional_alpha_probe(
        g_singular,
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
    alpha_value = alpha_probe_result.value
    status = _status_from_alpha_status(alpha_probe_result.status)
    value = SingularAlphaJetBundleObservation(
        point=point,
        probe_id=probe_id,
        function_label=function_label,
        h_values=h_tuple,
        eta=eta,
        alpha_probe_trace_id=alpha_probe_result.provenance.trace_id,
        transfer_trace_ids=alpha_value.transfer_trace_ids,
        slope_trace_id=alpha_value.slope_trace_id,
        observed_slope=alpha_value.observed_slope,
        observed_alpha=alpha_value.observed_alpha,
        alpha_status=alpha_probe_result.status,
        declared_alpha_models=models,
        declared_alpha_band=declared_alpha_band,
        selected_alpha_model=alpha_value.selected_alpha_model,
        matching_alpha_model_names=alpha_value.matching_alpha_model_names,
        expression_path=expression_path,
    )
    return TypedResult(
        value=value,
        space=SINGULAR_ALPHA_JET_BUNDLE_SPACE,
        status=status,
        validity=_validity_for_status(status),
        conditioning=_conditioning_for_status(status, value),
        provenance=Provenance(
            operation_id="singular_alpha_jet_bundle",
            expression_path=expression_path,
            precision=precision,
            backend=backend,
            device=device,
            measurement_resolution=measurement_resolution,
            inputs=(probe_id, function_label, point, h_tuple, eta),
            parents=(alpha_probe_result.provenance.trace_id,),
        ),
        protocol=ProtocolStatus.OK,
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
        raise ProtocolViolationError("declared_alpha_band must be finite and positive")
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


def _status_from_alpha_status(status: AlphaProbeStatus) -> SingularAlphaJetBundleStatus:
    if status is AlphaProbeStatus.ALPHA_REGULAR_INTEGER:
        return SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA
    if status is AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH:
        return SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH
    if status is AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY:
        return SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY
    if status in {AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS, AlphaProbeStatus.ALPHA_MODEL_NO_MATCH}:
        return SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_MODEL_REFUSED
    if status is AlphaProbeStatus.ALPHA_CANCELLATION_DOMINATED:
        return SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_CANCELLATION_DOMINATED
    if status in {AlphaProbeStatus.ALPHA_INSUFFICIENT_DATA, AlphaProbeStatus.ALPHA_INDETERMINATE}:
        return SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_INDETERMINATE
    if status is AlphaProbeStatus.ALPHA_DOMAIN_REFUSED:
        return SingularAlphaJetBundleStatus.SINGULAR_JET_DOMAIN_REFUSED
    if status is AlphaProbeStatus.ALPHA_NONFINITE:
        return SingularAlphaJetBundleStatus.SINGULAR_JET_NONFINITE
    return SingularAlphaJetBundleStatus.SINGULAR_JET_PROTOCOL_REFUSED


def _validity_for_status(status: SingularAlphaJetBundleStatus) -> Validity:
    if status in {
        SingularAlphaJetBundleStatus.SINGULAR_JET_REGULAR_INTEGER_ALPHA,
        SingularAlphaJetBundleStatus.SINGULAR_JET_FRACTIONAL_ALPHA_BRANCH,
    }:
        return Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True)
    if status is SingularAlphaJetBundleStatus.SINGULAR_JET_NEGATIVE_ALPHA_SINGULARITY:
        return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
    if status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_MODEL_REFUSED:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    if status is SingularAlphaJetBundleStatus.SINGULAR_JET_NONFINITE:
        return Validity(defined=True, finite=False, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning_for_status(status: SingularAlphaJetBundleStatus, value: SingularAlphaJetBundleObservation) -> Conditioning:
    alpha_status = value.alpha_status.value if value.alpha_status is not None else "pre_probe_refusal"
    if status in ACCEPTED_SINGULAR_ALPHA_JET_BUNDLE_STATUSES:
        return Conditioning(
            status=ConditioningStatus.WELL_CONDITIONED,
            notes=(
                f"observed_alpha={_format_optional(value.observed_alpha, '.6g')}",
                f"alpha_status={alpha_status}",
            ),
        )
    if status is SingularAlphaJetBundleStatus.SINGULAR_JET_ALPHA_MODEL_REFUSED:
        return Conditioning(
            status=ConditioningStatus.WARNING,
            notes=(
                f"alpha_status={alpha_status}",
                f"matching_models={list(value.matching_alpha_model_names)}",
            ),
        )
    return Conditioning(status=ConditioningStatus.WARNING, notes=(f"alpha_status={alpha_status}", f"status={status.value}"))


def _format_optional(value: float | None, spec: str) -> str:
    if value is None:
        return "none"
    return format(value, spec)
