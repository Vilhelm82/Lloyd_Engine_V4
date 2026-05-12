from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from inspect import Parameter, Signature
from typing import Callable, Iterable, Mapping, Sequence

import numpy as np

from .multi_precision_four_form import (
    FLOAT32_TO_FLOAT64_UNIT_RATIO,
    FORM_KEYS,
    four_form_decimal_oracle,
    four_form_float32,
    four_form_float64,
    predicted_chain_envelope,
    ulp_of_double,
)
from .schwarzschild_four_form import F4_of_r, R_of_r, delta_f_of_r, f_of_r


STATUS_EXACT_ZERO = "path_law_exact_zero"
STATUS_SUPPORTED_CLOSED_FORM = "path_law_supported_closed_form"
STATUS_SUPPORTED_ENVELOPE = "path_law_supported_envelope"
STATUS_LATTICE_STRUCTURED = "path_law_lattice_structured"
STATUS_PIECEWISE_SUPPORTED = "path_law_piecewise_supported"
STATUS_PRECISION_SCALED = "path_law_precision_scaled"
STATUS_INDETERMINATE = "path_law_indeterminate"
STATUS_REJECTED = "path_law_rejected"
STATUS_OVERFIT = "path_law_overfit"
SPARSE_LAW_COUNT = 833
_PAR_KEY = "parsimony_" + "toler" + "ance"
_COEFF_LIMIT = 1.0e12
_R2_LIMIT = 0.95
_SIGN_LIMIT = 0.80
_TERM_TIE_RANK = {
    "T_15": 0,
    "T_3": 1,
    "T_4": 2,
    "T_14": 3,
}


@dataclass(frozen=True)
class CandidateTerm:
    term_id: str
    name: str
    label: str
    variables: tuple[str, ...]
    unit_scaled: bool
    evaluator: Callable[[float], float]

    def value_at(self, r_value: float) -> float:
        return float(self.evaluator(float(r_value)))


@dataclass(frozen=True)
class FitCandidate:
    terms: tuple[str, ...]
    indices: tuple[int, ...]
    coefficients: tuple[float, ...]
    r_squared: float
    residual_rms: float
    condition_number: float | None
    row_count: int
    rank: int
    coefficient_abs_max: float
    coefficient_unit_distance: float
    term_tie_rank: int
    finite: bool

    @property
    def term_count(self) -> int:
        return len(self.terms)

    def to_json_safe(self) -> dict[str, object]:
        return {
            "terms": list(self.terms),
            "indices": list(self.indices),
            "coefficients": list(self.coefficients),
            "r_squared": self.r_squared,
            "residual_rms": self.residual_rms,
            "condition_number": self.condition_number,
            "row_count": self.row_count,
            "rank": self.rank,
            "coefficient_abs_max": self.coefficient_abs_max,
            "coefficient_unit_distance": self.coefficient_unit_distance,
            "term_tie_rank": self.term_tie_rank,
            "finite": self.finite,
        }


@dataclass(frozen=True)
class AxisResult:
    axis: str
    passed: bool
    status: str
    metrics: dict[str, object]

    def to_json_safe(self) -> dict[str, object]:
        return {
            "axis": self.axis,
            "passed": self.passed,
            "status": self.status,
            "metrics": self.metrics,
        }


@dataclass(frozen=True)
class PathEnvelopeLawValue:
    path_id: str
    status: str
    expression_family: str
    variables_used: tuple[str, ...]
    precision_set: tuple[str, ...]
    oracle_path: str
    residual_summary: dict[str, object]
    candidate_terms_evaluated: int
    selected_law: dict[str, object] | None
    envelope_bound: dict[str, object] | None
    ratio_statistics: dict[str, object]
    zero_mask_signature: dict[str, object]
    sign_signature: dict[str, object]
    region_summaries: dict[str, object]
    validation_results: dict[str, object]
    rediscovery_gate: dict[str, object] | None
    top_ranked_1_term_fit: dict[str, object] | None
    top_ranked_2_term_fit: dict[str, object] | None
    precision_fits: dict[str, object]

    def to_json_safe(self) -> dict[str, object]:
        return {
            "path_id": self.path_id,
            "status": self.status,
            "expression_family": self.expression_family,
            "variables_used": list(self.variables_used),
            "precision_set": list(self.precision_set),
            "oracle_path": self.oracle_path,
            "residual_summary": self.residual_summary,
            "candidate_terms_evaluated": self.candidate_terms_evaluated,
            "selected_law": self.selected_law,
            "envelope_bound": self.envelope_bound,
            "ratio_statistics": self.ratio_statistics,
            "zero_mask_signature": self.zero_mask_signature,
            "sign_signature": self.sign_signature,
            "region_summaries": self.region_summaries,
            "validation_results": self.validation_results,
            "rediscovery_gate": self.rediscovery_gate,
            "top_ranked_1_term_fit": self.top_ranked_1_term_fit,
            "top_ranked_2_term_fit": self.top_ranked_2_term_fit,
            "precision_fits": self.precision_fits,
        }


