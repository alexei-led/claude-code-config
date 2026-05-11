---
allowed-tools:
- Task
- TaskOutput
- TaskCreate
- TaskUpdate
- TaskList
- TodoWrite
- AskUserQuestion
- Read
- Write
- Edit
- Glob
- Grep
- mcp__morphllm__edit_file
- Bash(specctl *)
- Bash(rg *)
- Bash(fd *)
- Bash(wc *)
- Bash(head *)
- Bash(tail *)
- Bash(cat *)
- Bash(basename *)
- Bash(mkdir *)
- Bash(date *)
- Bash(echo *)
- Bash(make *)
- Bash(git *)
- Bash(gh pr *)
argument-hint: '[workflow] [args...]'
context: fork
description: Spec-driven development for AI coding agents — captures requirements,
  builds epics with vertical-slice tasks, runs implementation one task at a time with
  user approval, and tracks evidence-based completion. Use when the user wants to
  start a structured project, capture requirements for a feature, plan an epic, work
  on the next task, mark a task done, check progress, or otherwise drive a project
  through REQ → EPIC → TASK artifacts under `.spec/`.
model: sonnet
name: spec
user-invocable: true
---

# Spec-driven development

This skill manages a project's `.spec/` directory: requirements, epics, vertical-slice tasks, and progress. A bundled CLI (`scripts/specctl`) wraps the file conventions; the agent reads/writes the underlying markdown for everything else.

## When to use each workflow

Match the user's request to one of the workflows below and load the matching reference file:

- **Setting up a project or extending requirements from a document** — user wants to start tracking with `.spec/`, or has a doc/spec they want turned into requirements. See `references/init.md`.
- **Capturing requirements in depth** — user wants a thorough PRD-quality requirement built through structured Q&A. See `references/interview.md`.
- **Turning a requirement into an executable plan** — user has a `REQ-x` (or just an idea) and wants an epic with vertical-slice tasks, dependencies, and acceptance criteria. See `references/plan.md`.
- **Creating a single task or requirement from a template** — user wants a one-off `TASK-` or `REQ-` file (no full planning). See `references/new.md`.
- **Implementing the next task** — user wants to do the actual work: pick a ready task, plan it, implement with their approval, verify, mark done. See `references/work.md`.
- **Marking a task complete** — user has finished work on a specific task (or wants to discover which tasks look done). See `references/done.md`.
- **Checking progress** — user wants overview, a task detail, a filtered list, or a quality audit. See `references/status.md`.
- **Quick reference card** — user wants to know what the spec system can do. See `references/help.md`.

Pick the workflow by intent, not by literal keywords. "Let's plan REQ-auth", "create an epic for auth", and "spec plan REQ-auth" all map to the planning workflow.

## File structure

Every workflow reads/writes under `.spec/`:

- `.spec/reqs/REQ-<slug>.md` — requirements (WHAT / WHY)
- `.spec/epics/EPIC-<slug>.md` — epic grouping related tasks
- `.spec/tasks/TASK-<slug>.md` — vertical-slice task with acceptance criteria
- `.spec/memory/` — pitfalls, conventions, decisions discovered during work
- `.spec/SESSION.yaml` — current session state (task in progress, step, base commit)
- `.spec/PROGRESS.md` — append-only activity log

## Shared tool: `specctl`

The bundled CLI at `$SKILL_DIR/scripts/specctl` (resolve `$SKILL_DIR` to where this `SKILL.md` was loaded from) wraps the file operations. Run `specctl help` for the full command list. Key calls used across workflows:

- `specctl init` — initialize `.spec/` (idempotent)
- `specctl show REQ-x | EPIC-x | TASK-x` — render an artifact
- `specctl start TASK-x` — mark in-progress + record base commit
- `specctl done TASK-x --summary ... --files ... --commits ... --tests ...` — close with evidence
- `specctl ready [--epic EPIC-x]` — list tasks unblocked by dependencies, priority-ordered
- `specctl dep add A B [--type X]` / `specctl dep rm A B` — manage dependencies with cycle check
- `specctl session show | resume | step <name>` — current session state and recovery
- `specctl validate` — check for orphans, cycles, missing fields
- `specctl status` — global counts and progress

The CLI exists so workflow instructions stay short. If `specctl` is missing, fall back to direct file reads/writes following the file structure above.

## Cross-cutting rules

- **One task per session**. Complete it before starting the next.
- **User control over every edit**. Show diffs for approval; never silently overwrite.
- **Quality gates** before marking done: build, test, lint — or an explicit reason they were skipped.
- **REQ captures WHAT/WHY**; **task captures HOW** as vertical slices. Don't smear scope.
- **Blockers and open questions** stay in artifact frontmatter / body; don't invent a separate task type for "needs human decision".
- **Domain language lives in `CONTEXT.md`**, decisions in `docs/adr/`, rejected scope in `.out-of-scope/`. Reference these before naming architectural findings.

## Sequential pipeline

The workflows form a deterministic pipeline:

```
init → interview → plan → work → done
                            ↑___|  (loop until epic complete)
```

`status` reads state at any point. `new` and `help` are utility entry points.

## Edge cases

- No `.spec/` directory yet — only the init workflow is safe to start. Others should tell the user to set up the project first.
- Interrupted session (`.spec/SESSION.yaml` present) — the work workflow prompts to resume or clear before selecting a new task.
- `specctl` missing — degrade to direct file operations; warn the user once.

## Runtime mapping reminders

When a workflow says:

- _"Ask the user a multi-choice question"_ — use the runtime's native question facility (`AskUserQuestion`, `ask_user`, `ask_user_question`, or plain prose with explicit options).
- _"Delegate to a planning / exploration / implementation specialist"_ — spawn the runtime's subagent (`Task`, `spawn_agent`, `invoke_agent`, `Agent`) with the right role.
- _"Track progress through phases"_ — use the runtime's task-tracking tool if available.

Each reference keeps these phrasings generic; the model maps them to native tooling.
