# Task 029 Summary - Path-Basis Rank Clustering

## Scope

Task 029 generated a closed elementary-rewrite path catalog, computed
six-dimensional path signatures, built pairwise signature-distance matrices, ran
pure stdlib single-linkage clustering, and compared basis rank across
Schwarzschild, SR, and pure algebraic fixtures.

No V4 primitive, runtime status enum, manifest entry, transition rule, solver
behavior, or Task 025 law-library term was added.

## Baseline

- Pre-task HEAD: `6a5be55 Task 028: Conditional masks, joint signed-lattice, and pure algebraic four-form control`.
- Pre-task suite: 508 tests passing.

## Test Results

- Added tests: 25 in `tests/test_task029_path_basis_rank_clustering.py`.
- Post-task collection/full suite: 533 tests passing.

## Files Changed

- `src/lloyd_v4/evals/path_catalog.py`
- `src/lloyd_v4/evals/path_signature.py`
- `src/lloyd_v4/evals/path_distance.py`
- `src/lloyd_v4/evals/path_clustering.py`
- `src/lloyd_v4/evals/basis_rank_comparison.py`
- `tests/test_task029_path_basis_rank_clustering.py`
- `Build_Docs/Reports/task029_path_basis_rank_clustering/*`
- `Build_Docs/Reports/task029_summary.md`

## Candidate Catalog

Each fixture has exactly 15 paths covering all seven declared rewrite classes:
`canonical`, `sign_reordering`, `factored_f_routing`,
`difference_of_squares`, `scaled_identity`, `distributive_rewrite`, and
`compound_routing`.

| Fixture | Path count | Rewrite classes covered |
| --- | ---: | ---: |
| Schwarzschild | 15 | 7 |
| SR | 15 | 7 |
| Pure algebraic | 15 | 7 |

The canonical F1, F2, F3, and F4 paths recover the existing four-form values
exactly at all 137 grid cells and all three precision routes. F3 is exactly
silent across all three fixtures and all three precision routes.

## Signature Summary

Table columns: `nonzero` is `float32/float64/decimal_50`; `bins` is the number
of signed-lattice histogram bins; `alpha` is the five characteristic alpha
statuses; `env` is `(concentration, dynamic_range, small_region, large_region)`.

