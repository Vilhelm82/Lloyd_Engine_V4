# ProjectionResultV4 Status Table

| Projection status | Source condition | Branch compatibility | Flags | Validity mapping | Selection behavior | Advance behavior | Refusal behavior |
|---|---|---|---|---|---|---|---|
| `projection_transverse` | `two_real_roots` | `minus` or `plus` | root exists, projection defined, selected root valid, advance valid | defined, finite, selectable, advanceable, observable | uses Task 002 selection | advance-valid | none |
| `projection_tangent_contact` | `repeated_root` | `repeated` | root exists, projection defined, selected root valid, not advance valid | defined, finite, selectable, not advanceable, observable | uses Task 002 selection | not advance-valid | none |
| `projection_linear` | `linear_root` | `linear` | root exists, projection defined, selected root valid, advance valid | defined, finite, selectable, advanceable, observable | uses Task 002 selection | advance-valid | none |
| `projection_no_real_root` | `no_real_root` | branch ignored | no root, projection not defined, selected root invalid, not advance valid | not defined, not finite, not selectable, not advanceable, observable | no selection attempted | not advance-valid | status result, not scalar failure |
| `projection_identity` | `constant_identity` | branch ignored | root exists, projection not defined, selected root invalid, not advance valid | not defined, not finite, not selectable, not advanceable, observable | no selection attempted | not advance-valid | nonunique solution set |
| `projection_no_solution` | `constant_no_solution` | branch ignored | no root, projection not defined, selected root invalid, not advance valid | not defined, not finite, not selectable, not advanceable, observable | no selection attempted | not advance-valid | no real solution set |
| `projection_selection_refused` | selectable source with incompatible branch | incompatible | root existence inherited from source, projection not defined, selected root invalid, not advance valid | not defined, not finite, not selectable, not advanceable, observable | Task 002 selection refusal preserved | not advance-valid | typed refusal with requested branch and source status |

`projection_tangent_contact` intentionally differs from selection failure: the scalar root is valid, but projection advance is not valid in Task 003.

`projection_identity` intentionally has `root_exists=True` because the real solution set is nonempty, while `projection_defined=False` because no unique projection target exists.
