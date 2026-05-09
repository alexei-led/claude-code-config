---
name: planning-exec
description: Execute implementation plans task by task with strict verification and plan tracking. Use when user wants to run a plan, execute tasks from docs/plans/, or implement from an existing plan.
---

# Planning Exec

Execute a plan file one task at a time.

Pi can use `Agent`, but the main loop still stays here: one task, verify it, update the plan, then continue.

## Inputs

Use the plan path from the user. If missing:
- list `docs/plans/*.md`
- exclude `docs/plans/completed/`
- if one plan exists, use it
- if several exist, ask which one with `ask_user_question`

## Before Coding

1. State assumptions.
2. Read the plan.
3. Load custom rules:

```bash
bash ../planning-common/scripts/resolve-rules.sh planning-rules.md
```

4. Check repo state:
   - `git status --short`
   - current branch
5. If work is non-trivial, ask with `ask_user_question` whether to use a git worktree or stay in the current directory.
6. If the user chooses isolation, use the `using-git-worktrees` skill.
7. If the plan is obviously wrong or stale, stop and fix the plan first.
8. If the `todo` tool is available, mirror the current task checklist there while keeping the markdown plan file as the source of truth.

## Execution Loop

Repeat until no unchecked boxes remain in `Implementation Steps`:

1. Re-read the plan.
2. Find the first task with unchecked items.
3. Announce the task title and unchecked items.
4. If `todo` is available, sync the current task checklist into `todo` before editing code.
5. Make only the changes required for that task.
6. Add or update tests required by the task.
7. Run the smallest relevant verification first, then broader tests if needed.
8. If verification fails, fix it before moving on.
9. Mark completed checklist items as `[x]` immediately.
10. If `todo` is in use, update it immediately as items complete.
11. If new work appears, add it to the plan with `➕`.
12. If blocked, add `⚠️` with the reason and stop.
13. Use `Agent` only for bounded review or recon work on large tasks, never as an excuse to lose control of the main loop.

## Subagent Pattern

Use background agents for independent work only:

```text
Agent({
  subagent_type: "reviewer",
  description: "Review task diff",
  run_in_background: true,
  prompt: "Review the current diff for the completed task. Return blockers only with file:line. Do not edit."
})
```

Do not let a worker agent run ahead of the plan unless the user explicitly chooses delegated implementation. If delegated, use `isolation: "worktree"` in a git repo for non-trivial edits.

## Hard Rules

- Do not silently skip tests.
- Do not start the next task with failing checks.
- Do not rewrite the whole codebase because one function annoyed you.
- Match existing style.
- Delete dead code introduced by the change.
- Keep `todo` and the markdown plan in sync if `todo` is in use.
- If scope expands beyond the plan, stop and ask with `ask_user_question`.

## Verification Discipline

For each task:
- reproduce or define the expected behavior
- implement
- run targeted tests
- run lint/typecheck if relevant to touched files
- update the plan after success

At the end:
- verify acceptance criteria task
- run the full relevant test suite
- update docs if needed
- move the plan to `docs/plans/completed/` only after everything passes

## Reporting

After each task, report:
- what changed
- what was verified
- plan file updates
- todo updates if used
- next task

If `structured_output` is available and the user wants a machine-readable checkpoint, use it.

Short. Factual.
