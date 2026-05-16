# Fold-Readback Probe 0 v10 Preregistry - Active Dual-Arm Probe

## Scope

This preregistry locks the v10 active dual-arm scanner before the v10 runner is executed. v10 is eval-layer only and promotes no substrate primitive, manifest entry, protocol family, status enum, or runtime behavior.

## Frozen Reuse

The v10 runner imports the frozen scratch substrate:

- `scratch/run_foldreadback_probe0_v7.py`: `reseat`, `fit_ols`, `sweep`, `measure_point`, `binade_exp`, `DISTRIB`, `SCALARS`, `disc`, and `ols_design_pivot_ok`.
- `scratch/foldreadback_probe0_v8_outcomelaw.py`: `classify_instrument` and the v7-sourced `ANALYTIC_MAX`.
- `scratch/run_foldreadback_probe0_v9.py`: negative reference only. No accepted v10 logic uses the v9 `W` overlap ontology.

No v7 primitive is copied or modified.

## Locked Scanner

- Cancellation-relevant surface: points where `e_f < e_x`, sorted by `f0`.
- Stable rank source: full cancellation-relevant `A1` sweep.
- Scan contexts: fixed 9-point contexts by stable global rank order.
- Boundary contexts with fewer than 5 points are underpopulated.
- ARM-W functions: `["sign_pattern"]`.
- ARM-N functions: `["level_histogram", "transition", "signed_occ", "lattice_rank"]`.
- Default guard/hysteresis band: 1 scan stride on each side of each ARM-W below-floor core gap.
- Guard sanity variant: 2 scan strides.
- Anchored partition phases: 0 and 1. Phase may swap halves only; load-bearing outcome fields must match.

## Locked Validity

ARM-W is valid when:

- context has enough points in A1 and A2,
- `sign_pattern` instrument is `nondegenerate` under the anchored null band,
- v7 OLS design is viable for the local A1 and A2 contexts,
- nonzero occupancy exists in both local contexts.

ARM-N is valid when:

- context has enough points in A1 and A2,
- at least one ARM-N functional instrument is `nondegenerate` under the anchored null band.

ARM-N validity is independent of ARM-W validity. ARM-N activation is determined only by ARM-W falloff telemetry and guard expansion.

## Locked Outcome Precedence

First match wins:

1. `active_dual_read_disqualified_manufactured`
2. `active_dual_read_invalidated_partition_dependence`
3. `active_dual_read_protocol_refused`
4. `active_dual_read_handover_conflict`
5. `active_dual_read_gap_resolved`
6. `active_dual_read_gap_unresolved`
7. `active_dual_read_wide_only_no_falloff`

The rejected v9 `two_tier_*` labels are forbidden as accepted outcomes.
