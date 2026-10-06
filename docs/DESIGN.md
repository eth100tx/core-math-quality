# Design decisions and lessons carried forward

This workbench is deliberately small: a versioned test plan, a deterministic
runner, inspectable evidence, one coverage queue, and independent review.
It is not an autonomous upstream patching service.

Earlier audit work motivates these rules:

- A large report is less useful than an actionable lead. Separate the weekly
  summary from the full evidence and maintain a small active target list.
- Passing worst cases, complete branch coverage and a mathematical proof are
  three different results. None may stand in for another.
- Compiler options and errno macros materially change the measured program.
  Pin configurations and never combine them to hide a gap.
- Four-mode coverage can be complete while individual modes are not. Preserve
  both the union and individual mode results.
- A `.wc` parser may not encode every NaN payload. A reachable gap can therefore
  require a dedicated bit-pattern harness rather than a textual `.wc` row.
- A missing branch can be defensive, configuration-specific, unreachable under
  a proven precondition, or simply untested. Keep those dispositions separate.
- Compiler instrumentation can alter behavior. A suspected defect must reproduce
  in an ordinary build before it is described as an upstream correctness failure.
- Old proof comments can become obsolete after upstream revisions. Reconcile
  against the actual changed source/paper before repeating a finding.
- Unbounded searches and orphaned workers harm reproducibility. Use bounded
  sequential units, termination tests, OS locks, checkpoints and time accounting.
- A reviewer model can be wrong. Record its feedback and verify important claims.

The first release focuses on complete upstream `.wc` replay and target-file
coverage. Specialized random/exhaustive searches, shared-header coverage,
sanitizers, proof certificates and additional architectures can be added as
explicit scoped tasks with their own evidence. Scope limits remain visible.

The public repository contains neutral technical requirements and fresh reviewed
evidence. Private correspondence, machine identities and old audit history are
not required to operate it and are not imported.