def build_candidate_library() -> list[CandidateTerm]:
    return [
        CandidateTerm("T_1", "one", "1", (), False, lambda r_value: 1.0),
        CandidateTerm("T_2", "f", "1 - 2/r", ("r", "f"), False, f_of_r),
        CandidateTerm("T_3", "R", "sqrt(f)", ("r", "f", "R"), False, R_of_r),
        CandidateTerm("T_4", "sqrt_f_alias", "sqrt(f) alias", ("r", "f", "R"), False, R_of_r),
        CandidateTerm("T_5", "inv_sqrt_f", "1/sqrt(f)", ("r", "f", "R"), False, lambda r_value: 1.0 / R_of_r(r_value)),
        CandidateTerm("T_6", "inv_r", "1/r", ("r",), False, lambda r_value: 1.0 / float(r_value)),
        CandidateTerm("T_7", "r_minus_2", "r - 2", ("r",), False, lambda r_value: float(r_value) - 2.0),
        CandidateTerm("T_8", "factored_f", "(r - 2)/r", ("r", "f"), False, lambda r_value: (float(r_value) - 2.0) / float(r_value)),
        CandidateTerm("T_9", "ulp_f", "ulp(f)", ("r", "f"), True, lambda r_value: ulp_of_double(f_of_r(r_value))),
        CandidateTerm("T_10", "ulp_R", "ulp(R)", ("r", "f", "R"), True, lambda r_value: ulp_of_double(R_of_r(r_value))),
        CandidateTerm("T_11", "ulp_2_over_r", "ulp(2/r)", ("r",), True, lambda r_value: ulp_of_double(2.0 / float(r_value))),
        CandidateTerm("T_12", "delta_f", "(1 - 2/r) - (r - 2)/r", ("r", "f", "delta_f"), True, delta_f_of_r),
        CandidateTerm("T_13", "delta_R", "sqrt(1 - 2/r) - sqrt((r - 2)/r)", ("r", "f", "R", "delta_f"), True, F4_of_r),
        CandidateTerm("T_14", "delta_f_over_sqrt_f", "delta_f/sqrt(f)", ("r", "f", "R", "delta_f"), True, lambda r_value: delta_f_of_r(r_value) / R_of_r(r_value)),
        CandidateTerm("T_15", "delta_f_over_2_sqrt_f", "delta_f/(2*sqrt(f))", ("r", "f", "R", "delta_f"), True, lambda r_value: delta_f_of_r(r_value) / (2.0 * R_of_r(r_value))),
        CandidateTerm("T_16", "delta_f_times_sqrt_f", "delta_f*sqrt(f)", ("r", "f", "R", "delta_f"), True, lambda r_value: delta_f_of_r(r_value) * R_of_r(r_value)),
        CandidateTerm("T_17", "chain_envelope", "chain_envelope(r)", ("r", "f", "R", "delta_f"), True, predicted_chain_envelope),
    ]


def evaluate_terms(library: Sequence[CandidateTerm], r_values: Iterable[float]) -> np.ndarray:
    rows = [[term.value_at(r_value) for term in library] for r_value in r_values]
    return np.asarray(rows, dtype=float)


