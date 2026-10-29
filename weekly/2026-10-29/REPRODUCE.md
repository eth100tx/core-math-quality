# Reproduce the focused cosine checks

Use a qualified Linux x86-64 workbench and read the root AGENTS/RUNBOOK first.
Keep one science runner, bounded outer jobs and explicit accounting. The input
pins are in PINS.json. Preserve the immutable download; compile only copies in
`.work/`. These are focused checks, not a full completeness census.

```sh
python3 -B quality.py fetch --pin 42b48ae76610f5baaf9773308f2424459f8c9309 --functions cos
python3 -B quality.py run --pin 42b48ae76610f5baaf9773308f2424459f8c9309 --functions cos --profile gcc-linux-x86_64 --run-id YOUR_UNIQUE_ID --max-minutes 20
python3 -B weekly/2026-10-29/replay_cos.py
```

The replay refuses to overwrite its output directory; use a fresh reviewed copy
with a unique output label if its default already exists. Its four configurations
are normal/forced accurate under GCC v3 contraction enabled and baseline Clang
contraction off. Use an outer 30-minute monitored cap.

For mathematical checks, use the downloaded `cos.c` and proof `cos/cos.tex` at
the pins above, with Gappa **1.8.2**. Do not replace it silently with system 1.4.1.

```sh
python3 weekly/2026-10-29/certify_polynomials.py COPIED_COS_C polynomials.json
python3 weekly/2026-10-29/check_gappa.py weekly/2026-10-29/acclarge-upstream.g NEW_GAPPA_DIRECTORY /path/to/gappa-1.8.2
python3 weekly/2026-10-29/check_bindings_cos.py COPIED_COS_C weekly/2026-10-29/acclarge-upstream.g PINNED_COS_TEX NEW_GAPPA_DIRECTORY polynomials.json bindings.json
python3 weekly/2026-10-29/certify_reducer.py COPIED_COS_C reducer-certificate.json
```

In a disposable build directory containing the copied `cos.c`, compile `tables.c`
and `reducer.c` individually with GCC `-O2 -frounding-math -ffp-contract=off
-march=x86-64`, linking `-lmpfr -lgmp -lm`. Each takes less than a minute on the
tested host; keep a two-minute child cap. `scan_boundaries.c` takes a corpus path;
compile with `-DPRECISION=256` and then `512` to reproduce the supplied-section
classification. Extract the section beginning `# additional inputs in [1,2^1024)`
from pinned `cos.wc`; it has 17,222 unique rows. Whole-corpus classification and
this added-section classification have different populations.

`census_controls.c` includes the proof repository's pinned `cos/check_k0.c`;
copy that unmodified file alongside it and link additionally with `-fopenmp`.
Its 1,024 bounded dyadic controls do not run the full-binade generator.

The published `TARGETED.json` preserves hashes and outputs for the diagnostic
exception run. Its test-only instrumentation records the low limb immediately
before `uint64_t d = (uint64_t)c1u + 5`; it changes no arithmetic. The full public
entry corpus remains the regression and coverage evidence.

Run `python3 validate.py` from the root for the standard receipt validation.
Verify SHA256SUMS.json for custom artifacts. Tests, conditional bound certificates,
patch application and all-input search completeness are separate evidence types.
