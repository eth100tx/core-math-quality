# Supported configurations and qualification

| Profile | Intended host | Coverage | Qualification |
|---|---|---|---|
| `gcc-linux-x86_64` | Ubuntu 24.04 x86-64, including WSL2 | GCC O0; separate O3 regression | See dated weekly receipt; primary baseline |
| `gcc-linux-x86_64-v3` | Same, with successful v3 ISA probe | Separate GCC denominator | Selected-function qualification only until full census |
| `clang-linux-x86_64` | Same, Clang 18 | None; regression only | Selected-function qualification only |
| `clang-macos-arm64-experimental` | macOS Apple Silicon | None | Documented extension; **not tested or supported yet** |
| Native Windows/MSVC | Windows without WSL | None | Unsupported; use WSL2 |

A profile definition is not evidence of a passing run. Consult receipts for the
exact compiler, MPFR/GMP, libc, flags, function list and modes actually tested.
Other Linux distributions, Intel Macs and ARM Linux need their own qualification.
There is no remote-machine requirement; this project runs on the operator's computer.

Run `python3 tools/qualification.py` on the primary GCC host for positive and
deliberately broken checker controls. The mutation is confined to a disposable
copy and must fail in every rounding mode; it is not an upstream defect.
GCC explicitly enables `-fsignaling-nans`; the Clang profile omits that unsupported
flag. Both use the upstream checker's built-in NaN checks, but those observations
do not establish every compiler signaling-NaN behavior.

### Windows

Install WSL2 with an Ubuntu distribution if needed, open its terminal, and follow
the README. Keep the checkout on the Linux filesystem for better performance.
The Python runner is POSIX-only; do not invoke it with Windows Python. A Windows
scheduler can launch a saved WSL script. Do not embed complex quoting in commands.

### macOS extension

Install Python 3, Git, MPFR and GMP using your chosen package manager and make the
headers/libraries available to Clang (for Homebrew, use `CPATH` and `LIBRARY_PATH`
from `brew --prefix mpfr` and `brew --prefix gmp`). Try the experimental doctor,
then a single-function replay. Do not call the profile qualified until both the
positive run and a deliberately broken negative control behave as expected.
Apple Clang coverage requires a separate LLVM adapter; do not rank it against GCC.
No macOS installation or remote run was performed for this release.

### Extend a profile

Add a named entry with compiler, OS, architecture, explicit ISA flags and coverage
capability. Preserve semantic flags. Check how the upstream checker handles the
new ABI and floating-point environment. Add platform tests; publish a receipt.
Version a changed profile name if its semantics change. Never merge counts from
different profiles to improve apparent coverage. No `-march=native` or fast-math.
