# Binary64 sine follow-up — October 8, 2026

**Scope: the revised sine implementation and October 8 proof, plus pickup of
the asinpi coverage witness.** One source build regression is confirmed:
the errno-enabled tiny branch uses an undeclared variable. A one-word candidate
is supplied. The threshold change is consistently reflected in the algorithms;
the review also checks the newly routed hard cases, supplies proof-model corrections,
and a source-bound proof that the old missing sine arc is unreachable.
The subsequent upstream removal of that arm is now checked too: with the local
errno fix, the latest sine has 177/177 lines and 42/42 arcs in the four-mode GCC
union. No numerical mismatch was observed. The accepted asinpi witness also
closes its measured gap (258/258 lines, 76/76 arcs).

PDF-cited implementation: `84674bfadb0f920614355024c87a3eef73f2d938`.
Latest sine check: `74fcd1094a316164c94481f40f5c9658439bee63`, with only
the supplied errno fix in the tested candidate.
Proof sources: `57f6899abefaaf768d6a84e2bbc24944dcb650f2`.
This is an ad hoc follow-up to specific requests, not a new 25-function census
or a replacement for the scheduled Sunday review.

## Actionable changes

1. **Build fix — `sin-errno-name-latest.patch`** for the latest pin
   (`sin-errno-name.patch` for the PDF-cited pin). In the tiny branch of `cr_sin`,
   `ax` is undeclared; the renamed absolute-bit variable is `au`. GCC and Clang
   both reject the original with `CORE_MATH_SUPPORT_ERRNO`. The patch changes
   only `ax` to `au`; the subnormal/underflow predicate then has the intended
   meaning. The undeclared name remains present at the latest pin. This is a source regression, not a compiler defect.
2. **Newly routed hard cases — no corpus addition needed.** Reducing the
   tiny cutoff routes inputs just below the old x0 into AccurateSmall. The
   first cluster in the corpus begins at x0, but a later section contains
   the cases below it. Exact Taylor bounds isolate eight inputs within 2^-49 ulp of a midpoint;
   all eight are present after comparing numeric values, including equivalent
   hexadecimal spellings with omitted trailing zeros. The supplied certificate
   and boundary checks make this part of the argument explicit. No new
   wrong-value witness or missing corpus row is reported.
3. **Accurate proof model — `acclarge-reference.patch`.** Change
   `S5=c5-c7*u2` to use `U2`, `C6=v6-v8*u2` to use `U2`, and `T5=c4*U4` to
   use `C4`. The capitalized expressions should describe the ideal polynomial.
   The corrected model includes the previously hidden propagated error.
4. **Small-model hypotheses — verified; no patch needed.** Both magnitude
   preconditions and the final goal are checked separately for each sign/mode.
   Additional range goals connect the original eps2/H2 hypothesis to the
   FastTwoSum theorem; eps5/s5 follows directly from its exact-sum statement.
   An initially proposed model rewrite was unnecessary and is not a finding.
5. **Conversion/coverage lemma — [mathematical note](MATH-NOTE.md).** Describe
   `u128_tod` as the rounding proxy it implements, with its hard-case
   precondition. The generic claim that it rounds any nonzero 128-bit value
   is too broad. The supplied range proof explains why its high-word-zero arm
   is unreachable through the pinned public sine implementation.

## What changed since the earlier review

The tiny threshold and equality direction now match the code and small-path
domain. The restored reciprocal word `_T[19]`, moderate endpoint operation
order, signed large-path residual domain, factor of 2*pi, explicit polynomial
approximation errors, cosine's non-strict bound at zero, and the near-pi
enumeration's corrected index/exponent description address the corresponding
earlier concerns. Those are recorded as resolved revisions, not new findings.

The remaining reference-expression corrections above matter for a faithful
proof model. Stale C comments about the old threshold, reducer index range and
helper conversion contract should also be aligned with the implementation.

## Why the missing sine arc is not another test input

