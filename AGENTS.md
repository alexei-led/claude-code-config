# cc-thingz

Portable skills, agents, and hooks for Claude Code, Codex CLI, Gemini CLI, and Pi — code review, language tooling, infrastructure, testing, and developer utilities. Platform-specific skills are excluded.

## Build

```bash
make build    # compile src/ → dist/ for all four targets (claude, codex, gemini, pi)
make fmt      # auto-fix ruff + shfmt + markdownlint
make check    # full lint (ruff, shellcheck, markdownlint, validate-config)
```

`make build` needs sandbox disabled — uv cache at `~/.cache/uv` is restricted in the CC sandbox.

## Writing Agent/Skill Instructions

LLM signal hierarchy (MDEval benchmark + Perplexity research):

- HIGH: `#` headers, bullet/numbered lists, code blocks — always use
- MEDIUM: `**bold**` — ≤15% of prose lines; use for bullet labels (`- **Label**: desc`) and critical keywords only
- LOW/zero: `_italic_`, `---` horizontal rules, markdown tables, mermaid/ASCII diagrams — never use

Specific rules:

- `**Label:**` on its own line → `### Label` (real header, not bold pseudo-header)
- `**Sentence.** followed by prose` → strip bold, keep as plain sentence
- `---` before `##` or `**bold` → remove (redundant section break)
- `---` before ` ```` ` fence → keep (it's template content showing proposal format)

Run format lint: `make lint-instructions` or use the `/reviewing-instructions` skill for full scoring.

## Agents

Three role agents. A role is a capability envelope plus a reasoning stance no skill can supply. Domain procedure and output format live in skills; language specifics live in each skill's `references/<lang>.md`. Role × skill × references compose — language is not a routing key. Consolidated 39 → 3 (see `docs/agent-audit-2026-05-16.md` and the executed plan in `docs/plans/completed/`).

Envelope enforcement is per-target: Claude grants a hard `tools:` allowlist; Codex blocks writes via `sandbox_mode: read-only`; Gemini and Pi have no tool-allowlist primitive, so the envelope there is a system-prompt directive. Descriptions state each role behaviorally so the claim stays true on every target, and omit "use proactively" deliberately — roles are picked by the orchestrator to compose with a skill, not auto-delegated.

- **engineer** — read + write + execute. The only mutator: applies changes and runs the build/test/lint verification on what it changed. Fork target for `writing-{go,python,typescript,web}` and `managing-infra`. Claude preloads `looking-up-docs` + `smart-explore`; `mem-history` and `sequential-thinking` stay Skill-discoverable to keep spawn context lean.
- **reviewer** — Read + Grep + Glob + LS. Adversarial evaluator (assume bugs exist); emits structured findings/proposals, applies nothing. Non-mutating: tool-enforced on Claude, write-blocked on Codex, directive on Gemini/Pi. Absorbs the review family, code search, and planning (via `spec` / `planning:make`).
- **advisor** — strategic escalation: verdict, ranked risks, next actions. Ships to Codex, Gemini, and Pi; excluded from Claude, which has a built-in advisor. Codex enforces read-only via sandbox; Pi uses xhigh thinking with read-only Bash and transcript-forwarding invocation; elsewhere it is spawned as a normal custom agent.

## Development Workflow

- **ccgram-messaging** — Inter-agent messaging via ccgram swarm
- **committing-code** — Smart git commits with logical grouping
- **documenting-code** — Update project documentation based on recent changes
- **fixing-code** — Fix code problems with disciplined diagnosis
- **improve-codebase-architecture** — Find deepening opportunities informed by domain language in CONTEXT.md and docs/adr/
- **improving-tests** — Improve test design and coverage, including TDD/red-green-refactor guidance
- **refactoring-code** — Batch refactoring via MorphLLM edit_file
- **reviewing-code** — Sequential code review for security, quality, tests, and architecture
- **searching-code** — Intelligent codebase search and zoom-out mapping via WarpGrep
- **spec** — Spec-driven development (init, interview, plan, work, status, done, help)
- **watch-team** — Monitor a team in tmux, auto-approve prompts, and report status

## Language Tooling

- **writing-go** — Idiomatic Go 1.25+ development
- **writing-python** — Idiomatic Python 3.12+ development
- **writing-typescript** — Idiomatic TypeScript development
- **writing-web** — Simple web development with HTML, CSS, JS, and HTMX

## Infrastructure & Operations

- **managing-infra** — Infrastructure patterns for Kubernetes, Terraform, Helm, Kustomize, and GitHub Actions
- **using-cloud-cli** — Cloud CLI patterns for GCP and AWS

## Developer Tools

- **brainstorming-ideas** — Brainstorm ideas and stress-test draft plans before coding
- **context7-cli** — Current library documentation via the ctx7 CLI
- **evolving-config** — Audit Claude Code configuration against latest features and best practices
- **exploring-repos** — Explore public GitHub repositories via DeepWiki AI-generated documentation
- **grill-me** — Interview the user relentlessly about a plan or design until reaching shared understanding
- **learning-patterns** — Extract learnings and generate project-specific customizations
- **looking-up-docs** — Compatibility router for library documentation lookup
- **mem-history** — Query project history, past decisions, and known gotchas from claude-mem observations
- **researching-web** — Web research via Perplexity AI
- **sequential-thinking** — Structured stepwise reasoning with explicit revisions and branches
- **smart-explore** — Token-efficient code navigation via AST parsing
- **using-git-worktrees** — Creates isolated git worktrees for parallel development
- **using-modern-cli** — Prefer modern CLI tools: rg, fd, bat, sd, eza over grep/find/cat/sed/ls

## End-to-End Testing

- **playwright-skill** — Internal Playwright automation library
- **testing-e2e** — Sequential E2E workflow
