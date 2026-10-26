# Hypot verifier and Linux adapter review — October 26

Actual Claude Opus 5.5 CLI sessions independently reviewed the plan, implementation,
qualification evidence and a final addendum. The final verdict approved publication
subject to recording a green final test/validator run. The reviewer inspected the
provided code and evidence; it did not execute tests. Local checks independently
verified load-bearing claims, including both MPFR comparisons and exact bit encodings.

The review found no defect in the restricted integer arithmetic, fixture generator,
C adapter or MPFR oracle. Its conditions were closed as follows:

- The complete 144-observation receipt and executed tool snapshots are published,
  not just the derived private review summary. Each profile's 72 observations and
  specific rejection codes are checked again by the publication validator.
- Receipt mutations deliberately change values, flags, errno, modes, oracle
  bounds, scope, library identities and controls. Resealing the checksum after
  these changes does not make them valid. Corrupted tool/checksum evidence is
  rejected separately.
- Verifier tests cover both tie parities, exactness, a consistently shifted wrong
  bracket, malformed schemas/inputs, duplicate keys and positive/negative `-O`
  execution with specific failure messages. The first versions of two tests
  accidentally substituted an already-correct answer; they were corrected to
  flip a bit. No runtime acceptance boundary was weakened.
- Compiler identity is explicitly a driver hash, not a hermetic toolchain hash.
  WSL2 Ubuntu 24.04.3, profile flags and scope exclusions are named. Flag expectations
  follow the pinned upstream inexact-checking convention; sticky flags remain untested.
- The x86 glibc `FE_INEXACT=0x20` encoding was checked against the installed header.
  Raw and decoded flags must agree. A new receipt type is required for another ABI.
- A pre-existing process-cleanup selftest raced child startup after 0.7 seconds.
  It now waits on a bounded local socket readiness signal, then retains the same
  child-death assertion. The process helper already blocks SIGTERM around spawn
  and installs the handler before unblocking it; that implementation was unchanged.
- Generated, ignored Python caches are excluded from text privacy scanning, but
  tracked cache files are rejected. Git failures are not treated as successful
  identity/cache verification. Published evidence files remain fully manifest-checked.

Final checks on the published tree: **32 Linux selftests pass; 11 Windows hypot
verifier/receipt tests and six Windows publication tests pass.** The complete
validator accepts seven historical unary receipts and one restricted hypot bundle,
with checksum and privacy checks; all commands exit zero. Historical receipts were
not changed, and the numerical qualification was not rerun after documentation,
validator and test-only corrections. Its executed hashes still match the sealed tools.

Measured qualification cost: **15.502801 child CPU-seconds, 2.4467207 parent
CPU-seconds, 48.944526389 wall-seconds**. Private accounting additionally includes
conservative test/review-client/publication overhead. There is no full-corpus,
coverage, completeness, novel-case, new-defect or imported-archive claim.
