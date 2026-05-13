# Task 031 Summary - Sterbenz Audit

## Scope

Task 031 extended the Task 030 eval-layer refinery MVP into a six-candidate Sterbenz audit for the pure_algebraic fixture. It added hand-curated rewrite candidates, deterministic measurement extension, N-way Pareto frontier analysis, audit outputs, and focused tests. It did not touch substrate primitives, manifests, the existing Layer 2 refinery package, or non-pure_algebraic fixtures.

## Pre-registration

- Commit: `4c97759 Task 031 pre-registration: Sterbenz audit candidates, burden dimensions, headline logic`
- Date: `2026-05-14 07:58:39 +1000`
- File: `Build_Docs/Reports/task031_sterbenz_audit/pre_registration.md`
- Status: byte-identical to the pre-registration commit at completion.

## Six Candidates

| Candidate | Expression | Pre-registered relation | Observed Sterbenz-region relation to reference |
| --- | --- | --- | --- |
| `c1_reference` | `(R * R) - 1.0 + x` | reference | dominated by `c2_reassociated` |
| `c2_reassociated` | `(R * R) + (x - 1.0)` | predicted worse in Sterbenz region | dominates reference; sole frontier member |
| `c3_factored` | `(R - 1.0) * (R + 1.0) + x` | predicted worse | dominated; calibration passed |
| `c4_power_operator` | `(R ** 2) - 1.0 + x` | predicted tied | tied with reference pairwise, but dominated by `c2_reassociated` |
| `c5_identity_padded` | `((R * R) - 1.0) / 1.0 + x` | predicted worse on depth only | dominated by `c1_reference`, `c2_reassociated`, and `c4_power_operator` |
| `c6_decimal_emulated` | `float(Decimal(R) * Decimal(R) - Decimal(1)) + x` | genuine uncertainty | dominated by `c1_reference`, `c2_reassociated`, and `c4_power_operator` |

## Sterbenz-Region Burden Vectors

| Candidate | `b_k` | `lattice_class` | `max_integer_residual` | `polarity_class` | `calibration_zero_preserved` | `operation_chain_depth` |
| --- | ---: | --- | ---: | --- | --- | ---: |
| `c1_reference` | `0.7324814637856604` | `non_integer_lattice` | `0.25` | `grid_stable_polarity_coupling` | `false` | `2` |
| `c2_reassociated` | `0.6398595836166981` | `integer_lattice` | `0.0` | `grid_stable_polarity_coupling` | `false` | `2` |
| `c3_factored` | `0.6124186554909158` | `non_integer_lattice` | `0.25` | `grid_stable_polarity_coupling` | `false` | `4` |
| `c4_power_operator` | `0.7324814637856604` | `non_integer_lattice` | `0.25` | `grid_stable_polarity_coupling` | `false` | `2` |
| `c5_identity_padded` | `0.7324814637856604` | `non_integer_lattice` | `0.25` | `grid_stable_polarity_coupling` | `false` | `3` |
| `c6_decimal_emulated` | `0.599080404014236` | `non_integer_lattice` | `0.25` | `grid_stable_polarity_coupling` | `false` | `3` |

All fields include provenance in `sterbenz_region_burden_vectors.json`.

## Full-Grid Burden Vectors

| Candidate | `b_k` | `lattice_class` | `max_integer_residual` | `polarity_class` | `calibration_zero_preserved` | `operation_chain_depth` |
| --- | ---: | --- | ---: | --- | --- | ---: |
| `c1_reference` | `0.5795827058656476` | `non_integer_lattice` | `0.25` | `grid_stable_polarity_coupling` | `false` | `2` |
| `c2_reassociated` | `0.49591489363988595` | `integer_lattice` | `0.0` | `grid_stable_polarity_coupling` | `false` | `2` |
| `c3_factored` | `0.5911692354423094` | `non_integer_lattice` | `0.25` | `grid_stable_polarity_coupling` | `false` | `4` |
| `c4_power_operator` | `0.5795827058656476` | `non_integer_lattice` | `0.25` | `grid_stable_polarity_coupling` | `false` | `2` |
| `c5_identity_padded` | `0.5795827058656476` | `non_integer_lattice` | `0.25` | `grid_stable_polarity_coupling` | `false` | `3` |
| `c6_decimal_emulated` | `0.4738714272508232` | `non_integer_lattice` | `0.25` | `grid_stable_polarity_coupling` | `false` | `3` |

## Pareto Frontier

Sterbenz-region frontier: `["c2_reassociated"]`.

Dominated candidates:

- `c1_reference`: dominated by `c2_reassociated`.
- `c3_factored`: dominated by `c1_reference`, `c2_reassociated`, `c4_power_operator`, `c5_identity_padded`, and `c6_decimal_emulated`.
- `c4_power_operator`: dominated by `c2_reassociated`.
- `c5_identity_padded`: dominated by `c1_reference`, `c2_reassociated`, and `c4_power_operator`.
- `c6_decimal_emulated`: dominated by `c1_reference`, `c2_reassociated`, and `c4_power_operator`.

Incomparable pairs: none.

## Region-Swap Finding

