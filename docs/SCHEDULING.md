# Scheduling: one entry point, no hidden service

Use one weekly scheduler per operator. This repository owns the workflow; the
scheduler only checks out the operator-approved revision and asks an AI to follow
RUNBOOK.md. The deterministic checks also work without an AI or mail access.

Example Linux cron entry (08:00 Sunday **in the scheduler host's timezone**):

```cron
0 8 * * 0 /path/to/review-weekly.sh
```

Example saved script, after replacing paths and an explicitly selected source pin:

```sh
#!/bin/sh
set -eu
cd /path/to/core-math-quality
# Review/pin this workbench's updates before running new code.
# Fetch the authoritative upstream SHA and review its changes before updating PIN.
PIN=FULL_40_CHARACTER_UPSTREAM_SHA
RUN_ID=$(date -u +%Y%m%d)-gcc-errno1
mkdir -p .work/scheduler
timeout --signal=TERM --kill-after=10s 110m \
  python3 quality.py run --pin "$PIN" --functions all \
  --run-id "$RUN_ID" --max-minutes 100 > ".work/scheduler/$RUN_ID.log" 2>&1
# Hand results to your chosen AI with prompts/WEEKLY.txt.
# No automatic publication, email or upstream PR is performed by this script.
```

Install this only if a scheduler does not already own the weekly run. The initial
operator already has a Sunday local AI automation; it follows this repository
through its private workflow, so no second cron is installed here. Authentication
and email preferences stay private. The operator's authorized AI may publish and
send a reviewed summary; the public instructions do not grant that permission to
other users or forked agents.

The machine must be awake, connected and able to run the scheduler. A local
[Codex automation](https://learn.chatgpt.com/docs/automations?surface=app) also
depends on its configured local app/host. A missed run resumes the previous
reviewed baseline rather than skipping the interval. Daylight saving follows
the chosen local scheduler timezone; UTC examples must be adjusted deliberately.
After a missed run, compare against the last reviewed upstream pin so intervening
changes remain in scope; do not substitute an arbitrary last-seven-days window.
