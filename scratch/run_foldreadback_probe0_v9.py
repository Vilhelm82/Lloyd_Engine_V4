"""
Fold-Readback Probe 0 -- v9.3 task B: two-tier fused-sweep.
Pre-registry: preregistry.md v9.3 FROZEN.

Imports v7 primitives + corrected v8 law VERBATIM (same code objects,
no re-paste). ONLY new authored code: W-window construction + the
joint composer + arm/functional assignment (flagged joints 1/2/3).
No new measurement primitive. No numpy. Decimal prec=150 substrate
(inherited from v7 module import). mb=24, M1.
"""
import importlib.util as ilu, os, json, time
from decimal import Decimal

_d = os.path.dirname(__file__)
def _load(name, fn):
    s = ilu.spec_from_file_location(name, os.path.join(_d, fn))
    m = ilu.module_from_spec(s); s.loader.exec_module(m); return m
V7  = _load("_fr_v7", "run_foldreadback_probe0_v7.py")
LAW = _load("_fr_law", "foldreadback_probe0_v8_outcomelaw.py")

sweep   = V7.sweep
binexp  = V7.binade_exp
DISTRIB = V7.DISTRIB
disc    = V7.disc
nullband= V7.nullband
ols_ok  = V7.ols_design_pivot_ok
classify= LAW.classify_instrument            # corrected, v7-single-sourced
MB = 24
ARM_N_FUNCS = ["level_histogram", "transition", "signed_occ", "lattice_rank"]
ARM_W_FUNC  = "sign_pattern"
OUT = os.path.join(_d, "foldreadback_probe0_v9_artifact.json")


def creg(pts):
    return sorted([p for p in pts if p["e_f"] < p["e_x"]], key=lambda p: p["f0"])

def deepest_binades(cpts):
    # binades present, ordered deepest (most negative f) -> shallow
    bs = sorted({binexp(p["f0"]) for p in cpts})
    return bs                                # ascending == deepest first

def region_W(cpts, ordered_binades, W):
    keep = set(ordered_binades[:W])
    return [p for p in cpts if binexp(p["f0"]) in keep]

def arm_eval(regA1, regA2, arm):
    """Reuse v8 law per-arm. Returns (valid, infers, per)."""
    if len(regA1) < 5 or len(regA2) < 5:
        return False, {}, {"reason": "underpopulated"}
    nb = nullband(regA1)                      # v7 within-slope null, VERBATIM
    funcs = ARM_N_FUNCS if arm == "N" else [ARM_W_FUNC]
    per = {}
    nondeg = []
    for nm in funcs:
        band = nb[nm]
        inst = classify(nm, band)
        per[nm] = {"band": band, "instrument": inst}
        if inst == "nondegenerate":
            nondeg.append(nm)
    # ARM-W additionally requires OLS soundness; ARM-N must NOT use OLS.
    ols = ols_ok(regA1) if arm == "W" else None
    valid = (len(nondeg) >= 1) and (ols if arm == "W" else True)
    # inference: A1 vs A2 discrepancy vs band, on nondegenerate funcs only
    sep = {}
    for nm in nondeg:
        fn = DISTRIB.get(nm) or V7.SCALARS.get(nm)
        d = disc(nm, fn([p["L"] for p in regA1]), fn([p["L"] for p in regA2]))
        sep[nm] = (d > per[nm]["band"], d)
    fold = any(s[0] for s in sep.values())
    return bool(valid), {"fold": fold, "sep": sep, "ols": ols,
                         "nondeg": nondeg}, per


def run_fixture(aA1, aA2):
    SA1 = sweep(Decimal(aA1), MB); SA1 = SA1[0] if isinstance(SA1, tuple) else SA1
    SA2 = sweep(Decimal(aA2), MB); SA2 = SA2[0] if isinstance(SA2, tuple) else SA2
    cA1, cA2 = creg(SA1), creg(SA2)
    ob = deepest_binades(cA1)
    Wmax = len(ob)
    traj = []
    for W in range(1, Wmax + 1):
        rN1, rN2 = region_W(cA1, ob, W), region_W(cA2, ob, W)
        vN, iN, _ = arm_eval(rN1, rN2, "N")
        vW, iW, _ = arm_eval(rN1, rN2, "W")    # SAME region(W), both arms
        traj.append({"W": W, "nN": len(rN1),
                      "armN_valid": vN, "armN_fold": iN.get("fold", False),
                      "armW_valid": vW, "armW_fold": iW.get("fold", False)})
    return traj, Wmax


