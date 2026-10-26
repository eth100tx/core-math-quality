# Focused sine, asin and hypot review — October 26, 2026

**The changed sine kernel passes the selected exact proof checks and four-mode
GCC/Clang regressions. No new wrong-value or compiler defect was found.**
This is a requested follow-up, not a new whole-repository certification or
coverage campaign. Exp work is paused to avoid duplicating another effort.

1. **Sine: checked.** Independent exact certificates establish the new PS/PC
   approximation bounds; 13 Gappa goals pass and all nine coefficients match
   the implementation, model and proof. Normal and forced-accurate corpus runs
   pass. Historical full-domain hard-case completeness remains a separate premise.
2. **Asin: tested cleanup.** An [optional unsigned-gap patch](../../candidates/asin-unsigned-gap/README.md)
   removes the hard-case predicate's dependency on `long` width and signed casts.
   It is not a demonstrated wrong-answer fix. The complete corpus passes;
   Linux sanitizer checks find no issue in the original selected code.
3. **Hypot: feasibility quantified.** Literal enumeration of the restricted
   Cartesian domain is infeasible. The [compact certificate checker](../../hypot_verify.py) is useful for
   supplied cases, but is not a complete-domain proof or completeness census.
   The next task is bounded case construction and corpus deduplication.

Implementation: `336752ca18e1204321225ec90c1f43fcb90ada1b`.
Proof: `d0fc1625fd88f9987bc89c83e271b39b8201b7f7`.
[Changed-file inventory and deferrals](SOURCE-REVIEW.json).

## Sine: what was established

The transformation uses `U=8R`, with coefficients for sine/cosine at `(pi/4)U`.
The old `mhUU` multiplication by the pi/4 constant disappears. In the reducer,
masking gives `0<=u<2^115`; the centered branch maps its upper half to
`2^115-u`. Thus the returned magnitude is **at most** `2^114`, including the
endpoint. Shifting by three is exact and gives `U<=2^-11`. This is a direct
integer bound, not an inference from test inputs.

The actual dispatcher uses the large accurate kernel only for `|x|>=2^-16`;
smaller inputs use the small accurate routine. The new lower-domain C comment
is too broad and should say `|x|>=2^-16`; it does not change the dispatcher.

| Claim | Independent evidence |
|---|---|
| `|PS(X)-sin(pi*X/4)| < 2^-128.605`, `|X|<=2^-11` | Exact rational Taylor/Bernstein certificate, 306 cells |
| `|PC(X)-cos(pi*X/4)| <= 2^-128`, same domain | Exact certificate, one cell; equality at zero retained |
| Fixed-point evaluation and intermediate ranges | 13 Gappa 1.8.2 goals, including no-underflow/no-wrap ranges |
| C/model/TeX correspondence | Nine coefficient integers/scales match; ideal reference signs, powers and `U=8R` match; certificate bounds fit Gappa hypotheses |
| Conditional combined absolute error | Exact bound below `2^-123.358`; six reported numerical bounds checked against exact dyadic Gappa endpoints |

[Certificates](polynomials.json), [binding and numeric checks](bindings.json),
[Gappa goals/logs](gappa/), [mathematical details](MATH.md).
The upstream Sollya generators use `dirtyinfnorm`; their sampled norm is not
treated as a proof. Our independent certificate supplies the rigorous bound.

Seven previously reviewed components—the reciprocal table, three trigonometric
tables, accurate reducer, `mhUU`, and conversion helper—are unchanged apart from
comments and collapsed whitespace relative to the October 8 latest checked
source `74fcd109`. Full declarations and five supporting type/macro definitions
are included in the comparison. The new error
bound is smaller than the earlier `30*2^-128` allowance. Consequently the
[earlier distance/reduction and conversion-range argument](../2026-10-08/MATH-NOTE.md)
remains applicable to these components; it is reused with its original scope,
not advertised as newly regenerated. [Comparison receipt](UNCHANGED-COMPONENTS.json).
The formerly proposed `S5`, `C6`, `T5` reference corrections are present in the
current model. They are resolved revisions, not new findings.

The complete pinned sine corpus has 1,975,927 rows, expanded to 3,951,854 checks
per mode by the upstream sign symmetry. Both GCC 13.3 and Clang 18.1.3 pass
the four modes in each of two builds: unchanged public entry point, and a
test-only wrapper forcing the accurate kernel for its actual caller domain.
Both also pass the separate boundary-neighbor corpus. Builds are O3, baseline
x86-64, contraction off, `-frounding-math`, errno enabled, without coverage.
The Clang profile omits `-fsignaling-nans`.
The upstream checker performs value and its supported exception/errno checks.
No new FMA-contracted, x86-64-v3, ARM or other-platform run is claimed.
[Commands, hashes and raw outputs](SINE-REPLAY.json).

