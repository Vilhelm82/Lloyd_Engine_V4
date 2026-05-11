# V4 Design Update: Dual-Probe Architecture and V3/V1 Reference Hygiene

## Context

This document updates the design discussion around `ScalarAlphaJetBundle` and the negative-α stratum reachability question. The earlier recommendation (Option A: accept structural unreachability of `SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY` under the local-additive probe, document the limit, defer a sibling primitive) is correct as far as it goes. This update extends it with the substrate-correct architecture for the joint dual-probe object, clarifies what the "constraint curvature" framing actually means under V4 layer discipline, and records a general principle for referring to V3/V1 work without contaminating V4 substrate.

---

## Part 1: Re-framing the dual-probe question

### What the earlier analysis got right

- `g_local(h) = f(x₀ + h) − f(x₀)` can only observe α ≥ 0. The difference mechanically vanishes as h → 0, so there is no path to g_local → ∞.
- `g_singular(h) = f(x₀ + h)` is the natural construction for α < 0. No subtraction; the function value itself can blow up as h → 0⁺.
- These are structurally different measurements and must not be conflated into one primitive. Option C (extend `ScalarAlphaJetBundle` to handle both probe modes) is correctly rejected — it would make one primitive answer two different geometric questions.

### What the earlier analysis missed

The user's "dual probe / constraint curvature" proposal was treated as either (a) a metaphor that should be tightened, or (b) a stratified observation with dispatch labels (`LOCAL_AUTHORITATIVE` / `TRANSITION_ZONE` / `SINGULAR_AUTHORITATIVE`). Both of those readings are downstream of the actual point.

The proposal is asking a substrate-shaped question: instead of two probes with a dispatch rule between them, treat them as **two channels on a single joint observation** whose geometry varies continuously across the singularity, including through it. The dispatch-label framing collapses this back onto consumer-side dispatch logic. The "constraint curvature" framing reaches toward the *consumer-side geometric interpretation* of the joint observation. Both readings are real, but they live at different layers, and neither belongs in the L1 primitive that does the measurement.

---

## Part 2: The substrate-correct architecture

Under V4 layer discipline, the dual-probe object decomposes into three cleanly separated layers.

### L1: Sibling primitives

Two L1 primitives, not one primitive doing two jobs:

- **`ScalarAlphaJetBundle`** (already exists, Task 019). Builds `g_local`, consumes `AlphaProbe`. Sovereign in the regular region where f(x₀) is finite. The `SCALAR_JET_NEGATIVE_ALPHA_SINGULARITY` stratum remains in the status family as structurally unreachable from local-additive construction. Documented as such.

- **`SingularAlphaJetBundle`** (new sibling primitive, candidate next task). Builds `g_singular(h) = f(x₀ + h)` (no subtraction). Consumes `AlphaProbe` through the singular-direct construction. Sovereign in the singular region. Naturally reaches negative-α statuses. Emits a "no-singularity-here" status (or refuses) when f(x₀) is finite and `g_singular` returns weak/regular evidence.

These two primitives share the `AlphaProbe` consumer protocol but differ only in probe construction. That difference is the substrate fact. Everything else — the joint observation, the curvature interpretation, the solver dispatch — flows from it as downstream consumption.

### L1.5/L2: Typed joint composition

A composer consumes both arms' typed observations and emits a joint typed result. The joint object carries:

- both arms' lineage in provenance (transfer trace IDs, slope trace IDs, alpha-probe trace IDs from each arm)
- a joint status family indicating which arms produced observable evidence: `regular_arm_valid`, `singular_arm_valid`, `both_arms_valid`, `neither_arm_valid`
- the observed α values from each arm, kept as separate fields, never merged into one scalar
- conditioning evidence carried from both arms with arm-of-origin labels
- declared α models if present, applied independently per arm

This is the object the earlier discussion was reaching for under the name `ProjectiveLocalAlpha`. The name is fine. What matters is that the object **does not commit to dispatch labels at substrate**. The "transition zone" identified earlier is not a stratum label — it is the joint validity field showing both arms returning observable evidence at the same h-sweep range. Downstream consumers read what they need from the joint fields; they are not handed a pre-classified region label that pre-empts their dispatch logic.

This is also the cleanest place to surface what the user meant by "where one reading falls off is where the other picks back up." That hand-off is not a label — it is the trajectory of (regular_arm_validity, singular_arm_validity) across an h-sweep. The pattern is observable directly from the joint object's validity fields, without needing a stratification scheme.

### L3 (deferred, consumer-driven): Curvature on the implied joint surface

The dual-probe readings (u, v) = (g_local(h), g_singular(h)) at a sweep of h values trace a curve in (u, v)-space, or equivalently, imply a constraint relation F(h, u, v) = 0 over the swept domain. The curvature of that constraint surface — and any decomposition of it — is a **consumer-side observable**, not substrate. If a future solver or diagnostic wants curvature on the implied surface, it lives at L3 as a typed consumer of the L1.5 joint observation. It does not belong in any primitive.

This is where "constraint curvature" properly lives. The framing was not wrong in spirit; it was wrong in altitude. As a substrate commitment, it would pre-load named geometric content (curvature, Gaussian curvature, decompositions of it) which Axiom 11 (Epistemic Stance Only) excludes from substrate. As a downstream consumer observable, it is exactly the kind of corollary that `DISCOVERY_PHILOSOPHY.md` says should fall out of substrate purity rather than be designed into it.

---

## Part 3: Concrete implications for task sequencing

