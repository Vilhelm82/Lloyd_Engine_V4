# Codex Task: Fold-Readback Probe 0 v10 — Active Threshold-Governed Dual-Arm Probe

## Purpose

Build the corrected active dual-arm probe for Fold-Readback Probe 0.

This is **not** a continuation of the v9 Goldilocks/passive overlap design. The v9 runner swept a width parameter `W`, evaluated ARM-N and ARM-W on the same authored `region_W`, then searched for overlap. That ontology is rejected for v10.

v10 must implement Will's active design:

- ARM-W is the primary surface scanner.
- ARM-W emits local sensitivity/falloff telemetry.
- ARM-N is activated by ARM-W falloff / near-floor telemetry, with hysteresis / guard overlap.
- ARM-N's validity is judged only by ARM-N's own instrument law.
- Both arms may be simultaneously valid in overlap zones.
- Overlap is used for agreement/calibration, not as the definition of success.
- The final product is a stitched typed readback over the surface, not a search for a shared Goldilocks zone.

Promotes nothing. Eval-layer only. No substrate primitive, manifest entry, protocol family, status enum, or Layer 1/2 runtime behavior may be added.

## Source Files To Reuse

Use the existing scratch files as the frozen substrate:

```text
scratch/run_foldreadback_probe0_v7.py
scratch/foldreadback_probe0_v8_outcomelaw.py
scratch/run_foldreadback_probe0_v9.py
```

Required reuse:

- Import v7 primitives, do not paste them:
  - `reseat`
  - `fit_ols`
  - `sweep`
  - `measure_point`
  - `binade_exp`
  - functionals in `DISTRIB` and `SCALARS`
  - `disc`
  - `ols_design_pivot_ok`, unless factored into a margin-returning sibling without changing the original boolean behavior
- Import the corrected v8 outcome law:
  - `classify_instrument`
  - `ANALYTIC_MAX` single-sourced from v7
- Do not reuse the v9 outcome ontology except as a negative reference.

Forbidden carry-over from v9:

- Do not define success by `overlap = [W where armN_valid and armW_valid]`.
- Do not emit `two_tier_overlap_fold_observed`, `two_tier_overlap_no_fold`, or `two_tier_validity_disjoint_no_overlap`.
- Do not evaluate both arms on the same authored `region_W` and call that the handoff.
- Do not require monotone validity in `W`; v10 is not a `W`-sweep hypothesis.

## New File Targets

Create:

```text
scratch/run_foldreadback_probe0_v10_active_dualarm.py
scratch/foldreadback_probe0_v10_active_dualarm_artifact.json
Build_Docs/Reports/foldreadback_probe0_v10_active_dualarm/closeout_v10.md
Build_Docs/Reports/foldreadback_probe0_v10_active_dualarm/artifact_v10.json
Build_Docs/Reports/foldreadback_probe0_v10_active_dualarm/preregistry_v10.md
```

Add focused tests where the repo convention allows. Suggested:

```text
tests/test_foldreadback_probe0_v10_active_dualarm.py
```

If scratch runners are not normally imported by the test tree, place tests under the existing eval/campaign test convention and keep them focused on v10 source/artifact behavior.

## Conceptual Model

v10 is an active two-instrument readback.

ARM-W:

- wide/global/surface-scanning arm
- reads the coarse sparsity-robust channel
- owns falloff telemetry
- remains active wherever it has a valid read
- does not gate ARM-N validity

ARM-N:

- narrow/local/gap-reading arm
- activated by ARM-W warning/falloff telemetry
- reads local coherent-level functionals
- independently reports valid / untested / separated under v8 law
- may overlap ARM-W before, during, and after ARM-W falloff

Overlap:

- is allowed and expected
- is not the target
- is not the outcome definition
- is used only for agreement calibration and conflict detection

## ARM Assignment

Preserve the v9 functional split unless the run proves it mechanically unusable, in which case record refusal rather than tuning silently.

```python
ARM_W_FUNCS = ["sign_pattern"]
ARM_N_FUNCS = ["level_histogram", "transition", "signed_occ", "lattice_rank"]
```

ARM-W validity requires:

