---
description:
  Analyze AI coding agent usage, cost, efficiency, and burn rate — Claude Code
  (ccusage), Pi/pi-agent (ccusage-pi), or Codex CLI (ccusage-codex). Use when
  user says "usage", "cost", "spending", "tokens", "analyze usage", "how much did
  I spend", "usage report", "budget", "burn rate", "efficiency", "cache hits",
  "ccusage", "ccw", "ccp". NOT for general shell scripting, non-AI-agent cost
  analysis, or cloud infrastructure billing (use using-cloud-cli).
name: analyzing-usage
targets:
  - claude
  - codex
  - pi
---

# Analyze Claude Code Usage

## Critical Output Rules

- Use `ccusage` for Claude Code usage data. For workflow descriptions, show the exact `ccusage` query shape instead of generic analysis steps.
- Monthly cost reports must include: month-to-date total spend, average daily burn rate, projected month-end spend, limit/budget comparison, and tokens/cache/model breakdown when useful.
- Efficiency reports must include: 30-day window, total/input/output/cache creation/cache read tokens, cache hit/cache efficiency ratio, model breakdown, session/project breakdown when available, and uncertainty if data is missing.
- Always give concrete optimization suggestions tied to metrics: increase cache reuse, reduce repeated long prompts, route cheaper models, split long sessions, reuse project context, or investigate high cost-per-output days.
- Use `uvx termgraph` charts when describing trend visualization; mention `uvx termgraph` by name. If charts are unavailable, fall back to plain tables.
- Do not invent totals. If data has not been queried, label numbers as output fields or examples, not actual results. Say: "If ccusage data is missing or incomplete, report the gap and avoid firm conclusions."
- Ask one question at a time when profile/date scope is unclear.
- Do not run destructive shell commands; usage analysis is read-only.

## Profiles

- **work** (default): `CLAUDE_CONFIG_DIR=/Users/alexei/.claude-team-gaia-mbp-m2 ccusage` — Enterprise, $1,500/mo limit, focus on cost burn rate and project allocation
- **personal** (`ccp`): `ccusage` (no env override) — Max plan, $100-$200/mo, token-based limit, focus on token efficiency and cache rates

Bash tool uses zsh, not fish — always use full command form, not `ccw`/`ccp` aliases.

## Arguments

Parse skill arguments: `work`/`ccw`/`personal`/`ccp` -> profile. `daily`/`weekly`/`monthly`/`session` -> subcommand (default: `daily`). `--since`/`--until` -> date range (default: 14 days). `--today` -> today only. `--compare` -> both profiles.

## Date Defaults

Compute in zsh (macOS):

```bash
SINCE=$(date -v-14d +%Y%m%d)  # 14 days ago
UNTIL=$(date +%Y%m%d)          # today
TODAY=$(date +%Y%m%d)           # for --today mode
MONTH_START=$(date +%Y%m01)     # for burn rate projection
```

## ccusage

Bun global. Reads Claude Code JSONL logs -> token/cost stats.

Subcommands: `daily` (by date), `weekly` (ISO week), `monthly` (month), `session` (conversation), `blocks` (billing).

Key flags: `-s YYYYMMDD` since, `-u YYYYMMDD` until, `-j` JSON (required for piping to jq), `-b` model breakdown, `-i` instances, `-p NAME` project filter, `-o asc|desc`, `-q 'JQ_EXPR'` run jq inline (implies -j, outputs raw jq result — useful for standalone queries but NOT for piping to termgraph), `-O` offline pricing cache, `--no-color` disable ANSI.

JSON shape — daily returns `.daily[]`, weekly `.weekly[]`, monthly `.monthly[]`, session `.sessions[]`. Each entry has: `inputTokens`, `outputTokens`, `cacheCreationTokens`, `cacheReadTokens`, `totalTokens`, `totalCost`, `modelsUsed[]`, `modelBreakdowns[].{modelName, inputTokens, outputTokens, cacheCreationTokens, cacheReadTokens, cost}`. Date key varies: `.date` / `.week` / `.month`. Sessions add `.sessionId`, `.projectPath`, `.lastActivity`.

Always `2>/dev/null` to suppress bun resolver stderr.

## termgraph

Always invoke: `uvx termgraph`. Input: CSV via stdin — `label,value` or `label,v1,v2,v3`.

Flags (no short forms — all long): `--title STR`, `--width N` (use 60), `--color COLOR [...]` (red/blue/green/cyan/magenta/yellow/white — positional for multi-series), `--suffix STR` (" $", " M", "%"), `--stacked` (multi-series only), `--different-scale` (non-stacked multi-series only — NOT with --stacked), `--delim DELIM` (default comma or space), `--format FORMAT` (Python format spec), `--custom-tick CHAR` (emoji work: "🔥"), `--label-before` (values before bars), `--no-labels`, `--no-values`, `--space-between`.

Calendar heatmap: `--calendar --start-dt YYYY-MM-DD --color COLOR`. Labels must be `YYYY-MM-DD,value` format (full date, not MM-DD).

`--percentage` multiplies values by 100 — only useful when raw values are 0-1 ratios. Do NOT use with pre-computed percentages or absolute values.

## Visualization Style

Always use colors — every termgraph call must have `--color`. Use distinct colors per view for visual variety. For multi-series (stacked), use `--color red yellow blue` (opus=red, haiku=yellow, sonnet=blue — consistent across views). Use `--custom-tick "▇"` or emoji ticks (e.g., `--custom-tick "🔥"` for cost spikes) when it adds clarity. Add `--space-between` for views with many rows (>10).

## Views

All 11 view templates (work/personal profile prefix, the `CCU` shorthand, and the
exact `ccusage | jq | termgraph` pipeline per view) and the reusable jq snippets
live in `references/ccusage.md`. Read it before running any view.

## View Selection

- Default (no args): views 1 + 2 + 5
- `--today`: views 4 + 2 (today only) + 5 (7d context)
- `daily`: views 1 + 2 + 3 + 5
- `weekly`/`monthly`: adapt view 1 with matching subcommand, replace `.daily[]`/`.date` with `.weekly[]`/`.week` or `.monthly[]`/`.month`
- `session`: view 4 over date range
- `--compare`: run views 1 + 6 for each profile sequentially, with `echo "\n=== Work ===" / echo "\n=== Personal ==="` dividers
- Full analysis (user asks for everything): all 10 views
- Work profile always includes view 9 (burn rate) in default and daily modes

Run independent charts in parallel.

## Optimization Tracking

Always highlight in analysis: model mix shifts (opus vs sonnet vs haiku ratio changes), cost per output token trends (dropping = better efficiency), cache hit rate trends, sonnet/haiku share growth (signals routing optimization).

For work: compute daily burn rate, project to month-end, flag if trending over $1,500.
For personal: focus on token totals vs plan limits, not cost.

## Errors

Empty JSON -> "No usage data for this period". termgraph fails -> fall back to plain `ccusage daily` (no -j).
