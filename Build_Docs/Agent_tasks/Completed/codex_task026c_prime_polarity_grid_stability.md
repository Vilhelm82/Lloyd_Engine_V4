# Codex Task 026c-prime — Polarity Grid Stability Campaign

## 1. Repository / Baseline

- Repo: `git@github.com:Vilhelm82/Lloyd_Engine_V4.git`, branch `main`.
- Working tree state pre-task: clean. Origin/main matches local. `git log -1 --oneline` should return `d561a3c Task 026: Lattice and anomaly investigation campaign`.
- Pre-task test baseline: 456 tests passing (`pytest -q tests/`).
- Pre-task fixture (verify before starting): Schwarzschild four-form battery in `src/lloyd_v4/evals/multi_precision_four_form.py` and `src/lloyd_v4/evals/schwarzschild_four_form.py` must be untouched; their existing tests must pass.

## 2. Task Goal

Test whether the F1/F2 100% parallel-polarization finding from Task 026 is **grid-stable** — i.e., reproduces across independent r-sweeps — or is an artefact of the V3-reference grid. Same test is run for F1/F4 (expected: depolarized across all grids; this is the negative control) and F2/F4 (expected: undertested on most grids; this is the explicit guard against over-promotion).

This is a **campaign task**, not a substrate change. No new primitive, no new runtime status family, no manifest changes, no law-library term.

## 3. Source Labelling

- **V4-surface evidence**: Task 026 sub-module E float64 sign sequences for F1, F2, F3, F4; cross-form sign agreement counts; per-region density.
- **Reference-grid baseline**: Schwarzschild four-form values via `four_form_float32` and `four_form_float64` evaluated on `sweep_r_values()` (the V3-reference CSV r-grid).
- **Polarization analysis output (in scope of this task)**: per-pair, per-precision, per-grid cofire/agreement/binomial-p tables; region splits; precision-overlap relation invariance.

## 4. Design Principles

1. **Grids are tested independently.** No grid is privileged. The reference grid is one of four grids in the report. Promotion requires the relation to hold across all *non-reference* grids meeting power thresholds.
2. **Grid construction is deterministic.** Every grid is reproducible from a hard-coded seed or a closed-form jitter rule. No `time.time()`, no `os.urandom`, no environment-derived state.
3. **Deduplicate after clamping; preserve ordering.** After any perturbation step, sort r-values ascending and drop consecutive duplicates. Report `n_input` (137) and `n_after_dedup` for each grid; if dedup loses points, the actual N is what the analysis runs on.
4. **Underpowered grids are not failures.** A grid with cofire_count < 10 for a pair emits status `underpowered_grid` for that pair; this does not count as evidence against grid stability. It is open evidence.
5. **F1/F4 is the negative control.** If F1/F4 starts showing significant coupling on any grid, the analysis is too permissive and the entire report is flagged. F1/F4 should remain boringly coin-flippy across grids.
6. **F2/F4 is guarded.** F2/F4 cannot reach `grid_stable_supported` status unless ALL grids produce adequate cofire counts (>= 10). At 4 cofires on the reference grid, F2/F4 is currently `open_underpowered`. The task must not let small-N agreement bottle-cap-crown its way to promotion.
7. **Report-only statuses.** All status strings in this report are *report classifications*. They do not become runtime status enums, do not register as transition rules, do not appear in `lloyd_v4.core.status.StatusCode`. They live in the campaign output and the summary doc, not in production substrate.

## 5. Primitive-Sufficiency Gate

| Concept used in this task | Origin | Layer |
|---|---|---|
| Schwarzschild four-form values | `lloyd_v4.evals.schwarzschild_four_form` (admitted eval module) | eval |
| float32/float64 four-form | `lloyd_v4.evals.multi_precision_four_form` (admitted eval module) | eval |
| `decimal.Decimal` for region cutoffs | stdlib admitted for substrate-precision arithmetic | eval |
| `numpy.float32`, `numpy.float64` | admitted as type containers | eval |
| binomial coefficient `math.comb` | stdlib, used for exact p-values; no scipy | eval |
| pseudo-random sampling | `random.Random(seed)` with hard-coded integer seeds; no `numpy.random` global state | eval |

