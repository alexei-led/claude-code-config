---
description: Spec-driven development orientation and quick reference. Use when starting
  spec-driven development, unsure which sub-skill to use, or wanting a pipeline overview
  and current project state.
name: spec-core
---

# Spec-driven development

Show the user this quick reference, check `.spec/` state, and direct them to the right sub-skill.

## Pipeline

```
spec-init → spec-interview → spec-plan → spec-work → spec-done
                                               ↑___|  (loop until epic complete)
```

`spec-status` reads state at any point.

## Sub-skills

- `spec-init` — initialize `.spec/`, or add requirements from an existing doc
- `spec-interview` — deep PRD-quality requirement capture via Q&A
- `spec-plan` — create an EPIC + vertical-slice TASKs from a requirement or idea
- `spec-new` — one-off task or requirement from a template
- `spec-work` — implement the next ready task (one per session, user approval at every step)
- `spec-done` — mark a task complete with evidence; optionally discover or verify first
- `spec-status` — overview, single-task detail, filtered list, or quality audit

## specctl commands (bundled CLI)

CLI at `scripts/specctl`.

- `scripts/specctl init` — create the `.spec/` structure
- `scripts/specctl ready [--epic EPIC-x]` — list unblocked tasks, priority order
- `scripts/specctl show <REQ-x | EPIC-x | TASK-x>` — render an artifact
- `scripts/specctl start TASK-x` — mark in-progress, record base commit
- `scripts/specctl done TASK-x --summary ... --files ... --commits ... --tests ...` — close with evidence
- `scripts/specctl validate` — check for orphans, cycles, missing fields
- `scripts/specctl status` — global counts and progress
- `scripts/specctl dep add A B [--type X]` — add dependency with cycle check
- `scripts/specctl dep rm A B` — remove dependency
- `scripts/specctl epic close X` — mark an epic done
- `scripts/specctl session show | resume | step <name>` — session state and recovery
- `scripts/specctl hook install` — install git pre-commit validation

## File structure

- `.spec/reqs/REQ-*.md` — requirements (WHAT / WHY)
- `.spec/epics/EPIC-*.md` — epics grouping related tasks
- `.spec/tasks/TASK-*.md` — vertical-slice tasks with dependencies
- `.spec/memory/` — pitfalls, conventions, decisions discovered during work
- `.spec/SESSION.yaml` — current session (task, step, base commit)
- `.spec/PROGRESS.md` — activity log

## Principles

- REQ = WHAT / WHY (business requirements, success criteria)
- TASK = vertical slice with acceptance criteria
- Blockers and open questions stay in artifact frontmatter or body
- One task per session — complete before starting the next
- Quality gates: build, test, lint — every time
- User approves every edit — no hidden automation

## Where to start

```bash
scripts/specctl status 2>/dev/null || echo "NO_SPEC"
```

- No `.spec/` yet → use the `spec-init` skill to initialize the project
- Have an idea → use the `spec-interview` skill to capture requirements
- Have REQ files → use the `spec-plan` skill to create tasks
- Have TASK files → use the `spec-work` skill to implement the next task
