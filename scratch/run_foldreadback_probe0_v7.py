"""Fold-Readback Probe 0 — v5 runner (strictly to preregistry.md v5 FROZEN).

Adds Gate 0 (alpha-blind measurement-geometry viability) + binade-band
region selection (NOT the inherited Sterbenz label) + probe_void_degenerate
and fixture_refused_no_viable_region + frozen outcome precedence.
reseat/fit_ols VERBATIM from run_phase4C.py (provenance).

RUN: cd /home/william_lloydlt/projects/V4/Lloyd_Engine_V4
     python3 scratch/run_foldreadback_probe0_v5.py
OUT: scratch/foldreadback_probe0_v5_artifact.json
"""
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
getcontext().prec = 150
import json, time

OUT="/home/william_lloydlt/projects/V4/Lloyd_Engine_V4/scratch/foldreadback_probe0_v7_artifact.json"
ETA=Decimal("1e-6"); MB=24; TOL=0.020; AP=max(2*MB//3+30,80)
U_AP=Decimal(10)**(-(AP-1))                       # substrate unit roundoff at prec ap

def reseat(v, mant_bits):                          # VERBATIM phase4C
    if v==0: return Decimal(0)
    sign=1 if v>0 else -1
    v=abs(v); two=Decimal(2); e=0
    if v>=1:
        while two**(e+1)<=v: e+=1
    else:
        while two**e>v: e-=1
    ulp=two**(e-mant_bits+1)
    q=(v/ulp).quantize(Decimal(1))
    return sign*q*ulp

def fit_ols(pts, ap):                              # VERBATIM phase4C
    if len(pts)<5: return None
    old=getcontext().prec; getcontext().prec=max(ap,50)
    try:
        lp=[(f.ln(),T.ln()) for (f,T) in pts if f>0 and T>0]
        n=len(lp)
        if n<5: return None
        sx=sum((x for x,_ in lp),Decimal(0)); sy=sum((y for _,y in lp),Decimal(0))
        sxx=sum((x*x for x,_ in lp),Decimal(0)); sxy=sum((x*y for x,y in lp),Decimal(0))
        nD=Decimal(n); den=nD*sxx-sx*sx
        if den==0: return None
        return float((nD*sxy-sx*sy)/den)
    finally:
        getcontext().prec=old

def binade_exp(v):
    if v==0: return 0
    v=abs(v); two=Decimal(2); e=0
    if v>=1:
        while two**(e+1)<=v: e+=1
    else:
        while two**e>v: e-=1
    return e

def g_seated(f,a,mb): return reseat((a*f.ln()).exp(),mb)
def g_oracle(f,a):    return (a*f.ln()).exp()

def grid75_x():
    base={(Decimal(10)**(-k))*Decimal(m) for k in range(1,16) for m in [1,2,3,5,7]}
    near1={Decimal(1)-Decimal(10)**(-k) for k in range(1,16)}   # v6: reach x->1
    return sorted(base|near1,reverse=True)

def measure_point(x,a,mb):
    f0=reseat(Decimal(1)-x,mb)
    if f0<=0: return None
    df=f0*ETA; f1=reseat(f0+df,mb)
    if f1==f0: return None
    try:
        gs0=g_seated(f0,a,mb); gs1=g_seated(f1,a,mb)
        gh0=g_oracle(f0,a);    gh1=g_oracle(f1,a)
    except Exception:
        return None
    Ts=(gs1-gs0)/df; Te=(gh1-gh0)/df
    if not Ts.is_finite() or not Te.is_finite(): return None
    E=Ts-Te; e=binade_exp(f0); ulp=Decimal(2)**(e-mb+1)
    L=int((E/ulp).quantize(Decimal(1),rounding=ROUND_HALF_EVEN))
    return dict(x=x,f0=f0,Ts=Ts,E=E,L=L,e_f=e,e_x=binade_exp(x),
                c1=float(x-Decimal("0.5")),c2=float(e),c3=float(abs(Decimal(1)-x)))

def sweep(a,mb):
    pts=[]; nn=0
    for x in grid75_x():
        m=measure_point(x,a,mb)
        if m is None: nn+=1; continue
        pts.append(m)
    pts.sort(key=lambda p:p["f0"])
    return pts,nn

# functionals (frozen)
def _norm(d):
    s=sum(d.values()); return {k:v/s for k,v in d.items()} if s>0 else {}
def f_hist(L):  return _norm({abs(v):0 for v in L if v!=0} and {abs(v):sum(1 for w in L if w!=0 and abs(w)==abs(v)) for v in L if v!=0})
def f_hist2(L):
    h={}
    for v in L:
        if v!=0: h[abs(v)]=h.get(abs(v),0)+1
    return _norm(h)
def f_trans(L):
    t={}
    for x,y in zip(L,L[1:]): t[(x,y)]=t.get((x,y),0)+1
    return _norm(t)
def f_sign(L):
    nz=[v for v in L if v!=0]
    if not nz: return 0.0
    return (sum(1 for v in nz if v>0)-sum(1 for v in nz if v<0))/len(nz)
def f_rank(L): return len({abs(v) for v in L if v!=0})
def f_socc(L):
    h={}
    for v in L:
        if v!=0: h[v]=h.get(v,0)+1
    return _norm(h)
DISTRIB={"level_histogram":f_hist2,"transition":f_trans,"signed_occ":f_socc}
SCALARS={"sign_pattern":f_sign,"lattice_rank":f_rank}
ANALYTIC_MAX={"level_histogram":2.0,"transition":2.0,"signed_occ":2.0,"sign_pattern":2.0}  # lattice_rank: no finite max
def L1(a,b):
    ks=set(a)|set(b); return sum(abs(a.get(k,0.0)-b.get(k,0.0)) for k in ks)
def disc(nm,A,B): return abs(A-B) if nm in SCALARS else L1(A,B)
def allf(L):
    o={};
    for nm,fn in DISTRIB.items(): o[nm]=fn(L)
    for nm,fn in SCALARS.items(): o[nm]=fn(L)
    return o
def nz(pts): return sum(1 for p in pts if p["L"]!=0)

def ols_design_pivot_ok(pts):
    """Tightening A: 2x2 log-f normal-eqn 2nd pivot >= U_AP relative."""
    old=getcontext().prec; getcontext().prec=max(AP,50)
    try:
        lp=[p["f0"].ln() for p in pts if p["f0"]>0]
        n=len(lp)
        if n<5: return False
        sx=sum(lp,Decimal(0)); sxx=sum((v*v for v in lp),Decimal(0)); nD=Decimal(n)
        den=nD*sxx-sx*sx                       # 2nd-pivot * nD (Cauchy-Schwarz >=0)
        scale=nD*sxx if sxx>0 else Decimal(1)
        return bool(scale>0 and (abs(den)/scale)>=U_AP)
    finally:
        getcontext().prec=old

def halves(pts):
    s=sorted(pts,key=lambda p:p["f0"]); return s[0::2],s[1::2]

def nullband(pts):
    h1,h2=halves(pts); nbA={}
    for nm in list(DISTRIB)+list(SCALARS):
        fn=DISTRIB.get(nm) or SCALARS.get(nm)
        nbA[nm]=disc(nm, fn([p["L"] for p in h1]), fn([p["L"] for p in h2]))
    return nbA

def band_cancellation_relevant(pts):
    """Tightening C: structural leading-bit-loss test on 1-x (strict)."""
    return len(pts)>0 and all(p["e_f"] < p["e_x"] for p in pts)

def main():
    t0=time.time()
    print("=== Fold-Readback Probe 0 v7 (FROZEN) ===")
    A1,nnA1=sweep(Decimal("0.500"),MB)
    A2,nnA2=sweep(Decimal("0.501"),MB)
    H ,nnH =sweep(Decimal("0.5005"),MB)
    print(f"observable pts (full grid v6): A1={len(A1)} A2={len(A2)} H={len(H)}")

    art=dict(probe="foldreadback_probe0",preregistry="v7",mb=MB,
             region=None,gate0=None,gate1=None,gate2_nullband={},
             gate3={},gate4={},gate5={},outcome=None,interpretation=None)

    # v6: SINGLE cancellation-relevant region (no binade partition).
    def cregion(pts): return [p for p in pts if p["e_f"]<p["e_x"]]
    RA1=sorted(cregion(A1),key=lambda p:p["f0"])
    RA2=sorted(cregion(A2),key=lambda p:p["f0"])
    RH =sorted(cregion(H ),key=lambda p:p["f0"])
    print(f"cancellation-relevant region pts: A1={len(RA1)} A2={len(RA2)} H={len(RH)}")
    if RA1:
        lo=min(p['f0'] for p in RA1); hi=max(p['f0'] for p in RA1)
        print(f"  region f-range A1 [{lo:.3e},{hi:.3e}] binades={sorted({p['e_f'] for p in RA1})}")

    def finish(o,sub=None,interp=None):
        art["outcome"]=o
        if sub: art["sub_reason"]=sub
        if interp: art["interpretation"]=interp
        art["runtime_s"]=round(time.time()-t0,2)
        with open(OUT,"w") as fp: json.dump(art,fp,indent=2,default=str)
        print(f"\n=== OUTCOME (frozen precedence): {o} {sub or ''} ===")
        print(f"saved {OUT} ({art['runtime_s']}s)")

    def nondeg_resid(p):
        Ls=[q["L"] for q in p]
        return any(v!=0 for v in Ls) and len({abs(v) for v in Ls if v!=0})>=2
    ols_ok=bool(RA1 and RA2 and ols_design_pivot_ok(RA1) and ols_design_pivot_ok(RA2))
    occ_ok=bool(RA1 and RA2 and nz(RA1)>=8 and nz(RA2)>=8)
    resid_ok=bool(RA1 and RA2 and nondeg_resid(RA1) and nondeg_resid(RA2))
    nbA1=nullband(RA1) if len(RA1)>=4 else None
    nbA2=nullband(RA2) if len(RA2)>=4 else None
    funcs_ok=[]
    if nbA1 and nbA2:
        for nm in list(DISTRIB)+list(SCALARS):
            bv=max(nbA1[nm],nbA2[nm]); amax=ANALYTIC_MAX.get(nm)
            if not (amax is not None and bv>=amax) and bv!=0.0:
                funcs_ok.append(nm)
    g0=dict(region_n_A1=len(RA1),region_n_A2=len(RA2),
            nz_A1=(nz(RA1) if RA1 else 0),nz_A2=(nz(RA2) if RA2 else 0),
            ols_design_ok=ols_ok,occupancy_ok=occ_ok,
            per_slope_resid_ok=resid_ok,nondegenerate_functionals=funcs_ok,
            binades_spanned=sorted({p['e_f'] for p in RA1}) if RA1 else [])
    art["region"]=g0
    print(f"GATE 0: OLS_ok={ols_ok} occ={occ_ok} resid={resid_ok} "
          f"ndeg_funcs={len(funcs_ok)} nz_A1={g0['nz_A1']} nz_A2={g0['nz_A2']}")
    gate0_pass = ols_ok and occ_ok and resid_ok and len(funcs_ok)>=1
    if not (RA1 and RA2) or not gate0_pass:
        finish("fixture_refused_no_viable_region",
            interp=("v6 single cancellation-relevant region (x->1 grid, "
            "no binade partition, real log-f spread). Region empty or "
            "fails alpha-blind Gate 0. If the region HAS real log-f "
            "spread and still fails, confound (a) is isolated: the "
            "affine cancelling regime is genuinely non-viable on EARNED "
            "grounds, not the v5 grid/partition artifact. Next fixture "
            "in a separate pre-registry. NOT a failed hypothesis."))
        return
    art["gate0"]=dict(passed=True,n_A1=len(RA1),n_A2=len(RA2),
                      binades_spanned=g0["binades_spanned"])

    # GATE 1 toothless (now non-vacuous)
    def winsl(pts):
        sl=[]
        for a in range(0,len(pts)-9+1):
            s=fit_ols([(q["f0"],q["Ts"]) for q in pts[a:a+9]],AP)
            if s is not None: sl.append(s)
        return sl
    sA,sB=winsl(RA1),winsl(RA2)
    if len(sA)<1 or len(sB)<1:
        finish("probe_void_degenerate","gate1_windows_unformable")
        return
    def med(v): v=sorted(v); n=len(v); return v[n//2] if n%2 else (v[n//2-1]+v[n//2])/2
    def iqr(v):
        v=sorted(v); n=len(v); return v[int((n-1)*0.75)]-v[int((n-1)*0.25)]
    sep=abs(med(sA)-med(sB)); pooled=(iqr(sA)+iqr(sB))/2 if len(sA)>3 and len(sB)>3 else max(iqr(sA),iqr(sB),1e-12)
    art["gate1"]=dict(sep=sep,pooled_iqr=pooled,separates=bool(sep>=pooled),
                      n_win_A1=len(sA),n_win_A2=len(sB),
                      med_A1=med(sA),med_A2=med(sB))
    print(f"\nGATE 1: sep={sep:.3e} pooled_IQR={pooled:.3e} separates={sep>=pooled}")
    if sep>=pooled:
        finish("probe_void_toothless"); return

    LA1=[p["L"] for p in RA1]; LA2=[p["L"] for p in RA2]; LH=[p["L"] for p in RH]
    fA1,fA2,fH=allf(LA1),allf(LA2),allf(LH)
    names=list(DISTRIB)+list(SCALARS)

    nbA1=nullband(RA1); nbA2=nullband(RA2)
    nb={nm:max(nbA1[nm],nbA2[nm]) for nm in names}
    art["gate2_nullband"]={k:dict(band=v,A1=nbA1[k],A2=nbA2[k]) for k,v in nb.items()}
    print("GATE 2 null bands:", {k:round(v,4) for k,v in nb.items()})

    g3={}
    for nm in names:
        rd= nm in ("level_histogram","transition","signed_occ","lattice_rank")
        if rd and (nz(RA1)<8 or nz(RA2)<8):
            g3[nm]=dict(status="insufficient_occupancy"); continue
        d=disc(nm,fA1[nm],fA2[nm])
        g3[nm]=dict(status="ok",discrepancy=d,band=nb[nm],separates=bool(d>nb[nm]))
    art["gate3"]=g3
    print("GATE 3:", {k:(v.get('separates') if v['status']=='ok' else v['status']) for k,v in g3.items()})
    surv=[nm for nm in names if g3[nm].get("separates")]

    g4={}
    if surv:
        def reg_resid(pts,Ls):
            old=getcontext().prec; getcontext().prec=max(AP,50)
            try:
                C=[(p["c1"],p["c2"],p["c3"]) for p in pts]; n=len(Ls)
                X=[[Decimal(1),Decimal(c[0]),Decimal(c[1]),Decimal(c[2]),
                    Decimal(c[0])*Decimal(c[1]),Decimal(c[0])*Decimal(c[2]),
                    Decimal(c[1])*Decimal(c[2])] for c in C]
                y=[Decimal(v) for v in Ls]; p=7
                A=[[sum(X[i][r]*X[i][s] for i in range(n)) for s in range(p)] for r in range(p)]
                b=[sum(X[i][r]*y[i] for i in range(n)) for r in range(p)]
                for col in range(p):
                    piv=max(range(col,p),key=lambda r:abs(A[r][col]))
                    if A[piv][col]==0: return [float(v) for v in Ls]
                    A[col],A[piv]=A[piv],A[col]; b[col],b[piv]=b[piv],b[col]
                    for r in range(p):
                        if r==col: continue
                        fct=A[r][col]/A[col][col]
                        for s in range(col,p): A[r][s]-=fct*A[col][s]
                        b[r]-=fct*b[col]
                beta=[b[r]/A[r][r] for r in range(p)]
                return [float(y[i]-sum(beta[r]*X[i][r] for r in range(p))) for i in range(n)]
            finally:
                getcontext().prec=old
        rq=lambda res:[int(Decimal(r).quantize(Decimal(1),rounding=ROUND_HALF_EVEN)) for r in res]
        frA1=allf(rq(reg_resid(RA1,LA1))); frA2=allf(rq(reg_resid(RA2,LA2)))
        for nm in surv:
            d=disc(nm,frA1[nm],frA2[nm])
            g4[nm]=dict(resid_discrepancy=d,band=nb[nm],survives=bool(d>nb[nm]))
    art["gate4"]=g4
    if surv: print("GATE 4:", {k:v['survives'] for k,v in g4.items()})
    g4s=[nm for nm in surv if g4.get(nm,{}).get("survives")]

    oos={}
    for nm in g4s:
        if nm in SCALARS:
            a,b,h=fA1[nm],fA2[nm],fH[nm]
            oos[nm]=dict(kind="scalar",between=bool(min(a,b)<=h<=max(a,b)))
        else:
            ks=set(fA1[nm])|set(fA2[nm])|set(fH[nm])
            a=[fA1[nm].get(k,0.0) for k in ks]; b=[fA2[nm].get(k,0.0) for k in ks]
            hh=[fH[nm].get(k,0.0) for k in ks]; v=[bi-ai for ai,bi in zip(a,b)]
            vv=sum(z*z for z in v)
            if vv<=nb[nm]**2: oos[nm]=dict(kind="vector",degenerate=True,between=False); continue
            t=sum((hi-ai)*vi for ai,hi,vi in zip(a,hh,v))/vv
            oos[nm]=dict(kind="vector",t=t,between=bool(0.0<=t<=1.0))
    art["gate5"]=oos
    final=[nm for nm in g4s if oos.get(nm,{}).get("between")]

    if final:
        art["supporting_functionals"]=final
        finish("precondition_supported")
    elif surv and not g4s:
        finish("precondition_refused_cancellation",
               interp=("Gate 4 conservative: this formulation could not "
               "be separated from cancellation geometry; NOT 'no fold "
               "geometry exists'. Stratum-distinct."))
    else:
        finish("precondition_refused_no_signal")

if __name__=="__main__":
    main()
