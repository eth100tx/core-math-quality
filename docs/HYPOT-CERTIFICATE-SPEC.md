# Restricted hypot certificate: exact-integer checker specification

**Design v1, October 26. Not a runner qualification, search result, imported
certificate validation or completeness proof.** This is a first implementation
target that does not depend on receiving any earlier research archive.

## Domain and exact representation

Accept only positive finite binary64 x,y in [1,2), with x²+y² in [4,8).
All quantities below are exact integers. Decode each input's 16-digit hexadecimal
IEEE-754 bit pattern; reject decimal input, invalid length, negative values,
NaNs, infinities and values outside the domain. Do not parse through a host
floating-point computation. Byte order is irrelevant to the written integer
bit pattern.

Write x=X·2^-52 and y=Y·2^-52, where 2^52 ≤ X,Y < 2^53.
Set S=X²+Y². Check 4·2^104 ≤ S < 8·2^104. Therefore the exact result sqrt(S)·2^-52
is in [2,2√2), within the output binade [2,4).

The certificate supplies the lower binary64 bracket L=K·2^-51 and its immediate
successor U=(K+1)·2^-51, with 2^52 ≤ K < 2^53. The checker must decode both bit
patterns, verify adjacency (U=4 is unreachable in this domain), and independently check

    4K² ≤ S < 4(K+1)².

It must not trust a supplied K, residual, bracket or expected answer. Verify all
redundant fields against decoded bits. Wrong brackets are rejected even if a
claimed expected answer happens to be right.

## Four rounding decisions

If S=4K², the result is exactly L in every mode. Otherwise:

- toward zero and toward minus infinity return L;
- toward plus infinity returns U;
- nearest/ties-to-even compares S with (2K+1)², the square of the midpoint
  scaled by 2^104. Below returns L; above returns U; equality returns L if K
  is even and U if K is odd.

These conclusions use monotonicity of squaring on nonnegative reals. They are
only about the restricted input/result domain. They do not justify extending
certificates across underflow, overflow, signs, NaNs or arbitrary rescaling.
Midpoint handling is specified whether or not such a case is produced by a
particular search. No assertion about existence or completeness of tie families
is made here.

## Proposed record and worked exact case

The record is deliberately small. Unknown fields and unsupported versions must
be rejected. Four result encodings are mandatory; comparisons use integer bits.
Require canonical lowercase `[0-9a-f]{16}` encodings without a prefix, and reject
duplicate JSON keys at every nesting level (for Python, use an appropriate
`object_pairs_hook`). Require `schema_version` to have exact integer type, not
a boolean or floating value. Decode sign zero and exponent 0x3ff for x and y,
and sign zero and exponent 0x400 for L. Reject missing or extra expected-mode
keys. Validate U independently against the decoded successor.

```json
{
  "schema_version": 1,
  "domain": "positive-unit-binade-normal-result-v1",
  "x_bits": "3ff8000000000000",
  "y_bits": "3ffb800000000000",
  "lower_bits": "4002400000000000",
  "upper_bits": "4002400000000001",
  "expected_bits": {
    "rndn": "4002400000000000",
    "rndz": "4002400000000000",
    "rndu": "4002400000000000",
    "rndd": "4002400000000000"
  }
}
```

Here x=48/32=1.5 and y=55/32=1.71875. Since 48²+55²=73²,
hypot(x,y)=73/32=2.28125 exactly. X=48·2^47, Y=55·2^47,
K=73·2^46, so S=73²·2^94=4K². This single arithmetic example checks the
specification's scaling and encoding; it is not a hard-case discovery or a
claim that the example is absent from the upstream corpus.


### Worked midpoint case

Let m=2^51−1, X=3m, Y=4m and K=(5m−1)/2=5·2^50−3. Both inputs are
in the domain, and S=25m²=(2K+1)², exactly the midpoint square. K is odd:
nearest-even and upward return U; downward and toward zero return L.
The independently integer-checked encodings are:

| Field | Encoding |
|---|---|
| x | `3ff7fffffffffffd` |
| y | `3ffffffffffffffc` |
| L | `4003fffffffffffd` |
| U | `4003fffffffffffe` |

This is a worked arithmetic fixture, not a new search result or a corpus-novelty
claim. The executable checker and C runner still need implementation/qualification.

## Required implementation tests and receipts

1. Positive fixtures: exact example, strict brackets on both sides of a midpoint,
   a reachable tie, and a bracket with L=2 (an exactly equal hypot result of 2 is
   impossible here, but a result just above 2 is reachable). Test synthetic tie
   logic separately from claims about actual hypot inputs.
2. Negative controls: one-bit-corrupted expected result, wrong adjacent endpoint,
   non-adjacent bracket, swapped/reversed bracket, malformed bits, unsupported
   domain/version, unknown fields and out-of-domain values. An independent
   checker must reject them. A deliberate generator bug must not be accepted by
   sharing the same unchecked intermediate calculations.
3. Receipt: verifier hash/version, schema version, per-record result and reason,
   checked count, rejected count, limits and CPU/wall time. Avoid Python asserts
   as the sole acceptance boundary; optimization must not disable checks.
4. A **separate** pinned CORE-MATH runner feeds exact bit patterns to C, verifies
   the observed inputs and rounding mode, and compares returned bits in all four
   modes. Record returned values, each floating-point flag and errno separately.
   The integer checker alone does not qualify C execution or exception behavior.
5. Check the supplied certificate table independently. A family-table check is
   not regeneration of the search that claimed to enumerate that family; a
   completeness claim requires its domain, enumeration/proof and separate audit.

First implementation budget: one CPU-hour / 30 wall-minutes, with per-phase
checkpoints and outer timeout. Stop on a failed control or unresolved decoding
assumption. No search is enabled until the checker and runner qualify.
