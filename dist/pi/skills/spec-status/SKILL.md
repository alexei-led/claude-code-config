---
description: Report spec progress. Use when checking overall project state, viewing
  a specific task with its linked req/epic, listing tasks by status, or running a
  quality audit for orphans, cycles, and missing fields. NOT for mutating state —
  read-only; use spec-done or spec-work for state changes.
name: spec-status
---

<!-- Pi platform guidance -->
<!-- Use Pi tool names exactly: read, bash, edit, write, ask_user_question, structured_output, todo, Agent, get_subagent_result, steer_subagent, web_search, web_answer, web_research. -->
<!-- Use Agent, get_subagent_result, and steer_subagent for delegated work. -->
<!-- Use ctx7 or npx ctx7@latest through bash when Context7 documentation lookup is required. -->

# `spec status` — report progress

CLI at `scripts/specctl`. Match the user's request to one of these views:

- **Overview** — "what's the status", "show progress", no specific task named.
- **Specific task** — user names a `TASK-id`; show the task + its linked req/epic.
- **Filtered list** — user wants all tasks, just todo, or just completed.
- **Quality audit** — user wants to know about orphans, cycles, stale tasks, missing fields.

If `.spec/` doesn't exist, tell the user: "No `.spec/` folder. Use the `spec-init` skill to initialize the project." and stop.

## Overview

```bash
total=$(fd -e md . .spec/tasks/ | wc -l | tr -d ' ')
done=$(rg -l '^status: done' .spec/tasks/ 2>/dev/null | wc -l | tr -d ' ')
branch=$(git branch --show-current 2>/dev/null || echo "no-git")
```

Pick the next priority-ordered todo task:

```bash
next=$(rg -l '^priority: critical' .spec/tasks/ 2>/dev/null | xargs rg -l '^status: todo' 2>/dev/null | head -1)
[ -z "$next" ] && next=$(rg -l '^priority: normal' .spec/tasks/ 2>/dev/null | xargs rg -l '^status: todo' 2>/dev/null | head -1)
[ -z "$next" ] && next=$(rg -l '^status: todo' .spec/tasks/ 2>/dev/null | head -1)
```

Build a top-5 requirement rollup (tasks per REQ, with done counts).

Show:

```
## Spec status

Branch: <branch>
Tasks: <done>/<total> complete
Next ready: <task id or "none">

### Top requirements
- REQ-<slug>: <m>/<n> tasks done
- ...

### Suggested next
spec-work          # pick up the next ready task
spec-status list   # see every task
spec-status check  # quality audit
```

## Specific task

User passed a `TASK-id`. If no matching file exists under `.spec/tasks/`, say "Task not found." and stop.

Read the task file and any linked epic / requirement.

Show:

```
## TASK-<id>

Status: <status>
Priority: <priority>
Epic: <epic id or none>
Blocked by: <deps>

<task body>

### Epic
<epic overview>

### Requirement
<linked REQ summary>
```

## Filtered list

- `list` — every task
- `todo` — only `status: todo`
- `completed` — only `status: done`

Group by epic; show priority and a one-line summary per task.

## Quality audit

```bash
scripts/specctl validate
scripts/specctl status
```

Surface:

- Orphan tasks (no epic, no requirement link)
- Dependency cycles
- Tasks missing `acceptance` criteria
- Stale tasks (`status: in-progress` with no recent commits)
- Requirements with no associated tasks
- Epics with no tasks

For each issue, suggest the workflow that resolves it (usually `spec-interview` to enrich, `spec-plan` to add tasks, or manual edit).
