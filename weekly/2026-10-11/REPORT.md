# Week ending October 11, 2026

**Health: all 25 selected binary64 functions pass the refreshed GCC regression;
three small source/proof corrections are proposed, with proof limits still explicit.**

- **Correct rounding / .wc:** no new failure in the checked inputs; no new wrong-value witness.
- **Compiler / patches:** no new compiler build failure in the checked configurations.
  The earlier sine errno fix and all three model corrections are upstream, verified
  against the October8 candidate bytes. New candidates: [log2 sign adjustment](../../candidates/log2-sign-step/README.md),
  [sinh integer width](../../candidates/sinh-mask-width/README.md), and
  [exp proof derivative bound](../../candidates/exp-derivative-bound/README.md).
- **Coverage target: exp**, selected from the complete comparable census:
  **0 missing lines, 1 missing arc** (134/134 lines, 39/40 arcs).
  All 51 database keys are checked in four modes. Portable unreachability
  remains **deferred**, not proved by passing tests or compiler optimization.

## Evidence and scope

Authoritative implementation `81a899d67953a619d703660fd9630f0554673524`; proof
`58df57e5a46310d0e47d140ad23f146461788e0e`. Cutoff 2026-10-11 13:02 UTC.
Workbench runner `64f4b38c7267b389c0ede64ae9e6b1aa968ed7f8e80063c9b523d8b23cbfa566`; reviewed workbench
base `c28f35a63573563e0199e1dfe1dfcfdec0e44d82` had no intervening runner changes.
After measurement, nested self-tests exposed a workbench process-control bug:
children inherited the parent's temporary SIGTERM/SIGINT spawn guard. The
runner now restores the caller's original mask in the child, preserving
intentionally blocked signals. The new regression fails on the old code both
directly and nested; all 15 tests pass directly after the fix. All 15 tests also pass nested; patch application, arithmetic replay,
receipt hashes and privacy checks pass ([validation](VALIDATION.json)). Original numerical receipts retain their original
runner identity; no completed numerical result is reattributed to the fix.
[Every changed path and deferred scope](REVIEW-INVENTORY.json),
[source/proof reasoning](SOURCE-REVIEW.md).

The baseline uses GCC13.3/gcov13.3, Linux x86-64, errno enabled, O3 regression
and separate O0 coverage, all four rounding modes, complete pinned `.wc`
files and upstream checker built-ins. Both signs are used where the upstream
header requests them. `-frounding-math`, `-ffp-contract=off`,
`-fno-finite-math-only` and `-march=x86-64` are explicit.
This is not the unbounded `check_special` campaign.

[Full baseline receipt](runs/20261011-baseline-gcc-e1/result.json), with exact flags, accepted
counts, source/corpus/checker hashes and per-mode raw counters.
[Supplementary receipts and observations](SUPPLEMENT.json) distinguish full
corpus checks, literal/boundary inputs, shift sanitization, candidate builds
and sine's additional finite-math compilation. GCC and Clang18 are covered in
the listed cells only. No new v3, ARM, macOS or Windows-native qualification
is claimed. The unchanged historical search campaigns were not rerun.

## Comparable coverage census

17/25 functions have no missing target-file lines or arcs in this
specific four-mode union. Coverage improvements this week largely follow
upstream deletion of redundant predicates; they are **not** new test coverage
of those deleted paths. New sinpi/cospi integer inputs are separately reflected
in the pinned corpus hashes. Sine is now 177/177 lines and 42/42 arcs on
unmodified upstream source; asinpi is 258/258 and 76/76.

| Function | Lines hit/total | Arcs hit/total | Missing lines/arcs |
|---|---:|---:|---:|
| acos | 124/124 | 34/34 | 0/0 |
| acosh | 181/181 | 46/46 | 0/0 |
| acospi | 148/148 | 62/62 | 0/0 |
| asin | 108/108 | 34/34 | 0/0 |
| asinh | 177/177 | 50/50 | 0/0 |
| asinpi | 258/258 | 76/76 | 0/0 |
| atan | 100/100 | 40/40 | 0/0 |
| atanh | 159/159 | 36/36 | 0/0 |
| atanpi | 152/152 | 58/58 | 0/0 |
| cos | 372/431 | 100/151 | 59/51 |
| cosh | 153/153 | 42/42 | 0/0 |
| cospi | 149/149 | 46/48 | 0/2 |
| exp | 134/134 | 39/40 | 0/1 |
| exp10 | 135/135 | 51/52 | 0/1 |
| exp2 | 130/130 | 53/54 | 0/1 |
| log | 117/117 | 30/30 | 0/0 |
| log10 | 129/129 | 28/28 | 0/0 |
| log2 | 96/96 | 22/22 | 0/0 |
| rsqrt | 71/71 | 36/36 | 0/0 |
| sin | 177/177 | 42/42 | 0/0 |
| sinh | 168/168 | 42/42 | 0/0 |
| sinpi | 180/180 | 50/52 | 0/2 |
| tan | 415/474 | 112/163 | 59/51 |
| tanh | 153/153 | 40/40 | 0/0 |
| tanpi | 190/194 | 67/70 | 4/3 |


