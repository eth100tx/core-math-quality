# CORE-MATH weekly review — October 18, 2026

**All 25 pinned corpora pass; supplementary tests expose a new rsqrt flag
regression and the still-outstanding, previously reported exp value failure.**

- **Failures:** rsqrt row `0x1.0000000000001p+1022` raises spurious underflow
  in all four modes. Historical exp row `0x1.5a3a157335f3bp+9` fails under round-toward-zero only
  (RN/RU/RD pass), with contraction off, returning one ulp too large: actual `0x1.ffdebdc4e28acp+998`, correct
  `0x1.ffdebdc4e28abp+998`. Both rows are absent from the pinned corpora;
  unchanged baseline binaries reproduce them. [Witness evidence](witness-replay/receipt.json).
- **Patches and proof:** no compiler miscompilation was confirmed. Two small
  source candidates pass focused GCC/Clang checks; a directed-rounding correction
  to the exp proof generator preserves its four conditional error certificates.
  [Candidates](../../candidates/README.md). These are tested/proposed changes,
  not merged fixes or a full correctness proof. Last week's log2 and sinh source
  corrections and exp derivative bound are now upstream.
- **Coverage:** exp's replacement database is fully covered (117/117 lines,
  32/32 arcs); 19/25 target files have no measured gap. The single next target is
  **exp10**, zero missing lines/one missing arc: `["as_exp10_database",180,1]`.
  All 49 necessary trigger keys exclude that exit in the measured O3/O0 binaries;
  portable closure remains open. [Action and evidence](COVERAGE-TARGET.md).

## Scope and revisions

Cutoff 2026-10-18T13:02:58Z. Implementation
`dae5dd8c0d5bd2691b45de28c9edbe12f067c3d3`, compared with
`81a899d67953a619d703660fd9630f0554673524`.
Proof `5a42d3fb72533077c8b745b9fcd39b84ad3ee92a`, compared with
`58df57e5a46310d0e47d140ad23f146461788e0e`.
[Inventory](REVIEW-INVENTORY.json): 87 implementation paths and 7 proof paths,
with explicit reviewed/deferred dispositions. Changes outside the selected 25
binary64 functions/shared dependencies are inventoried, not certified. ARM,
Arithmos and other platforms are outside this run.

The complete primary census uses GCC 13.3/gcov 13.3, Linux x86-64, errno on,
four modes, O3 regression and O0 coverage, `-frounding-math`, contraction off.
The [receipt](runs/20261018-baseline-gcc-e1/result.json) records compiler,
MPFR/GMP, flags, exact accepted counts, sources/checker hashes and raw coverage.
The runner is unchanged from October 11. The corpus passes are consistent with the
supplementary findings: neither witness row is present numerically
([presence check](WITNESS-PRESENCE.json)).

## Targeted checks and their limits

[Fourteen supplementary cells](SUPPLEMENT.json) cover rsqrt/exp with GCC 13.3
and Clang 18, x86-64-v3, contraction off and enabled (GCC `fast`, Clang `on`).
Within each compiler, assembly counts verify additional fused instructions;
the counts are not comparable across compilers. No fast-math was used.

Both candidates pass their full pinned corpus and every generated extra row:
206,169 positive rsqrt inputs (also tested with negative sign by its checker),
and 2,335 exp inputs covering old/new database keys, proof examples, hard cases
and boundary neighbors. The current exp source fails the historical witness
in GCC/Clang contraction-off builds; the failed checker runs stop there, so
unvisited extra-input suffixes are not certified. Contraction-enabled builds
pass this finite set. This difference is not evidence of a compiler bug.

A separate wrapper forces exp's accurate path over its actual finite caller
domain, including the gap between 2^-54 and 2^-53, preserving the caller's errno
handling. It passes the full corpus and extras in the GCC 13.3 x86-64-v3 contraction-off supplementary build.
This is explicitly instrumented testing, not an unchanged public call.
An initial wrapper compared quiet NaNs before delegation and caused spurious
invalid flags; bit classification repaired the harness and the complete cell
was rerun. It was not an upstream finding.

The new rsqrt refinement predicate remains an open proof obligation. The instrumented candidate observed
a correction exponent gap of 51 in all three directed modes (minimum 52 in RN),
so no universal gap ≥52 can be assumed; no additional
wrong-value witness or speculative refinement patch is reported.

