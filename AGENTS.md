<!-- Hand-maintained catalog of skills exported to AGENTS.md-compatible tools. Update when adding/removing/renaming a skill under src/skills/. -->

# cc-thingz Skills

A Claude Code plugin suite with portable skill export for Codex CLI, Gemini CLI, and AGENTS.md-compatible tools.

32 portable skills exported to Gemini under `dist/gemini/skills/` — code review, language tooling, infrastructure, testing, and developer utilities. Claude-only skills are not listed here.

## Development Workflow

| Skill                         | Description                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------------ |
| ccgram-messaging              | Inter-agent messaging via ccgram swarm                                                           |
| committing-code               | Smart git commits with logical grouping                                                          |
| documenting-code              | Update project documentation based on recent changes                                             |
| fixing-code                   | Fix code problems with disciplined diagnosis                                                     |
| improve-codebase-architecture | Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and... |
| improving-tests               | Improve test design and coverage, including TDD/red-green-refactor guidance                      |
| refactoring-code              | Batch refactoring via MorphLLM edit_file                                                         |
| reviewing-code                | Sequential code review for security, quality, tests, and architecture                            |
| searching-code                | Intelligent codebase search and zoom-out mapping via WarpGrep                                    |
| spec                          | Spec-driven development (init, interview, plan, work, status, done, help)                        |
| watch-team                    | Monitor a team in tmux, auto-approve prompts, and report status                                  |

## Go Development

| Skill      | Description                    |
| ---------- | ------------------------------ |
| writing-go | Idiomatic Go 1.25+ development |

## Python Development

| Skill          | Description                        |
| -------------- | ---------------------------------- |
| writing-python | Idiomatic Python 3.12+ development |

## TypeScript Development

| Skill              | Description                      |
| ------------------ | -------------------------------- |
| writing-typescript | Idiomatic TypeScript development |

## Web Development

| Skill       | Description                                         |
| ----------- | --------------------------------------------------- |
| writing-web | Simple web development with HTML, CSS, JS, and HTMX |

## Infrastructure & Operations

| Skill           | Description                                                                            |
| --------------- | -------------------------------------------------------------------------------------- |
| managing-infra  | Infrastructure patterns for Kubernetes, Terraform, Helm, Kustomize, and GitHub Actions |
| using-cloud-cli | Cloud CLI patterns for GCP and AWS                                                     |

## Developer Tools

| Skill               | Description                                                                                         |
| ------------------- | --------------------------------------------------------------------------------------------------- |
| brainstorming-ideas | Brainstorm ideas and stress-test draft plans before coding                                          |
| context7-cli        | Current library documentation via the ctx7 CLI                                                      |
| evolving-config     | Audit Claude Code configuration against latest features and best practices                          |
| exploring-repos     | Explore public GitHub repositories via DeepWiki AI-generated documentation                          |
| grill-me            | Interview the user relentlessly about a plan or design until reaching shared understanding,...      |
| learning-patterns   | Extract learnings and generate project-specific customizations (CLAUDE.md, CONTEXT.md, ADRs,...     |
| looking-up-docs     | Compatibility router for library documentation lookup                                               |
| mem-history         | Query project history, past decisions, and known gotchas from claude-mem observations               |
| researching-web     | Web research via Perplexity AI                                                                      |
| sequential-thinking | Structured stepwise reasoning with explicit revisions and branches                                  |
| smart-explore       | Token-efficient code navigation via AST parsing                                                     |
| using-git-worktrees | Creates isolated git worktrees for parallel development                                             |
| using-modern-cli    | Prefer modern CLI tools for better performance: rg (ripgrep) instead of grep for text searching,... |

## End-to-End Testing

| Skill            | Description                            |
| ---------------- | -------------------------------------- |
| playwright-skill | Internal Playwright automation library |
| testing-e2e      | Sequential E2E workflow                |

## Skill files

@dist/gemini/skills/brainstorming-ideas/SKILL.md
@dist/gemini/skills/ccgram-messaging/SKILL.md
@dist/gemini/skills/committing-code/SKILL.md
@dist/gemini/skills/context7-cli/SKILL.md
@dist/gemini/skills/documenting-code/SKILL.md
@dist/gemini/skills/evolving-config/SKILL.md
@dist/gemini/skills/exploring-repos/SKILL.md
@dist/gemini/skills/fixing-code/SKILL.md
@dist/gemini/skills/grill-me/SKILL.md
@dist/gemini/skills/improve-codebase-architecture/SKILL.md
@dist/gemini/skills/improving-tests/SKILL.md
@dist/gemini/skills/learning-patterns/SKILL.md
@dist/gemini/skills/looking-up-docs/SKILL.md
@dist/gemini/skills/managing-infra/SKILL.md
@dist/gemini/skills/mem-history/SKILL.md
@dist/gemini/skills/playwright-skill/SKILL.md
@dist/gemini/skills/refactoring-code/SKILL.md
@dist/gemini/skills/researching-web/SKILL.md
@dist/gemini/skills/reviewing-code/SKILL.md
@dist/gemini/skills/searching-code/SKILL.md
@dist/gemini/skills/sequential-thinking/SKILL.md
@dist/gemini/skills/smart-explore/SKILL.md
@dist/gemini/skills/spec/SKILL.md
@dist/gemini/skills/testing-e2e/SKILL.md
@dist/gemini/skills/using-cloud-cli/SKILL.md
@dist/gemini/skills/using-git-worktrees/SKILL.md
@dist/gemini/skills/using-modern-cli/SKILL.md
@dist/gemini/skills/watch-team/SKILL.md
@dist/gemini/skills/writing-go/SKILL.md
@dist/gemini/skills/writing-python/SKILL.md
@dist/gemini/skills/writing-typescript/SKILL.md
@dist/gemini/skills/writing-web/SKILL.md
