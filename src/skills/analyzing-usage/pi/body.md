# Analyze Pi-Agent Usage

Analyze [pi-agent](https://github.com/badlogic/pi-mono) session usage via `ccusage-pi`.

- Reference: [ccusage-pi flags and JSON shapes](references/ccusage-pi.md)

## Tool

Binary: `ccusage-pi` — reads `~/.pi/agent/sessions/` (override: `PI_AGENT_DIR` env var)

```bash
npx @ccusage/pi@latest <subcommand> [flags]
```

## Subcommands

- `daily` — token/cost by date
- `monthly` — token/cost by month
- `session` — token/cost per conversation

No `blocks`, `weekly`, or `statusline` subcommands.

## Flags

All subcommands share:

- `--since YYYYMMDD` — start date (also accepts YYYY-MM-DD)
- `--until YYYYMMDD` — end date
- `--json` — JSON output (required for jq piping)
- `--breakdown` / `-b` — per-model breakdown rows
- `--order asc|desc` — sort order (default: desc)
- `--timezone` / `-z` — IANA timezone
- `--pi-path <path>` — override sessions directory

No `--jq`, `--offline`, `--mode`, `--instances`, or `--project` flags.

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

Detect OS before computing: `uname -s` returns `Darwin` (macOS) or `Linux`.

## Output Rules

- Only report numbers from actual `ccusage-pi` output. Never invent totals.
- When result is empty: "No pi-agent usage data for this period."
- Every report must include: date range queried, total cost, top model used.
- Compute `totalTokens` as `inputTokens + outputTokens + cacheCreationTokens + cacheReadTokens` — no `totalTokens` field in JSON.
- Empty session list returns bare `[]`, not `{ "sessions": [] }` — guard with `if type == "array"`.
- Give concrete optimization suggestions: reduce prompt size, increase cache reuse, check session reuse patterns.
- Always append `2>/dev/null` to suppress npm resolver stderr.
- Prefer `uvx termgraph` for visualization when available; fall back to plain `jq` table otherwise.

## Key Queries

### Daily Cost (14d)

```bash
npx @ccusage/pi@latest daily --since $SINCE --until $UNTIL --json 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.totalCost | . * 100 | round / 100)"' \
  | uvx termgraph --title "Daily Cost (USD)" --color cyan --width 60 --suffix " $"
```

### Monthly Totals

```bash
npx @ccusage/pi@latest monthly --json 2>/dev/null \
  | jq -r '.monthly[] | "\(.month),\(.totalCost | . * 100 | round / 100)"' \
  | uvx termgraph --title "Monthly Cost (USD)" --color green --width 60 --suffix " $"
```

### Session Breakdown (today)

```bash
npx @ccusage/pi@latest session --since $TODAY --until $TODAY --json 2>/dev/null \
  | jq -r 'if type == "array" then .[] else .sessions[] end
    | "\(.sessionId | split("-") | last),\(.totalCost | . * 100 | round / 100)"'
```

### Cache Efficiency

```bash
npx @ccusage/pi@latest daily --since $SINCE --until $UNTIL --json 2>/dev/null \
  | jq -r '.daily[] |
    (.cacheReadTokens + .cacheCreationTokens) as $cache |
    (.inputTokens + .outputTokens + $cache) as $total |
    select($total > 0) |
    "\(.date[5:]),\($cache / $total * 100 | . * 10 | round / 10)"' \
  | uvx termgraph --title "Cache Rate %" --color blue --width 60 --suffix "%"
```

### Token Volume

```bash
npx @ccusage/pi@latest daily --since $SINCE --until $UNTIL --json 2>/dev/null \
  | jq -r '.daily[] |
    (.inputTokens + .outputTokens + .cacheCreationTokens + .cacheReadTokens) as $total |
    "\(.date[5:]),\($total / 1000000 | . * 100 | round / 100)"' \
  | uvx termgraph --title "Daily Tokens (M)" --color yellow --width 60 --suffix " M"
```

## What to Show

- Default: daily cost + cache efficiency (14d window)
- `--today`: session breakdown + cache efficiency (7d context)
- `monthly`: monthly cost chart
- Full analysis: all five queries above
