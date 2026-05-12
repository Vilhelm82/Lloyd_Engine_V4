# Task 029 Report Bundle

This directory contains the Task 029 path-basis rank exploration artifacts.

## Files

- `candidate_path_catalog.json`: deterministic 45-path catalog, 15 paths per
  fixture.
- `candidate_path_table.csv`: flat catalog table.
- `path_signatures.json`: six-dimensional path signatures for every candidate.
- `signature_summary_table.csv`: compact per-path signature summary.
- `pairwise_distance_matrices.json`: per-fixture 15 by 15 composite distance
  matrices.
- `basis_rank_clustering.json`: single-linkage clustering assignments at cut
  values 0.05, 0.10, 0.15, and 0.20.
- `cluster_assignment_table.csv`: flat cluster assignment table.
- `sensitivity_threshold_table.csv`: flat basis-rank sensitivity table.
- `basis_rank_comparison.json`: three-fixture comparison at cut 0.10.

## Headline

`basis_rank_divergent`.

At cut 0.10, F1-F4 self-consistency holds in all three fixtures, so the
methodology gate passed. The resulting basis ranks diverge:

- Schwarzschild: rank 8
- SR: rank 9
- Pure algebraic: rank 8

F5+ candidate sets are present in all three fixtures, but they are not identical
across fixtures.

## Reproduction

From the repository root:

```bash
PYTHONPATH=src python -m lloyd_v4.evals.path_catalog
PYTHONPATH=src python -m lloyd_v4.evals.path_signature
PYTHONPATH=src python -m lloyd_v4.evals.path_distance
PYTHONPATH=src python -m lloyd_v4.evals.path_clustering
PYTHONPATH=src python -m lloyd_v4.evals.basis_rank_comparison
```
