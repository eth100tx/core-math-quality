# Source and proof review — October 18

Implementation: `dae5dd8c0d5bd2691b45de28c9edbe12f067c3d3`.
Proof: `5a42d3fb72533077c8b745b9fcd39b84ad3ee92a`.
The [inventory](REVIEW-INVENTORY.json) assigns a disposition to every changed
path. A review watermark does not certify the explicitly deferred paths.

## Confirmed source issues

**rsqrt: new spurious-underflow regression.** The biased-exponent condition
`e < 0x7fe` includes the binade [2^1022,2^1023). Its `1/x` intermediate is
subnormal for x>2^1022 and can raise underflow even though rsqrt(x) is normal.
For `0x1.0000000000001p+1022`, all four modes raise that erroneous flag.
The returned value agrees with MPFR. The previous revision does not raise the
flag on the same focused cases. This is a source range error, not evidence of
a compiler miscompilation. The old revision also has a misleading hexadecimal
threshold/comment; its measured behavior, rather than that comment, is the
regression control.

Changing the condition to `e < 0x7fd` routes [2^1022,DBL_MAX] through
`(4/x)*(0.25*sqrt(x))`. Both factors are normal throughout that interval.
Below 2^1022, the retained `1/x` is normal for the ordinary positive-input
branch. This explains removal of the intermediate underflow; it is not a
universal proof of the subsequent Newton/refinement algorithm.
[Patch and reproduction](../../candidates/rsqrt-underflow-range/README.md).

**exp: historical returned-value failure persists.** The already reported input
`0x1.5a3a157335f3bp+9` still returns one ulp too large under round-toward-zero in the primary build
(RN/RU/RD pass):
actual `0x1.ffdebdc4e28acp+998`, correct `0x1.ffdebdc4e28abp+998`.
It is identified in the upstream manuscript and was previously delivered in
the audit; this is a recheck after the table rewrite, not a new discovery.
The code retains `eps=1.64e-19`, whereas the manuscript analyzes
`0x1.27p-62`. The [candidate](../../candidates/exp-fast-allowance/README.md)
adopts that documented allowance. Both representative witness rows are absent
from the pinned corpora by numeric comparison
([presence evidence](WITNESS-PRESENCE.json)). The original upstream checker
reproduces both findings using the unchanged baseline binaries
([receipt](witness-replay/receipt.json)).

The rsqrt refinement predicate changed too. Its relation to the size of the
Newton correction remains a source-proof obligation. The supplementary
instrumentation records observed exponent gaps; finite passes do not establish
a universal bound or justify an additional speculative patch.

## Exp proof generator: a verified correction

The generator's FastTwoSum low part is `-rnd(h-(a+b))`; C computes
`rnd((a+b)-h)` once the intermediate `h-a` is exact. Negation and directed
rounding do not commute. With a=1, b=2^-154 and rounding upward, C produces
`-0x1.fffffffffffffp-53`, while the old model gives `-0x1p-52`.
With b=-2^-154 and rounding downward, C produces
`0x1.fffffffffffffp-54`, while the model gives `0x1p-53`.
These are helper/model counterexamples, not public exp wrong-value inputs.

The [generator patch](../../candidates/exp-fasttwosum-model/README.md)
corrects the rounding expression and updates the exact algebraic hint to match.
Four Gappa 1.8.2 runs prove the same stated bounds in the corrected, uncontracted
model: error <2^-101.191 and |y_l|<2^-49.883. For up/dn the corrected error bound
(approximately 2^-101.192) is larger than the old model's approximately 2^-101.414
and now matches the zr bound; it remains below the stated claim. Bounds are compared with those
decimal-power claims by exact rational exponentiation, not rounded logarithms.
See [faithful-model receipt](exp-proof/faithful-receipt.json) and the
independent C/MPFR direction counterexample there. The correction was identified
during this review; the sign-placement issue predates this week's changes.

## Bounds and endpoint checks

- All 64×64 table pairs in four modes satisfy the stated table-error and low-part
  bounds. The largest enclosed error is approximately 1.4027985582e-31 at
  (46,58), downward, below 2^-102.491. This uses the actual pinned C table
  calculation and outward MPFR 256 enclosures.
- The new reduction bounds for D_h and D_l pass four Gappa runs. The earlier
  reduction-error certificate is unchanged; it was not relabelled as a new proof.
