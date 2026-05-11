import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "Build_Docs" / "Architecture"


def test_layer_manifest_is_machine_readable() -> None:
    manifest_json = ARCH / "layer_manifest.json"
    if manifest_json.exists():
        payload = json.loads(manifest_json.read_text(encoding="utf-8"))
        layers = payload["layers"]
        assert {layer["name"] for layer in layers} == {
            "core",
            "primitives",
            "projection",
            "metrology",
            "branch",
            "refinery",
            "history",
            "solver",
        }
        for layer in layers:
            assert isinstance(layer["description"], str) and layer["description"]
            assert isinstance(layer["parents"], list)
            assert isinstance(layer["provides"], dict)
        return

    text = (ARCH / "LAYER_MANIFEST.md").read_text(encoding="utf-8")
    for layer in ["core", "primitives", "projection", "metrology", "branch", "refinery", "history", "solver"]:
        pattern = rf"^## {layer}\n.*?^### Parents\n.*?^### Provides"
        assert re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
