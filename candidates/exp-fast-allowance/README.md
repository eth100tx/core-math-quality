# exp: align the fast-path allowance with its manuscript

**Historical F01 rechecked; tested candidate, not a new discovery.** Input row
`0x1.5a3a157335f3bp+9` under round-toward-zero incorrectly returns `0x1.ffdebdc4e28acp+998` in
the contraction-off GCC/Clang builds; the correct result is
`0x1.ffdebdc4e28abp+998`. The value is one ulp too large; RN/RU/RD pass. The row is absent from the pinned exp corpus.
The upstream manuscript already identifies this failure. The new database
rewrite did not remove it from the primary configuration.

The C allowance remains `1.64e-19`; the manuscript analyzes `0x1.27p-62`.
This patch adopts the documented allowance, routing the witness to the accurate
path. It passes the full pinned exp corpus and 2,335 focused rows in all four
modes, GCC 13.3/Clang 18 x86-64-v3, contraction off and enabled. Current
contraction-enabled builds already pass this witness; this does not establish
their universal correctness. The original contraction-off extra-input runs
abort at this witness; their unvisited suffix is not counted as passing.

The manuscript still has exactness, domain and hard-case completeness
obligations listed in the [source review](../../weekly/2026-10-18/SOURCE-REVIEW.md).
Matching one documented allowance is not a complete proof of the Ziv test.
The larger allowance (approximately 2.50e-19 versus 1.64e-19) may route more inputs
to the accurate path; performance impact was not measured.

[Patch](fix.patch) · [Witness row](witness.wc) ·
[Focused receipts](../../weekly/2026-10-18/SUPPLEMENT.json) ·
[Unchanged-binary replay](../../weekly/2026-10-18/witness-replay/receipt.json).

Base implementation: `dae5dd8c0d5bd2691b45de28c9edbe12f067c3d3`.
Apply `fix.patch` only to a disposable checkout at that revision. The patch has
not been submitted or merged by this workbench. Reproduce with the baseline and
`python3 weekly/2026-10-18/reproduce_focus.py` as described in the
[weekly report](../../weekly/2026-10-18/REPORT.md). Exact source/patch hashes are
in [PATCH-BINDINGS.json](../../weekly/2026-10-18/PATCH-BINDINGS.json).
Tests are finite evidence, not a full-domain correctness proof.
