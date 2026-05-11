# Projection Rebuild Design

## `branch_selection`

`branch_selection(branch: BranchSelection) -> BranchSelectionResult` is a projection-layer composite over the primitive `typed_value`.

- Input type: `BranchSelection` enum only.
- Wrong Python type: raises `ProtocolViolationError`.
- Output value: `BranchSelectionValue(branch=branch)`.
- Output status: inherited from `typed_value`; for valid enum inputs this is `ValueStatus.VALUE_OBSERVED`.
- Validity and conditioning: inherited from `typed_value`.
- Provenance: parent is the inner `typed_value` trace id.
- Operation class: composite, not calibrated primitive.

The enum closes the branch vocabulary at the operation boundary without adding a new substrate primitive.

## `exact_quadratic_projection`

`exact_quadratic_projection(root_state_result, branch_selection_result) -> ProjectionResultV4` consumes two typed inputs:

- `root_state_result`: a `TypedResult` whose value is `StratifiedQuadraticRootValue`.
- `branch_selection_result`: a `TypedResult` whose value is `BranchSelectionValue`.

Wrong Python shape raises `ProtocolViolationError`. Right Python shape with wrong status returns a `ProjectionStatus.PROJECTION_SELECTION_REFUSED` typed result with canonical `TypedResult.refusal`.

The runtime status dispatch now goes through:

```python
apply_status_transition(
    QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE,
    root_state_result.status,
    branch=branch,
)
```

The transition callable maps the root status and typed branch selection to the projection status. Selectable statuses call `select_quadratic_root`; nonselectable statuses return the appropriate projection status with no selected root.

## Result contract

`ProjectionResultValue` contains only projection facts:

- source status
- requested branch
- selected branch
- selected root value
- selected root trace id
- source trace id
- source operation id
- projection status

It does not contain a duplicate refusal dictionary and does not contain `ProjectionFlags`. The single refusal authority is `TypedResult.refusal`; status is the single source of truth for whether roots exist, projection is defined, and advancement is possible.

## Behavioral justification

The raw branch string was an untyped substrate input. Replacing it with a local enum plus typed composite makes branch choice auditable without promoting it to a new primitive.

Wrong-status inputs are substrate observations, so they return typed refusals. Wrong Python types are programmer errors, so exceptions remain appropriate.

The transition rule is active machinery now. That removes duplicate status maps and gives the audit-visible rule the same authority the runtime uses.

Projection flags were denormalized status facts. Removing them prevents drift and pushes any future consumer-specific derived views into the consumer that needs them.
