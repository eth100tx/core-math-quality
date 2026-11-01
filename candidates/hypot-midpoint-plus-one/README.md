# Exact near-midpoint hypot regression candidates

**Eight unordered positive-normal pairs, plus swaps, are independently certified
and pass GCC/Clang four-mode checks. These are passing regression candidates,
not failure witnesses or a publication-novelty claim.**

[The 16-row `.wc` file](hypot-midpoint-plus-one.wc) is absent from the complete
`hypot.wc` at implementation `5f65574e2b3631fb31e9b88dd27782a936c68095`, including
equivalence under signs, argument swap and common power-of-two scaling.
Membership is a file comparison, not execution of that whole upstream corpus.

For `m = 2^51 - 1 - 2j`, `j=0,...,7`, set integer significands
`X=3m+2`, `Y=4m+1`, `Z=5m+2`. Then

```
X^2 + Y^2 = Z^2 + 1.
x = X * 2^-52, y = Y * 2^-52.
```

Both inputs are in `[1,2)`. The result is in `[2,sqrt(8))`, and odd `Z` makes
`Z*2^-52` a binary64 midpoint. Its distance below the exact result, in result
ulps, is `1 / (2*(sqrt(Z^2+1)+Z))`. Hence

```
1/(4Z+2) < distance_in_ulps < 1/(4Z) < 2^-55.
```

This proves the stated distance for these eight pairs. The integer residual
`+1` is the smallest positive integer in this particular scaled representation;
it is not a global worst-case claim. Midpoint proximity chiefly stresses
round-to-nearest; passing directed modes is not evidence of equally hard
directed-rounding inputs. This construction is not an exhaustive family census.

The [certificates](../../weekly/2026-11-01/hypot-certificates.json) are checked by
the existing independent integer verifier. Fresh GCC and Clang qualification,
two MPFR calculations, and deliberate value/input/mode/flag/errno/timeout failures
gate 128 observations. Values, flags and errno are separate fields in the
[execution receipt](../../weekly/2026-11-01/hypot-execution.json).
[Membership and rational bounds](../../weekly/2026-11-01/hypot-family.json) are
cross-checked with a separate exact-rational parser in
[verify_evidence.py](../../weekly/2026-11-01/verify_evidence.py).
The same verifier binds every pickup row to its certificate. These inputs were
executed through the restricted adapter, not upstream's bivariate `check_worst`.
No new stage/branch coverage or distinct-path contribution is claimed.

No upstream modification or PR was made. Optional maintainer action: pick up
the small regression file if useful. Next eligible work is a complementary
below-midpoint or near-representable family, not a larger unchanged sweep of
these eight examples. Missing historical archives remain unimported.
