# Week ending November 1, 2026

**The pinned sine source has a reproducible build regression with a tested
one-character fix. Changed log/tanpi corpus checks and a new exact hypot
regression family pass in the configurations below; broader proof review
remains incomplete.**

- No new correctly rounded value failure was observed in the completed tests.
  Sine cannot build at this pin, so it has no fresh numerical PASS.
- GCC and Clang both reject the same invalid source directive. This is not a
  compiler miscompilation. A small tested patch is available for pickup.
- Eight exact near-midpoint hypot pairs, with swaps, add passing regression
  candidates absent from the pinned corpus. No bug or novelty is claimed.

## Pins, inventory and limits

Implementation: `5f65574e2b3631fb31e9b88dd27782a936c68095`.
Proof: `d5fab2e483d00b7a21c5b50b1abb877cadeb5c5b`.
[Pins](PINS.json), [complete path inventory](INVENTORY.json), and
[per-path dispositions](SOURCE-REVIEW.json) separate current tests from retained
reviews and deferred obligations. The inventory compares from completed-review
bases `dae5dd8c0d5bd2691b45de28c9edbe12f067c3d3` and
`5a42d3fb72533077c8b745b9fcd39b84ad3ee92a`, respectively. Complete paginated trees
identify 29 implementation paths and 26 proof paths, counting both sides of a
proof-script rename. The comparison endpoint has 25 proof entries because it
combines that rename; no path is silently dropped.

Global completed-review watermarks **remain at those base pins**. These focused
tests do not close deferred source/proof work. Exp and routine coverage remain
paused. The October 18 global measurements and October 29 requested cosine
measurements keep their dates and original configurations; no new ranking.

## 1. Restore the sine build — tested candidate

At `sin.c:278`, `#if1` is invalid. Replacing it with `#if 1` restores compilation
under GCC 13.3 and Clang 18.1.3 on Linux x86-64. Both previous revision
`b5a3f7ffb9315afae57a309623c3c5c226ec8bec` and
the corrected revision compile; the original current source fails with the
expected diagnostic. The corrected preprocessed output matches the previous
active code under the recorded token comparison.

[Patch and instructions](../../candidates/sin-preprocessor-space/README.md) ·
[receipt](sine-build.json) · [reproducer](reproduce_build.py).
This changes no numerical expression in the active branch. The October 26
sine kernel evidence is retained as historical evidence, not re-labelled as
execution of this broken pin. The patch is tested, not an all-input proof.

## 2. Bind the new log near-one proof — tests pass, proof open

The full pinned `log.wc` and `tanpi.wc` pass four rounding modes with Clang
18.1.3, baseline x86-64, O3, `-frounding-math`, `-fno-finite-math-only`,
`-ffp-contract=off`, and errno enabled; no coverage instrumentation.
The [public-runner receipt](runs/20261101-log-tanpi-clang/result.json) records
134,960 log rows and 98,557 tanpi rows. Tanpi's symmetric checker executes
197,114 tests per mode. These are upstream `check_worst` checks, including its
built-in special inputs, not the separate `check_special` suite or exhaustive
testing. GCC numerical regressions for these two functions were not refreshed.

By source inspection, the tanpi change extracts the same double-double division
expression into a helper; no general equivalence proof is claimed. Log
introduces `cr_log_tiny` and associated proof/generation files.
Its claimed approximation margin still needs rigorous certificate/source
binding: `dirtyinfnorm` is exploratory, and no new Gappa replay or full log
proof is claimed here. This is the next bounded primary review task, rather
than treating passing corpora as a proof. The previously queued asin range/ABI
premise is explicitly deferred, not closed; its unsigned-gap cleanup remains
adopted with dated tests.

## 3. Add exact hypot regressions — certified small family

The identity `(3m+2)^2+(4m+1)^2=(5m+2)^2+1`, for eight specified odd `m`, yields
eight unordered pairs strictly less than `2^-55` result ulp above a midpoint.
[Construction, rational bounds and optional `.wc` file](../../candidates/hypot-midpoint-plus-one/README.md).

