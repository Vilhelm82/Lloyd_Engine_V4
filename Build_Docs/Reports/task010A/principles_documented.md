# Principles Documented

## Axioms

`Build_Docs/Architecture/AXIOMS.md` now records:

- Axiom 11: Epistemic Stance Only.
- Axiom 12: Self-Derivation.

These axioms make the engine's stance explicit: V4 records what its operators observe and derives higher-order structure from its own declared primitives instead of importing legacy semantics, external estimators, or pre-labeled outcome classes.

## Discovery Philosophy

`Build_Docs/Architecture/DISCOVERY_PHILOSOPHY.md` documents:

- Purpose.
- The agnostic workshop.
- The dark room.
- The engine as discovery instrument.
- No failures, only observations of varying refinement.
- Relationship to consumers.

The document frames V4 as a measurement workshop that emits structured observations. Consumers may classify, rank, or decide, but those are downstream acts.

## Layer Manifest

`Build_Docs/Architecture/LAYER_MANIFEST.md` and `Build_Docs/Architecture/layer_manifest.json` document the declared V4 layers:

- `core`
- `primitives`
- `projection`
- `metrology`
- `branch`
- `refinery`
- `history`
- `solver`

The manifest records each layer's parent dependencies and provided concepts, including public exports from the layer `__all__` declarations.

## Design Thesis

`Build_Docs/Architecture/DESIGN_THESIS.md` now includes `Design Commitments After the Reality-Check Review`, tying the new principles to:

- Axiom 11 and Axiom 12.
- The discovery philosophy.
- Operation ID as measurement in Task 010C'.
- The future `SYNTHESIS_PROTOCOL.md` from Task 010G.
- No-failures observation semantics.

## Task Template

`Build_Docs/Agent_tasks/TASK_TEMPLATE.md` now provides a reusable task format with required sections for future agent work, including explicit guardrails, TDD, verification, forbidden-source checks, deliverables, and completion criteria.
