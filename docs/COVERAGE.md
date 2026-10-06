# Coverage that can be compared and acted upon

The baseline measures the target `<function>.c` translation unit with GCC
`-O0 -g --coverage` and strict floating-point options. Correctness replay uses
a separate uninstrumented `-O3` build. Both use the same pinned upstream checker
and complete `.wc` corpus. No `-fopenmp` is passed and the disable macro is also
set. Four modes run sequentially with
fresh counters. The union sums counters with identical identities; it never
mixes errno, compiler, ISA or optimization profiles.

The denominator is executable lines and gcov branch outcomes emitted for that
compiled configuration. Preprocessor-excluded code is not in it. Inlined header
helpers are listed as other instrumented files but excluded from the target-file
headline and ranking; they require a separate helper audit. This is not whole-call-
graph coverage. GCC instrumentation and line attribution are not C source semantics.

## Ranking

Exclude only functions with **zero missing lines and zero missing arcs**. Sort
the remaining measured functions lexicographically by missing lines, then missing
arcs, then function name. A function with no missing lines but missing arcs is
eligible. Publish both counts rather than adding unlike units.

Rank only inside one run/profile. If any requested function is unmeasured, label
the ranking partial; the top is best **among measured functions**, not all 25.
This rule identifies a small measured gap, not necessarily the easiest proof.
Once selected, hold the active target until closed or explicitly deferred.
Only a complete 25-function census produces the automated recommendation;
subset tables remain scoped to their explicitly listed selection. A function
with FAIL is excluded from ranking and requires candidate investigation.

## Inspect a target

Use the immutable source pin, source/corpus hashes and raw per-mode gcov JSON.
Line keys are `(function_name, line_number)` and branch keys add the gcov branch
index on that line. Record GCC/gcov identity and JSON format version. These keys
must not be compared directly across compiler or source changes. Branch indices
need manual source/control-flow interpretation before recommending a patch.

Classify each gap separately:

| Classification | Required evidence | Action |
|---|---|---|
| Reachable, missing witness | Concrete input + mode; hit under pinned profile | `.wc` candidate, regression replay |
| Mode/configuration-specific | Per-mode and per-configuration counts | Explain; do not call dead code |
| Tool/optimization attribution | Source/disassembly or cross-profile evidence | Retain raw counts, annotate |
| Defensive/unreachable under stated preconditions | Explicit arithmetic/control-flow argument and independent review | Optional removal/simplification candidate |
| Unresolved | A search found no witness, or argument incomplete | Leave open; absence of hits is not proof |

Keep these annotations in a separate reviewed table. **Never subtract reviewed
unreachable gaps from raw measured totals.** A coverage improvement must rerun
the old and augmented corpus on the same profile and verify that correctness,
flags and errno still pass. Report per-mode gaps as well as the union: 100% union
does not mean every mode covers everything.

## Closure

Close a target when every measured gap has a reviewed disposition, with added
witnesses tested or an explicit justified code change. State whether closure is
measured 100%, a reviewed unreachable classification, or a mixture. Only upstream
acceptance closes a proposed patch as adopted; publishing here is not acceptance.

Reference: [GCC gcov options and JSON format](https://gcc.gnu.org/onlinedocs/gcc/Invoking-Gcov.html).