def main():
    t0 = time.time()
    print("=== Fold-Readback Probe 0 v9.3 (FROZEN) two-tier fused-sweep ===")

    # primary fixture: A1 a=0.500 vs A2 a=0.501 (separation 0.001)
    traj, Wmax = run_fixture("0.500", "0.501")
    # matched AFFINE control: a=1.0 (linear transfer, integer exponent,
    # structurally NO fold) vs same -> any "fold" here = manufactured
    aff, _ = run_fixture("1.000", "1.000")

    print(f"Wmax={Wmax}  (W = # deepest cancellation binades)")
    print(" W  nN  armN_valid armN_fold | armW_valid armW_fold | AFF_armN_fold AFF_armW_fold")
    for i, r in enumerate(traj):
        a = aff[i] if i < len(aff) else {}
        print(f"{r['W']:2d} {r['nN']:3d}    {str(r['armN_valid']):5s}      "
              f"{str(r['armN_fold']):5s}   |   {str(r['armW_valid']):5s}     "
              f"{str(r['armW_fold']):5s}   |    {str(a.get('armN_fold')):5s}      "
              f"{str(a.get('armW_fold')):5s}")

    vN = [r["armN_valid"] for r in traj]
    vW = [r["armW_valid"] for r in traj]
    overlap = [r["W"] for r in traj if r["armN_valid"] and r["armW_valid"]]

    # AFFINE KILL: any fold on the affine control in any overlap W
    aff_fold_in_overlap = any(
        (aff[i]["armN_fold"] or aff[i]["armW_fold"])
        for i, r in enumerate(traj) if r["W"] in overlap and i < len(aff))

    # v9.2 5-level precedence
    if aff_fold_in_overlap:
        outcome = "two_tier_disqualified_manufactured"
    elif overlap:
        fold_in_overlap = all(
            traj[i]["armN_fold"] and traj[i]["armW_fold"]
            for i, r in enumerate(traj) if r["W"] in overlap)
        outcome = ("two_tier_overlap_fold_observed" if fold_in_overlap
                   else "two_tier_overlap_no_fold")
    else:
        outcome = "two_tier_validity_disjoint_no_overlap"

    # v9.3 BREAK-CONFRONT (pre-derived, pre-assigned)
    mono_N = all(vN[i] >= vN[i + 1] for i in range(len(vN) - 1))  # non-increasing
    mono_W = all(vW[i] <= vW[i + 1] for i in range(len(vW) - 1))  # non-decreasing
    bracket_N = (vN[-1] is False)        # ARM-N invalid at widest (v6/v7)
    bracket_W = (vW[-1] is True)         # ARM-W valid at widest  (v6/v7)
    break_ok = mono_N and mono_W and bracket_N and bracket_W
    break_verdict = ("CONFIRMED: clean result breaks within derived expectation"
                     if break_ok else
                     "INVALIDATED: break violates monotonicity/bracket -> "
                     "the derivation that produced the clean result was wrong")

    print(f"\noverlap W = {overlap if overlap else 'NONE (disjoint)'}")
    print(f"OUTCOME (v9.2 precedence) = {outcome}")
    print(f"break-confront: mono_N={mono_N} mono_W={mono_W} "
          f"bracket_N={bracket_N} bracket_W={bracket_W}")
    print(f"=== BREAK-CONFRONT: {'PASS' if break_ok else 'FAIL'} ===")
    print(break_verdict)
    if not break_ok:
        print(">>> Per v9.3: clean result is INVALIDATED. Not a finding.")

    art = dict(probe="foldreadback_probe0", preregistry="v9.3", mb=MB,
               Wmax=Wmax, trajectory=traj, affine=aff, overlap=overlap,
               outcome=outcome,
               break_confront=dict(mono_N=mono_N, mono_W=mono_W,
                                   bracket_N=bracket_N, bracket_W=bracket_W,
                                   passed=break_ok, verdict=break_verdict),
               runtime_s=round(time.time() - t0, 3))
    json.dump(art, open(OUT, "w"), indent=2, default=str)
    print(f"saved {OUT} ({art['runtime_s']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
