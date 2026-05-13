# Codex Task 030 — Refinery MVP: Two-Stage Decision on F1 vs F2 (Pure Algebraic, Existing Campaign Data Only)

## 0. Context

This is the minimum-viable validation of the Instrument-Aware Equation Refinery concept. It is scoped tightly: one fixture, one form pair, one decision. It uses only V4-clean Layer 1 outputs and committed campaign report JSONs from Tasks 026c-prime, 029a/c, and 017c. It does not touch the V3-shape Layer 2 refinery module, does not introduce new substrate primitives, does not build new measurement infrastructure.

**The MVP exists to validate that the substrate floor V4 has accumulated through the chain-property campaigns is sufficient to drive a typed refinery decision.** If the MVP succeeds, the V4-native refinery rebuild proceeds to design as a proper Layer 2 module. If it fails, the substrate floor needs extending before any refinery rebuild is attempted.

**Three possible MVP outcomes:**

- `mvp_validates_decision_law` — script produces a typed decision that matches the pre-registered expected outcome on F1 vs F2 pure_algebraic, and the decision is derived cleanly from a Pareto comparison of burden vectors built from existing campaign data.
- `mvp_decision_law_partial` — script produces a typed decision but one or more burden vector dimensions are unavailable from existing data, or the decision outcome diverges from pre-registration on some dimensions. The decision law is implementable but the substrate floor is partially incomplete.
- `mvp_decision_law_refuted` — script cannot produce a typed decision from existing data, or the produced decision is structurally incoherent. The V4-native refinery rebuild needs more substrate work first.

All three are legitimate outcomes.

**Task renumbering note.** The previously-banked Task 030 (operation-level Sterbenz annotation) is renamed to **Task 031** to take this slot. The Sterbenz annotation work remains valuable but the refinery MVP is the higher-leverage move post-017c — it tests whether V4 substrate is ready to drive the capability that motivated the V4 rebuild in the first place.

---

## 1. Repository / Baseline

**Repository:** `~/projects/V4/Lloyd_Engine_V4`

**Baseline HEAD:** post-017c on `origin/main` (commit `ac54506` or descendant). Codex starts from current `origin/main`.

**Test baseline:** 622 passing (post-017c).

**Test count target:** previous baseline + ~14 new tests. Target ~636 against the 622 baseline.

**Sequencing dependency:** this task assumes Tasks 017c (`ac54506` or descendant), 029c (`975a3fb` or descendant), and 026c-prime have all landed and their report JSONs are committed. If any of those reports is missing, **halt and report**.

## 2. Task Goal

Implement and validate the two-stage refinery decision law on a single form pair:

1. **Stage 1 — Geometry admissibility gate.** Confirm the candidate form is in the same declared equivalence family as the reference form (same fixture, same operand grid, same algebraic identity, compatible calibration status). For F1 vs F2 of pure_algebraic this trivially passes — the gate exists so the protocol is exercised even when the case is trivial.

2. **Stage 2 — Burden vector comparison.** Extract a typed burden vector for each form from existing campaign reports. Apply componentwise Pareto comparison. Produce one of four typed outcomes: `accepted`, `rejected`, `forms_structurally_tied`, or `comparison_indeterminate`.

The decision law from Gemini's design contribution (which William refined and locked):

> A candidate is accepted only if: (1) it satisfies the declared equivalence/geometry protocol; (2) it preserves required statuses and calibration channels; (3) it does not worsen any required burden component; (4) it improves at least one declared burden component; (5) ties remain ties unless a declared typed comparator resolves them.

No hidden weighted aggregation. No single score. Burden is a vector and the comparison is Pareto-dominance.

**The MVP target form pair:** F1 (R² − f_direct) versus F2 (R² − 1 + x) in the pure_algebraic fixture. Both equal zero on the constraint surface; both are algebraically equivalent rewrites of the same identity; both have full campaign coverage in 017c, 029a/c, and 026c-prime.

## 3. Source Labelling

