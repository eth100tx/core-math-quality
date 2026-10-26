# Reproducible runbook

## First visit

Read the README and configuration table. Install the listed build dependencies
in a user-controlled Linux/WSL environment. The runner uses Python's standard
library. `doctor` compiles and executes a small probe of binary64 representation,
rounding-mode behavior, subnormals, FMA and MPFR/GMP availability; checks matching
GCC/gcov versions and checks the v3 ISA before a v3 build. A successful doctor
is machine qualification for the probe, not a complete platform certification.

```sh
python3 -m unittest discover -s tests -v
python3 quality.py doctor --profile gcc-linux-x86_64
```

If you already have a CORE-MATH checkout, you may copy its `src/` directory into
`.work/sources/FULL_CURRENT_SHA/src/` before fetching. The runner verifies each
requested file against the pinned upstream Git blob; stale or changed files are
replaced. The local directory name is never accepted as proof of source identity.
This avoids downloading large unchanged corpora. The original checkout stays
untouched. Network access is still required to verify the authoritative tree.
Files are blob-verified against GitLab's reported tree at the pinned SHA over
TLS; the client does not independently reconstruct the entire Git commit tree.
If GitLab rate limits or a transient download error interrupts acquisition,
retain the verified cache and retry the same command later within a fresh outer
timeout. Do not use an unbounded retry loop or treat acquisition failure as PASS.

## Weekly or ad hoc

First read `IMPROVEMENTS.md` and validate `config/improvements.json` with
`python3 validate.py`. Refresh prior-candidate adoption at exact pins. Select
one primary review task and at most one bounded bivariate task under the queue's
shared CPU/wall envelope. Routine changed-function regressions count against
that same envelope; checkpoint at the cap instead of automatically escalating. A missing research archive blocks reproducing it,
not independent checker design or qualified infrastructure work. Preserve the
original import request and mark its evidence unverified until reproduced.

The weekly output carries three ranked improvement slots, each with state,
this week's substantive change and next artifact. Unchanged items get a short
dated reference, not another maintainer request. Three slots are not three new
defects. If fewer than three genuine priorities exist, state that explicitly.
Meaningful progress needs a verifiable artifact or resolved obligation, not
a larger test count or a cosmetic queue-state change.

Check current operator scope before dispatch. If routine coverage is paused,
park its target and retain dated measurements; use a noncoverage profile for
focused changed-code regressions. Do not manufacture a fresh ranking from a
subset. A completed regression test does not close deferred source/proof review.
Archived bivariate results remain unverified until imported and independently
reproduced. New experiments require a separate exact-input, four-mode runner.
An authorized future
pilot gets one bounded task within the same overall budget, not an additional
open-ended campaign. Do not treat historical native runs as Linux qualification.

1. Read `STATUS.md` and the previous weekly report. If the operator has authorized
   correspondence access, read new requests privately and record only neutral
   public requirements. Anyone can run the tests without email access.
2. Resolve the upstream GitLab implementation revision and inspect the comparison
   from the previous reviewed baseline. Do not treat the last email date as a Git
   commit. Proof changes and open proof obligations need a separate review.
3. Run the selection aid, then manually review shared/build/header changes:

```sh
python3 quality.py plan --base FULL_PREVIOUS_SHA --pin FULL_CURRENT_SHA
```

4. When coverage is enabled, for a fresh coverage census, run all 25 in a single comparable profile:

```sh
python3 quality.py run --pin FULL_CURRENT_SHA --functions all \
  --profile gcc-linux-x86_64 --errno 1 --run-id YYYYMMDD-baseline --max-minutes 100
```

   For a focused request, substitute `--functions sin` or `sin,cos`. Change
   `--errno 0` or the profile only with a different run ID. Raw reports remain
   configuration-specific. Every function runs the entire pinned `.wc` file,
   the upstream checker's built-in special/NaN checks, all four modes, and both
   signs where upstream defines `WORST_SYMMETRIC`. This is **not** `check_special`
   or exhaustive/random testing. Add those as separate recorded investigations.
5. Read `.work/runs/RUN_ID/result.json` and `status.json`. A nonzero exit or
   INCOMPLETE is not a clean result. Reuse the identical command to resume
   completed functions; use a new ID after any input/tool change. Each function
   restarts its interrupted modes as one unit to avoid mixing counters.
6. When coverage is active, inspect the smallest nonzero gaps using `docs/COVERAGE.md`. Reproduce a
   new value failure without instrumentation before labeling it a defect.
7. Export to a new weekly directory:

```sh
python3 quality.py export --run-id YYYYMMDD-baseline --week YYYY-MM-DD
```

8. Write the report with `templates/WEEKLY.md`. Independently review evidence,
   classification, target choice and patch candidates. Run `python3 validate.py`
   and the selftests. Inspect the full staged diff and use a public-safe commit
   identity. Publish only to a repository the operator authorized.
9. Update STATUS and weekly index. Advance only the completed scope; record
   deferred source/proof/compiler work. Review, measurement and notification
   watermarks are separate. Never hide a missing check behind a passing total.

## Resume and bounded operation

The lock is kernel-managed, shared by clones using the same OS user account:
it is released when the process exits, without
deleting stale lock files. A remaining file alone does not mean a live run.
`status.json` names the current function and command with its timeout. The parent
prints each mode and retains child outputs. Each child runs in a process group,
killed on timeout or a handled termination signal. Download calls also have timeouts. For an overall wall-clock
limit that includes acquisition, use the scheduler's outer timeout.
Cancel through the runner's parent process so it records the interruption and
terminates the child process group. The runner restores the caller's original
signal mask in spawned children; its temporary spawn guard is not inherited.
Signals intentionally blocked by the caller remain blocked.

Successful function results are reused only if the identity matches the source
manifest, runner hash, config hashes, compiler/probe environment, profile, errno and selection.
Unsuccessful functions are retried whole. Raw `.gcda` counters are removed before
each mode. Never manually edit a PASS result to force resume.

CPU time in each receipt is child CPU for that invocation. Append-only
`invocations.jsonl` retains resume accounting; parent/AI overhead is recorded by
the operator's campaign ledger separately. Killed descendants may make collected
child CPU a lower bound; budget conservatively in external accounting. No
long-lived worker is installed. During a child, the status timestamp may remain
unchanged for up to the recorded ten-minute limit; it names the bounded operation.

After preserving reviewed exports, unused `.work/runs/RUN_ID` directories may be
removed by the operator. Do not remove an active run or its source cache. This
workbench deliberately does not install an automatic cleanup service.