**No new substrate primitive. No import of `numpy.random` (its global state is non-deterministic across sessions in some configurations); use `random.Random` with explicit seeds.**

## 6. Required Deliverables

### 6.1 Module

New file: `src/lloyd_v4/evals/polarity_grid_stability.py`.

Public surface:

```python
def construct_grid(name: str, seed: int) -> dict[str, object]:
    """
    Return {
        "name": name,
        "seed": seed,
        "n_input": 137,
        "n_after_dedup": int,
        "r_values": tuple[float, ...],   # sorted ascending, no duplicates
        "construction_rule": str,        # human-readable description
        "r_min": float,
        "r_max": float,
        "clamped_low_count": int,
        "clamped_high_count": int,
    }
    """

def compute_polarity_table(grid: dict, precision: str) -> dict:
    """
    For one grid, one precision ('float32' or 'float64'):
    Return {
        "grid_name": ...,
        "precision": ...,
        "n_after_dedup": ...,
        "per_form_nonzero": {"F1": int, "F2": int, "F3": int, "F4": int},
        "pairs": {
            "F1_F2": {
                "cofire_count": int,
                "same_sign_count": int,
                "same_sign_fraction": float | None,
                "p_one_tail_upper": float | None,
                "p_one_tail_lower": float | None,
                "p_two_tail": float | None,
                "region_split": {
                    "near":   {"cofire": int, "agree": int, "p_two_tail": float | None},
                    "middle": {...},
                    "far":    {...},
                },
            },
            "F1_F4": {...},
            "F2_F4": {...},
        },
    }
    """

def compute_precision_overlap_invariance(grid: dict) -> dict:
    """
    For one grid, compare float32 and float64 polarization relation per-r-position:
    Return {
        "grid_name": ...,
        "pairs": {
            "F1_F2": {
                "both_precision_cofire": int,
                "same_relation_count": int,
                "invariance_fraction": float | None,
            },
            "F1_F4": {...},
            "F2_F4": {...},
        },
    }
    """

def classify_pair(grid_tables: list[dict], invariance_tables: list[dict], pair: str) -> dict:
    """
    Returns {
        "per_grid": {grid_name: report_status, ...},
        "aggregate": aggregate_status,
        "reasoning": human-readable string,
    }
    """

def run_campaign() -> dict:
    """
    Orchestrates the four grids, computes all tables, runs classification, returns
    the full campaign payload. Used by both the CLI entry point and tests.
    """

def write_campaign_output(path: Path = DEFAULT_OUTPUT) -> dict:
    """Run the campaign and write campaign_output.json. Returns the payload."""

def main() -> None:
    """CLI entry; supports --output <path>."""
```

Module must be byte-stable on repeated runs. Two consecutive runs of `main()` writing to different paths must produce `diff`-clean files.

### 6.2 Grids

Exactly four grids, in this order:

1. **`reference`** — `seed=0`, `construction_rule="V3 reference CSV via sweep_r_values()"`. Use the existing `sweep_r_values()` directly. `n_after_dedup` must equal 137; if it doesn't, halt with an error (the V3 grid is by construction unique).

2. **`coarse_perturbation`** — `seed=1042`, `construction_rule="r_i * (1 + 0.05 * Uniform[-1, 1]), clamped to [2.005, 10.0], sorted, deduplicated"`. For each original r-value at index i, draw `delta = random.Random(seed).uniform(-1.0, 1.0)` (one Random instance, sequential draws). Compute `r_new = r * (1 + 0.05 * delta)`. Clamp to [2.005, 10.0] (track `clamped_low_count`, `clamped_high_count`). Sort ascending. Drop any value that is within `2 * ulp(max(abs(a), abs(b)))` of the previous value (these are the "duplicates"). Report `n_after_dedup`.

3. **`fine_perturbation`** — `seed=2317`, `construction_rule="r_i * (1 + 1e-4 * Uniform[-1, 1]), clamped to [2.005, 10.0], sorted, deduplicated"`. Same procedure with perturbation factor 1e-4.

