# Task 017c Summary - Multi-precision Theorem 2 Validation

## Scope

Task 017c added eval-layer multi-precision wrappers, unit-roundoff utilities,
linear-fit/bootstrap utilities, and a four-fixture precision campaign for
Theorem 2. The campaign covers F1-F4 as load-bearing paths and reports
`P_compound_split` and `P_sign_c` as supplementary F5+ fits. It did not modify
`typed_finite_difference`, substrate primitives, runtime statuses, manifests, or
law-library terms.

## Pre-registration

- Commit: `77dbd5a Task 017c pre-registration: Theorem 2 multi-precision validation predictions`
- File: `Build_Docs/Reports/task017c_multi_precision_theorem2/pre_registration.md`
- Status: byte-identical to the pre-registration commit at completion.

## Platform Report

`numpy.float128` is meaningfully distinct from `numpy.float64` on this host.

| Type | eps | bits | precision | tiny |
| --- | ---: | ---: | ---: | ---: |
| `float64` | `2.220446049250313e-16` | 64 | 15 | `2.2250738585072014e-308` |
| `float128` | `1.084202172485504434e-19` | 128 | 18 | `3.3621031431120935063e-4932` |

## Precision Battery

| Fixture | Executed precisions |
| --- | --- |
| `schwarzschild` | `float32`, `float64`, `float128`, `decimal_50`, `decimal_100`, `decimal_200` |
| `sr` | `float32`, `float64`, `float128`, `decimal_50`, `decimal_100`, `decimal_200` |
| `pure_algebraic` | `float32`, `float64`, `float128`, `decimal_50`, `decimal_100`, `decimal_200` |
| `cbrt_chain` | `float32`, `float64`, `float128`; Decimal rows marked `out_of_scope_by_design` |

## Per-fixture Per-path Fits

Regular-region fit for `C_p,k = a_k + b_k * u_p`.

| Fixture | Path | a_k CI | b_k CI | R2 | a_k CI includes 0? |
| --- | --- | --- | --- | ---: | --- |
| `schwarzschild` | F1 | `[-4.1077592267653366e-19, 9.286624925467283e-18]` | `[1.199712364613778e-41, 0.17284289159101582]` | 1.0 | Y |
| `schwarzschild` | F2 | `[-1.1525612859577966e-21, 8.570678969019874e-18]` | `[1.181138978153836e-101, 0.23145502407096058]` | 1.0 | Y |
| `schwarzschild` | F3 | `[0.0, 0.0]` | `[0.0, 0.0]` | 1.0 | Y |
| `schwarzschild` | F4 | `[-1.0760879017073154e-17, 5.1410066452106294e-17]` | `[7.810023646615227e-41, 1.0876423820808514]` | 1.0 | Y |
| `sr` | F1 | `[-1.099592531043776e-24, 1.9100225241640074e-17]` | `[2.0567417771331635e-101, 0.24924858690466786]` | 1.0 | Y |
| `sr` | F2 | `[-1.0106136704327782e-24, 2.6011889185449298e-17]` | `[3.4705280419690276e-101, 0.3825460263964471]` | 1.0 | Y |
| `sr` | F3 | `[0.0, 0.0]` | `[0.0, 0.0]` | 1.0 | Y |
| `sr` | F4 | `[-1.4612075039412093e-20, 1.4136432317976029e-16]` | `[4.362038703821367e-41, 1.0737639309908809]` | 1.0 | Y |
| `pure_algebraic` | F1 | `[-3.8351891896748484e-22, 1.0521668169838276e-17]` | `[4.058963392730887e-101, 0.28291099494431743]` | 1.0 | Y |
| `pure_algebraic` | F2 | `[-1.1832835287126046e-20, 2.0195147640539285e-17]` | `[2.727537910596299e-101, 0.3638034361837702]` | 1.0 | Y |
| `pure_algebraic` | F3 | `[0.0, 0.0]` | `[0.0, 0.0]` | 1.0 | Y |
| `pure_algebraic` | F4 | `[-4.020378688677416e-18, 2.0657338994764623e-17]` | `[1.4262256339916904e-71, 0.6183469401380516]` | 1.0 | Y |
| `cbrt_chain` | F1 | `[5.1423865152861276e-21, 5.797257633155526e-17]` | `[1.0742181190827827e-33, 0.365339725191255]` | 1.0 | N |
| `cbrt_chain` | F2 | `[-3.988801097377092e-21, 6.021687119447635e-17]` | `[1.1156893523159024e-33, 0.43723731445002]` | 1.0 | Y |
| `cbrt_chain` | F3 | `[0.0, 0.0]` | `[0.0, 0.0]` | 1.0 | Y |
| `cbrt_chain` | F4 | `[-3.647380859525672e-20, 5.214364699067244e-17]` | `[9.657935288719901e-34, 0.6724625483591272]` | 1.0 | Y |

## Sterbenz-region F2 Fits

| Fixture | F2 b_k CI regular region | F2 b_k CI Sterbenz region | Vanishing match? |
| --- | --- | --- | --- |
| `schwarzschild` | `[1.181138978153836e-101, 0.23145502407096058]` | `[4.948649853278049e-41, 0.6652067322885007]` | N |
| `sr` | `[3.4705280419690276e-101, 0.3825460263964471]` | `[6.544809797316893e-41, 0.7380586106951521]` | N |
| `pure_algebraic` | `[2.727537910596299e-101, 0.3638034361837702]` | `[5.511685706838241e-41, 0.7378477001220938]` | N |
| `cbrt_chain` | `[1.1156893523159024e-33, 0.43723731445002]` | `[2.629608090331026e-33, 0.9899903988708335]` | N |

