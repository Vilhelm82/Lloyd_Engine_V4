# Codex Task 008: History-Aware Status Traces

## Repository

Work in:

```text
/mnt/fast/Lloyd_Engine_V4
```

This is Lloyd Engine V4 clean-room work. V3 is reference evidence only. Do not import, call, bridge, compare against, adapt, or depend on V3 at runtime. Do not add legacy adapters, compatibility shims, downgrade modes, or cross-engine calls.

## Current verified baseline

Task 000 is complete. The M0 substrate exists: statuses, validity, conditioning, provenance, typed results/refusals, protocol validation, conservative status calculus, strict serialization, core errors, and architecture docs.

Task 001 is complete. `ProjectiveRatio(n, d)` exists as the first primitive. It preserves raw projective coordinates `[n:d]`, classifies exact projective strata without dividing by `d`, and scalarizes only through an explicit protocol that may refuse.

Task 002 is complete. `StratifiedQuadraticRoots` exists. `stratified_quadratic_roots(a, b, c)` returns a typed root-state result with raw coefficients, discriminant evidence, branch-labeled projective root coordinates, validity, conditioning, and provenance. `select_quadratic_root(result, branch)` is explicit and protocol-validated.

Task 003 is complete. `ProjectionResultV4` and the exact quadratic projection protocol exist. `exact_quadratic_projection(root_state_result, branch)` consumes validated Task 002 root-state results, calls Task 002 selection for selectable branches, and emits structured projection evidence with separate `root_exists`, `projection_defined`, `selected_root_valid`, and `advance_valid` flags.

Task 004 is complete. The Layer 2 metrology foundation exists under `src/lloyd_v4/metrology`. It implements declared and estimated `b_k` noise-floor evidence, limit-of-detection classification with explicit `identity_evidence`, pointwise `K_q` proxy calibration through ProjectiveRatio plus explicit scalarization, `proxy_uncalibrated(...)`, and `require_valid_proxy_calibration(...)`.

Task 005 is complete. `TypedResult` is generic over value type and status enum family. Protocols infer or declare status families and reject wrong-family typed results explicitly. Named transition-rule machinery exists with canonical rules for ProjectiveRatio scalarization, quadratic root selection, quadratic projection, limit-of-detection classification, valid `K_q` calibration, and later layer composition.

Task 006 is complete. The branch package exists under `src/lloyd_v4/branch`. It implements `BranchFingerprintStatus`, slope-flow comparison with ProjectiveRatio-backed segment slopes, declared model residual comparison, `K_q` slope-stability checks using Task 004 calibration evidence, and BranchFingerprint composition through named transition rules.

Task 007 is complete. The refinery package exists under `src/lloyd_v4/refinery`. It implements typed result snapshots, explicit slag vectors, scenario and candidate rewrite decisions, `RefineryStatus`, refinery protocols, named status-preservation transition rules, accepted-rewrite enforcement, and serialization. The refinery consumes supplied typed observations only. It does not parse, simplify, generate, or classify equations.

Task 007 verification baseline:

```text
Full suite: 156 passed
Required source audits: no matches
```

## Task 008 goal

Implement the first history-aware status trace substrate:

```text
History-aware status traces
```

Task 008 should record how V4 typed-result statuses evolve across an explicitly supplied sequence of observations. It must preserve protocol identity, status family, status value, validity, conditioning, provenance trace references, and optional geometry signatures. It must not become a domain consumer, flow integrator, time-series forecaster, database, logger, dashboard, or symbolic engine.

Task 008 should implement:

```text
1. a HistoryStatus family;
2. compact status-event evidence for existing TypedResult objects;
3. pairwise transition evidence between adjacent status events;
4. ordered trace construction over a single stream and observation key;
5. stable-versus-transitioned trace summaries;
6. typed refusals for consumers that require stable traces;
7. named transition rules for history events, trace construction, and stable-trace requirements;
8. serialization and reports for all new evidence.
```

History traces observe status evolution. They do not judge whether a status transition is good, bad, better, worse, safe, unsafe, domain-relevant, or consumer-acceptable unless an explicit history protocol says so.

## Design principles

