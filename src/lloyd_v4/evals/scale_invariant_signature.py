from __future__ import annotations

import argparse
import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import ulp_of_double
from .path_catalog import CandidatePath, FIXTURES, all_candidate_paths, evaluate_path_decimal_oracle, evaluate_path_float32, evaluate_path_float64
from .path_signature import PRECISIONS, PathSignature, canonical_operands, compute_path_signature


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029b_methodology_refinement"
DEFAULT_OUTPUT = REPORT_DIR / "scale_invariant_signatures.json"


def signed_lattice_histogram_value_relative(path: CandidatePath, precision: str) -> dict[str, int]:
    if precision not in PRECISIONS:
        raise ValueError(f"unknown precision: {precision}")
    counts: dict[str, int] = {}
    for operand in canonical_operands(path.fixture):
        value = _evaluate(path, precision, operand)
        if value == 0.0:
            continue
        unit = _unit_for_value(value, precision)
        if unit == 0.0:
            continue
        level = round((value / unit) * 2.0) / 2.0
        key = f"{precision}:L={_level_label(level)}:S={_sign_label(_sign(value))}"
        counts[key] = counts.get(key, 0) + 1
    return {key: counts[key] for key in sorted(counts)}


def compute_path_signature_scale_invariant(path: CandidatePath) -> PathSignature:
    original = compute_path_signature(path)
    merged: dict[str, int] = {}
    for precision in PRECISIONS:
        merged.update(signed_lattice_histogram_value_relative(path, precision))
    return replace(original, signed_lattice_histogram=merged)


def compute_all_signatures_scale_invariant(fixture: str) -> tuple[PathSignature, ...]:
    if fixture not in FIXTURES:
        raise ValueError(f"unknown fixture: {fixture}")
    return tuple(compute_path_signature_scale_invariant(path) for path in all_candidate_paths() if path.fixture == fixture)


def run_scale_invariant_signature_campaign() -> dict[str, object]:
    signatures = [compute_path_signature_scale_invariant(path) for path in all_candidate_paths()]
    return {
        "campaign": "task029b_scale_invariant_signatures",
        "fixtures": list(FIXTURES),
        "lattice_metric": "value_relative",
        "signatures": [asdict(signature) for signature in signatures],
    }


def write_scale_invariant_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_scale_invariant_signature_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scale_invariant_bytes(payload).decode("utf-8"), encoding="utf-8")
    return payload


def scale_invariant_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_scale_invariant_signature_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_scale_invariant_output(Path(args.output))


def _evaluate(path: CandidatePath, precision: str, operand: float) -> float:
    if precision == "float32":
        return evaluate_path_float32(path, operand)
    if precision == "float64":
        return evaluate_path_float64(path, operand)
    return evaluate_path_decimal_oracle(path, operand, 50)


def _unit_for_value(value: float, precision: str) -> float:
    if precision == "float32":
        return _ulp_of_float32(value)
    return ulp_of_double(value)


def _ulp_of_float32(value: float) -> float:
    x = np.float32(abs(float(value)))
    if x == np.float32(0.0):
        return float(np.nextafter(x, np.float32(1.0), dtype=np.float32) - x)
    return float(np.nextafter(x, np.float32("inf"), dtype=np.float32) - x)


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


def _sign(value: float) -> int:
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


if __name__ == "__main__":
    main()
