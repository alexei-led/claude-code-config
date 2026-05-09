# dev-workflow

Core development loop: code review, fixes, commits, linting hooks, and 24 language-specific review agents. Skills are exported for Claude Code, Codex CLI, Gemini CLI, and Pi; Claude-specific agents, hooks, and commands stay Claude Code-only unless ported under `platforms/pi/agents`.

## Skills (10)

| Skill                           | Invocable | What It Does                                                                   |
| ------------------------------- | --------- | ------------------------------------------------------------------------------ |
| `ccgram-messaging`              | yes       | Inter-agent messaging via ccgram swarm                                         |
| `committing-code`               | yes       | Smart git commits with logical grouping                                        |
| `reviewing-code`                | yes       | Multi-agent review (security, quality, idioms)                                 |
| `fixing-code`                   | yes       | Parallel agents fix all issues, zero tolerance                                 |
| `documenting-code`              | yes       | Update docs based on recent changes                                            |
| `improving-tests`               | yes       | Refactor tests: combine to tabular, fill gaps                                  |
| `improve-codebase-architecture` | yes       | Find deepening opportunities; module/seam/depth vocabulary                     |
| `refactoring-code`              | auto      | Behavior-preserving multi-file refactoring                                     |
| `searching-code`                | auto      | Scoped codebase search and zoom-out maps                                      |
| `coding`                        | auto      | Process discipline: surface assumptions, define verifiable goals before coding |

## Agents (25)

- `docs-keeper` — documentation updates
- 6 Go review agents: `go-qa`, `go-tests`, `go-idioms`, `go-impl`, `go-simplify`, `go-docs`
- 6 Python review agents: `py-qa`, `py-tests`, `py-idioms`, `py-impl`, `py-simplify`, `py-docs`
- 6 TypeScript review agents: `ts-qa`, `ts-tests`, `ts-idioms`, `ts-impl`, `ts-simplify`, `ts-docs`
- 6 Web review agents: `web-qa`, `web-tests`, `web-idioms`, `web-impl`, `web-simplify`, `web-docs`

## Hooks (8)

| Hook                     | Event            | What It Does                                 |
| ------------------------ | ---------------- | -------------------------------------------- |
| `skill-enforcer.sh`      | UserPromptSubmit | Pattern-matches prompt and suggests skills   |
| `file-protector.sh`      | PreToolUse       | Blocks edits to settings.json, secrets       |
| `git-guardrails.sh`      | PreToolUse       | Blocks destructive git commands              |
| `smart-lint.sh`          | PostToolUse      | Auto-runs linter after file edits            |
| `test-runner.sh`         | PostToolUse      | Auto-runs tests after implementation changes |
| `session-start.sh`       | SessionStart     | Shows git branch, last commit, file context  |
| `notify.sh`              | Notification     | Desktop notifications for long operations    |
| `performance-monitor.sh` | PostCompact      | Tracks context compaction metrics            |

### Hook Configuration

`smart-lint.sh` sources `~/.claude/.claude-hooks-config.sh` (global defaults) then `./.claude-hooks-config.sh` (project overrides). The per-tool linters read their own project configs (`.golangci.yml`, `pyproject.toml`, `.prettierrc`, `knip.json`, `.dependency-cruiser.cjs`, …).

See [`docs/lint-tools.md`](docs/lint-tools.md) for the full tool list, install commands, architecture-tier opt-in (knip, dependency-cruiser), and skip recipes (`SKIP_LINT`, `SKIP_ARCH`, `.nolint`, `.nolint-arch`).

## External Providers

| Provider | Used For |
| --- | --- |
| Context7 CLI (`ctx7`) | Portable docs lookup from skills |
| Perplexity/web providers | Research and current facts where available |
| MorphLLM MCP | Claude Code-only source workflows that use semantic search/editing |

Pi exports use local search/edit tools and do not assume MCP providers.
