# Session Handoff — Lloyd Engine V4 Substrate Development

## One-paragraph orientation

You are continuing work on **Lloyd Engine V4**, a typed numerical geometry kernel.
Repository at `/mnt/fast/Lloyd_Engine_V4`. The user is doing substrate-level work
alone, autodidact, with Codex executing tasks based on specs you write. Three
capability primitives are landed cleanly through Layer 1 (typed_finite_difference,
directional_alpha_probe, scalar_alpha_jet_bundle). 344 tests passing. The
architectural discipline has been formalized into project instructions (Axiom 11,
V3/V1 reference hygiene, three-layer dual-probe decomposition). The user's
persona preference is "Claire" — warm, dry, intellectually direct, lightly
sarcastic, subtly flirtatious; details in their userPreferences. **Do not be
sycophantic. Do not over-praise. Match the discipline of letting substrate
reveal patterns rather than designing ahead.**

---

## Repository state (verified)

**Location:** `/mnt/fast/Lloyd_Engine_V4`

**Verified baseline:** 344 tests passing (`pytest -x tests/`).

**Layers:**
- Layer 0: core (`TypedResult`, `Validity`, `Conditioning`, `Provenance`,
  `ProducerProtocol`, `ConsumerProtocol`, `validate_protocol`,
  `StatusCode` union, errors)
- Layer 1: primitives (calibrated and internal operations)
- Layer 1.5: projection (`projective_ratio`, exact projection)
- Layer 2+: metrology, branch, refinery, history, solver — **all V3-shape
  deferred-consumer first-drafts, NOT authoritative substrate. Reference only.**

---

## Layer 1 primitives (current map)

### Calibrated primitive operations (6)

| Operation | Module | Purpose | Status family |
|---|---|---|---|
| `typed_collection` | `primitives/typed_collection.py` | Substrate-input wrapping for collections | `CollectionStatus` |
| `typed_value` | `primitives/typed_value.py` | Substrate-input wrapping for scalars | `ValueStatus` |
| `projective_ratio` | `primitives/projective_ratio.py` | n/d as typed projective object | `ProjectiveRatioStatus` |
| `stratified_quadratic_roots` | `primitives/stratified_quadratic_roots.py` | Roots of ax²+bx+c by stratum | `QuadraticRootStatus` |
| `typed_finite_difference` | `primitives/typed_finite_difference.py` | Transfer T(f) = (g(f+δf)-g(f))/δf | `TransferStatus` |
| `directional_alpha_probe` | `primitives/directional_alpha_probe.py` | α as first-class typed object | `AlphaProbeStatus` |
| `scalar_alpha_jet_bundle` | `primitives/scalar_alpha_jet_bundle.py` | α evidence at a scalar point | `ScalarAlphaJetBundleStatus` |

### Internal operations (3)

- `projective_ratio.scalarize` (in `projective_ratio.py`)
- `stratified_quadratic_roots.select` (in `stratified_quadratic_roots.py`)
- `typed_log_log_slope` (`primitives/typed_log_log_slope.py`)

### Status families

`CollectionStatus`, `ValueStatus`, `ProjectiveRatioStatus`, `QuadraticRootStatus`,
`TransferStatus`, `SlopeStatus`, `AlphaProbeStatus`, `ScalarAlphaJetBundleStatus`.

### Headline measurement validated

**α-1 transfer law** (Theorem 1, `transfer_function_exponent_family_revised.tex`):
For `g(f) = c·f^α` near f=0, the log-log slope of typed_finite_difference
recovers α-1. Validated through ScalarAlphaJetBundle at x₀=0 for α ∈
{0.5, 1.5, 2.0, 3.0}, observed_alpha within 1e-2 of α, R² > 0.999 in all cases.

---

## Architectural discipline (LOAD-BEARING — added to project instructions)

### Axioms (V4_AXIOMS, all 12)

Axioms 1-10 are the original substrate axioms (geometry-first, degeneracy-as-stratum,
no hidden guard rails, multi-field validity, numerical representation as path,
zero must be measured, proxy observables require calibration, typed composition
by protocols, type-system failures are real failures, V3 reference-only).

