# Publication validation across platforms

The October 25 tooling repair preserves the evidence and its existing schemas.
It does not qualify a native Windows numerical runner or execute the proposed
bivariate pilot.

Two independent checkout/validation problems were reproduced against workbench
commit `71d15c5adb91b3b9e9a778c819650422250d9e04`:

- Windows `pathlib` globbing includes `MISSING-COVERAGE.json` when looking for
  `*-coverage.json`. The summary has `pin` and `profile` fields, which the raw
  gcov allowlist correctly rejects. Discovery now requires the exact lowercase
  suffix, matching Linux, both for recursive validation and the four-mode count.
  Genuine raw files with unknown fields are still rejected. Summary files remain
  covered by checksums and the privacy screen; no dedicated summary schema was
  added in this repair.
- Git's `core.autocrlf=true` can convert historical evidence at checkout, making
  its bytes differ from both Git blobs and the recorded SHA256 manifests.
  `.gitattributes` now disables text conversion for `weekly/` and `candidates/`.
  It does not modify the stored evidence or recompute historical checksums.

Use a fresh checkout for byte-faithful validation. Adding attributes to an
existing checkout does not guarantee that previously converted files have been
rewritten. Preserve local work before replacing any checkout; do not alter
manifests to match converted files.
When validating an older commit without these attributes, clone with
`git -c core.autocrlf=false clone <repository-url>` to preserve its evidence.
Do not stage converted historical files or use renormalization to repair them.

## Validation of this repair

- Native Windows Python 3.10: all six publication tests pass. The new tests
  reproduce the old discovery/count failures and retain rejection controls.
- Linux/WSL Python 3.12 on a native Linux filesystem: all 18 tests pass; the full
  validator passes on both the base and repaired code (six receipts).
- The repaired full validator also passes on the byte-faithful Windows checkout.
- All 818 historical files under `weekly/` and `candidates/` retain identical
  SHA256 values. An export with `core.autocrlf=true` and the new attributes
  preserves those same bytes.

The numerical runner still requires its supported POSIX environment. Attempting
the entire test suite natively on Windows produces three errors and one failure
in POSIX process/signal/lock tests; this repair does not claim to fix that scope.
The case-sensitive discovery test supplies Windows-style matches explicitly, so
it exercises the filter even when tests run on Linux. Additional lowercase raw
coverage files still fail the four-file check.

Claude Opus 5.5 independently reviewed the code diff and approved the repair.
That reviewer did not execute tests; the integrating agent performed the runs
and hash comparisons reported above. The review's existing-checkout warning is
addressed by the fresh-checkout guidance, without recommending destructive resets.