[All raw missing line numbers and arc identities](MISSING-COVERAGE.json).
These are target `.c` metrics; header/helper coverage is not silently combined.

## Active target: exp's remaining loop-exit arc

The missing arc is `as_exp_database`, line217, branch1: exhausting the
three-neighbor loop. The match requires a literal database key. The finite
necessary trigger set has 51 unique sorted encodings. A dedicated replay
checks every key under RN/RZ/RU/RD with GCC O0/O3 and Clang O3, counting
entries and trapping exhaustion. The analogous exp2/exp10 sets (43/49 keys)
were checked to review the same source change, not selected as additional
coverage targets. No exhaustion was observed.

The nonmatching search strictly shrinks its interval. Successful optimized
returns alone cannot prove source unreachability, and C instrumentation can
change code generation. We therefore also observed the actual helper arguments
in byte-identical copies of the baseline O3 and O0/gcov binaries, at debugger
breakpoints, for every key and mode. Every captured argument satisfies the
required residue condition; both binaries' argument sets agree. This is
binary-specific finite-reduction evidence, with rounding control and FTZ/DAZ
recorded. [Production capture](production-capture/receipt.json),
[coverage-binary capture](coverage-capture/receipt.json),
[offline verifier](verify_exp_capture.py), and [source argument](SOURCE-REVIEW.md).
The raw 0/1 gap remains. Portable arithmetic closure is deliberately deferred;
the next useful action is a caller-bound certificate independent of these
binaries. No fabricated `.wc` row is added.
exp, exp2 and exp10 tie at 0 missing lines/1 missing arc; the documented
missing-lines, missing-arcs, then alphabetical ranking selects exp.
The exp2/exp10 replays only review the shared source change.

## Source and proof corrections

The log2 expression computes +1/+3 instead of the earlier +1/−1 when signs
differ. The code comments claim only same signs are reachable. The candidate
restores unconditional source equivalence; no public wrong-value witness is
established. The sinh candidate restores a 52-bit mask to an `int64_t` variable,
avoiding narrowing-induced database calls. Full-corpus candidate passes are
finite regression evidence, not universal correctness proofs.

In exp's proof, Q'(0)=1 contradicts the displayed bound 2^-0.99. An exact
rational coefficient calculation gives |Q'|<1.0001 on the required interval.
The corrected term is <2^-116.47, and the final sum still fits 2^-100.29.
This error predates the latest edit; it was identified during this review.
[Arithmetic certificate and replay](exp-proof/receipt.json),
[proof-text patch](../../candidates/exp-derivative-bound/fix.patch).
Eight bounded Gappa goals cover four modes, with/without contraction of dxll;
the manual exactness/lattice argument and excluded cross-statement contraction
are recorded separately. The full accurate-path theorem is not certified:
its `th==1` path, subnormal FIXME and historical search dependencies remain.

## Reproduce, review and handoff

Follow [RUNBOOK](../../RUNBOOK.md) for host qualification and source acquisition.
Run `quality.py run` at the pin above with all25, primary GCC profile, errno1,
four modes and a fresh run ID. Then run
`python3 weekly/2026-10-11/reproduce_focus.py` under a two-hour outer timeout.
It uses the verified cache, per-child ten-minute limits and the shared runner
lock, and writes only under `.work/20261011-supplement`.
For the debugger replay, first produce baseline run ID `20261011-baseline-gcc-e1` as above,
then run `capture_exp.py plain` and `capture_exp.py covered` from this report
directory under a 15-minute outer timeout. GDB and binutils are required.
The capture scripts use the same lock and redirect gcov counters away from
the baseline. `verify_exp_capture.py PATH_TO_PINNED_EXP_C` checks the published
finite-key observations and O0/O3 agreement independently.
Replay the eight `exp-proof/*.g` goals with Gappa1.8.2; each has a concrete bound.
`verify_exp_arithmetic.py PATH_TO_PINNED_EXP_C` independently checks the source
hash, exact derivative inequality and high-precision corrected sum.

Actual Claude Opus5.5 independently reviewed planning, mathematical/source
reasoning and the final artifacts. [Review disposition](REVIEW-DISPOSITION.md).
Tests, source proofs, proposed corrections and upstream adoption are kept
separate. Outside-25 changes (including pow and other precisions) are inventoried
but deferred. Implementation CI was observed successful; proof CI was
unavailable (HTTP403). Public correspondence and machine identities are omitted.

Baseline child CPU: 1101.861s;
supplement cell child CPU: 339.588s;
Gappa child CPU: 1.144s;
debugger capture child CPU: 6.711s. Acquisition, review clients,
monitoring and publication are accounted separately in the private ledger.
