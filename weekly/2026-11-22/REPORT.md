# November 22 · tangent regression and reusable hypot evidence

The updated tangent implementation passes its full pinned corpus in four rounding modes on Clang 18. The transferred hypot table now has a self-contained independent replay. Clang's asin fast/off contraction settings produce identical objects for the tested build. These are scoped results, not a clean bill of health for the whole library.

### Tangent: upstream correction, passing regression

At implementation `333d11d04d73ef165cf217e773b3b3d6372aa66f`, the maintainer corrected `set_dd`: a shift-by-64 guard and a low-part exponent offset. The full **1,098,260-row** corpus and the checker's sign expansion produced **2,196,520 accepted tests per mode**, zero failures in all four modes. This used Linux baseline x86-64, Clang 18.1.3, contraction off, `-frounding-math`, errno support and the upstream inexact check. The receipt records the exact checker, flags and source hashes. Its built-in checks are not a separate exhaustive exception/errno qualification. Coverage and the special/random campaign were not run. We have not established whether the corpus reaches each corrected helper branch. [Runner receipt](runs/20261122-tan-clang/result.json)

### Hypot: table soundness, not a completeness census

All **160 supplied families**, at exponent gaps 24–26, pass exact non-tie checks within 2^-100 ulp of a midpoint. A changed row is rejected arithmetically, separately from digest rejection. Two separately implemented integer reference algorithms agree on **6,416 four-mode values**, representing 1,280 hard input pairs at one scale plus 324 format-boundary pairs. These expand 205 distinct unsigned unordered magnitude problems. Two additional exact midpoint controls exercise both tie parities. Neighbor location is independent; the exact midpoint decision formula is shared. This executes reference code, not CORE-MATH. The **323,428** canonical scale count is calculated from endpoints, without replaying all scales. Omitting a valid row still passes the inequalities: these tests cannot establish that the table is complete. [Reusable verifier and dependencies](../../candidates/hypot-compact-table/README.md) · [Detailed receipt](table-replay.json)

The compact archive lacks its native replay harness/raw receipt and adjacent-family census generator. Its historical Windows result is not current Linux qualification. Importing those missing pieces and regenerating completeness remain open. No bivariate bug or publication novelty is claimed.

### Asin: stop at equivalent compiled arithmetic

Clang 18.1.3 with x86-64-v3, `-O3 -frounding-math`, errno support and `-ffp-contract=fast` emits the same object bytes as `off`. The source hash is unchanged from November 15. The leading refinement sum and its residual remain separate multiply/add/subtract operations; there is no distinct contracted graph to certify in this build. P9 stops at its stated equivalence condition. **No new range certificate, library value run, flags or errno test was performed for asin.** The strict-model and GCC certificates retain their original assumptions. No new compiler defect was found. [Comparison receipt](clang-comparison.json) · [Reproducer and operation notes](REPRODUCE.md)

### Adoption, remaining scope and next work

All 32 previous ordered hypot rows remain in the current corpus. The asin signed-index comment and cosine sign correction remain present. This week's sine/cosine/sincos constant spelling change is exactly equal as an integer; sine proofs are unchanged and earlier numerical evidence retains its date. A new upstream atan2 corpus pair is inventoried but no stage-coverage comparison ran. The complete delta from the last full review contains **95 implementation paths and 28 proof paths**; unrelated detailed review stays deferred, including the earlier sincos rewrite and platform-specific changes. The global review watermarks do not advance. Exp and routine coverage remain paused. [Full path inventory, scoped dispositions and adoption](SOURCE-REVIEW.json)

| Next pickup | Deliverable and decision |
|---|---|
| 1 · Tangent conversion regression (P11) | Isolate the just-fixed `set_dd` shift/exponent boundaries. Deliver exact helper-level boundary cases, or state why they are not reachable through the public function. This is scoped regression work, not a duplicate of the maintainer's tangent proof. |
| 2 · Exact pow(x, 3/2) reference (P3) | Compare exact x³ with squared dyadic rounding boundaries on a bounded positive-normal sample, including a wrong-neighbor control. This has the next bivariate slot. |
| 3 · Hypot completeness dependencies (P12, blocked) | Recover the missing adjacent-family generator and raw census/native receipts; identify exact bounds and exclusions before proposing a bounded regeneration. Table replay alone cannot close this. No search is dispatched while dependencies are missing. |

P10 closes for supplied-table replay; P9 closes at the no-new-graph stop condition. These next items are planned or blocked work, not three tested patches. No upstream PR was opened. [Maintained roadmap](../../ROADMAP.md)
