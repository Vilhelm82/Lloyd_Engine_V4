from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable, Final, Sequence

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

# Standard-error multiplier for the zero-boundary envelope. 2.0 is the
# approximately 95% confidence interval multiplier for the slope estimate.
K_BOUNDARY: Final[float] = 2.0

# Standard-error multiplier for the nested-window drift significance check.
K_DRIFT: Final[float] = 2.0

# Precision-tied absolute floor for alpha-near-zero boundary classification.
ALPHA_NUMERIC_FLOOR: Final[float] = 1e-9

# Default materiality limit when callers do not provide declared_alpha_band.
DEFAULT_ALPHA_MATERIALITY: Final[float] = 0.05

# Minimum samples per nested-window slope fit and minimum fit count.
MIN_WINDOW_POINTS: Final[int] = 3
MIN_WINDOW_COUNT: Final[int] = 3

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


class AlphaWindowStabilityStatus(StrEnum):
    STABLE = "stable"
    UNSTABLE = "unstable"
    NOT_TESTED = "not_tested"


@dataclass(frozen=True, slots=True)
class AlphaWindowFit:
    h_start: float
    h_end: float
    h_count: int
    observed_slope: float
    observed_alpha: float
    slope_standard_error: float
    alpha_standard_error: float
    r_squared: float

    def to_json_safe(self) -> dict[str, Any]:
        from lloyd_v4.core.serialization import to_json_safe

        return {
            "h_start": to_json_safe(self.h_start),
            "h_end": to_json_safe(self.h_end),
            "h_count": self.h_count,
            "observed_slope": to_json_safe(self.observed_slope),
            "observed_alpha": to_json_safe(self.observed_alpha),
            "slope_standard_error": to_json_safe(self.slope_standard_error),
            "alpha_standard_error": to_json_safe(self.alpha_standard_error),
            "r_squared": to_json_safe(self.r_squared),
        }


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
    nested_window_fits: tuple[AlphaWindowFit, ...] | None
    alpha_window_min: float | None
    alpha_window_max: float | None
    alpha_window_span: float | None
    propagated_window_error: float | None
    alpha_stability_status: AlphaWindowStabilityStatus
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

    def __post_init__(self) -> None:
        nested_fields = (
            self.nested_window_fits,
            self.alpha_window_min,
            self.alpha_window_max,
            self.alpha_window_span,
            self.propagated_window_error,
        )
        if self.alpha_stability_status is AlphaWindowStabilityStatus.NOT_TESTED:
            if any(field is not None for field in nested_fields):
                raise ValueError("nested-window fields must all be None when stability is not_tested")
            return
        if any(field is None for field in nested_fields):
            raise ValueError("nested-window fields must all be populated when stability was tested")
        if not self.nested_window_fits:
            raise ValueError("nested_window_fits must be non-empty when stability was tested")
        if self.alpha_window_span is not None and self.alpha_window_span < 0:
            raise ValueError("alpha_window_span must be non-negative")

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
            "nested_window_fits": to_json_safe(self.nested_window_fits),
            "alpha_window_min": to_json_safe(self.alpha_window_min),
            "alpha_window_max": to_json_safe(self.alpha_window_max),
            "alpha_window_span": to_json_safe(self.alpha_window_span),
            "propagated_window_error": to_json_safe(self.propagated_window_error),
            "alpha_stability_status": self.alpha_stability_status.value,
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


@dataclass(frozen=True, slots=True)
class _NestedWindowEvidence:
    fits: tuple[AlphaWindowFit, ...] | None
    alpha_window_min: float | None
    alpha_window_max: float | None
    alpha_window_span: float | None
    propagated_window_error: float | None
    stability_status: AlphaWindowStabilityStatus


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
        nested_evidence = _untested_nested_evidence()
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
            nested_evidence,
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
        nested_evidence = _nested_window_evidence(transfers, declared_alpha_band)
        if _is_zero_boundary(observed_alpha, slope_result.value.standard_error):
            status, selected_model, matching_names = AlphaProbeStatus.ALPHA_ZERO_BOUNDARY, None, ()
        elif nested_evidence.stability_status is AlphaWindowStabilityStatus.UNSTABLE:
            status, selected_model, matching_names = AlphaProbeStatus.ALPHA_UNSTABLE_WINDOW, None, ()
        else:
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
            nested_evidence,
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

    nested_evidence = _untested_nested_evidence()
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
        nested_evidence,
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


def _untested_nested_evidence() -> _NestedWindowEvidence:
    return _NestedWindowEvidence(
        fits=None,
        alpha_window_min=None,
        alpha_window_max=None,
        alpha_window_span=None,
        propagated_window_error=None,
        stability_status=AlphaWindowStabilityStatus.NOT_TESTED,
    )