- **V4-surface (load-bearing):** Layer 1 primitives (already used by the campaigns whose JSONs are consumed here), the four chain-property fixtures, the canonical 137-point grid, byte-stability discipline, axioms 1–12.
- **Theorem-derived:** the linear-in-u_p separability empirically validated at R² = 1.0 across the precision battery (Theorem 2 + 017c result) — used here as the provenance lineage for the `b_k` burden dimension.
- **Proposal evidence:** the specific burden vector dimensions enumerated in §6.3 (subject to MVP validation); the Pareto-dominance decision protocol; the four typed outcome categories; the geometry admissibility gate's required field set.
- **V3 reference (concept only):** the V3 refinery's purpose — typed rewrite evaluation, accepted-rewrite protocol — is the destination this MVP validates the path toward. V3 implementation, status enums, score functions, parent-set inheritance do not transfer. The V3-shape Layer 2 module at `src/lloyd_v4/refinery/` is not imported, called, or referenced by this MVP.

## 4. Design Principles

1. **No new substrate primitives.** All burden dimensions trace to existing measurements committed in campaign JSONs.
2. **No Layer 2 module.** This MVP lives at the evals layer in `src/lloyd_v4/evals/refinery_mvp/`. Lifting to Layer 2 substrate is a separate future task contingent on MVP success.
3. **No new measurement.** Burden vectors are constructed by reading existing report JSONs from 017c, 029a/c, and 026c-prime. The MVP does not re-run any campaign.
4. **No V3-shape import.** The existing `src/lloyd_v4/refinery/` module is not touched. Its exports are not imported. A grep test enforces this.
5. **Pre-registration discipline.** Expected MVP outcome on F1 vs F2 pure_algebraic is locked before the script runs. Same byte-stability protocol as 029c/017c.
6. **Burden vector with explicit dimensions and explicit provenance.** Each dimension records the report JSON path and field name it was extracted from. No hidden derived quantities.
7. **Pareto-dominance comparison only.** No weighted aggregation. No single score. The four typed outcomes are first-class; `forms_structurally_tied` and `comparison_indeterminate` are not edge cases.
8. **Geometry admissibility gate exercised even when trivial.** F1 and F2 trivially pass on the same algebraic-identity declaration. The protocol still runs through the gate so the MVP demonstrates both stages.
9. **Discovery and promotion separated.** If the MVP reveals a burden dimension that suggests a new substrate concept, it is logged as a forward observation. No substrate promotion happens in this task.
10. **No physics-interpretive language.**

## 5. Primitive-Sufficiency Gate

| Concept used | Source | Status |
|---|---|---|
| `b_k` point estimate and CI per (fixture, path) | `Build_Docs/Reports/task017c_multi_precision_theorem2/precision_aggregate.json` | Read existing |
| Lattice class and max integer residual per (fixture, path) | `Build_Docs/Reports/task029c_cbrt_four_form_battery/cbrt_lattice_campaign_output.json` (cbrt), `Build_Docs/Reports/task029a*/lattice_campaign_output.json` (others) | Read existing |
| Polarity classification per (fixture, path pair) | `Build_Docs/Reports/task026c_prime*/polarity_grid_stability.json` (or post-029c equivalent) | Read existing |
| Calibration zero preservation per (fixture, path) | F3 sentinel result from any of the above campaigns | Read existing |
| Operation chain depth per path | Counted directly from fixture source files | Static, computed once |
| Pareto-dominance comparison | Pure-Python set/list operations | No substrate primitive needed |
| Geometry admissibility gate | Declared metadata fields (fixture name, operand grid, algebraic identity label) | Pure metadata comparison |

**Axiom 12 disposition.** Every burden dimension has measurement provenance lineage to a Layer 1 primitive: `b_k` traces to `typed_finite_difference` via 017c's fits; lattice class and integer residual trace to the 029-series lattice campaign; polarity classification traces to the polarity grid stability framework; calibration zero traces to the F3 sentinel discipline. No dimension is minted at evals layer without parent-layer provenance.

