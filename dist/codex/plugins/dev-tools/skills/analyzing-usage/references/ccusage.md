# ccusage View Templates and jq Patterns

All views use the work profile by default. Replace `CLAUDE_CONFIG_DIR=... ccusage`
with plain `ccusage` for personal. Replace SINCE/UNTIL with computed dates.

Shorthand `CCU` below means the full profile command prefix:

- work: `CLAUDE_CONFIG_DIR=/Users/alexei/.claude-team-gaia-mbp-m2 ccusage`
- personal: `ccusage`

## 1. Daily Cost

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.totalCost | . * 100 | round / 100)"' \
  | uvx termgraph --title "Daily Cost (USD)" --color cyan --width 60 --suffix " $"
```

## 2. Per-Model Cost (Stacked)

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

## 3. Token Volume

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.totalTokens / 1000000 | . * 100 | round / 100)"' \
  | uvx termgraph --title "Daily Tokens (M)" --color green --width 60 --suffix " M"
```

## 4. Session/Project Breakdown

```bash
CCU session -s $DATE -u $DATE -j 2>/dev/null \
  | jq -r '[.sessions[] | {key: (if .sessionId == "subagents" then "subagents" else (.sessionId | split("-") | last) end), cost: .totalCost}] | group_by(.key) | map({name: .[0].key, cost: (map(.cost) | add | . * 100 | round / 100)}) | sort_by(-.cost) | .[] | "\(.name),\(.cost)"' \
  | uvx termgraph --title "Session Cost (USD)" --color magenta --width 60 --suffix " $"
```

## 5. Cache Hit Rate

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.cacheReadTokens / (.cacheReadTokens + .cacheCreationTokens + .inputTokens + .outputTokens) * 100 * 10 | round / 10)"' \
  | uvx termgraph --title "Cache Hit Rate %" --color blue --width 60 --suffix "%"
```

## 6. Model Cost Share (Total)

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '[.daily[] | .modelBreakdowns[] | {model: .modelName, cost: .cost}] | group_by(.model) | map({model: .[0].model, total: (map(.cost) | add)}) | sort_by(-.total) | .[] | "\(.model | gsub("claude-"; "") | gsub("-20251001"; "")),\(.total | . * 100 | round / 100)"' \
  | uvx termgraph --title "Total Cost by Model" --color red yellow blue --width 60 --suffix " $"
```

## 7. Output Tokens

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date[5:]),\(.outputTokens / 1000 | round)"' \
  | uvx termgraph --title "Output Tokens (K)" --color yellow --width 60 --suffix " K"
```

## 8. Cost per Output Token

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | select(.outputTokens > 0) | "\(.date[5:]),\(.totalCost / .outputTokens * 1000 | . * 1000 | round / 1000)"' \
  | uvx termgraph --title "Cost per 1K Output Tokens" --color red --width 60 --suffix " $"
```

## 9. Burn Rate Projection (work profile)

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

## 10. Prompt Efficiency (Input/Output Ratio)

Lower ratio = more output per input token = better efficiency.

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | select(.outputTokens > 0) | "\(.date[5:]),\((.inputTokens + .cacheCreationTokens) / .outputTokens | . * 100 | round / 100)"' \
  | uvx termgraph --title "Input/Output Token Ratio" --color yellow --width 60
```

## 11. Calendar Heatmap (30d+)

Needs full YYYY-MM-DD labels. Best for longer ranges.

```bash
CCU daily -s $SINCE -u $UNTIL -j 2>/dev/null \
  | jq -r '.daily[] | "\(.date),\(.totalCost | . * 100 | round / 100)"' \
  | uvx termgraph --calendar --start-dt $(date -v-30d +%Y-%m-%d) --color green
```

## jq Patterns

Safe model extraction: `.modelBreakdowns // [] | map(select(.modelName == "X")) | if length > 0 then .[0].cost else 0 end`

Round cost: `. * 100 | round / 100`. Round to 1 decimal: `. * 10 | round / 10`.

Group sessions: `[.sessions[] | {key: ..., val: ...}] | group_by(.key) | map(...)`.

Percentage: `.a / (.a + .b + .c) * 100 * 10 | round / 10`.
