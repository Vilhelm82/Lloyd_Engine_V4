from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_task000_architecture_docs_exist() -> None:
    expected = [
        "Build_Docs/Architecture/AXIOMS.md",
        "Build_Docs/Architecture/DESIGN_THESIS.md",
        "Build_Docs/Architecture/STATUS_CALCULUS.md",
        "Build_Docs/Architecture/PROTOCOL_CONTRACTS.md",
        "Build_Docs/Architecture/PROVENANCE_MODEL.md",
        "Build_Docs/Architecture/RESULT_TYPES.md",
        "Build_Docs/Architecture/METROLOGY_PRINCIPLES.md",
        "Build_Docs/Architecture/V3_REFERENCE_LEDGER.md",
        "Build_Docs/Architecture/ROADMAP.md",
    ]

    missing = [path for path in expected if not (ROOT / path).is_file()]

    assert missing == []


def test_task000_reports_exist() -> None:
    expected = [
        "Build_Docs/Reports/task000/task000_summary.md",
        "Build_Docs/Reports/task000/created_files_manifest.csv",
        "Build_Docs/Reports/task000/design_decisions.md",
        "Build_Docs/Reports/task000/task001_scope_projective_ratio.md",
    ]

    missing = [path for path in expected if not (ROOT / path).is_file()]

    assert missing == []