The only missing helper arc takes the `h==0` alternative in the high-word
test. The exact continued-fraction certificate bounds the distance of every
eligible binary64 input from every multiple of pi/2. The separate reducer,
polynomial, directed table and Gappa certificates connect this to the integer
passed to the helper. The resulting bound is `J>2^67`, so `J>>64>=8` and
`sh<=60`. It simultaneously rules out final addition wrap and invalid shift
counts in this caller context. At the PDF-cited pin, raw coverage is 43/44
arcs with errno enabled; its one missing arm is classified mathematically.
Upstream commit `f547a26dbe5c3351427e78c82e4fd13c244b81d8` then removed
that arm. A complete executable sin.c comparison confirms this is the only
functional sine change through `74fcd1094a316164c94481f40f5c9658439bee63`
(apart from the same local errno fix). Thus the same lower bound validates
the new direct clz operation. Fresh full-corpus runs measure 42/42 arcs and
177/177 lines in the four-mode union on the latest candidate.

The bound uses 1,024 exponent certificates and an independent replay with a
different pi identity. All 1,040 accurate-reducer exponent/table windows are
checked, with a tail bound over all mantissas. See the mathematical note for
the assumptions and exact inequalities; no random sampling is used to infer
unreachability.

## Verification and limits

All entries below pass all four rounding modes. Coverage is the union of
separate O0 instrumented runs; ordinary regression builds are O3. Both signs
are exercised by the upstream checker.

| Source / configuration | Corpus rows | Lines | Arcs |
|---|---:|---:|---:|
| PDF pin, original sine, GCC x86-64, errno off | 1,975,927 | 174/174 | 37/38 |
| PDF pin, errno candidate, GCC x86-64 | 1,975,927 | 178/178 | 43/44 |
| PDF pin, errno candidate, Clang x86-64 | 1,975,927 | not measured | not measured |
| Latest pin, errno candidate, GCC x86-64 | 1,975,927 | 177/177 | 42/42 |
| Updated asinpi corpus, PDF pin, GCC x86-64, errno on | 58,412 | 258/258 | 76/76 |

Each full sine checker execution processes 3,951,854 tests including signs;
repeated builds and modes are not unique inputs. A separate 109,638-row
boundary corpus passes GCC x86-64-v3 and Clang x86-64 checks at the PDF pin.
Both compilers also pass all four modes with contraction enabled on x86-64-v3.
The latest pin has a fresh GCC corpus/coverage replay; Clang and FMA numerical
replays above remain explicitly tied to the earlier pin. Both compilers reject
the unmodified errno-enabled source at both pins.

The result manifests give exact corpus sizes, flags, compiler versions, source
and corpus hashes, mode results and coverage. All CORE-MATH builds use
`-frounding-math`. Corpus runs use the unchanged upstream MPFR checker,
including both signs and its supported exception/errno checks. Targeted tests
cover the new cutoff, old cutoff, small/large boundaries, normal/subnormal
boundary, tiny powers of two and a dense sample of the newly routed interval.
The exact interval argument additionally verifies that the entire potentially
difficult suffix is in the tested corpus.

Proof checks use Gappa 1.8.2. Polynomial bounds use exact rational
Taylor/Bernstein arithmetic; table checks use directed MPFR enclosures.
Each commented accurate-path goal is made executable separately, including
intermediate range/no-wrap goals. Generated inputs and raw logs are retained.

This review does not regenerate the historical full-domain hard-case searches.
Their completeness remains a separate dependency of a universal correct-rounding
proof. Passing the corpus, explaining a missing arc and proving the new interval
do not silently certify that dependency. No new full-repository health claim,
ARM result or untested-platform claim is made.

## Review and acknowledgement

Claude Opus 5.5 provided independent planning, adversarial technical and
mathematical reviews. Its assertions were checked against the code, exact
certificates, primary theorem statements and tool results; corrections to the
reviewer's interpretations are recorded. The final assembled report, response and closure evidence were independently
reviewed by Opus 5.5, which found no substantive blockers. Its advisory review
did not execute tests; the orchestrator verified the recorded results. Final
clarity and receipt checks are recorded in REVIEW-DISPOSITION.md.

For acknowledgement, the accurately recorded tools are OpenAI Codex and
Anthropic Claude Opus 5.5. A suitable wording is “Eric Hennenhoefer, assisted by
OpenAI Codex and Anthropic Claude Opus 5.5.” The precise historical OpenAI model
version is not asserted because it was not reliably recorded in this audit.

## Next scheduled review

The Sunday review will select the next coverage target from the updated census
and inspect new changes and correspondence first. The intervening exp change
`a37b7ae5ec10200a56533ca797aa64a73c8e07e0` is queued, not reviewed here.
The October 6 all-25 baseline retains its original revision; this sine follow-up
does not advance that repository-wide baseline.
