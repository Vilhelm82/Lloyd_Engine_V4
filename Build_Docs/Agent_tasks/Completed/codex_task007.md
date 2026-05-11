# Codex Task 007: Protocol-Aware Equation Refinery

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

Task 005 is complete. `TypedResult` is generic over value type and status enum family. Protocols infer or declare status families and reject wrong-family typed results explicitly. Named transition-rule machinery exists with canonical rules for ProjectiveRatio scalarization, quadratic root selection, quadratic projection, limit-of-detection classification, and valid `K_q` calibration.

Task 006 is complete. The branch package exists under `src/lloyd_v4/branch`. It implements `BranchFingerprintStatus`, slope-flow comparison with ProjectiveRatio-backed segment slopes, declared model residual comparison, `K_q` slope-stability checks using Task 004 calibration evidence, and BranchFingerprint composition through named transition rules.

Task 006 verification baseline:

```text
Task 006 slice: 13 passed
Full suite: 123 passed
Clean-room, hidden-correction, dependency-direction, earlier-layer leakage, deferred-feature, and compatibility audits: no matches
```

## Task 007 goal

Implement the first protocol-aware equation refinery:

```text
Protocol-aware equation refinery
```

Task 007 should judge whether a proposed rewrite candidate preserves typed geometry and improves explicit diagnostic burden. It must not become a symbolic algebra engine, parser, simplifier, optimizer, domain classifier, or V3 comparison harness.

The refinery evaluates already-computed typed results. It compares reference observations against candidate observations under explicit protocol, status-family, validity, branch/fingerprint, and slag-reduction rules.

Task 007 should implement:

```text
1. a RefineryStatus family;
2. typed observation snapshots for reference and candidate results;
3. status-preserving and protocol-preserving comparison rules;
4. branch/fingerprint-aware same-geometry evidence checks;
5. explicit componentwise slag vectors;
6. a lower-slag acceptance gate;
7. named transition rules for refinery decisions;
8. serialization and reports for all new evidence.
```

The phrase `same_geometry` in Task 007 means **same-geometry evidence under the supplied protocol observations**, not a formal symbolic proof of algebraic equivalence. The refinery can accept or reject candidate evidence. It cannot prove universal mathematical equivalence over all inputs.

## Design principles

- Geometry precedes scalarization.
- Degeneracy is a stratum, not failure.
- Typed results compose by protocols.
- Mixed-status composition must use named transition rules.
- A rewrite is not clean unless protocol, status family, status emission, validity semantics, and branch/fingerprint geometry are preserved.
- Lower slag is explicit componentwise evidence, not a scalar confidence score.
- A candidate may improve conditioning or residual evidence only after same-geometry evidence has passed.
- BranchFingerprint evidence may be consumed, but the refinery is not a domain branch classifier.
- Refinery decisions are evidence objects, not proof certificates.
- No hidden epsilons, tolerance gates, denominator floors, clamps, safe division, rescue constants, log offsets, fallback branches, symbolic simplification, or compatibility modes.
- Metrology may annotate observability. It must not rewrite exact ProjectiveRatio, root, projection, or branch-fingerprint strata.
- Existing Task 001 through Task 006 behavior and serialization must remain unchanged.

## Required package boundary

Create a new package for refinery work.

Recommended files:

```text
src/lloyd_v4/refinery/__init__.py
src/lloyd_v4/refinery/observations.py
src/lloyd_v4/refinery/slag.py
src/lloyd_v4/refinery/decision.py
```

If the repository has a clearly better naming convention, use it, but do not place refinery implementation inside primitives, projection, metrology, branch, or core.

Expected core modification:

```text
src/lloyd_v4/core/status.py
```

Only add the new Refinery status family there. Do not add refinery algorithms to core.

Task 007 may import earlier layers in this direction:

```text
refinery -> core
refinery -> primitives, if needed for status-family recognition
refinery -> projection, if needed for projection evidence extraction
refinery -> metrology, if needed for metrology evidence extraction
refinery -> branch, if needed for BranchFingerprint evidence extraction
```

