# Cosine proof errata candidate

**October 30: partially adopted at proof `d5fab2e483d00b7a21c5b50b1abb877cadeb5c5b`.**
Keep the original patch as dated evidence; do not reapply it wholesale to current
upstream. [Reconciliation](../../weekly/2026-10-30/REPORT.md) distinguishes active
text from commented proposals. A [small sign-bookkeeping follow-up](../cos-sign-bookkeeping/README.md)
addresses the revised paragraph; completeness and fallback obligations remain open.

This is a proposed document patch against proof commit
`df593398ddd877cdc00fd1684d9dea814928f28b`, not a change to `cos.c`.
[Patch](cos-proof-errata.patch), [metadata](METADATA.json),
[review, tests and limits](../../weekly/2026-10-29/REPORT.md).

It aligns LargePath and the sign narrative with C, states the accurate reducer's
small-input extension, describes the actual exception guard, and corrects the
classification/example in the near-zero census discussion. The measured corpus
minimum is explicitly scoped to supplied inputs. The patch does not certify
exhaustive search completeness or claim a fully closed correctness proof.

Apply only to a disposable checkout at the stated proof base:

```sh
git apply --check /path/to/cos-proof-errata.patch
git apply /path/to/cos-proof-errata.patch
```

Patch application and resulting bytes are checked. A full LaTeX document build
with the upstream bibliography/figures is not claimed. No upstream push, issue
or pull request was made. Source-derived hunks retain their upstream rights.
