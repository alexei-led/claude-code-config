# Pi Subagent Schedules

This directory is reserved for Pi cron-style schedules that drive subagent
runs (`scout`, `planner`, `reviewer`, `worker`, `playwright-tester`) on a
recurring cadence.

It is **empty by design** today — `cc-thingz` ships skills and runtime
subagents but does not yet ship schedules. `scripts/install-pi-exports.sh`
does not deploy this directory.

When schedules are introduced, expected layout:

```text
.pi/subagent-schedules/
├── README.md
└── <schedule-name>.json
```

A schedule file describes which subagent to invoke, what prompt or skill to
load, and the cron expression. The deploy script will be extended to mirror
this directory into `~/.pi/agent/subagent-schedules/` (or whatever Pi's
canonical schedules path turns out to be) when files exist.

See [docs/pi-skill-export.md](../../docs/pi-skill-export.md) for the rest of
the Pi deployment layout.
