# Data

This is a low-resource protein stability screening task. Every "assay result" was generated from historical experimental values by a fixed formula and frozen before the task started. The interface only replays the stored result for the candidates you submit; it never starts a new experiment.

Visible files:

- `protein_context.json`: WT sequences, objective, and campaign sizes for each episode.
- `design_space.csv`: queryable single-mutant candidates. It contains no wet-lab measurements for candidate variants.
- `pilot_assays.csv`: 399 historical measurements from separate, non-queryable positions; each episode has 39–40 rows.
- `pilot_qc_summary.csv`: public episode-level summary derived from `pilot_assays.csv`, including inferred pilot region coverage.
- `campaign_brief.md`: scientist-facing campaign objective and final handoff expectations.
- `assay_protocol.md`: interpretation of `measured_ddg`, `assay_sd`, and `qc_status`.
- `plate_constraints.json`: exact 96-well plate-map constraints.
- `campaign_constraints.json`: batch sizes, round count, output schemas, and budget rules.

Scoring data and the scoring program are never copied into the Agent workspace. At run time the only way to obtain measurements is the framework `validation` action, and only for candidates you have submitted. The returned results and the call history are kept by the framework in a private `VerifyContext`; they are not part of your final submission files.
