# CORE-MATH quality roadmap

Each Sunday we ask which small changes would help a maintainer next week, and which longer-term gap those changes would close. The [ranked queue](config/improvements.json) owns priority and budgets. The [candidate index](candidates/README.md) links available patches and adoption evidence. This page tracks the outcomes beyond any one patch.

## Proposals for November 22

| Next pickup | Deliverable and decision |
|---|---|
| 1 · Compact hypot verifier | Replay the supplied table from a clean Linux directory, include its dependencies and one deliberately invalid row. Publish the missing dependency if it blocks reproduction. Regenerating the family census is a separate task. |
| 2 · Clang asin range binding | Compare the Clang v3 fast-contraction listing with the two established models. Map any different high/residual pair, then replay the bounds or identify the first unbound operation. |
| 3 · Exact pow(x, 3/2) reference | Compare exact x³ with squared dyadic rounding boundaries on a bounded positive-normal sample. Include a wrong-neighbor control. It follows the compact table replay in the single bivariate slot. |

P10 and P3 share one bivariate slot and run in that order. P9 is the primary unary review. [November 15 results and limits](weekly/2026-11-15/REPORT.md)

## Longer-term outcomes

| Outcome | Verified starting point | Next milestone and decision |
|---|---|---|
| Preserve valuable regressions as special tests get cheaper | Both sets of hypot midpoint inputs, 32 ordered rows in total, entered the upstream corpus. [Membership check](weekly/2026-11-09/REPORT.md) | P7 found identical sampled serial streams at equal budgets. The tgamma tiny-branch input and its two neighbors already occur in the corpus. Retire both proposed additions. |
| Know which proof assumptions hold in the shipped code | The strict asin caller bounds are closed at their pinned source. Upstream incorporated revised comments. Three near-one log evaluation graphs have scoped evidence. [Asin adoption](candidates/README.md) · [Log certificate](weekly/2026-11-08/LOG.md) | P8 binds the contracted GCC 13.3 v3 graph. Compare a Clang graph under P9. For cosine, distinguish adoption of the sign correction from independent reproduction of the exceptional-input census. Reopen the latter when a replayable enumeration with its input bounds and exclusions becomes available. |
| Make hard bivariate cases independently reproducible | A restricted Linux hypot adapter has passed qualification. All ten files listed in the October transfer manifest now match their original SHA-256 digests. [Qualification and controls](docs/HYPOT-QUALIFICATION.md) · [Archive replay milestones](IMPROVEMENTS.md#bivariate-expansion-and-team-use) | Review the compact hypot bundle's dependencies and replay its supplied table from a clean workspace. Regenerating the completeness census is a separate milestone. Then refresh angular and pow corpus membership at a selected pin. Compare angular stage hits with the full same-build corpus before claiming an addition. P3 explores a different hypothesis from the earlier exponent sweep. |

## Decisions feeding the next review

**November 15.** Closed P7 for the sampled generators and P8 for the recorded GCC graph. Selected P10 for independent table replay. [Dated review](weekly/2026-11-15/REPORT.md)

**November 14 planning checkpoint.** Upstream implementation [018fa97c](https://gitlab.inria.fr/core-math/core-math/-/commit/018fa97cbdacf59924b899a9dfa422d532cb2bb7) reduces binary64 tgamma special checks. This adds a possible follow-up to P7. The cosine [TeX change](https://gitlab.inria.fr/zimmerma/core-math-proofs/-/blob/43c9a83bc6d15f96d2886dee543b5523ebf30394/cos/cos.tex#L744-756) now gives both the corrected swap condition and the total-sign identity. Retire the sign-bookkeeping proposal. The proof branch has also advanced [its tan divdd analysis](https://gitlab.inria.fr/zimmerma/core-math-proofs/-/commit/08b804138d9e39b507522762c5b0df5e1b0b1478). Inventory it in the Sunday scan before considering overlapping proof work. This planning check leaves the full weekly scan and its review baseline intact.

The [planning evidence](weekly/2026-11-14-planning/PLANNING.md) identifies the files and revisions checked. Exp and routine coverage remain [parked](IMPROVEMENTS.md#paused-work) until the authorized scope changes. The [Sunday runbook](RUNBOOK.md#weekly-improvement-candidates) defines how to update this roadmap and publish its dated decisions.
