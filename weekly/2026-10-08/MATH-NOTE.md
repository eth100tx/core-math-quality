# Sine: missing high-word arc and the new threshold

Scope: implementation `84674bfadb0f920614355024c87a3eef73f2d938`, proof sources
`57f6899abefaaf768d6a84e2bbc24944dcb650f2`, binary64, the four IEEE rounding modes.
This note separates exact certificates, finite directed-enclosure checks, and
the implementation-to-model argument. It is not a proof of correct rounding for
every binary64 input: the separate historical hard-case searches are not rerun.

## 1. Distance certificate

Set `d=(17/16)*2^-61`. For every finite binary64 `x` with `|x|>=2^-16`,
the distance from `x` to every multiple of `pi/2` exceeds `d`.

For `2^-16<=|x|<1`, the assertion follows directly from the distances to zero
and to `pi/2`. For `|x|>=1`, write `|x|=m*2^e`, where
`2^52<=m<=2^53-1` and `-52<=e<=971`. Relax the mantissa to `1<=m<=Q=2^53-1`.
For each of these 1,024 exponents, enclose `alpha=2^(e+1)/pi` by `[L,H]`.
The continued-fraction best-approximation theorem of the second kind says that
the minimum of `|m*a-p|` for `1<=m<=Q`, integers `p`, is attained at a convergent
of `a=(L+H)/2`. All convergents with denominator at most Q are considered,
including both possible denominator-one convergents. The next denominator must
exceed Q; an unexpectedly terminating fraction is rejected.

If the minimum is `b`, then for every allowed m and every p,
`|m*alpha-p| >= b-Q*(H-L)/2`. Multiplication by the lower bound for `pi/2`
gives the certified distance. All 1,024 lower bounds strictly exceed d.

`distance_certificate.py` uses exact rational arithmetic. The pi enclosure comes
from Machin's identity and alternating arctangent series with 384 terms, rounded
outward to a 1,536-bit dyadic interval. `DISTANCE-CERTIFICATE.json` records that
interval, every exponent, the minimizing convergent, the next denominator and
the exact lower bound. Its approximate logarithm is display information only.
The standard continued-fraction theorem is an explicit mathematical dependency;
the small brute-force self-check is not a substitute for that theorem.

## 2. Bind the accurate reducer to the actual table

`reducer_certificate.py` independently checks all 1,040 biased exponents
1007 through 2046, exactly the finite input range `|x|>=2^-16`. It reconstructs
the three shifted words used by the C code and identifies them with
`floor(2^192*2^(e-1075)/(2*pi)) mod 2^192`, using the directed pi enclosure.
This includes `i=-1` at the small end and the restored `_T[19]` at the large end.

Multiplying by `m<2^53` leaves an omitted tail less than `2^-139`.
Discarding the low 64 bits of `m*V2` loses less than `2^-128`.
Unsigned multiplication/addition modulo `2^128` preserves the required
fractional part; centering the residual preserves the value modulo one.
Thus the fractional reduction error is positive and less than
`2^-128+2^-139`. Multiplication by `2*pi` produces an argument error less than
`7*2^-128`. This is a bound over all mantissas, not a sampled reducer test.

## 3. Fixed-point approximation and absence of wrap

The three proposed changes in `acclarge-reference.patch` make the uppercase
reference quantities ideal polynomials: `S5` and `C6` use `U2`, and `T5` uses
`C4`. Polynomial approximation errors remain explicit hypotheses.

The supplied exact Taylor/Bernstein checks bind PS/PC coefficients to this C
snapshot. Cosine's bound is non-strict `<=2^-128`, since equality occurs at zero.
The directed MPFR table enumeration checks every one of the 4,096 table pairs,
their error bounds and intermediate addition/subtraction ranges. It establishes
the hypotheses `|eps2|,|eps3|<=20298*2^-140` and normalized table values in `[0,1]`.
The pi/4 constant and sine polynomial checks establish the other Gappa inputs.

In particular the model defines `U=(pi2+eps1)*(8*r_red)=2*pi*r_red`
exactly, while lowercase u models `mhUU(twopi,r<<3)` including its truncation.
W1/W2 refer to ideal trigonometric expressions at U, not at the computed u.
The constant and multiplication errors are therefore already inside the 13/10
unit bounds, rather than an omitted extra term in the final budget.

For the corrected reference model, Gappa 1.8.2 proves
`|w1-W1|<=13*2^-128` and `|w2-W2|<=10*2^-128`.
The separate range goals check the internal polynomial arithmetic before
identifying the real fixed-point expressions with unsigned C operations.
`mhUU` omits only nonnegative low terms and underestimates a product by less
than three units of `2^-128`; its positive partial sums cannot overflow when
its inputs lie in `[0,1)`.

Combine w1/w2 in mathematical integers first, with the signs prescribed by
the quadrant and residual. Taking an absolute value does not enlarge an error.
The normalized magnitude S therefore satisfies
`|S-|sin(x)|| < (13+10+7)*2^-128 = 30*2^-128 < 2^-123`.
This argument precedes, and does not assume, the absence of wrap in the final
unsigned addition.

