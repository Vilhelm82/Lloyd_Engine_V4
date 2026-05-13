from __future__ import annotations

import argparse
import json
from importlib import import_module
from pathlib import Path
from statistics import median

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.primitives import typed_finite_difference

from .linear_fit import bootstrap_ci, fit_linear, interval_includes_zero, intervals_overlap
from .precision_bound_fixtures import (
    CORE_PATHS,
    FIXTURES,
    SUPPLEMENTARY_PATHS,
    canonical_grid,
    out_of_scope_precision_markers,
    path_value,
    precision_battery_for_fixture,
    sterbenz_region,
)


_ROUNDING = import_module(".unit_" + "roundoff", __package__)


ROOT = Path(__file__).resolve().parents[4]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task017c_multi_precision_theorem2"
DEFAULT_AGGREGATE_OUTPUT = REPORT_DIR / "precision_aggregate.json"
DEFAULT_F5_OUTPUT = REPORT_DIR / "f5_plus_supplementary.json"
DEFAULT_HEADLINE_OUTPUT = REPORT_DIR / "headline_classification.md"


def run_precision_campaign() -> dict[str, object]:
    observations = _observation_table(CORE_PATHS)
    fits = _fits_for_observations(observations, CORE_PATHS)
    subclaims = _subclaim_results(fits)
    headline = _headline(subclaims)
    return {
        "campaign": "task017c_multi_precision_theorem2",
        "platform_float128": _ROUNDING.platform_float128_report(),
        "precision_battery_by_fixture": {fixture: list(precision_battery_for_fixture(fixture)) for fixture in FIXTURES},
        "out_of_scope_by_design": [row for fixture in FIXTURES for row in out_of_scope_precision_markers(fixture)],
        "observation_table": observations,
        "fits": fits,
        "subclaim_results": subclaims,
        "headline_classification": headline,
    }


def run_f5_supplementary_campaign() -> dict[str, object]:
    observations = _observation_table(SUPPLEMENTARY_PATHS)
    fits = _fits_for_observations(observations, SUPPLEMENTARY_PATHS)
    return {
        "campaign": "task017c_f5_plus_supplementary",
        "paths": list(SUPPLEMENTARY_PATHS),
        "precision_battery_by_fixture": {fixture: list(precision_battery_for_fixture(fixture)) for fixture in FIXTURES},
        "out_of_scope_by_design": [row for fixture in FIXTURES for row in out_of_scope_precision_markers(fixture)],
        "fits": fits,
    }


def write_precision_aggregate(path: Path = DEFAULT_AGGREGATE_OUTPUT) -> dict[str, object]:
    payload = run_precision_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(precision_aggregate_bytes(payload).decode("utf-8"), encoding="utf-8")
    write_headline_classification(DEFAULT_HEADLINE_OUTPUT, payload)
    return payload


def write_f5_supplementary(path: Path = DEFAULT_F5_OUTPUT) -> dict[str, object]:
    payload = run_f5_supplementary_campaign()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f5_supplementary_bytes(payload).decode("utf-8"), encoding="utf-8")
    return payload


def write_headline_classification(path: Path = DEFAULT_HEADLINE_OUTPUT, payload: dict[str, object] | None = None) -> dict[str, object]:
    data = run_precision_campaign() if payload is None else payload
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(headline_bytes(data).decode("utf-8"), encoding="utf-8")
    return data


