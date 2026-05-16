"""
Fold-Readback Probe 0 -- v8 task A: outcome-stratification correction.

Pure outcome-law module. Touches NO probe mechanics. Reads the frozen,
deterministic v7 run record and applies the v8 corrected outcome law
(preregistry.md v8). This file IS the frozen desk-check: success ==
the law applied to the existing frozen numbers yields the v8
acceptance target. No probe rerun (the v7 arithmetic is deterministic
and already on disk; re-deriving it confirms nothing).

AUTHORED JOINT (flagged for audit, not silent): ANALYTIC_MAX below.
Grounding -- the three L1 distance functionals over a normalised
2-level signed occupancy have analytic max 2.0 (stated as "L1
analytic max" in closeout_v7.md and the v8 acceptance target);
sign_pattern is a sign-agreement fraction in [0,1] -> max 1.0;
lattice_rank classifies via the band==0 collapse rule and needs no
max. This table is the single audited constant in task A. When this
folds into V4 the clean form is each functional declaring its own
analytic_max; here it is grounded in the frozen lineage.
"""
import json

ART = "/home/william_lloydlt/projects/V4/Lloyd_Engine_V4/scratch/foldreadback_probe0_v7_artifact.json"
# Byte-identical to the Vera-tree artifact_v7.json: both written from
# the single v7 run record. Reading either yields the same numbers.

# ERRATUM E-A1 (post-freeze, byte-traced): the original task-A value
# sign_pattern=1.0 was WRONG. f_sign(L) = (#pos-#neg)/#nonzero in
# [-1,+1] (v7 runner), so disc=|A-B| has analytic max 2.0, not 1.0.
# Non-consequential for the v7 desk-check (band 0.5 < both 1.0 and
# 2.0 -> nondegenerate either way; v7 outcome unchanged) but a wrong
# load-bearing constant is an erratum. Resolution: single-source the
# table from the v7 runner (the correct definition) instead of
# re-declaring it -- eliminates the v7/v8 inconsistency at root.
import importlib.util as _ilu, sys as _sys, os as _os
_v7p = _os.path.join(_os.path.dirname(__file__), "run_foldreadback_probe0_v7.py")
_spec = _ilu.spec_from_file_location("_fr_v7", _v7p)
_v7 = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_v7)
ANALYTIC_MAX = dict(_v7.ANALYTIC_MAX)   # SINGLE SOURCE OF TRUTH (v7)
FUNCS = ["level_histogram", "transition", "signed_occ",
         "sign_pattern", "lattice_rank"]


def classify_instrument(name, band):
    """v8 law: instrument validity from the NULL BAND alone."""
    if band == 0:
        return "collapsed"
    amax = ANALYTIC_MAX.get(name)
    if amax is not None and band == amax:
        return "saturated"
    return "nondegenerate"


def apply_v8_law(art):
    g2 = art["gate2_nullband"]
    g3 = art["gate3"]
    per = {}
    for f in FUNCS:
        band = g2[f]["band"]
        computed = (g3[f].get("status") == "ok")     # old "ok" = THIS only
        inst = classify_instrument(f, band)
        if inst == "nondegenerate":
            infer = "separated" if g3[f]["separates"] else "searched_no_separation"
        else:
            infer = "untested"
        per[f] = dict(computed=computed, instrument=inst, inference=infer,
                      band=band, discrepancy=g3[f]["discrepancy"])

    sound      = [f for f in FUNCS if per[f]["instrument"] == "nondegenerate"]
    degenerate = [f for f in FUNCS if f not in sound]
    separated  = [f for f in sound if per[f]["inference"] == "separated"]

    # Fixed precedence, first match wins (v8 spec).
    if not sound:
        outcome = "probe_void_degenerate"; scope = []; untested = degenerate
    elif separated:
        outcome = "precondition_supported_or_cancellation_on_sound"
        scope = sound; untested = degenerate
    elif len(sound) == 5 and not separated:
        outcome = "precondition_refused_no_signal"; scope = sound; untested = []
    else:  # 0 < |sound| < 5 and separated == {}
        outcome = "partial_search_no_separation"; scope = sound; untested = degenerate
    return per, sound, degenerate, separated, outcome, scope, untested


# ---- frozen v8 acceptance target (from preregistry.md v8) ----
TARGET = dict(
    instrument={"level_histogram": "saturated", "transition": "saturated",
                "signed_occ": "saturated", "lattice_rank": "collapsed",
                "sign_pattern": "nondegenerate"},
    sound=["sign_pattern"],
    untested=["level_histogram", "transition", "signed_occ", "lattice_rank"],
    sign_pattern_inference="searched_no_separation",
    separated=[],
    outcome="partial_search_no_separation",
)


def main():
    art = json.load(open(ART))
    per, sound, degenerate, separated, outcome, scope, untested = apply_v8_law(art)

    print("=== v8 task A -- outcome-law desk-check (NO probe rerun) ===")
    print(f"runner-emitted v7 outcome (REJECTED in closeout_v7): "
          f"{art.get('outcome', art.get('outcome_runner_emitted'))}")
    print("per-functional (computed / instrument / inference):")
    for f in FUNCS:
        p = per[f]
        print(f"  {f:16s} comp={str(p['computed']):5s} "
              f"inst={p['instrument']:13s} infer={p['inference']:22s} "
              f"(band={p['band']}, disc={p['discrepancy']})")
    print(f"sound      = {sound}")
    print(f"untested   = {sorted(degenerate)}")
    print(f"separated  = {separated}")
    print(f"v8 OUTCOME = {outcome}  scope={scope}")

    # ---- assert against frozen acceptance target ----
    checks = []
    checks.append(("instrument map",
        {f: per[f]["instrument"] for f in FUNCS} == TARGET["instrument"]))
    checks.append(("sound set", sound == TARGET["sound"]))
    checks.append(("untested set",
        sorted(degenerate) == sorted(TARGET["untested"])))
    checks.append(("sign_pattern inference",
        per["sign_pattern"]["inference"] == TARGET["sign_pattern_inference"]))
    checks.append(("separated empty", separated == TARGET["separated"]))
    checks.append(("outcome", outcome == TARGET["outcome"]))
    allok = all(ok for _, ok in checks)
    print("--- acceptance ---")
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"=== DESK-CHECK {'PASSED' if allok else 'FAILED'} ===")
    print("Interpretation: the v8 law applied to the FROZEN v7 numbers "
          "yields the stratified outcome the v7 closeout asserted by "
          "hand. The v4-class flattening is closed at both layers "
          "(per-functional status split + scoped precedence)."
          if allok else
          "Interpretation: law spec is WRONG (not the data) -- revise "
          "preregistry.md v8, do not touch the artifact.")
    return 0 if allok else 1


if __name__ == "__main__":
    raise SystemExit(main())
