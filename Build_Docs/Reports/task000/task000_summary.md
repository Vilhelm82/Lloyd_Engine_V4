# Task 000 Summary

## Created

Task 000 created the Lloyd V4 bootstrap substrate:

- minimal Python package under `src/lloyd_v4`
- core status, validity, conditioning, provenance, result, protocol, calculus, serialization, and error modules
- architecture documents for axioms, design thesis, status calculus, protocol contracts, provenance, result types, metrology principles, V3 reference stance, and roadmap
- guardrail tests for documentation presence, no V3 runtime dependency, typed refusal, provenance serialization, protocol rejection, strict non-finite serialization, and primitive status visibility

## Tests Run

Initial red run:

```text
python -m pytest tests -q
```

Result: failed during collection because `lloyd_v4` did not exist yet. This was the expected pre-implementation failure.

Final run:

```text
python -m pytest tests -q
```

Result:

```text
.........                                                                [100%]
```

Source audit:

```text
rg "lloyd_v3|safe_mask|projection_mode=\"legacy\"|legacy_compat|clamp_min|epsilon|eps" src tests Build_Docs -n
```

Result: matches were documentation-only references to forbidden concepts in task/planning/report files. A source-only audit over `src/` returned no matches.

## Deviations

The repository was not a git repository, so changes were made directly in the workspace.

The available interpreter was Python 3.14.4 rather than Python 3.11. `pytest` was not installed, so only `pytest` and its small direct support packages were installed into the user site to run the requested command.

## Unresolved Design Questions

- Exact static protocol-checking strategy remains future work. M0 uses strict runtime validation with structures intended to support static checking later.
- StatusTensor shape semantics are not implemented in M0.
- Provenance equivalence-class criteria are documented but not yet formalized.
- ScalarizationResult is documented as an intended object but not implemented until a scalarization operation exists.

## Task 001 Readiness

Task 001 is ready to start once final Task 000 verification passes. The next scope is ProjectiveRatio as a typed projective state with explicit scalarization refusal.
