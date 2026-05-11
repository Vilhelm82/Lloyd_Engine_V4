from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Sequence

from lloyd_v4.core.conditioning import Conditioning
from lloyd_v4.core.errors import ProtocolViolationError
from lloyd_v4.core.protocols import ConsumerProtocol, ProducerProtocol
from lloyd_v4.core.provenance import Provenance
from lloyd_v4.core.result import TypedResult
from lloyd_v4.core.status import AlphaProbeStatus, ConditioningStatus, ProtocolStatus, SlopeStatus, TransferStatus
from lloyd_v4.core.validity import Validity
from lloyd_v4.primitives.typed_collection import typed_collection
from lloyd_v4.primitives.typed_finite_difference import typed_finite_difference
from lloyd_v4.primitives.typed_log_log_slope import typed_log_log_slope


ALPHA_PROBE_SPACE = "AlphaProbeObservation"
ALPHA_PROBE_STATUSES = frozenset(AlphaProbeStatus)
ACCEPTED_ALPHA_PROBE_STATUSES = frozenset(
    {
        AlphaProbeStatus.ALPHA_REGULAR_INTEGER,
        AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH,
        AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY,
    }
)

DIRECTIONAL_ALPHA_PROBE_PROTOCOL = ProducerProtocol(
    name="directional_alpha_probe",
    emitted_statuses=ALPHA_PROBE_STATUSES,
    required_fields=frozenset({"value", "status", "validity", "provenance"}),
    status_family=AlphaProbeStatus,
)

ALPHA_PROBE_CONSUMER_PROTOCOL = ConsumerProtocol(
    name="alpha_probe_consumer",
    accepted_statuses=ACCEPTED_ALPHA_PROBE_STATUSES,
    required_validity_fields=frozenset({"defined", "finite", "selectable"}),
    scalarization_allowed=False,
    status_family=AlphaProbeStatus,
    refused_statuses=ALPHA_PROBE_STATUSES - ACCEPTED_ALPHA_PROBE_STATUSES,
)


@dataclass(frozen=True, slots=True)
class DeclaredAlphaModel:
    name: str
    alpha: float
    band: float

    def to_json_safe(self) -> dict[str, Any]:
        return {"name": self.name, "alpha": self.alpha, "band": self.band}


@dataclass(frozen=True, slots=True)
class AlphaProbeObservation:
    probe_id: str
    function_label: str
    f_values: tuple[float, ...]
    delta_values: tuple[float, ...]
    eta: float
    transfer_trace_ids: tuple[str, ...]
    slope_trace_id: str | None
    observed_slope: float | None
    observed_alpha: float | None
    r_squared: float | None
    standard_error: float | None
    log_f_min: float | None
    log_f_max: float | None
    n_input_observations: int
    n_observed: int
    n_cancellation_dominated: int
    n_non_finite: int
    n_domain_refused: int
    n_delta_indeterminate: int
    declared_alpha_models: tuple[DeclaredAlphaModel, ...]
    declared_alpha_band: float | None
    selected_alpha_model: str | None
    matching_alpha_model_names: tuple[str, ...]
    expression_path: str

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe

        return {
            "probe_id": self.probe_id,
            "function_label": self.function_label,
            "f_values": list(self.f_values),
            "delta_values": list(self.delta_values),
            "eta": self.eta,
            "transfer_trace_ids": list(self.transfer_trace_ids),
            "slope_trace_id": self.slope_trace_id,
            "observed_slope": to_json_safe(self.observed_slope),
            "observed_alpha": to_json_safe(self.observed_alpha),
            "r_squared": to_json_safe(self.r_squared),
            "standard_error": to_json_safe(self.standard_error),
            "log_f_min": to_json_safe(self.log_f_min),
            "log_f_max": to_json_safe(self.log_f_max),
            "n_input_observations": self.n_input_observations,
            "n_observed": self.n_observed,
            "n_cancellation_dominated": self.n_cancellation_dominated,
            "n_non_finite": self.n_non_finite,
            "n_domain_refused": self.n_domain_refused,
            "n_delta_indeterminate": self.n_delta_indeterminate,
            "declared_alpha_models": [model.to_json_safe() for model in self.declared_alpha_models],
            "declared_alpha_band": to_json_safe(self.declared_alpha_band),
            "selected_alpha_model": self.selected_alpha_model,
            "matching_alpha_model_names": list(self.matching_alpha_model_names),
            "expression_path": self.expression_path,
        }