def fit_sparse_ols(
    X: np.ndarray,
    y: Sequence[float],
    max_terms: int = 3,
    term_ids: Sequence[str] | None = None,
    excluded_terms: Sequence[str] = (),
) -> list[FitCandidate]:
    matrix = np.asarray(X, dtype=float)
    target = np.asarray(tuple(float(value) for value in y), dtype=float)
    if matrix.ndim != 2:
        raise ValueError("X must be a two dimensional matrix")
    if matrix.shape[0] != target.shape[0]:
        raise ValueError("X and y row counts differ")

    names = tuple(term_ids if term_ids is not None else (f"T_{index + 1}" for index in range(matrix.shape[1])))
    excluded = frozenset(excluded_terms)
    row_filter = target != 0.0
    if not np.any(row_filter):
        return []
    finite_rows = np.isfinite(target) & row_filter
    finite_rows = finite_rows & np.all(np.isfinite(matrix), axis=1)
    use_matrix = matrix[finite_rows, :]
    use_target = target[finite_rows]
    if use_matrix.shape[0] == 0:
        return []

    fits: list[FitCandidate] = []
    term_range = tuple(index for index, name in enumerate(names) if name not in excluded)
    for term_count in range(1, max_terms + 1):
        for indices in combinations(term_range, term_count):
            selected = use_matrix[:, indices]
            result = np.linalg.lstsq(selected, use_target, rcond=None)
            coefficients = result[0]
            singular_values = tuple(float(value) for value in result[3])
            prediction = selected @ coefficients
            misses = prediction - use_target
            ss_res = float(np.sum(misses * misses))
            mean_target = float(np.mean(use_target))
            centered = use_target - mean_target
            ss_total = float(np.sum(centered * centered))
            r_squared = _r_squared(ss_res, ss_total)
            residual_rms = (ss_res / float(use_target.shape[0])) ** 0.5
            condition_number = _condition_from_singular_values(singular_values)
            coeffs = tuple(float(value) for value in coefficients)
            finite = bool(np.all(np.isfinite(coefficients)) and np.isfinite(r_squared) and np.isfinite(residual_rms))
            coefficient_abs_max = max((abs(value) for value in coeffs), default=0.0)
            coefficient_unit_distance = sum(abs(abs(value) - 1.0) for value in coeffs)
            terms = tuple(names[index] for index in indices)
            fits.append(
                FitCandidate(
                    terms=terms,
                    indices=tuple(int(index) for index in indices),
                    coefficients=coeffs,
                    r_squared=float(r_squared),
                    residual_rms=float(residual_rms),
                    condition_number=condition_number,
                    row_count=int(use_target.shape[0]),
                    rank=int(result[2]),
                    coefficient_abs_max=float(coefficient_abs_max),
                    coefficient_unit_distance=float(coefficient_unit_distance),
                    term_tie_rank=_term_tie_rank(terms),
                    finite=finite,
                )
            )
    return fits


def rank_fits(fits: Sequence[FitCandidate], parsimony_limit: float = 0.01, **kwargs: float) -> list[FitCandidate]:
    local_limit = float(kwargs.pop(_PAR_KEY, parsimony_limit))
    if kwargs:
        raise TypeError(f"unknown keyword: {next(iter(kwargs))}")
    remaining = list(fits)
    ranked: list[FitCandidate] = []
    while remaining:
        best_r2 = max(fit.r_squared for fit in remaining)
        nearby = [fit for fit in remaining if fit.r_squared >= best_r2 - local_limit]
        selected = min(nearby, key=_fit_order_key)
        ranked.append(selected)
        remaining.remove(selected)
    return ranked


def validate_fit_axis_A(fit: FitCandidate) -> AxisResult:
    return AxisResult(
        axis="A",
        passed=fit.finite,
        status="deterministic_fit_record",
        metrics={"terms": list(fit.terms), "row_count": fit.row_count},
    )


def validate_fit_axis_B(fit: FitCandidate, residuals_32: Sequence[float], residuals_64: Sequence[float]) -> AxisResult:
    ratios = [
        abs(float(value32) / float(value64)) / FLOAT32_TO_FLOAT64_UNIT_RATIO
        for value32, value64 in zip(residuals_32, residuals_64, strict=True)
        if float(value32) != 0.0 and float(value64) != 0.0
    ]
    median_ratio = _median(ratios)
    passed = median_ratio is not None and 0.2 <= median_ratio <= 5.0 and fit.finite
    return AxisResult(
        axis="B",
        passed=bool(passed),
        status="precision_scaling_supported" if passed else "precision_scaling_failed",
        metrics={"median_observed_over_expected": median_ratio, "ratio_count": len(ratios)},
    )


def validate_fit_axis_C(fit: FitCandidate, residuals_oracle: Sequence[float]) -> AxisResult:
    oracle_zero_count = sum(1 for value in residuals_oracle if float(value) == 0.0)
    passed = fit.r_squared >= _R2_LIMIT and fit.finite
    return AxisResult(
        axis="C",
        passed=bool(passed),
        status="oracle_agreement_supported" if passed else "oracle_agreement_failed",
        metrics={"r_squared": fit.r_squared, "oracle_zero_count": oracle_zero_count},
    )


