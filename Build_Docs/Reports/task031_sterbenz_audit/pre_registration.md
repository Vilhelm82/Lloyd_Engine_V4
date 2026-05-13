# Task 031 Pre-Registration - Sterbenz Audit

This document was written before Task 031 measurement source, measurement outputs, frontier outputs, or audit summary artifacts were created. It locks the rewrite candidate set, burden dimensions, Sterbenz-region rule, and headline classification logic.

## Section A - Rewrite Candidate Set

All six candidates declare `fixture_name=pure_algebraic`, `operand_grid_label=pure_algebraic_x_grid_137`, `declared_algebraic_identity=pure_algebraic_zero_constraint`, `calibration_status=non_calibration`, and `domain_stratum_label=canonical_137_point_domain`.

| Candidate ID | Expression | Tested property | Expected burden relation to `c1_reference` |
| --- | --- | --- | --- |
| `c1_reference` | `(R * R) - 1.0 + x` | Sterbenz-blessed explicit subtraction | `reference` |
| `c2_reassociated` | `(R * R) + (x - 1.0)` | Reassociation; swaps subtraction protection from `x <= 1/2` to `x >= 1/2` | `predicted_worse` in the Sterbenz region; `predicted_better` or tied in the inapplicable region |
| `c3_factored` | `(R - 1.0) * (R + 1.0) + x` | Deliberate cancellation control near `R = 1` | `predicted_worse` and expected off the frontier |
| `c4_power_operator` | `(R ** 2) - 1.0 + x` | Operator shift from multiplication syntax to power syntax | `predicted_tied` |
| `c5_identity_padded` | `((R * R) - 1.0) / 1.0 + x` | Identity padding that should preserve values while increasing operation-chain depth | `predicted_worse` on operation-chain depth only |
| `c6_decimal_emulated` | `float(Decimal(R) * Decimal(R) - Decimal(1)) + x` | Decimal-100 intermediate before binary final addition | `genuine_uncertainty` |

The candidate set is closed. No extra rewrites are added after this commit.

## Section B - Burden Vector Dimensions and Pareto Rule

The audit uses the same burden dimensions and comparator directions as Task 030:

| Dimension | Comparator |
| --- | --- |
| `b_k_point_estimate` | lower is better; overlapping CIs are tied |
| `b_k_ci_lower` | support field for the `b_k` CI comparator |
| `b_k_ci_upper` | support field for the `b_k` CI comparator |
| `lattice_class` | lower rank is better: `integer_lattice` < `non_integer_lattice` < `unclassified` |
| `max_integer_residual` | lower is better |
| `polarity_class` | paired classification must match the reference pair requirement |
| `calibration_zero_preserved` | must match |
| `operation_chain_depth` | lower is better |

N-way Pareto frontier rule: a candidate is on the frontier if no other candidate strictly dominates it under the componentwise burden policy. Pairwise outcomes use Task 030's typed outcomes: `accepted`, `rejected`, `forms_structurally_tied`, and `comparison_indeterminate`.

No weighted aggregation and no scalar score are used.

## Section C - Sterbenz Region and Headline Logic

Sterbenz-applicable region: `x <= 0.5` on the canonical pure_algebraic grid. The grid boundary includes `x = 0.5`.

The audit headline is determined only by the Sterbenz-region Pareto frontier:

- `sterbenz_minimum_burden_form_confirmed`: `c1_reference` is the sole Pareto-frontier member.
- `sterbenz_dominated_by_alternative`: `c1_reference` is not on the Pareto frontier because at least one alternative strictly dominates it.
- `sterbenz_tied_with_alternatives`: `c1_reference` is on the frontier but is not the sole frontier member.
- `sterbenz_audit_indeterminate`: the comparison has inconsistent ordering, three or more required dimensions use unavailable-data sentinels, or the calibration control lands on the frontier.

Calibration rule: `c3_factored` is expected to be off the frontier. If `c3_factored` lands on the frontier, the headline is forced to `sterbenz_audit_indeterminate`.

The full-grid burden vectors and the `x > 0.5` region comparison are supplementary. They are recorded for the region-swap finding but do not determine the headline.