**Axiom 11 disposition.** No named mathematical content imports. No hardcoded mathematical constants. The MVP reads JSON, extracts numeric fields, applies comparison logic. All admitted.

## 6. Required Deliverables

### 6.1 Pre-registration document

`Build_Docs/Reports/task030_refinery_mvp/pre_registration.md`

Committed in a dedicated commit before any MVP code runs. Structured in two sections:

**Section A — Decision law (locked before script runs)**

1. The geometry admissibility gate's required field set.
2. The burden vector's declared dimensions with measurement provenance per dimension.
3. The Pareto-dominance comparison rule (componentwise; no aggregation; ties handled explicitly).
4. The four typed outcome categories.

**Section B — Expected outcome on F1 vs F2 pure_algebraic (pre-registered prediction)**

Based on existing data, the pre-registered expected outcome with justification per burden dimension. Best current read:

| Burden dimension | F1 (reference) | F2 (candidate) | Direction |
|---|---|---|---|
| `b_k` point estimate (CI) | (from 017c) | (from 017c) | overlap likely → tied or indeterminate on this dimension |
| `lattice_class` | `integer_lattice` | `non_integer_lattice` | F1 lower burden |
| `max_integer_residual` | 0.0 | 0.25 | F1 lower burden |
| `polarity_class` (paired) | `grid_stable_polarity_coupling` | `grid_stable_polarity_coupling` | tied (paired classification) |
| `calibration_zero_preserved` | `false` (non-calibration path) | `false` (non-calibration path) | tied |
| `operation_chain_depth` | 1 | 2 | F1 lower burden |

**Pre-registered MVP-level expected outcome:** F1 dominates F2 on at least two burden dimensions and is no worse on the rest. The decision outcome is `accepted` if F1 is the candidate and F2 the reference, or `rejected` if the assignment is reversed. The MVP runs with F2 as reference and F1 as candidate, so the pre-registered outcome is **`accepted`** with documented dominance on `lattice_class`, `max_integer_residual`, and `operation_chain_depth`.

The pre-registration commit message must be exactly:

```
Task 030 pre-registration: refinery MVP decision law and expected outcome

Predictions registered before MVP code execution. Predictions are not to
be edited after this commit. Subsequent commits carry the MVP run and
observed results.
```

### 6.2 Geometry admissibility module

`src/lloyd_v4/evals/refinery_mvp/geometry_admissibility.py`

Exposes a single function `check_geometry_admissibility(reference_form_metadata, candidate_form_metadata) -> AdmissibilityResult`.

The metadata input includes: `fixture_name`, `operand_grid_label`, `declared_algebraic_identity`, `calibration_status`, `domain_stratum_label`.

The function returns one of: `admissible`, `inadmissible_fixture_mismatch`, `inadmissible_grid_mismatch`, `inadmissible_identity_mismatch`, `inadmissible_calibration_mismatch`, `inadmissible_domain_mismatch`. The result records which field caused the mismatch for any inadmissible outcome.

For F1 vs F2 of pure_algebraic the result is `admissible` (both forms declare the same fixture, grid, identity, calibration status, and domain).

### 6.3 Burden vector extractor module

`src/lloyd_v4/evals/refinery_mvp/burden_vector.py`

Exposes `extract_burden_vector(fixture_name, path_name, campaign_reports_root) -> BurdenVector`.

The `BurdenVector` is a typed dataclass-like object (no Pydantic, no scipy — pure Python or numpy types) with fields:

- `b_k_point_estimate: float`
- `b_k_ci_lower: float`
- `b_k_ci_upper: float`
- `lattice_class: str` (one of `integer_lattice`, `non_integer_lattice`, `unclassified`)
- `max_integer_residual: float`
- `polarity_class: str` (one of `grid_stable_polarity_coupling`, `depolarized_invariant`, `open_underpowered`, `not_paired`)
- `calibration_zero_preserved: bool`
- `operation_chain_depth: int`
- `provenance: dict` — for each field, records `(report_path, field_path_in_json)` or `(source_file, computed_method)` for `operation_chain_depth`.

