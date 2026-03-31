# cc-thingz

[![CI](https://github.com/alexei-led/cc-thingz/actions/workflows/ci.yml/badge.svg)](https://github.com/alexei-led/cc-thingz/actions/workflows/ci.yml)
[![GitHub tag](https://img.shields.io/github/v/tag/alexei-led/cc-thingz?label=version&sort=semver)](https://github.com/alexei-led/cc-thingz/tags)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin_marketplace-blueviolet)](https://docs.anthropic.com/en/docs/claude-code)
[![Plugins](https://img.shields.io/badge/plugins-9-green)](plugins/)
[![Skills](https://img.shields.io/badge/skills-29-green)](plugins/)

A battle-tested Claude Code plugin marketplace — 29 skills, 34 agents, 9 hooks, and 9 commands built over 6+ months of daily use and continuous refinement.

## Why This Exists

Claude Code is powerful out of the box, but specialized workflows need specialized prompts. After months of iterating on skills, agents, and hooks across Go, Python, TypeScript, infrastructure, and planning workflows, these plugins encode hard-won patterns that make Claude Code dramatically more effective:

- **Code review** that spawns 6 parallel agents per language (QA, tests, idioms, implementation, simplification, docs)
- **Smart hooks** that auto-suggest skills, lint after edits, protect secrets, and run tests
- **Spec-driven development** with structured requirements, tasks, and a CLI for project management
- **Infrastructure ops** with validated K8s, Terraform, and Helm deployments
- **Developer utilities** including worktree isolation, codebase search, web research, and brainstorming

Every skill and agent has been manually crafted and refined through real-world use — not generated boilerplate.

## Installation

Add the marketplace:

```bash
/plugin marketplace add alexei-led/cc-thingz
```

Install plugins you want:

```bash
/plugin install dev-workflow@cc-thingz
/plugin install go-dev@cc-thingz
/plugin install python-dev@cc-thingz
```

Use `--scope project` to install into `.claude/settings.json` for team sharing (default is user scope at `~/.claude/settings.json`).

## Prerequisites

Some plugins use MCP servers for enhanced capabilities. These are optional — plugins degrade gracefully without them, but you'll get the best experience with all four configured.

| MCP Server                                                                                              | Purpose                                     | Used By                                                                  |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------ |
| [Context7](https://github.com/upstash/context7)                                                         | Library and framework documentation lookup  | All 9 plugins                                                            |
| [Perplexity](https://github.com/ppl-ai/modelcontextprotocol)                                            | Web research and technical comparisons      | dev-workflow, dev-tools, infra-ops                                       |
| [Sequential Thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) | Step-by-step reasoning for complex planning | go-dev, python-dev, typescript-dev, infra-ops, spec-system               |
| [MorphLLM](https://github.com/morphllm/morph-claude-code)                                               | Fast codebase search and batch file editing | dev-workflow, go-dev, python-dev, typescript-dev, infra-ops, spec-system |

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
| [**dev-workflow**](plugins/dev-workflow/README.md)     | 7      | 25     | Code review, fixes, commits, linting hooks, and 24 language-specific review agents |
| [**go-dev**](plugins/go-dev/README.md)                 | 1      | 1      | Idiomatic Go development with stdlib-first patterns, testing, and CLI tooling      |
| [**python-dev**](plugins/python-dev/README.md)         | 1      | 1      | Python 3.12+ development with uv/ruff/pyright toolchain                            |
| [**typescript-dev**](plugins/typescript-dev/README.md) | 1      | 1      | TypeScript with strict typing, React patterns, and modern tooling                  |
| [**web-dev**](plugins/web-dev/README.md)               | 1      | 1      | Web frontend with vanilla HTML, CSS, JavaScript, and HTMX                          |
| [**infra-ops**](plugins/infra-ops/README.md)           | 3      | 1      | Kubernetes, Terraform, Helm, GitHub Actions, AWS, GCP                              |
| [**dev-tools**](plugins/dev-tools/README.md)           | 13     | 2      | Modern CLI, git worktrees, docs lookup, web research, brainstorming, Gemini        |
| [**spec-system**](plugins/spec-system/README.md)       | 0      | 1      | Spec-driven development: requirements, tasks, and planning workflows               |
| [**testing-e2e**](plugins/testing-e2e/README.md)       | 2      | 1      | E2E testing with Playwright: browser automation and test generation                |

**Totals**: 29 skills, 34 agents, 9 hooks, 9 commands

## Skills

Skills teach Claude domain-specific knowledge and workflows. The `skill-enforcer` hook auto-suggests relevant skills based on your prompt.

### User-Invocable

Invoke as `/skill-name` or let the skill enforcer suggest them.

| Skill                 | What It Does                                     | Example Trigger                 |
| --------------------- | ------------------------------------------------ | ------------------------------- |
| `brainstorming-ideas` | Collaborative design dialogue before coding      | "brainstorm", "design"          |
| `committing-code`     | Smart git commits with logical grouping          | "commit", "save changes"        |
| `debating-ideas`      | Dialectic agents stress-test design decisions    | "debate", "pros and cons"       |
| `deploying-infra`     | Validate + deploy K8s/Terraform/Helm             | "deploy to staging", "rollout"  |
| `documenting-code`    | Update docs based on recent changes              | "update docs", "document"       |
| `evolving-config`     | Audit config against latest Claude Code features | "evolve", "audit config"        |
| `fixing-code`         | Parallel agents fix all issues, zero tolerance   | "fix errors", "make it pass"    |
| `improving-tests`     | Refactor tests: combine to tabular, fill gaps    | "improve tests", "coverage"     |
| `looking-up-docs`     | Library documentation via Context7               | "look up docs", "API ref"       |
| `mem-history`         | Query past sessions and decisions (claude-mem)   | "last session", "what happened" |
| `researching-web`     | Web research via Perplexity AI                   | "research", "X vs Y"            |
| `reviewing-code`      | Multi-agent review (security, quality, idioms)   | "review code", "check this"     |
| `testing-e2e`         | Playwright browser automation and test gen       | "e2e test", "playwright"        |
| `using-gemini`        | Consult Gemini CLI for second opinions           | "ask gemini", "gemini search"   |

### Auto-Activated

These activate silently when the skill enforcer detects matching patterns.

| Skill                 | Activates When                                      |
| --------------------- | --------------------------------------------------- |
| `learning-patterns`   | "learn from session", extract learnings             |
| `managing-infra`      | K8s resources, Terraform, Helm, GitHub Actions      |
| `refactoring-code`    | Multi-file batch changes, rename everywhere         |
| `searching-code`      | "how does X work", trace flow, find all uses        |
| `smart-explore`       | AST code navigation via claude-mem (10-20x savings) |
| `using-cloud-cli`     | bq queries, gcloud/aws commands                     |
| `using-git-worktrees` | Starting feature work needing isolation             |
| `using-modern-cli`    | rg, fd, bat, eza, sd instead of legacy tools        |
| `writing-go`          | Go files, go commands, Go-specific terms            |
| `writing-python`      | Python files, pytest, pip, frameworks               |
| `writing-typescript`  | TS/TSX files, npm/bun, React, Node.js               |
| `writing-web`         | HTML/CSS/JS/HTMX templates                          |

## Agents

| Need                      | Agent                     | Model  |
| ------------------------- | ------------------------- | ------ |
| Go implementation         | `go-engineer`             | opus   |
| Python implementation     | `python-engineer`         | opus   |
| TypeScript implementation | `typescript-engineer`     | opus   |
| Deep Go review            | `go-qa`, `go-tests`, etc. | sonnet |
| Deep Python review        | `py-qa`, `py-tests`, etc. | sonnet |
| Deep TypeScript review    | `ts-qa`, `ts-tests`, etc. | sonnet |
| Infrastructure validation | `infra-engineer`          | opus   |
| E2E browser testing       | `playwright-tester`       | opus   |
| Implementation planning   | `spec-planner`            | sonnet |
| Documentation updates     | `docs-keeper`             | sonnet |
| Web research              | `perplexity-researcher`   | sonnet |

## Hooks

| Hook                     | Event            | What It Does                                 |
| ------------------------ | ---------------- | -------------------------------------------- |
| `session-start.sh`       | SessionStart     | Shows git branch, last commit, file context  |
| `skill-enforcer.sh`      | UserPromptSubmit | Pattern-matches prompt and suggests skills   |
| `file-protector.sh`      | PreToolUse       | Blocks edits to settings.json, secrets       |
| `smart-lint.sh`          | PostToolUse      | Auto-runs linter after file edits            |
| `test-runner.sh`         | PostToolUse      | Auto-runs tests after implementation changes |
| `notify.sh`              | Notification     | Desktop notifications for long operations    |
| `performance-monitor.sh` | PostCompact      | Tracks context compaction metrics            |
| `worktree-create.sh`     | WorktreeCreate   | Sets up isolated git worktree environment    |
| `worktree-remove.sh`     | WorktreeRemove   | Cleans up worktree on exit                   |

## Structure

```
.claude-plugin/marketplace.json
plugins/
├── dev-workflow/    # Core dev loop + review agents + hooks
├── go-dev/          # Go development
├── python-dev/      # Python development
├── typescript-dev/  # TypeScript development
├── web-dev/         # Web frontend
├── infra-ops/       # Infrastructure & cloud
├── dev-tools/       # Utilities & research
├── spec-system/     # Spec-driven development
└── testing-e2e/     # E2E testing with Playwright
```

## Flat Directory

`flat/` provides a unified symlink view of all plugin components for tools that need flat directory access (chezmoi, Codex CLI, Gemini CLI). Regenerate with:

```bash
scripts/generate-flat.sh
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add plugins, run validation, and submit PRs.

## License

[MIT](LICENSE)
