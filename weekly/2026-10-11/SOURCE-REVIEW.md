# Source and proof review — October 11

Implementation: `81a899d67953a619d703660fd9630f0554673524`.
Proof: `58df57e5a46310d0e47d140ad23f146461788e0e`.
The report separates source reasoning, finite experiments and unresolved proof dependencies.

## Two small proposed corrections

**log2, line 307.** The unsigned sign bit `(t.u ^ w.u) >> 63` is either 0 or 1.
The new expression `2*bit+1` therefore returns +1 or +3. The previous branch
returned +1 or −1. `1-2*bit` preserves the earlier expression for both possible
signs, without a branch. The source comment says opposite signs cannot occur;
that reachability claim is not proved here. This is a conditional source
equivalence defect, not a demonstrated public wrong-value witness. The candidate
has no change when the documented same-sign invariant holds.

**sinh, line 355.** The masked value has up to 52 bits, but the new declaration
uses a 32-bit `int` in the tested configurations. Restoring `int64_t` preserves
the intended test. Narrowing can add unnecessary database calls; it cannot
remove a call when the full masked value is at most 16. The database returns
its argument unchanged when no key matches. No wrong-value result follows
merely from observing an extra call. The second site already uses `int64_t`.
For the existing corpus input `0x1.05a1a1b748058p+6`, RN, the observed tail
encoding is `bc9fffffffffffe8`. The intended mask is 4503599627370480,
but its signed 32-bit truncation is −16, reversing the `<=16` routing test.
This is a routing witness, not a new incorrect-rounding witness.

## Coverage target and finite database checks

The exp-family inner loops try the three neighboring encodings. Those have
three distinct residues modulo four, so changing their order does not change
the selected result. The fourth residue would exhaust the loop. Removing the
outer `break` would then repeat the same database match indefinitely.

The inner loop is reachable only if the original public input's bits equal one
of the literal `db[]` keys. Nonmatching binary-search iterations strictly
shrink the interval. This supplies a finite *necessary trigger set* for the
question. The supplementary checker extracts every key, verifies uniqueness
and unsigned ordering, and runs them through the public entry point in all
four modes. Instrumentation counts entries and aborts on exhaustion. It does
not feed arbitrary low-level `f` values to the helper.

Passing this finite replay supports the instrumented configurations and the exact
source reduction. Successful optimized returns alone cannot prove the state is
unreachable: the compiler may assume a side-effect-free loop terminates.
Instrumentation can change code generation, so the checks do not certify the
uninstrumented binaries' intermediate helper arguments. This is deliberately
bounded verification, not a completed unreachability proof. It does not prove a portable caller approximation bound or
certify arbitrary helper arguments. Raw gcov misses remain in the report;
they are not hidden by a synthetic witness. Portable arithmetic closure of
the caller/three-neighbor relation is explicitly deferred.

**Stronger check for the selected exp target.** We also capture x and f at
the helper's entry in byte-identical copies of the actual baseline O3 binary
and its O0/gcov companion, using debugger breakpoints rather than changed C.
The disassembly confirms the argument-register mapping and the literal-key
comparison. All 51 keys are replayed in each mode; every helper call records
the rounding-control bits and verifies FTZ/DAZ are off. For a matched key of
index m, exhaustion is exactly `(bits(f)+2) mod 4 == stored_residue[m]`.
The saved arguments all fail that equality. O3 and O0 argument sets agree.
Keys which bypass the helper in a mode are still checked through the public
entry point. This supplies binary-specific finite-reduction evidence for
the missing arc, under the recorded floating-point environment, without
assuming that successful optimized returns prove source-loop termination.
[Production capture](production-capture/receipt.json),
[coverage-binary capture](coverage-capture/receipt.json),
[offline replay](verify_exp_capture.py). Portable arithmetic closure, other
binaries/platforms and arbitrary helper arguments remain outside this result.

## Other removed predicates

- **exp tiny guard:** `as_exp_accurate` has one public caller. The public tiny
  exit covers the removed strict exponent range below `0x3c9` (2^-54).
- **exp/exp2 sign step:** arithmetic signed right shift yields 0 or −1 on
  the qualified GCC/Clang x86-64 profiles, preserving the old ±1 update.
- **exp2 zero tail:** exact integer inputs bypass the accurate path through
  the `frac == 0` checks, including the subnormal interval. This explains
  exact integer cases but is not a general proof of noncancellation for
  every noninteger accurate-path input. Instrumentation is empirical evidence.
- **log/log10 subnormal branch:** in the enclosing special-case block, NaN,
  infinity, zero and negative inputs return before normalization. Remaining
  inputs are positive subnormals. `cr_log_accurate` is only called by `cr_log`,
  whose fast path handles x=1; the removed x=1 check is redundant in that call
  context.
- **log/log10 sticky bit:** correctness still depends on the cited hard-case
  bounds and the exclusion of exact results from this conversion. This review
  did not regenerate the historical exhaustive searches. Exact powers of ten
  and x=1 are included in the supplementary public-entry checks.
