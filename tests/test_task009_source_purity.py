from pathlib import Path
import re

from _audit_helpers.precision_floor_allowance import is_allowed_precision_floor_comment_token


ROOT = Path(__file__).resolve().parents[1]


def _source_files(*roots: Path) -> list[Path]:
    return [path for root in roots for path in root.rglob("*.py") if path.is_file()]


def test_task009_source_audits() -> None:
    literal_checks = [
        (ROOT / "src", ("lloyd" + "_v3", "safe" + "_mask", 'projection_mode="' + "legacy" + '"', "legacy" + "_compat", "clamp" + "_min")),
        (ROOT / "src" / "lloyd_v4", ("safe" + "_divide", "safe" + "_denominator", "denominator" + "_floor", "small" + "_denominator", "res" + "cue", "gu" + "ard", "clamp", "stabilized" + "_log", "log" + "_offset", "log1p", "isclose", "allclose", "thresh" + "old", "toler" + "ance", "confidence" + "_score", "weighted" + "_score", "smoothing", "hysteresis", "interpolate", "extrapolate")),
        (ROOT / "src" / "lloyd_v4", ("lloyd" + "_core", "lloyd" + "_core_nvar", "lloyd" + "_decomposition", "hyperdual", "halley", "multi" + "_start", "route" + "_score")),
        (ROOT / "src" / "lloyd_v4" / "solver", ("JetBundle", "shape" + "_operator", "singularity", "symmetry", "centrifuge", "surface" + "_mesh", "implicit" + "_chart", "finite" + "_eta", "domain" + "_consumer", "domain" + "_classifier", "bearing", "aerospace", "betting", "scanner", "parser", "cas", "symbolic" + "_simplifier")),
        (ROOT / "src" / "lloyd_v4", ("adapter", "bridge", "compatibility" + "_shim", "downgrade", "legacy" + "_mode", "cross" + "_engine")),
    ]
    offenders = []
    for root, tokens in literal_checks:
        for path in _source_files(root):
            rel = str(path.relative_to(ROOT))
            text = path.read_text(encoding="utf-8")
            for token in tokens:
                if token in text and not is_allowed_precision_floor_comment_token(rel, text, token):
                    offenders.append(f"{rel}:{token}")
    for path in _source_files(ROOT / "src"):
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        for token in ("epsilon", "eps"):
            if re.search(rf"\b{token}\b", text) and not is_allowed_precision_floor_comment_token(rel, text, token):
                offenders.append(f"{rel}:{token}")

    assert offenders == []


def test_solver_dependency_direction_and_leakage() -> None:
    dependency_roots = [
        ROOT / "src" / "lloyd_v4" / "core",
        ROOT / "src" / "lloyd_v4" / "primitives",
        ROOT / "src" / "lloyd_v4" / "projection",
        ROOT / "src" / "lloyd_v4" / "metrology",
        ROOT / "src" / "lloyd_v4" / "branch",
        ROOT / "src" / "lloyd_v4" / "refinery",
        ROOT / "src" / "lloyd_v4" / "history",
    ]
    offenders = []
    for path in _source_files(*dependency_roots):
        text = path.read_text(encoding="utf-8")
        for token in ("lloyd_v4.solver", "from lloyd_v4.solver", "import solver"):
            if token in text:
                offenders.append(f"{path.relative_to(ROOT)}:{token}")
    leakage_roots = [
        ROOT / "src" / "lloyd_v4" / "primitives",
        ROOT / "src" / "lloyd_v4" / "projection",
        ROOT / "src" / "lloyd_v4" / "metrology",
        ROOT / "src" / "lloyd_v4" / "branch",
        ROOT / "src" / "lloyd_v4" / "refinery",
        ROOT / "src" / "lloyd_v4" / "history",
    ]
    for path in _source_files(*leakage_roots):
        text = path.read_text(encoding="utf-8")
        for token in ("TypedProjectionSolver", "SolverStatus", "solver_step", "solver_converged", "solver_projection", "solver_branch", "solver_refinery", "solver_history"):
            if token in text:
                offenders.append(f"{path.relative_to(ROOT)}:{token}")

    assert offenders == []
