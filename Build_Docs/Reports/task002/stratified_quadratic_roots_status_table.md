# StratifiedQuadraticRoots Status Table

| Status | Exact condition | Value shape | Validity mapping | Selection behavior | Refusal behavior |
|---|---|---|---|---|---|
| `two_real_roots` | `a != 0` and `b*b - 4*a*c > 0` | coefficients, discriminant, `minus` and `plus` projective coordinates | defined, finite, selectable, advanceable, observable | accepts `minus` and `plus` | other branches refuse |
| `repeated_root` | `a != 0` and `b*b - 4*a*c == 0` | coefficients, discriminant, `repeated` projective coordinate | defined, finite, selectable, advanceable, observable | accepts `repeated` | other branches refuse |
| `no_real_root` | `a != 0` and `b*b - 4*a*c < 0` | coefficients and discriminant, no real-root coordinates | defined, not finite, not selectable, not advanceable, observable | refuses | typed refusal; no complex root path |
| `linear_root` | `a == 0` and `b != 0` | coefficients, no discriminant, `linear` projective coordinate | defined, finite, selectable, advanceable, observable | accepts `linear` | other branches refuse |
| `constant_identity` | `a == 0`, `b == 0`, and `c == 0` | coefficients, no discriminant, no coordinate | defined, not finite, not selectable, not advanceable, observable | refuses | typed refusal; every real input satisfies the equation |
| `constant_no_solution` | `a == 0`, `b == 0`, and `c != 0` | coefficients, no discriminant, no coordinate | defined, not finite, not selectable, not advanceable, observable | refuses | typed refusal; no real input satisfies the equation |

## Root Coordinate Evidence

Selectable branches store projective coordinates:

```text
minus:    [ -b - sqrt(discriminant) : 2*a ]
plus:     [ -b + sqrt(discriminant) : 2*a ]
repeated: [ -b : 2*a ]
linear:   [ -c : b ]
```

The classification result itself does not return scalar roots. Scalar values appear only after `select_quadratic_root(result, branch)` succeeds.
