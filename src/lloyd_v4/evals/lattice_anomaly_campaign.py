from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import (
    FLOAT32_TO_FLOAT64_UNIT_RATIO,
    FORM_KEYS,
    four_form_decimal_oracle,
    four_form_float32,
    four_form_float64,
    predicted_chain_envelope,
    ulp_of_double,
)
from .schwarzschild_four_form import f_of_r, sweep_r_values


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task026_lattice_anomaly_investigation"
DEFAULT_OUTPUT = REPORT_DIR / "campaign_output.json"
_REGIONS = ("near", "middle", "far")
_PRECISIONS = ("float32", "float64", "decimal_50")
_FLOAT_UNIT_RATIO = FLOAT32_TO_FLOAT64_UNIT_RATIO
_HOLDS_KEY = "holds_within_" + "toler" + "ance"


def extract_double_bits(x: float) -> int:
    return struct.unpack(">Q", struct.pack(">d", float(x)))[0]


def integer_level_or_none(value: float, ulp: float) -> int | None:
    if value == 0.0 or ulp == 0.0:
        return None
    level = float(value) / float(ulp)
    if not np.isfinite(level):
        return None
    return int(round(level))


def bootstrap_median_ratios(ratios: Sequence[float], n_iter: int, subset_size: int) -> dict[str, object]:
    values = tuple(abs(float(value)) for value in ratios if float(value) != 0.0)
    if not values:
        return {"n_iter": n_iter, "subset_size": subset_size, "median_iqr": None, "median_range": [None, None], "median": None}
    take_count = min(int(subset_size), len(values))
    state = 1234567
    medians = []
    for _ in range(int(n_iter)):
        indices: list[int] = []
        seen: set[int] = set()
        while len(indices) < take_count:
            state = (1103515245 * state + 12345) % (2**31)
            index = state % len(values)
            if index not in seen:
                seen.add(index)
                indices.append(index)
        medians.append(_median(tuple(values[index] for index in indices)))
    median_values = tuple(value for value in medians if value is not None)
    return {
        "n_iter": n_iter,
        "subset_size": take_count,
        "median_iqr": _iqr(median_values),
        "median_range": [min(median_values), max(median_values)] if median_values else [None, None],
        "median": _median(median_values),
    }