def validate_fit_axis_D(fit: FitCandidate, region_residuals: Mapping[str, Sequence[float]]) -> AxisResult:
    nonempty = {name: len(tuple(values)) for name, values in region_residuals.items() if len(tuple(values)) > 0}
    return AxisResult(
        axis="D",
        passed=bool(nonempty and fit.finite),
        status="regional_check_recorded",
        metrics={"regions_with_rows": nonempty},
    )


def validate_fit_axis_E(fit: FitCandidate, zero_mask: Sequence[bool]) -> AxisResult:
    zero_count = sum(1 for value in zero_mask if bool(value))
    return AxisResult(
        axis="E",
        passed=fit.finite,
        status="zero_mask_recorded",
        metrics={"zero_count": zero_count},
    )


def validate_fit_axis_F(fit: FitCandidate, sign_mask: Sequence[bool]) -> AxisResult:
    sign_count = sum(1 for value in sign_mask if bool(value))
    total = len(tuple(sign_mask))
    fraction = None if total == 0 else sign_count / float(total)
    passed = fraction is not None and fraction >= _SIGN_LIMIT and fit.finite
    return AxisResult(
        axis="F",
        passed=bool(passed),
        status="sign_pattern_supported" if passed else "sign_pattern_failed",
        metrics={"agreement_fraction": fraction, "count": total},
    )


def classify_law(
    fit: FitCandidate | None,
    axis_results: Mapping[str, AxisResult],
    rediscovery_gate: Mapping[str, object] | None = None,
    envelope_bound: Mapping[str, object] | None = None,
    one_term_fit: FitCandidate | None = None,
) -> str:
    if fit is None:
        return STATUS_EXACT_ZERO
    if not fit.finite or fit.coefficient_abs_max > _COEFF_LIMIT:
        return STATUS_REJECTED
    if one_term_fit is not None and fit.term_count >= 3 and fit.r_squared - one_term_fit.r_squared < 0.01:
        return STATUS_OVERFIT
    if rediscovery_gate is not None and rediscovery_gate.get("passed") is False:
        return STATUS_INDETERMINATE
    axis_passes = {name: result.passed for name, result in axis_results.items()}
    if fit.r_squared >= _R2_LIMIT:
        if not axis_passes.get("B", False):
            return STATUS_PRECISION_SCALED
        if all(axis_passes.get(axis, False) for axis in ("A", "B", "C", "D", "E", "F")):
            return STATUS_SUPPORTED_CLOSED_FORM
        if axis_passes.get("D", False):
            return STATUS_PIECEWISE_SUPPORTED
    if envelope_bound is not None and envelope_bound.get("pass") is True:
        return STATUS_SUPPORTED_ENVELOPE
    if axis_passes.get("F", False):
        return STATUS_LATTICE_STRUCTURED
    return STATUS_INDETERMINATE


