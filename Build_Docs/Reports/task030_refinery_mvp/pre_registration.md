# Task 030 Pre-Registration - Refinery MVP Decision Law

This document was written before any Task 030 MVP source code or MVP run output was created. It locks the decision law and the expected F1 vs F2 pure_algebraic outcome.

## Section A - Decision Law

### Geometry admissibility gate

The candidate and reference forms must match on every required metadata field before burden comparison runs:

| Field | Requirement |
| --- | --- |
| `fixture_name` | exact match |
| `operand_grid_label` | exact match |
| `declared_algebraic_identity` | exact match |
| `calibration_status` | exact match |
| `domain_stratum_label` | exact match |

The gate returns one of these typed statuses: `admissible`, `inadmissible_fixture_mismatch`, `inadmissible_grid_mismatch`, `inadmissible_identity_mismatch`, `inadmissible_calibration_mismatch`, `inadmissible_domain_mismatch`. Any inadmissible result records the mismatch field.

### Burden vector dimensions

Each burden vector dimension is read from committed campaign output, except static operation-chain depth, which is counted from the committed pure_algebraic fixture definitions.

| Dimension | Source and field path |
| --- | --- |
| `b_k_point_estimate` | `Build_Docs/Reports/task017c_multi_precision_theorem2/precision_aggregate.json`; `fits.pure_algebraic.<path>.regular_region.fit.b_k` |
| `b_k_ci_lower` | `Build_Docs/Reports/task017c_multi_precision_theorem2/precision_aggregate.json`; `fits.pure_algebraic.<path>.regular_region.b_k_ci_95[0]` |
| `b_k_ci_upper` | `Build_Docs/Reports/task017c_multi_precision_theorem2/precision_aggregate.json`; `fits.pure_algebraic.<path>.regular_region.b_k_ci_95[1]` |
| `lattice_class` | `Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/pure_algebraic_lattice_campaign_output.json`; `by_form.<path>.by_precision.float64.candidate_classification`, normalized to `integer_lattice`, `non_integer_lattice`, or `unclassified` |
| `max_integer_residual` | `Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/pure_algebraic_lattice_campaign_output.json`; `by_form.<path>.by_precision.float64.level_integer_residual_max` |
| `polarity_class` | `Build_Docs/Reports/task028_conditional_masks_joint_lattice_pure_algebraic/pure_algebraic_polarity_grid_stability.json`; `aggregate_classifications.F1_F2.aggregate` for the F1/F2 pair |
| `calibration_zero_preserved` | committed path identity table; `F3` is the calibration-zero sentinel, while F1 and F2 are non-calibration paths |
| `operation_chain_depth` | committed pure_algebraic fixture definitions; static operation count per path |

If a dimension is unavailable from the existing reports, the MVP records a typed sentinel for that dimension and records absence provenance. No field may be `None` or NaN in a burden vector.

### Pareto comparison rule

The comparison is componentwise only. There is no weighted aggregation and no scalar score.

| Dimension | Comparator |
| --- | --- |
| `b_k_point_estimate` | lower is better; overlapping CIs are tied |
| `lattice_class` | lower rank is better: `integer_lattice` < `non_integer_lattice` < `unclassified` |
| `max_integer_residual` | lower is better |
| `polarity_class` | F1/F2 pair classification must match |
| `calibration_zero_preserved` | must match |
| `operation_chain_depth` | lower is better |

The comparison returns one of four typed outcomes:

- `accepted`: the candidate is no worse on every required dimension and strictly better on at least one required dimension.
- `rejected`: the reference is no worse on every required dimension and strictly better on at least one required dimension.
- `forms_structurally_tied`: every required dimension is tied or equal.
- `comparison_indeterminate`: neither form dominates, or a required equality/pairing dimension mismatches, or a required dimension is unavailable.

## Section B - Expected Outcome on F1 vs F2 pure_algebraic

The MVP run will use F2 as the reference and F1 as the candidate.

| Burden dimension | F1 candidate | F2 reference | Pre-registered comparison |
| --- | ---: | ---: | --- |
| `b_k` point estimate | `0.28291099494381716` | `0.3638034361836378` | tied because CIs overlap |
| `b_k` CI | `[4.058963392730887e-101, 0.28291099494431743]` | `[2.727537910596299e-101, 0.3638034361837702]` | overlap |
| `lattice_class` | `integer_lattice` | `non_integer_lattice` | F1 lower burden |
| `max_integer_residual` | `0.0` | `0.25` | F1 lower burden |
| `polarity_class` | `grid_stable_polarity_coupling` | `grid_stable_polarity_coupling` | tied |
| `calibration_zero_preserved` | `false` | `false` | tied |
| `operation_chain_depth` | `1` | `2` | F1 lower burden |

Pre-registered expected decision outcome: `accepted`.

Pre-registered expected headline classification: `mvp_validates_decision_law`, provided all required dimensions are available from committed reports and the produced decision record matches the expected `accepted` outcome.
