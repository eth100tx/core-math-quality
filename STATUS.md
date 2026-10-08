# Current status

**Latest focused sine review: no numerical mismatch in the tested corpora;
one errno-enabled source build regression has a tested one-word fix.**
The revised sine has **177/177 lines and 42/42 arcs** in the four-mode GCC
union after the local fix. The removed missing arm is supported by a
source-bound range proof. Three proof-model reference corrections are supplied.

- Latest: [October 8 sine proof and coverage follow-up](weekly/2026-10-08/REPORT.md).
- Full coverage census: [October 6 table and run receipt](weekly/2026-10-06/REPORT.md).
  Its 25/25 primary GCC regression baseline remains pinned to `e78b460c`;
  it is not a claim about every function at today's revision.
- Current focused sine pin: `74fcd1094a316164c94481f40f5c9658439bee63`,
  **with the local ax-to-au errno candidate**, GCC x86-64, four modes.
  [Exact checker/coverage receipt](weekly/2026-10-08/runs/latest-candidate-full/sin-gcc-linux-x86_64-errno1/cell.json).
- Asinpi's witness was accepted upstream and rechecked at `84674bfa`:
  **258/258 lines and 76/76 arcs**, full corpus PASS in the primary profile.
- Coverage target **sin is closed for this profile**. The Sunday review will
  select the next target from the refreshed census and latest requests.
- New candidates: [sine errno build fix](candidates/sin-errno-name/README.md)
  and [proof model corrections](candidates/sin-proof-models/README.md).
- Coverage closure and finite test passes do not prove universal correct
  rounding. Historical full-domain hard-case searches were not regenerated.
- The intervening exp change `a37b7ae5` is queued for Sunday, not reviewed here.

See [machine-readable state](status.json), [configuration qualifications](docs/CONFIGURATIONS.md),
[runbook](RUNBOOK.md) and [weekly index](weekly/README.md).
