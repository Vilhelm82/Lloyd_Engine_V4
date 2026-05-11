from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from lloyd_v4.core.serialization import to_json_safe
from lloyd_v4.primitives import scalar_alpha_jet_bundle, singular_alpha_jet_bundle


REPORT_DIR = Path(__file__).resolve().parent
OBSERVATIONS_MD = REPORT_DIR / "observations_data.md"
OBSERVATIONS_JSON = REPORT_DIR / "observations_data.json"


@dataclass(frozen=True)
class Fixture:
    label: str
    name: str
    function_source: str
    function: Callable[[float], float]
    x0: float
    h_grid: tuple[float, ...]
    theoretical: str
    purpose: str
    scalar_meaningful: bool = True
    singular_meaningful: bool = True


def fixture_a_sqrt(x: float) -> float:
    if x < 0:
        raise ValueError("sqrt fixture is defined for x >= 0")
    return math.sqrt(x)


def fixture_b_reciprocal(x: float) -> float:
    if x == 0.0:
        raise ZeroDivisionError("reciprocal fixture is singular at x0")
    return 1.0 / x


def fixture_c_slow_algebraic_drift(x: float) -> float:
    if x < 0:
        raise ValueError("slow drift fixture is defined for x >= 0")
    return math.sqrt(x) * (1.0 + 0.1 * (x**0.1))


def fixture_d_negative_log(x: float) -> float:
    if x <= 0:
        raise ValueError("negative log fixture is defined for x > 0")
    return -math.log(x)


def fixture_e_iterated_log(x: float) -> float:
    if x <= 0 or x >= 1.0:
        raise ValueError("iterated log fixture requires 0 < x < 1")
    inner = -math.log(x)
    if inner <= 0:
        raise ValueError("iterated log inner value must be positive")
    return math.log(inner)


def fixture_f_essential(x: float) -> float:
    if x == 0.0:
        return 0.0
    return math.exp(-1.0 / (x * x))


FIXTURES = (
    Fixture(
        label="A",
        name="pure algebraic positive",
        function_source="f(x) = x**0.5",
        function=fixture_a_sqrt,
        x0=0.0,
        h_grid=(1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1),
        theoretical="alpha = 0.5; clean fractional branch; both bundles should classify cleanly.",
        purpose="Baseline sibling agreement on a known algebraic fractional branch.",
    ),
    Fixture(
        label="B",
        name="pure algebraic negative",
        function_source="f(x) = 1.0 / x; raises at x == 0",
        function=fixture_b_reciprocal,
        x0=0.0,
        h_grid=(1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1),
        theoretical="alpha = -1; scalar should refuse at x0 and singular should classify a negative singularity.",
        purpose="Canonical informative sibling disagreement.",
        scalar_meaningful=False,
    ),
    Fixture(
        label="C",
        name="slow algebraic drift",
        function_source="f(x) = x**0.5 * (1 + 0.1 * x**0.1)",
        function=fixture_c_slow_algebraic_drift,
        x0=0.0,
        h_grid=tuple(10.0 ** (-i) for i in range(2, 9)),
        theoretical="leading alpha = 0.5 with finite-window drift from a subleading x**0.1 term.",
        purpose="Check whether current strata expose or hide slow algebraic drift evidence.",
    ),
    Fixture(
        label="D",
        name="logarithmic divergence",
        function_source="f(x) = -log(x)",
        function=fixture_d_negative_log,
        x0=0.0,
        h_grid=tuple(10.0 ** (-i) for i in range(2, 10)),
        theoretical="asymptotic slope = -1 and observed alpha = 0; scalar should refuse at x0.",
        purpose="Probe how AlphaProbe handles alpha approximately zero.",
        scalar_meaningful=False,
    ),
    Fixture(
        label="E",
        name="iterated logarithmic divergence",
        function_source="f(x) = log(-log(x)) for 0 < x < 1",
        function=fixture_e_iterated_log,
        x0=0.0,
        h_grid=tuple(10.0 ** (-i) for i in range(2, 12)),
        theoretical="finite-window alpha drifts slowly from about 0.22 toward 0 as h shrinks.",
        purpose="Canonical non-algebraic drift case.",
        scalar_meaningful=False,
    ),
    Fixture(
        label="F",
        name="essential singularity stress test",
        function_source="f(x) = exp(-1 / (x*x)); f(0) = 0",
        function=fixture_f_essential,
        x0=0.0,
        h_grid=(1e-3, 1e-2, 1e-1, 0.5),
        theoretical="flat at x0 with no power-law alpha; honest output should refuse or mark indeterminate/cancellation-dominated.",
        purpose="Stress cancellation and indeterminate strata on a non-power-law smooth flat function.",
    ),
)


