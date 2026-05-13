# Task 029c Summary - Cube-root Four-form Battery

## Scope

Task 029c added a cube-root four-form battery as a fourth chain-property
fixture, with `R = numpy.cbrt(1 - x)` over the canonical 137-point x-grid. The
task added eval-layer fixture, lattice, polarity-grid, cbrt campaign, report,
and test artifacts. It did not add substrate primitives, runtime statuses,
manifest entries, protocols, law-library terms, or new candidate path families.

## Pre-registration

- Commit: `9ee06d7 Task 029c pre-registration: cbrt four-form battery predictions`
- Date: `2026-05-13 11:43:03 +1000`
- File: `Build_Docs/Reports/task029c_cbrt_four_form_battery/pre_registration.md`
- Status: byte-identical to the pre-registration commit at completion.

## Section A - Five-invariants Table

| Invariant | Prediction | Observed | Match? |
| --- | --- | --- | --- |
| F1||F2 grid-stable polarity coupling | 100% sign agreement, p < 0.01, all 4 grids cofire >= 10 | aggregate `grid_stable_polarity_coupling`; reference fraction `1.0`; reference p `8.077935669463161e-28`; grid cofire reference/coarse/fine/uniform `91/89/83/94` | Y |
| F3 identity silence | F3 == 0.0 at every cell | all polarity-grid F3 nonzero counts are zero | Y |
| F2 non-integer lattice grain | non-integer character, grain observed by campaign | classification `non_integer_lattice`; max integer residual `0.25` | Y |
| F4 integer lattice character | integer-lattice classification | classification `lattice_integer`; max integer residual `0.0` | Y |
| Sterbenz boundary at x = 1/2, below density > above | location at x = 1/2, below higher | observed location `0.5`; below density `0.9420289855072463`; above density `0.4852941176470588`; direction `below_boundary_higher` | Y |

## Section B - Refined F5+ Predictions

| Path | Prediction | Observed status | Cofire rate | Match? |
| --- | --- | --- | ---: | --- |
| `P_compound_split` | PRESENT in cbrt strong cluster | `present` | `0.9285714285714286` | Y |
| `P_sign_c` | PRESENT in cbrt strong cluster | `present` | `0.9285714285714286` | Y |
| `P_distrib_sqrt_mul` | ABSENT or attenuated in cbrt strong cluster | `absent` | `0.0` | Y |

At cut=0.10 the cbrt scale-invariant rank is `5`. F1-F4 remain
self-consistent, and the cbrt F5 candidates under this rank are
`P_compound_split` and `P_sign_c`.

## Sterbenz Boundary

The cbrt fixture uses x directly, so the pre-registered boundary is x = 1/2.
The observed nearest grid point is exactly `0.5`. F2 nonzero density below the
boundary is `65/69 = 0.9420289855072463`; above the boundary it is
`33/68 = 0.4852941176470588`. This matches the pure algebraic direction and
supports the value-level boundary prediction.

## Headline Classification

Headline: `chain_property_universal`.

All five load-bearing Section A predictions matched in the cbrt fixture, and
the existing cross-fixture table now accepts the fourth fixture explicitly. The
headline is grounded only in Section A; Section B contributes mechanism evidence
but does not determine the headline.

## F5+ Interpretation

Section B matched all three predictions. `P_compound_split` and `P_sign_c`
remained present, consistent with Task 029b's universal refined F5+ set.
`P_distrib_sqrt_mul` was absent, which supports the 029b reading that this path
is operation-specific rather than substrate-universal.

## Tests

- Baseline at task start: `7777bf5`, 553 tests collected and passing.
- Pre-registration commit: `9ee06d7`.
- Added tests: 29 in `tests/test_task029c_cbrt_four_form_battery.py`.
- Post-task collection: 582 tests collected.
- Focused task suite: `python -m pytest -q tests/test_task029c_cbrt_four_form_battery.py` passed.
- Full suite: `python -m pytest -q tests/` passed.

## Byte-stability

- `campaign_results.json`: repeat run diff produced no output.
- `headline_classification.md`: repeat generation diff produced no output.
- `pre_registration.md`: diff against `9ee06d7` produced no output.

## Discipline Gates

- F3 sentinel held across every cbrt grid and precision used in this task.
- F1/F4 negative control held: cbrt aggregate is not `grid_stable_polarity_coupling`.
- F2/F4 bottle-cap gate held.
- `layer_manifest.json` and `LAYER_MANIFEST.md` were unchanged.
- No banned interpretive terms were present in the new cbrt source or report files.
- No `math.cbrt`, `cmath`, `scipy`, `sympy`, `mpmath`, `math.pi`, `math.e`, `math.tau`, or cube-root-by-fractional-power pattern was introduced.

## Files Changed

- `Build_Docs/Agent_tasks/Completed/codex_task029c_cbrt_four_form_battery.md`
- `Build_Docs/Reports/task029c_cbrt_four_form_battery/pre_registration.md`
- `Build_Docs/Reports/task029c_cbrt_four_form_battery/campaign_results.json`
- `Build_Docs/Reports/task029c_cbrt_four_form_battery/headline_classification.md`
- `Build_Docs/Reports/task029c_cbrt_four_form_battery/cbrt_four_form_battery.json`
- `Build_Docs/Reports/task029c_cbrt_four_form_battery/cbrt_lattice_campaign_output.json`
- `Build_Docs/Reports/task029c_cbrt_four_form_battery/cbrt_polarity_grid_stability.json`
- `Build_Docs/Reports/task029c_cbrt_four_form_battery/cbrt_polarity_grid_table.csv`
- `Build_Docs/Reports/task029c_cbrt_four_form_battery/cbrt_precision_overlap_table.csv`
- `Build_Docs/Reports/task029c_cbrt_four_form_battery/cbrt_region_split_table.csv`
- `Build_Docs/Reports/task029c_summary.md`
- `src/lloyd_v4/evals/cbrt_four_form.py`
- `src/lloyd_v4/evals/cbrt_lattice_campaign.py`
- `src/lloyd_v4/evals/cbrt_polarity_grid_stability.py`
- `src/lloyd_v4/evals/cbrt_four_form_campaign.py`
- `src/lloyd_v4/evals/cross_fixture_comparison.py`
- `tests/test_task029c_cbrt_four_form_battery.py`

## Forward Observations

The five-invariant structure survived the radical-degree change, so the
chain-property claim is not limited to the previous square-root skeleton. The
Sterbenz boundary stayed value-level at x = 1/2, which supports the existing
mechanism account. The cbrt F2 lattice residual of `0.25` shows the
non-integer-lattice branch has reproducible sub-integer structure. The F5+
results separate universal candidates from operation-specific behavior:
`P_compound_split` and `P_sign_c` persisted, while `P_distrib_sqrt_mul` did not.
