# CORE-MATH quality roadmap

Each Sunday we ask which small changes would help a maintainer next week, and which longer-term gap those changes would close. The [ranked queue](config/improvements.json) owns priority and budgets. The [candidate index](candidates/README.md) links available patches and adoption evidence. This page tracks the outcomes beyond any one patch.

## Draft proposals for November 15

| Queue card | Proposed change | What would make it ready for pickup |
|---|---|---|
| P7 · hypot special tests | Supply an equal-budget replay of the old and new input generators around `2b22bd62`. Compare streams by seed and exponent gap. | If a useful case disappeared, supply the exact pair and a deterministic regression. Otherwise publish the comparison and retire the patch idea. [Generator review scope](IMPROVEMENTS.md) |
| P8 · contracted asin | Extend the strict range certificate to one compiler's x86-64-v3 evaluation of the refinement. | Link the emitted operations to replayable enclosures for both indices and the high-part exponent. If an operation cannot be bounded, identify it precisely. [Starting certificate](weekly/2026-11-09-asin/REPORT.md) |
| P3 · exact pow reference | Build a small value oracle for positive normal inputs at exponent 3/2. Compare x³ with the squares of exact dyadic rounding boundaries. | Supply exact encodings, demonstrated positive and negative controls, and a replayable sample. P3 waits for P7 to release the bivariate slot. [Queue and limits](config/improvements.json) |

The Sunday reviewer should confirm or replace these proposals after checking the full upstream delta. Each can be evaluated independently. The execution order and available time determine which can be prepared this week.

## Longer-term outcomes

| Outcome | Verified starting point | Next milestone and decision |
|---|---|---|
| Preserve valuable regressions as special tests get cheaper | Both sets of hypot midpoint inputs, 32 ordered rows in total, entered the upstream corpus. [Membership check](weekly/2026-11-09/REPORT.md) | Use P7 to determine whether any deterministic input deserves a permanent place. Consider applying the replay method to the changed tgamma test only if it answers a concrete input-selection question. |
| Know which proof assumptions hold in the shipped code | The strict asin caller bounds are closed at their pinned source. Upstream incorporated revised comments. Three near-one log evaluation graphs have scoped evidence. [Asin adoption](candidates/README.md) · [Log certificate](weekly/2026-11-08/LOG.md) | Bind one contracted asin graph under P8 before extending to another build. For cosine, distinguish adoption of the sign correction from independent reproduction of the exceptional-input census. Reopen the latter when a replayable enumeration with its input bounds and exclusions becomes available. |
| Make hard bivariate cases independently reproducible | A restricted Linux hypot adapter has passed qualification. All ten files listed in the October transfer manifest now match their original SHA-256 digests. [Qualification and controls](docs/HYPOT-QUALIFICATION.md) · [Archive replay milestones](IMPROVEMENTS.md#bivariate-expansion-and-team-use) | Review the compact hypot bundle's dependencies and replay its supplied table from a clean workspace. Regenerating the completeness census is a separate milestone. Then refresh angular and pow corpus membership at a selected pin. Compare angular stage hits with the full same-build corpus before claiming an addition. P3 explores a different hypothesis from the earlier exponent sweep. |

## Decisions feeding the next review

**November 14 planning checkpoint.** Upstream implementation [018fa97c](https://gitlab.inria.fr/core-math/core-math/-/commit/018fa97cbdacf59924b899a9dfa422d532cb2bb7) reduces binary64 tgamma special checks. This adds a possible follow-up to P7. The cosine [TeX change](https://gitlab.inria.fr/zimmerma/core-math-proofs/-/blob/43c9a83bc6d15f96d2886dee543b5523ebf30394/cos/cos.tex#L744-756) now gives both the corrected swap condition and the total-sign identity. Retire the sign-bookkeeping proposal. The proof branch has also advanced [its tan divdd analysis](https://gitlab.inria.fr/zimmerma/core-math-proofs/-/commit/08b804138d9e39b507522762c5b0df5e1b0b1478). Inventory it in the Sunday scan before considering overlapping proof work. This planning check leaves the full weekly scan and its review baseline intact.

The [planning evidence](weekly/2026-11-14-planning/PLANNING.md) identifies the files and revisions checked. Exp and routine coverage remain [parked](IMPROVEMENTS.md#paused-work) until the authorized scope changes. The [Sunday runbook](RUNBOOK.md#weekly-improvement-candidates) defines how to update this roadmap and publish its dated decisions.
