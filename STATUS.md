# Current status

**October 26: the restricted hypot certificate verifier and Linux adapter are
implemented and qualified on 18 fixtures in four modes under GCC/Clang.**
[Qualification and limits](docs/HYPOT-QUALIFICATION.md). No full-corpus/search,
completeness or imported-archive claim; the missing transfer package remains open.

**October 25: the previously reported exp value error and rsqrt underflow-flag
regression are fixed in the tested master revision. A focused asin corpus check
also passes; broader source/proof review remains incomplete.**

- [Latest scoped report](weekly/2026-10-25/REPORT.md), [per-file pending work](weekly/2026-10-25/SOURCE-REVIEW.json).
- [Next three improvements](IMPROVEMENTS.md): exp proof/code binding, asin portability, and hypot certificate/runner qualification. The [first certificate specification](docs/HYPOT-CERTIFICATE-SPEC.md) is a design artifact, not an executed bivariate campaign.
- exp/rsqrt: GCC 13.3 and Clang 18.1.3 baseline x86-64, four modes, contraction off, errno enabled; finite tests, not correctness proofs.
- asin: new Clang baseline full-corpus regression passes; cast/range/portability analysis remains open.
- Routine coverage work is **paused**. exp10 remains parked; October 18 measurements retain their original date and scope. No new ranking.
- Both source patches and witness rows are now upstream; [candidate adoption status](candidates/README.md). The conditional exp proof-model proposal remains unadopted.
- [Hypot pilot proposal—not run](docs/BIVARIATE-PILOT.md); bivariate import and separate qualification remain pending. [Weekly index](weekly/README.md).
