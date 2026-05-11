# Quick reference

Present the following to the user as a readable summary (sections clearly separated, bullets, no decorative boxes). Then suggest the next workflow based on the current `.spec/` state.

## Workflows

- **init** — initialize `.spec/`, or add requirements from an existing doc
- **interview** — deep PRD-quality requirement capture via Q&A
- **plan** — create an EPIC + vertical-slice TASKs from a requirement or idea
- **new** — one-off task or requirement from a template
- **work** — implement the next ready task (one per session, with user approval at every step)
- **done** — mark a task complete with evidence; optionally discover or verify first
- **status** — overview, single-task detail, filtered list, or quality audit

## `specctl` commands (bundled CLI)

- `specctl init` — create the `.spec/` structure
- `specctl ready [--epic EPIC-x]` — list unblocked tasks, priority order
- `specctl show <REQ-x | EPIC-x | TASK-x>` — render an artifact
- `specctl start TASK-x` — mark in-progress, record base commit
- `specctl done TASK-x --summary ... --files ... --commits ... --tests ...` — close with evidence
- `specctl validate` — check for orphans, cycles, missing fields
- `specctl status` — global counts and progress
- `specctl dep add A B [--type X]` — add dependency with cycle check
- `specctl dep rm A B` — remove dependency
- `specctl epic close X` — mark an epic done
- `specctl session show | resume | step <name>` — session state and recovery
- `specctl hook install` — install git pre-commit validation

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

- No `.spec/` folder yet → run the **init** workflow
- Have an idea → run the **interview** workflow
- Have REQ files → run the **plan** workflow
- Have TASK files → run the **work** workflow