If any field cannot be extracted from the campaign reports, the field is set to a typed sentinel (`b_k_unavailable`, `lattice_class_unavailable`, etc.) rather than `None` or `NaN`, and the provenance entry records the absence reason.

### 6.4 Pareto decision module

`src/lloyd_v4/evals/refinery_mvp/pareto_decision.py`

Exposes `compare_burden_vectors(reference: BurdenVector, candidate: BurdenVector, burden_policy) -> ParetoComparisonResult`.

The `burden_policy` declares, per dimension, the "better" direction (`lower`, `higher`, `paired_equal`, `equal_required`) and whether the dimension is `required` or `optional`. For the MVP, the default policy is:

| Dimension | Better direction | Required? |
|---|---|---|
| `b_k_point_estimate` | `lower` (with CI overlap check) | required |
| `lattice_class` | `lower` (where `integer_lattice` < `non_integer_lattice` < `unclassified`) | required |
| `max_integer_residual` | `lower` | required |
| `polarity_class` | `paired_equal` | required (must match) |
| `calibration_zero_preserved` | `equal_required` (must match) | required |
| `operation_chain_depth` | `lower` | required |

The function returns one of:
- `accepted` — candidate dominates reference: no required dimension is worse, at least one is strictly better, all `equal_required` and `paired_equal` dimensions match.
- `rejected` — reference dominates candidate (symmetric).
- `forms_structurally_tied` — equal on every required dimension.
- `comparison_indeterminate` — neither dominates and not all-equal; some dimensions favor reference, some favor candidate; or required `equal_required` / `paired_equal` dimensions mismatch.

The result records per-dimension comparison breakdown.

### 6.5 MVP orchestrator

`src/lloyd_v4/evals/refinery_mvp/mvp_run.py`

Top-level callable `run_mvp_decision(reference_form, candidate_form, campaign_reports_root) -> MvpDecisionRecord`.

Sequences: admissibility check → if admissible, extract burden vectors → compare → produce decision record. If inadmissible, the decision record records the admissibility failure and skips burden comparison.

### 6.6 MVP decision record JSON

`Build_Docs/Reports/task030_refinery_mvp/mvp_decision_record.json`

Byte-stable. Contains: admissibility result, both burden vectors with provenance, comparison breakdown per dimension, final outcome, match against pre-registration.

### 6.7 Burden vectors JSON

`Build_Docs/Reports/task030_refinery_mvp/burden_vectors.json`

Byte-stable. The two burden vectors (F1 and F2 of pure_algebraic) with full provenance fields. Separated from the decision record so future tasks can read burden vectors without re-running the MVP.

### 6.8 Headline classification record

`Build_Docs/Reports/task030_refinery_mvp/headline_classification.md`

One of `mvp_validates_decision_law` / `mvp_decision_law_partial` / `mvp_decision_law_refuted` with one-paragraph justification.

### 6.9 Task summary

`Build_Docs/Reports/task030_refinery_mvp_summary.md`

Standard structure. Must include:

- Pre-registration commit hash.
- Geometry admissibility result.
- Burden vector tables (both forms, all fields, with provenance).
- Per-dimension comparison breakdown.
- Decision outcome.
- Match against pre-registered expected outcome.
- Headline classification with justification.
- Tests, byte-stability, discipline gates.
- Forward observations — what did the MVP reveal about (a) which burden dimensions were cleanly available from existing data and which had to use sentinels, (b) whether the Pareto comparison resolved cleanly or produced `comparison_indeterminate`, (c) what extensions the substrate would need to enable multi-form, multi-fixture, or rewrite-generation refinery operation. **No next-task drafts.**

## 7. Required Tests

Approximately **14 new tests** in `tests/test_task030_refinery_mvp.py`.

