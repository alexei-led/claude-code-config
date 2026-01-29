# Claude Code Configuration

Production-quality setup with specialized agents and zero-tolerance quality enforcement.

---

## Quick Start

```bash
fix issues          # or /fixing-code
review code         # or /reviewing-code
commit changes      # or /committing-code
research "topic"    # or /researching-web
```

---

## Spec-Driven Development (5 Commands)

| Command        | Verb   | Purpose                                 |
| -------------- | ------ | --------------------------------------- |
| `/spec:init`   | START  | Initialize project or add reqs          |
| `/spec:work`   | DO     | Main workflow - select, plan, implement |
| `/spec:status` | SEE    | Progress (args: list, todo, check)      |
| `/spec:new`    | CREATE | Create task or requirement              |
| `/spec:done`   | FINISH | Mark complete (args: discover, verify)  |

---

## Skills (User-Invocable)

| Skill                 | Triggers On                  |
| --------------------- | ---------------------------- |
| `brainstorming-ideas` | "brainstorm", "design"       |
| `fixing-code`         | "fix", "fix issues"          |
| `reviewing-code`      | "review", "review code"      |
| `committing-code`     | "commit", "save changes"     |
| `documenting-code`    | "update docs", "document"    |
| `checking-deploy`     | "deploy check", "validate"   |
| `looking-up-docs`     | Library docs via Context7    |
| `researching-web`     | "research", "compare X vs Y" |

---

## Agents

### Engineers

| Agent                 | Model | Focus              |
| --------------------- | ----- | ------------------ |
| `go-engineer`         | opus  | Go, stdlib-first   |
| `python-engineer`     | opus  | Python, type hints |
| `typescript-engineer` | opus  | TypeScript/React   |
| `infra-engineer`      | opus  | K8s, Terraform     |

### Specialists (deep reviews)

| Go            | Python        | TypeScript    |
| ------------- | ------------- | ------------- |
| `go-qa`       | `py-qa`       | `ts-qa`       |
| `go-tests`    | `py-tests`    | `ts-tests`    |
| `go-impl`     | `py-impl`     | `ts-impl`     |
| `go-idioms`   | `py-idioms`   | `ts-idioms`   |
| `go-docs`     | `py-docs`     | `ts-docs`     |
| `go-simplify` | `py-simplify` | `ts-simplify` |

### Spec + Utility

| Agent                   | Focus                     |
| ----------------------- | ------------------------- |
| `spec-planner`          | Implementation planning   |
| `docs-keeper`           | Documentation maintenance |
| `playwright-tester`     | E2E browser testing       |
| `perplexity-researcher` | Web research              |

---

## MCP Servers

| Server                | Purpose                   |
| --------------------- | ------------------------- |
| `context7`            | Library docs              |
| `sequential-thinking` | Multi-step reasoning      |
| `perplexity-ask`      | Web research              |
| `playwright`          | E2E browser testing       |
| `morphllm`            | Fast editing, code search |
| `gemini`              | Gemini AI queries         |
| `codex`               | OpenAI Codex agents       |

---

## Using Gemini/Codex Subscriptions

Use Claude Code with your Gemini or Codex subscription via CLIProxyAPI.

### Setup (one-time)

```bash
# 1. Install CLIProxyAPI
brew install cliproxyapi

# 2. Login with OAuth
cliproxy.sh --login-gemini  # For Gemini subscription
cliproxy.sh --login-codex   # For Codex/GPT subscription
```

### Usage

```bash
ce gemini           # Switch to Gemini + launch claude
ce codex            # Switch to Codex + launch claude
ce gm --continue    # Gemini with args
ce cx --continue    # Codex with args
```

### Models

| Provider | Opus                 | Sonnet/Haiku   |
| -------- | -------------------- | -------------- |
| Gemini   | gemini-3-pro-preview | gemini-3-flash |
| Codex    | gpt-5-codex-high     | gpt-5-codex    |

### Proxy Management

```bash
cliproxy.sh --status       # Check proxy status
cliproxy.sh --stop         # Stop proxy
ce --stop-cliproxy         # Alternative stop command
```

The proxy starts automatically when switching to gemini/codex.

---

## Hooks

| Hook             | Purpose                  |
| ---------------- | ------------------------ |
| `skill-enforcer` | Suggests relevant skills |
| `smart-lint`     | Auto-lints after edits   |
| `file-protector` | Protects sensitive files |

---

## Environment Switching (`ce`)

```bash
ce              # TUI picker
ce z            # Switch to z.ai + launch
ce --continue   # TUI + continue session
```

| Provider | Alias | Pricing |
| -------- | ----- | ------- |
| default  | max   | $20/mo  |
| vertex   | v     | Pay/use |
| zai      | z     | $0.40/M |
| deepseek | ds    | $0.28/M |

---

**[Complete Guide →](GUIDE.md)**
