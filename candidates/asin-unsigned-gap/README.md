# asin: optional unsigned hard-case predicate

**Tested portability cleanup, not a demonstrated numerical or compiler bug.**
Base: `336752ca18e1204321225ec90c1f43fcb90ada1b`.
[Patch](asin-unsigned-gap.patch), [metadata](METADATA.json),
[full test receipts](../../weekly/2026-10-26/ASIN-HYPOT-REPLAY.json).
No upstream issue or PR was opened.

The patch changes two executable lines. Let `T=tn.u`, `L=tl.u`,
`gap=(T-L) mod 2^64`. For `0<=T,L<2^63`, the LP64 signed difference
`L-T` is representable. If `L<=T`, `-2<=L-T<=0` is equivalent to
`gap<=2`; if `L>T`, both small-distance tests are false, while the shared
unsigned-shift test is true (`gap>>52>=2048`). Thus the complete predicates
are equivalent on this domain. The shift result is at most 4095.

`L` has its sign bit cleared. The required range for `T` follows if the biased
exponent of `ph` is at least 53: the source computes
`T=(exponent_bits)-(53<<52)`. This precondition is consistent with the
refinement caller's normal finite range but is not newly proved for every input
by the corpus tests. The replacement's unsigned operations are defined even
outside that precondition; equivalence to the old signed code is the conditional
claim above. No whole-function absence-of-UB claim is made.

With 32-bit `long` and modulo conversion, `T` converts to zero because its low
52 bits are zero. The old signed subtraction then cannot overflow, and its
small-distance test accepts low32(L) in {0, -1, -2}. It contains all intended
small-gap cases but can include additional cases. This is implementation-defined
conversion, not by itself undefined behavior. An extra database lookup returns
the original result on a miss; on a hit, correctness depends on the database
entry. We do not call every extra lookup harmless without that qualification.

The unsigned predicate removes those casts and `long`-width dependencies.
The retained legacy witness comment `dn=-2` corresponds to `gap=2`; the
`de=48` comment corresponds to `gap>>52=48`.

Both GCC 13.3 and Clang 18.1.3 pass all 249,134 corpus rows, both signs and all
four modes, with errno enabled and contraction off, on Linux x86-64. The original
source passes the same corpus under undefined-behavior/float-cast-overflow
sanitizers; each sanitizer rejects a deliberately overflowing control.
[23,923 synthetic encoding-pair checks](../../weekly/2026-10-26/asin-predicate.json)
are sanity checks for the algebra, not reachable `cr_asin` witnesses or a Windows
qualification. Windows/32-bit builds and a complete independent derivation of
all `phi/ph` range preconditions remain open. The index cast is safe if the
rounded `abs(phi)*0x1.45f306dc9c883p+4` is in [0,32]; testing does not prove that
precondition over the full domain.

The candidate is for optional maintainer pickup. Recheck the exact base and
adoption state before applying it to a later revision.
