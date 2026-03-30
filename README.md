# cc-thingz

A Claude Code plugin marketplace with 9 installable plugins for development workflows, language-specific tooling, infrastructure ops, and more.

## Installation

Install all plugins at once:

```bash
/plugin marketplace add alexei-led/cc-thingz
```

Or install individual plugins:

```bash
/plugin marketplace add alexei-led/cc-thingz --plugin dev-workflow
/plugin marketplace add alexei-led/cc-thingz --plugin go-dev
```

## Plugins

| Plugin             | Skills | Agents | Description                                                                        |
| ------------------ | ------ | ------ | ---------------------------------------------------------------------------------- |
| **dev-workflow**   | 7      | 25     | Code review, fixes, commits, linting hooks, and 24 language-specific review agents |
| **go-dev**         | 1      | 1      | Idiomatic Go development with stdlib-first patterns, testing, and CLI tooling      |
| **python-dev**     | 1      | 1      | Python 3.12+ development with uv/ruff/pyright toolchain                            |
| **typescript-dev** | 1      | 1      | TypeScript with strict typing, React patterns, and modern tooling                  |
| **web-dev**        | 1      | 1      | Web frontend with vanilla HTML, CSS, JavaScript, and HTMX                          |
| **infra-ops**      | 3      | 1      | Kubernetes, Terraform, Helm, GitHub Actions, AWS, GCP                              |
| **dev-tools**      | 10     | 2      | Modern CLI, git worktrees, docs lookup, web research, brainstorming                |
| **spec-system**    | 0      | 1      | Spec-driven development: requirements, tasks, and planning workflows               |
| **testing-e2e**    | 2      | 1      | E2E testing with Playwright: browser automation and test generation                |

**Totals**: 26 skills, 34 agents, 9 hooks, 8 commands

## Plugin Details

### dev-workflow

Core development loop. Includes skills for committing, reviewing, fixing, documenting, refactoring, searching code, and improving tests. Ships with 24 review sub-agents (6 per language: Go, Python, TypeScript, Web) plus `docs-keeper`. Hooks: skill-enforcer, file-protector, smart-lint, session-start, notify, performance-monitor, test-runner.

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

Utility skills: modern CLI tools (rg, fd, bat), git worktrees, docs lookup via Context7, web research via Perplexity, usage analysis, config evolution, Gemini integration, brainstorming, dialectic debate, and pattern learning. Agents: `perplexity-researcher`, `pdf-parser`. Hooks: worktree-create, worktree-remove.

### spec-system

Spec-driven development with 8 slash commands (`/spec:init`, `/spec:interview`, `/spec:plan`, `/spec:work`, `/spec:status`, `/spec:new`, `/spec:done`, `/spec:help`). Includes `spec-planner` agent and `specctl` CLI.

### testing-e2e

E2E testing skills: `testing-e2e` for test strategy and `playwright-skill` for browser automation with Playwright. Includes `playwright-tester` agent.

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

## Versioning

All plugins start at `1.0.0`. Git tags per plugin: `dev-workflow-v1.0.0`, `go-dev-v1.1.0`, etc.

- **major** — breaking changes (renamed skills, changed behavior)
- **minor** — new skills or agents
- **patch** — fixes and refinements

## CI

GitHub Actions validates on every push:

1. Config validation — frontmatter and cross-references
2. Python linting — ruff
3. Shell linting — shellcheck
4. Smoke tests — pytest

## Further Reading

See [GUIDE.md](GUIDE.md) for detailed usage: skill invocation, agent coordination, hook behavior, and spec-driven development workflow.
