# Task 000 Design Decisions

## Static Versus Runtime Protocol Checking

Decision: M0 uses strict runtime protocol validation while shaping protocol objects for later static checkability.

Reason: Python can enforce accepted status sets, required fields, and scalarization restrictions immediately. Static checking should be added after the first primitives reveal the stable contract surface.

## Status Calculus Minimum Viable Rules

Decision: M0 status composition is conservative. Empty joins, mixed joins, and unhandled statuses fail explicitly.

Reason: The early substrate must prevent ad hoc scalar escape paths. Named composition rules can be added when a primitive proves the rule is real.

## Provenance Propagation Strategy

Decision: Provenance carries operation ID, expression path, precision, backend, device, measurement resolution, parent trace references, trace ID, and status. Parent references are compact trace IDs by default.

Reason: Full recursive provenance would grow combinatorially. Silent provenance loss would make later precision/path attribution impossible.

## No V3 Runtime Dependency

Decision: V3 is static reference evidence only. V4 source must not import, call, bridge, or compare against V3 at runtime.

Reason: V4 is the typed substrate implementation. Runtime V3 dependence would turn reference evidence into architecture.

## No Legacy Adapters

Decision: Task 000 creates no adapters, downgrade shims, compatibility wrappers, or legacy modes.

Reason: Every V4 consumer should be rebuilt against explicit typed protocols. Compatibility layers would pull old scalar assumptions into the substrate.
