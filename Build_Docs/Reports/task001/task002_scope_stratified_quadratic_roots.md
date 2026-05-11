# Task 002 Scope: StratifiedQuadraticRoots

Task 002 should implement `StratifiedQuadraticRoots` without legacy mode.

The primitive should use the Task 001 lessons:

- construct a typed root state before scalar output
- classify strata explicitly
- preserve raw coefficients and provenance
- expose scalar/root selection through protocol validation
- refuse unsupported strata with typed results
- avoid hidden numeric correction paths

Required initial statuses should align with Task 000:

- `two_real_roots`
- `repeated_root`
- `no_real_root`
- `linear_root`
- `constant_identity`
- `constant_no_solution`

Task 002 should not start branch fingerprints, projection consumers, or V3 comparison fixtures.
