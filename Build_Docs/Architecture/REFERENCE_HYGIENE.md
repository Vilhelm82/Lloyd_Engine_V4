### V3 referencial dicipline

V3_REFERENCE_LEDGER.md` is explicit: "V3 is reference-only. V4 must not import, call, adapt, or bridge to V3." The same applies to V1. The ledger correctly forbids runtime dependency, adapters, and cross-engine calls. It does not forbid — and should not be read as forbidding — looking at V1/V3 for **mechanical-property guidance** on design challenges that V4 will encounter independently.

The principle, stated as three rules:

**Rule 1: Reference is for mechanical property, not design justification.**
"V1/V3 already solved this" is a starting hypothesis, never a closing argument. Every V4 design must stand on its own derivation from V4's typed-substrate axioms. The V1/V3 lookup is a sanity check that the design problem is real and has been engaged before. It is not the source of V4's answer. If the V4 derivation requires V1/V3 as justification, the derivation is incomplete.

**Rule 2: Reference is for what to attempt, not what to copy.**
V1/V3 data structures, status enums, score functions, tolerance bands, `safe_mask` patterns, dict-based statuses, scalar route scores — none of these survive transit. They were correct under V1/V3 constraints (raw floats, dicts, no protocol substrate) and would be wrong under V4 constraints (typed results, status families, lineage-preserving composition). Only the measurement *intent* and the engagement with the design problem transfer.

**Rule 3: Reference is for which design problems are real, not which solutions are correct.**
V1/V3 are evidence that certain design challenges recur: cancellation dominance, branch-vs-arithmetic identifiability, multi-arm observation, candidate-step generation, curvature extraction, route-vs-residual conflict. Engaging that evidence is engineering discipline. Importing the solutions is substrate contamination.

### The smell to watch for

When a design discussion starts sounding like "V1/V3 did X, so V4 does X" — that is the bridge sneaking through the back door. Pull up. The V4 derivation has to stand on its own or it does not ship. The correct form of the same observation is: "V1/V3 engaged this design problem in form X; V4 needs to engage the same problem; here is the V4-native derivation from axioms, which produces form Y; here is why form Y differs from form X under V4 substrate constraints."