def _nested_window_evidence(transfers: tuple[TypedResult, ...], declared_alpha_band: float | None) -> _NestedWindowEvidence:
    pairs = tuple(pair for pair in (_usable_pair(transfer) for transfer in transfers) if pair is not None)
    pairs = tuple(sorted(pairs, key=lambda pair: pair[0], reverse=True))
    max_window_count = len(pairs) - MIN_WINDOW_POINTS + 1
    if max_window_count < MIN_WINDOW_COUNT:
        return _untested_nested_evidence()

    fits: list[AlphaWindowFit] = []
    for drop_count in range(max_window_count):
        window_pairs = pairs[drop_count:]
        fit = _fit_window(window_pairs)
        if fit is not None:
            fits.append(fit)
    if len(fits) < MIN_WINDOW_COUNT:
        return _untested_nested_evidence()

    fits_tuple = tuple(fits)
    min_fit = min(fits_tuple, key=lambda fit: fit.observed_alpha)
    max_fit = max(fits_tuple, key=lambda fit: fit.observed_alpha)
    alpha_span = max_fit.observed_alpha - min_fit.observed_alpha
    propagated_error = math.sqrt(min_fit.alpha_standard_error**2 + max_fit.alpha_standard_error**2)
    materiality = declared_alpha_band if declared_alpha_band is not None else DEFAULT_ALPHA_MATERIALITY
    stability_status = (
        AlphaWindowStabilityStatus.UNSTABLE
        if alpha_span > materiality and alpha_span > K_DRIFT * propagated_error
        else AlphaWindowStabilityStatus.STABLE
    )
    return _NestedWindowEvidence(
        fits=fits_tuple,
        alpha_window_min=min_fit.observed_alpha,
        alpha_window_max=max_fit.observed_alpha,
        alpha_window_span=alpha_span,
        propagated_window_error=propagated_error,
        stability_status=stability_status,
    )


def _usable_pair(observation: TypedResult) -> tuple[float, float] | None:
    if observation.status is not TransferStatus.TRANSFER_OBSERVED or len(observation.provenance.inputs) < 1:
        return None
    h_value = observation.provenance.inputs[0]
    transfer = getattr(observation.value, "transfer", None)
    if isinstance(h_value, bool) or isinstance(transfer, bool):
        return None
    if not isinstance(h_value, int | float) or not isinstance(transfer, int | float):
        return None
    h_float = float(h_value)
    transfer_float = float(transfer)
    if not math.isfinite(h_float) or not math.isfinite(transfer_float):
        return None
    if h_float <= 0 or transfer_float == 0:
        return None
    return h_float, transfer_float


def _fit_window(pairs: tuple[tuple[float, float], ...]) -> AlphaWindowFit | None:
    if len(pairs) < MIN_WINDOW_POINTS:
        return None
    log_h = tuple(math.log(h_value) for h_value, _transfer in pairs)
    log_transfer = tuple(math.log(abs(transfer)) for _h_value, transfer in pairs)
    if max(log_h) - min(log_h) == 0 or max(log_transfer) - min(log_transfer) == 0:
        return None
    slope, _intercept, r_squared, standard_error = _ordinary_least_squares(log_h, log_transfer)
    return AlphaWindowFit(
        h_start=min(h for h, _transfer in pairs),
        h_end=max(h for h, _transfer in pairs),
        h_count=len(pairs),
        observed_slope=slope,
        observed_alpha=slope + 1.0,
        slope_standard_error=standard_error,
        alpha_standard_error=standard_error,
        r_squared=r_squared,
    )


def _ordinary_least_squares(x_values: tuple[float, ...], y_values: tuple[float, ...]) -> tuple[float, float, float, float]:
    n = len(x_values)
    mean_x = sum(x_values) / n
    mean_y = sum(y_values) / n
    sxx = sum((x - mean_x) ** 2 for x in x_values)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, y_values))
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    residuals = tuple(y - (slope * x + intercept) for x, y in zip(x_values, y_values))
    ss_res = sum(residual * residual for residual in residuals)
    ss_tot = sum((y - mean_y) ** 2 for y in y_values)
    r_squared = 1.0 if ss_tot == 0 else 1.0 - ss_res / ss_tot
    standard_error = math.sqrt(max(0.0, ss_res / (n - 2) / sxx))
    return slope, intercept, r_squared, standard_error