The ordering proposed in the targeted audit report (Task 018: `Directional AlphaProbe` → Task 019: `ScalarAlphaJetBundle` → Task 020+: solver) is unaffected by this update. The dual-probe architecture slots in cleanly as:

- **After Task 019 lands**, the natural next L1 task is `SingularAlphaJetBundle` as a sibling primitive. Implementation is similar in shape to Task 019: same `AlphaProbe` consumer protocol, different probe construction (`g_singular` instead of `g_local`), different reachable statuses. Most of the typed-result scaffolding, serialization, and provenance plumbing can be replicated with minor adaptation.
- **After both sibling primitives exist**, the L1.5/L2 joint-composition object can be specified. It is a composer, not a probe — it adds no new α measurement, only typed joint observation with both lineages preserved. This is a smaller task than either sibling primitive.
- **Any curvature/geometry work on the implied joint surface is deferred** to genuine consumer-pull. Not on the substrate path. If and when a solver or diagnostic needs it, it gets specified at L3 against the L1.5 joint object's contract.

This avoids two specific failure modes:

1. **Treating the joint object as terminal stratified labels.** Dispatch logic in disguise. Leaks Newton-shaped consumer assumptions back into substrate by encoding region-classification decisions at the wrong layer.
2. **Treating the implied-surface curvature as a substrate primitive.** Imports named mathematical content. Violates Axiom 11. Pre-empts the discovery process for what kind of curvature object (if any) is the right consumer-side abstraction.

---

## Part 4: V3/V1 reference hygiene

`V3_REFERENCE_LEDGER.md` is explicit: "V3 is reference-only. V4 must not import, call, adapt, or bridge to V3." The same applies to V1. The ledger correctly forbids runtime dependency, adapters, and cross-engine calls. It does not forbid — and should not be read as forbidding — looking at V1/V3 for **mechanical-property guidance** on design challenges that V4 will encounter independently.

The principle, stated as three rules:

**Rule 1: Reference is for mechanical property, not design justification.**
"V1/V3 already solved this" is a starting hypothesis, never a closing argument. Every V4 design must stand on its own derivation from V4's typed-substrate axioms. The V1/V3 lookup is a sanity check that the design problem is real and has been engaged before. It is not the source of V4's answer. If the V4 derivation requires V1/V3 as justification, the derivation is incomplete.

**Rule 2: Reference is for what to attempt, not what to copy.**
V1/V3 data structures, status enums, score functions, tolerance bands, `safe_mask` patterns, dict-based statuses, scalar route scores — none of these survive transit. They were correct under V1/V3 constraints (raw floats, dicts, no protocol substrate) and would be wrong under V4 constraints (typed results, status families, lineage-preserving composition). Only the measurement *intent* and the engagement with the design problem transfer.

**Rule 3: Reference is for which design problems are real, not which solutions are correct.**
V1/V3 are evidence that certain design challenges recur: cancellation dominance, branch-vs-arithmetic identifiability, multi-arm observation, candidate-step generation, curvature extraction, route-vs-residual conflict. Engaging that evidence is engineering discipline. Importing the solutions is substrate contamination.

### The smell to watch for

When a design discussion starts sounding like "V1/V3 did X, so V4 does X" — that is the bridge sneaking through the back door. Pull up. The V4 derivation has to stand on its own or it does not ship. The correct form of the same observation is: "V1/V3 engaged this design problem in form X; V4 needs to engage the same problem; here is the V4-native derivation from axioms, which produces form Y; here is why form Y differs from form X under V4 substrate constraints."

### Application to the current case

V3's branch fingerprint vector is **precedent** that asymptotic geometric evidence wants to be typed multi-component rather than scalar. That is mechanical property — informative, transferable as a design hint, validates the architectural shape of the joint dual-probe observation. The specific V3 fingerprint format, its dict-based status carrying, its score-weighted candidate selection — none of that transfers. The V4 joint observation derives from V4 axioms (typed result, status family, lineage-preserving composition) and is *informed* by the V3 evidence that multi-component typed observation is the correct shape for this class of measurement.

The same pattern applies to V1's transport/Halley work, V1's shape-operator and curvature-decomposition modules, V1's route-selection logic — all of them are mechanical-property references for design problems V4 will face at L3 (candidate generation, curvature extraction on consumer-side surfaces, route selection without scalar scoring). None of them are substrate content. The V4 versions, when they get built, will derive from V4 axioms and will look structurally different from their V1 counterparts even when solving the same design problem.

---

## Summary

- The dual-probe object is **three layers**, not one primitive: L1 sibling primitives (`ScalarAlphaJetBundle` + `SingularAlphaJetBundle`), L1.5/L2 typed joint composition, L3 (future, consumer-driven) curvature work on the implied joint surface.
- The earlier `ProjectiveLocalAlpha` instinct was correct in shape; the dispatch-label framing was the wrong implementation of the right intuition. The joint object should carry both arms' typed observations and lineages without pre-classifying regions for the consumer.
- "Constraint curvature" is a real object — at L3, as a consumer observable on the implied joint surface. Not at substrate. Axiom 11 forbids the substrate path; the L3 path is consistent with `DISCOVERY_PHILOSOPHY.md`.
- V3/V1 are mechanical-property references, never substrate content. The three rules above keep the boundary honest. The smell to watch for is "V1/V3 did X, so V4 does X" — that is the bridge sneaking in.
- No changes to the proposed Task 018 → 019 → 020+ ordering. `SingularAlphaJetBundle` and the joint composer are natural downstream additions to the same line, slotting in after Task 019 lands.