Changed asinh/atanh/cospi/tanpi special checkers compile with GCC and Clang;
their unbounded special campaigns were not run. The authoritative implementation
CI was successful at the cutoff. Proof CI was inaccessible (HTTP 403).

## Proof progress

[Source/proof review](SOURCE-REVIEW.md) distinguishes new and historical issues.
The corrected FastTwoSum model achieves the stated error and low-part bounds
in all four Gappa modes. Independent C/MPFR examples verify the original
directed-rounding mismatch. All 16,384 table/mode combinations satisfy the
stated table bounds; Sollya and reduction checks support the new approximation
analysis. Exact derivative arithmetic and outward subnormal endpoint enclosures
support specific deductions. The full exp theorem still needs source/domain
alignment, historical hard-case completeness and the listed exactness/contraction
obligations. No exhaustive historical search or complete PDF rebuild is claimed.

Sine's numerical source is unchanged and its proof diff is formatting only.
Its coverage is refreshed at 177/177 lines and 42/42 arcs; previous arithmetic
obligations remain. New tanpi rows close its measured gaps: 194/194 lines, 70/70 arcs.
New noncomment rows: sinpi 7,203, cospi 497, tanpi 41,508, acosh 1. No selected
corpus lost an existing noncomment row.

## Complete coverage census

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
| exp | 117/117 | 32/32 | 0/0 |
| exp10 | 135/135 | 51/52 | 0/1 |
| exp2 | 130/130 | 53/54 | 0/1 |
| log | 117/117 | 30/30 | 0/0 |
| log10 | 129/129 | 28/28 | 0/0 |
| log2 | 96/96 | 22/22 | 0/0 |
| rsqrt | 72/72 | 30/30 | 0/0 |
| sin | 177/177 | 42/42 | 0/0 |
| sinh | 168/168 | 42/42 | 0/0 |
| sinpi | 180/180 | 50/52 | 0/2 |
| tan | 415/474 | 112/163 | 59/51 |
| tanh | 153/153 | 40/40 | 0/0 |
| tanpi | 194/194 | 70/70 | 0/0 |

[Raw missing lines/arcs](MISSING-COVERAGE.json). A zero gap describes the
instrumented target file in this configuration; it is not a correctness proof.
The exp gap closed because upstream removed the old loop, not because this
review proved that deleted path unreachable. exp10 wins the 0/1 tie with exp2
by the repository's alphabetical tie rule.

## Next work and reproduction

Keep one active coverage target, exp10, with the bounded caller-residue proof
step in its target note. Separately, a [hypot-first bivariate pilot](../../docs/BIVARIATE-PILOT.md)
proposes exact-integer verification, a 131,072-pair limit and a four CPU-hour/two
wall-hour cap. It has not run; a reviewed bivariate runner/schema is required
before dispatch. The weekly unary regression remains unchanged.

Start with [RUNBOOK](../../RUNBOOK.md), qualify GCC and Clang, then run the
25-function baseline at the exact pin in this report. Supplement command:
`python3 weekly/2026-10-18/reproduce_focus.py`. It uses an exclusive runner lock,
per-child timeouts and checkpoints under `.work/20261018-supplement`; use an outer
90-minute timeout as in the runbook. Reuse that directory only with identical
script, source, compiler and configuration; use a fresh directory after changes.
The public adapter now accepts only the exact historical exp/RZ failure
with contraction off; unexpected failures or incomplete checker sequences stop
the run. This guard is tested against saved receipts and deliberately corrupted
copies. The guard also requires every candidate and forced-accurate cell to pass. Original measured receipts keep their original script/source bindings and are stored separately from rerun outputs.

For exp10 observations, first reproduce run ID `20261018-baseline-gcc-e1`, then
`python3 weekly/2026-10-18/capture_exp10.py plain` and the same command with
`covered`. The saved evidence can be checked without a debugger using
`python3 weekly/2026-10-18/verify_exp10_capture.py PATH/TO/exp10.c`.
Gappa models, Sollya input and the MPFR C table driver are under `exp-proof/`.
See [proof reproduction](exp-proof/README.md), [validation](VALIDATION.json),
[independent-review disposition](REVIEW-DISPOSITION.md) and [hash manifest](SHA256SUMS.json).
