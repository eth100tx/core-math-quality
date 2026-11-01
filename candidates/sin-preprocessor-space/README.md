# Sine preprocessing correction

**Tested build fix, not yet adopted at implementation
`5f65574e2b3631fb31e9b88dd27782a936c68095`.**

`src/binary64/sin/sin.c:278` says `#if1`. GCC 13.3 and Clang 18.1.3 reject this
as an invalid preprocessing directive, then reject the unmatched `#else` and
`#endif`. [The patch](sin-preprocessor-space.patch) inserts one space, selecting
the previous multiplication expression. The alternative FMA sequence remains
inactive. This is a source build failure, not a compiler miscompilation or a
wrong-value witness.

On disposable copies, the old revision, broken revision and corrected revision
were compiled with both strict baseline x86-64 configurations. Old and corrected
sources compile; the broken source fails. The corrected and old preprocessor
outputs match under the recorded token comparison. The pickup patch is also
applied to the pinned bytes and required to match the compiled fixed source's
SHA-256 in [verification](../../weekly/2026-11-01/VERIFICATION.json). No new numerical
campaign is claimed for the patch.

[Receipt](../../weekly/2026-11-01/sine-build.json) ·
[reproduction driver](../../weekly/2026-11-01/reproduce_build.py) ·
[reviewed report](../../weekly/2026-11-01/REPORT.md).

Apply only to a disposable copy of the stated pin, for example with
`git apply --check` followed by `git apply`. The upstream source remains under
its existing MIT license and copyright notice, which this patch does not change.
No upstream push, issue or pull request was made by this workbench.
