# Evidence receipt contract (schema version 1)

`validate.py` is the executable field allowlist and consistency validator.
`quality.py export` validates the receipt before placing it in `weekly/`.

Each run records:

- Immutable upstream SHA, file SHA-256 and Git blob IDs
  checked against the pinned Git tree. Downloads use Git blob IDs. Optional
  acquisition archive hashes may be retained in seeded caches; resume keys on
  file identities, never gzip container bytes.
- Runner file SHA-256, resolved profile, all configuration hashes, environment
  probe, compiler/gcov and MPFR/GMP/libc versions.
- Selection, errno mode, exact flags, uninstrumented and coverage commands,
  return codes, bounded output, corpus rows and upstream-accepted count per mode.
- Per-mode target gcov JSON and four-mode union. Header/helper code is outside
  the target-file denominator. JSON format version and other file names are recorded.
- PASS, FAIL, INCOMPLETE or NOT_RUN, with errors and unperformed work visible.
  FAIL is a checker failure candidate, not yet a confirmed upstream defect.
- Child CPU time and wall time for the invocation. The operator records parent
  and AI overhead separately; resume accounting is append-only under `.work/`.

A result never contains email headers, credentials, environment dumps, hostname
or absolute workspace paths. Free-text compiler/test output is additionally
screened and manually reviewed. An allowlist does not make arbitrary text safe.

Each exported evidence directory has a SHA256SUMS.json enumerating every file.
No silent replacement of published evidence. A correction is a new run or
explicit erratum with the old report retained. Raw measured counts stay unchanged
when a separate reviewer classifies a gap as unreachable.

The workbench's Git commit in the reviewed report identifies the publication;
the runner hash in each receipt identifies exact executed code even before a
release commit exists. If those differ, the report must explain the change and
provide the executed source version or rerun with the final runner.
