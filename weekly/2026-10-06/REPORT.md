# Initial qualification — 6 October 2026

**Health:** All 25 priority binary64 functions passed the complete upstream
worst-case replay in the primary GCC profile. This is a bounded test result,
not a whole-library correctness proof.

- **Correct rounding / .wc:** No new failure in the 25-function baseline.
- **Compiler / patches:** No new confirmed compiler issue or proposed fix from this baseline.
- **Coverage target:** `asinpi` has 0 missing executable lines
  and 1 missing branch outcome: a tested one-row corpus candidate is available below.

This is an ad hoc initial census, before the first scheduled Sunday edition.

## Scope and evidence

Source [e78b460](https://gitlab.inria.fr/core-math/core-math/-/tree/e78b460c41e5e155f45a5ff824140b81c84f55cc)
(`e78b460c41e5e155f45a5ff824140b81c84f55cc`). All 25 functions use the same commit.
GCC/gcov 13.3.0, Ubuntu 24.04 under WSL2 x86-64; MPFR 4.2.1, GMP 6.3.0.
Profile `gcc-linux-x86_64`, errno enabled, contraction off, `-frounding-math`.
Ordinary correctness build `-O3`; target-only coverage build `-O0 -g --coverage`.
Four rounding modes, exact upstream `.wc` files, unchanged checker built-in NaN
checks, and upstream sign symmetry where defined. No separate `check_special`,
random or exhaustive domain search is included.

The baseline contains 200 checker executions and 137,352,424 processed tests,
including repetitions across modes/builds/signs; this is not a unique-input count.
Full commands, source/checker/corpus identities, return codes and raw per-mode
counts are in [the run receipt](runs/20261006-baseline-gcc-e1/result.json).
The [manifest](runs/20261006-baseline-gcc-e1/SHA256SUMS.json) hashes every artifact.
The [change inventory](CHANGE-INVENTORY.json) records all changed paths since
the prior source pin: sine was tested; the sincos benchmark change was read
but not benchmarked; binary16 cbrt and binary64 pow changes are outside this
25-function qualification. Proof-repository revisions are not covered here.

## Coverage census

Target `.c` files only. Helpers attributed to separate headers are excluded;
helper definitions inside the target `.c` file are included.
The denominator is compiled code in this precise configuration; preprocessor-
excluded paths are not counted. Raw gaps are never subtracted merely because
an earlier review classified a similar path as unreachable.

| Function | Lines hit/total | Arcs hit/total | Missing lines | Missing arcs |
|---|---:|---:|---:|---:|
| exp | 135/136 | 40/42 | 1 | 2 |
| log | 121/122 | 35/38 | 1 | 3 |
| exp2 | 131/132 | 54/56 | 1 | 2 |
| log2 | 96/97 | 23/24 | 1 | 1 |
| exp10 | 136/137 | 53/54 | 1 | 1 |
| log10 | 132/132 | 32/34 | 0 | 2 |
| rsqrt | 71/71 | 36/36 | 0 | 0 |
| sin | 175/175 | 43/44 | 0 | 1 |
| cos | 372/431 | 100/151 | 59 | 51 |
| tan | 415/474 | 112/163 | 59 | 51 |
| asin | 108/108 | 34/34 | 0 | 0 |
| acos | 124/124 | 34/34 | 0 | 0 |
| atan | 100/100 | 40/40 | 0 | 0 |
| sinpi | 179/179 | 51/54 | 0 | 3 |
| cospi | 148/148 | 46/50 | 0 | 4 |
| tanpi | 190/194 | 67/70 | 4 | 3 |
| asinpi | 258/258 | 75/76 | 0 | 1 |
| acospi | 148/148 | 62/62 | 0 | 0 |
| atanpi | 152/152 | 58/58 | 0 | 0 |
| sinh | 168/168 | 44/46 | 0 | 2 |
| cosh | 153/153 | 44/46 | 0 | 2 |
| tanh | 153/153 | 40/40 | 0 | 0 |
| asinh | 177/177 | 50/50 | 0 | 0 |
| acosh | 181/181 | 46/46 | 0 | 0 |
| atanh | 159/159 | 36/36 | 0 | 0 |

Fully covered target files in this configuration: `rsqrt`, `asin`, `acos`, `atan`, `acospi`, `atanpi`, `tanh`, `asinh`, `acosh`, `atanh`.
Other configurations may expose different paths. Individual rounding-mode
coverage remains in the receipt; a full union does not imply full per-mode coverage.

The automated order excludes zero/zero functions and sorts by missing lines,
then missing arcs, then function name. The complete ranked queue is in the
receipt. It identifies a small measured gap, not necessarily the easiest proof.
Keep the selected target active until it is closed or deliberately deferred.

`asinpi` and `sin` tie at zero missing lines and one missing arc. The stated
alphabetical tiebreak selects `asinpi`, where a simple witness is available.
Changed-code review is a separate priority: sine received full replay and
coverage checks this time rather than waiting behind the cleanup target.

The equal cos/tan deficits (59 lines, 51 arcs) were checked against their distinct
source hashes, raw reports and different denominators. The missing lines occur
in corresponding fixed-point helper definitions inside each `.c` file; the
missing arcs include different function-specific entries. They are independent
measurements, not a copied total.

## First coverage candidate

The selected `asinpi` gap is reachable. Adding **`0x1.8p+0`** (1.5, with the
checker also exercising -1.5) changes the four-mode union from **75/76 to 76/76
arcs**, with **258/258 lines**. Both original and augmented complete corpora pass
the O3 regression and O0 coverage checks in all modes. This is a coverage-only
test addition; no implementation bug or upstream adoption is claimed.

The [candidate directory](../../candidates/asinpi-domain-witness/README.md)
contains the minimal patch, source explanation, before/after receipts and a
reproduction command. Keep it active until adopted or explicitly deferred.
Raw baseline counts above remain unchanged.

## New binary64 sine

The current implementation's four-mode union reaches 175/175
lines and 43/44 branch outcomes. Missing line/arc
identities and each mode's counts are directly recorded. These gaps are not
classified as unreachable from lack of hits.

The single missing outcome is the `h == 0` arm at
[sin.c:96](https://gitlab.inria.fr/core-math/core-math/-/blob/e78b460c41e5e155f45a5ff824140b81c84f55cc/src/binary64/sin/sin.c#L96) in `u128_tod`,
where `h = r >> 64`. It asks whether the accurate path can reach this helper
with a fixed-point integer below 2^64, including whether zero is excluded by the
caller. The helper assumes nonzero input; passing zero would violate that
precondition. A useful next investigation is
to connect the caller's range and near-zero bounds to that condition, or find
a public `cr_sin` input that exercises it. Calling the helper directly would
not establish reachability from the public function.
A pinned [helper experiment](qualification/sine-branch-map.json), reproduced
with `python3 tools/sine_gap_map.py`, verifies which branch index corresponds to
each arm using synthetic helper inputs. It does not establish public reachability.
This observation does not resolve the separate rounding specification or
shift-range proof obligations.

The October 5 source change adds a portable round-to-even wrapper and explicitly
narrows a reduced integer before conversion to double. On the tested modern GCC
path, the wrapper selects the builtin. The fallback for older compilers/other
architectures is not exercised. The narrowing preserves the 53-bit value:
after the right shift by 75, an unsigned 128-bit value is below 2^53, hence it
fits in uint64_t exactly. This local argument is not a proof of the complete
sine implementation. Sine proof-paper revision review remains separate work.

## Additional qualification

Selected `sin` and `rsqrt` complete corpora also pass all four modes on:

- [GCC x86-64-v3, errno enabled](runs/20261006-selected-gcc-v3-e1/result.json),
  with separate O3 regression and O0 coverage. Counts stay profile-specific.
- [Clang 18 x86-64, errno enabled](runs/20261006-selected-clang-e1/result.json),
  O3 regression only. No LLVM coverage census is claimed.

The [synthetic controls](qualification/checker-controls.json) pass the positive
case and detect deliberate value, inexact and errno errors in each of four modes.
These synthetic failures are harness checks, not upstream findings.
See [release review](RELEASE-REVIEW.md) for clean-clone validation and review scope.
Mac and native Windows remain unqualified; Windows users can use the tested WSL path.

## Limitations and next work

- Complete corpus regression and coverage are finite evidence, not exhaustive
  correctness or proof completion. No general unreachable-path claim is made.
- Other precisions and nonpriority functions were inventoried, not tested here.
- Reconcile old coverage dispositions against current source/profile before
  reopening or calling an unchanged gap new.
- The asinpi coverage-only witness is source-reviewed and ready for optional
  upstream pickup. Retain that target until adopted or deliberately deferred.
- Independent review, additional profile checks and fresh-clone replay are
  recorded in RELEASE-REVIEW.md before publication.
