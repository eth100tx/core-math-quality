# Reproduce this focused review

Use the Linux/WSL configuration documented in the workbench, with Python3,
GCC/Clang, MPFR/GMP development headers and Gappa1.8.2. This follow-up did not
qualify a new machine or platform. Run one science job at a time under a bounded
foreground runner. The workbench's ordinary corpus command is:

```
python3 quality.py run --pin 84674bfadb0f920614355024c87a3eef73f2d938 --functions sin --errno 0 --profile gcc-linux-x86_64 --run-id oct8-sin-original --max-minutes 30
```

The original errno-enabled compile fails; `sin-errno-name.patch` applies to a
separate copy at that pin. Never modify the verified download cache. The `runs/`
cell records contain the exact commands, flags, inputs' hashes and mode logs for
the candidate and targeted corpora. Run the same upstream checker against a
candidate copy and the provided boundary corpus to replay the candidate checks.
Use `-ffp-contract=fast -march=x86-64-v3` for the separately recorded FMA runs.
The target corpus contains 109638 rows; WORST_SYMMETRIC checks both signs.

From this dated directory, the certificate sequence is:

```
python3 fetch_source.py
python3 distance_certificate.py
python3 verify_distance.py
python3 reducer_certificate.py
python3 exact_polynomials.py
python3 cos_certificate.py
gcc -O2 -frounding-math -ffp-contract=off -march=x86-64 table_checks.c -lmpfr -lgmp -lm -o tables
./tables
python3 verify_models.py /path/to/gappa-1.8.2
python3 new_interval_certificate.py
```

The last step replays the mathematical suffix bound and checks its containment
and the saved test records; rerunning it alone does not rerun the MPFR tests.
`verify_models.py` has both a 30-minute overall cap and 180-second per-goal caps.
It writes new logs under replay-logs; compare these with the saved logs. It
does not trust a PASS word as a substitute for a successful tool exit.

To repeat the semantic membership check against the complete original corpus:

```
python3 fetch_source.py --corpus
python3 hardcase_suffix.py
```

The corpus download is large. If the workbench already has the pinned verified
corpus, copy it into `candidate-source/src/binary64/sin/sin.wc` first; the fetch
helper checks its recorded hash. Numeric equality matters: `...ef0p-26` and
`...efp-26` encode the same input. All eight isolated cases are already present.

`SHA256SUMS.json` covers every delivered file in this dated directory except
itself. Keep original evidence immutable; replay in a disposable copy. Original
and corrected Gappa models are both retained for comparison; the mathematical
closure uses the corrected reference goals and the expanded range goals.
See MATH-NOTE.md for the theorem dependencies and the historical hard-case
search scope that these commands do not reproduce.

The latest source pin is `74fcd1094a316164c94481f40f5c9658439bee63`.
Use `sin-errno-name-latest.patch` for that pin. `LATEST-RESULTS.json` records
its fresh GCC full-corpus and coverage replay; the exact certificate scripts
fetch the PDF-cited pin, and QA verifies the only executable sine difference
is removal of the proved-unreachable arm. The `runs/**/cell.json` files are
individual focused checker receipts, not ordinary full-run result manifests.

All 95 saved goal files have explicit successful exit receipts; one small-path
file duplicates an earlier pilot and is not an independent theorem. Internal
QA imports the workbench coverage validator; the commands above provide the
standalone ZIP replay route.
