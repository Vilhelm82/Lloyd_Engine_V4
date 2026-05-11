from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "Build_Docs" / "Architecture"
TASKS = ROOT / "Build_Docs" / "Agent_tasks"


def test_discovery_philosophy_layer_manifest_and_task_template_exist() -> None:
    discovery = (ARCH / "DISCOVERY_PHILOSOPHY.md").read_text(encoding="utf-8")
    for heading in [
        "## The agnostic workshop",
        "## The dark room",
        "## The engine as discovery instrument",
        "## No failures, only observations of varying refinement",
        "## Relationship to consumers",
    ]:
        assert heading in discovery

    manifest = (ARCH / "LAYER_MANIFEST.md").read_text(encoding="utf-8")
    for layer in ["core", "primitives", "projection", "metrology", "branch", "refinery", "history", "solver"]:
        assert f"## {layer}" in manifest

    template = (TASKS / "TASK_TEMPLATE.md").read_text(encoding="utf-8")
    for heading in [
        "## Repository",
        "## Current Verified Baseline",
        "## Task Goal",
        "## Design Principles",
        "## Primitive-Sufficiency Gate",
        "## Required Deliverables",
        "## Required Tests",
        "## Required Commands",
        "## Non-Goals",
        "## Completion Report",
        "## Acceptance Criteria",
    ]:
        assert heading in template
