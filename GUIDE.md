# Claude Code Guide

How to use skills, agents, hooks, and spec-driven development effectively.

---

## Skills

Skills teach Claude domain-specific knowledge and workflows. There are two kinds:

### User-Invocable (call directly)

Invoke as `/skill-name` or let the skill enforcer suggest them.

| Skill                 | What It Does                                     | Example Trigger                |
| --------------------- | ------------------------------------------------ | ------------------------------ |
| `brainstorming-ideas` | Collaborative design dialogue before coding      | "brainstorm", "design"         |
| `committing-code`     | Smart git commits with logical grouping          | "commit", "save changes"       |
| `debating-ideas`      | Dialectic agents stress-test design decisions    | "debate", "pros and cons"      |
| `deploying-infra`     | Validate + deploy K8s/Terraform/Helm             | "deploy to staging", "rollout" |
| `documenting-code`    | Update docs based on recent changes              | "update docs", "document"      |
| `evolving-config`     | Audit config against latest Claude Code features | "evolve", "audit config"       |
| `fixing-code`         | Parallel agents fix all issues, zero tolerance   | "fix errors", "make it pass"   |
| `improving-tests`     | Refactor tests: combine to tabular, fill gaps    | "improve tests", "coverage"    |
| `looking-up-docs`     | Library documentation via Context7               | "look up docs", "API ref"      |
| `researching-web`     | Web research via Perplexity AI                   | "research", "X vs Y"           |
| `reviewing-code`      | Multi-agent review (security, quality, idioms)   | "review code", "check this"    |
| `testing-e2e`         | Playwright browser automation and test gen       | "e2e test", "playwright"       |

### Auto-Activated (trigger on relevant prompts)

These activate silently when the skill enforcer detects matching patterns.

| Skill                 | Activates When                                 |
| --------------------- | ---------------------------------------------- |
| `learning-patterns`   | "learn from session", extract learnings        |
| `managing-infra`      | K8s resources, Terraform, Helm, GitHub Actions |
| `refactoring-code`    | Multi-file batch changes, rename everywhere    |
| `searching-code`      | "how does X work", trace flow, find all uses   |
| `using-cloud-cli`     | bq queries, gcloud/aws commands                |
| `using-git-worktrees` | Starting feature work needing isolation        |
| `using-modern-cli`    | rg, fd, bat, eza, sd instead of legacy tools   |
| `writing-go`          | Go files, go commands, Go-specific terms       |
| `writing-python`      | Python files, pytest, pip, frameworks          |
| `writing-typescript`  | TS/TSX files, npm/bun, React, Node.js          |
| `writing-web`         | HTML/CSS/JS/HTMX templates                     |

### How Skills Work

1. You type a prompt
2. The `skill-enforcer` hook (runs on every prompt) pattern-matches against skill triggers
3. If matched, it outputs `→ Consider skills: skill-name` as context
4. Claude loads the skill's `SKILL.md` and follows its workflow
5. Skills spawn agents, use tools, and produce structured output

### Creating Skills

```
~/.claude/skills/skill-name/SKILL.md
```

Key frontmatter fields:

- `name:` — skill identifier
- `description:` — trigger phrases for auto-activation
- `user-invocable: true|false` — whether it appears as `/skill-name`
- `context: fork` — if it spawns agents (prevents context pollution)
- `allowed-tools:` — tool restrictions
- `argument-hint:` — shows usage hint (e.g., `[run|record|generate]`)

---

## Agents

Agents are specialized subprocesses with their own context window and tool access. Skills orchestrate agents — you typically don't spawn them directly.

### When to Use Which Agent

| Need                       | Agent                     | Model  |
| -------------------------- | ------------------------- | ------ |
| Go implementation          | `go-engineer`             | opus   |
| Python implementation      | `python-engineer`         | opus   |
| TypeScript implementation  | `typescript-engineer`     | opus   |
| Deep Go review             | `go-qa`, `go-tests`, etc. | sonnet |
| Deep Python review         | `py-qa`, `py-tests`, etc. | sonnet |
| Deep TypeScript review     | `ts-qa`, `ts-tests`, etc. | sonnet |
| Infrastructure validation  | `infra-engineer`          | opus   |
| E2E browser testing        | `playwright-tester`       | opus   |
| Implementation planning    | `spec-planner`            | sonnet |
| Documentation updates      | `docs-keeper`             | sonnet |
| Web research               | `perplexity-researcher`   | haiku  |
| Quick codebase exploration | `Explore`                 | —      |

