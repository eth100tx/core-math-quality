# Current status

**25/25 priority functions pass the initial GCC regression baseline.**
Coverage and correctness are separate; no complete proof is claimed.

- Latest: [October 6 qualification and census](weekly/2026-10-06/REPORT.md).
- Active coverage target: **asinpi**, 0 missing lines,
  1 missing arcs in the primary profile. A tested one-row corpus candidate closes this gap locally.
- New sine coverage: **175/175 lines;
  43/44 arcs** in the four-mode union.
- New confirmed rounding/compiler defects from this baseline: **none**.
- Candidate: [asinpi domain witness](candidates/asinpi-domain-witness/README.md),
  tested locally; independent review pending, not applied upstream.
- Proof review and untested platforms remain explicit separate work.

See [machine-readable state](status.json), [configuration qualifications](docs/CONFIGURATIONS.md),
[runbook](RUNBOOK.md) and [weekly index](weekly/README.md).
The next weekly run must inspect changes after the pinned revision; it must not
repeat these results as new or silently advance unreviewed proof scope.