def _alpha_boundary_envelope(standard_error: float | None) -> float:
    if standard_error is None or not math.isfinite(standard_error):
        return ALPHA_NUMERIC_FLOOR
    return max(K_BOUNDARY * standard_error, ALPHA_NUMERIC_FLOOR)


def _is_zero_boundary(observed_alpha: float, standard_error: float | None) -> bool:
    return abs(observed_alpha) <= _alpha_boundary_envelope(standard_error)


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
    nested_evidence: _NestedWindowEvidence,
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
        nested_window_fits=nested_evidence.fits,
        alpha_window_min=nested_evidence.alpha_window_min,
        alpha_window_max=nested_evidence.alpha_window_max,
        alpha_window_span=nested_evidence.alpha_window_span,
        propagated_window_error=nested_evidence.propagated_window_error,
        alpha_stability_status=nested_evidence.stability_status,
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
    if status in {
        AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS,
        AlphaProbeStatus.ALPHA_MODEL_NO_MATCH,
        AlphaProbeStatus.ALPHA_ZERO_BOUNDARY,
        AlphaProbeStatus.ALPHA_UNSTABLE_WINDOW,
    }:
        return Validity(defined=True, finite=True, selectable=False, advanceable=False, observable=True)
    if status is AlphaProbeStatus.ALPHA_NONFINITE:
        return Validity(defined=True, finite=False, selectable=False, advanceable=False, observable=True)
    return Validity(defined=False, finite=False, selectable=False, advanceable=False, observable=True)


def _conditioning_for_status(status: AlphaProbeStatus, value: AlphaProbeObservation) -> Conditioning:
    nested_notes = _nested_conditioning_notes(value)
    if status in ACCEPTED_ALPHA_PROBE_STATUSES:
        return Conditioning(
            status=ConditioningStatus.WELL_CONDITIONED,
            notes=(
                f"observed_alpha={value.observed_alpha:.6g}",
                f"r_squared={value.r_squared:.6g}",
                f"standard_error={value.standard_error:.3e}",
                f"n_observed={value.n_observed}/{value.n_input_observations}",
            )
            + nested_notes,
        )
    if status in {AlphaProbeStatus.ALPHA_MODEL_AMBIGUOUS, AlphaProbeStatus.ALPHA_MODEL_NO_MATCH}:
        return Conditioning(
            status=ConditioningStatus.WARNING,
            notes=(
                f"observed_alpha={value.observed_alpha:.6g}",
                f"matching_models={list(value.matching_alpha_model_names)}",
                f"declared_models={len(value.declared_alpha_models)}",
            )
            + nested_notes,
        )
    if status is AlphaProbeStatus.ALPHA_ZERO_BOUNDARY:
        return Conditioning(
            status=ConditioningStatus.WARNING,
            notes=(
                f"observed_alpha={value.observed_alpha:.6g}",
                f"alpha_boundary_envelope={_alpha_boundary_envelope(value.standard_error):.3e}",
                f"standard_error={value.standard_error:.3e}",
            )
            + nested_notes,
        )
    if status is AlphaProbeStatus.ALPHA_UNSTABLE_WINDOW:
        materiality = value.declared_alpha_band if value.declared_alpha_band is not None else DEFAULT_ALPHA_MATERIALITY
        return Conditioning(
            status=ConditioningStatus.WARNING,
            notes=(
                f"observed_alpha={value.observed_alpha:.6g}",
                f"alpha_window_span={value.alpha_window_span:.3e}",
                f"propagated_window_error={value.propagated_window_error:.3e}",
                f"materiality_limit={materiality:.3e}",
            )
            + nested_notes,
        )
    if status is AlphaProbeStatus.ALPHA_NONFINITE:
        return Conditioning(status=ConditioningStatus.WARNING, notes=("slope_fit_overflow", f"observed_slope={value.observed_slope}"))
    return Conditioning(
        status=ConditioningStatus.WARNING,
        notes=(
            f"n_observed={value.n_observed}",
            f"n_cancellation_dominated={value.n_cancellation_dominated}",
            f"n_domain_refused={value.n_domain_refused}",
        )
        + nested_notes,
    )


def _nested_conditioning_notes(value: AlphaProbeObservation) -> tuple[str, ...]:
    if value.alpha_stability_status is AlphaWindowStabilityStatus.NOT_TESTED:
        if value.standard_error is not None and value.n_observed >= 3:
            return ("nested_window_skipped: h_grid_too_short",)
        return ()
    return (
        f"alpha_stability_status={value.alpha_stability_status.value}",
        f"alpha_window_span={value.alpha_window_span:.3e}",
        f"propagated_window_error={value.propagated_window_error:.3e}",
    )
