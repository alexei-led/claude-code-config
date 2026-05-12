# ccusage-codex Reference

Usage analyzer for [OpenAI Codex CLI](https://github.com/openai/codex) sessions. Status: Beta.

## Install

```bash
npx @ccusage/codex@latest <subcommand>       # one-off — always use npx, not bunx
npm install -g @ccusage/codex                # global install
```

**Do not use `bunx`** — bunx 1.2.x resolves a local `codex` binary instead of the npm package.

## Data Source

Default: `~/.codex/sessions/**/*.jsonl`

Override: `CODEX_HOME=/path/to/codex npx @ccusage/codex@latest ...`

## Subcommands

- `daily` — aggregated daily token/cost stats
- `monthly` — aggregated monthly token/cost stats
- `session` — per-session-file breakdown

No `blocks`, `weekly`, or `statusline`.

## Flags (all subcommands)

- `-j` / `--json` — JSON output (required for jq piping)
- `-s` / `--since YYYYMMDD` — start date (also YYYY-MM-DD)
- `-u` / `--until YYYYMMDD` — end date
- `-z` / `--timezone TZ` — IANA timezone string
- `-O` / `--offline` — use cached LiteLLM pricing (no network call)
- `--compact` — compact table layout
- `--color` / `--no-color` — color output

Missing flags (not available): `--breakdown`, `--jq`, `--order`, `--instances`, `--project`, `--mode`

## JSON Shapes

### `daily --json`

```json
{
  "daily": [
    {
      "date": "2025-09-11",
      "inputTokens": 1200,
      "cachedInputTokens": 200,
      "outputTokens": 500,
      "reasoningOutputTokens": 0,
      "totalTokens": 1700,
      "costUSD": 0.025,
      "models": [{ "model": "gpt-5", "isFallback": false }]
    }
  ],
  "totals": {
    "inputTokens": 1200,
    "cachedInputTokens": 200,
    "outputTokens": 500,
    "reasoningOutputTokens": 0,
    "totalTokens": 1700,
    "costUSD": 0.025
  }
}
```

When no data: `{ "daily": [], "totals": null }` — `totals` is `null`, guard: `.totals // {}`

### `monthly --json`

Same shape; top-level key is `"monthly"`, each entry has `"month"` (e.g. `"2025-09"`) instead of `"date"`.

### `session --json`

```json
{
  "sessions": [
    {
      "date": "2025-09-11",
      "directory": "/Users/alexei/myproject",
      "sessionFile": "abc12345.jsonl",
      "inputTokens": 1200,
      "cachedInputTokens": 200,
      "outputTokens": 500,
      "reasoningOutputTokens": 0,
      "totalTokens": 1700,
      "costUSD": 0.025,
      "models": [{ "model": "gpt-5", "isFallback": false }],
      "lastActivity": "2025-09-11T18:25:40.670Z"
    }
  ],
  "totals": { ... }
}
```

## Key Differences from ccusage

- Cost: `costUSD` (not `totalCost`)
- No `cacheCreationTokens` field (Codex tracks only `cachedInputTokens`)
- `reasoningOutputTokens` is informational only — already included in `outputTokens` billing; do not add it separately
- `models`: array of `{model, isFallback}` objects (not `modelsUsed: string[]`)
- `isFallback: true` means model metadata was missing; pricing estimated from GPT-5 defaults