An initial test wrapper used unavailable math declarations and failed to link;
the wrapper was corrected before any forced-path result was accepted. This was
a harness failure, not an upstream defect. A deliberately wrong coefficient and
an incompatible polynomial-error hypothesis are both rejected by the certificate
checks. [Control results](controls.json).

## Asin: a small, optional portability improvement

The current `dn/de` calculation depends on the width and conversion behavior of
`long`. Replace it with an unsigned distance and the equivalent intended tests:

```c
uint64_t gap = tn.u - tl.u;
int hard = (gap <= 2) || ((gap >> 52) > 47);
```

For `tl.u,tn.u<2^63`, the old LP64 subtraction is defined and this expression is
equivalent. The low 52 bits of `tn.u` are zero by construction. Under a 32-bit
modulo-conversion implementation, the old predicate can make extra database
lookups; its signed subtraction is not itself an overflow because the converted
`tn.u` is zero. A database miss returns the original result; a database hit relies
on the entry's existing correctness. No reachable wrong-answer witness or
compiler miscompilation is claimed. The proposed predicate is defined using
unsigned arithmetic on either ABI. The [candidate note](../../candidates/asin-unsigned-gap/README.md)
gives the algebra and its premises.

The 249,134-row full corpus (498,268 signed tests per mode) passes on both
compilers with the patch. The original code also passes all four modes under
undefined-behavior/float-cast-overflow sanitizers; an injected signed-overflow
control is rejected by each sanitizer. [Receipts](ASIN-HYPOT-REPLAY.json).
Synthetic encoding tests support the predicate argument but are not asserted
reachable inputs. Windows/32-bit execution remains unqualified, and a complete
proof of all `phi/ph` range preconditions has not been supplied by these tests.

## Hypot: what checking the entire restricted domain would cost

Let `N=2^52`, `x=X/N`, `y=Y/N`, and `N<=X,Y<2N`. Here the domain restriction
means the **exact real** norm is at least 2; its upper bound is automatically
less than `2*sqrt(2)<4`. There are approximately
`(sqrt(3)-pi/3)*2^104 = 1.3890474264e31` ordered admissible pairs.
The [exact count enclosure](hypot-domain.json) bounds this number within `2N`;
it does not enumerate the pairs. Symmetry saves about a factor of two.
If “result in [2,4)” instead includes inputs just below the real boundary whose
rounded result becomes 2, those extra boundary cases are outside this enclosure;
they do not make exhaustive checking feasible.

Even an assumed **one billion fully checked pairs per core-second**, including
all four modes, would require roughly **4.4e14 CPU-years** (half with symmetry).
That is an illustrative optimistic rate, not a measurement or a lower bound
on every possible proof/search algorithm.

The supplied bounded timing harness checked 100,000 deterministic pairs in
`[1.5,2)^2` in all four modes, comparing with correctly rounded MPFR at 53 bits
and separately checking flags and errno. All checks pass. Measured harness CPU
time was about 0.206 s with GCC and 0.185 s with Clang—about 0.49–0.54 million
four-mode pairs/s. A literal extrapolation is about 8–9e17 CPU-years. This timing
includes MPFR, random-input generation and environment operations; it is not
`cr_hypot` speed, a representative full-domain benchmark, or new qualification.
It avoids the circle boundary and makes no hard-case completeness claim.

The practical alternative is to generate exact ties and near-midpoint cases,
check compact exact-integer certificates, deduplicate against the pinned full
corpus, and retain only useful regressions. A proof or structured completeness
algorithm may avoid pair enumeration; no cost for such an unspecified algorithm
is claimed. The 18 earlier qualification fixtures and the missing research
archives are distinct: archive-family completeness has still not been reproduced.

## Review, reproduction and next checkpoint

Claude Opus 5.5 (`claude-opus-5-5`) independently reviewed the plan and mathematical tools;
the final assembled review and dispositions are recorded in [REVIEW.md](REVIEW.md).
Advisory review did not execute the checks; the orchestrator ran and verified them.
[Reproduction commands](REPRODUCE.md) and checksums accompany the evidence.

On November 1, first inspect correspondence and new commits. Keep exp and
routine coverage paused. Do not repeat these unchanged checks. Reconcile
candidate pickup, finish a named remaining asin range premise if useful, and
select at most one bounded hypot construction/deduplication task. The cosine
sign-normalization change, earlier log-model work, and unavailable angular/pow
archives retain explicit deferrals. No global review watermark advances here.
