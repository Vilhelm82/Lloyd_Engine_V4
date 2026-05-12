# Task 029b Methodology Refinement

This directory contains the Task 029b additive methodology-refinement campaign.
It leaves Task 029 outputs and modules unchanged, then adds parallel evidence for
three questions:

1. Whether a value-relative signed-lattice metric changes the F5+ candidates.
2. Whether decimal-50 scaled-form divergence is a Decimal-context artefact or a
   substrate-level finding.
3. Whether the `P_distrib_sqrt_mul` candidate is explained by a sparse sqrt route
   residual.

## Artifacts

- `scale_invariant_signatures.json`: Task 029 path signatures recomputed with
  value-relative signed-lattice levels.
- `scale_invariant_clustering.json`: clustering sweep over the scale-invariant
  signatures.
- `scale_invariant_vs_original_comparison.json`: cut=0.10 comparison between the
  original Task 029 clustering and the scale-invariant variant.
- `decimal_scaled_form_audit.json`: per-fixture audit of decimal-50 divergence
  between F1 and `P_scaled_2`.
- `decimal_scaled_form_audit_table.csv`: compact decimal-audit summary.
- `sqrt_roundtrip_residual.json`: per-fixture characterization of the sqrt
  route-difference residual matching `P_distrib_sqrt_mul`.
- `sqrt_roundtrip_summary_table.csv`: compact sqrt-residual summary.
- `refined_f5_report.json`: composed Task 029b conclusion and refined F5+ sets.
- `refined_f5_summary_table.csv`: compact refined-F5 summary.

## Headline

The refined methodology is not compromised: F1-F4 self-consistency holds under
the value-relative lattice metric at cut=0.10 for all three fixtures.

The headline classification is `mixed_resolution`. The cross-fixture universal
refined F5+ set is:

- `P_compound_split`
- `P_sign_c`

## Definition Note

The sqrt artifact reported here is the route residual expressed by the frozen
Task 029 catalog path `P_distrib_sqrt_mul`:

```text
(sqrt(f))**2 - sqrt(f) * sqrt(f)
```

This is the residual whose non-zero cells align with `P_distrib_sqrt_mul` firing.
