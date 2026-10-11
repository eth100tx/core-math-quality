# Sine: errno-enabled build fix

Tested and independently reviewed; accepted upstream. Base: `74fcd1094a316164c94481f40f5c9658439bee63` (also tested on `84674bfadb0f920614355024c87a3eef73f2d938`).

The tiny branch names its absolute-bit variable `au` but tests the undeclared `ax`. GCC and Clang reject errno-enabled builds. The one-word fix compiles and passes the full pinned corpus in all four modes, including the upstream checker's exception/errno checks. No new rounding failure is claimed.

Apply `git apply fix.patch` in a checkout at the base. [Full review and evidence](../../weekly/2026-10-08/REPORT.md).

Accepted upstream: the current source matches the October8 tested candidate bytes. [October11 verification](../../weekly/2026-10-11/REVIEW-INVENTORY.json).
