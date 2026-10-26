# Test plan and reporting priorities

## Every review

- Inventory implementation and proof changes since the last completed baseline.
  Triage every file: tested, source-reviewed, deferred, outside focus.
- Qualify the machine; pin toolchain, source, checker, corpora and exact flags.
- Run the complete `.wc` files for changed priority functions and, only when
  enabled, the active coverage target in four modes. Include shared dependencies.
- Run uninstrumented regression; add GCC coverage only when in scope. Compare raw gaps only where
  identities match. When coverage is enabled, refresh the full 25-function census when the source/profile/
  corpus changes enough to invalidate the ranking; otherwise retain dated results
  and mark freshness explicitly. Do not relabel old results as this week's run.
- Review changes that affect proofs separately; a passing test cannot close a
  proof obligation. Record limitations and avoid recycling unchanged allegations.
- Reconcile earlier patch/witness adoption. Maintain the three ranked proposals
  in `config/improvements.json`, with status, progress and next artifact. Select
  one primary task plus at most one bounded bivariate task within its envelope.
  Do not require three new findings; say when there are fewer eligible items.

## Widen when the change warrants it

| Trigger | Additional investigation |
|---|---|
| Rounding threshold/reduction/polynomial change | Neighboring representable values, all modes, fresh MPFR oracle |
| Exact/subnormal/overflow changes | Flags/errno and transition boundaries; upstream special checker |
| Compiler or architecture dependence | Second compiler, v3 vs baseline, contraction setting; minimize reproducer |
| New witness | Full old+new corpus; prove `.wc` row is accepted; independent reproduction |
| Suspected undefined behavior | Targeted sanitizer build, minimized case; do not conflate with compiler defect |
| Uncovered branch | Targeted witness search or explicit unreachability argument with preconditions |
| New platform | Doctor + positive/negative controls + full selected replay before qualification |

These investigations require explicit commands, bounded budgets and separate
receipts. The shipped runner automates corpus replay and coverage, not all possible
boundary generators, sanitizer campaigns or formal proofs. Expand by adding tested
adapters and profiles instead of silently changing the baseline semantics.

## Findings

Prioritize wrong rounded values, then flags/errno/UB and confirmed compiler issues,
then useful coverage improvements and proof-status changes. Severity and evidence
strength are separate. Only confirmed findings enter the lead; candidates remain
labeled candidates. Include actual/expected hexadecimal values and rounding mode.
Preserve upstream `.wc` syntax: rounding mode and expected value belong in metadata
unless that corpus explicitly includes them.

No regression observed means only the named checks passed. It never means
repository-wide absence of bugs or mathematical correct-rounding proof.