- enough points for the local context
- ARM-W functional instrument state is `nondegenerate`
- OLS design is viable for that local context
- occupancy is viable if the chosen ARM-W read requires nonzero lattice observations

ARM-N validity requires:

- enough points for the local context
- at least one ARM-N functional instrument state is `nondegenerate`
- ARM-N must not depend on OLS slope separation for validity

## Critical Authored Joint A: Width-Stable Null Partition

The v9 failure came from a parity confound: v7 `nullband()` uses `halves()` as local sorted-index even/odd interleaving. Under a changing `W` window, every point's even/odd assignment can flip, causing validity to track parity rather than surface geometry.

v10 must not use local-window even/odd interleaving as the only null partition.

Implement an anchored null partition:

1. Assign each observed point a stable global rank once, over the full cancellation-relevant sweep, using a deterministic key such as `f0` or `x`.
2. For any subwindow, split by global rank parity, not local subwindow index.
3. Adding/removing a boundary point must not flip the half assignment of all existing interior points.
4. Preserve v7 functionals and `disc`; only the null partition is new.

Suggested API:

```python
def global_rank_map(points): ...

def anchored_halves(points, rank_map, phase=0):
    # phase=0 and phase=1 should merely swap halves, not change bands.
    ...

def anchored_nullband(points, rank_map, phase=0):
    ...
```

Use anchored null bands for v10 ARM instrument classification. The original v7 `nullband()` may be used only for comparison/diagnostic fields, not as the sole v10 authority.

## Critical Authored Joint B: ARM-W Falloff Telemetry

ARM-W must emit more than a boolean.

At each scan context, record:

```text
surface_key / center identifier
context point count
f-range / binades / x-range
ols_ok
ols_margin if available
armW_band
armW_instrument
armW_discrepancy if A1/A2 comparison is formed
armW_valid
falloff_state
falloff_reason
```

Minimum acceptable v10 telemetry can be structural rather than numerically continuous:

```text
readable       = ARM-W valid under v8 law + OLS viable
warning        = ARM-W valid but adjacent to a non-readable context or within a predeclared guard interval
below_floor    = ARM-W invalid because OLS failed, instrument collapsed/saturated, insufficient occupancy, or underpopulation
recovered      = readable after a below_floor interval
```

A richer `margin` is welcome, but do not make the campaign depend on an unvalidated smooth margin. If a numeric margin is added, it must be recorded as telemetry and tested for invariance, not used as an unreviewed discovery knob.

## Critical Authored Joint C: Active ARM-N Attention Window

ARM-N activation is governed by ARM-W telemetry, not by an independent `W` sweep.

Define core gaps:

```text
core_gap = maximal contiguous scan contexts where ARM-W falloff_state == below_floor
```

Define active ARM-N intervals:

```text
active_N_interval = core_gap expanded by a predeclared guard/hysteresis band on both sides
```

The guard band may be one scan stride on each side for v10. It exists to allow overlap and prevent hard handoff artifacts.

ARM-N may report while ARM-W is still readable in the guard/overlap region. ARM-W may continue reporting while ARM-N is active. Neither arm gates the other's validity.

If no ARM-W core gap exists, outcome is not a failure. It is `active_dual_read_wide_only_no_falloff` unless controls disqualify.

## Suggested Scan Construction

Use the cancellation-relevant region from v7:

```python
def creg(points):
    return sorted([p for p in points if p["e_f"] < p["e_x"]], key=lambda p: p["f0"])
```

Suggested v10 scan context:

- Assign global ranks over `creg(A1)`.
- Build sliding contexts by stable rank order.
- Use a fixed point-count context for ARM-W, minimum 5, preferred 9 because v7 Gate 1 used 9-point OLS windows.
- Boundary contexts with fewer than minimum points are `underpopulated`, not silently widened.
- ARM-N evaluates contexts only inside active_N intervals, using its own functional set and anchored null bands.

Do not tune context width after seeing the result. If multiple widths are tested, make it an invariance control: the verdict must be invariant or the result is invalidated.

## Per-Context Record Schema

Each scan record should include at least:

