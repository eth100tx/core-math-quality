# exp proof generator: preserve directed rounding of the low part

**Verified helper/model mismatch; corrected conditional certificate.**
Base proof revision: `5a42d3fb72533077c8b745b9fcd39b84ad3ee92a`, file `exp/generate.py`.
The old model uses `-rnd(h-(a+b))`; C requires `rnd((a+b)-h)` when h−a is exact.
Negating a directed-rounded quantity is not equivalent to rounding its negative.
At a=1,b=2^-154 in RU, C's low part is `-0x1.fffffffffffffp-53`, versus
`-0x1p-52` in the old model. A separate downward example is also recorded.
These are helper-model examples, not public exp inputs demonstrating wrong values.

[The patch](fix.patch) corrects the expression and its exact algebraic hint.
Four Gappa 1.8.2 runs on the corrected generator still establish
error<2^-101.191 and |yl|<2^-49.883 under the stated hypotheses. Source-level
exactness premises, full hard-case completeness and contraction-enabled
evaluation trees are not certified by these runs. The mismatch predates this
week's proof extension; it was identified in this review.

Apply only to a disposable proof checkout at the stated base. Run the generator
for ne,zr,up,dn, then Gappa on each generated file. The exact models, outputs,
C/MPFR direction test and [receipt](../../weekly/2026-10-18/exp-proof/faithful-receipt.json)
are in [exp-proof](../../weekly/2026-10-18/exp-proof/). The
[source review](../../weekly/2026-10-18/SOURCE-REVIEW.md) states the remaining
proof obligations. This candidate has not been submitted or merged by this workbench.
