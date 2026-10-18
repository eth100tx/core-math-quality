# Current status

**October 18: all 25 pinned corpora pass, but supplementary checks confirm a new
rsqrt underflow-flag regression and the known exp wrong-value failure.**

- [Latest report](weekly/2026-10-18/REPORT.md), [raw missing-line/arc census](weekly/2026-10-18/MISSING-COVERAGE.json).
- GCC 13.3 x86-64, errno on, four modes; 19/25 target files have no measured gap.
- exp's new database has full measured coverage. **Active: exp10**, 0 missing lines/1 missing arc. Finite trigger set excludes the exit in measured O3/O0 binaries; portable closure remains open.
- Two tested source patches and one corrected conditional proof model are [proposed](candidates/README.md). Last week's log2/sinh corrections and exp derivative bound are upstream.
- [Proof obligations](weekly/2026-10-18/SOURCE-REVIEW.md), [hypot pilot proposal—not run](docs/BIVARIATE-PILOT.md), [weekly index](weekly/README.md).
