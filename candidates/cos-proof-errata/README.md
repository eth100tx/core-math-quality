# Cosine proof errata candidate

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
