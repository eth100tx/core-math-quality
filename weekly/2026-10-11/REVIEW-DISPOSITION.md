# Independent review disposition

Actual CLI metadata identifies **claude-opus-5-5** for the independent planning
and technical/mathematical reviews. The final review is the publication gate.
No Fable session was used. Advice was checked against source, exact arithmetic
and executed evidence rather than accepted on model authority.

- Retained a full comparable census because the owner requires that basis for
  global-smallest-gap selection and many priority functions changed. Old broad
  random/exhaustive campaigns were not repeated. Coverage changes from removed
  code are explicitly distinguished from new witnesses.
- Confirmed log2's +1/+3 expression independently by the two possible sign-bit
  values. Candidate restores +1/−1. No opposite-sign public witness was found
  in the listed checks; that is not an unreachability proof.
- Confirmed sinh's narrowing with an existing corpus input and exact integer
  bit arithmetic. Restoring int64_t is tested under GCC and Clang; extra routing
  is not labeled a numerical error or a measured timing regression.
- Rejected instrumentation-only or successful-return-only closure of the
  exp database loop. Captured actual helper arguments in unchanged baseline
  O3 and O0/gcov binaries, checked the ABI mapping in disassembly, and replayed
  every key in every mode. Offline residue checks and cross-binary argument
  comparison pass. The result is binary-specific; portable closure is deferred.
- Independently confirmed Q'(0)=1 and replaced the false derivative bound by
  an exact rational coefficient bound on an interval covering D and r.
  The review's rounded suggested exponent −116.48 was not used as an upper
  bound; the conservative −116.47 is justified by 1.0001<2^0.01.
- Expanded the exp reduction replay to all four modes both with and without
  dxll contraction: eight concrete Gappa goals pass. The exactness and lattice
  arguments were checked against the primary FastTwoSum paper. Cross-statement
  contraction, the `th==1` full-path obligation, subnormal FIXME and historical
  hard-case searches remain explicit limits.
- Reviewed early-exit range arguments for removed guards; retained the
  noncancellation, sticky-bit and sinh/cosh gap premises as unresolved where
  only bounded evidence is available. Shift sanitization is complementary
  evidence, not a substitute for the sinpi/cospi range argument.
- Verified prior sine fixes against the exact October8 candidate/model bytes.
  Resolved the collapsed full sine-text comparison by fetching its raw endpoints.
  Outside-25 source changes are inventoried and explicitly deferred.

- The independent runner review confirmed that the temporary parent signal
  mask must be restored in the child before exec. Its required stronger test
  establishes a known caller mask with SIGUSR1 blocked and SIGTERM/SIGINT
  unblocked. That test fails on old code directly and nested, and passes on
  the corrected code. Old numerical receipt identities are preserved; the
  validator checks recorded identities, not equality to the latest runner.

Final review: actual Claude Opus5.5 approved publication and the email after
four text corrections, all applied: close this disposition; state the exp/
exp2/exp10 tie and alphabetical tie-break; remove an unexplained old exponent;
and disambiguate the derivative comparison in the patch. Norm notation is
consistent and the candidate README states that the full PDF was not rebuilt.
The review suggested identifying r with dx; source inspection instead confirms
r=x-t*log(2)/2^12 (Eq. redacc). The patch uses that correct definition and the
paper's explicit |r|<=2^-13.528 bound. No new numerical run was required.

Optional broader-platform sinh mask changes remain outside this Linux x86-64
candidate. Exception status flags in captured MXCSR are not claimed cleared;
only rounding-control and FTZ/DAZ bits are assertions of this capture. The
offline verifier explicitly distinguishes saved evidence consistency from the
truth of acquisition; local acquisition checked byte-identical baseline copies.