AlphaProbeResult = TypedResult[AlphaProbeObservation, AlphaProbeStatus]


def directional_alpha_probe(
    observable: Callable[[float], float],
    f_values: Sequence[float],
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
    expression_path: str = "log_log_slope_fit",
) -> AlphaProbeResult:
    f_tuple = _validate_inputs(observable, f_values, eta, probe_id, function_label, declared_alpha_models, declared_alpha_band)
    models = tuple(declared_alpha_models)
    delta_values = tuple(eta * f_value for f_value in f_tuple)
    transfers = tuple(
        typed_finite_difference(
            observable,
            f_value,
            delta_value,
            function_label=function_label,
            precision=precision,
            backend=backend,
            device=device,
            measurement_resolution=measurement_resolution,
            expression_path="forward_difference",
        )
        for f_value, delta_value in zip(f_tuple, delta_values)
    )
    counts = _transfer_counts(transfers)

    if counts[TransferStatus.TRANSFER_OBSERVED] < 3:
        status = _low_observation_status(counts, len(transfers))
        return _probe_result(
            status,
            probe_id,
            function_label,
            f_tuple,
            delta_values,
            eta,
            transfers,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            counts,
            models,
            declared_alpha_band,
            None,
            (),
            expression_path,
            precision,
            backend,
            device,
            measurement_resolution,
        )

    collection = typed_collection(transfers)
    slope_result = typed_log_log_slope(collection, precision=precision, backend=backend, device=device, measurement_resolution=measurement_resolution)
    if slope_result.status is SlopeStatus.SLOPE_INSUFFICIENT_DATA:
        status = AlphaProbeStatus.ALPHA_INSUFFICIENT_DATA
    elif slope_result.status is SlopeStatus.SLOPE_DEGENERATE_INPUT:
        status = AlphaProbeStatus.ALPHA_INDETERMINATE
    elif not _finite_slope_value(slope_result.value.slope, slope_result.value.intercept):
        status = AlphaProbeStatus.ALPHA_NONFINITE
    else:
        observed_alpha = slope_result.value.slope + 1.0
        status, selected_model, matching_names = _classify_alpha(observed_alpha, models, declared_alpha_band)
        return _probe_result(
            status,
            probe_id,
            function_label,
            f_tuple,
            delta_values,
            eta,
            transfers,
            slope_result,
            slope_result.value.slope,
            observed_alpha,
            slope_result.value.r_squared,
            slope_result.value.standard_error,
            slope_result.value.log_f_min,
            slope_result.value.log_f_max,
            counts,
            models,
            declared_alpha_band,
            selected_model,
            matching_names,
            expression_path,
            precision,
            backend,
            device,
            measurement_resolution,
        )

    return _probe_result(
        status,
        probe_id,
        function_label,
        f_tuple,
        delta_values,
        eta,
        transfers,
        slope_result,
        slope_result.value.slope,
        None if slope_result.value.slope is None else slope_result.value.slope + 1.0,
        slope_result.value.r_squared,
        slope_result.value.standard_error,
        slope_result.value.log_f_min,
        slope_result.value.log_f_max,
        counts,
        models,
        declared_alpha_band,
        None,
        (),
        expression_path,
        precision,
        backend,
        device,
        measurement_resolution,
    )


def _validate_inputs(
    observable: Callable[[float], float],
    f_values: Sequence[float],
    eta: float,
    probe_id: str,
    function_label: str,
    declared_alpha_models: Sequence[DeclaredAlphaModel],
    declared_alpha_band: float | None,
) -> tuple[float, ...]:
    if not callable(observable):
        raise ProtocolViolationError("observable must be callable")
    if not isinstance(probe_id, str) or probe_id == "":
        raise ProtocolViolationError("probe_id must be a non-empty string")
    if not isinstance(function_label, str) or function_label == "":
        raise ProtocolViolationError("function_label must be a non-empty string")
    if isinstance(eta, bool) or not isinstance(eta, int | float) or not math.isfinite(eta) or eta == 0:
        raise ProtocolViolationError("eta must be a finite non-zero real scalar")
    try:
        f_tuple = tuple(f_values)
    except TypeError as exc:
        raise ProtocolViolationError("f_values must be a sequence of finite positive real scalars") from exc
    if not f_tuple:
        raise ProtocolViolationError("f_values must not be empty")
    for value in f_tuple:
        if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value) or value <= 0:
            raise ProtocolViolationError("f_values must contain only finite positive real scalars")
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
    return tuple(float(value) for value in f_tuple)


