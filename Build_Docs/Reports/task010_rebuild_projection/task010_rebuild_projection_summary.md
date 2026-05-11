# Task 010 Rebuild Projection Summary

## Files created

- `src/lloyd_v4/projection/branches.py`
- `tests/_projection_branch.py`
- `tests/test_task010_rebuild_projection_branch_selection.py`
- `tests/test_task010_rebuild_projection_protocol.py`
- `tests/test_task010_rebuild_projection_result.py`
- `tests/test_task010_rebuild_projection_serialization.py`
- `tests/test_task010_rebuild_projection_strata_scenarios.py`
- `Build_Docs/Reports/task010_rebuild_projection/task010_rebuild_projection_summary.md`
- `Build_Docs/Reports/task010_rebuild_projection/projection_rebuild_design.md`
- `Build_Docs/Reports/task010_rebuild_projection/behavioral_deltas.md`

## Files modified

- `src/lloyd_v4/projection/exact_projection.py`
- `src/lloyd_v4/projection/__init__.py`
- `src/lloyd_v4/solver/typed_projection_solver.py`
- `src/lloyd_v4/branch/fingerprint.py`
- `src/lloyd_v4/refinery/observations.py`
- `src/lloyd_v4/refinery/decision.py`
- `Build_Docs/Architecture/layer_manifest.json`
- `Build_Docs/Architecture/LAYER_MANIFEST.md`
- Existing tests that exercised the old raw-string projection signature or removed projection flags.

## Files deleted

- `tests/test_task003_projection_protocol.py`
- `tests/test_task003_projection_result.py`
- `tests/test_task003_projection_serialization.py`
- `tests/test_task009a_projection_strata_scenarios.py`

## Test results

Red slice before implementation:

```bash
python -m pytest tests/test_task010_rebuild_projection_branch_selection.py tests/test_task010_rebuild_projection_protocol.py tests/test_task010_rebuild_projection_result.py tests/test_task010_rebuild_projection_serialization.py tests/test_task010_rebuild_projection_strata_scenarios.py -q
```

Result: failed as expected because the new test files did not yet exist.

Green slice:

```bash
python -m pytest tests/test_task010_rebuild_projection_branch_selection.py tests/test_task010_rebuild_projection_protocol.py tests/test_task010_rebuild_projection_result.py tests/test_task010_rebuild_projection_serialization.py tests/test_task010_rebuild_projection_strata_scenarios.py -q
```

Result: `13 passed`.

Full suite:

```bash
python -m pytest tests -q
```

Result: full suite passed, `236 passed`.

010B/010C audits:

```bash
python -m pytest tests/test_task010b_manifest_completeness.py tests/test_task010b_export_drift.py tests/test_task010b_cross_layer_parent_check.py tests/test_task010b_status_family_layer_coherence.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_cross_family_transitions_justified.py tests/test_task010c_no_chain_cycles.py -q
```

Result: `9 passed`.

## Source audits

All required source audits returned no matches:

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance|confidence_score|weighted_score|smoothing|hysteresis|interpolate|extrapolate" src/lloyd_v4 -n
rg -i "lloyd_core|lloyd_core_nvar|lloyd_decomposition|hyperdual|halley|multi_start|route_score" src/lloyd_v4 -n
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

Additional projection-specific audits:

- `ProjectionFlags`: no source matches.
- `ProjectionResultValue.refusal`: no source matches.
- Old raw-string production call signature: no `src/lloyd_v4` call sites remain.
- Deleted test files: absent.

## Lineage corpus

Measured by running the full suite with the 010C collector:

- Distinct runtime operation_ids: 27
- Calibrated primitive operations in manifest: 11
- `exact_quadratic_projection` in calibrated primitives: false
- `branch_selection` registered in `projection.operations`: true
- `exact_quadratic_projection` instances with empty parents: 0

`exact_quadratic_projection` is now a composite result with parent traces from the root-state input, branch-selection input, and selected-root result when selection occurs.

## Deviations

The task asked to avoid modifying other layers except call sites. Removing `ProjectionFlags` made existing branch/refinery consumers dereference fields that no longer exist, so those consumers were updated to compare and serialize projection status/branch fields directly. This was necessary to keep the rebuilt value contract coherent and to pass the full suite without reintroducing flag derivation into projection.

Several existing tests outside the newly replaced files were updated because they were exercising the removed raw-string signature or removed projection flags. No production backward-compatibility shim was added.

## Next-task readiness

Projection is now rebuilt against typed primitive substrate inputs. The active transition-rule path worked cleanly once branch selection became typed. The next rebuild should inspect the next eligible layer directly; likely candidates are metrology or another layer depending only on core, primitives, and rebuilt projection. Do not assume the projection deltas repeat exactly.
