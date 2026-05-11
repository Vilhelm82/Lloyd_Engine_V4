# Task 002 Summary

Task 002 implemented `StratifiedQuadraticRoots` as the second Layer 1 primitive.

## Files Created

- `src/lloyd_v4/primitives/stratified_quadratic_roots.py`
- `tests/test_task002_stratified_quadratic_roots.py`
- `tests/test_task002_quadratic_root_selection.py`
- `tests/test_task002_quadratic_root_serialization.py`
- `tests/test_task002_source_purity.py`
- `Build_Docs/Reports/task002/task002_summary.md`
- `Build_Docs/Reports/task002/stratified_quadratic_roots_status_table.md`
- `Build_Docs/Reports/task002/design_decisions.md`

## Files Modified

- `src/lloyd_v4/primitives/__init__.py`

## Behavior Summary

`stratified_quadratic_roots(a, b, c)` returns a typed root-state result for the real equation `a*x^2 + b*x + c = 0`. It preserves raw coefficients, discriminant evidence where applicable, branch-labeled projective root coordinates for selectable real-root strata, validity, conditioning, and provenance.

The primitive classifies exactly into:

- `two_real_roots`
- `repeated_root`
- `no_real_root`
- `linear_root`
- `constant_identity`
- `constant_no_solution`

`select_quadratic_root(result, branch)` is explicit and protocol-validated. It accepts only compatible branches for selectable statuses. Unsupported statuses or incompatible branch labels return typed refusals.

## Red Test Result

Command:

```text
python -m pytest tests/test_task002_stratified_quadratic_roots.py tests/test_task002_quadratic_root_selection.py tests/test_task002_quadratic_root_serialization.py tests/test_task002_source_purity.py -q
```

Result: failed during collection because `lloyd_v4.primitives.stratified_quadratic_roots` did not exist.

## Task 002 Test Slice

Command:

```text
python -m pytest tests/test_task002_stratified_quadratic_roots.py tests/test_task002_quadratic_root_selection.py tests/test_task002_quadratic_root_serialization.py tests/test_task002_source_purity.py -q
```

Result:

```text
.......................                                                  [100%]
```

## Full Suite

Command:

```text
python -m pytest tests -q
```

Result:

```text
..............................................                           [100%]
```

## Source Audits

Command:

```text
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|epsilon|eps" src -n
```

Result: no matches.

Command:

```text
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard" src/lloyd_v4/primitives src/lloyd_v4/core -n
```

Result: no matches.

Command:

```text
rg "disc_floor|discriminant_floor|clamp_discriminant|safe_sqrt|sqrt_guard|small_discriminant|tolerance|threshold" src/lloyd_v4/primitives src/lloyd_v4/core -n
```

Result: no matches.

Command:

```text
rg "import cmath|from cmath|complex\(" src/lloyd_v4/primitives/stratified_quadratic_roots.py -n
```

Result: no matches.

## Deviations

No V3 references, adapters, comparison fixtures, arrays, tensors, complex roots, alternate quadratic formulas, projection consumers, branch fingerprints, or metrology estimators were added.

One exactness test originally used a float expression that rounded away the intended nonzero discriminant. The test was corrected to use a representable small positive discriminant.

## Task 003 Readiness

Task 003 is ready to scope as `ProjectionResultV4 and exact projection protocol`.
