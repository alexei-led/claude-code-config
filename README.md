# cc-thingz

[![CI](https://github.com/alexei-led/cc-thingz/actions/workflows/ci.yml/badge.svg)](https://github.com/alexei-led/cc-thingz/actions/workflows/ci.yml)
[![GitHub tag](https://img.shields.io/github/v/tag/alexei-led/cc-thingz?label=version&sort=semver)](https://github.com/alexei-led/cc-thingz/tags)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin_marketplace-blueviolet)](https://docs.anthropic.com/en/docs/claude-code)
[![AGENTS.md](https://img.shields.io/badge/AGENTS.md-standard-000000)](https://agents.md)
[![Codex CLI](https://img.shields.io/badge/Codex_CLI-skill_export-10A37F)](https://developers.openai.com/codex/plugins)
[![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-skill_export-4285F4)](https://geminicli.com/docs/extensions)
[![Plugins](https://img.shields.io/badge/plugins-9-green)](plugins/)
[![Skills](https://img.shields.io/badge/skills-36-green)](plugins/)

A **Claude Code** plugin suite — 36 skills, 34 agents, 10 hooks, and 9 commands — with portable skill export for Codex CLI, Gemini CLI, Pi, and [AGENTS.md](https://agents.md)-compatible tools. Built over 6+ months of daily use and continuous refinement.

Built for Claude Code, with all 36 portable skills exported as platform-optimized instructions for Codex CLI, Gemini CLI, Pi, and any tool supporting the AGENTS.md standard.

## Why This Exists

AI coding tools are powerful out of the box, but specialized workflows need specialized prompts. After months of iterating on skills, agents, and hooks across Go, Python, TypeScript, infrastructure, and planning workflows, these plugins encode hard-won patterns:

- **Code review** with parallel multi-agent review and sequential lint-and-check workflows
- **Smart hooks** that auto-suggest skills, lint after edits, protect secrets, and run tests (Claude Code)
- **Spec-driven development** with structured requirements, tasks, and a CLI for project management
- **Infrastructure ops** with validated K8s, Terraform, and Helm deployments
- **Developer utilities** including worktree isolation, codebase search, web research, and brainstorming

Every skill has been manually crafted and refined through real-world use — not generated boilerplate.

## Installation

> Each section below assumes the corresponding CLI is already installed and on
> `PATH`. If you don't have the CLI yet, install it first
> ([Claude Code](https://docs.anthropic.com/en/docs/claude-code/quickstart),
> [Codex CLI](https://github.com/openai/codex),
> [Gemini CLI](https://github.com/google-gemini/gemini-cli),
> [Pi](https://pi.dev/docs/latest/quickstart)).
> The Pi flow does **not** require chezmoi by default — `scripts/install-pi-exports.sh`
> handles the symlinks. Chezmoi is an optional alternative described in
> [docs/pi-skill-export.md](docs/pi-skill-export.md#chezmoi-install).

### Claude Code

```bash
/plugin marketplace add alexei-led/cc-thingz
/plugin install dev-workflow@cc-thingz
/plugin install go-dev@cc-thingz
```

Use `--scope project` to install into `.claude/settings.json` for team sharing.

The `dev-workflow` plugin wires `smart-lint.sh` as a `PostToolUse` hook so
formatters and linters run automatically after every `Edit` / `Write`.

### OpenAI Codex CLI

```bash
git clone https://github.com/alexei-led/cc-thingz.git ~/src/cc-thingz
cd ~/src/cc-thingz
codex
# inside Codex: /plugins  → install plugins from this local marketplace
```

The marketplace manifest lives at `.agents/plugins/marketplace.json`; each
plugin has its own `plugins/<plugin>/.codex-plugin/plugin.json` and ships
SKILL.md files under `plugins/<plugin>/skills-codex/`. To use the skills
without the plugin marketplace, point Codex at the flat skill directory
instead:

```jsonc
// ~/.codex/config.json (excerpt)
{
  "skills": ["~/src/cc-thingz/flat/skills-codex"],
}
```

`dev-workflow` ships hooks via `plugins/dev-workflow/hooks/codex.hooks.json`:

- `PreToolUse` on `Bash` → `git-guardrails.sh` (blocks `git reset --hard`,
  `git push --force`, etc.)
- `PostToolUse` on `apply_patch` → `smart-lint.sh` (auto-format and lint
  changed files)
- `SessionStart` → `session-start.sh` (prints branch and last commit)

All commands resolve via `$PLUGIN_ROOT`, the env var Codex injects for
plugin-sourced hooks (works without Claude Code installed; Codex also
exports `$CLAUDE_PLUGIN_ROOT` as a compatibility alias).

### Google Gemini CLI

```bash
gemini extensions install https://github.com/alexei-led/cc-thingz
```

For local development, link the checkout instead of copying it:

```bash
gemini extensions link /path/to/cc-thingz
```

Gemini reads `gemini-extension.json` at the repo root, loads context from
`GEMINI.md` (auto-generated), and discovers per-skill SKILL.md files under
`flat/skills-codex/` (Gemini and Codex share the same overlay format).

`hooks/hooks.json` at the repo root registers:

- `BeforeTool` on `write_file|replace` → `file-protector.sh` (blocks writes
  to `.env`, credentials, `.pem`/`.key` files)
- `BeforeTool` on `run_shell_command` → `git-guardrails.sh` (blocks
  destructive git commands)
- `AfterTool` on `write_file|replace` → `smart-lint.sh` (auto-format and
  lint changed files)
- `SessionStart` → `session-start.sh` (prints branch and last commit)

All commands resolve via `${extensionPath}`, Gemini's substitution variable
for the extension root.

### Pi

Pi uses generated skills, agents, **and TypeScript extensions** that mirror
Claude-Code-native features (plan mode, todos, AskUserQuestion, subagents,
file/path protection, post-edit lint). Two third-party packages are
prerequisites — Pi pulls one in transitively, the other you must install:

- **[`@tintinweb/pi-subagents`](https://github.com/tintinweb/pi-subagents)** (or the
  [pinned fork](https://github.com/alexei-led/pi-subagents/tree/fix/pi-skill-discovery))
  provides the `Agent` / `get_subagent_result` / `steer_subagent` tools used
  by the `subagent` extension.
- **[`@mariozechner/pi-coding-agent`](https://www.npmjs.com/package/@mariozechner/pi-coding-agent)**
  is the `ExtensionAPI` that the bundled extensions import from. Pi pulls
  this in as a dependency; it's named here so you know where the API
  surface comes from.

```bash
git clone https://github.com/alexei-led/cc-thingz.git ~/src/cc-thingz
cd ~/src/cc-thingz

# 1. Install the subagent runtime (pick one):
pi install npm:@tintinweb/pi-subagents
# or for unreleased fixes:
# pi install git:github.com/alexei-led/pi-subagents@fix/pi-skill-discovery

# 2. Preview, then apply (no chezmoi needed):
scripts/install-pi-exports.sh                    # dry-run, prints plan
scripts/install-pi-exports.sh --apply            # creates symlinks
# optional: rebuild outputs first
scripts/install-pi-exports.sh --build --apply
```

The script symlinks:

- `~/.pi/agent/skills` → `~/src/cc-thingz/flat/skills-pi` (40 skills)
- `~/.pi/agent/agents` → `~/src/cc-thingz/flat/agents-pi` (5 agents)
- `~/.pi/agent/extensions` → `~/src/cc-thingz/flat/extensions-pi` (8 TypeScript extensions)

Existing `~/.pi/agent/skills`, `agents`, or `extensions` paths are moved to
timestamped backups before the symlinks are created. Override target with
`--target-dir <DIR>` or `PI_CODING_AGENT_DIR=<DIR>`. Restart Pi or run
`/reload` after applying.

**Bundled Pi extensions** (`platforms/pi/extensions/`):

| Extension              | Role                                                     |
| ---------------------- | -------------------------------------------------------- |
| `smart-lint.ts`        | Runs `smart-lint.sh` after every turn that wrote a file  |
| `ask-user-question.ts` | `ask_user_question` tool with structured options         |
| `permission-gate.ts`   | Confirms dangerous bash (rm -rf, sudo, chmod 777)        |
| `protected-paths.ts`   | Blocks writes to `.env`, `.git/`, `node_modules/`        |
| `plan-mode/`           | `/plan` toggle for read-only exploration, step tracking  |
| `todo.ts`              | `todo` tool + `/todos` command, branch-aware state       |
| `subagent/`            | Spawns isolated `pi` processes (single, parallel, chain) |
| `structured-output.ts` | `structured_output` tool that terminates the agent loop  |

For a chezmoi-managed alternative, see
[docs/pi-skill-export.md#chezmoi-install](docs/pi-skill-export.md#chezmoi-install).

**Pi gets**: 36 skills mirrored from plugins, plus 4 Pi-only planning skills
(`planning-common`, `planning-make`, `planning-exec`, `planning-review`) and
runtime subagents (`scout`, `planner`, `reviewer`, `worker`, `playwright-tester`).

### Other AGENTS.md-Compatible Tools

The `AGENTS.md` at the repo root provides a skill catalog readable by any tool supporting the [AGENTS.md standard](https://agents.md) (GitHub Copilot, Cursor, Windsurf, Devin, and others).

## Prerequisites

Portable docs lookup uses the [Context7 CLI](https://github.com/upstash/context7):

```bash
npm install -g ctx7@latest
# or with Bun:
bun add -g ctx7@latest

# one-shot (no global install):
npx ctx7@latest docs /facebook/react "React hooks"
# or with Bun:
bunx ctx7@latest docs /facebook/react "React hooks"
```

Claude Code agents can also use optional MCP servers for enhanced capabilities.
These are optional — plugins degrade gracefully without them. Pi exports do not
assume MCP tools.

| MCP Server                                                                                              | Purpose                                     | Used By                                                    |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ---------------------------------------------------------- |
| [DeepWiki](https://cognition.ai/blog/deepwiki-mcp-server)                                               | AI-generated wiki for public GitHub repos   | Claude Code dev-tools                                      |
| [Perplexity](https://github.com/ppl-ai/modelcontextprotocol)                                            | Web research and technical comparisons      | Claude Code dev-workflow, dev-tools, infra-ops             |
| [Sequential Thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) | Step-by-step reasoning for complex planning | Claude Code language, infra, and spec agents               |
| [MorphLLM](https://github.com/morphllm/morph-claude-code)                                               | Fast codebase search and batch file editing | Claude Code dev-workflow, language, infra, and spec agents |

### Claude-Mem Integration

All agents and several skills optionally integrate with [claude-mem](https://github.com/thedotmack/claude-mem) for cross-session memory and AST-based code navigation. Install with:

```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem@thedotmack
```

**What this enables:**

| Capability                    | Tools Used                                      | Benefit                                            |
| ----------------------------- | ----------------------------------------------- | -------------------------------------------------- |
| AST code navigation           | `smart_search`, `smart_outline`, `smart_unfold` | 10-20x fewer tokens than reading full files        |
| Cross-session memory          | `search`, `get_observations`, `timeline`        | Find past decisions, known gotchas, recurring bugs |
| Historical context in reviews | `search` + `get_observations`                   | Review agents check past findings before starting  |

**Graceful degradation**: All plugins work without claude-mem. When it's not installed, MCP tools are silently absent — agents fall back to Read/Grep/Glob, and skills skip history checks. No errors, no configuration needed.

**How it works**: Agent frontmatter lists claude-mem MCP tools alongside standard tools. Claude Code silently omits unavailable tools at runtime, so agents always have their core tools (Read, Grep, Glob, LSP) and gain smart_explore/memory tools when claude-mem is present. Skill instructions use "when available" / "if claude-mem available" phrasing to guide Claude's behavior.

## Plugins

| Plugin                                                 | Skills | Agents | Description                                                                        |
| ------------------------------------------------------ | ------ | ------ | ---------------------------------------------------------------------------------- |
| [**dev-workflow**](plugins/dev-workflow/README.md)     | 10     | 25     | Code review, fixes, commits, linting hooks, and 24 language-specific review agents |
| [**go-dev**](plugins/go-dev/README.md)                 | 1      | 1      | Idiomatic Go development with stdlib-first patterns, testing, and CLI tooling      |
| [**python-dev**](plugins/python-dev/README.md)         | 1      | 1      | Python 3.12+ development with uv/ruff/pyright toolchain                            |
| [**typescript-dev**](plugins/typescript-dev/README.md) | 1      | 1      | TypeScript with strict typing, React patterns, and modern tooling                  |
| [**web-dev**](plugins/web-dev/README.md)               | 1      | 1      | Web frontend with vanilla HTML, CSS, JavaScript, and HTMX                          |
| [**infra-ops**](plugins/infra-ops/README.md)           | 3      | 1      | Kubernetes, Terraform, Helm, GitHub Actions, AWS, GCP                              |
| [**dev-tools**](plugins/dev-tools/README.md)           | 17     | 2      | Modern CLI, git worktrees, docs lookup, web research, config review, brainstorming |
| [**spec-system**](plugins/spec-system/README.md)       | 0      | 1      | Spec-driven development: requirements, tasks, and planning workflows               |
| [**testing-e2e**](plugins/testing-e2e/README.md)       | 2      | 1      | E2E testing with Playwright: browser automation and test generation                |

**Totals**: 36 skills, 34 agents, 10 hooks, 9 commands

## Skills

Skills teach the AI model domain-specific knowledge and workflows. All skills are authored in cc-thingz and exported with platform-optimized instructions for Codex CLI, Gemini CLI, Pi, and [AGENTS.md](https://agents.md)-compatible tools. On Claude Code, the `skill-enforcer` hook auto-suggests relevant skills based on your prompt.

### User-Invocable

Invoke as `/skill-name` or let the skill enforcer suggest them.

| Skill                           | What It Does                                      | Example Trigger                          |
| ------------------------------- | ------------------------------------------------- | ---------------------------------------- |
| `brainstorming-ideas`           | Brainstorm ideas and stress-test draft plans      | "brainstorm", "design feature"           |
| `grill-me`                      | Relentless decision-tree interview on one plan    | "grill me", "stress-test this plan"      |
| `improve-codebase-architecture` | Find deepening opportunities, module/seam vocab   | "improve architecture", "deepen modules" |
| `committing-code`               | Smart git commits with logical grouping           | "commit", "save changes"                 |
| `debating-ideas`                | Dialectic agents stress-test design decisions     | "debate", "pros and cons"                |
| `deploying-infra`               | Validate + deploy K8s/Terraform/Helm              | "deploy to staging", "rollout"           |
| `documenting-code`              | Update docs based on recent changes               | "update docs", "document"                |
| `evolving-config`               | Audit config against latest Claude Code features  | "evolve", "audit config"                 |
| `exploring-repos`               | Explore public GitHub repos and architecture      | "explore repo", "how does repo work"     |
| `fixing-code`                   | Parallel agents fix all issues, zero tolerance    | "fix errors", "make it pass"             |
| `improving-tests`               | Refactor tests: combine to tabular, fill gaps     | "improve tests", "coverage"              |
| `context7-cli`                  | Current library docs via ctx7 CLI                 | "ctx7", "context7", "current docs"       |
| `looking-up-docs`               | Router for Context7 CLI docs lookup               | "look up docs", "API ref"                |
| `mem-history`                   | Query project history and prior decisions         | "last session", "what happened"          |
| `researching-web`               | Web research via Perplexity AI                    | "research", "X vs Y"                     |
| `reviewing-code`                | Multi-agent review (security, quality, idioms)    | "review code", "check this"              |
| `testing-e2e`                   | Playwright browser automation and test gen        | "e2e test", "playwright"                 |
| `analyzing-usage`               | Analyze Claude Code usage, cost, and efficiency   | "usage", "cost", "spending"              |
| `learning-patterns`             | Extract learnings and generate customizations     | "learn", "extract learnings"             |
| `linting-instructions`          | Lint plugin prompts against Anthropic model cards | "lint instructions", "audit prompts"     |
| `reviewing-cc-config`           | Review CC config for context efficiency           | "review config", "config review"         |
| `using-gemini`                  | Consult Gemini CLI for second opinions            | "ask gemini", "gemini search"            |
| `using-git-worktrees`           | Isolated git worktrees for parallel development   | "worktree", "isolate"                    |

### Auto-Activated

These activate silently when relevant patterns are detected — no `/skill-name` needed.

| Skill                | Activates When                                 |
| -------------------- | ---------------------------------------------- |
| `managing-infra`     | K8s resources, Terraform, Helm, GitHub Actions |
| `playwright-skill`   | Runtime library for testing-e2e skill          |
| `refactoring-code`   | Multi-file batch changes, rename everywhere    |
| `searching-code`     | "how does X work", trace flow, find all uses   |
| `smart-explore`      | Token-efficient local code navigation          |
| `using-cloud-cli`    | bq queries, gcloud/aws commands                |
| `using-modern-cli`   | rg, fd, bat, eza, sd instead of legacy tools   |
| `writing-go`         | Go files, go commands, Go-specific terms       |
| `writing-python`     | Python files, pytest, pip, frameworks          |
| `writing-typescript` | TS/TSX files, npm/bun, React, Node.js          |
| `writing-web`        | HTML/CSS/JS/HTMX templates                     |

## Agents

Claude Code uses the full plugin agent set below. Pi gets a small generated
runtime set in `flat/agents-pi/`: `scout`, `planner`, `reviewer`, `worker`, and
`playwright-tester`.

| Need                       | Agent                       | Model  |
| -------------------------- | --------------------------- | ------ |
| Go implementation          | `go-engineer`               | sonnet |
| Python implementation      | `python-engineer`           | sonnet |
| TypeScript implementation  | `typescript-engineer`       | sonnet |
| Deep Go QA/impl review     | `go-qa`, `go-impl`          | opus   |
| Deep Python QA/impl review | `py-qa`, `py-impl`          | opus   |
| Deep TS QA/impl review     | `ts-qa`, `ts-impl`          | opus   |
| Go/Py/TS/Web review        | `*-idioms`, `*-tests`, etc. | sonnet |
| Go/Py/TS/Web docs review   | `*-docs`                    | haiku  |
| Infrastructure validation  | `infra-engineer`            | sonnet |
| E2E browser testing        | `playwright-tester`         | sonnet |
| Implementation planning    | `spec-planner`              | sonnet |
| Documentation updates      | `docs-keeper`               | sonnet |
| Web research               | `perplexity-researcher`     | sonnet |
| PDF data extraction        | `pdf-parser`                | sonnet |

## Hooks (Claude Code only)

| Hook                     | Event            | What It Does                                 |
| ------------------------ | ---------------- | -------------------------------------------- |
| `session-start.sh`       | SessionStart     | Shows git branch, last commit, file context  |
| `skill-enforcer.sh`      | UserPromptSubmit | Pattern-matches prompt and suggests skills   |
| `file-protector.sh`      | PreToolUse       | Blocks edits to settings.json, secrets       |
| `git-guardrails.sh`      | PreToolUse       | Blocks destructive git commands              |
| `smart-lint.sh`          | PostToolUse      | Auto-runs linter after file edits            |
| `test-runner.sh`         | PostToolUse      | Auto-runs tests after implementation changes |
| `notify.sh`              | Notification     | Desktop notifications for long operations    |
| `performance-monitor.sh` | PostCompact      | Tracks context compaction metrics            |
| `worktree-create.sh`     | WorktreeCreate   | Sets up isolated git worktree environment    |
| `worktree-remove.sh`     | WorktreeRemove   | Cleans up worktree on exit                   |

## Skill Export Architecture

Skills are authored under `plugins/<plugin>/skills/<skill>/` and exported into
platform-specific outputs. Generated directories are committed so downstream
tools can consume them without running Python first.

| Target                 | Output                                                            | Notes                                                           |
| ---------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------- |
| Claude Code            | `plugins/*/skills/`, `plugins/*/agents/`, hooks, commands         | Source of rich Claude workflows                                 |
| Codex/Gemini/AGENTS.md | `plugins/*/skills-codex/`, `flat/skills-codex/`                   | Claude-only frontmatter stripped; platform preamble added       |
| Pi skills              | `plugins/*/skills-pi/`, `platforms/pi/skills/`, `flat/skills-pi/` | Pi tool names, ctx7 CLI docs, no MCP assumptions                |
| Pi agents              | `platforms/pi/agents/`, `flat/agents-pi/`                         | Flat `.md` files for `pi-subagents`; filename is the agent name |
| Pi extensions          | `platforms/pi/extensions/`, `flat/extensions-pi/`                 | TypeScript extensions for `pi.on(...)` events and custom tools  |

### Pi Export and Deployment

Pi uses generated flat exports as the source of truth:

```text
~/.pi/agent/skills      -> <repo>/flat/skills-pi
~/.pi/agent/agents      -> <repo>/flat/agents-pi
~/.pi/agent/extensions  -> <repo>/flat/extensions-pi
```

The symlinks are created by `scripts/install-pi-exports.sh --apply` (no chezmoi
needed). A chezmoi-managed alternative is described in
[docs/pi-skill-export.md](docs/pi-skill-export.md).

### Structure

```text
AGENTS.md                            # AGENTS.md standard (generated)
GEMINI.md                            # Gemini context file (generated)
.claude-plugin/marketplace.json      # Claude Code marketplace
.agents/plugins/marketplace.json     # Codex CLI marketplace
gemini-extension.json                # Gemini CLI extension manifest
platforms/pi/                        # Pi-only skills and agents
flat/                                # Unified symlink view
plugins/
├── dev-workflow/
│   ├── .claude-plugin/plugin.json
│   ├── .codex-plugin/plugin.json
│   ├── gemini-extension.json
│   ├── skills/                      # source skills
│   ├── skills-codex/                # Codex/Gemini build output
│   ├── skills-pi/                   # Pi build output
│   ├── agents/                      # Claude Code agents
│   ├── hooks/
│   └── commands/
└── ...
```

## Flat Directory

`flat/` provides a unified symlink view of all plugin components for tools that
need flat directory access. `AGENTS.md` and `GEMINI.md` are generated from
`flat/skills-codex/`. Pi deploys from `flat/skills-pi/`, `flat/agents-pi/`, and
`flat/extensions-pi/`.

Regenerate with:

```bash
make flat overlays pi-overlays pi-agents agents-md gemini-md
```

Validate with:

```bash
make validate
make test
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add plugins, run validation, and submit PRs.

## License

[MIT](LICENSE)
