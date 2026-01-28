---
context: fork
argument-hint: [EPIC-xxx | TASK-xxx]
allowed-tools:
  - Task
  - TaskOutput
  - Read
  - Edit
  - Write
  - Skill
  - AskUserQuestion
  - TodoWrite
  - Bash(specctl:*)
  - Bash(rg:*)
  - Bash(fd:*)
  - Bash(wc:*)
  - Bash(head:*)
  - Bash(tail:*)
  - Bash(date:*)
  - Bash(basename:*)
  - Bash(git checkout:*)
  - Bash(git branch:*)
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git push:*)
  - Bash(make:*)
  - Bash(gh pr:*)
description: Main workflow - select, plan, implement, verify, done
---

# Spec Work

Full development workflow. One task per session, with user control at every step.

## Usage

```
/spec:work                      # next ready task (respects dependencies)
/spec:work EPIC-xxx             # next ready task in specific epic
/spec:work TASK-xxx             # specific task
```

---

## Step 0: Check State

```bash
specctl status 2>/dev/null || echo "NO_SPEC"
```

**If NO_SPEC**: "Run `/spec:init` first." Stop.

**Check for interrupted session:**

```bash
cat .spec/PROGRESS.md 2>/dev/null | tail -5
branch=$(git branch --show-current 2>/dev/null)
```

**If PROGRESS.md shows interrupted task** (START without DONE) **and on task branch**: Resume from last step.

---

## Step 1: Select Task

**If TASK-xxx argument**: Use that task.

**If EPIC-xxx argument**: Get ready tasks from that epic.

**Otherwise**: Get next ready task (any epic).

```bash
# Get ready tasks (respects dependencies, priority-ordered)
specctl ready                           # all ready tasks
specctl ready --epic EPIC-xxx           # ready tasks in specific epic
```

**If no ready tasks**:

- Check blocked tasks: `specctl ready` shows blockers
- "No tasks ready. Check blocked tasks or create new work."
- Stop.

**Load task:**

```bash
specctl show TASK-xxx
```

Read task file. Check for epic link and requirement link.

**Load context:**

- Epic file (if `epic:` field exists)
- Requirement file (if `implements:` in epic)

**Mark in-progress:**

```bash
specctl start TASK-xxx
```

**Present:**

```
## Session

**Progress**: {done}/{total} tasks
**Task**: TASK-xxx
**Epic**: EPIC-xxx (if any)
**Priority**: {priority}
**Blocked by**: {deps or "none - ready to start"}

---

{task content}

---

### Context
**Epic**: {epic overview}
**Requirement**: {requirement summary}
```

**STOP**: `AskUserQuestion` - "Work on this task?"

| Header  | Question                 | Options                                                                                                                              |
| ------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| Confirm | Start work on {task_id}? | 1. **Yes, proceed** - Start planning<br>2. **Different task** - Pick another<br>3. **View full context** - Show epic and requirement |

---

## Step 2: Plan

**Spawn spec-planner:**

```
Task(
  subagent_type="spec-planner",
  prompt="Create implementation plan.
  Task: {task content}
  Epic: {epic content}
  Requirement: {requirement content}
  Learn codebase style, return actionable plan."
)
```

**Persist plan:** Append plan summary to task file under `## Plan` section.

**Present plan.**

**STOP**: `AskUserQuestion` - "Approve this plan?"

| Header | Question                          | Options                                                                                                                            |
| ------ | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Plan   | Approve this implementation plan? | 1. **Yes, implement** - Start coding<br>2. **Modify plan** - I'll explain changes<br>3. **More research** - Explore codebase first |

---

## Step 3: Implement

**Create branch:**

```bash
git checkout -b "task/$task_id" 2>/dev/null || git checkout "task/$task_id"
```

**TodoWrite** from plan steps.

**Spawn engineer agent:**

Detect language from task files or epic, then spawn appropriate agent:

```
Task(
  subagent_type="{go|python|typescript}-engineer",
  prompt="Implement: {task description}
  Plan: {plan}
  Return proposals only - do not apply edits."
)
```

**Apply proposals** with user approval (each edit shown).

---

## Step 4: Verify (Max 3 Attempts)

```bash
make build && make test && make lint
```

**If pass**: Continue to Step 5.

**If fail (attempt < 3)**:

- Show errors
- Fix issues
- Re-verify

**If fail (attempt = 3)**:

**STOP**: `AskUserQuestion` - "Verify failed 3 times"

| Header  | Question                               | Options                                                                                                                  |
| ------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Blocked | Verification failed 3 times. What now? | 1. **Help me fix** - Continue debugging<br>2. **Skip verify** - Mark done anyway<br>3. **Stop** - Leave task in progress |

---

## Step 5: Complete

**Collect evidence:**

```bash
# Files changed
git diff --name-only HEAD~1 2>/dev/null || git diff --name-only --cached

# Commits
git log --oneline -3
```

**Mark done with evidence:**

```bash
specctl done TASK-xxx \
  --summary "Brief summary of what was done" \
  --files "file1.ts,file2.ts" \
  --commits "abc123" \
  --tests "make test passed"
```

---

## Step 6: Review & Commit (User Choice)

**STOP**: `AskUserQuestion` - "Task complete. What next?"

| Header | Question                                                 | Options                                                                                                                                                                             |
| ------ | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Next   | Task implementation complete. What would you like to do? | 1. **Review changes** - Spawn review agent<br>2. **Commit now** - Create commit<br>3. **Push & PR** - Commit, push, create PR<br>4. **Continue to next task** - Skip commit for now |

### If Review

```
Skill(skill="reviewing-code")
```

### If Commit

```
Skill(skill="committing-code")
```

### If Push & PR

```bash
git push -u origin "task/$task_id"
gh pr create --title "feat: {task title}" --body "Implements TASK-xxx from EPIC-xxx"
```

---

## Step 7: Next Task

**Cleanup PROGRESS.md** - keep last 10 entries:

```bash
tail -10 .spec/PROGRESS.md > /tmp/progress.tmp && mv /tmp/progress.tmp .spec/PROGRESS.md
```

**Check for more ready tasks:**

```bash
specctl ready --epic EPIC-xxx  # if working on epic
specctl ready                  # otherwise
```

**Summary:**

```
## Done

**Task**: TASK-xxx
**Summary**: {done-summary}
**Files**: {changed files}

**Progress**: {done}/{total} tasks in epic

### Next Ready Tasks
{list from specctl ready}

Continue: `/spec:work` or `/spec:work EPIC-xxx`
```

---

## Key Principles

1. **User control**: Every edit shown for approval
2. **Dependency respect**: `specctl ready` orders by dependencies
3. **Evidence tracking**: `specctl done` records what was done
4. **Suggestions not automation**: Review and commit are offered, not forced
5. **One task per session**: Complete fully before starting next
