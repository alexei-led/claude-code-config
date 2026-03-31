# Claude Code Guide

Detailed usage for skills, agents, hooks, and spec-driven development.

---

## Plugin Details

### dev-workflow

Core development loop. Skills for committing, reviewing, fixing, documenting, refactoring, searching code, and improving tests. Ships with 24 review sub-agents (6 per language: Go, Python, TypeScript, Web) plus `docs-keeper`. Hooks: skill-enforcer, file-protector, smart-lint, session-start, notify, performance-monitor, test-runner.

### go-dev

`writing-go` skill with CLI patterns, testing idioms, and Go best practices. Includes `go-engineer` agent.

### python-dev

`writing-python` skill with uv/ruff/pyright toolchain, CLI patterns, and testing. Includes `python-engineer` agent.

### typescript-dev

`writing-typescript` skill with strict typing, React patterns, and testing. Includes `typescript-engineer` agent.

### web-dev

`writing-web` skill for vanilla HTML/CSS/JS and HTMX. Includes `web-engineer` agent.

### infra-ops

Skills for managing infrastructure (Kubernetes, Terraform, Helm, Dockerfiles, GitHub Actions, Makefiles), deploying, and using cloud CLIs (AWS, GCP). Includes `infra-engineer` agent.

### dev-tools

Utility skills: modern CLI tools (rg, fd, bat), git worktrees, docs lookup via Context7, web research via Perplexity, usage analysis, config evolution, brainstorming, dialectic debate, and pattern learning. Agents: `perplexity-researcher`, `pdf-parser`. Hooks: worktree-create, worktree-remove.

### spec-system

Spec-driven development with 8 slash commands (`/spec:init`, `/spec:interview`, `/spec:plan`, `/spec:work`, `/spec:status`, `/spec:new`, `/spec:done`, `/spec:help`). Includes `spec-planner` agent and `specctl` CLI.

### testing-e2e

E2E testing skills: `testing-e2e` for test strategy and `playwright-skill` for browser automation with Playwright. Includes `playwright-tester` agent.

---

## MCP Servers

Plugins use four MCP (Model Context Protocol) servers for capabilities beyond Claude's built-in tools. All are optional — skills and agents work without them but with reduced functionality.

### Context7

Library and framework documentation lookup. Fetches current docs for any library, so Claude doesn't rely on potentially outdated training data.

**Used by:** All 9 plugins — every language engineer agent, `docs-keeper`, `playwright-tester`, `looking-up-docs` skill, and `documenting-code` skill.

**What breaks without it:** Doc lookup skills return no results. Engineer agents can't verify API syntax against current docs.

### Perplexity

Web research via Perplexity AI. Searches the web for technical comparisons, best practices, and up-to-date information.

**Used by:** `dev-tools` (researching-web, looking-up-docs, evolving-config, brainstorming-ideas), `dev-workflow` (QA and simplify review agents), `infra-ops` (deploying-infra).

**What breaks without it:** `/researching-web` skill won't work. Review agents lose the ability to check current best practices. Config evolution can't discover new Claude Code features.

### Sequential Thinking

Step-by-step reasoning for complex planning and implementation tasks. Helps Claude break down multi-step problems systematically.

**Used by:** `go-dev`, `python-dev`, `typescript-dev`, `infra-ops` (all engineer agents), `spec-system` (spec-planner agent and `/spec:work` command).

**What breaks without it:** Engineer agents still work but may produce less structured plans. Spec planning loses its systematic decomposition.

### MorphLLM

Fast semantic codebase search (`warpgrep_codebase_search`, `codebase_search`) and batch file editing (`edit_file`) for large codebases.

**Used by:** `dev-workflow` (searching-code, refactoring-code), `go-dev`, `python-dev`, `typescript-dev`, `infra-ops` (all engineer agents), `spec-system` (`/spec:work`).

**What breaks without it:** Codebase search falls back to Grep/Glob (slower, less semantic). Batch refactoring loses the ability to edit multiple files in one operation.

### Per-Plugin MCP Usage

| Plugin             | Context7 | Perplexity | Sequential Thinking | MorphLLM |
| ------------------ | -------- | ---------- | ------------------- | -------- |
| **dev-workflow**   | yes      | yes        | —                   | yes      |
| **go-dev**         | yes      | —          | yes                 | yes      |
| **python-dev**     | yes      | —          | yes                 | yes      |
| **typescript-dev** | yes      | —          | yes                 | yes      |
| **web-dev**        | yes      | —          | —                   | —        |
| **infra-ops**      | yes      | yes        | yes                 | yes      |
| **dev-tools**      | yes      | yes        | —                   | —        |
| **spec-system**    | —        | —          | yes                 | yes      |
| **testing-e2e**    | yes      | —          | —                   | —        |

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

Skills live inside a plugin's `skills/` directory:

```
plugins/my-plugin/skills/skill-name/SKILL.md
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

### Agent Reference

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
| Web research               | `perplexity-researcher`   | sonnet |
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
| `notify.sh`              | Notification     | Desktop notifications for long operations   |
| `performance-monitor.sh` | PostCompact      | Tracks context compaction metrics           |
| `worktree-create.sh`     | WorktreeCreate   | Sets up isolated git worktree environment   |
| `worktree-remove.sh`     | WorktreeRemove   | Cleans up worktree on exit                  |

### Testing Hooks

```bash
echo '{"prompt":"deploy to staging"}' | plugins/dev-workflow/hooks/skill-enforcer.sh
# → Consider skills: deploying-infra
```

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