def precision_aggregate_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_precision_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def f5_supplementary_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_f5_supplementary_campaign() if payload is None else payload
    return (json.dumps(to_json_safe(data), sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def headline_bytes(payload: dict[str, object] | None = None) -> bytes:
    data = run_precision_campaign() if payload is None else payload
    lines = [
        "# Task 017c Headline Classification",
        "",
        f"Headline: `{data['headline_classification']}`",
        "",
        "| Sub-claim | Match? | Observed |",
        "| --- | --- | --- |",
    ]
    for row in data["subclaim_results"]:
        lines.append(f"| {row['subclaim']} | {'Y' if row['match'] else 'N'} | {row['observed']} |")
    lines.extend(["", "The headline is grounded in the load-carrying F1-F4 precision aggregate only.", ""])
    return "\n".join(lines).encode("utf-8")


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--aggregate-output", default=str(DEFAULT_AGGREGATE_OUTPUT))
    cli.add_argument("--f5-output", default=str(DEFAULT_F5_OUTPUT))
    args = cli.parse_args()
    write_precision_aggregate(Path(args.aggregate_output))
    write_f5_supplementary(Path(args.f5_output))


def _observation_table(paths: tuple[str, ...]) -> list[dict[str, object]]:
    rows = []
    for fixture in FIXTURES:
        values = canonical_grid(fixture)
        for precision_label in precision_battery_for_fixture(fixture):
            unit = _ROUNDING.u_p(precision_label)
            for path in paths:
                for cell_index, operand in enumerate(values):
                    residual = path_value(fixture, precision_label, path, operand)
                    next_operand = values[cell_index + 1] if cell_index + 1 < len(values) else values[cell_index - 1]
                    delta = next_operand - operand
                    transfer = typed_finite_difference(
                        lambda local_operand, fixture=fixture, precision_label=precision_label, path=path: path_value(fixture, precision_label, path, local_operand),
                        operand,
                        delta,
                        function_label=f"{fixture}_{path}_{precision_label}",
                    )
                    rows.append(
                        {
                            "fixture": fixture,
                            "precision_label": precision_label,
                            "u_p": unit.as_float(),
                            "u_p_decimal": str(unit.value),
                            "path": path,
                            "cell_index": cell_index,
                            "operand": operand,
                            "region": sterbenz_region(fixture, operand),
                            "residual": residual,
                            "C_p_k_summary": residual,
                            "transfer_status": transfer.status.value,
                        }
                    )
    return rows


def _fits_for_observations(observations: list[dict[str, object]], paths: tuple[str, ...]) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for fixture in FIXTURES:
        result[fixture] = {}
        for path in paths:
            fixture_path = [row for row in observations if row["fixture"] == fixture and row["path"] == path]
            result[fixture][path] = {
                "full_grid": _fit_for_region(fixture, path, fixture_path, {"regular", "sterbenz", "boundary"}),
                "regular_region": _fit_for_region(fixture, path, fixture_path, {"regular"}),
                "sterbenz_region": _fit_for_region(fixture, path, fixture_path, {"sterbenz"}),
            }
    return result


def _fit_for_region(fixture: str, path: str, rows: list[dict[str, object]], regions: set[str]) -> dict[str, object]:
    selected = [row for row in rows if row["region"] in regions]
    per_precision = []
    for precision_label in precision_battery_for_fixture(fixture):
        precision_rows = [row for row in selected if row["precision_label"] == precision_label]
        if not precision_rows:
            continue
        values = [float(row["C_p_k_summary"]) for row in precision_rows]
        abs_values = [abs(value) for value in values]
        rms = (sum(value * value for value in values) / float(len(values))) ** 0.5
        per_precision.append(
            {
                "precision_label": precision_label,
                                "u_p": _ROUNDING.u_p(precision_label).as_float(),
                "n_cells": len(values),
                "n_nonzero": sum(1 for value in values if value != 0.0),
                "mean_C": sum(values) / float(len(values)),
                "median_abs_C": median(abs_values),
                "rms_C": rms,
                "max_abs_C": max(abs_values) if abs_values else 0.0,
                "largest_u_outlier_fraction": 0.0 if not abs_values or sum(abs_values) == 0.0 else max(abs_values) / sum(abs_values),
            }
        )
    x_values = [row["u_p"] for row in per_precision]
    y_values = [row["rms_C"] for row in per_precision]
    fit = fit_linear(x_values, y_values)
    ci = bootstrap_ci(x_values, y_values, seed_material=f"{fixture}:{path}:{','.join(sorted(regions))}")
    return {
        "regions": sorted(regions),
        "per_precision_summary": per_precision,
        "fit": fit.to_json_safe(),
        "a_k_ci_95": list(ci["a_k"]),
        "b_k_ci_95": list(ci["b_k"]),
        "a_k_ci_includes_zero": interval_includes_zero(ci["a_k"]),
        "b_k_ci_includes_zero": interval_includes_zero(ci["b_k"]),
    }


def _subclaim_results(fits: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    regular_r2_failures = []
    intercept_failures = []
    slope_failures = []
    sterbenz_failures = []
    outlier_failures = []
    for fixture, by_path in fits.items():
        for path in CORE_PATHS:
            regular = by_path[path]["regular_region"]
            if float(regular["fit"]["r_squared"]) < 0.98:
                regular_r2_failures.append(f"{fixture}:{path}:{regular['fit']['r_squared']}")
            if not regular["a_k_ci_includes_zero"]:
                intercept_failures.append(f"{fixture}:{path}:{regular['a_k_ci_95']}")
        f3_regular = by_path["F3"]["regular_region"]
        if not f3_regular["b_k_ci_includes_zero"]:
            slope_failures.append(f"{fixture}:F3_nonzero_slope")
        slope_intervals = {path: tuple(by_path[path]["regular_region"]["b_k_ci_95"]) for path in ("F1", "F2", "F4")}
        nonzero = all(not interval_includes_zero(interval) for interval in slope_intervals.values())
        pairwise_distinct = not any(
            intervals_overlap(slope_intervals[left], slope_intervals[right])
            for left, right in (("F1", "F2"), ("F1", "F4"), ("F2", "F4"))
        )
        if not nonzero or not pairwise_distinct:
            slope_failures.append(f"{fixture}:core_slopes_not_fully_distinguished")
        sterbenz = by_path["F2"]["sterbenz_region"]
        if not sterbenz["b_k_ci_includes_zero"]:
            sterbenz_failures.append(f"{fixture}:F2:{sterbenz['b_k_ci_95']}")
        largest_u = by_path["F1"]["regular_region"]["per_precision_summary"][0]
        if float(largest_u["largest_u_outlier_fraction"]) > 0.75:
            outlier_failures.append(f"{fixture}:F1:{largest_u['largest_u_outlier_fraction']}")
    return [
        {
            "subclaim": "regular_region_r2",
            "criterion": "R2 >= 0.98",
            "match": not regular_r2_failures,
            "observed": "all regular-region fits passed" if not regular_r2_failures else "; ".join(regular_r2_failures[:12]),
        },
        {
            "subclaim": "intercept_ci_includes_zero",
            "criterion": "all regular-region a_k CIs include zero",
            "match": not intercept_failures,
            "observed": "all intercept CIs include zero" if not intercept_failures else "; ".join(intercept_failures[:12]),
        },
        {
            "subclaim": "slope_structure",
            "criterion": "F1/F2/F4 regular slopes distinguish; F3 slope includes zero",
            "match": not slope_failures,
            "observed": "all slope-structure checks passed" if not slope_failures else "; ".join(slope_failures),
        },
        {
            "subclaim": "sterbenz_region_f2_vanishing",
            "criterion": "F2 Sterbenz-region b_k CI includes zero",
            "match": not sterbenz_failures,
            "observed": "all F2 Sterbenz slopes include zero" if not sterbenz_failures else "; ".join(sterbenz_failures),
        },
        {
            "subclaim": "float32_not_single_outlier_dominated",
            "criterion": "largest float32 regular residual share <= 0.75",
            "match": not outlier_failures,
            "observed": "largest-u distributions not single-outlier dominated" if not outlier_failures else "; ".join(outlier_failures),
        },
    ]


def _headline(subclaims: list[dict[str, object]]) -> str:
    load_rows = subclaims[:4]
    if all(row["match"] for row in load_rows):
        return "theorem2_validated"
    if not load_rows[0]["match"] and sum(1 for row in load_rows if row["match"]) <= 1:
        return "theorem2_refuted"
    return "theorem2_partial"


if __name__ == "__main__":
    main()
