---
allowed-tools:
  - Task
  - TaskOutput
  - TaskCreate
  - TaskUpdate
  - TaskList
  - AskUserQuestion
  - Read
  - Grep
  - Glob
  - LS
  - Bash(git *)
  - Bash(gh pr *)
  - Bash(gh api *)
  - Bash(rg *)
  - mcp__plugin_claude-mem_mcp-search__search
  - mcp__plugin_claude-mem_mcp-search__get_observations
argument-hint: "[deep] [team] [external] [architecture]"
context: fork
description:
  Code review covering security, quality, tests, implementation, documentation,
  and architecture / module-depth. Use when the user asks to review code, check changes,
  audit a PR or diff, find refactoring opportunities, or look for shallow modules
  and over-abstraction.
name: reviewing-code
user-invocable: true
---

# Code Review

Review changed code for security, quality, test coverage, and architecture. Ground every finding in concrete evidence: a `file:line` reference or tool output.

If a task-tracking facility is available, track these phases as tasks.

## Workflow

1. Determine review scope.
2. Detect languages from changed files.
3. Delegate to reviewer agents (one per detected language for a standard review; the thorough set per language for deep coverage).
4. Aggregate findings by severity and report.

Track progress through the workflow phases using `TaskCreate` / `TaskUpdate`.

If `$ARGUMENTS` is passed, the keywords below tune the workflow:

- `deep` — use the thorough-review agent set (full dimension coverage per language).
- `team` — run the reviewers as an agent team that challenges each other's findings and converges on consensus.
- `external` — additionally spawn external AI reviewers. Only when explicitly requested; never run by default.
- `architecture` — pass the Architecture vocabulary into every reviewer's prompt.

Without `external`, run only the language reviewers from this skill. Never spawn external reviewers implicitly.

## Determine scope

Ask the user which scope to review, with these options:

- Uncommitted changes
- Branch compared to the default branch
- Specific files (user provides paths)

Resolve to the appropriate git invocation and use it consistently across phases. If the user already named a scope in their request, use it without asking.

Use `AskUserQuestion` with header "Review scope" and the three options spelled out above.

## Detect languages

Scan the changed-file extensions and identify which language reviewers are needed.

## Delegate to reviewer agents

For each detected language, delegate to the agent(s) below in parallel if the runtime supports parallel sub-agents. Pass each agent: the scope, the project conventions (read `CONTEXT.md`/`docs/adr/` first), and whether architecture focus is requested.

**Standard review** — one agent per language:

- Go → `go-engineer`
- Python → `python-engineer`
- TypeScript → `typescript-engineer`
- Web (HTML / CSS / JS) → `web-engineer`

**Thorough review** — full dimension coverage per language:

- Go: `go-qa`, `go-idioms`, `go-tests`, `go-impl`, `go-docs`, `go-simplify`
- Python: `py-qa`, `py-idioms`, `py-tests`, `py-impl`, `py-docs`, `py-simplify`
- TypeScript: `ts-qa`, `ts-idioms`, `ts-tests`, `ts-impl`, `ts-docs`, `ts-simplify`
- Web: `web-qa`, `web-idioms`, `web-tests`, `web-impl`, `web-docs`, `web-simplify`

Dimension meanings (same across languages):

- `*-qa` — logic, security, OWASP, race conditions, unchecked errors, resource leaks
- `*-idioms` — patterns, conventions, stdlib usage, error handling
- `*-tests` — coverage, edge cases, mocking discipline
- `*-impl` — requirements match, dependency injection, edge cases
- `*-docs` — comments, docstrings, API docs (ARIA labels for web)
- `*-simplify` — over-abstraction, dead code, pass-throughs

If the runtime cannot spawn subagents, walk the dimensions sequentially as the main agent.

Spawn each agent via `Task(subagent_type="<name>", prompt=...)`. Each agent's model is set in its own metadata; do not pin a model from the skill.

When `team` is set, spawn the reviewers as an agent team so they challenge each other's findings; report format prefixes findings with `[Flagged by: agent1, agent2]`.

When `external` is set, additionally spawn in parallel:

- `Task(subagent_type="codex-assistant", prompt="review: code from <git_command>")` — security, quality, architecture from a second model.
- `Task(subagent_type="gemini-consultant", prompt="review: architecture of <git_command>")` — architecture alternatives and trade-offs.

## Review rules (passed to every reviewer)

- Cite concrete `file:line` evidence or tool output for every finding. No evidence, no finding.
- Findings include severity and a concrete fix.
- For security findings, remind the user: keep private code local; do not paste private diffs into web tools. Use web only for external facts (CVE, library docs); cite separately.
- Read relevant `CONTEXT.md`, `CONTEXT-MAP.md`, and `docs/adr/` before naming architecture findings. If a candidate contradicts an ADR, flag only when the friction justifies reopening the decision.
- Ask one clarifying question at a time; do not batch.

## Architecture vocabulary

Apply when the user asks for architecture focus. Pass these terms into reviewer prompts so findings use shared vocabulary:

- **Module** — anything with an interface and an implementation: function, class, package, slice.
- **Interface** — everything callers must know: types, invariants, ordering, error modes, config, performance.
- **Seam** — where an interface lives; a place behavior can change without editing in place.
- **Adapter** — a concrete thing satisfying an interface at a seam.
- **Depth** — leverage at the interface: lots of behavior behind a small interface.
- **Leverage** — caller value from depth.
- **Locality** — change, bugs, and verification concentrated in one place.

**Deletion test**: if deleting a module makes complexity vanish, it was a pass-through. If complexity reappears across callers, the module was earning its keep.

**Seam rule**: one adapter means a hypothetical seam; two adapters means a real seam. Do not propose ports without real variation.

## Historical context (optional)

If cross-session memory tooling is available, query for prior observations on the files about to be reviewed. Forward relevant findings into reviewer prompts so old issues are not re-litigated. Skip silently if no such tooling is configured.

If `mcp__plugin_claude-mem_mcp-search__search` is available, query for past findings on the files being reviewed:

```text
search({ query: "<file paths from git diff --name-only HEAD>", limit: 10 })
```

Fetch full observations via `get_observations` for relevant hits. Forward key findings into reviewer prompts. Skip silently if the MCP is not installed.

## Report format

```markdown
## Code Review Summary

**Scope**: <description>
**Languages**: <list>
**Reviewers**: <agents that ran>

### CRITICAL (must fix)

- [<agent>] `file:line` — issue. Fix.

### IMPORTANT (should fix)

- [<agent>] `file:line` — issue. Fix.

### SUGGESTIONS

- [<agent>] `file:line` — issue. Fix.

### Architecture opportunities (if requested)

- Candidate: `module`. Problem: shallow / pass-through / fake seam. Deepening move: <how>. Test benefit: <how>.

### Recommended actions

1. <prioritized list>
```

## Writing style

- One sentence per finding. No preamble, no "I noticed that…".
- Cut hedging: "potential", "might", "consider". State what is wrong.
- Direct: "This leaks memory" not "This could potentially lead to memory issues".
- Technical precision: include type names, function signatures, line numbers.

## Edge cases

- No changes in scope → "Nothing to review."
- Linters missing → say so explicitly; still review by reading.
- Tests missing → flag as a finding under the `*-tests` dimension.
- Runtime has no subagents → main agent performs the review sequentially using the same rubric.