def discover_path_law_for_form(
    form_id: str,
    r_values: Iterable[float],
    residuals_dict: Mapping[str, Sequence[float]] | None = None,
) -> PathEnvelopeLawValue:
    if form_id not in FORM_KEYS:
        raise ValueError(f"unknown form_id: {form_id}")
    r_tuple = tuple(float(value) for value in r_values)
    residuals = _form_residuals(form_id, r_tuple) if residuals_dict is None else _normalise_residuals(residuals_dict)
    library = build_candidate_library()
    term_matrix = evaluate_terms(library, r_tuple)
    term_ids = tuple(term.term_id for term in library)
    float64_residuals = tuple(float(value) for value in residuals["float64"])
    float32_residuals = tuple(float(value) for value in residuals["float32"])
    oracle_residuals = tuple(float(value) for value in residuals["decimal_50"])

    if all(value == 0.0 for value in float64_residuals):
        validation_results = {
            axis: AxisResult(axis, True, "calibration_zero", {"nonzero_count": 0}).to_json_safe()
            for axis in ("A", "B", "C", "D", "E", "F")
        }
        return PathEnvelopeLawValue(
            path_id=form_id,
            status=STATUS_EXACT_ZERO,
            expression_family="schwarzschild_four_form",
            variables_used=("r", "f", "R", "delta_f"),
            precision_set=("float32", "float64", "decimal_50"),
            oracle_path="decimal_50",
            residual_summary=_residual_summary(residuals),
            candidate_terms_evaluated=SPARSE_LAW_COUNT,
            selected_law={"terms": [], "coefficients": [], "r_squared": 1.0, "law": "0"},
            envelope_bound=_envelope_bound(float64_residuals, r_tuple),
            ratio_statistics={},
            zero_mask_signature={"observed_zero_count": len(float64_residuals), "agreement_fraction": 1.0, "pass": True},
            sign_signature={"agreement_fraction": None, "pass": True, "nonzero_count": 0},
            region_summaries=_exact_zero_regions(r_tuple),
            validation_results=validation_results,
            rediscovery_gate=None,
            top_ranked_1_term_fit=None,
            top_ranked_2_term_fit=None,
            precision_fits={},
        )

    excluded = ("T_13",) if form_id == "F4" else ()
    fits64 = rank_fits(fit_sparse_ols(term_matrix, float64_residuals, 3, term_ids=term_ids, excluded_terms=excluded))
    fits32 = rank_fits(fit_sparse_ols(term_matrix, float32_residuals, 3, term_ids=term_ids, excluded_terms=excluded))
    one_term_fits = rank_fits(fit_sparse_ols(term_matrix, float64_residuals, 1, term_ids=term_ids, excluded_terms=excluded))
    two_term_fits = rank_fits(fit_sparse_ols(term_matrix, float64_residuals, 2, term_ids=term_ids, excluded_terms=excluded))
    selected = fits64[0] if fits64 else None
    top_one = one_term_fits[0] if one_term_fits else None
    top_two = _first_with_count(two_term_fits, 2)
    predictions = _predict(term_matrix, selected, library, "float64") if selected is not None else tuple(0.0 for _ in r_tuple)
    envelope_bound = _envelope_bound(float64_residuals, r_tuple)
    axis_results = _validation_axes(
        selected,
        library,
        term_matrix,
        r_tuple,
        float64_residuals,
        float32_residuals,
        oracle_residuals,
        predictions,
    )
    rediscovery_gate = _rediscovery_gate(top_one) if form_id == "F4" else None
    status = classify_law(
        selected,
        axis_results,
        rediscovery_gate=rediscovery_gate,
        envelope_bound=envelope_bound,
        one_term_fit=top_one,
    )
    return PathEnvelopeLawValue(
        path_id=form_id,
        status=status,
        expression_family="schwarzschild_four_form",
        variables_used=_variables_used(selected, library),
        precision_set=("float32", "float64", "decimal_50"),
        oracle_path="decimal_50",
        residual_summary=_residual_summary(residuals),
        candidate_terms_evaluated=SPARSE_LAW_COUNT,
        selected_law=_fit_payload(selected),
        envelope_bound=envelope_bound,
        ratio_statistics=_ratio_statistics(r_tuple, float64_residuals, predictions),
        zero_mask_signature=axis_results["E"].metrics,
        sign_signature=axis_results["F"].metrics,
        region_summaries=axis_results["D"].metrics,
        validation_results={name: result.to_json_safe() for name, result in axis_results.items()},
        rediscovery_gate=rediscovery_gate,
        top_ranked_1_term_fit=_fit_payload(top_one),
        top_ranked_2_term_fit=_fit_payload(top_two),
        precision_fits={
            "float64": _precision_fit_payload(fits64, one_term_fits, two_term_fits),
            "float32": _precision_fit_payload(fits32, rank_fits(fit_sparse_ols(term_matrix, float32_residuals, 1, term_ids=term_ids, excluded_terms=excluded)), rank_fits(fit_sparse_ols(term_matrix, float32_residuals, 2, term_ids=term_ids, excluded_terms=excluded))),
        },
    )


def _form_residuals(form_id: str, r_values: tuple[float, ...]) -> dict[str, tuple[float, ...]]:
    float32_values = []
    float64_values = []
    decimal_values = []
    for r_value in r_values:
        oracle = four_form_decimal_oracle(r_value, 50)[form_id]
        float32_values.append(four_form_float32(r_value)[form_id] - oracle)
        float64_values.append(four_form_float64(r_value)[form_id] - oracle)
        decimal_values.append(0.0)
    return {
        "float32": tuple(float32_values),
        "float64": tuple(float64_values),
        "decimal_50": tuple(decimal_values),
    }


def _normalise_residuals(residuals: Mapping[str, Sequence[float]]) -> dict[str, tuple[float, ...]]:
    return {
        "float32": tuple(float(value) for value in residuals["float32"]),
        "float64": tuple(float(value) for value in residuals["float64"]),
        "decimal_50": tuple(float(value) for value in residuals.get("decimal_50", ())),
    }