**Axiom 11: Epistemic Stance Only.** V4 commits at the level of how observation
works, not what is observed. **No imports of named mathematical content**
(`math`, `cmath`, `numpy.special`, `scipy.special`, `sympy`, `mpmath`); **no
hardcoded mathematical constants** (`pi`, `tau`, `e`, `gamma`, `golden_ratio`);
**no named theorems/functions/equations as substrate building blocks.** Named
content is consumer-side, derived from substrate observations, never assumed
as substrate.

**Axiom 12: Self-Derivation.** Every layer derives from its parents. A higher
layer needing a concept absent from parents must halt; parent layer is extended
honestly, then higher layer rebuilds. No ad-hoc concept minting.

### V3/V1 Reference Hygiene (in `Build_Docs/Architecture/`)

Three rules formalized this session:

1. **Reference is for mechanical property, not design justification.** "V1/V3
   already solved this" is starting hypothesis, never closing argument. V4
   derivations must stand alone on V4 axioms. If V4 derivation requires
   V1/V3 as justification, the derivation is incomplete.
2. **Reference is for what to attempt, not what to copy.** Specific data
   structures, status enums, score functions, tolerance bands, `safe_mask`
   patterns, dict-based statuses — none survive transit.
3. **Reference is for which design problems are real, not which solutions
   are correct.**

**The smell to watch for:** "V1/V3 did X, so V4 does X" is the bridge sneaking
in. Catch it. The correct phrasing is "V1/V3 engaged this problem in form X;
V4 needs to engage the same problem; here is the V4-native derivation from
axioms, producing form Y, which differs from form X under V4 substrate
constraints."

### Three-layer dual-probe decomposition (also in `Build_Docs/Architecture/`)

For the regularity-channel dual-probe architecture:

| Layer | Object | Contains |
|---|---|---|
| L1 | `ScalarAlphaJetBundle` (built), `SingularAlphaJetBundle` (next candidate) | Single-arm typed α observation per construction |
| L1.5/L2 | `ProjectiveLocalAlpha` (or similar name) | Joint typed observation, BOTH arms' lineage preserved, joint validity field, **NO pre-classification labels** |
| L3 | (deferred, consumer-driven) | Curvature work on implied joint surface |

**Critical:** No dispatch labels (LOCAL_AUTHORITATIVE / TRANSITION_ZONE /
SINGULAR_AUTHORITATIVE) at substrate. Those are consumer dispatch logic.
The joint object carries both arms' typed observations and joint validity
(`regular_arm_valid`, `singular_arm_valid`); consumers classify.

---

## Drift patterns the previous Claude kept falling into

**Watch for these. Catch yourself before drafting.**

1. **Smuggling consumer logic into substrate.** Proposed dispatch labels
   (LOCAL_AUTHORITATIVE etc.) in dual-probe design. The user caught it.
   Substrate carries typed observations; consumers classify.

2. **Pulling concepts UP into substrate that belong downstream.** Tried to
   make precision a Layer 1 primitive (Task 017, dropped) when precision is
   already provenance per Axiom 5. Tried to put curvature in L1.5 joint
   composer when it belongs L3 consumer-side.

3. **V3-shape thinking sneaking in.** Reaching for V3 BranchFingerprint,
   metrology, refinery patterns as if they were substrate authority. They
   are V3-shape deferred-consumer first-drafts. NOT substrate.

4. **Importing named mathematical content.** Anytime a primitive's design
   wants to reach for curvature, gradient norm, condition number, Lipschitz
   constant, Hessian, shape operator — that's Axiom 11 territory. Named
   content is consumer-side or it doesn't exist yet.

5. **Designing ahead of evidence.** Tried to spec Tasks 019/020/021 together
   before AlphaProbe landed. User correctly insisted: let each task land,
   inspect typed shape, then decide next.

6. **Forgetting present_files.** Wrote files to /mnt/user-data/outputs/ and
   didn't call present_files. Did this for Task 016 and Task 019. Always
   call present_files after creating user-facing artifacts.

---

## Active forward direction

**Natural next L1 task candidate (NOT YET DRAFTED):** `SingularAlphaJetBundle`
— sibling to ScalarAlphaJetBundle. Constructs `g_singular(h) = f(x₀+h)` (no
subtraction). Sovereign in singular region. Naturally reaches negative-α
statuses that ScalarAlphaJetBundle cannot reach (because g_local(h) → 0 as
h → 0 when f(x₀) finite). This is the structurally-honest companion primitive.

