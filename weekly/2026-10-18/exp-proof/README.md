# Reproduce the conditional exp checks

Use a disposable directory, Gappa 1.8.2, Sollya with MPFI and MPFR/GMP development
headers. Copy the pinned implementation's `src/binary64/exp/exp.c` alongside the
two C drivers. The implementation/proof pins and source hashes are in the receipts.
Keep all compiler floating-point options exactly as shown; do not use fast-math.

```
gcc -O3 -frounding-math -ffp-contract=off -march=x86-64 exp_tables.c -lmpfr -lgmp -lm -o tables
./tables
gcc -O3 -frounding-math -ffp-contract=off -march=x86-64 f2s-direction.c -lmpfr -lgmp -lm -o direction
./direction
sollya --warnonstderr accurate.sollya
gappa faithful-ne.g
gappa faithful-zr.g
gappa faithful-up.g
gappa faithful-dn.g
gappa reduction-ne.g
gappa reduction-zr.g
gappa reduction-up.g
gappa reduction-dn.g
```

Each child should have a 180-second timeout; a 15-minute overall limit suffices
on the qualified configuration. Conditional goals succeeding says nothing about
an unverified source-level hypothesis. Original `generated-*.g` files are retained
for comparison; they contain the old directed-rounding model mismatch.

`python3 generate-faithful.py` writes `generated.g` with the placeholder `RND`.
Replace that literal by ne,zr,up,dn in four copies to reproduce `faithful-*.g`.
The tested patch changes only the FastTwoSum low-part expression and its hint.
`verify_arithmetic.py PATH/TO/exp.c` checks the saved Gappa bounds using exact
rationals, regenerates the derivative bound from the C coefficients, and checks
the displayed error sum with 90-digit decimal arithmetic. It checks the saved
evidence; rerun Gappa to independently reproduce those bounds.

Table checks enumerate 64×64×4 combinations with outward MPFR 256 enclosures.
The endpoint driver also reports reduction/scaling boundary values. These finite
checks and conditional inequalities do not establish historical hard-case
completeness or the full correct-rounding theorem. See the parent source review.
