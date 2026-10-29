# One daily entry point, with a longer Sunday review

The initial operator uses one existing local AI automation at 08:00 in
America/Chicago each day. On Sunday it performs correspondence alignment and
the longer weekly review in one invocation. On other days it checks correspondence and completes substantive authorized
requests when read, following the request-driven lane. Do not install a second cron or parallel inbox monitor.

Every activation starts with [BOOTSTRAP.md](../BOOTSTRAP.md): fetch canonical
main, review the delta, fast-forward only a clean compatible checkout, record
the coherent revision, and read the role and key files. The schedule is a
launcher; reviewed GitHub instructions and the private operator overlay own
the work. An old local prompt is not a substitute for this synchronization.

Route by the current date in **America/Chicago**, not a fixed UTC weekday or
the date a delayed trigger claims. Keep the host's scheduler timezone aligned
with that zone and verify its daylight-saving behavior when setting it up.
Record local date, lane, invocation state, workbench revision and budget in
private state. Use [DAILY.md](DAILY.md) for duplicate/missed-run handling.

| Lane | Entry prompt | Work and delivery |
|---|---|---|
| Monday-Saturday | [DAILY.txt](../prompts/DAILY.txt) | Correspondence, full requested investigations and reviewed replies; no routine campaign |
| Sunday | [WEEKLY.txt](../prompts/WEEKLY.txt) | Same correspondence check plus bounded technical review and one reviewed weekly result |

The weekly scan and light no-action checks share the existing weekly budget.
Explicitly authorized request investigations have separate scope/accounting as
specified in DAILY.md; they are not gated on Sunday. No daily newsletter is sent. Protected sources, independent review, private credentials,
permission boundaries and delivery verification apply to both lanes.

The former generic full-corpus cron example is retired: it could ignore current
pauses or repeat an unchanged campaign. A new operator should configure one
approved AI entry point to follow this repository and their own private state.
The deterministic test commands in RUNBOOK.md remain available for manually
selected, authorized runs; no hidden scheduler or automatic mailer is installed
by this repository.

For an approved numerical run, retain an outer wall-clock timeout covering
acquisition and every child, in addition to the runner's per-child limits.
For example, an operator can wrap the selected RUNBOOK command with Linux
`timeout --signal=TERM --kill-after=30s <remaining-seconds>s` inside their
monitored job wrapper. Derive remaining seconds from the applicable recorded request or weekly budget; a
timeout is an incomplete run, never a clean result. This is not a cron recipe.

The host and local app must be awake and online. A missed invocation is not a
successful check; retain read and review baselines so subsequent work covers
the gap. Do not generate backdated reports or duplicate sends. Public files
cannot supply another operator's credentials or sending authorization.