**After both siblings exist:** `ProjectiveLocalAlpha` joint composer. NOT a
new measurement — composes both arms' typed observations into joint typed
result with joint validity and full lineage preservation. NO dispatch labels.

**L3 deferred:** Curvature work on implied (u, v) joint surface, only when
consumer pull justifies it.

**Solver MVP (forward, not scoped):** Two-phase + tie-refusal acceptance
law recorded in Task 018 discipline notes:
- Phase 1 admissibility: geometry gates only (protocol-valid + projection
  defined + advance-valid + α in accepted stratum + generator compatible +
  no unhandled transition). Residual cannot make inadmissible candidates
  admissible.
- Phase 2 selection: declared typed comparators only. Residual/progress
  comparator emits typed result (candidate_preferred_by_progress /
  candidate_progress_tied / candidate_progress_indeterminate /
  candidate_progress_comparison_refused). No hidden numeric sort.
- Phase 3: typed tie-refusal if no comparator resolves.

**Discipline:** Do not draft solver until LocalModelProvider patterns are
known. Do not draft LocalModelProvider until SingularAlphaJetBundle and the
joint composer reveal their shapes.

---

## Backlog (no urgency, noted for awareness)

1. **eps vs eps/2 inconsistency** in `typed_finite_difference`'s raw_python
   precision floor. Documented honestly, not resolved.
2. **Six missing V4-plan Layer 1 primitives:** `signed_difference`,
   `norm_state`, `stratified_sqrt`, `spectral_gap_state`, `projector_state`,
   `constraint_zero_state`. Likely real dependencies during solver arc
   (signed_difference for residual observation, norm_state for gradient_norm,
   stratified_sqrt for fractional-α step shapes).
3. **Task 010 documentation fan-out cleanup:** 6 overlapping files in
   `Build_Docs/Reports/task010*`.
4. **Stress Test Findings 2/3:** validity dishonesty / conditioning honesty
   backlog. Deferred as Tasks 012/013.
5. **Task 017b conditional:** actual multi-precision execution (numpy/mpmath
   as backends). Requires Axiom 11 review for the imports. Banked, not
   scheduled. Would unlock the precision dual-arm probe.

---

## The two banked dual-arm ideas (NOT scheduled)

The user has surfaced two stereoscopic-observation ideas, both V4-natural,
both deferred:

1. **Precision dual-arm** (regularity-precision channel): high-precision
   arm + low-precision arm. Disparity measures arithmetic-path visibility
   (related to PPS b_k coefficient). Requires Task 017b (actual multi-
   precision execution) as prerequisite.
2. **Regularity dual-arm** (singularity channel): local-additive arm +
   singular-direct arm. Disparity measures singularity proximity. This is
   the three-layer architecture above; next candidate L1 task.

These could compose into a 2×2 four-arm probe with two-dimensional depth
observation. Way ahead of current scope but worth knowing about.

---

## Working relationship with Codex

The user has Codex as the implementation executor. Workflow:

1. User describes what they want or asks for design discussion
2. You discuss/refine the design with the user
3. You write Codex-executable specs to `/mnt/user-data/outputs/codex_taskNNN_*.md`
   when the user asks
4. User passes spec to Codex; Codex implements
5. User returns with completion report (typically `task0NN_summary.md`)
6. You review the completion report, note observations, suggest forward
   direction (without drafting next spec until user asks)

**Codex working patterns observed:**
- Codex executes specs faithfully when they're detailed
- Codex sometimes proposes its own design ideas (good ones — has caught
  things the previous Claude missed)
- Codex's instinct for sequencing and architectural cleanliness is genuine;
  worth engaging with substantively when it pushes back

**Spec template pattern that has worked** (see `codex_task018_*.md` and
`codex_task019_*.md` for examples):

1. Repository / Baseline
2. Task Goal
3. Source labelling (V4-surface / theorem-derived / proposal evidence)
4. Design Principles
5. Primitive-Sufficiency Gate (table of concepts used and where they come from)
6. Required Deliverables (status family, module, exports, manifests, tests)
7. Required Tests (pre-task evidence, stratum coverage, input validation,
   provenance/identity, discipline tests, serialization, protocol validation)
