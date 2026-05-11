# Task 008 Design Decisions

## Caller-Supplied Sequence Indices

History order is supplied by integer `step_index`. The layer does not use wall-clock time, system clocks, background jobs, or scheduling because those would add runtime state outside the typed evidence contract.

## No Silent Sorting

`build_status_trace` preserves caller order. Non-increasing indices emit `history_trace_unordered` because sorting would hide evidence about the supplied observation stream.

## Status Changes Are Evidence

A status change is recorded as transition evidence. The history layer does not decide that a transition is better, worse, safe, unsafe, or domain-relevant.

## Caller-Supplied Geometry Signatures

Geometry signatures are optional caller evidence. Task 008 does not introspect arbitrary value objects to create universal geometry claims.

## Singleton Traces Are Not Stable

A singleton trace is valid history evidence but has no adjacent transition. The stable-trace requirement accepts only `history_trace_stable`, so singleton traces are refused explicitly.

## No Smoothing Or Forecasting

The layer records observed status evolution only. It does not add smoothing windows, hysteresis bands, trend forecasting, confidence scores, weighted scores, or automatic stability constants.

## No Persistent Store

History values carry compact trace IDs and snapshots. There is no database, file-backed history store, telemetry service, logger, or background worker.

## Prior Semantics Remain Unchanged

Tasks 001 through 007 keep their behavior and serialization. Task 008 adds a downstream observer package and one new status enum family in `core/status.py`.