4. **`independent_uniform`** — `seed=4099`, `construction_rule="137 samples drawn from Uniform(2.005, 10.0), sorted, deduplicated"`. Draw 137 samples via sequential `random.Random(seed).uniform(2.005, 10.0)` calls. No clamping needed (samples are already in range; `clamped_low_count = clamped_high_count = 0`). Sort. Apply same dedup rule.

The clamp endpoints (2.005, 10.0) are derived from the existing `sweep_r_values()` range:
```python
_REF = sweep_r_values()
_R_MIN, _R_MAX = _REF[0], _REF[-1]
```
NOT hard-coded fresh in this module.

**Empirical expectations (pre-verified, for sanity check during implementation):**

| Grid | Expected n_after_dedup | Expected clamp behavior | Note |
|---|---|---|---|
| `reference` | 137 (must equal exactly) | 0 / 0 | Halt with error if not 137. |
| `coarse_perturbation` | ~121 (give or take a few) | ~16 high-clamped, ~0 low-clamped | `r * 1.05` for r near 10.0 clamps to 10.0, creating boundary pile-up that dedup catches. |
| `fine_perturbation` | 137 (no dedup expected) | 0 / 0 | 1e-4 jitter is ~12 orders of magnitude above ulp; perturbed points remain numerically distinct. |
| `independent_uniform` | 137 (no dedup expected) | 0 / 0 | 137 samples from [2.005, 10.0] have min spacing ~2.3e-4, well above ulp. |

If empirical results diverge significantly from these expectations (e.g., `fine_perturbation` losing >5 points, or `independent_uniform` losing any points), flag in the summary as an unexpected substrate behavior and investigate before reporting classifications. These expectations are NOT acceptance criteria — they are sanity benchmarks.

**Boundary-clamp metrology note:** The 16 high-clamped points in `coarse_perturbation` all land at exactly r=10.0. This is a real metrology observation about how the perturbation distributes near the boundary; the `clamped_high_count` field records it. F1/F2 cofires concentrate in the `far` region (13 of 16 reference cofires); if boundary clamping disproportionately removes far-region points, the coarse-grid F1/F2 cofire count could drop close to or below the 10-threshold for `underpowered_grid`. The spec handles this gracefully; just be aware.

### 6.3 Tables

Each table is a CSV in `Build_Docs/Reports/task026c_prime_polarity_grid_stability/`:

**`polarity_grid_table.csv`** — one row per (grid, precision, pair):
```
grid,precision,pair,cofire_count,same_sign_count,same_sign_fraction,p_one_tail_upper,p_one_tail_lower,p_two_tail,status
```

**`region_split_table.csv`** — one row per (grid, precision, pair, region):
```
grid,precision,pair,region,n_in_region,cofire_count,same_sign_count,same_sign_fraction,p_two_tail
```

**`precision_overlap_table.csv`** — one row per (grid, pair):
```
grid,pair,both_precision_cofire,same_relation_count,invariance_fraction,status
```

All numeric columns: 6-decimal precision in CSV (use `format(value, '.6f')`); p-values < 1e-6 are formatted as `'{:.3e}'`. NaN/None encoded as the literal string `null`.

### 6.4 Report statuses (per-pair, per-grid; and per-pair aggregate)

Per-pair per-grid status:

- `reference_grid_confirmed`: this is the reference grid AND same_sign_fraction >= 0.9 AND p_two_tail < 0.001 AND cofire_count >= 10.
- `grid_stable_supported`: non-reference grid AND same_sign_fraction >= 0.9 AND p_two_tail < 0.001 AND cofire_count >= 10 AND both precisions support same direction where cofire >= 10.
- `grid_stability_rejected`: non-reference grid AND cofire_count >= 10 AND (same_sign_fraction < 0.9 OR p_two_tail >= 0.001 OR precisions disagree). This is real evidence against invariance.
- `depolarized_supported`: cofire_count >= 10 AND 0.4 <= same_sign_fraction <= 0.6 AND p_two_tail > 0.1 (i.e., consistent with chance). Used primarily for F1/F4.
- `underpowered_grid`: cofire_count < 10. Not a failure.

Per-pair aggregate status (over all 4 grids):

