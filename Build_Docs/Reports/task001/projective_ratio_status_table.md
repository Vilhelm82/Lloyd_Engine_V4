# ProjectiveRatio Status Table

| Status | Exact condition | Projective value | Projective defined | Scalarization | Refusal behavior |
|---|---:|---|---|---|---|
| `finite_ratio` | `d != 0 and n != 0` | `[n:d]` | yes | permitted | none |
| `signed_zero` | `d != 0 and n == 0` | `[0:d]` | yes | permitted | none |
| `infinite_direction` | `d == 0 and n != 0` | `[n:0]` | yes | refused | typed refusal; no scalar infinity |
| `indeterminate` | `d == 0 and n == 0` | `[0:0]` | no | refused | typed refusal; no numeric sentinel |

## Validity Mapping

Task 000 validity fields are used as follows:

- `defined`: whether the projective state is determined.
- `finite`: whether scalarization can produce a finite scalar.
- `selectable`: whether scalarization protocol may select this state for scalar output.
- `advanceable`: same as scalarizable for Task 001; future primitives may split this further.
- `observable`: whether raw projective evidence is retained.
