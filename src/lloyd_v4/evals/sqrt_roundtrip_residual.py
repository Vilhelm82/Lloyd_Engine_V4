from __future__ import annotations

import argparse
import csv
import json
from decimal import Decimal, localcontext
from pathlib import Path

import numpy as np

from lloyd_v4.core.serialization import to_json_safe

from .path_catalog import FIXTURES, all_candidate_paths, evaluate_path_float64
from .path_signature import PRECISIONS, canonical_operands


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029b_methodology_refinement"
DEFAULT_OUTPUT = REPORT_DIR / "sqrt_roundtrip_residual.json"
SUMMARY_CSV = REPORT_DIR / "sqrt_roundtrip_summary_table.csv"


def sqrt_roundtrip_residual_at_cell(fixture: str, cell_index: int, precision: str) -> float:
    operands = canonical_operands(fixture)
    operand = operands[cell_index]
    if precision == "float32":
        s = np.float32
        f_value = _direct_float32(fixture, operand)
        root = f_value**s(0.5)
        return float(root**s(2.0) - root * root)
    if precision == "float64":
        f_value = _direct_float64(fixture, operand)
        root = f_value**0.5
        return float(root**2 - root * root)
    if precision == "decimal_50":
        with localcontext() as context:
            context.prec = 50
            f_value = _direct_decimal(fixture, operand)
            root = f_value ** (Decimal(1) / Decimal(2))
            return float(root ** Decimal(2) - root * root)
    raise ValueError(f"unknown precision: {precision}")


def sqrt_roundtrip_residual_full_grid(fixture: str, precision: str) -> tuple[float, ...]:
    return tuple(sqrt_roundtrip_residual_at_cell(fixture, index, precision) for index, _ in enumerate(canonical_operands(fixture)))


def characterize_sqrt_roundtrip(fixture: str) -> dict[str, object]:
    if fixture not in FIXTURES:
        raise ValueError(f"unknown fixture: {fixture}")
    by_precision = {}
    for precision in PRECISIONS:
        values = sqrt_roundtrip_residual_full_grid(fixture, precision)
        by_precision[precision] = {
            "n_cells_with_nonzero_residual": sum(1 for value in values if value != 0.0),
            "max_abs_residual": max((abs(value) for value in values), default=0.0),
        }
    residual64 = sqrt_roundtrip_residual_full_grid(fixture, "float64")
    top64 = _top_residual_cells(fixture, residual64)
    firing_cells = _p_distrib_sqrt_mul_firing_cells(fixture)
    top_indices = {item["cell_index"] for item in top64}
    return {
        "fixture": fixture,
        "by_precision": by_precision,
        "top_abs_residual_cells_float64": top64,
        "p_distrib_sqrt_mul_firing_cells_float64": firing_cells,
        "firing_cells_align_with_top_abs_residual": all(cell in top_indices for cell in firing_cells),
    }


def write_sqrt_roundtrip_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_sqrt_roundtrip_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sqrt_roundtrip_bytes(payload).decode("utf-8"), encoding="utf-8")
    _write_csv(payload, SUMMARY_CSV)
    return payload


def run_sqrt_roundtrip_campaign() -> dict[str, object]:
    return {
        "campaign": "task029b_sqrt_roundtrip_residual",
        "fixtures": {fixture: characterize_sqrt_roundtrip(fixture) for fixture in FIXTURES},
    }


def sqrt_roundtrip_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_sqrt_roundtrip_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_sqrt_roundtrip_output(Path(args.output))


def _direct_float32(fixture: str, operand: float) -> np.float32:
    s = np.float32
    value = s(operand)
    if fixture == "schwarzschild":
        return s(1.0) - s(2.0) / value
    if fixture == "sr":
        return s(1.0) - value * value
    if fixture == "pure_algebraic":
        return s(1.0) - value
    raise ValueError(f"unknown fixture: {fixture}")


def _direct_float64(fixture: str, operand: float) -> float:
    value = float(operand)
    if fixture == "schwarzschild":
        return 1.0 - 2.0 / value
    if fixture == "sr":
        return 1.0 - value * value
    if fixture == "pure_algebraic":
        return 1.0 - value
    raise ValueError(f"unknown fixture: {fixture}")


def _direct_decimal(fixture: str, operand: float) -> Decimal:
    one = Decimal(1)
    value = Decimal.from_float(float(operand))
    if fixture == "schwarzschild":
        return one - Decimal(2) / value
    if fixture == "sr":
        return one - value * value
    if fixture == "pure_algebraic":
        return one - value
    raise ValueError(f"unknown fixture: {fixture}")


def _top_residual_cells(fixture: str, residuals: tuple[float, ...]) -> list[dict[str, object]]:
    operands = canonical_operands(fixture)
    ranked = sorted(((abs(value), index, value) for index, value in enumerate(residuals)), reverse=True)
    return [
        {
            "cell_index": index,
            "operand": operands[index],
            "residual": value,
            "abs_residual": absolute,
        }
        for absolute, index, value in ranked[:5]
    ]


def _p_distrib_sqrt_mul_firing_cells(fixture: str) -> list[int]:
    path = next(path for path in all_candidate_paths() if path.fixture == fixture and path.label == "P_distrib_sqrt_mul")
    return [index for index, operand in enumerate(canonical_operands(fixture)) if evaluate_path_float64(path, operand) != 0.0]


def _write_csv(payload: dict[str, object], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", "precision", "n_cells_with_nonzero_residual", "max_abs_residual", "firing_cells_align_with_top_abs_residual"))
        for fixture in FIXTURES:
            data = payload["fixtures"][fixture]
            for precision in PRECISIONS:
                row = data["by_precision"][precision]
                writer.writerow((fixture, precision, row["n_cells_with_nonzero_residual"], row["max_abs_residual"], data["firing_cells_align_with_top_abs_residual"]))


if __name__ == "__main__":
    main()
