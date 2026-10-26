# Restricted hypot verifier and Linux qualification

**October 26, 2026: the exact-integer verifier and separate Linux adapter pass
qualification for 18 explicit positive-normal fixtures in four rounding modes,
under GCC and Clang.** This is qualification of the listed configuration and
test setup, not exhaustive validation of hypot or a new hard-case search.

## What is implemented

`hypot_verify.py` checks the [v1 certificate specification](HYPOT-CERTIFICATE-SPEC.md)
using arbitrary-precision integers, without importing the fixture generator or
using floating-point square roots. Supplied brackets and expected answers are
recomputed and checked. Unknown/missing fields, duplicate keys, noncanonical
bits, unsupported versions and out-of-domain inputs are rejected. Files are
limited to 4 MiB and 4,096 records; Python optimization does not disable checks.

```sh
python3 hypot_verify.py bivariate/hypot-fixtures.json
```

The independent fixture generator uses integer square root to select brackets.
Its finite qualification set includes an exact result, both midpoint parities,
inputs adjacent to ties, a bracket starting at 2, maximal input significands,
equal inputs and swapped arguments. These are known arithmetic constructions,
not a claim of new corpus members. There is no corpus-membership or coverage claim.

## Executed qualification

Implementation pin: `336752ca18e1204321225ec90c1f43fcb90ada1b`, acquired from the
authoritative [GitLab tree](https://gitlab.inria.fr/core-math/core-math/-/tree/336752ca18e1204321225ec90c1f43fcb90ada1b/src/binary64/hypot)
via `https://gitlab.inria.fr/api/v4/projects/35719` and checked against the returned Git blob identifier.
Only `hypot.c` was required; a newly introduced local header dependency would
stop acquisition for explicit review. This focused pin does not advance the
weekly whole-repository review watermark.

WSL2 Ubuntu 24.04.3 x86-64, GCC 13.3 and Clang 18.1.3; glibc 2.39, MPFR 4.2.1 and GMP 6.3.0.
Each compiler's doctor probe passed. Each profile executed 18 inputs × four
modes = 72 CORE-MATH observations, **144 total**. Values, all five standard
floating-point flags, errno, input bits and active/preserved rounding modes agree
with the restricted certificate contract. All results were normal. Zero, signed
zero, negative inputs, subnormals, underflow, overflow, infinities, NaNs, ERANGE
paths and other architectures/ABIs remain outside this qualification. All flags
were cleared before each call; preservation of pre-existing sticky flags was
not tested.

The source is compiled separately, with no LTO, baseline `-march=x86-64`,
`-frounding-math`, `-ffp-contract=off` and errno support. The adapter calls through
a volatile function pointer and captures flags/errno before printing. Clang's
adapter additionally uses strict exception behavior. The exact build flags, source,
compiler **driver** executable, linked MPFR/GMP libraries, tools and produced binaries are hashed in
the [receipt](../bivariate/results/2026-10-26/qualification.json).
The driver hash does not identify GCC's separate cc1, assembler or linker;
libc/libm are not content-hashed. This is not a hermetic toolchain/image identity.

Every observation is gated by two independent MPFR calculations: correctly
rounded `mpfr_hypot` at precision 53, and an exact sum of squares at precision 256
followed by outward-rounded square roots and directed conversion. The MPFR
ternary result supplies an independent exactness check. Its reported flags are
oracle expectations, not observations of MPFR's host floating-point environment.
The local qualification contract requires inexact exactly for nonrepresentable
results, no other standard flags and errno zero in this domain. It is not a
claim about general C libm exception requirements. It follows the pinned upstream
[`CORE_MATH_CHECK_INEXACT` checker contract](https://gitlab.inria.fr/core-math/core-math/-/blob/336752ca18e1204321225ec90c1f43fcb90ada1b/src/binary64/support/check_worst.c),
which rejects both missing and spurious inexact flags, and the hypot source's
explicit flag restore on exact-result paths. The upstream checker's sticky-flag
test was not reproduced by this restricted adapter.

For **each compiler**, compiled controls deliberately corrupt the value, input,
rounding mode, inexact flag and errno. Each must fail with its specific rejection
code. A SIGTERM-ignoring suspended process must time out and be killed/reaped by
the shared process-group timeout helper. Six malformed/out-of-domain bit-string
controls are also rejected by the C parser. The executable receives only records
already accepted by the integer verifier; its parser alone does not enforce the
sum-of-squares domain restriction.

## Reproduce and extend

```sh
timeout 30m python3 hypot_run.py \
  --pin 336752ca18e1204321225ec90c1f43fcb90ada1b \
  --run-id my-hypot-qualification --max-minutes 20
python3 -m unittest discover -s tests -v
python3 validate.py
```

Use a new run ID; existing evidence is not overwritten. The runner takes the
same host lock as the unary runner, uses bounded children and records incomplete
state on failure. The outer timeout covers acquisition/doctor as well as child
execution. Compile/run serially under the existing coordination rules. Qualification
is specific to these toolchains; flags or adapter changes require requalification.

The [sealed tool snapshots](../bivariate/results/2026-10-26/tools/) preserve the
executed versions. The publication validator recomputes answers, checks every
observation and control, and checks the evidence manifest. Passing tests are
finite evidence, not a formal proof of the verifier implementation.
The tie neighbours are qualification fixtures, not hard-to-round cases; no
difficulty ranking is claimed. Acquisition has download timeouts, and
doctor has per-command timeouts; these do not consume the runner's per-command
deadline helper. The documented outer timeout is required for the overall bound.

## Remaining work

- Import/reproduce the prior research archives when supplied; this implementation
  neither depends on them nor substitutes for that still-open request.
- Checking a supplied certificate family is distinct from regenerating its
  completeness census. No family census was regenerated here.
- A bounded candidate-generation experiment and upstream corpus deduplication
  are next possibilities. They are not included in this qualification.
- Angular/pow certificates, full-corpus atan2 stage comparisons and a different
  pow hypothesis remain separate work. No new bivariate bug or novelty is claimed.

[Independent review and validation](HYPOT-REVIEW.md) records the final scope and
resolved conditions.
