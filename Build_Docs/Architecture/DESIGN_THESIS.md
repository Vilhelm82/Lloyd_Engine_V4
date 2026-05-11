# Design Thesis

Lloyd V4 is a typed, stratified geometry kernel where every computation is a partial map between typed geometric spaces with explicit domain, stratum, validity, conditioning, provenance, and protocol contract.

The core relation remains:

```text
D (+) S = P
```

The relation is algebraic, but the operands and outputs are typed geometric objects rather than unqualified scalars. `D`, `S`, and `P` may carry branch state, validity, conditioning, metrology status, and provenance. `K_G` is not the engine identity; it is one scalar projection that may or may not be permitted by the active stratum and protocol.

## Layer Architecture

Layer 0: Core typed substrate

Layer 0 defines statuses, validity, conditioning, provenance, typed results, protocol contracts, strict serialization, and the minimal status calculus. Task 000 builds only this scaffolding and the architecture documents.

Layer 1: Primitive geometric operations

Layer 1 will implement primitives such as ProjectiveRatio and StratifiedQuadraticRoots. These primitives emit typed results and do not collapse to scalars unless explicitly asked.

Layer 2: Metrology and transfer

Layer 2 will handle finite-precision observation, measurement resolution, path attribution, proxy calibration, branch fingerprints, and transfer observables.

Layer 3: Consumers

Layer 3 contains domain consumers. No consumer is part of Task 000, and no consumer should shape Layer 0 into a domain-specific API.

## Initial Primitive Order

```text
M1: ProjectiveRatio
M2: StratifiedQuadraticRoots
M3: ProjectionResultV4
M4: Metrology and branch fingerprint foundation
M5: Protocol-aware refinery
```

ProjectiveRatio comes first because division is the smallest operation where scalar numerics lies. A ratio may be finite, signed zero, infinite-directional, or indeterminate. That status must exist before later primitives compose ratios internally.

## Design Commitments After the Reality-Check Review

Axiom 11, Epistemic Stance Only, states that V4 commits to how observation works rather than importing named mathematical content as substrate. Axiom 12, Self-Derivation, states that every layer must derive from its declared parent layers and halt when it needs a concept the parents do not provide.

The agnostic-workshop framing in `DISCOVERY_PHILOSOPHY.md` makes this operational: V4 is built as a discovery instrument whose clean primitive behavior produces downstream consumers as corollaries, not as design targets.

The structural-measurement principle for provenance fields, including operation identity as something measured from the call tree rather than author-declared, will be implemented in Task 010C-prime.

The discovery-layer hierarchy and synthesis protocol are to be created in Task 010G as `SYNTHESIS_PROTOCOL.md`. Until then, synthesis remains a forward reference, not a substrate dependency.

The engine produces no failures, only structure-revealing observations of varying refinement. `DISCOVERY_PHILOSOPHY.md` elaborates how closed syntheses, typed gaps, multi-solution gaps, and axiomatic conflicts each prescribe different substrate work rather than acting as terminal failure modes.
