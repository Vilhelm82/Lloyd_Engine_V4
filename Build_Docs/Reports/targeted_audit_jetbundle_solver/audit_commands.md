# Audit Commands

Run from `/mnt/fast/Lloyd_Engine_V4` on 2026-05-11.

## Full tests

```bash
python -m pytest tests -q
```

Output:

```text
........................................................................ [ 24%]
........................................................................ [ 48%]
........................................................................ [ 72%]
........................................................................ [ 97%]
........                                                                 [100%]
```

Additional collection count:

```bash
python -m pytest --collect-only -q tests | rg "^[^ ]+: [0-9]+$" | awk '{sum += $2} END {print sum}'
```

Output:

```text
296
```

## Source purity

```bash
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|\bepsilon\b|\beps\b" src -n
```

Output: no matches (`rg` exit code 1).

```bash
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard|clamp|stabilized_log|log_offset|log1p|isclose|allclose|threshold|tolerance|confidence_score|weighted_score|smoothing|hysteresis|interpolate|extrapolate" src/lloyd_v4 -n
```

Output: no matches (`rg` exit code 1).

```bash
rg -i "lloyd_core|lloyd_core_nvar|lloyd_decomposition|hyperdual|halley|multi_start|route_score" src/lloyd_v4 -n
```

Output: no matches (`rg` exit code 1).

```bash
rg "adapter|bridge|compatibility_shim|downgrade|legacy_mode|cross_engine" src/lloyd_v4 -n
```

Output: no matches (`rg` exit code 1).

## Alpha / transfer search

```bash
rg "typed_finite_difference|typed_log_log_slope|TRANSFER_CANCELLATION_DOMINATED|precision_floor|cancellation_ratio|alpha|α|log_log|slope" src tests Build_Docs -n
```

Output was long because it includes task specifications and completed reports. Key source/test matches:

```text
src/lloyd_v4/primitives/typed_finite_difference.py:20:        TransferStatus.TRANSFER_CANCELLATION_DOMINATED,
src/lloyd_v4/primitives/typed_finite_difference.py:28:    name="typed_finite_difference",
src/lloyd_v4/primitives/typed_finite_difference.py:50:    cancellation_ratio: float | None
src/lloyd_v4/primitives/typed_finite_difference.py:67:def typed_finite_difference(
src/lloyd_v4/primitives/typed_finite_difference.py:80:    precision_floor = _precision_floor(precision)
src/lloyd_v4/primitives/typed_finite_difference.py:172:    cancellation_ratio = abs(delta_g) / max_g
src/lloyd_v4/primitives/typed_finite_difference.py:173:    if cancellation_ratio < precision_floor:
src/lloyd_v4/primitives/typed_finite_difference.py:214:def _precision_floor(precision: str) -> float:
src/lloyd_v4/primitives/typed_log_log_slope.py:27:    name="typed_log_log_slope",
src/lloyd_v4/primitives/typed_log_log_slope.py:74:def typed_log_log_slope(
src/lloyd_v4/primitives/typed_log_log_slope.py:104:    log_f = tuple(math.log(f_value) for f_value, _transfer in pairs)
src/lloyd_v4/primitives/typed_log_log_slope.py:105:    log_t = tuple(math.log(abs(transfer)) for _f_value, transfer in pairs)
src/lloyd_v4/primitives/typed_log_log_slope.py:114:    slope, intercept, r_squared, standard_error = _ordinary_least_squares(log_f, log_t)
src/lloyd_v4/branch/slope_flow.py:170:def compare_slope_flow_to_models(
src/lloyd_v4/branch/slope_flow.py:246:    ratio = projective_ratio(delta_observable, delta_control)
src/lloyd_v4/branch/fingerprint.py:212:def compare_kq_slope_stability(
tests/test_task015_typed_finite_difference.py:42:def test_cancellation_dominated_stratum() -> None:
tests/test_task016_typed_log_log_slope.py:21:def _power_observations(alpha: float, f_values: list[float], delta_ratio: float = 1e-6):
tests/test_task016_typed_log_log_slope.py:28:def test_observed_stratum_recovers_alpha_minus_one_for_quadratic() -> None:
tests/test_task016_typed_log_log_slope.py:260:def test_alpha_minus_one_law_recovers_slope_for_known_alphas() -> None:
Build_Docs/Reports/task015_summary.md:1:# Task 015 Summary -- typed_finite_difference
Build_Docs/Reports/task016_summary.md:1:# Task 016 Summary -- typed_log_log_slope
Build_Docs/Reports/task016_summary.md:79:## Alpha-minus-one validation
```

## Precision floor search

```bash
rg "precision_floor|roundoff_floor|unit_roundoff|machine_epsilon|cancellation_ratio|2\.0\s*\*\*\s*-52|sys\.float_info\.epsilon|np\.finfo" src tests Build_Docs -n
```

Output:

