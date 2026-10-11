# log2: preserve the two sign cases

Proposed, tested and independently reviewed; not merged at the reviewed pin.

Base implementation: `81a899d67953a619d703660fd9630f0554673524`.

Unsigned sign-bit arithmetic yields +1/+3. The candidate yields +1/−1, matching the earlier branch for both bit values. Opposite-sign public reachability is not established; no wrong-value witness is claimed.

Both baseline and candidate pass the full pinned `.wc` in all four modes on the listed GCC/Clang configurations. Exact receipts and instrumentation observations: [weekly report](../../weekly/2026-10-11/REPORT.md), [supplement](../../weekly/2026-10-11/SUPPLEMENT.json).

Apply `git apply fix.patch` to a disposable checkout at the base. These are source-equivalence/width corrections, not claims of newly discovered numerical failures.
