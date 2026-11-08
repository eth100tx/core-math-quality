# Eight exact hypot inputs below rounding midpoints

For k = 73,000,000 + 5j, j=0,…,7, put U=2k², V=2k, X=(3U−4V)/5, Y=(4U+3V)/5 and Z=U+1. The rotation preserves squared length: X²+Y²=U²+V²=Z²−1. Divisibility holds for these multiples of 5. Scaled inputs are X/2^52 and Y/2^52, both positive binary64 normals in [1,2). Z is odd in (2^53,2^54), so Z/2^52 is a midpoint within the result binade [2,4). The positive distance from the midpoint in result ulps is

`(Z−sqrt(Z²−1))/2 = 1/[2(Z+sqrt(Z²−1))] < 1/(4Z−2) < 2^-55.`

Thus nearest, downward and toward-zero choose the lower neighbor, and upward chooses the upper. Last week's residual was +1 and nearest chose the upper neighbor. This is a deliberately small complementary test, not a claim that all hard cases have either form.

[Pickup file](hypot-below.wc) · [certificates](hypot-certificates.json) · [full-corpus membership](hypot-family.json) · [Linux execution](hypot-execution.json). All 16 ordered rows including swaps were checked once per mode per compiler. The existing exact-input adapter and independent MPFR calculations agreed on values; with initially clear flags, only inexact was set and errno was zero. Each compiler passed the six negative controls for value, mode, input, flags, errno and timeout. The corpus comparison is about numeric membership, not execution of all its rows. No branch/stage gain, completeness or publication novelty is claimed.

Replay this workbench revision on qualified Linux x86-64 with GCC 13.3 and Clang 18.1.3, MPFR and GMP: `timeout 10m python3 -B weekly/2026-11-08/run_hypot_family.py` in a fresh checkout. It refuses to overwrite an existing execution directory. `python3 -B weekly/2026-11-08/verify_hypot.py` checks the committed receipts, including every output, the exact pickup bytes as decoded pairs, and membership using a second rational parser. It does not repeat the numerical execution. No historical research archive was used.