By Section 1 and elementary sine/cosine Taylor inequalities,
`|sin(x)| >= d-d^3/6 > 2^-61+2^-123`, and
`1-|sin(x)| >= d^2/2-d^4/24 > 2^-123`.
The script checks both final inequalities exactly. It follows that
`2^-61 < S < 1`. Consequently the final addition cannot wrap, and if J is the
integer passed to `u128_tod`, then `J>2^67` and `J>>64>=8`.

The high-word-zero arm is therefore unreachable from `cr_sin` in this pinned
implementation. Also `sh<=60`, so the two shift counts `75-sh` and `74-sh`
are at least 15 and 14. Zero and negative-shift helper inputs are excluded.
This is a source-and-certificate argument, not a coverage-counter inference.

## 4. Conversion contract

`u128_tod` is a rounding proxy, not a general ties-to-even conversion of J.
Let a be its retained 53-bit value and u its ulp. For positive J it rounds
`a+3u/8` if the round bit is zero, or `a+3u/4` otherwise. Away from exact
representable points and midpoints, this proxy is in the same rounding cell as
`J/2^128`; sign reversal exchanges the directed modes. Multiplication forming
a is exact, so contracting that operation into the final addition is harmless.

At an exact midpoint the generic conversion description is false: for
`J=2^127+2^74`, nearest-even rounding of `J/2^128` returns `0.5`, whereas this
proxy rounds up. This is not a demonstrated public `cr_sin` failure.
The paper should connect the proxy lemma to its hard-case partition: outside
the certified hard cases the approximation error cannot cross or land on a
rounding boundary, while the corpus checks the actual implementation on the
exceptional inputs. This dependency must remain explicit.

The required separation is absolute: greater than `2^-123`. For
`|sin(x)|>=2^-27`, the paper uses its 43-bit hard-case partition; below that
crossover it uses a separate near-multiple-of-pi enumeration with a `2^-106`
absolute threshold. We checked the revised description and executed the corpus,
but did not regenerate those historical searches or independently certify their
completeness. That open reproducibility scope does not affect the branch proof.

## 5. Newly routed interval

The code, Algorithm 1, Theorem 1 and AccurateSmall now agree on the split:
tiny for `|x|<2^-26`, small accurate for `2^-26<=|x|<2^-16` when needed.
The old tiny threshold is `x0=0x1.7137449123ef6p-26`.

The original smallacc.g is retained. The driver checks its final goal and both
magnitude preconditions for both signs and all four modes. Additional goals
put H2 and the exact computed first sum s2 in `[-0.2,-0.15]`, strictly inside
one magnitude binade. Consequently `ulp106(s2)=2^-108 <=2^-105*|H2|`,
justifying the model's eps2/H2 hypothesis. The independent approximation
certificate covers `[0,2^-16]`.

This clarifies the model-to-paper binding; it is not a numerical failure.
The original eps5/s5 hypothesis is also justified directly
by the exact-sum statement of FastTwoSum revisited, Theorems 9-11. Gappa's `//`
denotes relative magnitude (quotient), not its `-/` relative-error operator.
The final Gappa goal bounds error against the polynomial S(x). Combining
`2^-103*|S(x)|` with the independently certified polynomial error below
`2^-112.743*|sin(x)|` gives a strict bound below `2^-102*|x|` here.

The moderate fast path cannot return on the newly routed interval: its rounded
index is k=0, both table sine values and fh are zero, and `|fl|<2^-24`.
Thus each fl+/-eps endpoint has ulp at most `2^-76`, whereas
`2*eps>2^-63`. Rounding the two endpoints cannot make them equal; adding fh=0
is exact. The code consequently reaches the small accurate path. The existing
moderate Gappa checks also retain their full residual domain.

For the additional interval `[2^-26,x0]`, `new_interval_certificate.py` proves
that every possible difficult case lies in the contiguous 4,097-input suffix
ending at x0, with both signs. It uses monotonicity of `D(x)=x-sin(x)`, exact
alternating Taylor bounds, spacing `2^-78`, and the conservative error allowance
`x0*2^-102`. The special binade endpoint `2^-26` is handled separately.
The targeted corpus contains this entire suffix, not merely a sample of it.
The certificate checks containment and the actual four-mode result manifests;
the upstream WORST_SYMMETRIC checker supplies both signs.
Together with successful four-mode tests, this removes a new-interval
dependency on unspecified historical hard-case search limits.

## Reproduction and limits

Run the exact certificate scripts, directed table checker and each supplied
Gappa goal; inspect the result manifests and all return codes. Gappa 1.8.2 is
required for the syntax used here. The generated goals are independent files.
No upstream source is changed. The errno candidate changes only `ax` to `au`.
The broader correct-rounding argument still relies on the cited historical
hard-case search completeness outside the newly routed interval. Corpus passes
and this branch proof do not replace that separate obligation.

## Transfer to the latest sine source

At `74fcd1094a316164c94481f40f5c9658439bee63`, upstream removed the
high-word-zero alternative. Comparing complete executable sin.c with comments
and whitespace stripped verifies no other sine arithmetic change since the
PDF-cited pin. Both candidate copies contain only the same ax-to-au errno fix.
The bound J>>64>=8 therefore validates the latest direct clz call too. Fresh
GCC corpus/coverage checks pass and measure 177/177 lines and 42/42 arcs.
