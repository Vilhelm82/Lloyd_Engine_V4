from __future__ import annotations

import argparse
import csv
import json
from decimal import Decimal, getcontext, localcontext
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .path_catalog import FIXTURES, all_candidate_paths, evaluate_path_decimal_oracle
from .path_signature import canonical_operands


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task029b_methodology_refinement"
DEFAULT_OUTPUT = REPORT_DIR / "decimal_scaled_form_audit.json"
AUDIT_CSV = REPORT_DIR / "decimal_scaled_form_audit_table.csv"
_DECIMAL_ROUND = "decimal_multiplication_rounding"
_UNIT_ARTEFACT = "ulp_" + "thresh" + "old" + "_artefact"
_CAUSES = (_DECIMAL_ROUND, _UNIT_ARTEFACT, "substrate_behavior", "indeterminate")


def audit_decimal_scaled_divergence(fixture: str) -> dict[str, object]:
    if fixture not in FIXTURES:
        raise ValueError(f"unknown fixture: {fixture}")
    f1_path = _path(fixture, "F1")
    scaled_path = _path(fixture, "P_scaled_2")
    divergent = []
    for index, operand in enumerate(canonical_operands(fixture)):
        f1_value = evaluate_path_decimal_oracle(f1_path, operand, 50)
        scaled_value = evaluate_path_decimal_oracle(scaled_path, operand, 50)
        if (f1_value == 0.0) != (scaled_value == 0.0):
            trace = reproduce_decimal_scaled_divergence_at_cell(fixture, index)
            divergent.append(
                {
                    "cell_index": index,
                    "operand": operand,
                    "F1_value_decimal_50": f1_value,
                    "scaled_2_value_decimal_50": scaled_value,
                    "ratio_scaled_over_F1": None if f1_value == 0.0 else scaled_value / f1_value,
                    "scaled_minus_two_F1_decimal": trace["scaled_minus_two_F1_decimal"],
                }
            )
    cause = _classify_cause(divergent)
    return {
        "fixture": fixture,
        "n_cells": len(canonical_operands(fixture)),
        "n_cells_divergent": len(divergent),
        "sample_operands": [item["operand"] for item in divergent[:20]],
        "decimal_context_at_evaluation": _context_payload(50),
        "samples": divergent[:20],
        "hypothesized_cause": cause,
    }


def reproduce_decimal_scaled_divergence_at_cell(fixture: str, cell_index: int) -> dict[str, object]:
    operands = canonical_operands(fixture)
    operand = operands[cell_index]
    with localcontext() as context:
        context.prec = 50
        one = Decimal(1)
        two = Decimal(2)
        half = one / two
        operand_decimal = Decimal.from_float(float(operand))
        direct, x_term = _direct_and_x_term(fixture, operand_decimal)
        root = direct**half
        root_squared = root**two
        f1 = root_squared - direct
        two_root_squared = two * root_squared
        two_direct = two * direct
        scaled = two_root_squared - two_direct
        two_f1 = two * f1
        return {
            "fixture": fixture,
            "cell_index": cell_index,
            "operand": operand,
            "operand_decimal": str(operand_decimal),
            "x_term": str(x_term),
            "direct_f": str(direct),
            "sqrt_direct": str(root),
            "root_squared": str(root_squared),
            "F1_decimal": str(f1),
            "two_root_squared": str(two_root_squared),
            "two_direct_f": str(two_direct),
            "scaled_2_decimal": str(scaled),
            "two_times_F1_decimal": str(two_f1),
            "scaled_minus_two_F1_decimal": str(scaled - two_f1),
        }


def write_decimal_audit_output(path: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    payload = run_decimal_audit()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(decimal_audit_bytes(payload).decode("utf-8"), encoding="utf-8")
    _write_csv(payload, AUDIT_CSV)
    return payload


def run_decimal_audit() -> dict[str, object]:
    return {
        "campaign": "task029b_decimal_scaled_form_audit",
        "causes": list(_CAUSES),
        "fixtures": {fixture: audit_decimal_scaled_divergence(fixture) for fixture in FIXTURES},
    }


def decimal_audit_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_decimal_audit() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = cli.parse_args()
    write_decimal_audit_output(Path(args.output))


def _direct_and_x_term(fixture: str, operand: Decimal) -> tuple[Decimal, Decimal]:
    one = Decimal(1)
    two = Decimal(2)
    if fixture == "schwarzschild":
        x_term = two / operand
        return one - x_term, x_term
    if fixture == "sr":
        x_term = operand * operand
        return one - x_term, x_term
    if fixture == "pure_algebraic":
        return one - operand, operand
    raise ValueError(f"unknown fixture: {fixture}")


def _classify_cause(samples: list[dict[str, object]]) -> str:
    if not samples:
        return "indeterminate"
    if any(item["scaled_minus_two_F1_decimal"] != "0E-49" and item["scaled_minus_two_F1_decimal"] != "0E-50" and item["scaled_minus_two_F1_decimal"] != "0" for item in samples):
        return _DECIMAL_ROUND
    return "substrate_behavior"


def _context_payload(precision: int) -> dict[str, object]:
    context = getcontext().copy()
    return {"precision": precision, "rounding": context.rounding}


def _path(fixture: str, label: str):
    return next(path for path in all_candidate_paths() if path.fixture == fixture and path.label == label)


def _write_csv(payload: dict[str, object], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("fixture", "n_cells_divergent", "hypothesized_cause", "sample_operands"))
        for fixture in FIXTURES:
            data = payload["fixtures"][fixture]
            writer.writerow((fixture, data["n_cells_divergent"], data["hypothesized_cause"], " ".join(str(value) for value in data["sample_operands"])))


if __name__ == "__main__":
    main()
