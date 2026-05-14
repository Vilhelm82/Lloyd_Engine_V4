# Task 033 Pre-Registration - Schwarzschild-Cbrt Transformed n=3

This document was written before Task 033 fixture source, measurement outputs, headline output, or summary artifacts were created. It locks the fixture construction, hypothesis table, headline mapping, and supplementary observations.

## Section A - Fixture Construction

The fixture uses the existing Schwarzschild operand grid: 137 `r` values on `[2.005, 10.0]`, reusing `schwarzschild_four_form.sweep_r_values`.

The direct transformed operand is:

- `f_direct(r) = 1 - 2 / r`

The alternate transformed operand is:

- `f_alt(r) = (r - 2) / r`

The radical is:

- `R(r) = numpy.cbrt(1 - 2 / r)`

The four forms are:

| Form | Definition |
| --- | --- |
| `F1` | `R * R * R - f_direct(r)` |
| `F2` | `R * R * R - 1 + 2 / r` |
| `F3` | `R - numpy.cbrt(f_direct(r))` |
| `F4` | `R - numpy.cbrt(f_alt(r))` |

The float32 fixture converts input and intermediate values through `numpy.float32`. The float64 fixture uses Python floats with `numpy.cbrt`.

## Section B - Hypotheses and Pre-Registered Outcomes

| Hypothesis | Predicted F2 grain | Source |
| --- | ---: | --- |
| H2: transformed operand gives `0.5`, independent of `n` | `0.5` | transformed n=2 fixtures |
| H2-refined: transformed effect is n=2-specific | `0.25` | identity n=3 and n=4 fixtures |
| Indeterminate | any other value | neither hypothesis predicts |

Headline mapping:

- `transformed_operand_law_supported_at_n3` if observed F2 `level_integer_residual_max` at float64 is exactly `0.5`.
- `transformed_operand_law_refuted_at_n3` if observed F2 `level_integer_residual_max` at float64 is exactly `0.25`.
- `lattice_grain_indeterminate_at_n3` for any other observed value.

The equality comparison is exact because the observed lattice grain is a typed dyadic rational from the float64 ULP-level lattice campaign.

## Section C - Supplementary Observations

These observations are reported but do not determine the headline:

- F1, F3, and F4 lattice classifications. Expected: F3 is `lattice_empty`; F1 and F4 are `lattice_integer`.
- Polarity grid stability for `F1_F2` at float64. Expected: `grid_stable_polarity_coupling`.
- Sterbenz boundary at `r = 4.0`. Expected directional observation: above-boundary F2 nonzero density is higher than below-boundary density, matching the n=2 Schwarzschild fixture.
- Boundary location comparison: the boundary is expected to stay at `r = 4.0`, showing operand-determined rather than radical-degree-determined placement.
