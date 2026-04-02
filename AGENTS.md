# cc-thingz Skills

A Claude Code plugin suite with portable skill export for Codex CLI, Gemini CLI, and AGENTS.md-compatible tools.

30 skills across 8 plugins — code review, language tooling, infrastructure, testing, and developer utilities.

## Development Workflow

| Skill | Description |
|-------|-------------|
| ccgram-messaging | Inter-agent messaging via ccgram swarm |
| committing-code | Smart git commits with logical grouping |
| documenting-code | Update project documentation based on recent changes |
| fixing-code | Sequential fix workflow |
| improving-tests | Sequential test improvement |
| refactoring-code | Batch refactoring via MorphLLM edit_file |
| reviewing-code | Sequential code review for security, quality, and architecture |
| searching-code | Intelligent codebase search via WarpGrep |

## Go Development

| Skill | Description |
|-------|-------------|
| writing-go | Idiomatic Go 1.25+ development |

## Python Development

| Skill | Description |
|-------|-------------|
| writing-python | Idiomatic Python 3.12+ development |

## TypeScript Development

| Skill | Description |
|-------|-------------|
| writing-typescript | Idiomatic TypeScript development |

## Web Development

| Skill | Description |
|-------|-------------|
| writing-web | Simple web development with HTML, CSS, JS, and HTMX |

## Infrastructure & Operations

| Skill | Description |
|-------|-------------|
| deploying-infra | Sequential infrastructure deployment |
| managing-infra | Infrastructure patterns for Kubernetes, Terraform, Helm, Kustomize, and GitHub Actions |
| using-cloud-cli | Cloud CLI patterns for GCP and AWS |

## Developer Tools

| Skill | Description |
|-------|-------------|
| analyzing-usage | Analyze Claude Code usage, cost, efficiency, and burn rate using ccusage and termgraph |
| brainstorming-ideas | Collaborative design workflow |
| debating-ideas | Dialectic thinking |
| evolving-config | Audit Claude Code configuration against latest features and best practices |
| learning-patterns | Extract learnings and generate project-specific customizations (CLAUDE.md, commands, skills, hooks) |
| linting-instructions | Lint plugin agent/skill prompts against rules derived from Anthropic model cards (Opus 4.6,... |
| looking-up-docs | Library documentation via Context7 |
| mem-history | Query project history, past decisions, and known gotchas from claude-mem observations |
| researching-web | Web research via Perplexity AI |
| smart-explore | Token-efficient code navigation via AST parsing |
| using-gemini | Consult Gemini for second opinions, brainstorming, or web search |
| using-git-worktrees | Creates isolated git worktrees for parallel development |
| using-modern-cli | Prefer modern CLI tools for better performance: rg (ripgrep) instead of grep for text searching,... |

## End-to-End Testing

| Skill | Description |
|-------|-------------|
| playwright-skill | Complete browser automation with Playwright. Auto-detects dev servers, writes clean test scripts... |
| testing-e2e | Sequential E2E workflow |