### 7.1 Pre-task evidence (~2 tests)

- Confirm 017c, 029c, and 026c-prime report JSONs exist at expected paths; halt if not.
- Record HEAD hash and pre-existing test count.

### 7.2 Geometry admissibility tests (~3 tests)

- F1 vs F2 pure_algebraic produces `admissible`.
- Mismatched fixture produces `inadmissible_fixture_mismatch`.
- The admissibility result records the specific field that caused any mismatch.

### 7.3 Burden vector extraction tests (~4 tests)

- Burden vector for F1 pure_algebraic populates `b_k`, `lattice_class`, `max_integer_residual`, `polarity_class`, `calibration_zero_preserved`, `operation_chain_depth` from existing JSONs.
- Burden vector for F2 pure_algebraic populates the same fields.
- Provenance dictionary records report path and field path for every populated dimension.
- Missing-data sentinel is used (not `None` or `NaN`) when a field cannot be extracted.

### 7.4 Pareto comparison tests (~3 tests)

- F1 vs F2 produces a typed outcome (one of the four).
- The comparison result records per-dimension breakdown.
- Tied input vectors produce `forms_structurally_tied`.

### 7.5 Byte-stability tests (~2 tests)

- `mvp_decision_record.json` byte-identical between two consecutive runs.
- `pre_registration.md` byte-identical to the committed file at task close.

### 7.6 Discipline gate tests (~5 tests)

- No imports from `src/lloyd_v4/refinery/` (V3-shape module not touched). Grep test on all new files.
- No `scipy`, `sympy`, `mpmath`, `numpy.special`, `scipy.special`, `statsmodels` imports.
- No hardcoded mathematical constants.
- `layer_manifest.json` byte-identical to start.
- No physics-interpretive language (grep).

## 8. Required Commands

1. `git status` — clean.
2. `git log -1 --oneline` — record HEAD.
3. Confirm 017c, 029c, 026c-prime reports exist on `origin/main`.
4. `pytest -q tests/` — baseline.
5. Create `pre_registration.md` per §6.1.
6. `git add Build_Docs/Reports/task030_refinery_mvp/pre_registration.md`
7. `git commit -m "Task 030 pre-registration: refinery MVP decision law and expected outcome..."` (full message per §6.1)
8. Record pre-registration commit hash.
9. Implement modules and tests.
10. `pytest -q tests/` — confirm all pass.
11. Run MVP; write `mvp_decision_record.json` and `burden_vectors.json`.
12. Run MVP a second time; diff against repository copies; byte-identical.
13. Write `headline_classification.md` and `task030_refinery_mvp_summary.md`.
14. `pytest -q tests/` — final.
15. `git add -A && git commit -m "Task 030: refinery MVP — <headline>" && git push origin main`.
16. `git status` — clean.
17. `git log -2 --oneline` — both commits visible on `origin/main`.

## 9. Non-Goals (Loud and Explicit)

- **NOT** modifying any substrate primitive.
- **NOT** modifying `layer_manifest.json`.
- **NOT** building a Layer 2 module. The MVP lives at evals layer.
- **NOT** importing from `src/lloyd_v4/refinery/` (the V3-shape draft).
- **NOT** generating new rewrite candidates. The MVP uses F1 and F2 as already-defined campaign paths.
- **NOT** measuring anything new. The MVP reads existing JSON reports.
- **NOT** extending to other fixtures or other form pairs. F1 vs F2 pure_algebraic only.
- **NOT** implementing diagnostic-vs-evaluation selection policies. The MVP runs the evaluation policy implicitly via the default burden policy.
- **NOT** promoting any new concept to substrate.
- **NOT** drafting Task 031 (the renumbered Sterbenz annotation), Task 032 (the substrate refinery rebuild), or any forward task in the summary.
- **NOT** using weighted aggregation or single-score collapse of the burden vector. The decision is Pareto-dominance only.
- **NOT** dressing the MVP in V3-shape vocabulary because the V3 refinery used a particular term. V4-native naming.

