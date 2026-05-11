# Provenance Model

Provenance is structural. It records how a typed result was observed or produced, and it is part of the substrate rather than an optional debug trail.

## Required Fields

Operation ID: Stable identity for the operation that produced the result.

Expression path: The algebraic or computational path used to obtain the result.

Precision: Numeric precision or exactness mode used by the operation.

Backend: Runtime backend, such as Python, NumPy, CUDA, symbolic, or future kernels.

Device: Device where the operation ran.

Measurement resolution: Declared observation resolution or policy, when relevant.

Parent provenance references: Trace references to parent results, not full recursive copies by default.

Trace ID or hash: Stable identifier derived from the compact provenance payload.

Provenance status: Complete, compacted, lost, or unknown.

## Avoiding Combinatorial Explosion

Naively copying full parent provenance into every child result grows without bound. V4 uses parent references and trace IDs as the default propagation mechanism.

When combining results, a child should retain:

- its own operation ID and expression path
- compact parent trace references
- a provenance status indicating complete or compacted lineage
- equivalence-class tags when multiple paths are known to be interchangeable under the active protocol

If provenance is intentionally compacted, the compaction is explicit. If provenance is unavailable, the result carries `lost` provenance status. Lost provenance is a typed status, not silent omission.

## Provenance Equivalence Classes

Different expression paths may be equivalent for a given protocol. V4 may later represent equivalence classes so that many arithmetic paths can compact into one class reference. The equivalence criterion must be protocol-defined; it cannot be guessed from identical scalar values.

## Precision and Path Attribution

Provenance supports later precision/path attribution:

```text
C_{p,k} = a + u_p b_k
```

Task 000 does not implement this estimator. It only preserves the fields needed for later attribution: precision, expression path, backend, device, measurement resolution, and trace references.
