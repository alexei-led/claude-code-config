---
allowed-tools:
- Bash
- Read
- Grep
- Glob
- AskUserQuestion
argument-hint: '[work|personal] [daily|weekly|monthly|session] [--since YYYYMMDD]
  [--until YYYYMMDD] [--today] [--compare]'
context: fork
description: Analyze AI coding agent usage, cost, efficiency, and burn rate — Claude
  Code (ccusage), Pi/pi-agent (ccusage-pi), or Codex CLI (ccusage-codex). Use when
  user says "usage", "cost", "spending", "tokens", "analyze usage", "how much did
  I spend", "usage report", "budget", "burn rate", "efficiency", "cache hits", "ccusage",
  "ccw", "ccp". NOT for general shell scripting, non-AI-agent cost analysis, or cloud
  infrastructure billing (use using-cloud-cli).
model: sonnet
name: analyzing-usage
user-invocable: true
---

## Arguments

From `$ARGUMENTS`: `work`/`ccw`/`personal`/`ccp` -> profile. `daily`/`weekly`/`monthly`/`session` -> subcommand (default: `daily`). `--since`/`--until` -> date range (default: 14 days). `--today` -> today only. `--compare` -> both profiles.
