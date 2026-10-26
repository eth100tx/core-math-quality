# Current status

**October 26 follow-up: the scaled sine kernel passes exact polynomial/Gappa checks and full normal/forced GCC/Clang corpus runs; an optional asin portability patch passes; the restricted hypot domain cost is quantified.**
[Focused report and limits](weekly/2026-10-26/REPORT.md). Exp and routine coverage are paused.

**October 26: the restricted hypot certificate verifier and Linux adapter are
implemented and qualified on 18 fixtures in four modes under GCC/Clang.**
[Qualification and limits](docs/HYPOT-QUALIFICATION.md). No full-corpus/search,
completeness or imported-archive claim; the missing transfer package remains open.

**October 25: the previously reported exp value error and rsqrt underflow-flag
regression are fixed in the tested master revision. A focused asin corpus check
also passes; broader source/proof review remains incomplete.**

- [October 25 fix report](weekly/2026-10-25/REPORT.md), [prior per-file pending work](weekly/2026-10-25/SOURCE-REVIEW.json); [October 26 scoped follow-up](weekly/2026-10-26/REPORT.md).
- [Next three improvements](IMPROVEMENTS.md): sine proof/code binding, asin portability, and bounded hypot certificates. Exp work is paused from October 26. The [first certificate specification](docs/HYPOT-CERTIFICATE-SPEC.md) is a design artifact, not an executed bivariate campaign.
- exp/rsqrt: GCC 13.3 and Clang 18.1.3 baseline x86-64, four modes, contraction off, errno enabled; finite tests, not correctness proofs.
- asin: the new unsigned-gap candidate and original-source sanitizer corpus checks pass GCC/Clang; whole-function range preconditions and Windows/32-bit qualification remain open.
- Routine coverage work is **paused**. exp10 remains parked; October 18 measurements retain their original date and scope. No new ranking.
- Both source patches and witness rows are now upstream; [candidate adoption status](candidates/README.md). The conditional exp proof-model proposal remains unadopted.
- [Hypot pilot proposal—not run](docs/BIVARIATE-PILOT.md); prior-archive import remains pending; restricted Linux qualification is complete. [Weekly index](weekly/README.md).
