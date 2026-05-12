from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Sequence

import numpy as np

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.primitives.directional_alpha_probe import directional_alpha_probe

from .multi_precision_four_form import ulp_of_double
from .path_catalog import (
    CandidatePath,
    FIXTURES,
    all_candidate_paths,
    evaluate_path_decimal_oracle,
    evaluate_path_float32,
    evaluate_path_float64,
)
from .pure_algebraic_four_form import x_grid
from .schwarzschild_four_form import f_of_r, sweep_r_values
from .sr_four_form import beta_grid


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029_path_basis_rank_clustering"
DEFAULT_OUTPUT = REPORT_DIR / "path_signatures.json"
SIGNATURE_CSV = REPORT_DIR / "signature_summary_table.csv"
PRECISIONS = ("float32", "float64", "decimal_50")
ANCHORS = ("F1", "F2", "F3", "F4")


@dataclass(frozen=True)
class PathSignature:
    path_label: str
    fixture: str
    zero_mask_fingerprint: tuple[bool, ...]
    signed_lattice_histogram: dict[str, int]
    precision_scaling: tuple[float, float, float]
    alpha_status_at_characteristic: tuple[str, ...]
    cofire_polarity_with_canonical: dict[str, tuple[int, int, int]]
    envelope_shape: tuple[float, float, float, float]


def compute_path_signature(path: CandidatePath) -> PathSignature:
    operands = canonical_operands(path.fixture)
    values_by_precision = {
        precision: tuple(_evaluate(path, operand, precision) for operand in operands)
        for precision in PRECISIONS
    }
    zero_mask = tuple(value == 0.0 for precision in PRECISIONS for value in values_by_precision[precision])
    histogram = _signed_lattice_histogram(path.fixture, operands, values_by_precision)
    scaling = tuple(float(sum(1 for value in values_by_precision[precision] if value != 0.0)) for precision in PRECISIONS)
    alpha_statuses = _alpha_statuses(path)
    cofire = _cofire_with_canonical(path, operands, values_by_precision["float64"])
    envelope = _envelope_shape(values_by_precision["float64"])
    return PathSignature(
        path_label=path.label,
        fixture=path.fixture,
        zero_mask_fingerprint=zero_mask,
        signed_lattice_histogram=histogram,
        precision_scaling=scaling,
        alpha_status_at_characteristic=alpha_statuses,
        cofire_polarity_with_canonical=cofire,
        envelope_shape=envelope,
    )


def compute_all_signatures(fixture: str) -> tuple[PathSignature, ...]:
    if fixture not in FIXTURES:
        raise ValueError(f"unknown fixture: {fixture}")
    return tuple(compute_path_signature(path) for path in all_candidate_paths() if path.fixture == fixture)


def write_signatures_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_signature_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(signature_bytes(payload).decode("utf-8"), encoding="utf-8")
    _write_csv(payload, SIGNATURE_CSV)
    return payload


def run_signature_campaign() -> dict[str, object]:
    signatures = [compute_path_signature(path) for path in all_candidate_paths()]
    return {
        "campaign": "task029_path_signature",
        "fixtures": list(FIXTURES),
        "signature_dimensions": [
            "zero_mask_fingerprint",
            "signed_lattice_histogram",
            "precision_scaling",
            "alpha_status_at_characteristic",
            "cofire_polarity_with_canonical",
            "envelope_shape",
        ],
        "signatures": [asdict(signature) for signature in signatures],
    }


def signature_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_signature_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_signatures_output(Path(args.output))


def canonical_operands(fixture: str) -> tuple[float, ...]:
    if fixture == "schwarzschild":
        return sweep_r_values()
    if fixture == "sr":
        return beta_grid()
    if fixture == "pure_algebraic":
        return x_grid()
    raise ValueError(f"unknown fixture: {fixture}")


def unit_for_precision(fixture: str, operand: float, precision: str) -> float:
    if fixture == "schwarzschild":
        if precision == "float32":
            s = np.float32
            f_value = s(1.0) - s(2.0) / s(operand)
            return _ulp_of_float32(float(f_value))
        return ulp_of_double(f_of_r(operand))
    if fixture == "sr":
        if precision == "float32":
            s = np.float32
            beta_value = s(operand)
            q_value = s(1.0) - beta_value * beta_value
            return _ulp_of_float32(float(q_value))
        value = float(operand)
        return ulp_of_double(1.0 - value * value)
    if fixture == "pure_algebraic":
        if precision == "float32":
            s = np.float32
            f_value = s(1.0) - s(operand)
            return _ulp_of_float32(float(f_value))
        return ulp_of_double(1.0 - float(operand))
    raise ValueError(f"unknown fixture: {fixture}")


def _evaluate(path: CandidatePath, operand: float, precision: str) -> float:
    if precision == "float32":
        return evaluate_path_float32(path, operand)
    if precision == "float64":
        return evaluate_path_float64(path, operand)
    return evaluate_path_decimal_oracle(path, operand, 50)


