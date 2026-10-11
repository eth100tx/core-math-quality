# exp proof: correct the derivative term

Proposed; not merged at proof pin `58df57e5a46310d0e47d140ad23f146461788e0e`.

Q'(0)=1 refutes the displayed 2^-0.99 derivative bound. Exact dyadic coefficient arithmetic proves |Q'|<1.0001 on a rational interval containing the cited reduction interval. The corrected contribution is <2^-116.47; the final sum remains below 2^-100.29. This patch repairs that calculation, not the entire accurate-path proof or its other open obligations.

Apply `git apply fix.patch` at the proof repository root. [Review](../../weekly/2026-10-11/SOURCE-REVIEW.md), [certificate](../../weekly/2026-10-11/exp-proof/receipt.json), [replay](../../weekly/2026-10-11/verify_exp_arithmetic.py).

The patch applies to the pinned proof source and its arithmetic is checked.
The complete multi-file PDF was not rebuilt.