| Fixture | Path | Rewrite class | nonzero | bins | alpha | env |
| --- | --- | --- | --- | ---: | --- | --- |
| Schwarzschild | F1 | canonical | 59/69/55 | 6 | zero zero zero zero zero | 0.609, 2.408, 0.333, 0.319 |
| Schwarzschild | F2 | canonical | 25/28/12 | 18 | insufficient insufficient zero negative zero | 0.646, 0.778, 0.000, 1.000 |
| Schwarzschild | F3 | canonical | 0/0/0 | 0 | insufficient insufficient insufficient insufficient insufficient | 0.000, 0.000, 0.000, 0.000 |
| Schwarzschild | F4 | canonical | 80/92/62 | 73 | zero zero zero insufficient insufficient | 0.325, 1.447, 0.478, 0.109 |
| Schwarzschild | P_sign_a | sign_reordering | 59/69/55 | 6 | zero zero zero zero zero | 0.609, 2.408, 0.333, 0.319 |
| Schwarzschild | P_sign_b | sign_reordering | 25/28/12 | 18 | insufficient insufficient zero negative zero | 0.646, 0.778, 0.000, 1.000 |
| Schwarzschild | P_sign_c | sign_reordering | 15/16/12 | 10 | insufficient insufficient zero zero zero | 0.812, 0.000, 0.000, 1.000 |
| Schwarzschild | P_factor_b | factored_f_routing | 0/0/0 | 0 | insufficient insufficient insufficient insufficient insufficient | 0.000, 0.000, 0.000, 0.000 |
| Schwarzschild | P_diff_squares | difference_of_squares | 0/0/0 | 0 | insufficient insufficient insufficient insufficient insufficient | 0.000, 0.000, 0.000, 0.000 |
| Schwarzschild | P_scaled_2 | scaled_identity | 59/69/31 | 6 | zero zero zero zero zero | 0.609, 2.408, 0.333, 0.319 |
| Schwarzschild | P_scaled_half | scaled_identity | 59/69/34 | 6 | zero zero zero zero zero | 0.609, 2.408, 0.333, 0.319 |
| Schwarzschild | P_distrib_mul | distributive_rewrite | 59/70/55 | 6 | zero zero zero zero zero | 0.605, 2.408, 0.329, 0.314 |
| Schwarzschild | P_distrib_sqrt_mul | distributive_rewrite | 0/1/0 | 1 | insufficient insufficient insufficient insufficient insufficient | 1.000, 0.000, 0.000, 0.000 |
| Schwarzschild | P_compound_split | compound_routing | 15/16/12 | 10 | insufficient insufficient zero zero zero | 0.812, 0.000, 0.000, 1.000 |
| Schwarzschild | P_compound_zero | compound_routing | 59/69/55 | 6 | zero zero zero zero zero | 0.609, 2.408, 0.333, 0.319 |
| SR | F1 | canonical | 28/34/21 | 7 | zero insufficient insufficient insufficient insufficient | 0.543, 0.301, 0.559, 0.000 |
| SR | F2 | canonical | 92/95/59 | 22 | zero zero zero insufficient insufficient | 0.263, 2.186, 0.474, 0.116 |
| SR | F3 | canonical | 0/0/0 | 0 | insufficient insufficient insufficient insufficient insufficient | 0.000, 0.000, 0.000, 0.000 |
| SR | F4 | canonical | 42/27/83 | 22 | zero insufficient insufficient insufficient zero | 0.752, 1.806, 0.222, 0.519 |
| SR | P_sign_a | sign_reordering | 64/75/44 | 6 | zero insufficient zero fractional zero | 0.231, 3.612, 0.320, 0.400 |
| SR | P_sign_b | sign_reordering | 92/95/59 | 22 | zero zero zero insufficient insufficient | 0.263, 2.186, 0.474, 0.116 |
| SR | P_sign_c | sign_reordering | 52/55/38 | 10 | zero insufficient zero insufficient insufficient | 0.236, 0.000, 0.436, 0.182 |
| SR | P_factor_b | factored_f_routing | 0/0/0 | 0 | insufficient insufficient insufficient insufficient insufficient | 0.000, 0.000, 0.000, 0.000 |
| SR | P_diff_squares | difference_of_squares | 0/0/0 | 0 | insufficient insufficient insufficient insufficient insufficient | 0.000, 0.000, 0.000, 0.000 |
| SR | P_scaled_2 | scaled_identity | 64/75/11 | 6 | zero insufficient zero fractional zero | 0.231, 3.612, 0.320, 0.400 |
| SR | P_scaled_half | scaled_identity | 64/75/20 | 6 | zero insufficient zero fractional zero | 0.231, 3.612, 0.320, 0.400 |
| SR | P_distrib_mul | distributive_rewrite | 64/76/45 | 6 | zero insufficient zero fractional zero | 0.229, 3.612, 0.316, 0.408 |
| SR | P_distrib_sqrt_mul | distributive_rewrite | 0/1/1 | 2 | insufficient insufficient insufficient insufficient insufficient | 1.000, 0.000, 0.000, 1.000 |
| SR | P_compound_split | compound_routing | 52/55/38 | 10 | zero insufficient zero insufficient insufficient | 0.236, 0.000, 0.436, 0.182 |
| SR | P_compound_zero | compound_routing | 64/75/44 | 6 | zero insufficient zero fractional zero | 0.231, 3.612, 0.320, 0.400 |
| Pure algebraic | F1 | canonical | 65/70/45 | 7 | zero zero zero zero zero | 0.302, 1.505, 0.271, 0.386 |
| Pure algebraic | F2 | canonical | 60/64/128 | 21 | zero zero insufficient insufficient insufficient | 0.320, 1.380, 0.594, 0.031 |
| Pure algebraic | F3 | canonical | 0/0/0 | 0 | insufficient insufficient insufficient insufficient insufficient | 0.000, 0.000, 0.000, 0.000 |
| Pure algebraic | F4 | canonical | 39/40/51 | 25 | insufficient insufficient insufficient insufficient cancellation | 0.383, 0.544, 0.250, 0.475 |
| Pure algebraic | P_sign_a | sign_reordering | 65/70/45 | 7 | zero zero zero zero zero | 0.302, 1.505, 0.271, 0.386 |
| Pure algebraic | P_sign_b | sign_reordering | 60/64/128 | 21 | zero zero insufficient insufficient insufficient | 0.320, 1.380, 0.594, 0.031 |
| Pure algebraic | P_sign_c | sign_reordering | 37/39/38 | 10 | zero zero insufficient insufficient insufficient | 0.333, 0.000, 0.487, 0.051 |
| Pure algebraic | P_factor_b | factored_f_routing | 0/0/8 | 2 | insufficient insufficient insufficient insufficient insufficient | 0.000, 0.000, 0.000, 0.000 |
| Pure algebraic | P_diff_squares | difference_of_squares | 0/0/0 | 0 | insufficient insufficient insufficient insufficient insufficient | 0.000, 0.000, 0.000, 0.000 |
| Pure algebraic | P_scaled_2 | scaled_identity | 65/70/16 | 7 | zero zero zero zero zero | 0.302, 1.505, 0.271, 0.386 |
| Pure algebraic | P_scaled_half | scaled_identity | 65/70/24 | 7 | zero zero zero zero zero | 0.302, 1.505, 0.271, 0.386 |
| Pure algebraic | P_distrib_mul | distributive_rewrite | 65/70/45 | 7 | zero zero zero zero zero | 0.302, 1.505, 0.271, 0.386 |
| Pure algebraic | P_distrib_sqrt_mul | distributive_rewrite | 0/0/0 | 0 | insufficient insufficient insufficient insufficient insufficient | 0.000, 0.000, 0.000, 0.000 |
| Pure algebraic | P_compound_split | compound_routing | 37/39/38 | 10 | zero zero insufficient insufficient insufficient | 0.333, 0.000, 0.487, 0.051 |
| Pure algebraic | P_compound_zero | compound_routing | 65/70/45 | 7 | zero zero zero zero zero | 0.302, 1.505, 0.271, 0.386 |