## 10. Completion Report

`Build_Docs/Reports/task030_refinery_mvp_summary.md`, in this order:

1. **Scope.**
2. **Pre-registration commit hash and date.**
3. **Geometry admissibility result** for F1 vs F2 pure_algebraic.
4. **Burden vector tables:**

   | Dimension | F1 value | F1 provenance | F2 value | F2 provenance |
   |---|---|---|---|---|

5. **Per-dimension comparison:**

   | Dimension | Direction | F1 vs F2 | Winner |
   |---|---|---|---|

6. **Decision outcome** with one-paragraph justification.
7. **Match against pre-registered expected outcome.**
8. **Headline classification** with justification.
9. **Tests** — total count, new tests added, pytest result.
10. **Byte-stability confirmation.**
11. **Discipline gates** explicit confirmation, including the V3-shape no-import grep result.
12. **Files changed.**
13. **Forward observations** — three categories required: (a) which burden dimensions were cleanly available vs required sentinels, (b) how the Pareto comparison resolved (clean dominance vs tied vs indeterminate), (c) what extensions the substrate would need for multi-form / multi-fixture / rewrite-generation / Layer 2 refinery operation. **No next-task drafts.**

## 11. Acceptance Criteria

1. Pre-registration committed as its own commit before any MVP code ran.
2. All pre-existing tests pass.
3. All new tests pass (~14 new).
4. F1 vs F2 pure_algebraic admissibility result is `admissible`.
5. Burden vectors for both forms have at least four of six declared dimensions populated (sentinel for unavailable).
6. Pareto comparison produces one of the four typed outcomes.
7. `mvp_decision_record.json` byte-stable.
8. `burden_vectors.json` byte-stable.
9. `pre_registration.md` byte-identical to committed file.
10. `layer_manifest.json` byte-identical to start.
11. No imports from `src/lloyd_v4/refinery/` in any new file.
12. No forbidden imports or patterns.
13. Headline classification recorded.
14. Forward observations recorded without drafting next task.
15. Final commit pushed to `origin/main`. `git status` clean. Both commits on `origin/main` in order.

## 12. Discipline Notes

### Axiom 10 — V3 reference-only (with non-reflexive interpretation)

The V3 refinery concept — typed rewrite evaluation, accepted-rewrite protocol, slag/burden vocabulary — is reference-only at the conceptual level. The V3 refinery's *purpose* informs what this MVP validates the path toward. The V3 refinery's *implementation*, status enum shapes, parent-set inheritance, and data structures do not transfer.

The discipline is to question V3-shape choices, not to reject them reflexively. Where the V4-native derivation would land on the same shape as V3's, the agreement is evidence the shape is right. Where V4-native derivation lands somewhere different, the divergence is deliberate and documented.

The V3-shape Layer 2 module at `src/lloyd_v4/refinery/` is not touched by this MVP. The grep test in §7.6 enforces this. The module itself is not being deprecated by this task — it remains as reference and may be partially salvaged in the future Layer 2 rebuild after this MVP validates the substrate floor.

### Axiom 11 — Epistemic stance only

No named numerical-analysis content imported. The burden vector dimensions are V4-native observables. Sterbenz, Wilkinson, Kahan, Higham etc. are comparison cases for future audit tasks, not substrate building blocks of the MVP.

### Axiom 12 — Self-derivation

Every burden vector dimension traces to a Layer 1 primitive via existing campaign measurement provenance. The MVP introduces no new concept that does not have parent-layer derivation. The provenance dictionary in every burden vector records this lineage explicitly.

### Discovery and promotion separated

If the MVP reveals that a burden dimension is structurally inadequate, or that a new dimension is needed, or that some forms produce structurally novel results — those are forward observations only. No new substrate concept is minted in this task. The future Layer 2 refinery rebuild task is where promotion decisions get made, with their own gates.

### Pre-registration is non-negotiable

