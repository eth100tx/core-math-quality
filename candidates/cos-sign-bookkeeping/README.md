# Cosine sign bookkeeping follow-up

Proposed proof-only correction against `d5fab2e483d00b7a21c5b50b1abb877cadeb5c5b`.
[Patch](cos-sign-bookkeeping.patch), [metadata](METADATA.json),
[reconciliation](../../weekly/2026-10-30/REPORT.md).

The printed swap-bit definition `q+sigma_r=0` misses `(q,sigma_r)=(1,1)`.
Use equality `q=sigma_r`, then state the total sign as `(b+q+d) mod 2`.
The half-turn factor alone is `(-1)^b`; the final `sigma` includes other flips.
C already handles these cases. This is not a demonstrated binary64 value failure.

Apply with `git apply --check` and `git apply` in a disposable proof checkout
at the exact base. Patch application and 24 exact sign-algebra cases are checked;
full LaTeX build and a whole-function proof are not claimed. No upstream PR made.

[24-case receipt](../../weekly/2026-10-30/SIGN-CHECK.json) and
[standalone reproducer](../../weekly/2026-10-30/check_sign.py).