Earlier layers must not import refinery:

```text
core must not import refinery implementation modules
primitives must not import refinery
projection must not import refinery
metrology must not import refinery
branch must not import refinery
```

Task 007 may consume public APIs, result aliases, and named transition rules from earlier tasks. It must not patch earlier task behavior.

## Required status family

Add a new status enum family. Recommended name:

```python
RefineryStatus
```

Required initial statuses:

```text
rewrite_accepted_same_geometry_lower_slag
rewrite_equivalent_no_improvement
rewrite_rejected_protocol_mismatch
rewrite_rejected_status_family_mismatch
rewrite_rejected_status_mismatch
rewrite_rejected_validity_mismatch
rewrite_rejected_geometry_mismatch
rewrite_rejected_slag_regression
rewrite_indeterminate_insufficient_evidence
rewrite_indeterminate_unhandled_status
```

These names may be adjusted only if the final report includes a status table proving the same semantic coverage.

### Status meanings

`rewrite_accepted_same_geometry_lower_slag`

The candidate passes protocol preservation, status-family preservation, status preservation, validity preservation, and same-geometry evidence checks across all compared observations. Its slag vector is componentwise no worse than the reference and strictly lower in at least one declared dimension.

`rewrite_equivalent_no_improvement`

The candidate passes same-geometry evidence checks, but the slag vector is equal to the reference or has no declared strictly lower dimension. This is not a rejection of equivalence evidence; it is a refusal to claim refinement improvement.

`rewrite_rejected_protocol_mismatch`

At least one candidate observation has a different producer or consumer protocol identity than the reference observation, or cannot be validated under the expected protocol.

`rewrite_rejected_status_family_mismatch`

At least one candidate observation has a different status enum family from the reference observation. A wrong-family typed result must fail explicitly before ordinary accepted-set checks.

`rewrite_rejected_status_mismatch`

The candidate emits a different status from the reference for the same scenario under the same status family. Task 007 is status-preserving; changing a status is not a clean rewrite.

`rewrite_rejected_validity_mismatch`

The candidate changes `defined`, `finite`, `selectable`, `advanceable`, or `observable` semantics relative to the reference. Validity fields are part of the protocol contract, not metadata to ignore.

`rewrite_rejected_geometry_mismatch`

The candidate preserves status but changes required geometry evidence. Examples include changing a selected projection branch, changing projection flags, changing a BranchFingerprint selected model name, changing observable kind, or dropping source trace structure needed for comparison.

`rewrite_rejected_slag_regression`

The candidate passes same-geometry evidence checks but is worse in at least one declared slag dimension.

`rewrite_indeterminate_insufficient_evidence`

The comparison lacks required paired observations, scenario identifiers, trace/protocol/status information, or declared slag dimensions needed to make an honest decision.

`rewrite_indeterminate_unhandled_status`

The comparison encounters a status family or status that is not covered by a named refinery preservation rule.

## Validity mapping

Use the M0 validity fields consistently.

Recommended mapping:

```text
rewrite_accepted_same_geometry_lower_slag: defined, finite, selectable, not advanceable, observable
rewrite_equivalent_no_improvement:        defined, finite, not selectable, not advanceable, observable
rewrite_rejected_protocol_mismatch:       defined, finite, not selectable, not advanceable, observable
rewrite_rejected_status_family_mismatch:  defined, finite, not selectable, not advanceable, observable
rewrite_rejected_status_mismatch:         defined, finite, not selectable, not advanceable, observable
rewrite_rejected_validity_mismatch:       defined, finite, not selectable, not advanceable, observable
rewrite_rejected_geometry_mismatch:       defined, finite, not selectable, not advanceable, observable
rewrite_rejected_slag_regression:         defined, finite, not selectable, not advanceable, observable
rewrite_indeterminate_insufficient_evidence: not defined, not finite, not selectable, not advanceable, observable
rewrite_indeterminate_unhandled_status:      not defined, not finite, not selectable, not advanceable, observable
```

