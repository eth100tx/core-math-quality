# Patch and witness candidates

| Candidate | Type | State |
|---|---|---|
| [asin unsigned gap](asin-unsigned-gap/README.md) | Optional portability cleanup | Tested GCC/Clang, four modes; no demonstrated wrong-answer bug; not yet upstream at the selected pin. |
| [rsqrt reciprocal range](rsqrt-underflow-range/README.md) | Spurious-underflow regression | Adopted upstream; [October 25 verification](../weekly/2026-10-25/REPORT.md). Candidate directory preserves historical evidence. |
| [exp fast allowance](exp-fast-allowance/README.md) | Historical wrong-value failure | Adopted upstream; [October 25 verification](../weekly/2026-10-25/REPORT.md). Candidate directory preserves historical evidence. |
| [exp FastTwoSum model](exp-fasttwosum-model/README.md) | Directed-rounding model correction | Four corrected Gappa certificates; conditional, not full correctness |
| [log2 sign step](log2-sign-step/README.md) | Source equivalence | Semantic correction accepted upstream; October 18 verified |
| [sinh mask width](sinh-mask-width/README.md) | Restore int64_t | Accepted upstream; October 18 verified |
| [exp derivative bound](exp-derivative-bound/README.md) | Proof calculation | Corrected bound adopted upstream; current hull bound rechecked |
| [sine errno name](sin-errno-name/README.md) | Build fix | Accepted upstream; October 11 verified |
| [sine proof references](sin-proof-models/README.md) | Three model corrections | Accepted upstream; October 11 verified |
| [asinpi domain witness](asinpi-domain-witness/README.md) | One .wc row | Accepted upstream; October 11 verified |

Each directory records the exact base and limits. Apply patches only to a
disposable checkout at the stated base. The workbench never pushes upstream.
Its MIT license does not replace upstream rights in source-derived hunks.