The expected outcome on F1 vs F2 pure_algebraic is locked before the script runs. Post-hoc adjustment is forbidden. If the observed outcome diverges from pre-registration, the divergence is reported honestly and the headline records `mvp_decision_law_partial` rather than `mvp_validates_decision_law`.

### Byte-stability

All MVP outputs are byte-stable. Run the MVP twice. Diff. The diff is empty.

### Git discipline non-negotiable

Pre-registration commit lands on `origin/main` before MVP code runs. Main task commit lands before the task is considered closed. `git status` clean. Summary references both commit hashes.

---

## Appendix A — The two-stage decision law (formal statement)

**Stage 1: Geometry admissibility gate.**

Given two forms with declared metadata, the gate returns `admissible` if and only if all of:

- `fixture_name` matches
- `operand_grid_label` matches
- `declared_algebraic_identity` matches
- `calibration_status` is compatible (both calibration, or both non-calibration, or both with the same declared calibration channel)
- `domain_stratum_label` matches

Any mismatch produces a typed inadmissibility outcome identifying the field. An inadmissible pair is not "different burden" — it is a different object, and burden comparison is not performed.

**Stage 2: Burden vector comparison.**

Given two admissible forms with extracted burden vectors and a declared burden policy:

- For each dimension declared `required` in the policy, the comparison applies the declared "better" direction (`lower`, `higher`, `paired_equal`, `equal_required`).
- For `paired_equal` and `equal_required` dimensions, mismatch produces `comparison_indeterminate` (these are constraint dimensions, not comparison dimensions).
- For `lower` and `higher` dimensions, the standard Pareto rule applies: candidate is accepted iff no required dimension is worse and at least one required dimension is strictly better.
- Symmetric for rejection.
- All-equal across required dimensions produces `forms_structurally_tied`.
- Non-dominance without all-equal produces `comparison_indeterminate`.

The four outcomes — `accepted`, `rejected`, `forms_structurally_tied`, `comparison_indeterminate` — are exhaustive and mutually exclusive. The MVP must produce exactly one.

## Appendix B — Why F1 vs F2 pure_algebraic is the right MVP target

Three reasons:

1. **Full campaign coverage.** Both forms have measurements in 017c (b_k fits), 029a/c (lattice grain, classification), and 026c-prime (polarity coupling). No new measurement needed.
2. **Non-trivial expected outcome.** F1 and F2 differ on at least two burden dimensions (lattice_class and operation_chain_depth), so the Pareto comparison should produce a clean `accepted` or `rejected` rather than a trivial tie. This exercises the decision law non-trivially.
3. **No diagnostic-form complications.** F2 is the form that carries the Sterbenz boundary signal and the non-integer lattice grain — it would be the diagnostic-policy choice over F1 in a diagnostic context. The MVP uses evaluation policy only, where lower burden wins. The diagnostic-policy work is deferred to a future task. Choosing F1 vs F2 makes the evaluation-policy outcome clean while documenting the diagnostic-policy tension as a forward observation.

## Appendix C — What the MVP validates and what it does not

**Validates:**

- The two-stage decision law is implementable on V4-clean substrate.
- The burden vector concept is operational on existing campaign data.
- Pareto comparison produces typed outcomes including ties and indeterminates as first-class.
- The substrate floor accumulated through Tasks 026c-prime, 029a/c, and 017c is sufficient to drive at least one refinery decision.

**Does not validate (and is not intended to):**

- Rewrite-candidate *generation* (the MVP uses pre-existing campaign paths).
- Multi-fixture refinery operation (only pure_algebraic).
- Multi-form-pair operation (only F1 vs F2).
- Diagnostic-vs-evaluation selection policy.
- Geometry admissibility on forms that genuinely differ in algebraic identity.
- The proper Layer 2 substrate rebuild (parent set, status family, transition rules, protocols).
- Generalisation of the burden vector dimensions to forms outside the chain-property fixture family.

A successful MVP demonstrates the path forward is clear. It does not demonstrate the destination has been reached.