All 16 ordered rows pass four modes under GCC 13.3 and Clang 18.1.3 with the
existing qualified exact-input adapter: 128 CORE-MATH observations, gated by
the integer certificates and two MPFR calculations. Inexact is set, the other
four standard flags are clear and errno is zero in every observation. Flags
were cleared before each call; sticky-flag preservation is not tested. The
fresh compiler doctor checks and all six deliberate fault controls pass for
each compiler. [Execution](hypot-execution.json) records values, flags and errno
separately, exact tool/source hashes, flags and CPU/wall use. This remains a
restricted positive-normal test, not general platform qualification.
Neither this test nor the sine build comparison refreshes an x86-64-v3 or
`__FMA__`-enabled configuration. The hypot rows were executed through the
restricted adapter, not upstream's bivariate `check_worst`; no added stage or
branch coverage is claimed.

The complete pinned hypot corpus contains 33,174 rows. None matches these
pairs directly or after absolute-value, swap and common power-of-two
normalization; 284 zero/nonfinite rows cannot match this positive-normal family.
[Membership receipt](hypot-family.json) and a separate exact-rational parser
agree. This is a full **membership comparison**, not a full-corpus numerical
run, a regenerated completeness census or a claim that the construction is new.
The missing research archives, angular/pow certificates and atan2 stage
comparison remain open. No unchanged pow search was scaled.

## Prior proposals and unfinished review

- Cosine's proof pin is unchanged from October 30; the focused sign correction
  is still open. All 13 recorded source/build/harness/corpus blobs still match
  the October 29 run; [reconciliation](COS-RECONCILIATION.json). No duplicate
  execution or new completeness/unreachability claim.
- Asin unsigned-gap, exp allowance and rsqrt underflow fixes remain present.
  Their dated checks were not repeated. Exp work stays paused.
- Tangent proof work is inventoried and deferred; no readiness or independent
  completion is asserted. Shared script changes were inspected but not executed
  as a CI/performance campaign. Compiler-issue listings are not newly reproduced
  compiler defects. See every path's disposition and the deferred queue snapshot.

## Reproduce, review and next checkpoint

Run on the documented Linux dependencies with one runner. The two custom
drivers use fixed disposable paths and refuse to overwrite them. Use a fresh
checkout or preserve and move those completed outputs before reproduction:
use this report's workbench revision, since later tool changes may correctly
fail its recorded identity checks.

```sh
timeout --signal=TERM --kill-after=10s 8m python3 -B weekly/2026-11-01/reproduce_build.py
timeout --signal=TERM --kill-after=10s 12m python3 -B weekly/2026-11-01/run_hypot_family.py
timeout --signal=TERM --kill-after=10s 15m python3 -B quality.py run --pin 5f65574e2b3631fb31e9b88dd27782a936c68095 --functions log,tanpi --profile clang-linux-x86_64 --errno 1 --run-id independent-20261101-log-tanpi --max-minutes 10
python3 -B weekly/2026-11-01/verify_evidence.py
python3 -B validate.py
```

`verify_evidence.py` replays the committed receipts; it does not automatically
substitute the output of a new run. It independently parses corpus membership,
applies the published patch and checks pickup rows against the certificates.
It reuses the qualified value/flag/errno classification functions rather than
claiming another independently implemented library oracle. Every numerical child
has a timeout; the outer timeout covers acquisition and doctor calls too.
The family checker initially stopped on non-ASCII corpus comments before any
library execution; decoding UTF-8 fixed the tooling issue, and a new run ID
preserves the failed checkpoint. An attempted evidence export encountered the
active-run lock and was retried only after the numerical runner finished.

[Independent review](REVIEW.md), [receipt verification](VERIFICATION.json),
[learning](LEARNING.md), and [accounting](ACCOUNTING.json) record the scope.
Next: check sine patch adoption and bind the log near-one error model. Preserve
cosine/asin obligations and the complementary hypot-family checkpoint; do not
repeat the completed unchanged campaigns. Nothing was pushed to upstream.