def _signed_lattice_histogram(
    fixture: str,
    operands: tuple[float, ...],
    values_by_precision: dict[str, tuple[float, ...]],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for precision in PRECISIONS:
        values = values_by_precision[precision]
        for operand, value in zip(operands, values, strict=True):
            if value == 0.0:
                continue
            unit = unit_for_precision(fixture, operand, precision)
            if unit == 0.0:
                continue
            level = round((value / unit) * 2.0) / 2.0
            key = f"{precision}:L={_level_label(level)}:S={_sign_label(_sign(value))}"
            counts[key] = counts.get(key, 0) + 1
    return {key: counts[key] for key in sorted(counts)}


def _alpha_statuses(path: CandidatePath) -> tuple[str, ...]:
    statuses = []
    for operand in _characteristic_operands(path.fixture):
        scale = max(abs(float(operand)), 1.0) * 1.0e-4
        h_values = tuple(scale * float(index) for index in range(1, 8))

        def observable(h_value: float, base: float = float(operand), candidate: CandidatePath = path) -> float:
            return evaluate_path_float64(candidate, base + h_value)

        result = directional_alpha_probe(
            observable,
            h_values,
            probe_id=f"{path.fixture}_{path.label}_{operand}",
            function_label=path.label,
            eta=1.0e-6,
            expression_path="task029_path_signature_alpha",
        )
        statuses.append(result.status.value)
    return tuple(statuses)


def _cofire_with_canonical(path: CandidatePath, operands: tuple[float, ...], path_values: tuple[float, ...]) -> dict[str, tuple[int, int, int]]:
    result: dict[str, tuple[int, int, int]] = {}
    anchor_paths = {candidate.label: candidate for candidate in all_candidate_paths() if candidate.fixture == path.fixture and candidate.label in ANCHORS}
    for anchor in ANCHORS:
        cofire = 0
        aligned = 0
        opposed = 0
        for operand, path_value in zip(operands, path_values, strict=True):
            anchor_value = evaluate_path_float64(anchor_paths[anchor], operand)
            left = _sign(path_value)
            right = _sign(anchor_value)
            if left == 0 or right == 0:
                continue
            cofire += 1
            if left == right:
                aligned += 1
            else:
                opposed += 1
        result[anchor] = (cofire, aligned, opposed)
    return result


def _envelope_shape(values: tuple[float, ...]) -> tuple[float, float, float, float]:
    magnitudes = tuple(abs(value) for value in values if value != 0.0)
    if not magnitudes:
        return (0.0, 0.0, 0.0, 0.0)
    total = sum(magnitudes)
    top_count = max(1, len(values) // 10)
    top_sum = sum(sorted(magnitudes, reverse=True)[:top_count])
    concentration = top_sum / total if total != 0.0 else 0.0
    dynamic_range = _log10_ratio(max(magnitudes), min(magnitudes))
    lower_end = len(values) // 3
    upper_start = len(values) - lower_end
    nonzero_total = float(len(magnitudes))
    small = sum(1 for value in values[:lower_end] if value != 0.0) / nonzero_total
    large = sum(1 for value in values[upper_start:] if value != 0.0) / nonzero_total
    return (concentration, dynamic_range, small, large)


def _characteristic_operands(fixture: str) -> tuple[float, ...]:
    if fixture == "schwarzschild":
        return (2.1, 3.0, 4.0, 6.0, 9.0)
    if fixture == "sr":
        return (0.1, 0.3, 0.5, 0.707, 0.9)
    if fixture == "pure_algebraic":
        return (0.1, 0.3, 0.5, 0.7, 0.9)
    raise ValueError(f"unknown fixture: {fixture}")


def _log10_ratio(max_value: float, min_value: float) -> float:
    if max_value <= 0.0 or min_value <= 0.0:
        return 0.0
    with localcontext() as context:
        context.prec = 50
        ratio = Decimal.from_float(float(max_value)) / Decimal.from_float(float(min_value))
        return float(ratio.log10())


def _level_label(level: float) -> str:
    value = float(level)
    if value == 0.0:
        return "0"
    sign = "+" if value > 0.0 else "-"
    absolute = abs(value)
    if absolute.is_integer():
        return f"{sign}{int(absolute)}"
    return f"{sign}{absolute:.1f}"


def _sign_label(sign: int) -> str:
    if sign > 0:
        return "+"
    if sign < 0:
        return "-"
    return "0"


def _ulp_of_float32(value: float) -> float:
    x = np.float32(abs(float(value)))
    if x == np.float32(0.0):
        return float(np.nextafter(x, np.float32(1.0), dtype=np.float32) - x)
    return float(np.nextafter(x, np.float32("inf"), dtype=np.float32) - x)


def _sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


def _write_csv(payload: dict[str, object], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", "path_label", "nonzero_float32", "nonzero_float64", "nonzero_decimal_50", "lattice_bins", "alpha_statuses", "envelope_concentration", "envelope_dynamic_range", "envelope_region_small", "envelope_region_large"))
        for item in payload["signatures"]:
            envelope = item["envelope_shape"]
            scaling = item["precision_scaling"]
            writer.writerow((item["fixture"], item["path_label"], int(scaling[0]), int(scaling[1]), int(scaling[2]), len(item["signed_lattice_histogram"]), " ".join(item["alpha_status_at_characteristic"]), envelope[0], envelope[1], envelope[2], envelope[3]))


if __name__ == "__main__":
    main()