- `grid_stable_polarity_coupling`: reference is `reference_grid_confirmed` AND all 3 non-reference grids are EITHER `grid_stable_supported` OR `underpowered_grid` (with at least one being `grid_stable_supported`, including the `independent_uniform` grid which is the strongest test).
- `depolarized_invariant`: all 4 grids are EITHER `depolarized_supported` OR `underpowered_grid` (with at least one `depolarized_supported`).
- `reference_grid_only`: reference is `reference_grid_confirmed` AND at least one non-reference grid is `grid_stability_rejected`. The relation holds on the reference grid but does NOT generalize.
- `open_underpowered`: cofire_count < 10 on all non-reference grids; no aggregate classification possible.
- `negative_control_failed`: F1/F4 reached `grid_stable_supported` on any grid. This flags the entire campaign — analysis is too permissive.

### 6.5 Promotion criteria (encoded in `classify_pair`)

F1/F2 can be upgraded from `reference_grid_only` to `grid_stable_polarity_coupling` only if:

1. cofire_count >= 10 on each non-reference grid; AND
2. same_sign_fraction >= 0.9 on each grid (including reference); AND
3. p_two_tail < 0.001 on each grid; AND
4. float32 and float64 both support the same direction (parallel vs anti-parallel) where cofire_count >= 10 in both precisions; AND
5. precision-overlap invariance_fraction >= 0.9 where both_precision_cofire >= 10.

If any non-reference grid has cofire_count >= 10 but fails condition (2), (3), (4), or (5), the aggregate status is `grid_stability_rejected` → `reference_grid_only`. If cofire counts are below threshold on all non-reference grids, the aggregate status is `open_underpowered`.

**F2/F4 explicit guard**: F2/F4 cannot reach `grid_stable_polarity_coupling` unless ALL four grids produce cofire_count >= 10. If any grid is `underpowered_grid` for F2/F4, the aggregate status is at most `open_underpowered`. 4/4 and 2/2 do not promote.

### 6.6 Report files

```
Build_Docs/Reports/task026c_prime_polarity_grid_stability/
    campaign_output.json
    polarity_grid_table.csv
    region_split_table.csv
    precision_overlap_table.csv
    README.md
Build_Docs/Reports/task026c_prime_summary.md
```

`campaign_output.json` schema:

```json
{
  "campaign": "task026c_prime_polarity_grid_stability",
  "grids": [
    {"name": "reference", "seed": 0, "n_input": 137, "n_after_dedup": 137,
     "construction_rule": "...", "r_min": 2.005, "r_max": 10.0,
     "clamped_low_count": 0, "clamped_high_count": 0},
    {"name": "coarse_perturbation", "seed": 1042, "n_input": 137, "n_after_dedup": ..., ...},
    ...
  ],
  "polarity_tables": [ {grid, precision, pair tables as in 6.1} ... ],
  "precision_overlap_tables": [ ... ],
  "aggregate_classifications": {
    "F1_F2": {"per_grid": {...}, "aggregate": "...", "reasoning": "..."},
    "F1_F4": {...},
    "F2_F4": {...}
  },
  "negative_control_passed": true,
  "headline_findings": [ "F1/F2: ...", "F1/F4: ...", "F2/F4: ..." ]
}
```

`README.md` documents the four grids, the status vocabulary, and the headline findings in prose.

`task026c_prime_summary.md` is the standard completion report (see section 10).

## 7. Required Tests

New test file: `tests/test_task026c_prime_polarity_grid_stability.py`.

Required tests (at minimum):

