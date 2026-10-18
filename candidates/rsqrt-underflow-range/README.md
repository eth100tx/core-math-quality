# rsqrt: avoid an intermediate subnormal reciprocal

**Confirmed new flag regression; tested source patch.** For the input row
`0x1.0000000000001p+1022`, the current implementation raises spurious underflow
in all four rounding modes. The value is correct and normal: RN/RZ/RD return
`0x1.fffffffffffffp-512`, RU returns `0x1p-511`; inexact is appropriate, errno=0.
The witness is absent from the pinned corpus numerically. The previous revision
passes the same boundary controls.

`e<0x7fe` admits the binade [2^1022,2^1023), where 1/x can be subnormal.
The one-line change to `e<0x7fd` uses `(4/x)*(0.25*sqrt(x))` in that binade;
both factors are normal over the whole high-input branch. This range argument
explains the flag repair, but does not prove the entire refinement algorithm.

The candidate passes the full pinned corpus and 206,169 generated positive rows
(the checker also checks their negatives), all four modes, GCC 13.3 and Clang 18,
x86-64-v3 with contraction off and enabled. Actual assembly changes confirm
the enabled configurations performed additional contractions. A separate
eight-input boundary probe compares previous/current/candidate sources.
The new refinement predicate still has an open source-proof obligation;
the instrumented candidate observed a correction exponent gap of 51 in the
three directed modes (minimum 52 in RN), so no universal gap ≥52 can be assumed.

[Patch](fix.patch) · [Witness row](witness.wc) ·
[Focused receipts](../../weekly/2026-10-18/SUPPLEMENT.json) ·
[Unchanged-binary replay](../../weekly/2026-10-18/witness-replay/receipt.json).

Base implementation: `dae5dd8c0d5bd2691b45de28c9edbe12f067c3d3`.
Apply `fix.patch` only to a disposable checkout at that revision. The patch has
not been submitted or merged by this workbench. Reproduce with the baseline and
`python3 weekly/2026-10-18/reproduce_focus.py` as described in the
[weekly report](../../weekly/2026-10-18/REPORT.md). Exact source/patch hashes are
in [PATCH-BINDINGS.json](../../weekly/2026-10-18/PATCH-BINDINGS.json).
Tests are finite evidence, not a full-domain correctness proof.