Full signatures, including zero-mask fingerprints and co-fire polarity tuples,
are serialized in `path_signatures.json`.

## Pairwise Distances

Each fixture has a 15 by 15 pairwise matrix in
`pairwise_distance_matrices.json`. Matrix diagonals are exactly zero and every
matrix is symmetric. The composite distance is the unweighted mean of the six
normalized dimension distances.

F3 self-check distances were all above the required separation gate:

| Fixture | F3-F1 | F3-F2 | F3-F4 |
| --- | ---: | ---: | ---: |
| Schwarzschild | 0.907543 | 0.744864 | 0.825070 |
| SR | 0.636627 | 0.866423 | 0.794972 |
| Pure algebraic | 0.873488 | 0.796894 | 0.657274 |

## Basis Rank Clustering

Sensitivity sweep:

| Fixture | Cut | Rank | F1-F4 self-consistent | F5+ candidates |
| --- | ---: | ---: | --- | --- |
| Schwarzschild | 0.05 | 8 | yes | P_compound_split, P_sign_c, P_distrib_sqrt_mul, P_scaled_2, P_scaled_half |
| Schwarzschild | 0.10 | 8 | yes | P_compound_split, P_sign_c, P_distrib_sqrt_mul, P_scaled_2, P_scaled_half |
| Schwarzschild | 0.15 | 7 | yes | P_compound_split, P_sign_c, P_distrib_sqrt_mul, P_scaled_2, P_scaled_half |
| Schwarzschild | 0.20 | 6 | yes | P_compound_split, P_sign_c, P_distrib_sqrt_mul |
| SR | 0.05 | 9 | yes | P_compound_split, P_sign_c, P_compound_zero, P_distrib_mul, P_sign_a, P_distrib_sqrt_mul, P_scaled_2, P_scaled_half |
| SR | 0.10 | 9 | yes | P_compound_split, P_sign_c, P_compound_zero, P_distrib_mul, P_sign_a, P_distrib_sqrt_mul, P_scaled_2, P_scaled_half |
| SR | 0.15 | 9 | yes | P_compound_split, P_sign_c, P_compound_zero, P_distrib_mul, P_sign_a, P_distrib_sqrt_mul, P_scaled_2, P_scaled_half |
| SR | 0.20 | 7 | yes | P_compound_split, P_sign_c, P_compound_zero, P_distrib_mul, P_scaled_2, P_scaled_half, P_sign_a, P_distrib_sqrt_mul |
| Pure algebraic | 0.05 | 8 | yes | P_compound_split, P_sign_c, P_factor_b, P_scaled_2, P_scaled_half |
| Pure algebraic | 0.10 | 8 | yes | P_compound_split, P_sign_c, P_factor_b, P_scaled_2, P_scaled_half |
| Pure algebraic | 0.15 | 8 | yes | P_compound_split, P_sign_c, P_factor_b, P_scaled_2, P_scaled_half |
| Pure algebraic | 0.20 | 6 | yes | P_compound_split, P_sign_c, P_factor_b |

At the methodology gate cut of 0.10, F1, F2, F3, and F4 are in distinct
clusters for all three fixtures. The methodology gate passed.

## Three-Fixture Comparison

At cut 0.10:

| Fixture | Basis rank | F1-F4 self-consistent | F5+ candidates | F5+ rewrite classes |
| --- | ---: | --- | --- | --- |
| Schwarzschild | 8 | yes | P_compound_split, P_sign_c, P_distrib_sqrt_mul, P_scaled_2, P_scaled_half | compound_routing, distributive_rewrite, scaled_identity, sign_reordering |
| SR | 9 | yes | P_compound_split, P_sign_c, P_compound_zero, P_distrib_mul, P_sign_a, P_distrib_sqrt_mul, P_scaled_2, P_scaled_half | compound_routing, distributive_rewrite, scaled_identity, sign_reordering |
| Pure algebraic | 8 | yes | P_compound_split, P_sign_c, P_factor_b, P_scaled_2, P_scaled_half | compound_routing, factored_f_routing, scaled_identity, sign_reordering |

## Headline Finding

`basis_rank_divergent`.

F1-F4 self-consistency holds, so the methodology is not compromised. However,
the basis rank at cut 0.10 is not invariant across fixtures:
Schwarzschild rank 8, SR rank 9, pure algebraic rank 8. F5+ candidate sets are
present in every fixture, but they do not have the same rewrite-class support:
pure algebraic exposes `factored_f_routing`, while Schwarzschild and SR expose
`distributive_rewrite`; SR also separates an additional sign/distributive group.

## Honest Observations

- F1-F4 are not a complete elementary-rewrite basis under this signature metric.
- The result is not a clean rank-5 invariant. Multiple non-canonical clusters
  appear at cut 0.10.
- `P_diff_squares` clusters with the F3-silent family in all fixtures.
- Scaled identities separate from F1 even when their envelope shapes match,
  mainly through precision-scaling and lattice differences.
- `P_factor_b` is silent in Schwarzschild and SR but fires on decimal-50 in pure
  algebraic, producing a pure-algebraic F5+ candidate.

## Limits

- The catalog is the fixed 15-path elementary-rewrite family only.
- No nested rewrite expansion, long-double route, platform FMA axis, or alternate
  root-definition family was tested.
- F5+ candidates are typed clustering evidence only; no substrate promotion was
  performed.

## Forward References

Task 030 should use operation-level Sterbenz annotation against the observed
basis-rank divergence. Substrate promotion of a typed path-signature observable
should be considered only after a derivable structural law explains the
cross-fixture cluster assignments.

## Verification

- `git log -1 --oneline`
- `python -m pytest -q tests/`
- `PYTHONPATH=src python -m lloyd_v4.evals.path_catalog`
- `PYTHONPATH=src python -m lloyd_v4.evals.path_catalog --output /tmp/path_catalog_repeat.json`
- `diff Build_Docs/Reports/task029_path_basis_rank_clustering/candidate_path_catalog.json /tmp/path_catalog_repeat.json`
- `PYTHONPATH=src python -m lloyd_v4.evals.path_signature`
- `PYTHONPATH=src python -m lloyd_v4.evals.path_signature --output /tmp/path_signatures_repeat.json`
- `diff Build_Docs/Reports/task029_path_basis_rank_clustering/path_signatures.json /tmp/path_signatures_repeat.json`
- `PYTHONPATH=src python -m lloyd_v4.evals.path_distance`
- `PYTHONPATH=src python -m lloyd_v4.evals.path_distance --output /tmp/pairwise_distances_repeat.json`
- `diff Build_Docs/Reports/task029_path_basis_rank_clustering/pairwise_distance_matrices.json /tmp/pairwise_distances_repeat.json`
- `PYTHONPATH=src python -m lloyd_v4.evals.path_clustering`
- `PYTHONPATH=src python -m lloyd_v4.evals.path_clustering --output /tmp/basis_rank_repeat.json`
- `diff Build_Docs/Reports/task029_path_basis_rank_clustering/basis_rank_clustering.json /tmp/basis_rank_repeat.json`
- `PYTHONPATH=src python -m lloyd_v4.evals.basis_rank_comparison`
- `PYTHONPATH=src python -m lloyd_v4.evals.basis_rank_comparison --output /tmp/basis_rank_comp_repeat.json`
- `diff Build_Docs/Reports/task029_path_basis_rank_clustering/basis_rank_comparison.json /tmp/basis_rank_comp_repeat.json`
- `python -m pytest -q tests/test_task029_path_basis_rank_clustering.py`
- `python -m pytest -q tests/`
- `python -m pytest -q tests/test_task001_source_purity.py`
- `python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py`
- `rg "numpy\\.random|np\\.random|scipy|sympy|mpmath|sklearn" src/lloyd_v4/evals/path_catalog.py src/lloyd_v4/evals/path_signature.py src/lloyd_v4/evals/path_distance.py src/lloyd_v4/evals/path_clustering.py src/lloyd_v4/evals/basis_rank_comparison.py`