def _transfer_counts(transfers: tuple[TypedResult, ...]) -> dict[TransferStatus, int]:
    return {status: sum(1 for transfer in transfers if transfer.status is status) for status in TransferStatus}


def _low_observation_status(counts: dict[TransferStatus, int], total: int) -> AlphaProbeStatus:
    refused = total - counts[TransferStatus.TRANSFER_OBSERVED]
    majority = refused // 2 + 1
    if counts[TransferStatus.TRANSFER_CANCELLATION_DOMINATED] >= majority:
        return AlphaProbeStatus.ALPHA_CANCELLATION_DOMINATED
    if counts[TransferStatus.TRANSFER_DOMAIN_REFUSED] >= majority:
        return AlphaProbeStatus.ALPHA_DOMAIN_REFUSED
    if counts[TransferStatus.TRANSFER_NON_FINITE] >= majority:
        return AlphaProbeStatus.ALPHA_NONFINITE
    return AlphaProbeStatus.ALPHA_INSUFFICIENT_DATA


def _finite_slope_value(slope: float | None, intercept: float | None) -> bool:
    return slope is not None and intercept is not None and math.isfinite(slope) and math.isfinite(intercept)


def _classify_alpha(
    observed_alpha: float,
    models: tuple[DeclaredAlphaModel, ...],
    declared_alpha_band: float | None,
) -> tuple[AlphaProbeStatus, str | None, tuple[str, ...]]:
    if not math.isfinite(observed_alpha):
        return AlphaProbeStatus.ALPHA_NONFINITE, None, ()
    if models:
        matching = tuple(model for model in models if abs(observed_alpha - model.alpha) <= model.band)
        matching_names = tuple(model.name for model in matching)
        if len(matching) > 1:
            return AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS, None, matching_names
        if not matching:
            return AlphaProbeStatus.ALPHA_MODEL_NO_MATCH, None, ()
        matched = matching[0]
        if matched.alpha < 0:
            return AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY, matched.name, matching_names
        if _is_close_to_positive_integer(matched.alpha, matched.band):
            return AlphaProbeStatus.ALPHA_REGULAR_INTEGER, matched.name, matching_names
        return AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH, matched.name, matching_names
    if observed_alpha < 0:
        return AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY, None, ()
    if declared_alpha_band is not None and _is_close_to_positive_integer(observed_alpha, declared_alpha_band):
        return AlphaProbeStatus.ALPHA_REGULAR_INTEGER, None, ()
    return AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH, None, ()


def _is_close_to_positive_integer(alpha: float, band: float) -> bool:
    if alpha <= 0:
        return False
    nearest = round(alpha)
    if nearest < 1:
        return False
    return abs(alpha - nearest) <= band


