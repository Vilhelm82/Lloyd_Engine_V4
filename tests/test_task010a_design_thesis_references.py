from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THESIS = ROOT / "Build_Docs" / "Architecture" / "DESIGN_THESIS.md"


def test_design_thesis_references_reality_check_commitments_and_preserves_existing_content() -> None:
    text = THESIS.read_text(encoding="utf-8")

    assert "## Design Commitments After the Reality-Check Review" in text
    assert "Axiom 11" in text
    assert "Axiom 12" in text
    assert "agnostic-workshop" in text
    assert "DISCOVERY_PHILOSOPHY.md" in text

    assert "## Layer Architecture" in text
    assert "## Initial Primitive Order" in text
    assert "D (+) S = P" in text