def main() -> None:
    observations = [run_fixture(fixture) for fixture in FIXTURES]
    OBSERVATIONS_MD.write_text(render_markdown(observations), encoding="utf-8")
    OBSERVATIONS_JSON.write_text(json.dumps(observations, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OBSERVATIONS_MD}")
    print(f"wrote {OBSERVATIONS_JSON}")
    print(f"fixtures: {len(observations)}")


def run_fixture(fixture: Fixture) -> dict:
    scalar = scalar_alpha_jet_bundle(
        fixture.function,
        fixture.x0,
        fixture.h_grid,
        probe_id=f"task023_{fixture.label}_scalar",
        function_label=f"task023_{fixture.label}_{fixture.name.replace(' ', '_')}",
    )
    singular = singular_alpha_jet_bundle(
        fixture.function,
        fixture.x0,
        fixture.h_grid,
        probe_id=f"task023_{fixture.label}_singular",
        function_label=f"task023_{fixture.label}_{fixture.name.replace(' ', '_')}",
    )
    scalar_summary = summarize_result(scalar)
    singular_summary = summarize_result(singular)
    trace_distinct = trace_ids_are_distinct(scalar_summary, singular_summary)
    return {
        "label": fixture.label,
        "name": fixture.name,
        "function_source": fixture.function_source,
        "x0": fixture.x0,
        "h_grid": list(fixture.h_grid),
        "theoretical": fixture.theoretical,
        "purpose": fixture.purpose,
        "scalar_meaningful": fixture.scalar_meaningful,
        "singular_meaningful": fixture.singular_meaningful,
        "scalar": scalar_summary,
        "singular": singular_summary,
        "comparison": compare_siblings(fixture, scalar_summary, singular_summary, trace_distinct),
        "sibling_alpha_probe_trace_ids_distinct": trace_distinct,
    }


def summarize_result(result) -> dict:
    alpha_status = getattr(result.value, "alpha_status", None)
    return {
        "status": result.status.value,
        "observed_alpha": getattr(result.value, "observed_alpha", None),
        "observed_slope": getattr(result.value, "observed_slope", None),
        "alpha_status": None if alpha_status is None else alpha_status.value,
        "alpha_probe_trace_id": getattr(result.value, "alpha_probe_trace_id", None),
        "slope_trace_id": getattr(result.value, "slope_trace_id", None),
        "transfer_trace_ids": list(getattr(result.value, "transfer_trace_ids", ())),
        "conditioning_status": result.conditioning.status.value,
        "conditioning_notes": list(result.conditioning.notes),
        "validity": result.validity.to_json_safe(),
        "provenance_trace_id": result.provenance.trace_id,
        "typed_result": to_json_safe(result),
    }


def trace_ids_are_distinct(scalar_summary: dict, singular_summary: dict) -> bool | None:
    scalar_trace = scalar_summary["alpha_probe_trace_id"]
    singular_trace = singular_summary["alpha_probe_trace_id"]
    if scalar_trace is None or singular_trace is None:
        return None
    return scalar_trace != singular_trace


def compare_siblings(fixture: Fixture, scalar_summary: dict, singular_summary: dict, trace_distinct: bool | None) -> str:
    scalar_status = scalar_summary["status"]
    singular_status = singular_summary["status"]
    scalar_alpha_status = scalar_summary["alpha_status"]
    singular_alpha_status = singular_summary["alpha_status"]
    if not fixture.scalar_meaningful and singular_summary["observed_alpha"] is not None:
        return f"informative disagreement: scalar emitted {scalar_status}; singular emitted {singular_status}"
    if scalar_alpha_status is not None and scalar_alpha_status == singular_alpha_status:
        trace_note = "trace ids distinct" if trace_distinct else "trace distinctness not available"
        return f"alpha-status agreement on {scalar_alpha_status}; {trace_note}"
    return f"status disagreement: scalar emitted {scalar_status}; singular emitted {singular_status}"


def render_markdown(observations: Iterable[dict]) -> str:
    observations = list(observations)
    lines = [
        "# Task 023 Iterated Logarithm Discovery - Raw Observations",
        "",
        "Generated by `discovery_script.py`.",
        "",
        f"- fixtures observed: {len(observations)}",
        "- bundles run per fixture: scalar_alpha_jet_bundle, singular_alpha_jet_bundle",
        "",
    ]
    for item in observations:
        lines.extend(render_fixture_markdown(item))
    return "\n".join(lines).rstrip() + "\n"


def render_fixture_markdown(item: dict) -> list[str]:
    lines = [
        f"## Fixture {item['label']}: {item['name']}",
        "",
        f"- Function: `{item['function_source']}`",
        f"- x0: `{format_number(item['x0'])}`",
        f"- h-grid: {', '.join(format_number(h) for h in item['h_grid'])}",
        f"- Theoretical: {item['theoretical']}",
        f"- Purpose: {item['purpose']}",
        f"- Comparison: {item['comparison']}",
        f"- Sibling alpha probe trace IDs distinct: {item['sibling_alpha_probe_trace_ids_distinct']}",
        "",
        "### Bundle summary",
        "",
        "| bundle | status | alpha_status | observed_alpha | observed_slope | conditioning | alpha_probe_trace_id |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for bundle_name in ("scalar", "singular"):
        summary = item[bundle_name]
        conditioning = format_conditioning(summary)
        lines.append(
            "| "
            + " | ".join(
                [
                    bundle_name,
                    summary["status"],
                    str(summary["alpha_status"]),
                    format_number(summary["observed_alpha"]),
                    format_number(summary["observed_slope"]),
                    conditioning,
                    str(summary["alpha_probe_trace_id"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "### Scalar full typed result",
            "",
            "```json",
            json.dumps(item["scalar"]["typed_result"], indent=2, sort_keys=True),
            "```",
            "",
            "### Singular full typed result",
            "",
            "```json",
            json.dumps(item["singular"]["typed_result"], indent=2, sort_keys=True),
            "```",
            "",
        ]
    )
    return lines


def format_conditioning(summary: dict) -> str:
    notes = "; ".join(summary["conditioning_notes"])
    return summary["conditioning_status"] if not notes else f"{summary['conditioning_status']} ({notes})"


def format_number(value: object) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return f"{value:.16e}"
    return str(value)


if __name__ == "__main__":
    main()