Task 007 must not use `advanceable=True`. Refinery decisions are not projection advancement.

## Required value objects

Use frozen dataclasses unless the existing codebase uses a different immutable pattern.

Recommended objects:

```python
@dataclass(frozen=True)
class TypedResultSnapshot:
    label: str
    scenario_id: str
    trace_id: str | None
    operation_id: str | None
    expression_path: str | None
    protocol: str | None
    status_family: str
    status: str
    validity: dict[str, bool]
    conditioning: str
    value_fingerprint: dict[str, object]
    source_trace_ids: tuple[str, ...]
```

`value_fingerprint` is not a domain fingerprint. It is a compact comparison summary extracted from known V4 typed values. It should preserve fields that are necessary for same-geometry evidence checks, such as branch labels, projection flags, selected model name, observable kind, and BranchFingerprint component summaries.

```python
@dataclass(frozen=True)
class RefineryObservation:
    label: str
    scenario_id: str
    result: object
    snapshot: TypedResultSnapshot
```

The `result` field may hold the original typed result in memory. Serialization should use the snapshot and trace IDs, not attempt to serialize arbitrary callables or unevaluated expressions.

```python
@dataclass(frozen=True)
class SlagVector:
    warning_count: int
    refusal_count: int
    indeterminate_count: int
    incomplete_count: int
    uncalibrated_count: int
    unstable_count: int
    max_model_residual: float | None
    max_kq_slope_abs: float | None
```

The exact slag dimensions may be adjusted if the design-decision report explains why. They must remain named dimensions, not weighted into a single hidden score.

```python
@dataclass(frozen=True)
class SlagComparison:
    reference: SlagVector
    candidate: SlagVector
    declared_dimensions: tuple[str, ...]
    componentwise_no_worse: bool
    strictly_lower_dimensions: tuple[str, ...]
    regressed_dimensions: tuple[str, ...]
```

```python
@dataclass(frozen=True)
class RefineryScenarioComparison:
    scenario_id: str
    reference_snapshot: TypedResultSnapshot
    candidate_snapshot: TypedResultSnapshot
    same_protocol: bool
    same_status_family: bool
    same_status: bool
    same_validity: bool
    same_geometry_evidence: bool
    slag_comparison: SlagComparison
    rejection_reasons: tuple[str, ...]
```

```python
@dataclass(frozen=True)
class RefineryDecisionValue:
    reference_name: str
    candidate_name: str
    scenario_comparisons: tuple[RefineryScenarioComparison, ...]
    aggregate_slag_comparison: SlagComparison
    accepted: bool
    decision_reason: str
    source_trace_ids: tuple[str, ...]
```

Exact field names can vary if necessary, but serialized evidence must preserve the same information.

Do not store only a boolean accept/reject result. Preserve per-scenario comparisons, status/protocol evidence, slag vectors, and source trace IDs.

## Required result aliases

Expose concrete typed result aliases, following the Task 005 pattern:

```python
RefineryDecisionResult = TypedResult[RefineryDecisionValue, RefineryStatus]
```

If you expose intermediate comparison results as typed results, also add explicit aliases for them. Export public aliases from the refinery package.

## Required protocols

Define producer/consumer protocols for Task 007.

Recommended protocol names:

```text
REFINERY_OBSERVATION_PROTOCOL
REFINERY_DECISION_PROTOCOL
REFINERY_ACCEPTED_REWRITE_PROTOCOL
```

Protocols must be status-family aware and use Task 005 machinery.

`REFINERY_ACCEPTED_REWRITE_PROTOCOL` should accept only:

```text
rewrite_accepted_same_geometry_lower_slag
```

and refuse every other `RefineryStatus`.

Wrong-family typed results must fail explicitly. For example, a `BranchFingerprintStatus.fingerprint_complete` result must not be mistaken for an accepted refinery decision just because it is selectable.

## Required transition rules

