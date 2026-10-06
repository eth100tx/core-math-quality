# Patch and witness candidates

No new patch is assumed merely because a coverage gap exists. Add a directory
per actual independently reviewed candidate, using `templates/PATCH.md` or
`templates/FINDING.md`. Keep the exact upstream base, minimal witness, patch,
before/after results and review together. Preserve original license notices for
source-derived hunks. Upstream uses its own license; this workbench's MIT license
does not remove source copyright obligations.

Maintainers can download/apply a candidate in a disposable checkout whenever
useful. This repository never pushes changes into CORE-MATH automatically.