- Geometry precedes scalarization.
- Degeneracy is a stratum, not failure.
- Typed results compose by protocols.
- Mixed-status composition must use named transition rules.
- History records typed evidence. It does not invent semantic ordering between unrelated statuses.
- A status change is evidence, not automatically a regression.
- A stable trace is explicit history evidence, not a proof that future observations will remain stable.
- History order is caller-supplied by integer sequence index. Do not use wall-clock time, current time, background jobs, async work, or external clocks.
- Optional geometry signatures are caller-supplied evidence. The history layer must not introspect arbitrary value objects and pretend that is universal geometry.
- Existing Task 001 through Task 007 behavior and serialization must remain unchanged.
- No hidden epsilons, tolerance gates, smoothing windows, hysteresis bands, denominator floors, clamps, safe division, rescue constants, log offsets, confidence scores, weighted scores, fallback branches, symbolic simplification, persistent stores, or compatibility modes.
- Existing Task 000 `measurement_resolution` provenance metadata remains legitimate substrate metadata. Do not rename or hide it.

## Required package boundary

Create a new package for history work.

Recommended files:

```text
src/lloyd_v4/history/__init__.py
src/lloyd_v4/history/status_trace.py
```

If the repository has a clearly better naming convention, use it, but do not place history implementation inside primitives, projection, metrology, branch, refinery, or core.

Expected core modification:

```text
src/lloyd_v4/core/status.py
```

Only add the new History status family there. Do not add history algorithms to core.

Task 008 may import earlier layers in this direction:

```text
history -> core
history -> primitives, if needed only for public status/result alias recognition
history -> projection, if needed only for public status/result alias recognition
history -> metrology, if needed only for public status/result alias recognition
history -> branch, if needed only for public status/result alias recognition
history -> refinery, if needed only for public status/result alias recognition
```

Earlier layers must not import history:

```text
core must not import history implementation modules
primitives must not import history
projection must not import history
metrology must not import history
branch must not import history
refinery must not import history
```

Task 008 may consume public APIs, result aliases, protocols, and named transition rules from earlier tasks. It must not patch earlier task behavior.

## Required status family

Add a new status enum family. Recommended name:

```python
HistoryStatus
```

Required initial statuses:

```text
history_event_recorded
history_transition_stable
history_transition_protocol_changed
history_transition_status_family_changed
history_transition_status_changed
history_transition_validity_changed
history_transition_geometry_changed
history_transition_incomparable
history_trace_empty
history_trace_singleton
history_trace_stable
history_trace_transitioned
history_trace_incomplete
history_trace_unordered
```

These names may be adjusted only if the final report includes a status table proving the same semantic coverage.

### Status meanings

`history_event_recorded`

A compact status event was recorded from an existing V4 `TypedResult`. The event preserves source protocol identity, status family, status value, validity, conditioning, source trace ID, operation identity, expression path, and optional caller-provided geometry signature.

`history_transition_stable`

Two adjacent events are comparable and have the same source protocol identity, status family, status value, validity snapshot, and geometry signature when a geometry signature is provided.

`history_transition_protocol_changed`

Two adjacent events are comparable by stream and observation key, but their source protocol identities differ. This status takes precedence over lower-level status/validity/geometry differences. The value must still preserve all changed fields.

`history_transition_status_family_changed`

Two adjacent events are comparable by stream and observation key and source protocol identity, but their status enum families differ.

`history_transition_status_changed`

Two adjacent events are comparable by stream and observation key, source protocol identity, and status family, but their status values differ.

`history_transition_validity_changed`

Two adjacent events have the same protocol, status family, and status value, but at least one validity field differs: `defined`, `finite`, `selectable`, `advanceable`, or `observable`.

`history_transition_geometry_changed`

Two adjacent events have the same protocol, status family, status value, and validity, but their geometry signatures differ. If both geometry signatures are absent, do not emit this status. If exactly one signature is present, emit this status and record the missing signature as evidence.

`history_transition_incomparable`

Two supplied events cannot honestly be compared as adjacent observations. Examples: different stream IDs, different observation keys, missing required event fields, wrong input status, or non-increasing sequence index in a pairwise comparison.

`history_trace_empty`

A trace was requested from an empty event list. Preserve observable empty evidence. Do not raise unless the API receives invalid non-event objects.

`history_trace_singleton`

A trace contains exactly one valid event. It is valid history evidence, but it has no pairwise transition evidence.

`history_trace_stable`

A trace contains two or more valid, ordered, comparable events and every adjacent pair emits `history_transition_stable`.

`history_trace_transitioned`

A trace contains two or more valid, ordered, comparable events and at least one adjacent pair emits a non-stable transition status. This includes protocol, family, status, validity, or geometry changes. The summary value must preserve per-pair transition evidence.

