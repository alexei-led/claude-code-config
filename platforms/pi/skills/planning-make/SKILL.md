---
name: planning-make
description: Create structured implementation plans in docs/plans/. Use when user asks to make a plan, implementation plan, rollout plan, or wants structured task breakdown before coding.
---

# Planning Make

Create a plan in `docs/plans/YYYYMMDD-<topic>.md`.

## Assumptions First

Before writing the plan:
- State assumptions.
- If intent is ambiguous, ask.
- If a simpler path exists, say so.
- Use `ask_user_question` for user choices and clarifications.
- If `structured_output` is available, use it for the final plan summary and next-step choices.

## Custom Rules

Load custom rules before planning:

```bash
bash ../planning-common/scripts/resolve-rules.sh planning-rules.md
```

If non-empty, treat them as extra planning constraints.

If the user wants rules management:
- show rules: run the script above and report the source file
- add/update project rules: write `.pi/planning-rules.md`
- add/update user rules: write `~/.pi/agent/planning-rules.md`
- clear project rules: delete `.pi/planning-rules.md`
- clear user rules: delete `~/.pi/agent/planning-rules.md`

Never edit skill files while managing rules.

See `../planning-common/references/custom-rules.md`.

## Step 0: Quick Context Scan

Use direct tools. No exhaustive archaeology.

- Feature work: inspect relevant files, top-level layout, existing patterns.
- Bug fix: grep for error text, read touched files, check `git log --oneline -5`.
- Refactor: inspect key files and dependency points.
- Unclear request: check `git status --short`, `git log --oneline -5`, `README.md`, `CLAUDE.md`, top-level dirs.

Rules:
- Keep scan under 30 seconds.
- Read at most 5 files before asking questions.
- For large ambiguous areas, use one background `scout` agent with a narrow prompt and a low `max_turns`; do not start an archaeology department.
- Use `web_answer` or `web_search` only for external APIs, standards, or current dependency behavior that affects the plan.
- Summarize findings in 3-5 bullets.

## Step 1: Ask One Question At A Time

Ask sequentially. Wait for each answer.

Use `ask_user_question`. One tool call per question.

1. Main goal
2. Scope: which components/files matter
3. Constraints: compatibility, deadlines, migration limits, no-refactor boundaries
4. Testing style: TDD or regular
5. Short plan title

Prefer multiple choice when the codebase scan suggests options.

## Step 1.5: Propose Approaches

Unless the path is obvious or user already chose one:
- Offer 2-3 approaches.
- Lead with the recommended option.
- Include trade-offs.
- Always include a minimal option.
- Use `ask_user_question` to make the user pick.

## Step 2: Write the Plan

Create `docs/plans/YYYYMMDD-<slug>.md` with this structure:

```markdown
# <Plan Title>

## Overview
- what changes
- why
- success criteria

## Context
- relevant files
- current patterns
- dependencies and risks

## Development Approach
- testing style: TDD or Regular
- finish one task before the next
- keep changes small and focused
- every task includes tests
- tests must pass before the next task
- update plan when scope changes

## Testing Strategy
- unit tests required for each task
- integration/e2e tests when applicable
- success, error, and edge cases

## Progress Tracking
- mark done with [x] immediately
- add discovered work with ➕
- add blockers with ⚠️
- keep the plan in sync with reality

## Solution Overview
- chosen approach
- key decisions
- why this fits the codebase

## Technical Details
- data shape changes
- control flow
- APIs, flags, config, migrations

## Implementation Steps

### Task 1: <specific goal>

**Files:**
- Create: `path/if-needed`
- Modify: `path/if-needed`

- [ ] implement the code change
- [ ] verify integration points
- [ ] write tests for success cases
- [ ] write tests for error or edge cases
- [ ] run relevant tests and make them pass

### Task N-1: Verify acceptance criteria
- [ ] verify requirements from Overview
- [ ] verify edge cases
- [ ] run full relevant test suite
- [ ] verify docs/config changes if needed

### Task N: Update documentation
- [ ] update README.md if user-visible behavior changed
- [ ] update CLAUDE.md or project docs if new conventions matter
- [ ] move this plan to `docs/plans/completed/` when done

## Post-Completion
- manual checks
- deploy or migration steps
- external follow-up
```

Plan rules:
- One logical unit per task.
- Use specific task names. No vague trash like "core logic".
- Each task lists files.
- Each task includes tests as separate checklist items.
- Keep scope tight. No speculative extras.

## Step 3: Next Step Prompt

After creating the plan, tell the user the file path and use `ask_user_question` to offer:
1. Review the plan
2. Review the plan with a `reviewer` or `planner` Agent if useful
3. Start implementation interactively
4. Execute the plan step by step in this session
5. Enter `/plan` mode for read-only review
6. Stop

If `structured_output` is available, use it for the final summary before asking.

If the user chooses implementation or execution, suggest `planning-exec`.
If the user chooses review, suggest `planning-review`.
If the user chooses `/plan`, tell them to run `/plan` and keep the session read-only until the plan is solid.