- Sollya at 300-bit precision on the outward dyadic interval
  [-90901·2^-30,90901·2^-30] encloses the approximation error below 2^-129.
- Exact rational coefficient arithmetic gives |Q'|<1.0001 on
  J=[-9/100000,9/100000], containing both r and D. The displayed error sum is
  approximately 2^-100.699, below 2^-100.69; that sum comparison is a
  90-digit arithmetic check, separately labelled from the exact derivative bound.

[Receipts and arithmetic](exp-proof/receipt.json), [table/endpoint output](exp-proof/tables.log).
These are conditional model bounds and finite table checks. A successful tool
run does not itself prove all source-level exactness hypotheses or all compiler
contraction trees.

Let x0=-0x1.6232bdd7abcd2p+9 and x-=-0x1.74910d52d3052p+9.
Outward MPFR 256 evaluation gives:

| Endpoint expression | Enclosed value, approximately |
|---|---:|
| x0 + 1022·log(2) | +2.7475416721e-14 |
| nextdown(x0) + 1022·log(2) | −8.6211421000e-14 |
| nextup(x-) + 1075·log(2) | +9.9203673596e-14 |

This repairs the endpoint choice in the new subnormal argument: its two
`nextdown(x-)` references must use `nextdown(x0)`. It also supplies a uniform
argument instead of assuming the computed high part is monotone. Conditional
on Theorem 2 and |y_l|<2^-49.883, when i_e=-1075, the true scaled exponential
is at least exp(nextup(x-)+1075·log(2))>1+2^-44. Subtracting the stated
approximation error and low-part bound still leaves y_h>1 in every mode.
When i_e=-1022 on the subnormal branch, monotonicity of the *real* exponential
and the upper endpoint instead give y_h<1, with a margin exceeding 2^-45.
That margin also prevents rounding the p=0 construction across 2. These are
conditional mathematical deductions from uniform bounds, not an extrapolation
from one tested output.

## What the revised exp document still needs

1. Bind it to a concrete implementation commit, reconcile its fast allowance
   with the C constant, and cover the actual accurate-path domain |x|>2^-54;
   its current theorems start at |x|≥2^-53. These source/document discrepancies
   predate this week's proof extension.
2. In the new normal-path argument, use x≥x0, x'=x−i_e·log(2), and
   “rounding of exp(x)”. The “less than 46”/“more than 46” split omits exactly 46;
   the hard-case premise must include **at least 46** identical bits.
3. Cite and preserve evidence that the normal and four-case subnormal hard-case
   lists are complete over their stated domains. Passing a corpus checks its
   members; it does not establish completeness. The four listed subnormal cases,
   old/new database keys and boundary neighbors are included in the focused
   test inputs. The actual database filter is tested through the C implementation,
   rather than replaced by the manuscript's abstract “exceptional” predicate.
4. State the mean-value bound on the hull J of r and D. State the reduction
   lattice correctly: the rounded product is a multiple of ulp(l2s)=2^-154,
   not necessarily an integer multiple of l2s itself. The prior lattice argument
   remains applicable.
5. Complete the fast-path subnormal error accounting, including the addition of
   the FastTwoSum residual and scale-dependent rounding of f_l±eps. Restrict
   the formal model claim to contraction off until the other evaluated trees
   are modeled. Compiler tests with contraction enabled are empirical evidence.

The full exp correctness theorem is therefore **not certified by this review**.
The useful completed outputs are reproducible counterexamples, tested candidate
changes, faithful conditional model bounds, and explicit remaining obligations.

## Other changes and scope

The log2 sign correction and sinh mask-width correction are upstream. The
revised exp proof adopts the corrected derivative bound. New corpus rows occur
in sinpi, cospi, tanpi and acosh; no existing noncomment row was removed from
the 25 selected corpora. The new tanpi rows close its measured gaps. Sine's
proof change is formatting only; the prior arithmetic obligations are retained,
and its source coverage is refreshed at the new implementation pin.

Changed special-checker exit handling is reviewed and separately compiled; no
unbounded special-test campaign is claimed. Source changes in other precisions
and functions outside the selected 25 are deferred. The implementation pipeline
was successful at the cutoff; proof CI was inaccessible (HTTP 403). Neither
status substitutes for these local checks. The separate
[bivariate pilot proposal](../../docs/BIVARIATE-PILOT.md) has not been executed.