`history_trace_incomplete`

Trace construction lacks required evidence. Examples: one or more inputs are not `history_event_recorded`, required event metadata is missing, stream IDs are mixed, observation keys are mixed, or a pairwise transition is incomparable for reasons other than ordering.

`history_trace_unordered`

Trace construction received valid events from one stream and observation key, but their sequence indices are not strictly increasing. Do not silently sort or repair the order.

## Status precedence

Pairwise transition classification must use this precedence:

```text
incomparable
protocol_changed
status_family_changed
status_changed
validity_changed
geometry_changed
stable
```

If multiple fields change, emit the highest-precedence status and record all changed fields in the transition value.

Trace summary classification must use this precedence:

```text
empty
incomplete
singleton
unordered
stable
transitioned
```

The summary value must preserve enough evidence to explain the final trace status.

## Validity mapping

Use the M0 validity fields consistently.

Recommended mapping:

```text
history_event_recorded:                  defined, finite, selectable, not advanceable, observable
history_transition_stable:               defined, finite, selectable, not advanceable, observable
history_transition_protocol_changed:     defined, finite, selectable, not advanceable, observable
history_transition_status_family_changed:defined, finite, selectable, not advanceable, observable
history_transition_status_changed:       defined, finite, selectable, not advanceable, observable
history_transition_validity_changed:     defined, finite, selectable, not advanceable, observable
history_transition_geometry_changed:     defined, finite, selectable, not advanceable, observable
history_transition_incomparable:         not defined, not finite, not selectable, not advanceable, observable
history_trace_empty:                     not defined, not finite, not selectable, not advanceable, observable
history_trace_singleton:                 defined, finite, not selectable, not advanceable, observable
history_trace_stable:                    defined, finite, selectable, not advanceable, observable
history_trace_transitioned:              defined, finite, selectable, not advanceable, observable
history_trace_incomplete:                not defined, not finite, not selectable, not advanceable, observable
history_trace_unordered:                 not defined, not finite, not selectable, not advanceable, observable
```

Task 008 must not set `advanceable=True`. History evidence is not projection advancement.

## Required value objects

Use frozen dataclasses unless the existing codebase uses a different immutable pattern.

Recommended objects:

```python
@dataclass(frozen=True)
class StatusEventValue:
    stream_id: str
    observation_key: str
    step_index: int
    scenario_id: str | None
    source_protocol: str
    source_status_family: str
    source_status: str
    source_validity: dict[str, bool]
    source_conditioning: str
    source_trace_id: str
    source_operation_id: str | None
    source_expression_path: str | None
    source_precision: str | None
    source_backend: str | None
    source_device: str | None
    geometry_signature: str | None

@dataclass(frozen=True)
class StatusTransitionValue:
    stream_id: str
    observation_key: str
    previous_step_index: int | None
    next_step_index: int | None
    previous_event_trace_id: str | None
    next_event_trace_id: str | None
    previous_source_trace_id: str | None
    next_source_trace_id: str | None
    changed_fields: tuple[str, ...]
    comparison_reason: str

@dataclass(frozen=True)
class StatusTraceValue:
    stream_id: str | None
    observation_key: str | None
    event_count: int
    first_step_index: int | None
    last_step_index: int | None
    event_trace_ids: tuple[str, ...]
    source_trace_ids: tuple[str, ...]
    transition_trace_ids: tuple[str, ...]
    transition_status_counts: dict[str, int]
    stable: bool
    transition_count: int
    notes: tuple[str, ...]
```

These value shapes may be adjusted if the final report explains why, but the implemented shapes must preserve equivalent evidence.

Do not store full recursive parent results in history values. Use compact trace IDs and compact snapshots. Task 000 chose compact parent trace references to avoid combinatorial provenance growth.

## Required API

Recommended public functions:

```python
record_status_event(
    result: TypedResult[Any, Any],
    *,
    stream_id: str,
    observation_key: str,
    step_index: int,
    scenario_id: str | None = None,
    geometry_signature: str | None = None,
) -> HistoryResult
```

Records one V4 typed result as a status event.

Requirements:

```text
- `result` must be a TypedResult.
- `stream_id` and `observation_key` must be nonempty strings.
- `step_index` must be an integer and must not be negative.
- `scenario_id`, when provided, must be a nonempty string.
- `geometry_signature`, when provided, must be a nonempty string.
- The returned result status is `history_event_recorded`.
- The returned provenance parent trace is the source result trace ID.
```

