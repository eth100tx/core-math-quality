# Certificate and composition details

## Polynomial certificate

`certify_polynomials.py` extracts PS/PC integer literals directly from the selected
C source and records its SHA-256. Signs, powers and scales correspond to the
reviewed alternating Estrin evaluation; `check_bindings.py` also checks those
ideal expressions in Gappa and the coefficient integers in TeX.

Machin's identity `pi=16*atan(1/5)-4*atan(1/239)` and 160-term alternating
series provide a rational enclosure, rounded outward to 512 fractional bits.
No floating-point estimate is used in a decisive comparison.

Set `t=(2048*X)^2`, so `t in [0,1]`. Expand sine through degree 17 and cosine
through degree 16 at `(pi/8192)*sqrt(t)`. Their Taylor remainders are bounded by
the next nonzero term, using the upper endpoint of the pi interval. In the
odd case factor out `sqrt(t)`; in the even case retain the polynomial in t.
Coefficient uncertainty is enclosed term by term since t is nonnegative.
Transform each interval to Bernstein coefficients; their convex hull encloses
the polynomial exactly. Adaptive subdivision accepts only rationally proved
cells, and the accepted cells are checked to cover [0,1] without gaps/overlaps.
Parity extends the result to negative X.

The sine target is a dyadic number strictly below `2^-128.605`. The decimal
calculation only proposes that target; the integer comparison
`numerator^200 * 2^25721 < denominator^200` proves its direction. For cosine,
the constant error is exactly `-2^-128`. Dividing the lower-error comparison by
t proves its sign for t>0 while retaining equality at zero. A strict cosine
bound at zero would be false.

`check_bindings.py` rejects a source-hash mismatch, verifies successful Gappa
receipts and model/log hashes, and checks that the certified PS/PC errors fit
the model's absolute `eps5` and `eps4` hypotheses in the same variable. Six
numerical endpoints are compared to the published powers using exact integers;
the other seven range goals are retained with their successful receipts.

## Integer arithmetic and composition

For normalized 128-bit integers, `mhUU` omits the nonnegative low-low product
and two middle remainders. Hence it underestimates the exact normalized product
by less than `3*2^-128`. Positive partial sums do not overflow. The separately
executed Gappa range goals establish the subtraction/addition ranges inside
PS/PC before identifying its real arithmetic with unsigned C operations.

Masking and centering in `reduce_large_acc` give a returned integer magnitude
in `[0,2^114]`, even at the exact half-cell endpoint. Thus `r<<3` is exact and
the polynomial domain is inclusive `[0,2^-11]`.

The signed angle-addition decomposition is the same as before: two table/kernel
products, with quadrant/residual sign selection, then the reducer's argument
error. Apply the triangle inequality before considering the unsigned final
sum. The new Gappa product bounds plus the published reduction-error bound
give an absolute error strictly below `2^-123.358`. Table errors and reduction
error are explicit premises, linked to the unchanged components and the prior
October 8 certificates; they are not silently inferred from the corpus.

The reduction term is in **absolute sine-output units**, just like the two
product errors. Section 2 of the [October 8 note](../2026-10-08/MATH-NOTE.md)
bounds fractional-turn error by `2^-128+2^-139`. Multiplying by `2*pi` converts
to radians; `|sin(a)-sin(b)|<=|a-b|` then bounds output error.
`check_bindings.py` recomputes a rational Machin upper bound for pi and proves
`2*pi_upper*(2^-128+2^-139) < 2^-125.347` by exact comparison. This agrees
with `eq2` in the pinned `sin.tex` (equation 5 on PDF page 7), which explicitly
bounds `|sin(2*pi*(z+R))-sin(x)|`. No fractional-turn bound is added directly
to output errors. The receipt retains both units and their conversion.

Full declarations and bodies of all seven reused components, plus both u128
type alternatives and their selection condition, u64, the two union types and
the U128 macro, match the October 8 latest checked pin `74fcd109` after comment
removal and whitespace collapsing. This is a conservative textual comparison;
it preserves whitespace separating operators. Declaration/operator mutation
controls pass. The older PDF pin `84674bfa` still had the redundant zero-high-word
branch; the October 8 note's final section explicitly covers its removal at
`74fcd109`. That already-reviewed change is not counted as new.

The bound is below the earlier `30*2^-128` allowance. Thus the previous
distance-from-multiples-of-pi/2 argument still gives `2^-61<S<1` and `J>2^67`
for the integer conversion input, excluding wrap and invalid helper shifts.
The conversion is a rounding proxy, not a fresh Ziv test with an error constant.
Full correct rounding still relies on the separately stated hard-case distance
and corpus-completeness premises. Neither finite tests nor this local update
regenerates the historical exhaustive searches.

## Hypot count enclosure

The inadmissible area inside [1,2]^2 is
`integral(1..sqrt(3), sqrt(4-x^2)-1) = pi/3-sqrt(3)+1`.
The admissible area is therefore `a=sqrt(3)-pi/3`.

For the N-by-N grid, an admissible lower-left corner makes its whole cell
admissible; counting upper-right corners bounds area from above. Shifting both
indices by one removes/adds only boundary rows and columns, with at most 2N
net difference. Therefore `a*N^2-2N <= A <= a*N^2` for the ordered count A.
`hypot_domain.py` recomputes the rational pi enclosure and uses integer square
root to enclose sqrt(3), then rounds both count bounds outward. The diagonal
count is `2N-ceil(sqrt(2N^2))`; the unordered count is `(A+diagonal)/2`.
This proves a narrow count enclosure, not completeness of any selected family.
