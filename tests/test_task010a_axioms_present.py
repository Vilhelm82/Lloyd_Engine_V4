from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AXIOMS = ROOT / "Build_Docs" / "Architecture" / "AXIOMS.md"


def _section(text: str, start: str, end: str | None = None) -> str:
    start_index = text.index(start)
    if end is None:
        return text[start_index:]
    return text[start_index:text.index(end, start_index)]


def test_axiom_11_and_12_are_present_with_required_subsections() -> None:
    text = AXIOMS.read_text(encoding="utf-8")

    assert "## 11. Epistemic Stance Only" in text
    assert "## 12. Self-Derivation" in text

    axiom_11 = _section(text, "## 11. Epistemic Stance Only", "## 12. Self-Derivation")
    axiom_12 = _section(text, "## 12. Self-Derivation")

    for section in (axiom_11, axiom_12):
        assert "Statement:" in section
        assert "Rationale:" in section
        assert "V4 forbids:" in section
        assert "V4 must represent instead:" in section
