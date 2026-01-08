# Claude Code Configuration Development

Project-specific guidance for developing commands, agents, skills, and hooks.

## Command Development Patterns

### YAML Frontmatter

- Add `context: fork` for heavy analysis or intermediate output that would pollute main context
- Use array format: `allowed-tools: [Task, Bash(make *)]`
- Add `agent: <type>` for specialized execution routing
- Use `hooks:` with `once: true` for expensive checks

### Agent Types

| Agent                 | Use For                     |
| --------------------- | --------------------------- |
| Explore               | Quick codebase exploration  |
| go-engineer           | Go 1.25+ development        |
| python-engineer       | Python 3.14+ development    |
| typescript-engineer   | TypeScript 5.x development  |
| infra-engineer        | K8s, Terraform, Helm, CI/CD |
| playwright-tester     | E2E browser testing         |
| perplexity-researcher | Web research                |

### Agent Orchestration

- Spawn ALL independent agents in single message (parallel)
- Pattern: `run_in_background: true` → `TaskOutput(block=true)`
- Capture `agentId` for resumption: `Task(resume="<id>")`
- Reference implementation: `/code/commit.md`

### Multi-Phase Design

- 3+ phases → add TodoWrite for progress tracking
- Parallel spawns for analysis (read-only); sequential for application (writes)
- Include fallback logic ("if empty", "if no changes")

### Tool Selection

| Task                   | Use                         | Not             |
| ---------------------- | --------------------------- | --------------- |
| Find files             | Glob                        | find, ls        |
| Search content         | Grep                        | grep/rg in Bash |
| Read files             | Read                        | cat, head, tail |
| Codebase understanding | `warpgrep_codebase_search`  | Grep alone      |
| Batch refactoring      | `mcp__morphllm__edit_file`  | Multiple Edits  |
| Library docs           | `mcp__context7__query-docs` | WebSearch       |

Wildcards: `Bash(make *)`, `mcp__context7__*`, `mcp__playwright__*`

## Command Review Checklist

Before finalizing a command, verify:

- [ ] `context: fork` if spawns agents or modifies files
- [ ] `allowed-tools` uses array format with wildcards
- [ ] Multi-phase workflows have TodoWrite
- [ ] Background agents captured for resumption
- [ ] Fallback logic for empty/error cases
- [ ] No sequential loops that could be parallel

## Reference Commands

| Pattern                        | Example Command   |
| ------------------------------ | ----------------- |
| Background agents + TaskOutput | `/code/commit.md` |
| Multi-agent parallel review    | `/code/review.md` |
| Full spec workflow             | `/spec/work.md`   |

## Status Summary (from review)

| Status         | Count | Action                    |
| -------------- | ----- | ------------------------- |
| OPTIMAL        | 5     | Reference implementations |
| NEEDS_UPDATE   | 8     | Add missing features      |
| MAJOR_REFACTOR | 4     | Priority fixes needed     |

**Status**: All commands updated (2025-01)

## Skill Documentation Structure

Each skill in `~/.claude/skills/` should include:

- Purpose (1-2 lines), when to use / NOT use
- Decision tree or quick reference table
- Good/Bad examples with code
- Numbered workflow steps
- Error scenarios with fallbacks

### Reference Skills (Best Examples)

| Skill            | Pattern                                         |
| ---------------- | ----------------------------------------------- |
| writing-go       | Comprehensive (PATTERNS.md, TESTING.md, CLI.md) |
| managing-infra   | Agent + 5 supplementary guides                  |
| refactoring-code | Clear comparison tables, dryRun workflow        |