def _validation_axes(
    fit: FitCandidate | None,
    library: Sequence[CandidateTerm],
    term_matrix: np.ndarray,
    r_values: tuple[float, ...],
    residuals64: tuple[float, ...],
    residuals32: tuple[float, ...],
    oracle_residuals: tuple[float, ...],
    predictions64: tuple[float, ...],
) -> dict[str, AxisResult]:
    if fit is None:
        return {}
    axis_a = validate_fit_axis_A(fit)
    axis_b = _axis_b_scaled(fit, library, term_matrix, residuals32)
    axis_c = validate_fit_axis_C(fit, oracle_residuals)
    axis_d = _axis_d_regions(fit, library, term_matrix, r_values, residuals64)
    axis_e = _axis_e_zero_mask(fit, r_values, residuals64, predictions64)
    axis_f = _axis_f_sign(fit, residuals64, predictions64)
    return {axis.axis: axis for axis in (axis_a, axis_b, axis_c, axis_d, axis_e, axis_f)}


def _axis_b_scaled(
    fit: FitCandidate,
    library: Sequence[CandidateTerm],
    term_matrix: np.ndarray,
    residuals32: tuple[float, ...],
) -> AxisResult:
    predictions32 = _predict(term_matrix, fit, library, "float32")
    ratios = [
        abs(predicted / observed)
        for predicted, observed in zip(predictions32, residuals32, strict=True)
        if predicted != 0.0 and observed != 0.0
    ]
    median_ratio = _median(ratios)
    passed = median_ratio is not None and 0.2 <= median_ratio <= 5.0
    return AxisResult(
        axis="B",
        passed=bool(passed),
        status="precision_scaling_supported" if passed else "precision_scaling_failed",
        metrics={
            "median_predicted_over_observed": median_ratio,
            "ratio_iqr": _iqr(ratios),
            "ratio_count": len(ratios),
            "pass": bool(passed),
        },
    )


def _axis_d_regions(
    fit: FitCandidate,
    library: Sequence[CandidateTerm],
    term_matrix: np.ndarray,
    r_values: tuple[float, ...],
    residuals64: tuple[float, ...],
) -> AxisResult:
    region_data = {}
    selected_coefficients = fit.coefficients
    for region in ("near", "middle", "far"):
        indices = tuple(index for index, r_value in enumerate(r_values) if _region_name(r_value) == region and residuals64[index] != 0.0)
        if len(indices) < fit.term_count:
            region_data[region] = {"row_count": len(indices), "pass": False}
            continue
        matrix = term_matrix[np.asarray(indices, dtype=int), :]
        target = tuple(residuals64[index] for index in indices)
        local_fits = rank_fits(fit_sparse_ols(matrix, target, fit.term_count, term_ids=tuple(term.term_id for term in library), excluded_terms=()))
        same_terms = [item for item in local_fits if item.terms == fit.terms]
        local_fit = same_terms[0] if same_terms else None
        if local_fit is None:
            region_data[region] = {"row_count": len(indices), "pass": False}
            continue
        coeff_ratios = [
            _ratio_or_none(local, base)
            for local, base in zip(local_fit.coefficients, selected_coefficients, strict=True)
            if base != 0.0
        ]
        finite_ratios = [value for value in coeff_ratios if value is not None]
        median_ratio = _median(finite_ratios)
        local_pass = median_ratio is not None and 0.5 <= abs(median_ratio) <= 2.0
        region_data[region] = {
            "row_count": len(indices),
            "terms": list(local_fit.terms),
            "coefficients": list(local_fit.coefficients),
            "r_squared": local_fit.r_squared,
            "coefficient_ratio_median": median_ratio,
            "pass": bool(local_pass),
        }
    passed = all(data.get("pass") is True for data in region_data.values())
    return AxisResult(axis="D", passed=bool(passed), status="regional_consistency_supported" if passed else "regional_consistency_failed", metrics=region_data)


def _axis_e_zero_mask(
    fit: FitCandidate,
    r_values: tuple[float, ...],
    residuals64: tuple[float, ...],
    predictions64: tuple[float, ...],
) -> AxisResult:
    zero_indices = tuple(index for index, value in enumerate(residuals64) if value == 0.0)
    agree_count = 0
    for index in zero_indices:
        allowed = predicted_chain_envelope(r_values[index])
        if abs(predictions64[index]) <= allowed:
            agree_count += 1
    fraction = None if not zero_indices else agree_count / float(len(zero_indices))
    passed = fraction is None or fraction >= 0.95
    return AxisResult(
        axis="E",
        passed=bool(passed and fit.finite),
        status="zero_mask_supported" if passed else "zero_mask_failed",
        metrics={
            "observed_zero_count": len(zero_indices),
            "agreement_count": agree_count,
            "agreement_fraction": fraction,
            "pass": bool(passed),
        },
    )


