# Projection Behavioral Deltas

- Old: `exact_quadratic_projection(root_state, branch: str)`.
  New: `exact_quadratic_projection(root_state_result, branch_selection_result)`.
  Principle: operation boundaries consume typed substrate observations.

- Old: invalid branch strings were handled inside projection.
  New: branch vocabulary is closed by `BranchSelection`; non-enum inputs fail before projection.
  Principle: Python type errors are programmer errors, not substrate states.

- Old: wrong-status root inputs raised `ProtocolViolationError`.
  New: wrong-status typed inputs return a typed projection refusal.
  Principle: valid typed values with refused statuses stay inside the substrate result channel.

- Old: `ProjectionResultValue.refusal` duplicated `TypedResult.refusal`.
  New: value-level refusal was removed.
  Principle: refusal has one canonical representation.

- Old: `ProjectionResultValue.flags: ProjectionFlags` denormalized status into booleans.
  New: flags were removed.
  Principle: `ProjectionStatus` is the source of truth for projection geometry state.

- Old: status mapping lived in `_SELECTABLE_PROJECTION_STATUS` and `_NONSELECTABLE_PROJECTION_STATUS`.
  New: runtime dispatch calls `apply_status_transition(QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE, ...)`.
  Principle: declared transition rules must be executable authority, not audit-only metadata.

- Old: solver called `exact_quadratic_projection(root_state, model.branch)`.
  New: solver calls `branch_selection(BranchSelection(model.branch))` and passes that typed input.
  Principle: existing solver model strings remain local to solver until solver is rebuilt, but projection receives typed input.

- Old: branch/refinery consumers serialized or compared projection flags.
  New: those consumers use projection status and selected/requested branch fields.
  Principle: downstream consumers cannot rely on removed projection denormalizations.
