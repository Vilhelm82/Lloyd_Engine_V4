# Task 024b Summary - Schwarzschild Four-Form Battery

## Scope

Task 024b added a V4-native discovery campaign for the Schwarzschild
four-form battery. The campaign reconstructs the four V3 reference forms,
runs existing V4 typed primitives over the 137-point sweep, records
transfer strata, bare log-log slope strata, AlphaProbe statuses, and the
023b reliability fields. It adds no primitives, no status families, no
manifest entries, and no architecture edits.

## Test Count

- Pre-task baseline after Task 023b: 414 tests passing.
- Post-task suite: 423 tests passing.
- Added tests: 9 in `tests/test_task024b_schwarzschild_four_form.py`.

## Files Changed

- `src/lloyd_v4/evals/__init__.py`
- `src/lloyd_v4/evals/schwarzschild_four_form.py`
- `src/lloyd_v4/evals/schwarzschild_four_form_campaign.py`
- `tests/test_task024b_schwarzschild_four_form.py`
- `Build_Docs/Reports/task024b_schwarzschild_four_form/v3_reference_overlay.csv`
- `Build_Docs/Reports/task024b_schwarzschild_four_form/v3_reference_overlay.json`
- `Build_Docs/Reports/task024b_schwarzschild_four_form/campaign_output.json`
- `Build_Docs/Reports/task024b_schwarzschild_four_form/README.md`
- `Build_Docs/Reports/task024b_summary.md`

The downloaded CSV was display-rounded while the JSON had full row values.
The repo CSV was rendered from the supplied JSON rows so the CSV can serve
as the canonical 1-ULP fixture-validation table required by the task.

## Stratum Pattern Across The Four Forms

| Form | Transfer stratum counts | Slope status | Alpha status | Alpha stability |
| --- | --- | --- | --- | --- |
| F1 | 124 x `transfer_observed`, 12 x `transfer_cancellation_dominated` | `slope_observed` | `alpha_unstable_window` | `unstable` |
| F2 | 133 x `transfer_observed`, 3 x `transfer_cancellation_dominated` | `slope_observed` | `alpha_zero_boundary` | `unstable` |
| F3 | 136 x `transfer_observed` | `slope_insufficient_data` | `alpha_insufficient_data` | `not_tested` |
| F4 | 132 x `transfer_observed`, 4 x `transfer_cancellation_dominated` | `slope_observed` | `alpha_negative_singularity` | `stable` |

## Slope And Alpha Values

| Form | Bare slope | R2 | n_used | Observed alpha | Alpha slope | Alpha R2 | Alpha span | Propagated error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| F1 | `-0.23544846424874247` | `0.1786037205306339` | 91 | `0.7827028943465816` | `-0.2172971056534184` | `0.5492644062018636` | `1.4111331327728664` | `0.4082494488158547` |
| F2 | `-2.6114475287740198` | `0.6237726561789159` | 31 | `-0.18388341173364164` | `-1.1838834117336416` | `0.7934315112540486` | `0.4726397961065195` | `0.1627423798963913` |
| F3 | n/a | n/a | 0 | n/a | n/a | n/a | n/a | n/a |
| F4 | `-1.2306199463834475` | `0.8196653610793952` | 103 | `-0.133538800106082` | `-1.133538800106082` | `0.8668114844094328` | `2.7885690293087757` | `4.38421894074107` |

## V3 Overlay

For F4, V4 reconstructed the fixture-level ratio
`F4_act / (delta_f / (2 * f**0.5))` across non-zero entries:

- ratio count: 92
- median: `1.0175882794383106`
- IQR: `0.3212617028151089`
- V3 reported slope reference: `-0.4988` on a different protocol
  (`log|F4/delta_f|` vs `log f`)

V4's bare slope in this campaign is `log|transfer|` vs `log|f|`, with
transfer observations produced by the V4 finite-difference primitive.
The values are descriptive overlays, not match/mismatch claims.

## Sample Serialized Observations

F1:

```json
{"transfer":{"status":"transfer_observed","transfer":2.6830389761773123e-15},"slope":{"status":"slope_observed","slope":-0.23544846424874247,"n_used":91},"alpha":{"status":"alpha_unstable_window","observed_alpha":0.7827028943465816,"alpha_stability_status":"unstable"}}
```

F2:

```json
{"transfer":{"status":"transfer_observed","transfer":0.0},"slope":{"status":"slope_observed","slope":-2.6114475287740198,"n_used":31},"alpha":{"status":"alpha_zero_boundary","observed_alpha":-0.18388341173364164,"alpha_stability_status":"unstable"}}
```

F3:

```json
{"transfer":{"status":"transfer_observed","transfer":0.0},"slope":{"status":"slope_insufficient_data","slope":null,"n_used":0},"alpha":{"status":"alpha_insufficient_data","observed_alpha":null,"alpha_stability_status":"not_tested"}}
```

F4:

```json
{"transfer":{"status":"transfer_observed","transfer":1.0732155904709249e-14},"slope":{"status":"slope_observed","slope":-1.2306199463834475,"n_used":103},"alpha":{"status":"alpha_negative_singularity","observed_alpha":-0.133538800106082,"alpha_stability_status":"stable"}}
```

Full serialized samples are in `campaign_output.json` under each form's
`sample_serialized` block.

## V3 Fixture Validation

All 137 rows of V4-computed `f`, `R`, `F1`, `F2`, `F3`, `F4`, and `delta_f`
agree with the static V3 reference overlay to within one `ulp_f` column
unit. Rows with expected zero require exact V4 zero; F3 satisfies this
for all 137 rows.

## Limits

- The campaign does not add a value-vs-value slope primitive; it uses
  existing transfer observations and presents the slope as V4 substrate
  evidence.
- The campaign does not retry eta, h-grid, or sweep choices to force a
  different emission.
- No multi-precision execution was run.
- No SR or Bell four-form analog was added.
- The path-roundoff residual `delta_f` remains fixture-level evidence,
  not a promoted V4 primitive concept.

## Honest Observations

- F3 is exactly silent as predicted: every transfer is observed with
  transfer `0.0`; the slope fit has no usable non-zero transfers.
- F1 is not merely partial-observe; its AlphaProbe emits
  `alpha_unstable_window`.
- F2 emits `alpha_zero_boundary` even though nested evidence is unstable.
  This follows Task 023b precedence: zero-boundary classification wins
  before unstable-window classification.
- F4 has the expected structured non-zero residual pattern in the V3
  overlay ratio, with median close to 1.0, but V4's AlphaProbe emits a
  stable `alpha_negative_singularity`, not `alpha_unstable_window`.
- V4's bare F4 transfer slope is `-1.2306199463834475`; it is not the
  V3 reference slope because the V4 protocol is not the same fitted
  quantity.

## Audits

- `python -m pytest -q tests/test_task024b_schwarzschild_four_form.py`: passed, 9 tests.
- `python -m pytest -q tests/`: passed, 423 tests.
- `python -m pytest -q tests/test_task001_source_purity.py`: passed.
- `python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py`: passed.
- `PYTHONPATH=src python -m lloyd_v4.evals.schwarzschild_four_form_campaign --output /tmp/campaign_output_repeat.json`: passed.
- `diff Build_Docs/Reports/task024b_schwarzschild_four_form/campaign_output.json /tmp/campaign_output_repeat.json`: passed.
- `git diff --check`: passed.
- Git commit and push: recorded in final handoff after commit creation.
