# Improve the workbench

Pick one named function, profile, generator, documentation gap or candidate.
Open an issue or propose a change in this independent repository. Do not contact
upstream automatically. Maintainers decide when to pick up candidates.

For runner changes, include a focused test for the failure mode and a small real
integration run. Changes to counts, profile flags, corpus selection or comparison
rules require new measurements and a versioned explanation. Preserve past weekly
evidence; corrections belong in an erratum or new run, not silent replacements.

For new platforms, follow `docs/CONFIGURATIONS.md`: untested profiles are
experimental. A portable-looking command is not a qualified configuration.

For scientific claims use the finding/patch/review templates. Make the command,
inputs, reference, result and limitations clear enough that another person or AI
can reproduce them without this chat. Independently review important claims.

Use a public-safe Git identity. Never add correspondence, credentials, absolute
machine paths, unrelated private reports or ignored downloads. Run selftests and
`python3 validate.py`, then inspect the exact staged diff. Keep authored files
under the workbench's MIT license and preserve any upstream notices.