Add named transition rules for Task 007. They may live in the refinery package and be exported publicly. Core must not import refinery to register them.

Recommended rules:

```text
refinery.projective_ratio.status_preservation
refinery.quadratic_roots.status_preservation
refinery.projection.status_preservation
refinery.metrology.status_preservation
refinery.branch_fingerprint.status_preservation
refinery.decision.require_accepted
```

The exact set may vary, but the report must document every rule and prove that refinery decisions use named rules rather than local ad hoc joins.

### Required semantic coverage

Each status-preservation rule must cover every known status in its family at Task 007 time:

```text
ProjectiveRatioStatus
QuadraticRootStatus
ProjectionStatus
MetrologyStatus
BranchFingerprintStatus
```

For each family, a preservation rule must determine, with context, whether the candidate has the same status as the reference.

Recommended contextual keys:

```text
reference_status
candidate_status
reference_snapshot
candidate_snapshot
scenario_id
```

The rule output should feed the refinery decision path. It may map failures to a `RefineryStatus` rejection status.

`refinery.decision.require_accepted` must accept only:

```text
rewrite_accepted_same_geometry_lower_slag
```

and refuse:

```text
rewrite_equivalent_no_improvement
rewrite_rejected_protocol_mismatch
rewrite_rejected_status_family_mismatch
rewrite_rejected_status_mismatch
rewrite_rejected_validity_mismatch
rewrite_rejected_geometry_mismatch
rewrite_rejected_slag_regression
rewrite_indeterminate_insufficient_evidence
rewrite_indeterminate_unhandled_status
```

Generic `join_statuses(...)` must remain conservative. Task 007 must not add a universal mixed-family join.

## Required public APIs

Exact function names can vary if the package style requires, but Task 007 must expose equivalent APIs.

### 1. Snapshot a typed result

```python
def snapshot_typed_result(
    result: object,
    *,
    label: str,
    scenario_id: str,
) -> TypedResultSnapshot:
    ...
```

Behavior:

```text
- Accept only V4 TypedResult objects.
- Reject raw scalars, raw coefficient tuples, dictionaries, callables, strings, and unrelated objects.
- Preserve trace ID, operation ID, expression path, protocol identity, status family, status, validity, conditioning, and source trace IDs where available.
- Extract known comparison geometry fields from ProjectiveRatio, quadratic root, ProjectionResultV4, metrology, and BranchFingerprint values.
- Unknown but valid TypedResult families must either produce a minimal snapshot and later become rewrite_indeterminate_unhandled_status, or fail through explicit protocol validation. Do not silently compare unknown values.
```

Snapshot extraction must not recompute the original operation. It reads evidence only.

### 2. Compute an explicit slag vector

```python
def compute_slag_vector(
    snapshot: TypedResultSnapshot,
    *,
    declared_dimensions: Sequence[str] | None = None,
) -> SlagVector:
    ...
```

Behavior:

```text
- Use named dimensions only.
- Count warning conditioning as warning evidence.
- Count statuses containing explicit refusal evidence as refusal evidence when available.
- Count indeterminate, incomplete, uncalibrated, and unstable statuses by status semantics, not by string hacks alone.
- Extract max model residual from BranchFingerprint/slope-flow evidence when present.
- Extract max absolute Kq slope evidence from Kq slope-stability evidence when present.
- Do not compute a hidden weighted scalar score.
- Do not use a hidden tolerance, threshold, epsilon, or rescue constant.
```

If a declared dimension is not available for either reference or candidate, the dimension may be ignored. If it is available for the reference but missing from the candidate, the comparison should become indeterminate or a geometry mismatch, depending on which evidence was dropped.

### 3. Compare one scenario

```python
def compare_refinery_scenario(
    reference: RefineryObservation,
    candidate: RefineryObservation,
    *,
    declared_slag_dimensions: Sequence[str] | None = None,
) -> RefineryScenarioComparison:
    ...
```

Behavior:

