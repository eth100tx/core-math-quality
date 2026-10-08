# asinpi: one domain-error coverage witness

**State: accepted upstream; verified October 8.** The upstream corpus at
`84674bfadb0f920614355024c87a3eef73f2d938` includes the witness and passes the
full four-mode GCC checks with 258/258 lines and 76/76 arcs.
[Pickup verification](../../weekly/2026-10-08/REPORT.md).

The original candidate and before/after evidence below remain a historical
reproduction at the earlier base. Do not apply this patch again to current upstream.
This is a test-suite improvement, not a newly discovered implementation defect.

Base: `e78b460c41e5e155f45a5ff824140b81c84f55cc`.
Add the single row `0x1.8p+0` to `src/binary64/asinpi/asinpi.wc`.
It represents 1.5; the unchanged upstream checker also tests -1.5 because
`WORST_SYMMETRIC` is enabled. The row/value is absent from the pinned corpus.

At [asinpi.c:517](https://gitlab.inria.fr/core-math/core-math/-/blob/e78b460c41e5e155f45a5ff824140b81c84f55cc/src/binary64/asinpi/asinpi.c#L517),
`e == 0 && m == 0` recognizes exactly +/-1. Inputs with
1 < |x| < 2 have `e == 0` and `m != 0`, exercising the missing second-condition
false outcome. This is a normal domain-error path: the expected result is NaN,
with invalid raised and errno EDOM. The upstream MPFR checker validates the
result, supported exception flags and errno in all four rounding modes.
The branch interpretation comes from inspecting the source condition; the
before/after measurement shows that this row newly hits arc index 3.
The checker's EDOM requirement for a normal input producing a domain NaN is
explicit at [check_worst_uni.c:369](https://gitlab.inria.fr/core-math/core-math/-/blob/e78b460c41e5e155f45a5ff824140b81c84f55cc/src/binary64/support/check_worst_uni.c#L369).
Upstream may prefer this domain case in its special-test harness; the `.wc`
addition is a suggestion for optional pickup, not a required corpus convention.

| Primary GCC x86-64, errno on | Original corpus | With one row |
|---|---:|---:|
| Corpus rows | 58411 | 58412 |
| Accepted tests per mode/build, including signs | 116822 | 116824 |
| Target lines hit/total | 258/258 | 258/258 |
| Target arcs hit/total, four-mode union | 75/76 | 76/76 |

Both complete corpora pass separate O3 regression and O0 coverage builds in all
four modes, with strict floating-point flags. Only the corpus changed; source,
checker and toolchain remain identical. Raw per-mode outcomes are retained;
union coverage is not a claim that each individual mode covers every branch.
Full coverage here does not prove correct rounding or cover excluded profiles.

## Apply or reproduce

Apply [the patch](asinpi.wc.patch) in a disposable upstream checkout at the base:

```sh
git apply --check /path/to/asinpi.wc.patch
git apply /path/to/asinpi.wc.patch
```

Or, from the workbench root:

```sh
timeout --kill-after=10s 15m python3 candidates/asinpi-domain-witness/reproduce.py
```

The reproduction downloads/verifies the pinned public source, uses disposable
copies under `.work/`, and reruns before/after. It neither edits the source cache
nor writes upstream. Source-derived patch context remains under the upstream
source's license; the workbench license does not replace upstream notices.

[Before/after receipts](evidence/checks.json), [artifact hashes](evidence/SHA256SUMS.json),
and [release review](../../weekly/2026-10-06/RELEASE-REVIEW.md).
