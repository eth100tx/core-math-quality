# Release verification and independent review

**Independent release review: Claude Opus 5.5, source-only, completed.**
The reviewer did not execute tests. Its required corrections and the release
operator's independent verification are recorded below.

## Executed version and configurations

The deterministic runner is available at
[452de58](https://github.com/eth100tx/core-math-quality/blob/452de585a810502abf6d4a917b0004b9dcb88559/quality.py).
The released deterministic runner is byte-for-byte the executed quality.py. Its SHA-256 is `64f4b38c7267b389c0ede64ae9e6b1aa968ed7f8e80063c9b523d8b23cbfa566` in every primary/profile/fresh
receipt. It was frozen throughout the numerical runs. Later documentation and
publication-validator changes do not change those executed arithmetic checks.
The candidate reproduction has its own script hash in its before/after receipt.

- GCC 13.3.0, baseline x86-64, errno enabled: all 25 functions; four modes;
  separate O3 regression and O0 target coverage; all passed.
- GCC 13.3.0, x86-64-v3: sin and rsqrt, four modes, both builds; all passed.
- Clang 18, x86-64: sin and rsqrt, four-mode O3 regression; all passed.
- No complete second-compiler census, errno-disabled census, macOS execution,
  or shared-header coverage is claimed.

## Runner and candidate qualification

Fourteen selftests pass: eleven in tests/test_quality.py and three schema tests
in [test_publication.py](../../tests/test_publication.py). They include real detached-child termination, timeout
cleanup, cross-process lock exclusion, stale-counter removal, denominator checks,
accepted-row checks and schema rejection. The synthetic checker controls pass
the good implementation and detect deliberately wrong values, inexact flags and
errno in each of four modes. The negative controls exercise the ordinary
checker only, because a failing ordinary check skips instrumented execution.
The positive control exercises both builds. These are not upstream defects.

A [fresh local Git clone](runs/20261006-fresh-clone-rsqrt/result.json) at `452de585a810502abf6d4a917b0004b9dcb88559` downloaded and
verified its own pinned rsqrt sources and corpus, ran all 14 selftests, qualified
the machine, and passed O3 regression plus O0 coverage in all four modes.
Its source/checker/corpus hashes, flags, per-mode coverage and union match the
primary baseline. This is an independent source acquisition/build in the same
host/toolchain, not cross-machine replication.

The asinpi candidate replays the entire original and augmented corpora. Accepted
counts increase by exactly two per mode/build, reflecting the added row and
upstream sign symmetry. The source is unchanged; the raw union improves from
75/76 to 76/76 arcs. `git apply --check` succeeds and applying the patch produces
exactly the tested augmented-corpus SHA-256. No implementation fix is claimed.

The sine helper experiment maps branch indices with two explicit internal
integers. It does not prove those states occur on the public function's path.

## Review and publication safeguards

Claude Opus 5.5 provided separate planning, code and repair reviews.
Those reviews were source-only advisory reviews; the reviewer did not run the
tests. Corrections independently implemented and checked include fresh per-mode
counters, source Git-blob verification, strict run identities, preservation of
completed runs on reuse errors, all-25 ranking eligibility, parsed failure
classification, process cleanup, bounded output, and raw-count recomputation.

The final review recommended release after R1-R6, without rerunning the baseline
if the executed runner hash matched. All six were independently checked:

1. **Target tie:** disclosed asinpi/sin at 0 lines/1 arc; alphabetic selection and
   changed-code sine review are distinct priorities.
2. **Negative controls:** code now requires every ordinary mode to fail; all four
   controls rerun successfully. Instrumented negative checks are not claimed.
3. **Selftests:** the reviewer had initially received only the eleven-test file;
   the three-test publication file exists in the fresh clone and was executed.
4. **Privacy:** separate release audit checked all tracked UTF-8 files, reachable
   Git blobs and commit metadata. The validator alone is not this full audit.
   Public author name CORE-MATH AI assistant is intentional; noreply email used.
5. **Runner provenance:** released runner hash exactly matches every receipt.
6. **State:** candidate labeled tested/source-reviewed, not submitted or accepted.

Also tightened corpus parsing, reran sine branch mapping with the exact primary
coverage flags, clarified zero reachability and the source-inspected asinpi
condition, checked matching cos/tan deficits, cited the checker's EDOM contract,
and documented domain-corpus discretion and acquisition retry behavior.
The follow-up closure review confirmed the technical corrections and made
release conditional on a case-insensitive privacy scan with an explicit email
allowlist. That scan is required on the exact clean commit being pushed; the
release operator retains its commit-specific record. No tags are pushed.
Full private reviewer prompts are not part of this repo.

Evidence exports have complete SHA-256 manifests. The validator rebuilds each
coverage union from four raw reports, checks receipt selections/configurations
and candidate before/after consistency, and screens publication data. Separately, the release operator checked the full
tracked-file inventory, every reachable Git blob and commit metadata for private
markers. This is additional release auditing beyond the public validator.
This new repository has no private audit ancestor, correspondence or credentials.
Commit identity uses a public GitHub noreply address. No upstream write occurred.

Remaining limits: source acquisition needs network access; locks coordinate one
OS user and require external coordination across users/containers/hosts; no
general process-memory sandbox is claimed; children inherit blocked SIGTERM/SIGINT
and must be cancelled through the runner; archived ranking validation is tied to
the version-1 target population until a schema migration; SIGKILL/power loss cannot guarantee
terminal status or complete child CPU accounting. Use the documented outer
timeout and inspect interrupted runs. Formal sine proof review remains separate.