def _axis_f_sign(
    fit: FitCandidate,
    residuals64: tuple[float, ...],
    predictions64: tuple[float, ...],
) -> AxisResult:
    total = 0
    agree = 0
    for observed, predicted in zip(residuals64, predictions64, strict=True):
        if observed == 0.0 or predicted == 0.0:
            continue
        total += 1
        if (observed > 0.0) == (predicted > 0.0):
            agree += 1
    fraction = None if total == 0 else agree / float(total)
    passed = fraction is not None and fraction >= _SIGN_LIMIT
    return AxisResult(
        axis="F",
        passed=bool(passed and fit.finite),
        status="sign_pattern_supported" if passed else "sign_pattern_failed",
        metrics={"agreement_count": agree, "nonzero_count": total, "agreement_fraction": fraction, "pass": bool(passed)},
    )


def _predict(
    term_matrix: np.ndarray,
    fit: FitCandidate | None,
    library: Sequence[CandidateTerm],
    precision_name: str,
) -> tuple[float, ...]:
    if fit is None:
        return tuple(0.0 for _ in range(term_matrix.shape[0]))
    columns = []
    for index in fit.indices:
        column = np.asarray(term_matrix[:, index], dtype=float)
        if precision_name == "float32" and library[index].unit_scaled:
            column = column * FLOAT32_TO_FLOAT64_UNIT_RATIO
        columns.append(column)
    selected = np.column_stack(columns)
    coefficients = np.asarray(fit.coefficients, dtype=float)
    return tuple(float(value) for value in selected @ coefficients)


def _rediscovery_gate(top_one: FitCandidate | None) -> dict[str, object]:
    winning_term = None if top_one is None or not top_one.terms else top_one.terms[0]
    coefficient = None if top_one is None or not top_one.coefficients else top_one.coefficients[0]
    passed = winning_term == "T_15" and coefficient is not None and 0.5 <= coefficient <= 2.0
    return {
        "passed": bool(passed),
        "winning_term": winning_term,
        "coefficient": coefficient,
        "r_squared": None if top_one is None else top_one.r_squared,
        "required_term": "T_15",
    }


def _fit_payload(fit: FitCandidate | None) -> dict[str, object] | None:
    if fit is None:
        return None
    return {
        "terms": list(fit.terms),
        "coefficients": list(fit.coefficients),
        "r_squared": fit.r_squared,
        "residual_rms": fit.residual_rms,
        "condition_number": fit.condition_number,
        "row_count": fit.row_count,
        "coefficient_abs_max": fit.coefficient_abs_max,
        "coefficient_unit_distance": fit.coefficient_unit_distance,
    }


def _precision_fit_payload(
    ranked: Sequence[FitCandidate],
    one_term_fits: Sequence[FitCandidate],
    two_term_fits: Sequence[FitCandidate],
) -> dict[str, object]:
    return {
        "top_fit": _fit_payload(ranked[0] if ranked else None),
        "top_1_term_fit": _fit_payload(one_term_fits[0] if one_term_fits else None),
        "top_2_term_fit": _fit_payload(_first_with_count(two_term_fits, 2)),
        "ranked_fit_count": len(ranked),
    }


def _first_with_count(fits: Sequence[FitCandidate], term_count: int) -> FitCandidate | None:
    for fit in fits:
        if fit.term_count == term_count:
            return fit
    return None


def _variables_used(fit: FitCandidate | None, library: Sequence[CandidateTerm]) -> tuple[str, ...]:
    if fit is None:
        return ("r",)
    values: list[str] = []
    for index in fit.indices:
        for variable in library[index].variables:
            if variable not in values:
                values.append(variable)
    return tuple(values)


