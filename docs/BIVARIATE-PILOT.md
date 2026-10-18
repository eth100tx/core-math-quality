# A bounded bivariate hard-to-round pilot

**Proposal, October 18, 2026. No bivariate search has been run under this plan.**
Keep this research separate from the reproducible 25-function unary weekly
regression and its single coverage target. Report only independently verified
new witnesses or a useful measured feasibility result, not a stream of near misses.

## First target: hypot

Start with positive finite binary64 inputs in [1,2), restricting the first pilot
to outputs in [2,4). This deliberately excludes signs, exceptional values,
subnormal results and overflow; those require separate validation. It offers a
small domain with a simple independent oracle: after an exact common power-of-two
scaling, x²+y² is an integer. Compare it with the exact square of each relevant
representable output or midpoint. Squaring is order-preserving here, so these
integer comparisons decide directed rounding and nearest rounding, including
ties. A high-precision floating-point evaluation alone is not the certificate.

Proposed first experiment:

1. Review the pinned upstream hypot source, checker, corpus and existing search
   references. Deduplicate against the corpus numerically, including symmetric
   input pairs. Characterize exact results and midpoint cases before counting
   them as difficult inexact cases.
2. Choose a reproducible grid of at most 4,096 x values and 16 output midpoints
   per x. Derive y candidates around sqrt(m²−x²) using outward intervals, then
   inspect the two enclosing binary64 y values. Reject candidates outside the
   stated pilot domain. This is a heuristic construction, not an exhaustive search.
3. Rank candidates by their certified distance from a rounding boundary in
   output ulps. Keep at most 128 distinct pairs. Record exact residual integers,
   scale exponents and boundary encodings so another implementation can verify
   the ranking without trusting the search program.
4. Compare the retained pairs with unmodified CORE-MATH in all four rounding
   modes, checking values, flags and errno. Independently review any mismatch;
   require a second compiler/configuration and an exact integer oracle before
   publishing a defect. Keep difficult-but-correct inputs distinct from failures.
5. Stop at two wall hours or four CPU hours, whichever comes first; at most
   131,072 constructed pairs. Checkpoint by x-grid slice. Report candidate count,
   best certified distance, corpus novelty, elapsed CPU, and whether extending
   the method appears worthwhile. No automatic budget escalation.

Simultaneous exact power-of-two scaling and exchanging the two arguments can
extend useful hypot tests. Such transformations are accepted only after checking
input representability and the output's rounding regime; they do not justify
carrying an ordinary-range rounding result through underflow or overflow.

## Follow-on choices

| Function | Bounded construction worth assessing | Required caution |
|---|---|---|
| atan2 | Positive rational slopes near selected angular rounding boundaries; then separately check signs/quadrants | Equal real ratios share an angle, but binary64 pairs do not collapse into a complete binary64 unary domain. Preserve the exact input pair. |
| atan2pi | Similar slope construction using scaled-angle boundaries | Certify the scaled angle with outward intervals; do not round atan2 first and then divide that rounded value by pi. |
| pow | Fixed finite exponent slices and bases near selected result boundaries | Classify exact identities and domain/special cases first; a finite set of exponent slices says nothing about the full two-input space. |

For transcendental candidates, use adaptive outward interval evaluation until
the interval isolates the required rounding decision, with an explicit precision
and time limit. Unresolved candidates remain unresolved; they are not failures.
Review the upstream bibliography before making novelty claims about a method.

## Evidence and integration

Each run needs a manifest with implementation/checker pins, generator hash,
domain and selection rules, deterministic seed if used, compiler flags,
precision policy, resource cap, per-slice checkpoint and CPU accounting. Candidate
rows must be copyable in upstream's actual two-argument corpus format. Include a
standalone exact/interval verifier and distinguish new corpus rows from already
present inputs. Use the existing qualification, single-runner and review rules.

Do not silently add these functions to `config/targets.json`: the unary checker
interface and coverage rankings must remain comparable. A bivariate runner needs
its own reviewed input schema, qualification controls and result schema before
the experiment. Publish any reviewed candidates under `candidates/`; summarize
only substantive results in the weekly report.