## Sub-claim Results

| Sub-claim | Pre-registered threshold | Observed | Match? |
| --- | --- | --- | --- |
| Regular-region R2 | R2 >= 0.98 | all regular-region fits passed | Y |
| Intercept CI includes zero | all regular-region a_k CIs include 0 | cbrt F1 CI excludes zero | N |
| Slope structure | F1/F2/F4 slopes distinguish; F3 slope includes zero | F3 passed; core slopes were not fully distinguished in any fixture | N |
| Sterbenz-region F2 b_k vanishing | F2 Sterbenz-region b_k CI includes zero | all four F2 Sterbenz-region CIs excluded zero | N |

## F5+ Supplementary Fits

| Fixture | Path | a_k | b_k | R2 | a_k CI includes 0? |
| --- | --- | ---: | ---: | ---: | --- |
| `schwarzschild` | `P_compound_split` | `-4.596029916032691e-22` | `0.23145502407094903` | 1.0 | Y |
| `schwarzschild` | `P_sign_c` | `-4.596029916032691e-22` | `0.23145502407094903` | 1.0 | Y |
| `sr` | `P_compound_split` | `1.909369805507599e-18` | `0.38254602636441326` | 1.0 | Y |
| `sr` | `P_sign_c` | `1.909369805507599e-18` | `0.38254602636441326` | 1.0 | Y |
| `pure_algebraic` | `P_compound_split` | `-3.943603038900057e-21` | `0.3638034361836378` | 1.0 | Y |
| `pure_algebraic` | `P_sign_c` | `-3.943603038900057e-21` | `0.3638034361836378` | 1.0 | Y |
| `cbrt_chain` | `P_compound_split` | `2.0884190554005388e-17` | `0.4372373140995743` | 1.0 | Y |
| `cbrt_chain` | `P_sign_c` | `2.0884190554005388e-17` | `0.4372373140995743` | 1.0 | Y |

## Headline Classification

Headline: `theorem2_partial`.

The regular-region linear-in-`u_p` model fit passed across all load-bearing
fixture/path rows, and F3 behaved as a calibration zero. The full theorem-level
claim did not validate as pre-registered because cbrt F1's intercept CI excluded
zero, the F1/F2/F4 slope CIs did not fully separate by path, and F2's
Sterbenz-region slope CI excluded zero in every fixture. The result supports a
linear precision-axis model, but not the full pre-registered separation and
Sterbenz-vanishing structure.

## Tests

- Baseline at task start: `975a3fb`, 582 tests collected and passing.
- Pre-registration commit: `77dbd5a`.
- Added tests: 40 in `tests/test_task017c_multi_precision_theorem2.py`.
- Post-task collection: 622 tests collected.
- Focused task suite: `python -m pytest -q tests/test_task017c_multi_precision_theorem2.py` passed.
- Full suite: `python -m pytest -q tests/` passed.

## Byte-stability

- `precision_aggregate.json`: repeat run diff produced no output.
- `f5_plus_supplementary.json`: repeat run diff produced no output.
- `headline_classification.md`: repeat generation diff produced no output.
- `pre_registration.md`: diff against `77dbd5a` produced no output.

## Discipline Gates

- F3 sentinel held at every precision in every fixture.
- `layer_manifest.json` and `LAYER_MANIFEST.md` were unchanged.
- `typed_finite_difference.py` was byte-identical to the pre-registration commit.
- No banned interpretive terms were present in new Task 017c files.
- No `scipy`, `sympy`, `mpmath`, `statsmodels`, `numpy.special`, `numpy.random`, `math.cbrt`, or cube-root-by-fractional-power pattern was introduced.
- Decimal precision changes are confined to `localcontext()` blocks.

## Files Changed

- `Build_Docs/Agent_tasks/Completed/codex_task017c_multi_precision_theorem2.md`
- `Build_Docs/Reports/task017c_multi_precision_theorem2/pre_registration.md`
- `Build_Docs/Reports/task017c_multi_precision_theorem2/precision_aggregate.json`
- `Build_Docs/Reports/task017c_multi_precision_theorem2/f5_plus_supplementary.json`
- `Build_Docs/Reports/task017c_multi_precision_theorem2/headline_classification.md`
- `Build_Docs/Reports/task017c_summary.md`
- `src/lloyd_v4/evals/precision/__init__.py`
- `src/lloyd_v4/evals/precision/unit_roundoff.py`
- `src/lloyd_v4/evals/precision/precision_bound_fixtures.py`
- `src/lloyd_v4/evals/precision/linear_fit.py`
- `src/lloyd_v4/evals/precision/multi_precision_campaign.py`
- `tests/test_task017c_multi_precision_theorem2.py`

## Forward Observations

The precision-axis model is very strong as a linear empirical description over
the executed battery: every regular-region R2 is 1.0 in the aggregate. The
pre-registered mechanism-level interpretation is narrower: path slopes do not
separate cleanly enough under the bootstrap CI criterion, and the F2
Sterbenz-region slope remains positive rather than vanishing. The supplementary
F5+ paths mirror F2-like behavior across fixtures, which supports keeping them
as useful observed paths while leaving them non-load-bearing for Theorem 2.