```json
{
  "idx": 0,
  "center_key": "...",
  "point_count_A1": 0,
  "point_count_A2": 0,
  "f_min": "...",
  "f_max": "...",
  "binades": [],
  "armW": {
    "active": true,
    "valid": false,
    "falloff_state": "readable|warning|below_floor|recovered|underpopulated",
    "falloff_reason": [],
    "instrument": {"sign_pattern": "nondegenerate|saturated|collapsed"},
    "band": {"sign_pattern": 0.0},
    "inference": "searched_no_separation|separated|untested",
    "ols_ok": false
  },
  "armN": {
    "active": false,
    "valid": false,
    "activation_reason": "none|guard|core_gap",
    "instrument": {},
    "band": {},
    "inference": "searched_no_separation|separated|untested"
  },
  "overlap": {
    "both_active": false,
    "both_valid": false,
    "agreement": "not_applicable|agree|conflict|underpowered"
  }
}
```

## Outcome Law

Outcome labels must be scoped to active dual readback:

```text
active_dual_read_disqualified_manufactured
active_dual_read_invalidated_partition_dependence
active_dual_read_protocol_refused
active_dual_read_wide_only_no_falloff
active_dual_read_gap_resolved
active_dual_read_gap_unresolved
active_dual_read_handover_conflict
```

Fixed precedence, first match wins:

1. `active_dual_read_disqualified_manufactured`
   - exact-zero or matched-affine control emits fold/separation where it must be silent.

2. `active_dual_read_invalidated_partition_dependence`
   - anchored partition phase / guard / scan-width invariance fails in any load-bearing outcome field.

3. `active_dual_read_protocol_refused`
   - no valid scan contexts can be formed or v8 law cannot classify required functionals.

4. `active_dual_read_handover_conflict`
   - at any overlap context where both arms are valid, their inferences conflict beyond the predeclared agreement rule.

5. `active_dual_read_gap_resolved`
   - ARM-W has at least one core gap / below-floor interval; ARM-N is active over that interval; at least one ARM-N context inside the interval is valid and not contradicted by controls; overlap contexts do not conflict.

6. `active_dual_read_gap_unresolved`
   - ARM-W has at least one core gap / below-floor interval; ARM-N activates but remains untested/invalid throughout the gap; controls pass.

7. `active_dual_read_wide_only_no_falloff`
   - ARM-W never enters below-floor on the scanned surface; ARM-N may remain inactive or guard-only; controls pass.

Important: `gap_resolved` does not mean the alpha-minus-one mission is satisfied. It means the active instrument architecture produced at least one ARM-N-valid read in an ARM-W-declared gap.

## Agreement Rule For Overlap

Overlap is diagnostic, not the target.

At overlap contexts:

- If both valid and both report no separation: `agree`.
- If both valid and both report separation/fold with compatible sign/direction if such direction is defined: `agree`.
- If one valid and the other active-but-untested: `underpowered`.
- If both valid and one reports separation while the other reports searched_no_separation on an explicitly comparable channel: `conflict`.
- If channels are not comparable, record `not_comparable`, not conflict.

Do not invent cross-channel equivalence after seeing output.

## Controls

Run all controls through the same active scanner and same ARM-N activation law.

Required controls:

1. Exact-zero / F3-like negative control
   - must remain silent
   - no fold/separation in either arm
   - no manufactured gap resolution claim

2. Matched-affine kill control
   - same active pipeline
   - any fold/separation in a context where the control should be silent -> disqualified manufactured

3. Partition invariance control
   - run anchored partition phase 0 and phase 1
   - load-bearing outputs must match
   - because phase should only swap halves, not alter bands/inference

4. Guard/hysteresis sanity control
   - changing the guard band by the predeclared sanity variant, e.g. 1 stride vs 2 strides, may change coverage counts but must not change top-level outcome from resolved to unresolved or conflict to non-conflict
   - if it does, invalidate as guard-dependent

5. Passive-v9 regression control
   - source audit must prove no v9 passive outcome labels are emitted
   - artifact must not contain `two_tier_overlap_no_fold` as the accepted outcome

## Tests To Add

Minimum focused tests:

1. `test_v10_does_not_emit_v9_overlap_labels`
   - Search artifact and source for accepted outcome labels beginning `two_tier_`.
   - They may appear only in comments explaining rejection, not in outcome fields.