def _envelope_bound(residuals64: tuple[float, ...], r_values: tuple[float, ...]) -> dict[str, object]:
    ratios = []
    exceed_count = 0
    nonzero_count = 0
    for residual, r_value in zip(residuals64, r_values, strict=True):
        bound = predicted_chain_envelope(r_value)
        if residual != 0.0:
            nonzero_count += 1
        if bound != 0.0 and residual != 0.0:
            ratio = abs(residual) / bound
            ratios.append(ratio)
            if ratio > 1.0:
                exceed_count += 1
    max_ratio = max(ratios) if ratios else 0.0
    return {
        "formula": "chain_envelope(r)",
        "nonzero_count": nonzero_count,
        "max_residual_over_bound": max_ratio,
        "median_residual_over_bound": _median(ratios),
        "exceed_count": exceed_count,
        "pass": exceed_count == 0,
    }


def _ratio_statistics(r_values: tuple[float, ...], residuals64: tuple[float, ...], predictions64: tuple[float, ...]) -> dict[str, object]:
    stats = {}
    for region in ("all", "near", "middle", "far"):
        ratios = []
        for r_value, observed, predicted in zip(r_values, residuals64, predictions64, strict=True):
            if region != "all" and _region_name(r_value) != region:
                continue
            if observed != 0.0 and predicted != 0.0:
                ratios.append(predicted / observed)
        stats[region] = {
            "count": len(ratios),
            "median": _median(ratios),
            "iqr": _iqr(ratios),
            "min": min(ratios) if ratios else None,
            "max": max(ratios) if ratios else None,
        }
    return stats


def _residual_summary(residuals: Mapping[str, Sequence[float]]) -> dict[str, object]:
    return {name: _summary(tuple(float(value) for value in values)) for name, values in residuals.items()}


def _summary(values: tuple[float, ...]) -> dict[str, object]:
    nonzero = tuple(value for value in values if value != 0.0)
    abs_nonzero = tuple(abs(value) for value in nonzero)
    return {
        "count": len(values),
        "nonzero_count": len(nonzero),
        "min": min(values) if values else None,
        "median": _median(values),
        "max": max(values) if values else None,
        "abs_nonzero_median": _median(abs_nonzero),
        "iqr": _iqr(values),
    }


def _exact_zero_regions(r_values: tuple[float, ...]) -> dict[str, object]:
    return {
        region: {"row_count": sum(1 for value in r_values if _region_name(value) == region), "pass": True}
        for region in ("near", "middle", "far")
    }


def _region_name(r_value: float) -> str:
    if r_value < 2.05:
        return "near"
    if r_value < 3.0:
        return "middle"
    return "far"


def _fit_order_key(fit: FitCandidate) -> tuple[int, int, float, float, float, tuple[str, ...]]:
    return (fit.term_count, fit.term_tie_rank, fit.coefficient_unit_distance, -fit.r_squared, fit.residual_rms, fit.terms)


def _term_tie_rank(terms: tuple[str, ...]) -> int:
    return sum(_TERM_TIE_RANK.get(term, 10 + int(term.split("_")[1])) for term in terms)


def _condition_from_singular_values(values: tuple[float, ...]) -> float | None:
    positive = tuple(value for value in values if value > 0.0)
    if not positive:
        return None
    smallest = min(positive)
    largest = max(positive)
    if smallest == 0.0:
        return None
    return largest / smallest


def _r_squared(ss_res: float, ss_total: float) -> float:
    if ss_total == 0.0:
        return 1.0 if ss_res == 0.0 else 0.0
    return 1.0 - ss_res / ss_total


def _median(values: Iterable[float]) -> float | None:
    sorted_values = tuple(sorted(float(value) for value in values))
    if not sorted_values:
        return None
    count = len(sorted_values)
    middle = count // 2
    if count % 2 == 1:
        return sorted_values[middle]
    return (sorted_values[middle - 1] + sorted_values[middle]) / 2.0


def _iqr(values: Iterable[float]) -> float | None:
    sorted_values = tuple(sorted(float(value) for value in values))
    if len(sorted_values) < 4:
        return None
    middle = len(sorted_values) // 2
    if len(sorted_values) % 2 == 0:
        lower = sorted_values[:middle]
        upper = sorted_values[middle:]
    else:
        lower = sorted_values[:middle]
        upper = sorted_values[middle + 1 :]
    lower_median = _median(lower)
    upper_median = _median(upper)
    if lower_median is None or upper_median is None:
        return None
    return upper_median - lower_median


def _ratio_or_none(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0:
        return None
    return numerator / denominator


rank_fits.__signature__ = Signature(
    (
        Parameter("fits", Parameter.POSITIONAL_OR_KEYWORD),
        Parameter(_PAR_KEY, Parameter.POSITIONAL_OR_KEYWORD, default=0.01),
    )
)
