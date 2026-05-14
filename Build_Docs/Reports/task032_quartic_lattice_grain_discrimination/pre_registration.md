# Task 032 Pre-Registration - Quartic Lattice Grain Discrimination

This document was written before Task 032 fixture source, measurement outputs, headline output, or summary artifacts were created. It locks the fixture construction, hypothesis table, headline mapping, and supplementary observations.

## Section A - Fixture Construction

The quartic-root fixture uses the canonical pure_algebraic operand grid: 137 values on `x in [0.01, 0.99]`, reusing `pure_algebraic_four_form.x_grid`.

The direct identity operand is:

- `f_direct(x) = 1 - x`

The admitted quartic root is computed by composed square roots:

- `R(x) = numpy.sqrt(numpy.sqrt(1 - x))`

This composition has two root-rounding events. That property is part of the pre-registered fixture; a native single-rounding quartic-root primitive would be a different fixture.

The four forms are:

| Form | Definition |
| --- | --- |
| `F1` | `R * R * R * R - f_direct(x)` |
| `F2` | `R * R * R * R - 1 + x` |
| `F3` | `R - numpy.sqrt(numpy.sqrt(f_direct(x)))` |
| `F4` | `R - numpy.sqrt(numpy.sqrt(f_alt(x)))`, where `f_alt(x) = (1 - x / 2) - x / 2` |

The float32 fixture converts input and intermediate values through `numpy.float32`. The float64 fixture uses Python floats with `numpy.sqrt`.

## Section B - Hypotheses and Pre-Registered Outcomes

| Hypothesis | Predicted F2 grain at `n=4` | Source |
| --- | ---: | --- |
| H1: algebraic-degree law, grain = `2^(1-n)` | `0.125` | two-of-three fit on transformed fixtures plus cube-root |
| H2: operand-transformation law | `0.25` | four-of-four fit on existing data |
| Indeterminate | any other value | neither hypothesis predicts |

Headline mapping:

- `lattice_grain_h1_quartic` if observed F2 `level_integer_residual_max` at float64 is exactly `0.125`.
- `lattice_grain_h2_operand` if observed F2 `level_integer_residual_max` at float64 is exactly `0.25`.
- `lattice_grain_indeterminate` for any other observed value, including `0.0`, `0.5`, or another fractional value.

The equality comparison is exact because the observed lattice grain is a typed dyadic rational from the float64 ULP-level lattice campaign.

## Section C - Supplementary Observations

These observations are reported but do not determine the headline:

- F1, F3, and F4 lattice classifications. Expected: F3 is `lattice_empty`; F1 and F4 are `lattice_integer`.
- Polarity grid stability for `F1_F2` at float64. Expected: `grid_stable_polarity_coupling`.
- Sterbenz boundary at `x = 0.5`. Expected directional observation: below-boundary F2 nonzero density is higher than above-boundary density.
- The two-root-rounding composition caveat: the result applies to the admitted `sqrt(sqrt(...))` quartic fixture, not to a native single-rounding quartic-root primitive.