1. **`test_grids_are_deterministic`**: construct each grid twice; `r_values` must match exactly (byte-stable).
2. **`test_grids_preserve_ordering`**: each grid's `r_values` must be strictly increasing.
3. **`test_grids_deduplicate`**: no two consecutive r-values differ by less than `2 * ulp(max(abs(a), abs(b)))`.
4. **`test_grids_clamp_to_range`**: every r-value in every grid must satisfy `2.005 <= r <= 10.0`.
5. **`test_reference_grid_matches_sweep_r_values`**: `construct_grid("reference", 0)["r_values"] == sweep_r_values()`.
6. **`test_polarity_table_schema`**: `compute_polarity_table` returns the schema described in 6.1 for every grid × precision; all required keys present.
7. **`test_region_split_consistency`**: for every (grid, precision, pair), sum of region cofire counts equals the global cofire count.
8. **`test_negative_control_f1_f4`**: aggregate classification for F1/F4 must be `depolarized_invariant` (or `open_underpowered` if all non-reference grids underpowered; but cofires for F1/F4 are 48 on reference, so non-reference grids should hit >= 10 too unless the perturbation is pathological). If `negative_control_failed`, fail the test loudly — that is a campaign-level finding.
9. **`test_f2_f4_underpromotion_guard`**: if any grid has F2/F4 cofire_count < 10, the F2/F4 aggregate must NOT be `grid_stable_polarity_coupling`.
10. **`test_byte_stable_campaign_output`**: run `run_campaign()` twice; the JSON output must be identical byte-for-byte.
11. **`test_no_runtime_status_enum_additions`**: capture `set(StatusCode)` before and after importing the new module; they must be equal.
12. **`test_no_law_library_term_added`**: import the new module; assert that Task 025's law-library candidate list (if accessible via module-level import) is unchanged.
13. **`test_p_value_computation_exact`**: for `cofire=16, same_sign=16`, `p_one_tail_upper` must equal `2**-16` exactly (use `math.comb` summation).
14. **`test_f3_remains_zero`**: across all four grids and both precisions, F3 must be identically zero. If any grid produces a nonzero F3, the test FAILS LOUDLY — substrate has changed.

## 8. Required Commands

In completion report:

```bash
# Pre-task baseline confirmation
git log -1 --oneline
python -m pytest -q tests/

# Module import sanity
PYTHONPATH=src python -c "from lloyd_v4.evals.polarity_grid_stability import run_campaign; print(sorted(run_campaign().keys()))"

# Run campaign and verify byte-stable
PYTHONPATH=src python -m lloyd_v4.evals.polarity_grid_stability
PYTHONPATH=src python -m lloyd_v4.evals.polarity_grid_stability --output /tmp/polarity_grid_repeat.json
diff Build_Docs/Reports/task026c_prime_polarity_grid_stability/campaign_output.json /tmp/polarity_grid_repeat.json

# Task-specific tests
python -m pytest -q tests/test_task026c_prime_polarity_grid_stability.py

# Full suite
python -m pytest -q tests/

# Source purity audit
python -m pytest -q tests/test_task001_source_purity.py

# Manifest audits
python -m pytest -q tests/test_task010a_layer_manifest_machine_readable.py tests/test_task010b_export_drift.py tests/test_task010b_manifest_completeness.py tests/test_task010c_no_unregistered_operations.py tests/test_task010c_lineage_terminates_in_primitive.py tests/test_task010c_no_chain_cycles.py

# Forbidden-import grep (expected: zero matches)
rg "numpy\.random|np\.random|scipy|sympy|mpmath" src/lloyd_v4/evals/polarity_grid_stability.py
```

## 9. Non-Goals (explicit)

1. **No new substrate primitive.** This is an eval module, full stop.
2. **No new runtime status enum.** Report statuses live in JSON/CSV/Markdown only.
3. **No new manifest entries.** `layer_manifest.json` and `LAYER_MANIFEST.md` are not modified.
4. **No new transition rule.** Polarity is not a primitive observable yet.
5. **No new law-library term.** Task 025's candidate library is not extended by this task.
6. **No promotion to substrate even on full pass.** A successful `grid_stable_polarity_coupling` finding licenses a *future* substrate task; it does not itself add anything to substrate.
7. **No solver behavior changes.**
8. **No grid construction with `numpy.random` global state.** Use `random.Random(seed)`.
9. **No silent fallback if a grid has zero co-fires for a pair.** Emit `underpowered_grid`, log explicitly.
10. **No re-run of Task 026 sub-modules.** This task consumes existing 026 evidence by reference; the polarity computation is fresh on each new grid.
11. **No use of `math.pi`, `math.e`, `math.tau`, `numpy.pi`, or any other named mathematical constant.** Axiom 11.
12. **No use of `math.sqrt`, `math.log`, `numpy.sqrt`, `numpy.log` for substrate quantities.** The only legitimate uses of `numpy.sqrt` are inside the existing `four_form_*` functions (which this module CONSUMES, not extends). New code in this module uses arithmetic operators only.

