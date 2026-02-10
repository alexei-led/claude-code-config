# Claude Code Configuration

Custom configuration that makes Claude Code a development partner — with domain skills, automated hooks, and spec-driven workflows.

## How It Works

**Skills** are the core building blocks. Each skill teaches Claude a specific domain — writing Go, deploying infrastructure, reviewing code, running E2E tests. Skills activate automatically when you talk about their domain (the `skill-enforcer` hook detects patterns in your prompt), or you invoke them directly as `/skill-name`.

**Hooks** run automatically on events: suggest skills on every prompt, lint files after edits, protect sensitive files from accidental changes, show project context on session start.

**Spec-driven development** (`/spec:*` commands) manages structured requirements and tasks for larger projects. Initialize with `/spec:init`, work with `/spec:work`.

**Agents** are specialized subprocesses spawned by skills. Language engineers (`go-engineer`, `python-engineer`, `typescript-engineer`), language specialists for deep review (`go-qa`, `py-tests`, `ts-impl`, etc.), and utility agents (`infra-engineer`, `playwright-tester`). Skills orchestrate agents — you rarely spawn them directly.

## Quick Start

Just talk naturally. The skill enforcer suggests relevant skills based on your prompt:

- "write a Go HTTP handler" → `writing-go` activates
- "deploy to staging" → `deploying-infra` activates
- "review my code" → `reviewing-code` activates
- "improve tests" → `improving-tests` activates

For spec-driven projects: `/spec:init` → `/spec:work` → `/spec:done`.

## Environments

Switch API providers with `ce <env>`: `default` (Anthropic), `vertex`, `codex`, `gemini`, `deepseek`, `zai`.

## Remote Sessions

Control Claude Code from anywhere via Telegram using [ccbot](https://github.com/six-ddc/ccbot):

1. `ccbot` — starts bot, manages tmux session `ccbot`
2. `ce --tmux` — attach to the ccbot tmux session (or create one)
3. Inside tmux, use `ce <env>` to switch providers

Architecture: `1 Telegram Topic = 1 tmux Window = 1 Claude Code Session`. Set `CLAUDE_COMMAND=ce --current` in `~/.ccbot/.env` so new windows launch with the active env.

## Reference

See **GUIDE.md** for detailed usage of skills, agents, hooks, and remote sessions.
See **CLAUDE.md** for instructions that Claude follows in every session.