2. `test_anchored_halves_stable_under_boundary_extension`
   - Construct a toy ranked point list.
   - Add one point to the start or end.
   - Existing points must keep the same half assignment.
   - This catches the v9 parity bug class.

3. `test_partition_phase_invariance`
   - Run v10 with anchored phase 0 and phase 1.
   - Top-level outcome and per-context instrument classification must match, allowing only half-label swap metadata.

4. `test_armN_activation_depends_on_armW_falloff_not_W_overlap`
   - Monkeypatch or synthetic telemetry: when ARM-W has no below-floor interval, ARM-N has no core-gap activation.
   - When ARM-W has a below-floor interval, ARM-N activates over that interval plus guard.

5. `test_armN_validity_independent_of_armW_validity`
   - Construct or monkeypatch a context where ARM-W is invalid and ARM-N has nondegenerate functionals.
   - ARM-N may be valid.
   - Construct or monkeypatch a context where ARM-W is valid and ARM-N degenerate.
   - ARM-N must remain untested.

6. `test_overlap_is_diagnostic_not_outcome_definition`
   - Force an overlap context.
   - Confirm outcome is not chosen merely because overlap exists.
   - Outcome must depend on gap resolution / controls / conflict rules.

7. `test_affine_kill_control_disqualifies_manufactured_fold`
   - If affine control has fold/separation in required-silent context, top-level outcome is `active_dual_read_disqualified_manufactured`.

8. `test_gap_unresolved_when_armN_never_valid`
   - Synthetic or monkeypatched active interval with ARM-N degenerate throughout -> `active_dual_read_gap_unresolved`.

9. `test_gap_resolved_when_armN_valid_inside_armW_gap`
   - Synthetic or monkeypatched active interval with at least one ARM-N valid context and no conflict -> `active_dual_read_gap_resolved`.

10. `test_artifact_schema_contains_telemetry_and_stitched_readback`
   - Artifact must include scan records, active intervals, control records, invariance records, top-level outcome, and closeout verdict.

## Acceptance Gates

Codex must report:

- New files created.
- Exact source reuse/import statement.
- Whether any v7 primitive was copied or modified. Expected: no.
- Whether v8 law was imported. Expected: yes.
- Whether v9 `region_W` overlap ontology appears in accepted logic. Expected: no.
- Focused tests passing.
- Full relevant test suite passing, or explicit reason if scratch-only campaign cannot run full repo tests.
- Artifact generated and copied into Build_Docs report folder.
- Closeout written.

Hard failure if:

- Accepted outcome uses `two_tier_*` labels.
- ARM-N validity is gated by ARM-W validity.
- ARM-N activation is independent of ARM-W falloff telemetry.
- Overlap is treated as the target rather than as diagnostic calibration.
- Local sorted-index even/odd nullband is the sole null authority.
- Controls are omitted.
- Any source primitive, manifest, runtime status enum, or protocol is modified.

## Closeout Requirements

The closeout must explicitly answer:

1. Did ARM-W produce falloff / below-floor intervals?
2. Did ARM-N activate because of ARM-W falloff telemetry?
3. Did ARM-N produce any valid read inside an ARM-W-declared gap?
4. Did overlap occur, and if so was it agreement, conflict, underpowered, or not comparable?
5. Did exact-zero and affine controls remain silent?
6. Did partition and guard invariance hold?
7. What is the accepted top-level outcome?
8. What does the outcome *not* establish?
9. Is the alpha-minus-one mission satisfied? Expected for v10: no, unless separately proven by the run under pre-registered criteria.

## Expected Scientific Status

v10 is an instrument architecture correction, not a claim of sub-noise-floor success.

Allowed findings:

- The active dual-arm architecture can or cannot produce an ARM-N valid gap read under ARM-W-declared falloff.
- Overlap can or cannot calibrate without conflict.
- The parity confound is or is not removed by anchored null partitions.
- The passive Goldilocks v9 failure is not repeated.

Forbidden findings:

- Do not claim the alpha-minus-one mission is solved.
- Do not claim fold geometry exists unless the predeclared fold criteria and controls support it.
- Do not claim no fold geometry exists from ARM-N untested regions.
- Do not collapse degenerate/untested into no-signal.