### Agent Patterns

**Parallel spawn** — for independent work:

```
Task(subagent_type="go-tests", run_in_background=true, ...)
Task(subagent_type="go-qa", run_in_background=true, ...)
# then collect:
TaskOutput(task_id=..., block=true)
```

**Sequential** — when output feeds the next step:

```
result = Task(subagent_type="Explore", prompt="find all auth handlers")
# use result to inform next agent
Task(subagent_type="go-engineer", prompt="refactor auth based on: {result}")
```

**Resume** — long-running agents return an `agentId`:

```
Task(resume="<agentId>")
```

### Agent Teams vs Subagents

| Scenario                           | Use      | Why                               |
| ---------------------------------- | -------- | --------------------------------- |
| Independent modules, parallel work | Teams    | Each teammate owns separate files |
| Code review, competing hypotheses  | Teams    | Reviewers challenge each other    |
| Research, report-back tasks        | Subagent | Simple, no file conflicts         |
| Same-file edits                    | Subagent | Avoids merge conflicts            |

---

## Hooks

Hooks run automatically on Claude Code events.

| Hook                     | Event            | What It Does                                |
| ------------------------ | ---------------- | ------------------------------------------- |
| `session-start.sh`       | SessionStart     | Shows git branch, last commit, file context |
| `skill-enforcer.sh`      | UserPromptSubmit | Pattern-matches prompt → suggests skills    |
| `file-protector.sh`      | PreToolUse       | Blocks edits to settings.json, secrets      |
| `smart-lint.sh`          | PostToolUse      | Auto-runs linter after file edits           |
| `notify.sh`              | PostToolUse      | Desktop notifications for long operations   |
| `performance-monitor.sh` | PostToolUse      | Tracks tool execution performance           |
| `test-runner.sh`         | PostToolUse      | Auto-runs tests after code changes          |

### Testing Hooks

```bash
echo '{"prompt":"deploy to staging"}' | ~/.claude/hooks/skill-enforcer.sh
# → Consider skills: deploying-infra
```

---

## Environments (`ce`)

Switch between API providers with the `ce` environment switcher.

### Quick Reference

```bash
ce                    # TUI picker → switch + launch claude
ce cx                 # Switch to codex → launch
ce gm --continue      # Switch to gemini → launch with --continue
ce --current          # Launch with last-used env (for ccbot)
ce --tmux             # Wrap in tmux session 'ccbot'
```

### Providers

| Env        | Alias | Provider                   | Best For                        |
| ---------- | ----- | -------------------------- | ------------------------------- |
| `default`  | `max` | Anthropic API              | Standard development            |
| `vertex`   | `v`   | Vertex AI                  | Enterprise, GCP integration     |
| `copilot`  | `cp`  | GitHub Copilot proxy       | Copilot subscription            |
| `codex`    | `cx`  | OpenAI Codex (CLIProxyAPI) | Code completion, fast iteration |
| `gemini`   | `gm`  | Gemini (CLIProxyAPI)       | Large context, multimodal       |
| `deepseek` | `ds`  | DeepSeek                   | Reasoning, cost-effective       |
| `zai`      | `z`   | Z.ai                       | Alternative provider            |

### Model Profiles

Model IDs are stored in `~/.claude/model-profiles.json` (not in settings.json). Each provider maps `opus`, `sonnet`, `haiku` to provider-specific model IDs.

```bash
ce --show-models          # Show resolved model IDs per provider
ce --show-models --json   # Machine-readable
ce --init-model-profiles  # Create default profiles (required on fresh setup)
ce --migrate-models       # Extract legacy model IDs from settings → profiles
ce --migrate-models=check # Dry run
```

**Without this file, proxy-based providers (codex, gemini) will fail** — Claude Code sends its default Anthropic model IDs (e.g. `claude-sonnet-4-5-20250929`) which the proxy doesn't recognize.

Per-provider env overrides: `CE_<PROVIDER>_OPUS`, `CE_<PROVIDER>_SONNET`, `CE_<PROVIDER>_HAIKU`.

### Effort Levels (Anthropic 4.6)

4.6 models use adaptive thinking — the model decides when and how deeply to reason.
Control via `effortLevel` in settings.json or `/model` per-session.

