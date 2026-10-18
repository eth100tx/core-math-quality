# sinh: retain the full mask width

**October 18 status:** The int64_t restoration is upstream in implementation commit 6a4458059c4f552ff2cf219cf4e91d778db325ab.


Proposed, tested and independently reviewed; not merged at the reviewed pin.

Base implementation: `81a899d67953a619d703660fd9630f0554673524`.

The first accurate-path mask was narrowed to 32-bit int. Restore int64_t, as already used at the second site. This avoids extra database routing; no public wrong-value failure is claimed.

Both baseline and candidate pass the full pinned `.wc` in all four modes on the listed GCC/Clang configurations. Exact receipts and instrumentation observations: [weekly report](../../weekly/2026-10-11/REPORT.md), [supplement](../../weekly/2026-10-11/SUPPLEMENT.json).

Apply `git apply fix.patch` to a disposable checkout at the base. These are source-equivalence/width corrections, not claims of newly discovered numerical failures.
