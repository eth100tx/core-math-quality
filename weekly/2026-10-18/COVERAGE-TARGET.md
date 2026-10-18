# One active target: exp10

The complete 25-function census selects exp10: zero missing lines and one
missing arc, tied with exp2 and first alphabetically under the published policy.
The exact raw arc is `["as_exp10_database",180,1]`, the false exit of the
three-neighbor loop. Line/arc totals are 135/135 and 51/52.

The loop is entered only when x matches one of 49 exact database keys. For a
given helper argument f, let F be its binary64 bit pattern and p the stored
two-bit residue. The candidates F−1,F,F+1 cover three consecutive residues
modulo 4. Exhaustion occurs exactly when p=(F+2) mod4. An arbitrary synthetic f
can satisfy that condition; calling the helper artificially is not a public
coverage witness.

All 49 keys were passed through the unchanged public checker in all four modes,
observing helper entry with a debugger. Each public call was repeated by the
upstream checker as part of its flag/errno tests. Every observed pair (x,f)
excludes exhaustion, and the O3 production and O0/gcov argument multisets agree.
The copied executable hashes match the original baseline executables. MXCSR
rounding modes and FTZ/DAZ were checked. The original coverage counters were
protected by redirecting debugger-run gcov output into a separate directory.

This finite necessary-trigger argument excludes the exit for the two measured
GCC 13.3 binaries at the pinned source. It is not a portable arithmetic proof
over all conforming compilers or contraction trees. No new .wc row is proposed.
**Retain exp10 as active; portable closure is deliberately deferred.** The next
step is to certify the caller's f residue for these 49 exact keys and four modes
against a specified floating-point evaluation model, then reconcile the models
of other supported compiler profiles. Do not launch an open-ended input search.

[Production receipt](exp10-capture/production-capture/receipt.json),
[coverage receipt](exp10-capture/coverage-capture/receipt.json),
[offline verifier](verify_exp10_capture.py).

The previous exp target is closed for this coverage profile because upstream
removed the old loop. Its replacement has 117/117 lines and 32/32 arcs covered;
that does not prove the deleted path was unreachable.
