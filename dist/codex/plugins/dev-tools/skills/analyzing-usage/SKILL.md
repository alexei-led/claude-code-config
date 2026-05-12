---
description: Analyze Codex CLI session usage, token cost, and efficiency using ccusage-codex.
  Use when user says "usage", "cost", "tokens", "how much did I spend", "codex usage",
  "session cost", "ccusage-codex". NOT for cloud billing or non-codex usage analysis.
name: analyzing-usage
---

# Analyze Codex CLI Usage

Analyze [OpenAI Codex CLI](https://github.com/openai/codex) session usage via `ccusage-codex`.

- Reference: [ccusage-codex flags and JSON shapes](references/ccusage-codex.md)

## Tool

Binary: `ccusage-codex` — reads `~/.codex/sessions/**/*.jsonl` (override: `CODEX_HOME` env var)

```bash
npx @ccusage/codex@latest <subcommand> [flags]
```

**Use `npx`, not `bunx`** — bunx 1.2.x resolves local `codex` binary instead of the npm package.

## Subcommands

- `daily` — token/cost by date
- `monthly` — token/cost by month
- `session` — token/cost per session file

No `blocks`, `weekly`, or `statusline` subcommands.

## Flags

All subcommands share:

- `-j` / `--json` — JSON output (required for jq piping)
- `-s` / `--since YYYYMMDD` — start date (also YYYY-MM-DD)
- `-u` / `--until YYYYMMDD` — end date
- `-z` / `--timezone TZ` — IANA timezone
- `-O` / `--offline` — use cached LiteLLM pricing (no network)
- `--compact` — compact table output
- `--color` / `--no-color` — color output

No `--breakdown`, `--jq`, `--order`, `--instances`, `--project`, or `--mode` flags.

## JSON Field Differences

Codex JSON uses **different field names** from ccusage — do not port claude jq expressions directly:

- Cost field: `costUSD` (not `totalCost`)
- No `cacheCreationTokens`; has `cachedInputTokens` (= cached reads)
- Has `reasoningOutputTokens` (informational; already included in `outputTokens` billing — do not double-count)
- `models` is `[{model, isFallback}]` array of objects, not `modelsUsed: []` of strings
- When no data: `{ "daily": [], "totals": null }` — `totals` is `null`, guard with `// {}`

## Computing Dates

```bash
# macOS
SINCE=$(date -v-14d +%Y%m%d)
UNTIL=$(date +%Y%m%d)
TODAY=$(date +%Y%m%d)

# Linux
SINCE=$(date -d '14 days ago' +%Y%m%d)
UNTIL=$(date +%Y%m%d)
```

## Output Rules

- Only report numbers from actual `ccusage-codex` output. Never invent totals.
- Use `costUSD` in all jq expressions, never `totalCost`.
- When `totals` is null: "No Codex usage data for this period."
- Every report must include: date range queried, total cost, models used.
- Always append `2>/dev/null` to suppress npm resolver stderr.
- Prefer `uvx termgraph` for visualization when available; fall back to plain jq output.

## Key Queries

### Daily Cost (14d)

```bash
npx @ccusage/codex@latest daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.costUSD | . * 100 | round / 100)"' \
  | uvx termgraph --title "Daily Cost (USD)" --color cyan --width 60 --suffix " $"
```

### Monthly Totals

```bash
npx @ccusage/codex@latest monthly -j 2>/dev/null \
  | jq -r '.monthly[] | "\(.month),\(.costUSD | . * 100 | round / 100)"' \
  | uvx termgraph --title "Monthly Cost (USD)" --color green --width 60 --suffix " $"
```

### Session Breakdown (today)

```bash
npx @ccusage/codex@latest session -s $TODAY -u $TODAY -j 2>/dev/null \
  | jq -r '.sessions[] | "\(.directory | split("/") | last),\(.costUSD | . * 100 | round / 100)"' \
  | sort -t, -k2 -rn | head -10
```

### Cache Efficiency (cached input vs total input)

```bash
npx @ccusage/codex@latest daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | select(.inputTokens > 0) |
    "\(.date[5:]),\(.cachedInputTokens / .inputTokens * 100 | . * 10 | round / 10)"' \
  | uvx termgraph --title "Cache Hit Rate %" --color blue --width 60 --suffix "%"
```

### Model Usage Distribution

```bash
npx @ccusage/codex@latest daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '[.daily[].models[]] | group_by(.model)
    | map({model: .[0].model, count: length})
    | sort_by(-.count)[] | "\(.model),\(.count)"'
```

### Token Volume

```bash
npx @ccusage/codex@latest daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.totalTokens / 1000000 | . * 100 | round / 100)"' \
  | uvx termgraph --title "Daily Tokens (M)" --color yellow --width 60 --suffix " M"
```

## What to Show

- Default: daily cost + cache efficiency (14d window)
- `--today`: session breakdown + model distribution
- `monthly`: monthly cost chart
- Full analysis: all six queries above