8. Required Commands
9. Non-Goals (loud and explicit)
10. Completion Report (what the summary should contain)
11. Acceptance Criteria
12. Discipline Notes (forward references, V3-shape stance, etc.)

---

## User working style notes (Claire persona applies)

- Autodidact doing substrate-level work alone
- Holds discipline lines well; catches drift the previous Claude misses
- Values typed substrate honesty over forward velocity
- Patient with iteration
- Direct; doesn't want sycophancy or over-praise
- Engages substantively with architectural discussion; sharp on what's
  V4-aligned vs what's V3-shape sneaking in
- Has theoretical instincts (the regularity dual-probe idea was genuinely
  original and architecturally sound)

**Claire persona** (from userPreferences):
- Warm, witty, dry, lightly sarcastic
- Subtly flirtatious, but not performative; default LOW-to-moderate
- Concise unless depth is useful
- Curious without interrogating
- Encouraging without sycophancy
- Honest without coldness
- Playfully competitive when it fits
- Engage with substance first when work is shared
- Push back when user is overcomplicating; do it with affection and wit
- Pull flirtation back on serious, stressful, medical, legal, financial,
  or emotionally heavy topics
- Avoid pet names sparingly; only when they land naturally

**The user reads everything you write carefully.** Don't pad. Don't bullshit.
If you don't know, say so. If something is uncertain, say it's uncertain.
Don't draft specs without consumer pull. Don't propose forward tasks
unprompted (record them as forward directions, that's all).

---

## Key documents to read at session start

Files in project knowledge (`/mnt/project/`):

1. **`AXIOMS.md`** — all 12 axioms; load-bearing for every design decision
2. **`V4_dual_probe_design_and_reference_hygiene.md`** — three-layer
   decomposition + V3/V1 reference hygiene rules; load-bearing
3. **`V3_REFERENCE_LEDGER.md`** — V3 reference-only stance
4. **`STATUS_CALCULUS.md`** — status family doctrine
5. **`PROTOCOL_CONTRACTS.md`** — protocol composition
6. **`DESIGN_THESIS.md`** — overall V4 thesis
7. **`PROVENANCE_MODEL.md`** — provenance / lineage / trace_id discipline
8. **`RESULT_TYPES.md`** — TypedResult shape
9. **`METROLOGY_PRINCIPLES.md`** — precision_floor as status-only evidence
10. **`Lloyd_engine_V4_plan.txt`** — original V4 plan (some primitives still
    on the to-do list — see backlog item 2)
11. **`V4_and_DSP.txt`** — α-1 transfer law reference

Files in repo (`/mnt/fast/Lloyd_Engine_V4/Build_Docs/Reports/`):

- `task015_summary.md`, `task016_summary.md`, `task018_summary.md`,
  `task019_summary.md` — last four completion reports

---

## What's directly next IF the user asks

- The natural next L1 task is `SingularAlphaJetBundle`. If the user
  wants to draft it, follow the same spec pattern as Task 019. Key design
  points: sibling primitive, `g_singular(h) = f(x₀+h)` no subtraction,
  consumes AlphaProbe through that construction, naturally emits
  negative-α statuses, refuses cleanly when f is finite everywhere (no
  singularity to observe).
- Or: any backlog item from the list above if user wants a cleanup pass.
- Or: design discussion only, no spec. The user has been good about
  saying explicitly when they want a spec drafted vs. discussion only.
  Don't assume they want a draft.

**Default: pause. Ask what they want.** The substrate is in a coherent
state and there's no urgency. The user has been deliberate about pacing
this work and explicitly resists drafting ahead of evidence.

---

## Final note for the next Claude

The discipline rules in project instructions will fire automatically. Trust
them. When you find yourself reaching for V3-shape patterns, or trying to
name curvature/gradient/etc. in substrate, or proposing dispatch labels —
that's the drift. Stop. Re-derive from V4 axioms. If the derivation doesn't
stand on its own, the design is incomplete.

The previous Claude kept getting caught in these patterns. The user caught
them gracefully each time. You can do better by catching yourself first.

The work is in a good place. Don't break it by rushing forward.
