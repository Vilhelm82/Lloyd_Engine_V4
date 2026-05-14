# Task 034 Pre-Registration - Schwarzschild-Quartic Transformed n=4

This document was written before Task 034 fixture source, measurement outputs, headline output, or summary artifacts were created. It locks the fixture construction, hypothesis table, headline mapping, and supplementary observations.

## Section A - Fixture Construction

The fixture uses the existing Schwarzschild operand grid: 137 `r` values on `[2.005, 10.0]`, reusing `schwarzschild_four_form.sweep_r_values`.

The direct transformed operand is:

- `f_direct(r) = 1 - 2 / r`

The alternate transformed operand is:

- `f_alt(r) = (r - 2) / r`

The radical is:

- `R(r) = numpy.sqrt(numpy.sqrt(1 - 2 / r))`

The four forms are:

| Form | Definition |
| --- | --- |
| `F1` | `(R * R) * (R * R) - f_direct(r)` |
| `F2` | `(R * R) * (R * R) - 1 + 2 / r` |
| `F3` | `R - numpy.sqrt(numpy.sqrt(f_direct(r)))` |
| `F4` | `R - numpy.sqrt(numpy.sqrt(f_alt(r)))` |

The float32 fixture converts input and intermediate values through `numpy.float32`. The float64 fixture uses Python floats with two `numpy.sqrt` invocations.

## Section B - Hypotheses and Pre-Registered Outcomes

| Hypothesis | Predicted F2 grain | Source |
| --- | ---: | --- |
| H3: compound law, transformed gives `2^(1-n)` while identity gives `0.25` | `0.125` | six existing fixture data points |
| H3-converges: transformed decay floors at identity baseline | `0.25` | alternative convergence reading |
| H_rounding: rounding-event count dominates | `0.0625` | two-rounding composed sqrt-of-sqrt caveat |
| Indeterminate | any other value | none of the above |

Headline mapping:

- `compound_law_h3_supported_at_n4` if observed F2 `level_integer_residual_max` at float64 is exactly `0.125`.
- `transformed_decay_converges_to_identity_floor` if observed F2 `level_integer_residual_max` at float64 is exactly `0.25`.
- `rounding_event_count_dominates` if observed F2 `level_integer_residual_max` at float64 is exactly `0.0625`.
- `lattice_grain_indeterminate_at_n4_transformed` for any other observed value.

The equality comparison is exact because the observed lattice grain is a typed dyadic rational from the float64 ULP-level lattice campaign.

## Section C - Supplementary Observations

These observations are reported but do not determine the headline:

- F1, F3, and F4 lattice classifications. Expected: F3 is `lattice_empty`; F1 and F4 are `lattice_integer`.
- Polarity grid stability for `F1_F2` at float64. Expected: `grid_stable_polarity_coupling`.
- Sterbenz boundary at `r = 4.0`. Expected directional observation: above-boundary F2 nonzero density is higher than below-boundary density, matching Schwarzschild n=2 and Schwarzschild-cbrt n=3.
- Comparison against the Task 032 pure-algebraic quartic fixture at n=4 identity, which gave `0.25`.
