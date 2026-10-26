# Three priorities, with evidence and follow-through

**Goal: make the library easier to trust and maintain by delivering small,
independently checked fixes, regression inputs and proof obligations that the
team can act on.** Passing tests alone is useful maintenance, but it is not the
whole weekly output. A review should also say what improvement comes next and
what would count as finishing it.

[Independent strategy/design review and dispositions](docs/IMPROVEMENT-REVIEW.md).

## Close the loop on earlier proposals

At implementation `0ce0cbc15935e24c656280e5a46c34e89f301b7a`, **two of the three
October 18 patch proposals are adopted**. No upstream PRs were opened by this
workbench.

| Proposal | Current disposition | Evidence |
|---|---|---|
| rsqrt high-binade underflow fix | Adopted; witness added; fresh old/new checks pass | [upstream commit](https://gitlab.inria.fr/core-math/core-math/-/commit/304b681add2ad392274005b5f423a1609afcd4c6), [verification](weekly/2026-10-25/REPORT.md) |
| exp fast-path allowance | Adopted; witness added; fresh old/new checks pass | [upstream commit](https://gitlab.inria.fr/core-math/core-math/-/commit/84fef47b7c7759ef389d370cb1f20d645062f7b4), [verification](weekly/2026-10-25/REPORT.md) |
| exp directed FastTwoSum proof model | Open, unadopted at proof `3ec3c827eb3b0c4849ad2f47da20ec68dadf8482`; conditional bounds only | [candidate and limits](candidates/exp-fasttwosum-model/README.md), [current reconciliation](weekly/2026-10-25/SOURCE-REVIEW.json) |

Refresh this disposition against the exact implementation/proof branch before
calling an item open, adopted, superseded or withdrawn. Do not keep applying an
old patch after its source has changed. Adoption describes matching source and
tests, not a claim about who originated a change.

## Current ranked improvement proposals

| Rank | Improvement and why it matters | Next concrete deliverable | Completion criterion / present limit |
|---|---|---|---|
| 1 | **Bind a changed proof to the code it describes.** Passing corpus tests cannot establish that a proof models the executed operations. | A small exp proof-to-`exp_proof` source map, one checked directed-rounding obligation, and a disposition for the existing model candidate. | A checked correspondence/certificate under explicit hypotheses, a reviewed minimal correction, or a precisely isolated unresolved premise. Full exp correctness is not promised. Sine follows only after checking source stability and choosing one obligation. |
| 2 | **Resolve asin cast and integer-range portability.** Its current Clang corpus pass does not settle signed arithmetic or 32-bit `long` behavior. | A source-range analysis of the changed casts/subtraction, supported by bounded LP64 and, if available, LLP64 checks and negative controls. | Either a minimized reachable failure with a tested remedy, or a justified defined-behavior/equivalence argument for the stated domain/ABI. Tests alone cannot prove absence of UB. Unsupported ABI execution remains explicitly untested. |
| 3 | **Turn bivariate hard cases into reusable, independently checkable regressions.** Two-input functions add a much larger input space than the unary suite. | The [restricted verifier and Linux adapter are qualified](docs/HYPOT-QUALIFICATION.md). Next: one bounded candidate-construction task and pinned-corpus deduplication; import prior archives when available. | Qualification covers 18 fixtures, four modes, GCC/Clang and specific negative controls. Values/flags/errno remain separate. This is not a search, imported-result validation or completeness census. |

The [machine-readable queue](config/improvements.json) owns status, next action,
budget and checkpoint. These are three real proposals, **not a quota of three
new bugs or patches every week**. Reprioritize when evidence or upstream changes
justify it. Replace closed cards with the next eligible task. If fewer than three
are useful, say so; never fill a slot with an invented finding.

## Weekly acceptance and limits

- Lead with scoped health and material adoption changes; keep failure values,
  compiler bugs, source UB and proof gaps distinct.
- Show three ranked improvement slots, each with a status, this week's change
  and next deliverable. An unchanged item gets one short line and a link, not a
  repeated request to maintainers. Planned work is not a tested patch.
- Aim for at least one substantive, evidence-backed improvement: a reproduced
  witness, checked certificate, resolved obligation, qualified component or
  adopted fix. A precise new blocker can be useful, but rediscovering the same
  missing dependency or changing a status label is not progress. Report a quiet
  week honestly.
- Default budget: **four CPU-hours and two wall-hours total per weekly science
  run**, including acquisition/build/review-support execution. Pick one primary
  review card and at most one bounded bivariate task, run serially under existing
  locks. Individual cards are capped more tightly; reserve budget for failures.
  Record measured child CPU and conservative overhead, and never silently raise
  limits. External model inference is recorded separately where available.
- Coverage remains parked under current scope. No new census or arc backlog is
  required to fill an improvement slot. Keep dated historical evidence intact.
- Stop/reassess a card when its selected source changes, a prerequisite fails,
  a negative control fails, or its cap is reached. Preserve partial evidence;
  source refresh is not permission to skip unreviewed changes.

## Bivariate expansion and team use

Hypot goes first because, in a restricted normal positive domain, exact integer
comparisons can decide its rounding without trusting the candidate generator.
The [specification](docs/HYPOT-CERTIFICATE-SPEC.md) and [implemented verifier with
Linux qualification](docs/HYPOT-QUALIFICATION.md) are available now. The listed
fixtures qualify the setup; they do not prove a complete family or discover new
hard cases.

When available, import angular and pow certificates and refresh corpus
membership at the selected pin. Compare atan2/atan2pi stage behavior with the full
pinned corpus before claiming added stage coverage. Preserve mixed/negative
search results and choose a different pow hypothesis instead of enlarging an
unchanged search. Until source archives are received and checked, their reported
results remain unverified by this workbench and are not used as evidence.

Any team member or AI can select a queue ID, read the linked acceptance criterion,
run a bounded task, and contribute its verifier, witness or candidate plus a
receipt. New platforms need their own qualification; historical Windows runs
do not qualify Linux, macOS or another compiler. Keep the 25-function unary
population separate. Publishing here never implies an upstream merge.
