# November 15 · binary64 asin and hypot

On one GCC 13.3 x86-64-v3 build, both asin refinement table accesses stay in bounds and the high part has ample exponent headroom. At equal serial budgets, the two hypot generators produced identical traces from 256 raw draw pairs, each used at 27 exponent gaps. Neither check produced a library fix.

### What the asin certificate establishes

For every binary64 argument that can reach the refinement, the rounded index `j` and its complement `32−j` are in 0–32. The high part `ph` has biased exponent at least **997**. The exponent-field subtraction needs only 53. The checker covers both signs and all four rounding modes with outward rational intervals over 256 magnitude slabs and 712 branch boxes. It overapproximates the branch into refinement. [Bounds, compiler identity and controls](binding.json)

The certificate is for the recorded GCC 13.3 v3 assembly with fast contraction, binary64 SSE arithmetic, gradual underflow, masked traps, and faithfully rounded square root, including the linked libm call. The hand-checked operation mapping is described in [the replay instructions](REPRODUCE.md). Separate MPFR comparisons matched all **542 calls per mode** (2,168 total). Those comparisons measured values only. Correct rounding of the complete function, flags, errno, other compiler graphs and the database decision remain outside this result. [Interval checker](contracted_asin.py) · [MPFR probe](probe_asin.c)

### Did the shorter hypot test change its inputs?

At the same seed and budget, the serial generator before and after `2b22bd62` produced byte-identical traces. We compared 128 raw pairs per seed, for two seeds, rescaled across 27 exponent gaps. The actual MPFR candidate construction ran. Resetting the seed repeated each raw stream across gaps in both versions. The emitted input pairs changed with gap and seed. The default count fell from 100,000,000 to 100,000. This finite comparison leaves the removed tail and historical OpenMP sampling unmeasured. It ran the input generator only. The matched streams give us no specific missing input to propose as a regression. We retired the patch idea for this comparison. [Replay and stream digests](replay.json)

### Adoption, scope and next work

All 32 previously proposed ordered hypot rows still occur once each in the pinned corpus. The signed asin index comment and corrected cosine sign identity are present. Sine implementation and proof had no new change in the comparison from November 8. The positive tgamma input `2^-1024` and both immediate neighbors already appear at corpus lines 545548, 545550 and 545552. We dropped that proposed addition. The shared unary checker's recent diff changes a diagnostic format string. The previous sine test result stands at its original date. The tan proof is changing upstream. We inventoried every changed blob from the last complete review (88 implementation paths and 28 proof paths). Detailed review of the remaining changes stays open, including the rewritten sincos source, platform-specific changes, and the exceptional-input census. No full regression or coverage campaign ran. [Pinned inventory and adoption receipt](SOURCE-REVIEW.json)

| Next pickup | Deliverable and decision |
|---|---|
| 1 · Compact hypot verifier | Replay the supplied table from a clean Linux directory, include its dependencies and one deliberately invalid row. Publish the missing dependency if it blocks reproduction. Regenerating the family census is a separate task. |
| 2 · Clang asin range binding | Compare the Clang v3 fast-contraction listing with the two established models. Map any different high/residual pair, then replay the bounds or identify the first unbound operation. |
| 3 · Exact pow(x, 3/2) reference | Compare exact x³ with squared dyadic rounding boundaries on a bounded positive-normal sample. Include a wrong-neighbor control. It follows the compact table replay in the single bivariate slot. |

The [roadmap](../../ROADMAP.md) tracks when these proposals can close and which earlier items were adopted. No upstream PR was opened.