```python
compare_status_events(
    previous_event: HistoryResult,
    next_event: HistoryResult,
) -> HistoryResult
```

Compares two recorded events and returns pairwise transition evidence.

Requirements:

```text
- Inputs must be History typed results.
- Inputs must have status `history_event_recorded`; otherwise return or raise through the existing protocol/refusal path, consistent with the rest of V4.
- Events with different stream IDs or observation keys emit `history_transition_incomparable`.
- Events with non-increasing step indices emit `history_transition_incomparable`.
- Comparable pairs use the precedence order defined above.
- The returned provenance parents are the two event result trace IDs.
```

```python
build_status_trace(
    events: Sequence[HistoryResult],
) -> HistoryResult
```

Builds an ordered trace over a single stream and observation key.

Requirements:

```text
- Empty input emits `history_trace_empty`.
- One valid event emits `history_trace_singleton`.
- Mixed stream IDs or observation keys emit `history_trace_incomplete`.
- Non-event or wrong-status inputs emit `history_trace_incomplete`.
- Valid events with non-strictly-increasing step indices emit `history_trace_unordered`.
- Do not silently sort, deduplicate, interpolate, or repair events.
- For two or more valid ordered events, compare adjacent pairs using `compare_status_events(...)`.
- If all pairwise transitions are stable, emit `history_trace_stable`.
- If at least one pairwise transition is non-stable and no incomplete/unordered condition applies, emit `history_trace_transitioned`.
- The returned provenance parents are the event trace IDs.
```

```python
require_stable_status_trace(
    trace_result: HistoryResult,
) -> HistoryResult
```

Consumes a trace result and accepts only `history_trace_stable`.

Requirements:

```text
- Validate against a stable-trace consumer protocol.
- Accept only `history_trace_stable`.
- Refuse `history_trace_empty`, `history_trace_singleton`, `history_trace_transitioned`, `history_trace_incomplete`, and `history_trace_unordered` through typed refusal.
- Preserve the original trace status and refusal reason.
- Do not convert singleton traces into stable traces.
```

If naming differs, preserve this semantic surface and document the final API in the Task 008 summary.

## Result aliases and protocols

Expose a concrete result alias, following Task 005 style:

```python
HistoryResult = TypedResult[StatusEventValue | StatusTransitionValue | StatusTraceValue, HistoryStatus]
```

If Python typing ergonomics require narrower aliases, expose them too:

```python
HistoryEventResult
HistoryTransitionResult
HistoryTraceResult
```

Define producer and consumer protocols, recommended names:

```python
HISTORY_EVENT_PROTOCOL
HISTORY_TRANSITION_PROTOCOL
HISTORY_TRACE_PROTOCOL
STABLE_HISTORY_TRACE_PROTOCOL
```

Protocols must declare or infer the `HistoryStatus` family. Wrong-family results must fail as wrong-family protocol violations, not ordinary accepted-set misses.

## Named transition rules

Use the Task 005 transition-rule machinery. Do not invent local ad hoc joins.

Add canonical rules, recommended names:

```text
history.record_event
history.event_pair.compare
history.events.to_trace
history.trace.require_stable
```

Required semantics:

`history.record_event`

```text
input protocol: any valid V4 TypedResult producer protocol
output protocol: history_event
input status family: any known V4 status family
output status family: HistoryStatus
mapped status: any valid source status -> history_event_recorded
context keys: stream_id, observation_key, step_index
```

`history.event_pair.compare`

```text
input protocol: history_event
output protocol: history_transition
input status family: HistoryStatus
output status family: HistoryStatus
accepted input status: history_event_recorded
mapped statuses: contextual pair comparison statuses
context keys: previous_event, next_event
```

`history.events.to_trace`

```text
input protocol: history_event
output protocol: history_trace
input status family: HistoryStatus
output status family: HistoryStatus
accepted input status: history_event_recorded
mapped statuses: contextual trace summary statuses
context keys: events
```

`history.trace.require_stable`

```text
input protocol: history_trace
output protocol: stable_history_trace
input status family: HistoryStatus
output status family: none
accepted statuses: history_trace_stable
refused statuses: history_trace_empty, history_trace_singleton, history_trace_transitioned, history_trace_incomplete, history_trace_unordered
context keys: none
```

