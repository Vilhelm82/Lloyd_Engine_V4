# Lloyd V4 Axioms

Lloyd V4 treats numerical computation as navigation through stratified geometric spaces under finite-precision observation.

## 1. Geometry precedes scalarization

Statement: A scalar is a valid projection of a typed geometric state only when the domain, stratum, validity, conditioning, provenance, and protocol allow scalarization.

Rationale: The geometric object is the truth carrier. A scalar is one possible representation of that object, not the default output.

V4 forbids: Default scalar collapse, implicit float return from every primitive, and scalar success when the status fields say otherwise.

V4 must represent instead: Typed geometric spaces, non-scalar values, scalarization requests, scalarization results, and typed scalarization refusal.

## 2. Degeneracy is a stratum, not a failure

Statement: Degenerate regions are part of the space and must be represented as named strata.

Rationale: Zero denominators, repeated roots, tangent contact, and underdetermined identities are meaningful geometric cases.

V4 forbids: Treating degeneracy as exception-only behavior, boolean failure, or an implementation accident.

V4 must represent instead: Stratum status, validity fields, and protocol declarations for consumers that can or cannot handle the stratum.

## 3. Hidden guard rails are forbidden

Statement: Undeclared rescue operations are invalid substrate behavior.

Rationale: Secret numerical rescue changes truth status without exposing the measurement or policy decision.

V4 forbids: Secret tolerances, denominator floors, discriminant laundering, value clamps, and unreported fallback paths.

V4 must represent instead: Declared measurement resolution, explicit policy parameters, typed status transitions, and provenance for the operation path.

## 4. Validity is multi-field, never one universal boolean

Statement: Defined, finite, selectable, advanceable, observable, and policy-accepted are distinct properties.

Rationale: A point may be defined but not scalarizable, finite but not advanceable, or observable but not selectable.

V4 forbids: Universal safe flags and one-bit validity for geometric state.

V4 must represent instead: A structured validity object with optional fields whose absence is itself meaningful.

## 5. Numerical representation is a path, not the object

Statement: Precision, backend, device, and expression path describe how a state was observed, not what the object is.

Rationale: Algebraically equivalent expressions can expose different finite-precision behavior.

V4 forbids: Dropping arithmetic path information as irrelevant implementation detail.

V4 must represent instead: Operation identity, expression path, precision, backend, device, and parent provenance.

## 6. Zero must be measured or proven, not assumed

Statement: Zero is a typed metrology conclusion, not a default interpretation of small magnitude.

Rationale: Blindness below a measurement limit is not the same as mathematical identity.

V4 forbids: Equating small, unseen, or rounded values with true zero.

V4 must represent instead: `identity_zero`, `below_limit_of_detection`, `indeterminate`, and `detected_nonzero`.

## 7. Proxy observables require calibration

Statement: A proxy observable is not equivalent to a direct transfer observable until calibrated.

Rationale: A proxy may carry its own response curve and finite-window bias.

V4 forbids: Treating proxy signals as direct geometry without calibration evidence.

V4 must represent instead: Proxy calibration status, calibration factors such as `K_q`, and explicit uncalibrated proxy status.

## 8. Typed results compose by protocols

Statement: A producer emits typed statuses and a consumer declares which statuses it accepts.

Rationale: Composition is reliable only when status handling is explicit and exhaustive.

V4 forbids: Passing unhandled strata downstream as ordinary numeric values.

V4 must represent instead: Producer protocols, consumer protocols, accepted status sets, required fields, and protocol check results.

## 9. Type-system failures are real failure modes

Statement: A bad or incomplete protocol declaration is a substrate failure, not a harmless annotation problem.

Rationale: A false type sticker is worse than an obvious untyped failure because it can license invalid composition.

V4 forbids: Treating protocol mismatch as a warning that can be ignored by default.

V4 must represent instead: Protocol violations, protocol uncertainty, failed exhaustive checks, and repairable contract evidence.

## 10. V3 is reference evidence only, never a runtime authority

Statement: Lloyd V4 must not import, call, adapt, or bridge to Lloyd V3.

Rationale: V4 is a clean implementation of typed geometric relations, not a compatibility shell.

V4 forbids: Runtime V3 calls, cross-engine adapters, live V3 comparison dependencies, and legacy modes.

V4 must represent instead: Static reference evidence, copied fixtures when needed, and deliberate divergence when typed results are more honest.

## 11. Epistemic Stance Only

Statement: V4 commits at the level of how observation works, not at the level of what is observed. Imported constants, named theorems, and off-the-shelf formalisms are domain articulations, not substrate.

Rationale: Each formalism is one specific articulation of underlying mathematical territory. Importing it brings its vocabulary, its operations, and its tacit claim to be the natural articulation. The room behind that articulation closes the moment the formalism is brought in as substrate. The Gamma Function is one extension of the factorial to the complex plane; Hadamard's gamma is another. Bohr-Mollerup uniqueness picks one. Building Gamma into the substrate forecloses on every other extension that V4 might independently observe to fit a given territory better.

V4 forbids: Imports of named mathematical content (`math`, `cmath`, `numpy.special`, `scipy.constants`, `scipy.special`, `sympy`, `mpmath`); hardcoded mathematical constants (`pi`, `tau`, `e`, `gamma`, `zeta`, `golden_ratio`); use of named theorems, named functions, or named equations as substrate building blocks.

V4 must represent instead: Constants and named objects as observables, values the engine measures or synthesises through its own primitives, with full provenance lineage to substrate operations. Existing maths may serve as navigation targets through the synthesis protocol, never as substrate content.

## 12. Self-Derivation

Statement: Every layer derives from its parent layers. A higher layer that requires a concept absent from its parents must halt; the parent layer is extended honestly, then the higher layer rebuilds.

Rationale: Without enforced layered derivation, higher layers can mint novel concepts ad hoc, and the substrate becomes a collection of jumps and forced rearrangements rather than a coherent structure where each level is built from below. The discipline of speaking the same language across layers requires that every concept used at any layer trace back to a primitive through registered transitions.

V4 forbids: Concepts minted at consumer layers that do not exist in any parent layer; transition rules that compose primitives without registered lineage; cross-layer references that bypass declared parent relationships.

V4 must represent instead: Layer manifests declaring provided concepts and parent layers; structural lineage from primitives to consumers via registered transition rules; descend-extend-return procedure when a higher layer's needs exceed parent provisions.