## 10. Completion Report

`Build_Docs/Reports/task026c_prime_summary.md` must contain:

- Scope statement.
- Pre-task baseline confirmation (commit hash, test count).
- Test results (new test count, full suite count).
- Files changed list.
- Grid construction summary table (grid name, seed, n_input, n_after_dedup, range, clamp counts).
- Polarity table summary: for each pair × grid × precision, the cofire/agree/fraction/p row.
- Region split summary.
- Precision overlap invariance summary.
- Aggregate classification per pair with the deciding reasoning.
- Negative control status (F1/F4).
- Byte-stability verification.
- Honest observations: any surprises, any grids that produced unexpected dedup losses, any boundary-clamping behavior worth noting.
- Limits section: explicit list of what was NOT tested (cross-fixture, finer grid families, larger N, no substrate primitive added, etc.).
- Forward references: what substrate task this licenses (if any) and what remains open.

## 11. Acceptance Criteria

- All 14 required tests pass.
- Full pytest suite count == 456 + 14 == 470 (report exact number; if Codex adds additional tests beyond the 14 required, report the count and rationale).
- Byte-stable campaign output verified.
- No additions to `StatusCode` enum.
- No modifications to `layer_manifest.json` or `LAYER_MANIFEST.md`.
- No imports of `numpy.random`, `scipy`, `sympy`, `mpmath`, or `math`-named-constants in the new module.
- `tests/test_task001_source_purity.py` passes.
- All manifest-audit tests pass.
- Headline classification for F1/F2 is one of: `grid_stable_polarity_coupling`, `reference_grid_only`, or `open_underpowered`. The classification reflects the data; the task does not pre-decide which.
- F1/F4 classification is `depolarized_invariant` or `open_underpowered`. Anything else triggers `negative_control_failed` and is treated as a campaign-level finding to flag, not a test failure — but `test_negative_control_f1_f4` MUST fail loudly if `negative_control_failed`, so that the human can decide how to proceed.
- F2/F4 classification is NOT `grid_stable_polarity_coupling` unless all grids have cofire >= 10.

## 12. Discipline Notes

1. **The conclusion follows from the data.** This task's spec-author (Claude) has a hypothesis (F1/F2 will hold) and an expected null (F1/F4 will stay random). The spec must not bias the implementation toward those outcomes. If F1/F2 fails the perturbation tests, report `reference_grid_only` cleanly. If F1/F4 starts looking coupled on a perturbed grid, report `negative_control_failed` cleanly. Either is real evidence.

2. **F3 sentinel.** F3 must remain identically zero across all four grids at all precisions. If F3 emits any nonzero value, halt the campaign and flag — the substrate has changed and Task 026c-prime is not the place to discover that.

3. **No silent rescue.** If a grid produces fewer than 50 r-values after dedup, that is a finding, not a reason to re-seed. Emit `underpowered_grid` for everything on that grid and let the aggregate classifier do its job.

4. **Forward references.** The next substrate task — if F1/F2 passes — would be a typed polarization observable as a primitive (alongside the existing harmonic observables). That is NOT this task. This task only produces typed evidence.

5. **V3/V1 reference hygiene.** No V1 polarization analysis is imported or copied. The polarization analysis here derives from V4's own typed observations (sign sequences from Task 026 + fresh per-grid computation).

6. **Bottle-cap-crown discipline.** Small-N agreement is not evidence of structural invariance. The spec explicitly bans F2/F4 promotion at low cofire counts. Codex must enforce this in `classify_pair`; the test `test_f2_f4_underpromotion_guard` verifies enforcement.

7. **End-of-task git discipline (non-negotiable).**

```bash
git add -A
git status
git commit -m "Task 026c-prime: Polarity grid stability campaign"
git push origin main
```

The commit MUST land on origin/main before the task is considered closed. The completion summary MUST include the commit hash and confirmation that `git status` returned clean.
