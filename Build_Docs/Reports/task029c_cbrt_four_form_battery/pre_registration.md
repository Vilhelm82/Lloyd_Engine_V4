# Task 029c Pre-registration - Cube-root Four-form Battery

This document records the Task 029c predictions before campaign execution. These
predictions are not to be edited after the pre-registration commit.

## Section A - Strong-cluster Invariants

Section A is load-bearing for the headline classification.

| Invariant | Prediction |
| --- | --- |
| F1||F2 grid-stable polarity coupling | 100% sign agreement, binomial p-value below 0.01, and all four perturbation grids have cofire count at least 10. |
| F3 identity silence | F3 is exactly 0.0 at every sampled cell and every perturbation grid. |
| F2 lattice character | F2 has non-integer lattice character. The observed grain is left to the campaign. |
| F4 lattice character | F4 has integer-lattice character. |
| Sterbenz boundary | Boundary at x = 1/2, with below-boundary density greater than above-boundary density. |

### Sterbenz Boundary Prediction

The cbrt fixture uses `f = 1 - x` and `R = cbrt(f)`, so `R**3 = f`. The
subtraction in F2 includes `R**3 - 1`; Sterbenz exactness is predicted when
`R**3 >= 1/2`, equivalently `1 - x >= 1/2`, so `x <= 1/2`. The predicted
boundary location is therefore x = 1/2, with higher F2 nonzero density below
the boundary than above it.

### Fixture Definition

The operand is x directly. The canonical grid is the same 137-point grid used by
the existing pure algebraic fixture:

```text
x_min = 0.01
x_max = 0.99
n = 137
```

The fixture definitions are:

```text
f_direct(x) = 1 - x
f_alt_routing(x) = (1 - x / 2) - x / 2
R(x) = numpy.cbrt(f_direct(x))
F1(x) = R(x)**3 - f_direct(x)
F2(x) = R(x)**3 - 1 + x
F3(x) = R(x) - numpy.cbrt(f_direct(x))
F4(x) = R(x) - numpy.cbrt(f_alt_routing(x))
```

## Section B - Refined F5+ Predictions

Section B is secondary and informative. It does not determine the headline.

| Path | Prediction | Rationale |
| --- | --- | --- |
| P_compound_split | present | Task 029b retained this path in the universal refined F5+ set. |
| P_sign_c | present | Task 029b retained this path in the universal refined F5+ set. |
| P_distrib_sqrt_mul | absent or attenuated | Task 029b aligned this path with sparse sqrt route-residual cells, so it is predicted not to appear as a strong cbrt cluster. |

Section B predictions must be reported with observed status, cofire rate, and
match or mismatch in the completion summary.

## Closing

The predictions in both sections are registered before campaign execution and
are not to be edited after this commit. The pre-registration commit hash is
recorded in `Build_Docs/Reports/task029c_summary.md`.
