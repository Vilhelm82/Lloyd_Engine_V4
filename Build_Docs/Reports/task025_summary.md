# Task 025 Summary - Arithmetic Path Law Discovery

## Scope

Task 025 ran a campaign-only discovery pass for arithmetic path-response laws
on the Schwarzschild four-form battery. The campaign used the three-flavor
framing from the task: decimal-50 oracle as truth reference, first-order
chain envelope as the conservative substrate baseline, and sparse discovered
laws as the object under test.

The fixed 17-term candidate library was evaluated without expansion. Sparse OLS
searched 1-, 2-, and 3-term laws. No primitives, status families, manifests,
protocols, or transition rules were added.

## Test Count

- Pre-task baseline: 431 tests passing.
- Post-Task 025 collection: 443 tests.
- Added tests: 12 in `tests/test_task025_path_law_discovery.py`.
- Full suite: 443 tests passing.

## Files Changed

- `src/lloyd_v4/evals/path_law_discovery.py`
- `src/lloyd_v4/evals/path_law_campaign.py`
- `tests/test_task025_path_law_discovery.py`
- `Build_Docs/Reports/task025_path_law_discovery/campaign_output.json`
- `Build_Docs/Reports/task025_path_law_discovery/README.md`
- `Build_Docs/Reports/task025_summary.md`
- `Build_Docs/Agent_tasks/Completed/codex_task025_arithmetic_path_law_discovery.md`

The task-ledger move for Task 017b was already present in the handoff state and
was preserved.

## Per-Form Discovery Results

| Form | Status | Top 1-term fit | Top 2-term fit | R2 of selected fit | Axes passed | Notable observations |
| --- | --- | --- | --- | ---: | --- | --- |
| F1 | `path_law_supported_envelope` | `T_16`, c=-0.43464231440804224 | `T_13 + T_15`, c=(0.8147416042117659, -0.8210405083064486) | 0.2621103091007638 | A, B, E | No closed-form fit met R2 >= 0.95; chain envelope held with max residual/bound 0.2857142857142857. |
| F2 | `path_law_supported_envelope` | `T_7`, c=-5.8982831699991455e-18 | `T_13 + T_15`, c=(0.9992675373694574, -0.6617634646597813) | 0.29495978731107164 | A | No closed-form fit met R2 >= 0.95; chain envelope held with max residual/bound 0.42857142857142855. |
| F3 | `path_law_exact_zero` | none | none | 1.0 | A, B, C, D, E, F | Calibration zero across float32, float64, and decimal-50 residuals. |
| F4 | `path_law_supported_closed_form` | `T_15`, c=1.0111298989021043 | `T_14 + T_15`, c=(0.4044519595608417, 0.2022259797804209) | 0.9578834217812657 | A, B, C, D, E, F | Rediscovered the known `delta_f/(2*sqrt(f))` law. |

## F4 Rediscovery Gate

Pass.

- Winning term: `T_15`
- Coefficient: `1.0111298989021043`
- R2: `0.9578834217812657`
- Required term: `T_15`

This confirms that the discovery machinery can recover the known F4 transfer
law from the constrained candidate library. F1 and F2 results are therefore not
quarantined by a failed gate, but they still do not qualify as closed-form laws.

## F1 And F2 Classifications

F1 and F2 were classified as `path_law_supported_envelope`. Their smooth sparse
fits were weak (`R2` below 0.30), and regional/sign axes did not justify a
closed-form law claim. The chain-envelope bound held cleanly for both forms, so
the honest result is envelope support rather than closed-form discovery.

Piecewise fits were exercised through regional axis D, but the selected global
fits did not produce region-consistent closed forms.

## F3 Calibration Zero

F3 remained the calibration zero. The campaign emitted the zero law and all six
validation axes passed.

## Precision Scaling

| Form | Axis B status | Median predicted/observed float32 ratio | Pass |
| --- | --- | ---: | --- |
| F1 | `precision_scaling_supported` | 2.3741356301945 | yes |
| F2 | `precision_scaling_failed` | 1.1724403427279958e-09 | no |
| F3 | calibration zero | n/a | yes |
| F4 | `precision_scaling_supported` | 0.9948202827321421 | yes |

## Honest Observations

- `T_13` and `T_15` ranked usefully for F1's weak 2-term fit, but the fit quality
  was not strong enough for a law claim.
- F2's best selected fit was a weak 3-term smooth fit with tiny coefficients and
  failed precision scaling; the envelope classification is the substrate-honest
  result.
- F4's 2-term fit included the collinear alias pair `T_14 + T_15` with a large
  condition number, while the parsimony-ranked 1-term `T_15` law was cleaner and
  passed all axes.

## Limits

- Schwarzschild four-form battery only.
- Fixed 17-term candidate library.
- Sparse fits limited to at most 3 terms.
- Decimal-50 oracle, float32, and float64 only.
- No envelope predictor, deconvolution, solver behavior, or substrate promotion.

## Verification

- `python -m pytest -q tests/test_task025_path_law_discovery.py`
- `python -m pytest -q tests/`
- `python -m pytest -q tests/test_task001_source_purity.py`
- `PYTHONPATH=src python -m lloyd_v4.evals.path_law_campaign`
- `PYTHONPATH=src python -m lloyd_v4.evals.path_law_campaign --output /tmp/path_law_repeat.json`
- `diff Build_Docs/Reports/task025_path_law_discovery/campaign_output.json /tmp/path_law_repeat.json`
- `python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py`