```text
- Scenario IDs must match.
- Protocol identities must match.
- Status families must match.
- Statuses must match.
- Validity fields must match exactly.
- Geometry evidence must match according to the value_fingerprint for the active status family.
- Conditioning may improve or remain equal. Conditioning regression contributes to slag regression.
- Provenance trace IDs and expression paths may differ. A rewrite is expected to have a different expression path.
- Source trace IDs must be preserved sufficiently for auditability. Dropping source traces is a geometry/evidence mismatch.
- Use the relevant named status-preservation transition rule for the active status family.
- Do not use generic mixed joins to compare statuses.
```

Same-geometry evidence checks should include at least:

```text
ProjectiveRatio: preserve projective status and coordinate-shape evidence.
Quadratic roots: preserve root-state status and branch label set for selectable roots.
ProjectionResultV4: preserve projection status, requested/selected branch labels, and projection flags.
Metrology: preserve metrology status and comparison/calibration role.
BranchFingerprint: preserve fingerprint status, observable kind, selected model name when present, projection branch evidence, and proxy mode evidence.
```

Do not require the candidate trace ID to equal the reference trace ID. That would reject every actual rewrite.

### 4. Evaluate a rewrite candidate across scenarios

```python
def evaluate_rewrite_candidate(
    reference_observations: Sequence[RefineryObservation],
    candidate_observations: Sequence[RefineryObservation],
    *,
    reference_name: str = "reference",
    candidate_name: str,
    declared_slag_dimensions: Sequence[str] | None = None,
) -> RefineryDecisionResult:
    ...
```

Behavior:

```text
- Require paired scenario IDs.
- Reject duplicate scenario IDs.
- Preserve all scenario comparison evidence.
- If any scenario has protocol mismatch, emit rewrite_rejected_protocol_mismatch.
- Else if any scenario has status-family mismatch, emit rewrite_rejected_status_family_mismatch.
- Else if any scenario has status mismatch, emit rewrite_rejected_status_mismatch.
- Else if any scenario has validity mismatch, emit rewrite_rejected_validity_mismatch.
- Else if any scenario has geometry mismatch, emit rewrite_rejected_geometry_mismatch.
- Else aggregate slag vectors componentwise across scenarios.
- If candidate regresses in any declared slag dimension, emit rewrite_rejected_slag_regression.
- If candidate is componentwise no worse and strictly lower in at least one declared dimension, emit rewrite_accepted_same_geometry_lower_slag.
- If candidate is componentwise equal or no declared dimension is strictly lower, emit rewrite_equivalent_no_improvement.
- If evidence is missing or unhandled, emit the appropriate indeterminate status.
```

The aggregate lower-slag gate must be componentwise. Do not introduce weights, learned scoring, confidence scores, or total-order ranking unless the policy is explicit and serialized. Task 007 should not choose among multiple candidate rewrites. It evaluates one candidate against one reference observation suite.

### 5. Require an accepted rewrite

```python
def require_accepted_rewrite(result: RefineryDecisionResult) -> RefineryDecisionResult:
    ...
```

Behavior:

```text
- Validate the result against REFINERY_ACCEPTED_REWRITE_PROTOCOL.
- Accept only rewrite_accepted_same_geometry_lower_slag.
- Return typed refusal evidence for every other RefineryStatus.
- Wrong-family typed results fail explicitly.
```

## Slag semantics

Task 007 may use the word `slag` because the roadmap explicitly calls for a same-geometry lower-slag gate. It must define slag as explicit evidence dimensions only.

Recommended default dimensions:

```text
warning_count
refusal_count
indeterminate_count
incomplete_count
uncalibrated_count
unstable_count
max_model_residual
max_kq_slope_abs
```

Comparison rule:

```text
candidate is lower-slag iff:
  candidate <= reference in every declared comparable dimension
  and candidate < reference in at least one declared comparable dimension
```

No dimension may be silently weighted. No dimension may be hidden. No absent dimension may be replaced with a magic numeric sentinel.

