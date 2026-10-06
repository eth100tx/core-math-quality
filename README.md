# CORE-MATH Quality

**An independent, reproducible quality workbench for 25 binary64 functions.**
Run regression checks, measure source coverage, and work through one small
coverage target at a time. A person or any coding AI can run one function or
the complete target list. No AI subscription is needed to execute the tests.

**Start with [current status](STATUS.md), [weekly results](weekly/README.md),
or the [runbook](RUNBOOK.md).** This project is not an official CORE-MATH
repository and does not certify the library's correctness.

## The weekly flow

1. **Choose a revision.** Review upstream changes and any newly authorized
   requests. Pin the implementation; track proof changes separately.
2. **Check regressions.** Replay unchanged upstream worst-case files in all
   four rounding modes using the upstream MPFR checker and strict builds.
3. **Measure gaps.** Collect GCC coverage separately by build configuration;
   retain raw uncovered lines and branch outcomes.
4. **Pick one target.** Prefer the function closest to measured coverage closure.
   Keep it assigned until closed or deliberately deferred. Review newly changed
   functions alongside this list: urgent regression investigation takes
   precedence, while coverage cleanup retains one explicit target.
5. **Improve and review.** Reproduce failures, prepare minimal `.wc` or patch
   candidates, test before/after, and obtain an independent review.
6. **Publish a short result.** Lead with scoped health, new failures, compiler
   issues, and one coverage action. Link the evidence; do not repeat old backlogs.

## Run now

On an x86-64 Ubuntu machine, or Ubuntu under Windows WSL2:

```sh
sudo apt-get update
sudo apt-get install python3 gcc g++ make git libmpfr-dev libgmp-dev
git clone https://github.com/eth100tx/core-math-quality.git
cd core-math-quality
python3 -m unittest discover -s tests -v
python3 quality.py doctor
python3 quality.py run --functions rsqrt --run-id my-rsqrt-check --max-minutes 15
```

The default pin is explicit in `config/source.json`; it never silently means
"latest". For a new review supply a full commit SHA with `--pin`. For the full
list use `--functions all`. See the [supported configurations](docs/CONFIGURATIONS.md)
before choosing another compiler, machine or ISA.

To direct an AI, copy this:

> Read AGENTS.md, STATUS.md and RUNBOOK.md. Qualify this machine. Run the
> requested functions at an immutable upstream revision. Keep raw coverage
> and proof claims separate. Review the results and prepare a short weekly
> report plus reproducible evidence. Do not publish or contact maintainers
> without the operator's authorization.

## What is here

| Location | Purpose |
|---|---|
| `config/targets.json` | The ordered 25-function focus list |
| `config/profiles.json` | Reproducible platform/compiler profiles |
| `quality.py` | Download, qualify, plan, run, resume, export |
| `docs/TEST-PLAN.md` | What runs weekly, when to widen, what results mean |
| `docs/COVERAGE.md` | Denominators, ranking, classifications, closure |
| `docs/SCHEDULING.md` | Small cron/AI handoff without duplicate notification streams |
| `templates/` | Weekly, finding, review and patch-candidate forms |
| `weekly/` | Reviewed outputs and immutable run evidence |
| `candidates/` | Independently reviewed, optional upstream patch/witness candidates |
| `examples/` | Clearly marked synthetic presentation mockup |

Upstream sources and corpora are downloaded from authoritative GitLab into
ignored `.work/`; their original notices remain intact. Only original
orchestration, reviewed reports and measurement evidence belong in this repo.
Private email, credentials and machine identities do not belong here.

Tests are finite evidence. Coverage does not prove correctness; a missed branch
is not automatically unreachable. See [measurement rules](docs/COVERAGE.md).