| Level    | Behavior                                            |
| -------- | --------------------------------------------------- |
| `low`    | Skip thinking for simple tasks, prioritize speed    |
| `medium` | Moderate thinking, may skip for simple queries      |
| `high`   | Deep thinking when useful (Opus default)            |
| `max`    | Maximum capability, no depth limits (Opus 4.6 only) |

### Thinking Levels (router-for-me, CLIProxyAPI)

For proxy providers (codex/gemini). Appends `(level)` to model names — the proxy strips the suffix and sets `reasoning_effort`.

```bash
ce cx --thinking=medium   # Override for this session
```

Levels: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `auto`. Codex default: `high`.

Resolution order: CLI flag → `CE_<PROVIDER>_THINKING` env → profile `"thinking"` field.

### CLIProxyAPI (codex/gemini)

Proxy-based providers require `cliproxyapi` running on localhost:8317.

```bash
# First-time setup
brew install cliproxyapi
cliproxy.sh --login-codex    # OAuth for Codex/GPT
cliproxy.sh --login-gemini   # OAuth for Gemini

# Proxy management
cliproxy.sh                  # Start in background
cliproxy.sh --status         # Check health
cliproxy.sh --stop           # Stop
```

`ce` auto-starts the proxy when switching to codex or gemini.

### Troubleshooting

| Error                                 | Cause                      | Fix                                     |
| ------------------------------------- | -------------------------- | --------------------------------------- |
| `unknown provider for model claude-*` | Missing model profiles     | `ce --init-model-profiles`              |
| `502 / connection refused`            | Proxy not running          | `cliproxy.sh` or `cliproxy.sh --status` |
| `401 / unauthorized`                  | Expired OAuth token        | `cliproxy.sh --login-codex`             |
| Legacy model keys warning             | Model IDs in settings.json | `ce --migrate-models`                   |

---

## Spec-Driven Development

For structured projects with requirements and tasks.

### Commands

| Command        | Purpose                                              |
| -------------- | ---------------------------------------------------- |
| `/spec:init`   | Initialize `.spec/` or add reqs from docs            |
| `/spec:work`   | Main loop: select → plan → implement → verify → done |
| `/spec:status` | Progress overview (`--list`, `--todo`, `--check`)    |
| `/spec:new`    | Create new task or requirement                       |
| `/spec:done`   | Mark complete (`--discover`, `--verify`)             |

### Structure

```
.spec/
├── reqs/           # REQ-*.md — WHAT (success criteria, constraints)
├── tasks/          # TASK-*.md — HOW (implementation steps)
└── PROGRESS.md     # Auto-managed session log (last 5 entries)
```

### Workflow

`/spec:init` → `/spec:work` (repeats) → `/spec:done`

Each `/spec:work` cycle: select a task → plan implementation → implement → verify → mark done.

---

## Remote Sessions (tmux + ccbot)

Control Claude Code from anywhere — desktop, SSH, or iPhone via Telegram using [ccbot](https://github.com/six-ddc/ccbot).

### Architecture

`1 Telegram Topic = 1 tmux Window = 1 Claude Code Session`

- **ccbot** — standalone bot that manages a tmux session, bridges Telegram messages to Claude
- **tmux** — session persistence (survives terminal close, SSH disconnect)
- **`ce --tmux`** — attach to the ccbot tmux session from a terminal

### Usage

```bash
# Start the bot (creates tmux session 'ccbot', manages windows)
ccbot

# Attach to the tmux session from terminal
ce --tmux

# Inside tmux, switch providers as usual
ce z              # switch to zai
ce default        # switch to default

# Custom tmux session name
ce --tmux=dev
```

ccbot creates windows and runs `CLAUDE_COMMAND` for each Telegram topic. Set `CLAUDE_COMMAND=ce --current` in `~/.ccbot/.env` — this launches with whatever env you last selected (including team).

### ccbot Telegram Commands

| Command                       | Action                   |
| ----------------------------- | ------------------------ |
| `/screenshot`                 | Terminal screenshot      |
| `/esc`                        | Interrupt Claude         |
| `/history`                    | Conversation history     |
| `/clear`, `/compact`, `/cost` | Forwarded to Claude Code |
| Any text                      | Sent as input to Claude  |

### Setup

1. Install: `uv tool install git+https://github.com/six-ddc/ccbot.git`
2. Config: `~/.ccbot/.env` (chezmoi + 1Password) — set `CLAUDE_COMMAND=ce --current`
3. Hook: `ccbot hook` on SessionStart (auto-registers sessions)
4. Run: `ccbot` directly (or via systemd/launchd for persistence)
