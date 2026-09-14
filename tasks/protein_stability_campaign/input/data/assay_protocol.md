# Assay Protocol Notes

The campaign objective is to minimize measured ddG for single mutants. Lower `measured_ddg` is better, and `measured_ddg < 0` indicates a stabilizing mutation relative to the wild type.

Round submissions are measured through the provided assay interface. Returned fields include:

- `measured_ddg`: historical mutant stability relative to the median historical wild-type value; lower is better.
- `assay_sd`: approximate standard deviation propagated from the reported 95% confidence-interval widths of the wild type and mutant. It is computed as `sqrt(wt_width^2 + mutant_width^2) / 3.92`.
- `qc_status`: assay quality flag; `pass` means normal interpretation, while `warn` means `assay_sd > 0.25` and the measurement should be treated cautiously.
- `is_stabilizing`: whether `measured_ddg < 0`.

Use `assay_sd` and `qc_status` when deciding how much to trust individual measurements. A good report distinguishes robust trends from single noisy measurements and states when a follow-up confirmation would be appropriate.
