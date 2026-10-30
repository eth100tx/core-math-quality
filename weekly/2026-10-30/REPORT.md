# Cosine proof adoption follow-through - October 30

**Most October 29 proof corrections now appear upstream. One new sign-definition typo remains; no new numerical failure is claimed.** The code and tested corpus are unchanged, so the dated October 29 regressions were retained rather than repeated.

Proof pin: `d5fab2e483d00b7a21c5b50b1abb877cadeb5c5b`.
Implementation pin: `b5a3f7ffb9315afae57a309623c3c5c226ec8bec`.
This is focused follow-through, not the Sunday scan. [Source binding](BINDING.json), [changed-path scope](SCOPE.json).

| October 29 item | Current disposition |
|---|---|
| Moderate-path signed reduction; LargePath leading term and half-turn relation | Adopted, equivalent or verbatim statements |
| Accurate reducer domain and exponent-variable correction | Adopted; the proposed supporting extension argument is present only as comments, not an active proof paragraph |
| Exception guard matching C | Adopted; the proposed completeness/fallback explanation is present only as comments |
| Accurate-path subtraction, C sign conversion, four-case decomposition and signed reduction error | Adopted with a remaining swap-bit typo described below |
| Quarter-turn distance and its reduction-error allowance | Adopted |
| Small-cosine population 16,778 and minimum `0x1.6477e472c5074p+715` | Adopted; source now includes a commented Sage check of the supplied corpus, not a regenerated exhaustive census |

In the new sign paragraph, `d=1 if q+sigma_r=0 and w1<=w2` omits the subtraction case `q=sigma_r=1`. Replace the sum condition with `q=sigma_r`. The complete sign is `sigma=(b+q+d) mod 2`; the half-turn factor alone is `(-1)^b`. C already implements the quadrant and comparison flips. The [small follow-up patch](../../candidates/cos-sign-bookkeeping/README.md) corrects the prose without changing code. [24-case exact check](SIGN-CHECK.json), [reproducer](check_sign.py). Its abstract magnitude examples are not binary64 failing inputs.

All 13 input blobs in the earlier source/build/harness/corpus manifest match at the new implementation pin; the new proof's named implementation also has the same `cos.c` blob. The previous GCC/Clang, four-mode, normal/forced-accurate results remain **October 29 measurements at their original pin**. No new execution or coverage is claimed. The old broad proof patch is partly adopted and must not be blindly reapplied.

No complete hardness-generation census or exception-fallback unreachability proof was obtained. The commented reducer/completeness paragraphs are not treated as adopted proof obligations. No new search, full proof, performance or platform qualification was performed. Tangent proof changes are inventoried and deferred, with no readiness or validation claim. The earlier hypot and asin checkpoints and exp/routine-coverage pauses remain.

Next: reconcile the small sign correction and any new completeness evidence; reuse unchanged checks. [Review](REVIEW.md), [hashes](SHA256SUMS.json).
