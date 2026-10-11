# Current status

**All25 selected functions pass the October11 GCC regression. Three small
source/proof corrections are proposed; no new public wrong-value witness.**

- [Latest weekly report](weekly/2026-10-11/REPORT.md), [full missing-line/arc census](weekly/2026-10-11/MISSING-COVERAGE.json).
- Baseline `81a899d67953a619d703660fd9630f0554673524`, GCC13.3 x86-64, errno on, four modes, O3 regression/O0 coverage. 17/25 target files have no missing lines/arcs.
- One active coverage target: **exp**, 0 missing lines/1 missing arc. Finite exception-key replay complete; portable unreachability deliberately deferred.
- [Candidates](candidates/README.md): log2 sign equivalence, sinh mask width, exp proof derivative term. Earlier sine fixes and asinpi witness are accepted upstream.
- Coverage rises largely because upstream removed predicates; this is not new testing of deleted paths or a universal correct-rounding proof.
- [Source review and open obligations](weekly/2026-10-11/SOURCE-REVIEW.md), [weekly index](weekly/README.md), [supported configurations](docs/CONFIGURATIONS.md).
