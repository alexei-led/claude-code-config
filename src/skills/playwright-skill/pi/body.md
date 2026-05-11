# Playwright Helper for Pi

Playwright primitives for browser automation on Pi: dev-server detection, a script runner, and helper utilities. Use when a task needs an actual browser; prefer cheaper tools (curl, unit tests) when it doesn't.

## Path resolution

Resolve `$SKILL_DIR` to the directory holding this `SKILL.md`. Common Pi deployment path:

```text
~/.pi/agent/skills/playwright-skill
```

## Setup

See [`references/setup.md`](references/setup.md). First invocation of `run.js` auto-installs Playwright via bun if missing.

## Detect dev servers

```bash
node -e "require('$SKILL_DIR/scripts/lib/helpers').detectDevServers().then(s => console.log(JSON.stringify(s)))"
```

If multiple servers are found, ask the user which to test.

## Run a temporary browser script

Write scripts outside the skill directory (typically under `/tmp`), then:

```bash
node $SKILL_DIR/scripts/run.js /tmp/playwright-check.js
```

## Rules

- Never write generated tests into the skill directory.
- Prefer visible browser mode unless the user asks for headless.
- Parameterize target URLs.
- Return artifact paths for screenshots, traces, and logs.
- Higher-level test strategy stays in `testing-e2e`.
