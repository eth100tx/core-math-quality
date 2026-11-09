# Binary64 asin refinement ranges

**For the pinned source evaluated in binary64 with contraction disabled, the refinement table index stays in 0–32 and the biased exponent of `ph` is at least 997.** The exponent subtraction needs only 53. This closes the two range premises for the adopted hard-case predicate in all four rounding modes under this evaluation model. The proposed patch corrects two comments. [Pinned implementation](https://gitlab.inria.fr/core-math/core-math/-/blob/d5d309237132fec40a98cb866dbce43c04b98010/src/binary64/asin/asin.c#L268) · [Patch](asin-signed-index.patch)

| Quantity | Certified enclosure or implication |
|---|---|
| Rounded product before nearest-even integer rounding | Nonnegative and at most `0x1.00145f07af691p+5`, about 32.009947. The boundary for rounding to 33 is 32.5. |
| Indices | Both `j` and `32-j` are in 0–32. The signed multiplier `jt` is in −32–32. |
| Final `abs(ph)` | At least `0x1.71374489ffffap-26` and at most `0x1.921fb504dd3d9p+0`. |
| Encoded threshold | With biased exponent E ≥ 997, `T=(E−53)·2^52` stays in [0,2^63). Clearing the sign bit gives the same range for L. The historical signed difference L−T is therefore representable on LP64. The subsequent unsigned T−L can wrap when T < L. |

The calculation bounds the only caller's actual argument `lb`, including its error allowance. It covers a superset of calls by allowing refinement whether or not the fast-path endpoints agree. The special cases exclude nonfinite inputs, |x| ≥ 1 and inputs below the tiny cutoff. The checker decodes the cutoff, splits the remaining magnitudes into 256 closed intervals meeting at 0.5 and other grid points, checks both signs, and takes every table index allowed by each enclosure. Shared endpoints may be checked twice.

**Checking the bounds.** The verifier forms exact rational endpoint expressions and rounds the hull outward to binary64 at each ordinary operation. It checks that each endpoint lies on its required side. Explicit FMA expressions have one rounding. It verifies square-root bounds by squaring and implements nearest-even integer rounding at the two index conversions. Assumptions are IEEE binary64 intermediates, gradual underflow, correctly rounded operations and square root, the stated round-to-even behavior, and the uncontracted source evaluation order. The C table values come from the hash-checked source.

Two dependencies matter. In `fasttwosum`, write `s=round(x+y)` and `z=round(s−x)`. The unrounded `y−z` is the negative sum of those two rounding errors. Bounding them by the spacing of the enclosing results also works in directed modes. Near |x|=1, when the rounded square lies in [1/2,1], Sterbenz makes its subtraction from 1 exact and the first low part is zero. The real input to the second high rounding is then `1−x²` minus the FMA residual's rounding error. This keeps the square-root argument positive. The checker propagates the polynomial and both final renormalizations to the `ph` actually read by the predicate. [Verifier](verify_asin.py) · [Hexadecimal bounds](range.json)

**One source correction.** The comment `0 <= jt <= 64` misses reachable negative indices. Both strict Linux builds reached `j=24, jt=−24` for `x=−0x1.d46p−1` in upward rounding. The two initial angle products are exactly representable for all 65 signed multipliers, verified with rational arithmetic. The comment patch produced byte-identical uninstrumented object files before and after in each of four builds. [Patch](asin-signed-index.patch) · [Compiler observations](probes.json)

The probes used 8,356 signed inputs per build in four rounding modes. The receipt counts actual refinement calls separately from early returns. GCC 13.3 and Clang 18.1.3 were each checked at baseline x86-64 with contraction off and at x86-64-v3 with fast contraction enabled. For v3 fast contraction the evidence is finite testing. Native Windows execution and whole-function correct rounding are outside this certificate. The earlier ABI analysis still applies to historical 32-bit `long` conversions. [Predicate analysis](../../candidates/asin-unsigned-gap/README.md)

To reproduce with the pinned `asin.c`, run from this directory. The first two commands need Python. The last also needs Git, GCC, Clang 18 and a v3-capable Linux host.

```sh
python3 -B verify_asin.py asin.c
python3 -B negative_control.py asin.c
python3 -B probe.py asin.c
```

The identity check rejects a mutated source. With that synthetic source explicitly enabled in an isolated interpreter, doubling the index scale makes the mathematical check reject index 33. [Negative control](controls.json)

The next bivariate card checks which inputs the shortened hypot special test exercises. It shares one slot with the queued pow reference design. The next asin proof card addresses emitted v3 operations. [Upstream test change](https://gitlab.inria.fr/core-math/core-math/-/commit/2b22bd62) · [Ranked queue](../../IMPROVEMENTS.md)

Claude Opus 5.5 independently reviewed the source mapping, rounding and residual enclosures, index conversions and interpretation of the compiler probes. The range proof passed review for its stated graph. The checker, negative controls and builds were executed separately.