def _probe_result(
    status: AlphaProbeStatus,
    probe_id: str,
    function_label: str,
    f_values: tuple[float, ...],
    delta_values: tuple[float, ...],
    eta: float,
    transfers: tuple[TypedResult, ...],
    slope_result: TypedResult | None,
    observed_slope: float | None,
    observed_alpha: float | None,
    r_squared: float | None,
    standard_error: float | None,
    log_f_min: float | None,
    log_f_max: float | None,
    counts: dict[TransferStatus, int],
    declared_alpha_models: tuple[DeclaredAlphaModel, ...],
    declared_alpha_band: float | None,
    selected_alpha_model: str | None,
    matching_alpha_model_names: tuple[str, ...],
    expression_path: str,
    precision: str,
    backend: str,
    device: str,
    measurement_resolution: Any | None,
) -> AlphaProbeResult:
    transfer_trace_ids = tuple(transfer.provenance.trace_id for transfer in transfers)
    slope_trace_id = None if slope_result is None else slope_result.provenance.trace_id
    value = AlphaProbeObservation(
        probe_id=probe_id,
        function_label=function_label,
        f_values=f_values,
        delta_values=delta_values,
        eta=eta,
        transfer_trace_ids=transfer_trace_ids,
        slope_trace_id=slope_trace_id,
        observed_slope=observed_slope,
        observed_alpha=observed_alpha,
        r_squared=r_squared,
        standard_error=standard_error,
        log_f_min=log_f_min,
        log_f_max=log_f_max,
        n_input_observations=len(transfers),
        n_observed=counts[TransferStatus.TRANSFER_OBSERVED],
        n_cancellation_dominated=counts[TransferStatus.TRANSFER_CANCELLATION_DOMINATED],
        n_non_finite=counts[TransferStatus.TRANSFER_NON_FINITE],
        n_domain_refused=counts[TransferStatus.TRANSFER_DOMAIN_REFUSED],
        n_delta_indeterminate=counts[TransferStatus.TRANSFER_DELTA_INDETERMINATE],
        declared_alpha_models=declared_alpha_models,
        declared_alpha_band=declared_alpha_band,
        selected_alpha_model=selected_alpha_model,
        matching_alpha_model_names=matching_alpha_model_names,
        expression_path=expression_path,
    )
    parents = transfer_trace_ids + (() if slope_trace_id is None else (slope_trace_id,))
    return TypedResult(
        value=value,
        space=ALPHA_PROBE_SPACE,
        status=status,
        validity=_validity_for_status(status),
        conditioning=_conditioning_for_status(status, value),
        provenance=Provenance(
            operation_id="directional_alpha_probe",
            expression_path=expression_path,
            precision=precision,
            backend=backend,
            device=device,
            measurement_resolution=measurement_resolution,
            inputs=(probe_id, function_label, f_values, eta),
            parents=parents,
        ),
        protocol=ProtocolStatus.OK,
    )


def _validity_for_status(status: AlphaProbeStatus) -> Validity:
    if status in {AlphaProbeStatus.ALPHA_REGULAR_INTEGER, AlphaProbeStatus.ALPHA_FRACTIONAL_BRANCH}:
        return Validity(defined=True, finite=True, selectable=True, advanceable=True, observable=True)
    if status is AlphaProbeStatus.ALPHA_NEGATIVE_SINGULARITY:
        return Validity(defined=True, finite=True, selectable=True, advanceable=False, observable=True)
    if status in {AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS, AlphaProbeStatus.ALPHA_MODEL_NO_MATCH}:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    if status is AlphaProbeStatus.ALPHA_NONFINITE:
        return Validity(defined=True, finite=False, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning_for_status(status: AlphaProbeStatus, value: AlphaProbeObservation) -> Conditioning:
    if status in ACCEPTED_ALPHA_PROBE_STATUSES:
        return Conditioning(
            status=ConditioningStatus.WELL_CONDITIONED,
            notes=(
                f"observed_alpha={value.observed_alpha:.6g}",
                f"r_squared={value.r_squared:.6g}",
                f"standard_error={value.standard_error:.3e}",
                f"n_observed={value.n_observed}/{value.n_input_observations}",
            ),
        )
    if status in {AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS, AlphaProbeStatus.ALPHA_MODEL_NO_MATCH}:
        return Conditioning(
            status=ConditioningStatus.WARNING,
            notes=(
                f"observed_alpha={value.observed_alpha:.6g}",
                f"matching_models={list(value.matching_alpha_model_names)}",
                f"declared_models={len(value.declared_alpha_models)}",
            ),
        )
    if status is AlphaProbeStatus.ALPHA_NONFINITE:
        return Conditioning(status=ConditioningStatus.WARNING, notes=("slope_fit_overflow", f"observed_slope={value.observed_slope}"))
    return Conditioning(
        status=ConditioningStatus.WARNING,
        notes=(
            f"n_observed={value.n_observed}",
            f"n_cancellation_dominated={value.n_cancellation_dominated}",
            f"n_domain_refused={value.n_domain_refused}",
        ),
    )
