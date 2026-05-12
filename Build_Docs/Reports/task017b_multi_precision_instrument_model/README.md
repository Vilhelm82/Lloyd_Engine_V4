# Task 017b Multi-Precision Instrument Model Artifacts

This directory contains the deterministic campaign output for Task 017b.
The campaign compares the Task 024b Schwarzschild four-form battery across
float32, float64, and decimal-50 oracle arithmetic without adding V4
primitives or manifest entries.

- `campaign_output.json`: deterministic output for Phases A, B, and C.

Reproduce from the repository root:

```bash
PYTHONPATH=src python -m lloyd_v4.evals.multi_precision_campaign
```

Write a repeat output for byte comparison:

```bash
PYTHONPATH=src python -m lloyd_v4.evals.multi_precision_campaign --output /tmp/multi_precision_repeat.json
diff Build_Docs/Reports/task017b_multi_precision_instrument_model/campaign_output.json /tmp/multi_precision_repeat.json
```
