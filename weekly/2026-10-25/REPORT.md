# Week ending October 25, 2026

**The previously reported `exp` value error and `rsqrt` underflow-flag regression are fixed in the tested master revision. A focused `asin` corpus check also passes. This is a three-function test update, not a repository-wide correctness certification.**

- Both fixes and witness rows are upstream; no additional library failure was observed in the checks below.
- No new compiler-specific failure was established in these configurations. No new patch is proposed this week.
- New log/exp/sine proof work remains incompletely reviewed. Source/proof binding and certificate replay are explicit next steps. Routine coverage reporting is paused; the previous measurements remain dated October 18 evidence.

## Pins and scope

Implementation `0ce0cbc15935e24c656280e5a46c34e89f301b7a`, compared with `dae5dd8c0d5bd2691b45de28c9edbe12f067c3d3`.
Proof repository `3ec3c827eb3b0c4849ad2f47da20ec68dadf8482`, compared with `5a42d3fb72533077c8b745b9fcd39b84ad3ee92a`.
The separate implementation branch `exp_proof` is pinned at `d7a619c5de08abd5c89460cd2f472c7d8ea767b7`; it is not master and was not executed here.
Final inventory refresh was October 26 UTC, still October 25 in the review's local calendar. The pins are unchanged from the earlier October 25 fix checks. A compact fresh replay was added specifically to remove reliance on inferred runner provenance; no broad campaign was repeated.

[Inventory](INVENTORY.json) lists all ten changed implementation paths and nine proof paths. [Per-file dispositions](SOURCE-REVIEW.json) retain unfinished work. The global completed implementation/proof review watermarks remain at the October 18 base pins. Focused execution at the new implementation pin does not advance those global watermarks.

## Adopted fixes

| Function | Exact input row | Upstream membership at this pin | Verified outcome |
|---|---|---|---|
| `exp` | `0x1.5a3a157335f3bp+9` | `exp.wc:1129479` | Old control reproduces the toward-zero result `0x1.ffdebdc4e28acp+998` instead of `0x1.ffdebdc4e28abp+998`; new source passes four modes. |
| `rsqrt` | `0x1.0000000000001p+1022` | `rsqrt.wc:9957` | Old control reproduces spurious underflow in four modes; new source passes the explicit value/flags/errno boundary probe. |

The source changes match the previously tested candidates exactly. The exp allowance changed from `1.64e-19` to `0x1.27p-62`, matching the manuscript allowance; this is not a newly proved error bound.

For each function, the complete pinned upstream `.wc` corpus and the original witness plus its 256 adjacent positive inputs on either side (513 positive inputs total) pass all four modes under GCC 13.3 and Clang 18.1.3. The fresh replay binds each cell to its [environment qualification](fix-replay.json). Configurations: Linux x86-64 baseline ISA, O3, `-frounding-math`, `-fno-finite-math-only`, `-ffp-contract=off`, errno enabled; GCC additionally uses `-fsignaling-nans`, Clang does not. The rsqrt symmetric checker also checks negative counterparts. These are upstream `check_worst` checks, not exhaustive/random testing or the standalone `check_special` suite. No x86-64-v3 or contraction-enabled build was refreshed this week. Explicit fma calls may use hardware through the runtime library.

The separate [rsqrt probe](rsqrt_probe.c) checks eight inputs in four modes, including all standard floating-point flags and errno, on each compiler: 32 cases, zero failures on new source. Its failure predicate checks underflow, overflow, invalid, divide-by-zero, inexact agreement and errno; printed output shows only underflow/inexact/errno. This samples the affected high binade; it does not exhaust it. Exp has no comparable separate flags/errno probe this week: only the upstream checker's implemented conditions were exercised. No inference of full exception/errno correctness is made from value agreement.

[Original focused receipts](fix-verification/FIX-VERIFICATION.json) · [qualification](fix-verification/QUALIFICATION.json) · [publication-time recheck](fix-verification/RECHECK.json) · [restart provenance](fix-verification/PROVENANCE.json).