- **sinh/cosh exponent-gap predicates:** source comments alone do not prove
  `ml>16` excludes `eh-el>103`. The instrumented corpus check tests that
  implication at both sites. A complete mathematical justification remains
  an explicit dependency, irrespective of zero observed violations.
- **sinpi/cospi shifts:** the preceding small-input exits imply biased
  exponents at least 1018 for sinpi and 1011 for cospi, so `si=e-1011`
  is nonnegative. The preceding large-input exit bounds `si<=52`.
  In cospi, the `si-1` shift occurs only on the integer/half-integer path;
  for `si=0`, the nonzero 53-bit significand shifted once cannot be zero,
  so that path is not taken. Shift-sanitized regression complements this
  range argument. New integer/half-integer corpus inputs are genuine test
  additions, distinct from coverage changes due to removed predicates.

## exp proof revision

The changed Gappa model is replayed with the concrete goal
`|dxr-dx_real| <= 1025*2^-128`, which is stricter than 2^-117.99,
for nearest-even, zero, upward and downward rounding, both with ordinary dxll
evaluation and with its multiply/add contracted to an FMA. Its exact-operation
assumptions need the following manual source binding; a successful Gappa
return alone would not establish them.

The source uses `roundeven_finite`, matching `int<ne>`. Cross-statement
contraction of dxl into dxh is excluded by our explicit `-ffp-contract=off`
builds; other compilation modes require separate source/binary binding.
The accurate reduction
computes the same constants and operation sequence as the model; the exact
second subtraction permits the source's `(dx-dxh)+dxl` variant. For t=0 the
reduction is trivial. Otherwise the unchanged reduction lemma supplies exact
dx, its 2^-66 grid and magnitude bound; l2h*t fits exactly in 52 significant
bits (29+23). For t=0 and the public accurate-path domain |x|>2^-54,
x belongs to 2^-106 Z, so the final 2^-154 grid conclusion also holds.
The rounded b=l2l*t has magnitude between 2^-47 and 2^-24,
and lies on the 2^-99 grid. Thus dx is a multiple of ulp(b).

Lemma 2 of [FastTwoSum revisited](https://www.arith2025.org/proceedings/215900a141.pdf)
applies to faithful rounding, including all four modes, and makes the second
subtraction exact. The sum error lies on the 2^-99 grid and has magnitude
below 2^-66; at most 33 significant bits suffice, so the residual is exact
and cannot underflow. The l2l*t product residual also has a 2^-99 grid and
magnitude below 2^-77; the FMA computes it exactly. The constants and
intermediate values are far from overflow and underflow.

For the final lattice claim, l2s belongs to 2^-154 Z. Rounding a lattice
multiple preserves that lattice, as do the additions here. Consequently
dxll, Dl and Dh+Dl lie in 2^-154 Z. The paper's wording “dxs is an integer
multiple of l2s” is stronger than required and should instead refer to this
binary lattice. Its set-membership symbol between the two lattices should
be inclusion. These are presentation corrections, not new numeric failures.

The displayed derivative estimate is independently false: Q'(0)=1, whereas
2^-0.99<1. This term predates this week's edit; it was found while reviewing
the revised sum. An exact rational coefficient calculation on |z|<=9/100000
bounds |Q'(z)|<1.0001. This interval contains the cited reduction interval
and D: |dx|<2^-13.523 and the coarse |D-dx|<2^-23 bound leave sufficient
margin, checked by an exact rational comparison.
Consequently the mean-value term is less than 2^-116.47 (using
1.0001<2^0.01). The corrected final sum is below 2^-100.29, consistent with
the theorem statement. A focused text patch and exact derivative calculation
are supplied. We check the corrected sum independently at high precision; the
derivative correction does not require changing the stated final bound. This does
not rerun the entire exp proof, its polynomial generation, or historical
full-domain hard-case searches. The existing subnormal rounding-error FIXME
remains open. Also, the paper's commented-out `th==1.0` branch and its stated
accurate-path lower threshold do not completely describe the current C path;
our reduction lemma covers the extra t=0 region, but the full branch proof is
not closed by that fact. The Gappa header's t>=2 text and stale Sage error comment are
also editorial leftovers; the active hypothesis includes t=±1.

## Prior sine work and scope boundaries

The errno name correction and three ideal-reference corrections from October8
are checked against upstream bytes. Prior sine obligations retain the
October8 dispositions and certificates. The new proof text only changes its
date/acknowledgement after those fixes; it does not require rerunning unchanged
goal sets. The strict baseline keeps `-fno-finite-math-only`; a separate
supplementary check uses sine's `-ffinite-math-only` setting explicitly.

All changed implementation/proof paths are inventoried. Binary16, bfloat16,
binary128 and binary64 pow are outside this workbench's 25-function test scope
and are deferred, not declared clean. The changed sincos performance harness
now consumes x+y to discourage elimination of cosine work; this changes timing
interpretation and is not used by our correctness runner. No performance
benchmark claim is made. Open merge requests outside the selected scope remain
unreviewed. Implementation CI is observed separately; proof CI could not be
read (HTTP403), which is an availability limitation, not a failed pipeline.
