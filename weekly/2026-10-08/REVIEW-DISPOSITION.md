# Independent review disposition

Actual CLI response metadata identifies `claude-opus-5-5` for the planning,
technical and mathematical reviews. Reviews are advisory; checks below bind
their load-bearing statements to independent evidence.

- Technical F1: reproduced with GCC and Clang, minimal ax-to-au candidate.
- F2: newly routed hard-case region handled by an exact Taylor/monotonicity
  certificate and contiguous boundary tests. All eight isolated cases already
  exist in the corpus, including a spelling without a trailing hexadecimal zero.
  The initial lexical-only comparison was corrected to numeric equality;
  no corpus addition is necessary and no defect is claimed for this concern.
- F3: three ideal-reference substitutions supplied and Gappa rerun.
- F4: narrowed after checking the primary FastTwoSum paper. The original
  eps5/s5 hypothesis is valid; a numerical bug is not established. Further
  range goals place H2 and s2 strictly inside the same binade and justify
  eps2/H2 too. Original smallacc.g retained; no patch is needed. An exploratory
  rounded-high rewrite timed out at 180 seconds and proves nothing. Gappa `//`
  was checked against its documentation and denotes relative magnitude.
- F5: expanded each commented accurate-path goal into a separate executable
  file, with precision 200 and checked return codes/logs. Small-path magnitude
  preconditions are separate goals for every sign/mode.
- F6: restricted proxy conversion contract stated, not reported as a public
  sine wrong-value witness.
- F7: fast path cannot return in the newly routed interval; explicit k=0 and
  endpoint separation argument added.
- F8: exact distance proof plus reducer/table/polynomial/range binding; no
  inference from a zero counter alone. Independent pi identity replay added.
- F9: editorial comments separated from functional findings.

Mathematical review B1: the model's U is exact 2*pi times the reducer residual;
lowercase u includes the pi/4 constant and mhUU errors. Thus those errors are
included in the 13/10-unit bounds, not an extra omitted term.
B2: substitutions/counts and generated active goals are checked; output logs
are checked for failed/vacuous goals. B3: explicit k=0 fast-path argument.
B4: contiguous suffix containment, WORST_SYMMETRIC and four-mode manifests
are verified by the new-interval certificate.

Primary references used to resolve interpretation:
- https://www.arith2025.org/proceedings/215900a141.pdf (Theorems 9-11).
- https://gappa.gitlabpages.inria.fr/gappa/formalizing.html (relative magnitude).

Final review: actual Claude Opus 5.5 approved the assembled report, response
and closure evidence with no genuine blockers. The reviewer read supplied
artifacts and did not execute tests; all tool outcomes were independently
verified by the orchestrator. Optional suggestions were applied: distinguish
the eight near-midpoint cases (2^-49 ulp criterion) from the 4,097-input suffix
tested in the separate boundary corpus; narrow executable-equivalence wording
to sin.c; add explicit successful exit receipts for all model files including
the eight tight-binade goals; remove status-file mutation from the checker.
QA.json verifies all 95 goal files against completed rc=0 records. The
small-ne-positive model duplicates small182-ne-positive and is retained for
pilot history, not as an independent theorem. Internal QA imports the public
workbench coverage validator; the ZIP reproduction uses the listed standalone
certificate scripts and verify_models.py. No historical hard-case-search
completeness is claimed from corpus execution.
