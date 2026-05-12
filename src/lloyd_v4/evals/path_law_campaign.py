from __future__ import annotations

import argparse
import json
from pathlib import Path

from lloyd_v4.core.serialization import to_json_safe

from .multi_precision_four_form import FORM_KEYS
from .path_law_discovery import build_candidate_library, discover_path_law_for_form
from .schwarzschild_four_form import sweep_r_values


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "Build_Docs" / "Reports" / "task025_path_law_discovery"
DEFAULT_OUTPUT = REPORT_DIR / "campaign_output.json"


def run_campaign() -> dict[str, object]:
    r_values = sweep_r_values()
    forms = {form_id: discover_path_law_for_form(form_id, r_values).to_json_safe() for form_id in FORM_KEYS}
    f4_gate = forms["F4"]["rediscovery_gate"]
    return {
        "campaign": "task025_path_law_discovery",
        "expression_family": "schwarzschild_four_form",
        "r_count": len(r_values),
        "r_min": r_values[0],
        "r_max": r_values[-1],
        "candidate_term_count": len(build_candidate_library()),
        "max_sparse_terms": 3,
        "candidate_law_count": 833,
        "forms": forms,
        "f4_rediscovery_gate": f4_gate,
        "law_claims_trusted": bool(f4_gate and f4_gate["passed"]),
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


if __name__ == "__main__":
    main()