Generic mixed-family joins must remain conservative. History observes mixed-family changes only through named history transition evidence.

## Serialization requirements

Task 008 results must serialize through existing strict serialization.

Serialization must preserve:

```text
- history status
- protocol identity
- stream_id
- observation_key
- step_index
- scenario_id when present
- source protocol
- source status family
- source status
- source validity snapshot
- source conditioning
- source trace ID
- source operation identity
- source expression path
- source precision/backend/device where available
- geometry signature when present
- transition changed_fields
- transition status counts
- provenance parent trace references
- refusal evidence for stable-trace requirements
```

Serialization must not include non-serializable enum objects, datetimes, live result objects, callables, file handles, database handles, or recursive full-parent result trees.

## Red tests first

Add failing tests before implementation.

Recommended test files:

```text
tests/test_task008_history_event_recording.py
tests/test_task008_status_transition_comparison.py
tests/test_task008_status_trace_building.py
tests/test_task008_history_protocols.py
tests/test_task008_transition_rules.py
tests/test_task008_serialization.py
tests/test_task008_source_purity.py
```

The first red run should fail because `lloyd_v4.history` and `HistoryStatus` do not exist yet.

## Required tests

At minimum, test the following.

### Event recording

```text
- record a ProjectiveRatio result event
- record a StratifiedQuadraticRoots result event
- record a ProjectionResultV4 result event
- record a Metrology result event
- record a BranchFingerprint result event
- record a Refinery decision result event
- preserve source protocol, status family, status, validity, conditioning, and source trace ID
- preserve optional geometry_signature
- reject invalid stream_id, observation_key, step_index, scenario_id, and geometry_signature inputs
```

### Pairwise transition comparison

```text
- same protocol/status family/status/validity/signature -> history_transition_stable
- protocol changed -> history_transition_protocol_changed
- status family changed -> history_transition_status_family_changed
- status value changed -> history_transition_status_changed
- validity changed -> history_transition_validity_changed
- geometry signature changed -> history_transition_geometry_changed
- one signature missing while the other is present -> history_transition_geometry_changed
- different stream IDs -> history_transition_incomparable
- different observation keys -> history_transition_incomparable
- non-increasing step index -> history_transition_incomparable
- changed_fields records all changed fields, not only the highest-precedence one
```

### Trace building

```text
- empty input -> history_trace_empty
- one valid event -> history_trace_singleton
- two or more stable events -> history_trace_stable
- any non-stable comparable transition -> history_trace_transitioned
- mixed stream IDs -> history_trace_incomplete
- mixed observation keys -> history_trace_incomplete
- wrong-status history inputs -> history_trace_incomplete
- non-history inputs -> history_trace_incomplete or protocol violation through the existing path
- duplicate step indices -> history_trace_unordered
- decreasing step indices -> history_trace_unordered
- build_status_trace does not silently sort events
- trace summary preserves transition_status_counts
```

### Stable trace protocol

```text
- require_stable_status_trace accepts history_trace_stable
- require_stable_status_trace refuses history_trace_empty
- require_stable_status_trace refuses history_trace_singleton
- require_stable_status_trace refuses history_trace_transitioned
- require_stable_status_trace refuses history_trace_incomplete
- require_stable_status_trace refuses history_trace_unordered
- refusal preserves original trace status and reason
- wrong-family typed results fail as wrong-family protocol violations
```

### Transition rules

```text
- exported history transition rules exist
- rules declare HistoryStatus as output family where appropriate
- stable-trace requirement rule accepts exactly history_trace_stable
- all HistoryStatus values are either mapped, accepted, or explicitly refused by the relevant rule
- generic mixed-family joins remain conservative
```

### Serialization

```text
- event serialization preserves source status family/status/protocol/validity/provenance
- transition serialization preserves changed fields and event trace IDs
- trace serialization preserves event count, transition counts, event trace IDs, and source trace IDs
- stable-trace refusal serializes without non-finite sentinels or recursive object trees
```

## Source purity and dependency audits

Keep existing audits green, adjusting only where Task 008 legitimately introduces history terms in the new history layer and `HistoryStatus` in `core/status.py`.

