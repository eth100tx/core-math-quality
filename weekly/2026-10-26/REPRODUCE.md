# Reproduce this focused review

Use a qualified Linux x86-64 profile from the runbook. Python 3.10+, GCC/Clang,
MPFR/GMP development files and Gappa 1.8.2 were used. Do not run with Python
optimization (`-O`), which disables the certificate assertions. Run one science
task at a time under the operator's monitor and time/CPU budget. The scripts
refuse an existing output directory instead of mixing runs.

From the repository root, acquire the blob-verified source:

```sh
python3 -B quality.py fetch --pin 336752ca18e1204321225ec90c1f43fcb90ada1b --functions sin,asin,hypot
python3 -B quality.py doctor --profile gcc-linux-x86_64
python3 -B quality.py doctor --profile clang-linux-x86_64
```

The supplied regression scripts use fresh directories under `.work/candidates`,
the repository's shared lock and doctor, strict flags and bounded children:

```sh
timeout --kill-after=10s 30m python3 -B weekly/2026-10-26/replay_sine.py
timeout --kill-after=10s 25m python3 -B weekly/2026-10-26/replay_asin_hypot.py
```

Full corpus/sign/mode results are in `SINE-REPLAY.json` and
`ASIN-HYPOT-REPLAY.json`. The latter includes deliberately failing sanitizer
controls; only those named controls are expected to return nonzero.
The hypot timing is a separate illustrative harness, not replacement
qualification for `hypot_run.py`.

Regenerate the exact polynomial certificate and replay the Gappa goals:

```sh
python3 -B weekly/2026-10-26/certify_polynomials.py .work/sources/336752ca18e1204321225ec90c1f43fcb90ada1b/src/binary64/sin/sin.c .work/new-polynomials.json
python3 -B weekly/2026-10-26/check_gappa.py weekly/2026-10-26/acclarge-upstream.g .work/new-gappa gappa
```

`acclarge-upstream.g` is the unmodified proof file from
[proof commit d0fc1625](https://gitlab.inria.fr/zimmerma/core-math-proofs/-/blob/d0fc1625fd88f9987bc89c83e271b39b8201b7f7/sin/acclarge.g).
Download `sin/sin.tex` from that same commit to `.work/sin.tex` to run the
coefficient/model checks. The expected TeX and Gappa SHA-256 values are recorded
in `bindings.json`; verify them before use.

```sh
python3 -B weekly/2026-10-26/check_bindings.py .work/sources/336752ca18e1204321225ec90c1f43fcb90ada1b/src/binary64/sin/sin.c weekly/2026-10-26/acclarge-upstream.g .work/sin.tex .work/new-gappa .work/new-polynomials.json .work/new-bindings.json
python3 -B weekly/2026-10-26/hypot_domain.py .work/new-polynomials.json .work/new-hypot-domain.json
python3 -B weekly/2026-10-26/check_asin_predicate.py .work/new-asin-predicate.json
```

`compare_components.py` accepts the previously verified October 8 source,
current source, binding receipt and a destination. It checks seven unchanged
full definitions, five supporting type/macro definitions and that the new error
allowance is tighter. It does not
redownload or independently validate the historical source pin; use the
blob-verified cache and recorded source hashes.

```sh
python3 -B quality.py fetch --pin 74fcd1094a316164c94481f40f5c9658439bee63 --functions sin
python3 -B weekly/2026-10-26/compare_components.py .work/sources/74fcd1094a316164c94481f40f5c9658439bee63/src/binary64/sin/sin.c .work/sources/336752ca18e1204321225ec90c1f43fcb90ada1b/src/binary64/sin/sin.c .work/new-bindings.json .work/new-components.json
```

The binding receipt keys use the supplied file names; compare the source hash
values rather than requiring identical keys when renaming input files.

Receipt contents bind source/profile/tool inputs and record CPU time. Timings,
environment versions and log formatting can differ on another machine; do not
compare regenerated JSON bytes as a scientific success criterion. Compare
the exact mathematical inequalities and named successful checks instead.
`SHA256SUMS.json` seals the delivered bytes. No corpus-generation completeness,
new bug or publication-novelty claim follows from a successful replay.
