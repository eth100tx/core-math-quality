# Patch and witness candidates

| Candidate | Type | State |
|---|---|---|
| [log2 sign step](log2-sign-step/README.md) | Source equivalence | Proposed; GCC/Clang tested; no public wrong-value witness |
| [sinh mask width](sinh-mask-width/README.md) | Restore int64_t | Proposed; GCC/Clang tested |
| [exp derivative bound](exp-derivative-bound/README.md) | Proof calculation | Proposed; exact coefficient bound and corrected sum checked |
| [sine errno name](sin-errno-name/README.md) | Build fix | Accepted upstream; byte-verified October11 |
| [sine proof references](sin-proof-models/README.md) | Three model corrections | Accepted upstream; byte-verified October11 |
| [asinpi domain witness](asinpi-domain-witness/README.md) | One .wc row | Accepted upstream; regression/coverage refreshed October11 |

Each directory records the exact base and limits. Apply patches only to a
disposable checkout at the stated base. The workbench never pushes upstream.
Its MIT license does not replace upstream rights in source-derived hunks.
