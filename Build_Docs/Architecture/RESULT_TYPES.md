# Result Types

Typed results are the primary outputs of Lloyd V4. A result may carry a scalar, vector, projective state, subspace, root state, branch fingerprint, refusal, protocol violation, or protocol uncertainty.

## Base Objects

`TypedResult`: The generic result envelope. It contains `value`, `space`, `status`, `validity`, `conditioning`, `provenance`, `protocol`, and optional refusal.

`StatusTensor`: A future status carrier for array-shaped or batch-shaped statuses. M0 uses scalar enums and retains this as an intended object.

`Validity`: Multi-field validity carrier with fields such as defined, finite, selectable, advanceable, and observable.

`Conditioning`: Conditioning carrier for well-conditioned, warning, ill-conditioned, singular, or unknown status.

`Provenance`: Structural provenance carrier for operation identity, expression path, precision, backend, device, measurement resolution, parent references, and trace ID.

`ProtocolCheck`: Runtime result of validating a typed result against a consumer protocol.

`ScalarizationResult`: Future typed result for explicit conversion from geometric state into scalar form. It may succeed or refuse.

`TypedRefusal`: First-class refusal object explaining why no honest value or scalarization exists.

## Value Semantics

`TypedResult.value` is not necessarily scalar. It may be a structured object or absent. Absence of value is valid when the honest output is a typed refusal, protocol violation, or uncertainty.

Scalarization is an operation. It is not an automatic consequence of a primitive returning successfully.
