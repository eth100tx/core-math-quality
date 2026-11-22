# CORE-MATH quality roadmap

Each Sunday we ask which small changes would help a maintainer next week, and which longer-term gap those changes would close. The [ranked queue](config/improvements.json) owns priority and budgets. The [candidate index](candidates/README.md) links available patches and adoption evidence. This page tracks the outcomes beyond any one patch.

## Proposals for November 29

| Next pickup | Deliverable and decision |
|---|---|
| 1 · Tangent conversion regression (P11) | Isolate the just-fixed `set_dd` shift/exponent boundaries. Deliver exact helper-level boundary cases, or state why they are not reachable through the public function. This is scoped regression work, not a duplicate of the maintainer's tangent proof. |
| 2 · Exact pow(x, 3/2) reference (P3) | Compare exact x³ with squared dyadic rounding boundaries on a bounded positive-normal sample, including a wrong-neighbor control. This has the next bivariate slot. |
| 3 · Hypot completeness dependencies (P12, blocked) | Recover the missing adjacent-family generator and raw census/native receipts; identify exact bounds and exclusions before proposing a bounded regeneration. Table replay alone cannot close this. No search is dispatched while dependencies are missing. |

P11 is the primary unary task; P3 has the next bivariate slot. P12 remains dependency-blocked. [November 22 results and limits](weekly/2026-11-22/REPORT.md)

## Longer-term outcomes

| Outcome | Verified starting point | Next milestone and decision |
|---|---|---|
| Preserve valuable regressions as special tests get cheaper | Both sets of hypot midpoint inputs, 32 ordered rows in total, entered the upstream corpus. [Membership check](weekly/2026-11-09/REPORT.md) | P7 found identical sampled serial streams at equal budgets. The tgamma tiny-branch input and its two neighbors already occur in the corpus. Retire both proposed additions. |
| Know which proof assumptions hold in the shipped code | The strict asin caller bounds are closed at their pinned source. Upstream incorporated revised comments. Three near-one log evaluation graphs have scoped evidence. [Asin adoption](candidates/README.md) · [Log certificate](weekly/2026-11-08/LOG.md) | P8 binds the contracted GCC 13.3 v3 graph. P9 found identical Clang fast/off objects; no further range-transfer claim. P11 now targets regression fixtures around the newly corrected tangent conversion helper. For cosine, distinguish adoption of the sign correction from independent reproduction of the exceptional-input census. Reopen the latter when a replayable enumeration with its input bounds and exclusions becomes available. |
| Make hard bivariate cases independently reproducible | A restricted Linux hypot adapter has passed qualification. All ten files listed in the October transfer manifest now match their original SHA-256 digests. [Qualification and controls](docs/HYPOT-QUALIFICATION.md) · [Archive replay milestones](IMPROVEMENTS.md#bivariate-expansion-and-team-use) | P10 independently checked all 160 supplied rows and published a self-contained reference replay. P12 records the missing original census/native dependencies. Regenerating the completeness census is a separate milestone. Then refresh angular and pow corpus membership at a selected pin. Compare angular stage hits with the full same-build corpus before claiming an addition. P3 explores a different hypothesis from the earlier exponent sweep. |

## Decisions feeding the next review

**November 22.** P10 closed for supplied-table soundness and finite reference cross-checks. P9 stopped at identical Clang objects. The new upstream tangent fix passed the full pinned Clang corpus; helper-branch reachability remains a useful bounded regression question. Prior hypot rows and cosine/asin adoption are retained. [Dated review](weekly/2026-11-22/REPORT.md)

**November 15.** Closed P7 for the sampled generators and P8 for the recorded GCC graph. Selected P10 for independent table replay. [Dated review](weekly/2026-11-15/REPORT.md)

**November 14 planning checkpoint.** Upstream implementation [018fa97c](https://gitlab.inria.fr/core-math/core-math/-/commit/018fa97cbdacf59924b899a9dfa422d532cb2bb7) reduces binary64 tgamma special checks. This adds a possible follow-up to P7. The cosine [TeX change](https://gitlab.inria.fr/zimmerma/core-math-proofs/-/blob/43c9a83bc6d15f96d2886dee543b5523ebf30394/cos/cos.tex#L744-756) now gives both the corrected swap condition and the total-sign identity. Retire the sign-bookkeeping proposal. The proof branch has also advanced [its tan divdd analysis](https://gitlab.inria.fr/zimmerma/core-math-proofs/-/commit/08b804138d9e39b507522762c5b0df5e1b0b1478). Inventory it in the Sunday scan before considering overlapping proof work. This planning check leaves the full weekly scan and its review baseline intact.

The [planning evidence](weekly/2026-11-14-planning/PLANNING.md) identifies the files and revisions checked. Exp and routine coverage remain [parked](IMPROVEMENTS.md#paused-work) until the authorized scope changes. The [Sunday runbook](RUNBOOK.md#weekly-improvement-candidates) defines how to update this roadmap and publish its dated decisions.
