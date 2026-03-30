---
name: analyzing-usage
description: >-
  Analyze Claude Code usage, cost, efficiency, and burn rate using ccusage and termgraph.
  Use when user says "usage", "cost", "spending", "tokens", "analyze usage",
  "how much did I spend", "usage report", "budget", "burn rate", "efficiency",
  "cache hits", "ccusage", "ccw", "ccp".
user-invocable: true
model: sonnet
context: fork
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - AskUserQuestion
argument-hint: "[work|personal] [daily|weekly|monthly|session] [--since YYYYMMDD] [--until YYYYMMDD] [--today] [--compare]"
---

# Analyze Claude Code Usage

Visual usage reports with cost, token, and efficiency analysis.

## Profiles

- **work** (default): `CLAUDE_CONFIG_DIR=/Users/alexei/.claude-team-gaia-mbp-m2 ccusage` — Enterprise, $1,500/mo limit, focus on cost burn rate and project allocation
- **personal** (`ccp`): `ccusage` (no env override) — Max plan, $100-$200/mo, token-based limit, focus on token efficiency and cache rates

Bash tool uses zsh, not fish — always use full command form, not `ccw`/`ccp` aliases.

## Arguments

From `$ARGUMENTS`: `work`/`ccw`/`personal`/`ccp` -> profile. `daily`/`weekly`/`monthly`/`session` -> subcommand (default: `daily`). `--since`/`--until` -> date range (default: 14 days). `--today` -> today only. `--compare` -> both profiles.

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

All views use work profile by default. Replace `CLAUDE_CONFIG_DIR=... ccusage` with plain `ccusage` for personal. Replace SINCE/UNTIL with computed dates.

Shorthand `CCU` below means the full profile command prefix:

- work: `CLAUDE_CONFIG_DIR=/Users/alexei/.claude-team-gaia-mbp-m2 ccusage`
- personal: `ccusage`

### 1. Daily Cost

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.totalCost | . * 100 | round / 100)"' \
  | uvx termgraph --title "Daily Cost (USD)" --color cyan --width 60 --suffix " $"
```

### 2. Per-Model Cost (Stacked)

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(
    .modelBreakdowns // [] | map(select(.modelName == "claude-opus-4-6")) | if length > 0 then .[0].cost | . * 10 | round / 10 else 0 end
  ),\(
    .modelBreakdowns // [] | map(select(.modelName == "claude-haiku-4-5-20251001")) | if length > 0 then .[0].cost | . * 10 | round / 10 else 0 end
  ),\(
    .modelBreakdowns // [] | map(select(.modelName == "claude-sonnet-4-6")) | if length > 0 then .[0].cost | . * 10 | round / 10 else 0 end
  )"' \
  | uvx termgraph --title "Per-Model Daily Cost" --color red yellow blue --stacked --width 60 --suffix " $"
```

### 3. Token Volume

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.totalTokens / 1000000 | . * 100 | round / 100)"' \
  | uvx termgraph --title "Daily Tokens (M)" --color green --width 60 --suffix " M"
```

### 4. Session/Project Breakdown

```bash
CCU session -s $DATE -u $DATE -j 2>/dev/null \
  | jq -r '[.sessions[] | {key: (if .sessionId == "subagents" then "subagents" else (.sessionId | split("-") | last) end), cost: .totalCost}] | group_by(.key) | map({name: .[0].key, cost: (map(.cost) | add | . * 100 | round / 100)}) | sort_by(-.cost) | .[] | "\(.name),\(.cost)"' \
  | uvx termgraph --title "Session Cost (USD)" --color magenta --width 60 --suffix " $"
```

### 5. Cache Hit Rate

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.cacheReadTokens / (.cacheReadTokens + .cacheCreationTokens + .inputTokens + .outputTokens) * 100 * 10 | round / 10)"' \
  | uvx termgraph --title "Cache Hit Rate %" --color blue --width 60 --suffix "%"
```

### 6. Model Cost Share (Total)

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '[.daily[] | .modelBreakdowns[] | {model: .modelName, cost: .cost}] | group_by(.model) | map({model: .[0].model, total: (map(.cost) | add)}) | sort_by(-.total) | .[] | "\(.model | gsub("claude-"; "") | gsub("-20251001"; "")),\(.total | . * 100 | round / 100)"' \
  | uvx termgraph --title "Total Cost by Model" --color red yellow blue --width 60 --suffix " $"
```

### 7. Output Tokens

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.outputTokens / 1000 | round)"' \
  | uvx termgraph --title "Output Tokens (K)" --color yellow --width 60 --suffix " K"
```

### 8. Cost per Output Token

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | select(.outputTokens > 0) | "\(.date[5:]),\(.totalCost / .outputTokens * 1000 | . * 1000 | round / 1000)"' \
  | uvx termgraph --title "Cost per 1K Output Tokens" --color red --width 60 --suffix " $"
```

### 9. Burn Rate Projection (work profile)

For work: compute month-to-date spend, project to month-end, compare to $1,500 limit.

```bash
CCU daily -s $MONTH_START -u $UNTIL -j 2>/dev/null \
  | jq -r '
    (.daily | length) as $days |
    (.daily | map(.totalCost) | add) as $mtd |
    ($mtd / $days) as $daily_avg |
    (if .daily[-1].date[5:7] == "02" then 28 elif (.daily[-1].date[5:7] | test("0[469]|11")) then 30 else 31 end) as $month_days |
    ($daily_avg * $month_days) as $projected |
    "MTD (\($days)d),\($mtd | . * 100 | round / 100)\nProjected,\($projected | . * 100 | round / 100)\nLimit,1500"
  ' | uvx termgraph --title "Monthly Burn Rate (USD)" --color cyan cyan red --width 60 --suffix " $"
```

### 10. Prompt Efficiency (Input/Output Ratio)

Lower ratio = more output per input token = better efficiency.

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | select(.outputTokens > 0) | "\(.date[5:]),\((.inputTokens + .cacheCreationTokens) / .outputTokens | . * 100 | round / 100)"' \
  | uvx termgraph --title "Input/Output Token Ratio" --color yellow --width 60
```

### 11. Calendar Heatmap (30d+)

Needs full YYYY-MM-DD labels. Best for longer ranges.

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date),\(.totalCost | . * 100 | round / 100)"' \
  | uvx termgraph --calendar --start-dt $(date -v-30d +%Y-%m-%d) --color green
```

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

## jq Patterns

Safe model extraction: `.modelBreakdowns // [] | map(select(.modelName == "X")) | if length > 0 then .[0].cost else 0 end`

Round cost: `. * 100 | round / 100`. Round to 1 decimal: `. * 10 | round / 10`.

Group sessions: `[.sessions[] | {key: ..., val: ...}] | group_by(.key) | map(...)`.

Percentage: `.a / (.a + .b + .c) * 100 * 10 | round / 10`.

## Errors

Empty JSON -> "No usage data for this period". termgraph fails -> fall back to plain `ccusage daily` (no -j).