The pre-registered region-swap prediction was only partly supported. In the Sterbenz region (`x <= 0.5`), `c2_reassociated` was expected to be worse than `c1_reference`, but it instead dominated by improving `lattice_class` from `non_integer_lattice` to `integer_lattice` and `max_integer_residual` from `0.25` to `0.0`, with `b_k` tied by overlapping CI and no worse required dimensions. In the inapplicable region (`x > 0.5`), `c1_reference` and `c2_reassociated` were structurally tied under the declared burden rule: both had `integer_lattice`, residual `0.0`, depth `2`, matched polarity, and overlapping `b_k` CI.

## Calibration Check

`c3_factored` is off the Pareto frontier. The calibration check passed: the audit rejected the deliberately padded cancellation control through higher operation-chain depth while preserving the required equality and pairing channels.

## Decimal-Intermediate Finding

`c6_decimal_emulated` did not dominate the reference. Although its point-estimate `b_k` was lower than the reference in the Sterbenz region, the declared CI rule tied the `b_k` dimension, while `c6_decimal_emulated` retained the same non-integer lattice class and residual as the reference and had higher operation-chain depth. Under the pre-registered Pareto rule it was dominated by `c1_reference`, `c2_reassociated`, and `c4_power_operator`.

## Headline Classification

Headline: `sterbenz_dominated_by_alternative`.

The Sterbenz-blessed reference candidate was not on the Sterbenz-region Pareto frontier. `c2_reassociated` strictly dominated it through lower lattice burden while matching all required equality and pairing dimensions, and the calibration control remained off the frontier.

## Tests

- Baseline at task start: `d7a846658f4bd9144f69620cedbb3a70cb01292c`, 644 passing tests.
- Pre-registration commit: `4c97759`.
- Added tests: 42 collected tests in `tests/test_task031_sterbenz_audit.py`.
- Post-task collection: 686 tests collected.
- Focused task suite: `PYTHONPATH=src python -m pytest tests/test_task031_sterbenz_audit.py -q` passed.
- Full suite: `PYTHONPATH=src python -m pytest tests/ -q` passed.

## Byte-Stability

- `measurement_aggregate.json`: repeat generation matched report bytes.
- `sterbenz_region_burden_vectors.json`: repeat generation matched report bytes.
- `full_grid_burden_vectors.json`: repeat generation matched report bytes.
- `pareto_frontier.json`: repeat generation matched report bytes.
- `headline_classification.md`: repeat generation matched report bytes.
- `pre_registration.md`: diff against `4c97759` produced no output.

## Discipline Gates

- The candidate set stayed fixed to the six pre-registered rewrites.
- The existing Layer 2 refinery package was not imported or touched.
- `layer_manifest.json` and `LAYER_MANIFEST.md` were unchanged.
- `typed_finite_difference.py` was byte-identical to the task-start baseline.
- No forbidden import or API patterns from the task spec were introduced.
- No named hardcoded math constants were introduced in the new Task 031 source.
- No banned interpretive terms were present in the new Task 031 source or report files.

## Files Changed

- `Build_Docs/Agent_tasks/Completed/codex_task031_sterbenz_audit.md`
- `Build_Docs/Reports/task031_sterbenz_audit/pre_registration.md`
- `Build_Docs/Reports/task031_sterbenz_audit/measurement_aggregate.json`
- `Build_Docs/Reports/task031_sterbenz_audit/sterbenz_region_burden_vectors.json`
- `Build_Docs/Reports/task031_sterbenz_audit/full_grid_burden_vectors.json`
- `Build_Docs/Reports/task031_sterbenz_audit/pareto_frontier.json`
- `Build_Docs/Reports/task031_sterbenz_audit/headline_classification.md`
- `Build_Docs/Reports/task031_sterbenz_audit_summary.md`
- `src/lloyd_v4/evals/sterbenz_audit/__init__.py`
- `src/lloyd_v4/evals/sterbenz_audit/rewrite_candidates.py`
- `src/lloyd_v4/evals/sterbenz_audit/measurement_extension.py`
- `src/lloyd_v4/evals/sterbenz_audit/n_way_pareto.py`
- `src/lloyd_v4/evals/sterbenz_audit/audit_run.py`
- `tests/test_task031_sterbenz_audit.py`

## Forward Observations

- Substrate-level Decimal-100 intermediate exactness did not dominate operation-level exact subtraction under the declared burden vector; operation-chain depth kept it off the frontier.
- The reassociation region-swap prediction was refuted in the audit region and reduced to a tie above the boundary, so the region profile is more favorable to `c2_reassociated` than predicted.
- The audit discriminated operationally different but mathematically equivalent rewrites: `c4_power_operator` tied the reference, `c5_identity_padded` was rejected by depth, and `c2_reassociated` dominated by lattice burden.
- The unexpected profile is `c2_reassociated`: it moved from predicted-worse to sole-frontier status because it removed the non-integer lattice grain in the audit region.
- Auditing non-Sterbenz mechanisms such as Kahan summation or Wilkinson bounds would require mechanism-specific candidate curation, region declarations, and burden dimensions for sequence-level or bound-level behavior; those extensions are outside this task.