Required audits:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
```

```bash
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance|confidence_score|weighted_score|smoothing|hysteresis|interpolate|extrapolate" src/lloyd_v4 -n
```

```bash
rg "lloyd_v4\.history|from lloyd_v4\.history|import .*history" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery -n
```

```bash
rg "history_trace|status_trace|history_event|status_history" src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery -n
```

```bash
rg "lloyd_v4\.refinery|from lloyd_v4\.refinery|import .*refinery" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch -n
```

```bash
rg "lloyd_v4\.branch|from lloyd_v4\.branch|import .*branch" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology -n
```

```bash
rg "lloyd_v4\.metrology|from lloyd_v4\.metrology|import .*metrology" src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

```bash
rg "lloyd_v4\.projection|from lloyd_v4\.projection|import .*projection" src/lloyd_v4/primitives src/lloyd_v4/metrology -n
```

```bash
rg "finite_eta|domain_consumer|domain_classifier|bearing|aerospace|betting|scanner|flow_integrator|symbolic_simplifier|cas|parser" src/lloyd_v4 -n
```

```bash
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

History terms may appear in:

```text
src/lloyd_v4/history
src/lloyd_v4/core/status.py, only for HistoryStatus enum definitions
Build_Docs/Reports/task008
Task 008 tests
```

They must not leak into earlier algorithm layers.

## Full-suite verification

After implementation, run:

```bash
python -m pytest tests -q
```

Also run the Task 008 slice:

```bash
python -m pytest tests/test_task008_*.py -q
```

Record both command outputs in the Task 008 summary.

## Required reports

Create:

```text
Build_Docs/Reports/task008/task008_summary.md
Build_Docs/Reports/task008/history_status_table.md
Build_Docs/Reports/task008/status_transition_rules.md
Build_Docs/Reports/task008/design_decisions.md
```

The status table must document:

```text
- each HistoryStatus
- input condition
- value shape
- validity mapping
- conditioning behavior
- protocol behavior
- refusal or incomplete behavior
```

The transition-rule report must document:

```text
- history.record_event
- history.event_pair.compare
- history.events.to_trace
- history.trace.require_stable
- input protocol
- output protocol
- input family
- output family
- accepted statuses
- refused statuses
- mapped statuses
- context keys
- notes
```

The design-decisions report must explicitly address:

```text
- why history uses caller-supplied sequence indices instead of wall-clock time
- why build_status_trace must not silently sort events
- why status changes are evidence rather than automatic regressions
- why optional geometry signatures are caller supplied
- why singleton traces are not accepted by the stable-trace requirement protocol
- why no smoothing, hysteresis, or forecasting is added
- why no persistent logging/database layer is added
- why existing Task 001 through Task 007 semantics remain unchanged
```

## Non-goals

Do not implement:

```text
- a domain consumer
- a domain classifier
- bearing/aerospace/betting/scanner logic
- flow integration
- finite_eta correction
- symbolic parsing
- symbolic simplification
- rewrite generation
- database persistence
- file-backed history storage
- telemetry/logging service
- wall-clock scheduling
- background workers
- smoothing windows
- hysteresis bands
- trend forecasting
- confidence scores
- weighted scores
- automatic stable/unstable thresholds
- result interpolation or extrapolation
- V3 fixtures
- adapters
- bridges
- compatibility modes
- cross-engine calls
```

## Acceptance criteria

Task 008 is complete only when:

```text
1. HistoryStatus exists and is exported consistently.
2. src/lloyd_v4/history exists with public history trace APIs.
3. record_status_event records compact event evidence from existing TypedResult objects.
4. compare_status_events emits pairwise transition evidence with defined precedence.
5. build_status_trace emits empty, singleton, stable, transitioned, incomplete, or unordered trace evidence correctly.
6. require_stable_status_trace accepts only stable traces and returns typed refusals otherwise.
7. HistoryResult aliases and protocols are exported.
8. Named history transition rules are exported and covered by tests.
9. Generic mixed-family joins remain conservative.
10. Existing Task 001 through Task 007 behavior and serialization remain unchanged.
11. Serialization preserves history evidence without recursive result trees.
12. No hidden correction constants, thresholds, smoothing, hysteresis, confidence scoring, or forecasting appear.
13. No domain consumer or V3 runtime dependency is added.
14. Task 008 reports are created under Build_Docs/Reports/task008.
15. Task 008 test slice passes.
16. Full suite passes.
17. Required source audits return no matches.
```

## Task 009 readiness

Task 009 may begin as the first domain-consumer scoping task, chosen only after the substrate is stable. Task 008 should leave the repository with a clean history layer that can record how typed evidence evolves, without deciding any downstream domain meaning.