**Historical provenance limitation:** an earlier storage interruption truncated the original runner. Three pre-interruption cells were rerun; those replay receipts record the retained runner hash (`26b9605e…`). Five other resumed receipts do not embed a runner hash; their identity is inferred from the retained resumed script (`6d260f45…`). This distinction remains explicit in the provenance and recheck files. Publication-time checks independently matched all eight receipts, retained source/corpus hashes, old-failure outputs and binary hashes against the prior reconciliation. A hash observed now is not a contemporaneous execution record. No original receipt was edited to fill that gap. Repeated historical corpus-verification entries correspond to the four mode checks, not four distinct corpora.

**Fresh primary evidence:** [fix-replay.json](fix-replay.json) repeats all eight old/new cells using the included [self-contained driver](reproduce_fixes.py). Every new cell records its driver, public runner, source/input and checker binary hashes, environment, timestamp, corpus hashes and exact command outputs. The probe source is hashed; its binary was not separately hashed. The current conclusions are supported by this fresh replay; historical receipts above remain unchanged for traceability. Corpus membership locations in the table are physical file line numbers, including comments, rather than test-row counts.

## New focused asin regression check

The current complete asin `.wc` corpus passes all four modes through the public runner, Clang 18.1.3, x86-64 baseline, O3, contraction off, errno enabled, with no coverage instrumentation. [Receipt](runs/20261025-asin-clang/result.json) includes exact source/corpus identity and mode counts. This finite regression check does **not** establish equivalence of the changed casts, signed-subtraction safety or LLP64 portability. Those source obligations remain open; no defect is asserted from the cast change alone.

## Proof and deferred work

- `log.c` changes are comments only. `logfast.sollya` uses `dirtyinfnorm`, not a rigorous approximation certificate. The new near-zero model and its eight mode/interval Gappa runs were inventoried, not replayed; source binding remains open.
- Exp's changed manuscript/scripts require review against the separate WIP implementation branch. The earlier directed FastTwoSum model candidate remains unadopted; this is a status carry-forward, not a new failure. No full exp proof is certified here.
- Sine's new accurate-phase scaling/coefficients differ from unchanged master. Existing certificates are not assumed to bind to that new model. This is an incomplete proof-to-source reconciliation, not an observed master numerical failure.
- `check.sh` changed its default flags; this week's explicit strict flags were retained. The upstream default script itself was not executed. Implementation CI was successful at acquisition; proof CI access returned HTTP 403 and is unknown.
- No new all-25 census, gap ranking, cos/tan campaign or bivariate execution. The hypot-first bivariate proposal remains gated on reviewed certificate import and a separately qualified runner. No bivariate bug or novelty is claimed.

## Reproduce and review

Use the documented Linux dependencies and run from the repository root:

```sh
python3 quality.py doctor --profile clang-linux-x86_64
timeout --signal=TERM --kill-after=30s 15m python3 quality.py run \
  --pin 0ce0cbc15935e24c656280e5a46c34e89f301b7a --functions asin \
  --profile clang-linux-x86_64 --errno 1 \
  --run-id independent-20261025-asin --max-minutes 10
```

For the exact old/new full-corpus, neighbor and probe replay, run `PYTHONOPTIMIZE=0 timeout --signal=TERM --kill-after=30s 15m python3 weekly/2026-10-25/reproduce_fixes.py`. This recorded driver uses assertions: do not use Python `-O` or `-OO`. It uses the normal advisory lock, per-command timeouts and a ten-minute science budget, refuses to reuse an existing output directory, and writes receipts under `.work/candidates/20261025-public-fix-replay`. Before a repeat, preserve its old receipts and move/remove that output directory only after confirming no run is active. The previous [focused reproduction driver](../2026-10-18/reproduce_focus.py) and candidate witness files remain available at their documented historical base. Do not apply historical patches to already-fixed master. Original private orchestration is not required for this new self-contained replay.

The checkout passed Linux doctor, 18 self-tests and the existing strict validator after the reviewed portability repair at workbench `8fdc27dfe44c891db6d2ce7b32e0ec17068fdf9d`. The validator was not weakened and old evidence was not rewritten. The new asin run used that workbench revision. Actual Claude Opus 5.5 planning and final independent review, claim verification, limitations and dispositions are recorded in [REVIEW.md](REVIEW.md). Tests are not proofs.
