# ccusage-pi Reference

Usage analyzer for [pi-agent](https://github.com/badlogic/pi-mono) sessions.

## Install

```bash
npx @ccusage/pi@latest <subcommand>          # one-off, always current
npm install -g @ccusage/pi                   # global install
```

Alias in shell config:

```bash
alias ccusage-pi='npx @ccusage/pi@latest'
```

## Data Source

Default: `~/.pi/agent/sessions/`

Override: `PI_AGENT_DIR=/path/to/sessions npx @ccusage/pi@latest ...`

Or per-command: `npx @ccusage/pi@latest daily --pi-path /custom/sessions`

## Subcommands

- `daily` — aggregated daily token/cost stats
- `monthly` — aggregated monthly token/cost stats
- `session` — per-conversation session breakdown

No `blocks`, `weekly`, or `statusline`.

## Flags (all subcommands)

- `--since YYYYMMDD` — start date (also accepts YYYY-MM-DD)
- `--until YYYYMMDD` — end date
- `--json` — JSON output (required for jq piping)
- `--breakdown` / `-b` — per-model cost breakdown rows
- `--order asc|desc` — sort order (default: desc)
- `--timezone` / `-z` — IANA timezone string
- `--pi-path <path>` — override sessions directory path

Missing flags (not available): `--jq`, `--offline`, `--mode`, `--instances`, `--project`, `--compact`

## JSON Shapes

### `daily --json`

```json
{
  "daily": [
    {
      "date": "2025-05-12",
      "source": "pi-agent",
      "inputTokens": 12000,
      "outputTokens": 800,
      "cacheCreationTokens": 200,
      "cacheReadTokens": 100,
      "totalCost": 0.045,
      "modelsUsed": ["claude-sonnet-4-6"],
      "modelBreakdowns": [
        {
          "modelName": "claude-sonnet-4-6",
          "inputTokens": 12000,
          "outputTokens": 800,
          "cacheCreationTokens": 200,
          "cacheReadTokens": 100,
          "cost": 0.045
        }
      ]
    }
  ],
  "totals": {
    "inputTokens": 12000,
    "outputTokens": 800,
    "cacheCreationTokens": 200,
    "cacheReadTokens": 100,
    "totalCost": 0.045
  }
}
```

No `totalTokens` field — compute as `inputTokens + outputTokens + cacheCreationTokens + cacheReadTokens`.

### `monthly --json`

Same shape as daily; top-level key is `"monthly"`, each entry has `"month"` (e.g. `"2025-05"`) instead of `"date"`.

### `session --json`

```json
{
  "sessions": [
    {
      "sessionId": "abc-def-ghi-...",
      "projectPath": "/Users/alexei/myproject",
      "source": "pi-agent",
      "inputTokens": 5000,
      "outputTokens": 300,
      "cacheCreationTokens": 50,
      "cacheReadTokens": 200,
      "totalCost": 0.015,
      "lastActivity": "2025-05-12T10:23:00.000Z",
      "modelsUsed": ["claude-sonnet-4-6"],
      "modelBreakdowns": [...]
    }
  ],
  "totals": { ... }
}
```

When session list is empty, returns bare `[]` (not `{ "sessions": [] }`). Guard in jq:
`if type == "array" then .[] else .sessions[] end`

All objects include `"source": "pi-agent"` field — not present in base ccusage output.
