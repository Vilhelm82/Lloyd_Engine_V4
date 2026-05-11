# Task 024b Schwarzschild Four-Form Report Artifacts

This directory contains the static V3 reference overlay and the V4
campaign output for the Schwarzschild four-form battery.

- `v3_reference_overlay.json`: supplied V3 reference table with metadata
  and full-precision row values.
- `v3_reference_overlay.csv`: CSV rendering of the same row data used by
  the V4 fixture-validation test.
- `campaign_output.json`: deterministic V4 campaign output generated from
  existing V4 primitives.

Reproduce the campaign output from the repository root:

```bash
PYTHONPATH=src python -m lloyd_v4.evals.schwarzschild_four_form_campaign
```

To write a second copy for byte comparison:

```bash
PYTHONPATH=src python -m lloyd_v4.evals.schwarzschild_four_form_campaign --output /tmp/campaign_output_repeat.json
diff Build_Docs/Reports/task024b_schwarzschild_four_form/campaign_output.json /tmp/campaign_output_repeat.json
```