For float evidence, comparisons use the computed finite Python float values stored in typed evidence. Task 007 does not attempt symbolic real comparison or arbitrary-precision comparison.

## Same-geometry evidence contract

Task 007 must distinguish these concepts:

```text
same protocol       same producer/consumer protocol identity
same status family  same enum family
same status         same emitted status within the family
same validity       same validity flags
same geometry       same status plus required branch/model/projection/fingerprint evidence
lower slag          same geometry plus explicit componentwise diagnostic improvement
```

Same-geometry evidence is not merely scalar equality. It must inspect the typed evidence appropriate to the active family.

Examples:

```text
A projection rewrite that changes selected_branch from minus to plus is rejected as geometry mismatch.
A projection rewrite that changes advance_valid is rejected as validity or geometry mismatch.
A BranchFingerprint rewrite that changes selected_model_name is rejected as geometry mismatch.
A BranchFingerprint rewrite that preserves selected_model_name but lowers max model residual may be accepted.
A metrology rewrite that turns below_limit_of_detection into detected is rejected as status mismatch.
A ProjectiveRatio rewrite that turns infinite_direction into finite_ratio is rejected as status mismatch, even if it returns a finite scalar.
```

## Serialization requirements

All new values must serialize strictly through existing V4 serialization.

Serialization must preserve:

```text
RefineryStatus
reference name
candidate name
scenario IDs
reference snapshots
candidate snapshots
protocol identities
status families
statuses
validity fields
conditioning labels
value_fingerprint evidence
per-scenario slag vectors
aggregate slag vector
componentwise comparison evidence
accepted flag
decision reason
rejection reasons
source trace IDs
provenance
```

No `inf`, `nan`, scalar sentinel, stringified exception, hidden score, or unserializable callable should appear in serialized evidence.

## Conditioning requirements

Recommended conditioning mapping:

```text
well-conditioned:
  rewrite_accepted_same_geometry_lower_slag
  rewrite_equivalent_no_improvement

warning:
  rewrite_rejected_protocol_mismatch
  rewrite_rejected_status_family_mismatch
  rewrite_rejected_status_mismatch
  rewrite_rejected_validity_mismatch
  rewrite_rejected_geometry_mismatch
  rewrite_rejected_slag_regression
  rewrite_indeterminate_insufficient_evidence
  rewrite_indeterminate_unhandled_status
```

If the existing code uses different conditioning enum names, map these semantics to the existing enum.

## Required tests

Create Task 007 tests under `tests/`. Recommended files:

```text
tests/test_task007_refinery_snapshot.py
tests/test_task007_same_geometry_checks.py
tests/test_task007_slag_gate.py
tests/test_task007_refinery_protocols.py
tests/test_task007_transition_rules.py
tests/test_task007_serialization.py
tests/test_task007_source_purity.py
```

### Red test expectation

Before implementation, the Task 007 slice should fail during collection because `lloyd_v4.refinery` and/or `RefineryStatus` do not exist.

### Snapshot tests

Test at least:

```text
- snapshot_typed_result rejects raw scalars, tuples, dictionaries, callables, and unrelated objects;
- ProjectiveRatio results snapshot status family, status, validity, protocol, trace ID, and projective coordinate shape;
- quadratic root-state results snapshot status family, status, validity, branch labels, and trace evidence;
- ProjectionResultV4 results snapshot requested branch, selected branch, projection flags, and source trace IDs;
- metrology results snapshot calibration/noise-floor role and status;
- BranchFingerprint results snapshot fingerprint status, observable kind, selected model name, proxy evidence, and projection branch evidence;
- snapshots do not recompute the source operation.
```

### Same-geometry tests

Test at least:

