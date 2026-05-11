# Task 001 Summary

Task 001 implemented `ProjectiveRatio(n, d)` as the first typed primitive.

## Created

- `src/lloyd_v4/primitives/projective_ratio.py`
- Task 001 tests for projective strata, scalarization, serialization, and source purity
- Task 001 reports under `Build_Docs/Reports/task001/`

## Modified

- `src/lloyd_v4/primitives/__init__.py` now exports ProjectiveRatio APIs.
- `src/lloyd_v4/core/errors.py` had one error docstring tightened so the Task 001 source audit can distinguish actual implementation terminology from M0 prose.

## Behavior

`projective_ratio(n, d)` preserves the raw projective coordinates `[n:d]` and classifies the exact stratum without dividing by `d`.

`scalarize_projective_ratio(result)` is explicit. It succeeds only for `finite_ratio` and `signed_zero`. It returns a typed refusal for `infinite_direction` and `indeterminate`.

## Tests Run

Task 001 red run:

```text
python -m pytest tests/test_task001_projective_ratio.py tests/test_task001_projective_ratio_scalarization.py tests/test_task001_projective_ratio_serialization.py tests/test_task001_source_purity.py -q
```

Result: failed during collection because `lloyd_v4.primitives.projective_ratio` did not exist.

Task 001 implementation slice:

```text
python -m pytest tests/test_task001_projective_ratio.py tests/test_task001_projective_ratio_scalarization.py tests/test_task001_projective_ratio_serialization.py tests/test_task001_source_purity.py -q
```

Result:

```text
..............                                                           [100%]
```

Final full-suite verification:

```text
python -m pytest tests -q
```

Result:

```text
.......................                                                  [100%]
```

Source-only forbidden-term audit:

```text
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|epsilon|eps" src -n
```

Result: no matches.

Denominator-correction audit:

```text
rg "safe_divide|safe_denominator|denominator_floor|small_denominator|rescue|guard" src/lloyd_v4/primitives src/lloyd_v4/core -n
```

Result: no matches.

## Deviations

No domain consumers, V3 fixtures, adapters, torch/CUDA dependencies, or StratifiedQuadraticRoots implementation were added.

## Task 002 Readiness

Task 002 is ready to scope as `StratifiedQuadraticRoots`.