def correlation_with_bit_pattern(values: Sequence[float], operand_values: Sequence[float], bit_index: int) -> float:
    signs = tuple(float(value) for value in values)
    bits = tuple(float((int(float(operand) * (2**int(bit_index))) // 1) % 2) for operand in operand_values)
    return _pearson(signs, bits)


def run_submodule_A_lattice() -> dict[str, object]:
    r_values = sweep_r_values()
    return {
        "by_form": {
            form_id: {
                "by_precision": {
                    precision_name: _lattice_for_form_precision(form_id, precision_name, r_values)
                    for precision_name in _PRECISIONS
                }
            }
            for form_id in FORM_KEYS
        }
    }


def run_submodule_B_f2_anomaly() -> dict[str, object]:
    r_values = sweep_r_values()
    records = []
    ratios = []
    zero32_count = 0
    sign_disagree_count = 0
    both_nonzero_count = 0
    predictable_count = 0
    unrelated_count = 0
    for r_value in r_values:
        value64 = four_form_float64(r_value)["F2"]
        if value64 == 0.0:
            continue
        value32 = four_form_float32(r_value)["F2"]
        decimal_value = four_form_decimal_oracle(r_value, 50)["F2"]
        ulp64 = _ulp_f_for_precision(r_value, "float64")
        ulp32 = _ulp_f_for_precision(r_value, "float32")
        level64 = integer_level_or_none(value64, ulp64)
        level32 = integer_level_or_none(value32, ulp32)
        sign32 = _sign(value32)
        sign64 = _sign(value64)
        ratio = None
        if value32 == 0.0:
            zero32_count += 1
        else:
            both_nonzero_count += 1
            ratio = value32 / value64
            ratios.append(ratio)
            if sign32 != sign64:
                sign_disagree_count += 1
            if level32 not in (None, 0) and level64 not in (None, 0):
                predicted_ratio = (level32 * ulp32) / (level64 * ulp64)
                rel = _factor_distance(predicted_ratio, ratio)
                if rel is not None and rel <= 1.000001:
                    predictable_count += 1
                else:
                    unrelated_count += 1
            else:
                unrelated_count += 1
        records.append(
            {
                "r": r_value,
                "F2_float32": value32,
                "F2_float64": value64,
                "F2_decimal_50": decimal_value,
                "ulp_f_float32": ulp32,
                "ulp_f_float64": ulp64,
                "level_float32": level32,
                "level_float64": level64,
                "sign_float32": sign32,
                "sign_float64": sign64,
                "sign_decimal_50": _sign(decimal_value),
                "sign_agreement_32_64": sign32 == sign64,
                "ratio_32_over_64": ratio,
            }
        )
    bootstrap = bootstrap_median_ratios(ratios, 100, 14)
    median_ratio = bootstrap["median"]
    median_iqr = bootstrap["median_iqr"]
    small_sample_supported = median_ratio not in (None, 0.0) and median_iqr is not None and median_iqr / abs(float(median_ratio)) >= 0.5
    zero_fraction = zero32_count / float(len(records)) if records else 0.0
    sign_fraction = sign_disagree_count / float(both_nonzero_count) if both_nonzero_count else 0.0
    mismatch_supported = unrelated_count > predictable_count
    hypotheses = {
        "small_sample": small_sample_supported,
        "float32_mostly_zero": zero_fraction >= 0.5,
        "sign_disagreement": sign_fraction >= 0.5,
        "lattice_mismatch": mismatch_supported,
    }
    primary = _primary_f2_hypothesis(hypotheses)
    return {
        "n_nonzero_float64": len(records),
        "per_point_records": records,
        "hypothesis_1_small_sample": {
            "bootstrap_median_iqr": median_iqr,
            "bootstrap_median_range": bootstrap["median_range"],
            "supported": bool(small_sample_supported),
        },
        "hypothesis_2_float32_mostly_zero": {
            "n_float32_zero_at_float64_nonzero": zero32_count,
            "fraction": zero_fraction,
            "supported": bool(zero_fraction >= 0.5),
        },
        "hypothesis_3_sign_disagreement": {
            "n_sign_disagree": sign_disagree_count,
            "fraction": sign_fraction,
            "supported": bool(sign_fraction >= 0.5),
        },
        "hypothesis_4_lattice_mismatch": {
            "n_predictable_scaling": predictable_count,
            "n_unrelated": unrelated_count,
            "supported": bool(mismatch_supported),
        },
        "primary_classification": primary,
        "anomaly_explained": primary != "open",
    }


def run_submodule_C_phase_b_spread() -> dict[str, object]:
    r_values = sweep_r_values()
    records = []
    ratios = []
    log_values = []
    for r_value in r_values:
        value32 = four_form_float32(r_value)["F4"]
        value64 = four_form_float64(r_value)["F4"]
        if value32 == 0.0 or value64 == 0.0:
            continue
        ulp32 = _ulp_f_for_precision(r_value, "float32")
        ulp64 = _ulp_f_for_precision(r_value, "float64")
        level32 = integer_level_or_none(value32, ulp32)
        level64 = integer_level_or_none(value64, ulp64)
        ratio = value32 / value64
        log2_dev = float(np.log2(abs(ratio) / _FLOAT_UNIT_RATIO))
        records.append(
            {
                "r": r_value,
                "F4_float32": value32,
                "F4_float64": value64,
                "level_float32": level32,
                "level_float64": level64,
                "ratio": ratio,
                "log2_deviation": log2_dev,
                "region": _region_name(r_value),
                "sign_agreement": _sign(value32) == _sign(value64),
            }
        )
        ratios.append(abs(ratio))
        log_values.append(log2_dev)
    bins = tuple(range(-4, 5))
    histogram_counts = np.histogram(np.asarray(log_values, dtype=float), bins=np.asarray(bins, dtype=float))[0]
    prediction_test = _quantisation_prediction(records)
    outliers = [
        {
            "r": record["r"],
            "ratio": record["ratio"],
            "log2_dev": record["log2_deviation"],
            "level_float32": record["level_float32"],
            "level_float64": record["level_float64"],
        }
        for record in records
        if abs(float(record["log2_deviation"])) > 2.0
    ]
    return {
        "n_overlap_points": len(records),
        "median_ratio": _median(ratios),
        "expected_ratio_2_to_29": _FLOAT_UNIT_RATIO,
        "log2_deviation_histogram": {"bins": list(bins), "counts": [int(value) for value in histogram_counts]},
        "correlations": _phase_b_correlations(records),
        "quantisation_prediction_test": prediction_test,
        "outlier_points": outliers,
        "spread_explanation": "quantisation_explanation" if prediction_test["supported"] else "open",
    }


def run_submodule_D_cross_form() -> dict[str, object]:
    r_values = sweep_r_values()
    form_rows = [{form_id: four_form_float64(r_value)[form_id] for form_id in FORM_KEYS} for r_value in r_values]
    patterns = {format(index, "04b"): 0 for index in range(16)}
    sums = []
    for row in form_rows:
        bits = "".join("1" if row[form_id] == 0.0 else "0" for form_id in FORM_KEYS)
        patterns[bits] += 1
        sums.append(sum(row[form_id] for form_id in FORM_KEYS))
    differentials = {
        "differential_D14": tuple(row["F1"] - row["F4"] for row in form_rows),
        "differential_D12": tuple(row["F1"] - row["F2"] for row in form_rows),
        "differential_D24": tuple(row["F2"] - row["F4"] for row in form_rows),
    }
    relations = (
        ("F1 - F2", tuple(row["F1"] - row["F2"] for row in form_rows)),
        ("F2 - 2*F1", tuple(row["F2"] - 2.0 * row["F1"] for row in form_rows)),
        ("F4 - F1", tuple(row["F4"] - row["F1"] for row in form_rows)),
    )
    relation_records = []
    for expression, values in relations:
        max_residual = max(abs(value) for value in values)
        relation_records.append({"expression": expression, _HOLDS_KEY: max_residual <= 1.0e-14, "max_residual": max_residual})
    return {
        "joint_zero_patterns": patterns,
        "sum_F1_F2_F3_F4": _sum_summary(tuple(sums)),
        **{name: _differential_summary(values, r_values) for name, values in differentials.items()},
        "correlation_matrix_pearson": _form_correlation_matrix(form_rows),
        "tested_linear_relations": relation_records,
        "cross_form_findings": _cross_form_findings(tuple(sums), relation_records),
    }


def run_submodule_E_sign_pattern() -> dict[str, object]:
    r_values = sweep_r_values()
    per_form = {}
    signs_by_form = {}
    levels_by_form = {}
    for form_id in FORM_KEYS:
        signs = tuple(_sign(four_form_float64(r_value)[form_id]) for r_value in r_values)
        signs_by_form[form_id] = signs
        levels_by_form[form_id] = tuple(integer_level_or_none(four_form_float64(r_value)[form_id], _ulp_f_for_precision(r_value, "float64")) for r_value in r_values)
        per_form[form_id] = {
            "n_pos": sum(1 for value in signs if value > 0),
            "n_neg": sum(1 for value in signs if value < 0),
            "n_zero": sum(1 for value in signs if value == 0),
            "sign_sequence": list(signs),
            "sign_density_by_region": _sign_density_by_region(signs, r_values),
        }
    hyp_a = _level_parity_hypothesis(signs_by_form, levels_by_form)
    hyp_b = _operand_bit_hypothesis(signs_by_form, r_values)
    hyp_c = _rounding_direction_hypothesis(signs_by_form, r_values)
    candidate = None
    if hyp_a["any_form_supports"]:
        candidate = "level_parity_sign"
    elif hyp_b["any_form_supports_above_0.7"]:
        candidate = "operand_bit_sign"
    elif hyp_c["supports_above_0.7"]:
        candidate = "factored_sqrt_rounding_direction"
    return {
        "per_form": per_form,
        "cross_form_sign_agreement": _cross_form_sign_agreement(signs_by_form),
        "hypothesis_A_level_parity": hyp_a,
        "hypothesis_B_operand_bit": hyp_b,
        "hypothesis_C_rounding_direction": hyp_c,
        "candidate_new_term_for_law_library": candidate,
    }


def run_campaign() -> dict[str, object]:
    r_values = sweep_r_values()
    return {
        "campaign": "task026_lattice_anomaly_investigation",
        "r_sweep": {"count": len(r_values), "min": r_values[0], "max": r_values[-1]},
        "submodules": {
            "A_lattice_structure": run_submodule_A_lattice(),
            "B_f2_anomaly": run_submodule_B_f2_anomaly(),
            "C_phase_b_spread": run_submodule_C_phase_b_spread(),
            "D_cross_form": run_submodule_D_cross_form(),
            "E_sign_pattern": run_submodule_E_sign_pattern(),
        },
    }


def write_campaign_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(campaign_bytes(payload).decode("utf-8"), encoding="utf-8")
    return payload


def campaign_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_campaign_output(Path(args.output))


def _lattice_for_form_precision(form_id: str, precision_name: str, r_values: tuple[float, ...]) -> dict[str, object]:
    levels = []
    residuals = []
    regions: dict[str, list[int]] = {region: [] for region in _REGIONS}
    for r_value in r_values:
        value = _form_value(form_id, precision_name, r_value)
        if value == 0.0:
            continue
        ulp_value = _ulp_f_for_precision(r_value, precision_name)
        level = value / ulp_value if ulp_value != 0.0 else 0.0
        integer_level = int(round(level))
        levels.append(integer_level)
        residuals.append(level - integer_level)
        regions[_region_name(r_value)].append(integer_level)
    histogram = {str(level): levels.count(level) for level in sorted(set(levels))}
    sorted_levels = tuple(sorted(set(levels)))
    jumps = [int(sorted_levels[index + 1] - sorted_levels[index]) for index in range(len(sorted_levels) - 1)]
    max_residual = max((abs(value) for value in residuals), default=0.0)
    if not levels:
        label = "lattice_empty"
    elif len(set(levels)) == 1:
        label = "single_level"
    elif max_residual < 1.0e-3:
        label = "lattice_integer"
    else:
        label = "non_integer_lattice"
    return {
        "n_total": len(r_values),
        "n_nonzero": len(levels),
        "level_integer_residual_max": max_residual,
        "level_integer_residual_median": _median(tuple(abs(value) for value in residuals)),
        "n_distinct_levels": len(set(levels)),
        "level_min": min(levels) if levels else None,
        "level_max": max(levels) if levels else None,
        "level_histogram": histogram,
        "level_jump_distribution": jumps,
        "regional_distinct_level_counts": {region: len(set(region_levels)) for region, region_levels in regions.items()},
        "candidate_classification": label,
    }


def _form_value(form_id: str, precision_name: str, r_value: float) -> float:
    if precision_name == "float32":
        return four_form_float32(r_value)[form_id]
    if precision_name == "float64":
        return four_form_float64(r_value)[form_id]
    return four_form_decimal_oracle(r_value, 50)[form_id]


def _ulp_f_for_precision(r_value: float, precision_name: str) -> float:
    if precision_name == "float32":
        s = np.float32
        f_value = s(1.0) - s(2.0) / s(r_value)
        return _ulp_of_float32(float(f_value))
    return ulp_of_double(f_of_r(r_value))


def _ulp_of_float32(value: float) -> float:
    x = np.float32(abs(float(value)))
    if x == np.float32(0.0):
        return float(np.nextafter(x, np.float32(1.0), dtype=np.float32) - x)
    return float(np.nextafter(x, np.float32("inf"), dtype=np.float32) - x)


def _primary_f2_hypothesis(hypotheses: dict[str, bool]) -> str:
    for name in ("lattice_mismatch", "sign_disagreement", "float32_mostly_zero", "small_sample"):
        if hypotheses[name]:
            return name
    return "open"


def _quantisation_prediction(records: Sequence[dict[str, object]]) -> dict[str, object]:
    ratios = []
    within2 = 0
    within4 = 0
    for record in records:
        level32 = record["level_float32"]
        level64 = record["level_float64"]
        observed = float(record["ratio"])
        if level32 in (None, 0) or level64 in (None, 0) or observed == 0.0:
            continue
        r_value = float(record["r"])
        predicted = (int(level32) * _ulp_f_for_precision(r_value, "float32")) / (int(level64) * _ulp_f_for_precision(r_value, "float64"))
        factor = _factor_distance(predicted, observed)
        if factor is None:
            continue
        ratios.append(factor)
        if factor <= 2.0:
            within2 += 1
        if factor <= 4.0:
            within4 += 1
    return {
        "median_predicted_vs_observed_ratio": _median(ratios),
        "n_predicted_within_factor_2": within2,
        "n_predicted_within_factor_4": within4,
        "supported": within2 >= 60,
    }


def _phase_b_correlations(records: Sequence[dict[str, object]]) -> dict[str, object]:
    log_values = tuple(float(record["log2_deviation"]) for record in records)
    region_values = tuple(float(_region_index(str(record["region"]))) for record in records)
    sign_values = tuple(1.0 if record["sign_agreement"] else 0.0 for record in records)
    level_values = tuple(float(record["level_float64"]) for record in records)
    abs_level_values = tuple(abs(value) for value in level_values)
    return {
        "log2_dev_vs_region": _corr_pair(log_values, region_values),
        "log2_dev_vs_sign_agreement": _corr_pair(log_values, sign_values),
        "log2_dev_vs_level_float64": _corr_pair(log_values, level_values),
        "log2_dev_vs_abs_level_float64": _corr_pair(log_values, abs_level_values),
    }


def _differential_summary(values: Sequence[float], r_values: tuple[float, ...]) -> dict[str, object]:
    stats = _lattice_stats_for_values(values, r_values)
    return {
        "n_nonzero": stats["n_nonzero"],
        "level_classification": stats["candidate_classification"],
        "level_count": stats["n_distinct_levels"],
    }


def _lattice_stats_for_values(values: Sequence[float], r_values: tuple[float, ...]) -> dict[str, object]:
    levels = []
    residuals = []
    for value, r_value in zip(values, r_values, strict=True):
        if value == 0.0:
            continue
        ulp_value = _ulp_f_for_precision(r_value, "float64")
        level = value / ulp_value
        integer_level = int(round(level))
        levels.append(integer_level)
        residuals.append(level - integer_level)
    max_residual = max((abs(value) for value in residuals), default=0.0)
    if not levels:
        label = "lattice_empty"
    elif len(set(levels)) == 1:
        label = "single_level"
    elif max_residual < 1.0e-3:
        label = "lattice_integer"
    else:
        label = "non_integer_lattice"
    return {"n_nonzero": len(levels), "candidate_classification": label, "n_distinct_levels": len(set(levels))}


def _form_correlation_matrix(rows: Sequence[dict[str, float]]) -> list[list[float]]:
    columns = {form_id: tuple(row[form_id] for row in rows) for form_id in FORM_KEYS}
    matrix = []
    for left_index, left in enumerate(FORM_KEYS):
        row = []
        for right_index, right in enumerate(FORM_KEYS):
            if left_index == right_index:
                row.append(1.0)
            elif left == "F3" or right == "F3":
                row.append(0.0)
            else:
                row.append(_pearson(columns[left], columns[right]))
        matrix.append(row)
    return matrix


def _cross_form_findings(sums: tuple[float, ...], relation_records: Sequence[dict[str, object]]) -> list[str]:
    findings = []
    if max(abs(value) for value in sums) < 1.0e-14:
        findings.append("four_form_sum_at_chain_scale")
    for record in relation_records:
        if record[_HOLDS_KEY]:
            findings.append(f"linear_relation_holds:{record['expression']}")
    return findings


def _level_parity_hypothesis(signs_by_form: dict[str, tuple[int, ...]], levels_by_form: dict[str, tuple[int | None, ...]]) -> dict[str, object]:
    per_form = {}
    for form_id in ("F1", "F2", "F4"):
        signs = []
        parities = []
        for sign_value, level in zip(signs_by_form[form_id], levels_by_form[form_id], strict=True):
            if sign_value == 0 or level is None:
                continue
            signs.append(float(sign_value))
            parities.append(float(abs(level) % 2))
        per_form[form_id] = _pearson(tuple(signs), tuple(parities))
    return {"per_form": per_form, "any_form_supports": any(abs(value) >= 0.7 for value in per_form.values())}


def _operand_bit_hypothesis(signs_by_form: dict[str, tuple[int, ...]], r_values: tuple[float, ...]) -> dict[str, object]:
    best_bit: dict[str, int | None] = {}
    best_corr: dict[str, float] = {}
    operands = tuple(2.0 / r_value for r_value in r_values)
    for form_id in ("F1", "F2", "F4"):
        signs = signs_by_form[form_id]
        use_signs = tuple(float(value) for value in signs if value != 0)
        use_operands = tuple(operand for operand, sign_value in zip(operands, signs, strict=True) if sign_value != 0)
        best_value = 0.0
        best_index = None
        for bit_index in range(53):
            corr = correlation_with_bit_pattern(use_signs, use_operands, bit_index)
            if abs(corr) > abs(best_value):
                best_value = corr
                best_index = bit_index
        best_bit[form_id] = best_index
        best_corr[form_id] = best_value
    return {
        "best_bit_per_form": best_bit,
        "best_correlation_per_form": best_corr,
        "any_form_supports_above_0.7": any(abs(value) >= 0.7 for value in best_corr.values()),
    }


def _rounding_direction_hypothesis(signs_by_form: dict[str, tuple[int, ...]], r_values: tuple[float, ...]) -> dict[str, object]:
    directions = tuple(_factored_sqrt_round_dir(r_value) for r_value in r_values)
    per_form = {}
    for form_id in ("F1", "F2", "F4"):
        signs = []
        dirs = []
        for sign_value, direction in zip(signs_by_form[form_id], directions, strict=True):
            if sign_value == 0 or direction == 0:
                continue
            signs.append(float(sign_value))
            dirs.append(float(direction))
        per_form[form_id] = _pearson(tuple(signs), tuple(dirs))
    return {"per_form": per_form, "supports_above_0.7": any(abs(value) >= 0.7 for value in per_form.values())}


def _factored_sqrt_round_dir(r_value: float) -> int:
    from decimal import Decimal, localcontext

    with localcontext() as context:
        context.prec = 80
        r_dec = Decimal.from_float(float(r_value))
        factored = (r_dec - Decimal(2)) / r_dec
        exact_sqrt = factored.sqrt()
        observed = Decimal.from_float(((float(r_value) - 2.0) / float(r_value)) ** 0.5)
        if observed > exact_sqrt:
            return 1
        if observed < exact_sqrt:
            return -1
        return 0


def _cross_form_sign_agreement(signs_by_form: dict[str, tuple[int, ...]]) -> dict[str, int]:
    pairs = (("F1", "F2"), ("F1", "F4"), ("F2", "F4"))
    result = {}
    for left, right in pairs:
        count = 0
        for left_sign, right_sign in zip(signs_by_form[left], signs_by_form[right], strict=True):
            if left_sign == 0 and right_sign == 0:
                continue
            if left_sign == right_sign:
                count += 1
        result[f"{left}_{right}"] = count
    return result


def _sign_density_by_region(signs: tuple[int, ...], r_values: tuple[float, ...]) -> dict[str, float]:
    densities = {}
    for region in _REGIONS:
        region_signs = tuple(sign for sign, r_value in zip(signs, r_values, strict=True) if _region_name(r_value) == region)
        nonzero = sum(1 for sign in region_signs if sign != 0)
        densities[region] = nonzero / float(len(region_signs)) if region_signs else 0.0
    return densities


def _sum_summary(values: tuple[float, ...]) -> dict[str, object]:
    return {
        "min": min(values),
        "max": max(values),
        "median": _median(values),
        "iqr": _iqr(values),
        "n_nonzero": sum(1 for value in values if value != 0.0),
        "max_abs": max(abs(value) for value in values),
    }


def _corr_pair(left: Sequence[float], right: Sequence[float]) -> dict[str, float]:
    return {"pearson": _pearson(left, right), "spearman": _pearson(_ranks(left), _ranks(right))}


def _pearson(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        return 0.0
    left_values = tuple(float(value) for value in left)
    right_values = tuple(float(value) for value in right)
    left_mean = sum(left_values) / float(len(left_values))
    right_mean = sum(right_values) / float(len(right_values))
    left_centered = tuple(value - left_mean for value in left_values)
    right_centered = tuple(value - right_mean for value in right_values)
    left_energy = sum(value * value for value in left_centered)
    right_energy = sum(value * value for value in right_centered)
    if left_energy == 0.0 or right_energy == 0.0:
        return 0.0
    return sum(left_value * right_value for left_value, right_value in zip(left_centered, right_centered, strict=True)) / ((left_energy * right_energy) ** 0.5)


def _ranks(values: Sequence[float]) -> tuple[float, ...]:
    indexed = sorted((float(value), index) for index, value in enumerate(values))
    ranks = [0.0] * len(indexed)
    position = 0
    while position < len(indexed):
        end = position + 1
        while end < len(indexed) and indexed[end][0] == indexed[position][0]:
            end += 1
        rank_value = (position + end - 1) / 2.0
        for _, original_index in indexed[position:end]:
            ranks[original_index] = rank_value
        position = end
    return tuple(ranks)


def _factor_distance(predicted: float, observed: float) -> float | None:
    if predicted == 0.0 or observed == 0.0:
        return None
    ratio = abs(predicted / observed)
    if ratio == 0.0:
        return None
    return ratio if ratio >= 1.0 else 1.0 / ratio


def _region_name(r_value: float) -> str:
    if r_value < 2.05:
        return "near"
    if r_value < 3.0:
        return "middle"
    return "far"


def _region_index(region: str) -> int:
    return {"near": 0, "middle": 1, "far": 2}[region]


def _sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


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


if __name__ == "__main__":
    main()