```text
- identical status/protocol/validity evidence passes same-geometry checks;
- different protocol emits rewrite_rejected_protocol_mismatch;
- wrong status family emits rewrite_rejected_status_family_mismatch;
- same family but different status emits rewrite_rejected_status_mismatch;
- same status but different validity flags emits rewrite_rejected_validity_mismatch;
- same projection status but different selected_branch emits rewrite_rejected_geometry_mismatch;
- same projection status but changed advance_valid/projection flag emits rewrite_rejected_geometry_mismatch or validity mismatch;
- same BranchFingerprint status but different selected_model_name emits rewrite_rejected_geometry_mismatch;
- same BranchFingerprint status and selected_model_name with lower residual remains eligible for the slag gate.
```

### Slag-gate tests

Test at least:

```text
- same-geometry candidate with componentwise lower slag emits rewrite_accepted_same_geometry_lower_slag;
- same-geometry candidate with equal slag emits rewrite_equivalent_no_improvement;
- same-geometry candidate with one worse declared dimension emits rewrite_rejected_slag_regression;
- lower max_model_residual can count as lower slag only when status, selected model, protocol, and geometry evidence are preserved;
- lower warning_count can count as lower slag only when status/protocol/validity/geometry evidence are preserved;
- absent comparable dimensions are not replaced with numeric sentinels;
- no hidden weighted score is produced.
```

### Protocol tests

Test at least:

```text
- REFINERY_DECISION_PROTOCOL is status-family aware;
- REFINERY_ACCEPTED_REWRITE_PROTOCOL accepts only rewrite_accepted_same_geometry_lower_slag;
- require_accepted_rewrite returns typed refusal for equivalent, rejected, and indeterminate refinery statuses;
- wrong-family typed results fail explicitly;
- runtime protocol validation remains active even with generic TypedResult aliases.
```

### Transition-rule tests

Test at least:

```text
- Task 007 transition rules are exported and importable;
- every ProjectiveRatioStatus is covered by the projective status-preservation rule;
- every QuadraticRootStatus is covered by the root status-preservation rule;
- every ProjectionStatus is covered by the projection status-preservation rule;
- every MetrologyStatus is covered by the metrology status-preservation rule;
- every BranchFingerprintStatus is covered by the branch-fingerprint status-preservation rule;
- refinery.decision.require_accepted accepts only the accepted rewrite status;
- generic join_statuses remains conservative for mixed families;
- evaluate_rewrite_candidate uses named preservation rules rather than local ad hoc joins.
```

### Serialization tests

Test at least:

```text
- RefineryDecisionResult serializes scenario comparisons, snapshots, slag vectors, componentwise comparison evidence, status, validity, conditioning, and provenance;
- typed refusals from require_accepted_rewrite serialize without numeric sentinels;
- serialized snapshots preserve source trace IDs and expression path differences;
- serialized evidence contains no callables or raw unevaluated expression objects.
```

### Existing-flow regression

Run full suite and ensure all previous Task 001 through Task 006 tests still pass.

Task 007 must not alter existing behavior or serialization for ProjectiveRatio, StratifiedQuadraticRoots, ProjectionResultV4, metrology, BranchFingerprint, core protocols, or prior transition rules.

## Source-purity audits

Run these audits after implementation. Adjust only for actual package names if they differ.

Clean-room and legacy audit:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
```

Hidden correction audit:

```bash
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance|confidence_score|weighted_score" src/lloyd_v4 -n
```

Dependency-direction audit:

```bash
rg "lloyd_v4\.refinery|from lloyd_v4\.refinery|import .*refinery" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch -n
```

Earlier-layer refinery leakage audit:

```bash
rg "equation_refinery|refinery|rewrite_candidate|same_geometry|lower_slag|slag" src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch -n
```

Layer dependency audits:

```bash
rg "lloyd_v4\.branch|from lloyd_v4\.branch|import .*branch" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology -n
rg "lloyd_v4\.metrology|from lloyd_v4\.metrology|import .*metrology" src/lloyd_v4/primitives src/lloyd_v4/projection -n
rg "lloyd_v4\.projection|from lloyd_v4\.projection|import .*projection" src/lloyd_v4/primitives src/lloyd_v4/metrology -n
```

Deferred-feature and domain-consumer audit:

```bash
rg "finite_eta|history_trace|domain_consumer|domain_classifier|bearing|aerospace|betting|scanner|flow_integrator|symbolic_simplifier|cas|parser" src/lloyd_v4 -n
```

Compatibility audit:

```bash
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