```text
tests/test_task015_typed_finite_difference.py:39:    assert result.value.cancellation_ratio is None
tests/test_task015_typed_finite_difference.py:48:    assert any("cancellation_ratio" in note for note in result.conditioning.notes)
src/lloyd_v4/primitives/typed_finite_difference.py:50:    cancellation_ratio: float | None
src/lloyd_v4/primitives/typed_finite_difference.py:60:            "cancellation_ratio": to_json_safe(self.cancellation_ratio),
src/lloyd_v4/primitives/typed_finite_difference.py:80:    precision_floor = _precision_floor(precision)
src/lloyd_v4/primitives/typed_finite_difference.py:172:    cancellation_ratio = abs(delta_g) / max_g
src/lloyd_v4/primitives/typed_finite_difference.py:173:    if cancellation_ratio < precision_floor:
src/lloyd_v4/primitives/typed_finite_difference.py:176:            TransferObservation(transfer, g_f, g_f_plus, delta_g, cancellation_ratio),
src/lloyd_v4/primitives/typed_finite_difference.py:185:            (f"cancellation_ratio={cancellation_ratio:.3e}", f"precision_floor={precision_floor:.3e}"),
src/lloyd_v4/primitives/typed_finite_difference.py:190:        TransferObservation(transfer, g_f, g_f_plus, delta_g, cancellation_ratio),
src/lloyd_v4/primitives/typed_finite_difference.py:214:def _precision_floor(precision: str) -> float:
src/lloyd_v4/primitives/typed_finite_difference.py:216:        return 2.0**-52
Build_Docs/Reports/task015_summary.md:62:    "cancellation_ratio": 0.001997003995005692
Build_Docs/Agent_tasks/codex_task016_typed_log_log_slope.md:870:- **Task 017**: Add multi-precision support — extend `_precision_floor`
Build_Docs/Agent_tasks/Completed/codex_task015_typed_finite_difference.md:128:  `|Δg| / max(|g(f)|, |g(f+δf)|) < precision_floor` AND `max(|g(f)|, |g(f+δf)|) > 0`.
Build_Docs/Agent_tasks/Completed/codex_task015_typed_finite_difference.md:191:    cancellation_ratio: float | None  # |Δg|/max(|g_f|, |g_f_plus|), if defined
Build_Docs/Agent_tasks/Completed/codex_task015_typed_finite_difference.md:309:   Compute precision_floor = _precision_floor(precision)
Build_Docs/Agent_tasks/Completed/codex_task015_typed_finite_difference.md:310:     (sys.float_info.epsilon for "raw_python", future precisions add their own).
Build_Docs/Agent_tasks/Completed/codex_task015_typed_finite_difference.md:376:def _precision_floor(precision: str) -> float:
Build_Docs/Agent_tasks/Completed/codex_task015_typed_finite_difference.md:379:        return sys.float_info.epsilon  # ≈ 2.22e-16
```

## Transition rule search

```bash
rg "StatusTransitionRule|mapped_statuses|transition_fn|apply_status_transition|quadratic_roots.to_exact_projection|projection" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection tests -n
```

Key output:

```text
src/lloyd_v4/core/transitions.py:37:class StatusTransitionRule:
src/lloyd_v4/core/transitions.py:45:    mapped_statuses: Mapping[Enum, Enum]
src/lloyd_v4/core/transitions.py:83:def apply_status_transition(rule: StatusTransitionRule, status: Enum, **context: Any) -> StatusTransitionOutcome:
src/lloyd_v4/core/transitions.py:94:    if rule.transition is not None:
src/lloyd_v4/core/transitions.py:95:        return rule.transition(status, context)
src/lloyd_v4/core/transitions.py:96:    if status in rule.mapped_statuses:
src/lloyd_v4/primitives/projective_ratio.py:60:PROJECTIVE_RATIO_SCALARIZATION_TRANSITION_RULE = StatusTransitionRule(
src/lloyd_v4/primitives/stratified_quadratic_roots.py:102:QUADRATIC_ROOT_SELECTION_TRANSITION_RULE = StatusTransitionRule(
src/lloyd_v4/projection/exact_projection.py:78:def _projection_transition(status, context):
src/lloyd_v4/projection/exact_projection.py:116:QUADRATIC_ROOT_TO_EXACT_PROJECTION_TRANSITION_RULE = StatusTransitionRule(
src/lloyd_v4/projection/exact_projection.py:117:    rule_id="quadratic_roots.to_exact_projection",
src/lloyd_v4/projection/exact_projection.py:124:    mapped_statuses={
src/lloyd_v4/projection/exact_projection.py:135:    transition=_projection_transition,
tests/test_task005_status_transition_rules.py:30:def test_projection_contextual_transition_rule() -> None:
tests/test_task010_rebuild_projection_strata_scenarios.py:47:        projection = exact_quadratic_projection(root, branch_selection(branch))
```

## Layer dependency search

```bash
rg "from lloyd_v4\.metrology|import .*metrology" src/lloyd_v4/primitives src/lloyd_v4/projection -n
```

Output: no matches (`rg` exit code 1).

```bash
rg "from lloyd_v4\.branch|import .*branch" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology -n
```

Output: no matches (`rg` exit code 1).

```bash
rg "from lloyd_v4\.refinery|import .*refinery" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch -n
```

Output: no matches (`rg` exit code 1).

```bash
rg "from lloyd_v4\.history|import .*history" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery -n
```

Output: no matches (`rg` exit code 1).

```bash
rg "from lloyd_v4\.solver|import .*solver" src/lloyd_v4/core src/lloyd_v4/primitives src/lloyd_v4/projection src/lloyd_v4/metrology src/lloyd_v4/branch src/lloyd_v4/refinery src/lloyd_v4/history -n
```

Output: no matches (`rg` exit code 1).
