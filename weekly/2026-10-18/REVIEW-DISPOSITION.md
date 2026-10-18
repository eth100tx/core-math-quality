# Independent review and dispositions

The actual Claude CLI model `claude-opus-5-5` provided independent planning,
technical and final adversarial reviews. Model-usage metadata was checked for
each invocation. A separate final addendum reviews the tightened public
reproduction guard. Reviewers are advisory; the orchestrator independently
checked the load-bearing arithmetic, witnesses, source bindings and receipts.

## Accepted and independently verified

- The changed rsqrt range condition can create a subnormal reciprocal and
  spurious underflow. Unchanged-binary upstream-checker replay, a previous-source
  control, an independent MPFR probe and the candidate matrix confirm this.
- The exp fast allowance still differs from the manuscript. The replay confirms
  the historical F01 witness; previous audit material and the manuscript establish
  that this is a recheck, not a newly discovered wrong-value input.
- Directed rounding invalidates the generator's sign placement. C/MPFR helper
  counterexamples confirm the difference. Correcting expression and hint yields
  four conditional Gappa certificates. Directed error bounds become slightly
  weaker, although still strictly within the manuscript's stated bound.
- Exact coefficient arithmetic, outward table and endpoint enclosures, and
  arithmetic comparisons support the specifically labelled proof steps. The
  remaining domain, exactness, contraction and historical completeness premises
  are explicit in the source review.
- The finite exp10 trigger/residue argument is valid for the two measured
  binaries. It does not establish a portable caller certificate.
- The hypot proposal's positive-domain integer oracle and resource bounds are
  coherent. It remains a proposal requiring a separate reviewed runner/schema.

## Corrections made before publication

The final review found no mathematical blocker in the submitted claims, but
required four presentation/reproduction corrections: name round-toward-zero as
the failing mode and state the result is one ulp too large; actually supply the
promised attachments; distinguish the primary x86-64 baseline from the v3
instrumented supplementary build; and avoid accepting arbitrary upstream-exp
failures as expected. The public adapter now rejects every unexpected failure
or incomplete checker sequence. All 14 saved cells are accepted, including the
two exact documented failure cells; eight adversarial mutations are rejected
([guard validation](GUARD-VALIDATION.json)). Original measured receipts were
not altered. Final local receipt QA independently checks the same restriction.
The addendum required rejecting missing count expectations and saving failed
special-build receipts before an explicit exception; both are implemented.

The report now also states the changed directed-mode bounds, observed rsqrt
minimum gap by mode, unmeasured performance cost of the larger exp allowance,
and why absent witness rows can coexist with a passing corpus. No performance
improvement or universal fix is claimed. The sender signature follows the
owner's explicit requested wording and names the owner on whose behalf it is sent.

## Rejected or deferred suggestions

An inferred universal rsqrt correction gap of at least 52 was not accepted:
instrumentation observes 51 in directed modes. This does not itself establish a
wrong-value failure or justify changing the refinement predicate. An open-ended
or exhaustive binary32/bivariate search was not dispatched. Original model
success is not a reason to skip source/model alignment. The full exp theorem,
historical complete hard-case searches, unsupported platforms and outside-25
changes remain unverified where explicitly listed.

The initial forced-accurate wrapper mishandled NaN comparisons; bit classification
fixed the harness and the entire cell was rerun. An initial local table-driver
compile omitted math.h and was repaired. A first proof-model repair retained an
unhelpful old hint; the published candidate includes the matching exact hint.
These are local preparation failures, not upstream numerical findings. They and
their CPU are retained in the private operational record. Only useful verified
public evidence is included here, with these limitations disclosed.