If an audit catches an intended Task 007 identifier, narrow the audit path rather than renaming architectural concepts into nonsense. Do not rename existing core provenance fields.

## Required reports

Create Task 007 reports under:

```text
Build_Docs/Reports/task007/
```

Required files:

```text
Build_Docs/Reports/task007/task007_summary.md
Build_Docs/Reports/task007/refinery_status_table.md
Build_Docs/Reports/task007/status_transition_rules.md
Build_Docs/Reports/task007/design_decisions.md
```

### task007_summary.md

Include:

```text
files created
files modified
behavior summary
red test result
task slice result
full suite result
source audit results
deviations
Task 008 readiness
```

### refinery_status_table.md

Include a table with:

```text
status
input condition
value shape
validity mapping
conditioning behavior
protocol behavior
refusal/indeterminate behavior
```

### status_transition_rules.md

Document all Task 007 transition rules, including:

```text
input protocol
output protocol
input status family
output status family
accepted statuses
refused statuses
mapped statuses
context keys
notes
```

### design_decisions.md

Document at least:

```text
why the refinery consumes typed observations rather than parsing equations
why same_geometry is evidence-based, not symbolic proof
why status preservation is mandatory
why protocol preservation is mandatory
why validity preservation is mandatory
why branch/model/fingerprint evidence is part of geometry preservation
why lower slag is componentwise and explicit, not weighted or hidden
why trace IDs may differ while source trace evidence must be preserved
why the refinery is not a domain classifier
why no hidden tolerances or confidence scores are allowed
```

## Non-goals

Do not implement:

```text
symbolic equation parsing
symbolic simplification
CAS integration
automatic rewrite generation
multi-candidate ranking or search
domain branch classification
bearing, aerospace, betting, scanner, or other domain consumers
history-aware status traces
finite-eta correction
flow integration
spatial projection
adaptive sampling
arbitrary-precision arithmetic
complex roots
new quadratic formulas
new projection policies
nearest/principal/default branch policies
K_G as engine identity
V3 fixtures or V3 comparison tests
adapters, bridges, compatibility shims, downgrade modes, or cross-engine calls
```

Task 007 may evaluate a supplied candidate against a supplied reference observation suite. It must not invent candidate rewrites.

## Acceptance criteria

Task 007 is complete when:

```text
1. RefineryStatus exists with the required semantic coverage.
2. A refinery package exists and exposes snapshot, slag, scenario-comparison, candidate-evaluation, and require-accepted APIs.
3. The refinery consumes V4 TypedResult observations only and rejects raw scalars, raw tuples, callables, dictionaries, and unrelated objects.
4. Status preservation, protocol preservation, status-family preservation, validity preservation, and geometry-evidence preservation are enforced before any lower-slag claim.
5. Lower slag is componentwise explicit evidence, not a hidden weighted score.
6. BranchFingerprint evidence is consumed without becoming a domain classifier.
7. Projection branch labels, projection flags, selected model names, observable kind, proxy evidence, and source trace IDs are preserved in same-geometry checks.
8. Named Task 007 transition rules exist and cover all Task 001 through Task 006 status families relevant to refinery comparisons.
9. Generic join_statuses remains conservative for mixed families.
10. Existing Task 001 through Task 006 behavior and serialization remain unchanged.
11. New serialization tests pass.
12. New transition-rule coverage tests pass.
13. Source audits return no matches.
14. Full test suite passes.
15. Task 007 reports are written under Build_Docs/Reports/task007.
```

## Task 008 readiness

Task 008 should be scoped as:

```text
History-aware status traces
```

Task 008 may use refinery decision evidence as one source of status-transition history. It must not be implemented in Task 007.
