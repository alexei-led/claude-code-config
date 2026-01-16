---
context: fork
argument-hint: [TASK-xxx]
allowed-tools:
  - Task
  - TaskOutput
  - Read
  - Edit
  - Write
  - Skill
  - AskUserQuestion
  - TodoWrite
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
  - Bash(git push:*)
  - Bash(make:*)
  - Bash(gh pr:*)
description: Main workflow - select, plan, implement, verify, done
---

# Spec Work

Full development workflow. One task per session.

## Usage

```
/spec:work                      # auto-select next task by priority
/spec:work TASK-xxx             # work on specific task
```

---

## Step 0: Check State

```bash
ls .spec/tasks 2>/dev/null || echo "NO_SPEC"
```

**If NO_SPEC**: "Run `/spec:init` first." Stop.

**Check for interrupted session:**

```bash
cat .spec/PROGRESS.md 2>/dev/null | tail -5
branch=$(git branch --show-current 2>/dev/null)
```

**If PROGRESS.md shows interrupted task** (SELECT without DONE) **and on task branch**: Resume from last step.

---

## Step 1: Select Task

**If TASK-xxx argument provided**: Use that task.

**Otherwise, find by priority:**

```bash
total=$(fd -e md . .spec/tasks/ | wc -l | tr -d ' ')
done_count=$(rg -l '^status: done' .spec/tasks/ 2>/dev/null | wc -l | tr -d ' ')

# Priority: critical → normal → low → any
next=$(rg -l '^priority: critical' .spec/tasks/ 2>/dev/null | xargs rg -l '^status: todo' 2>/dev/null | head -1)
[ -z "$next" ] && next=$(rg -l '^priority: normal' .spec/tasks/ 2>/dev/null | xargs rg -l '^status: todo' 2>/dev/null | head -1)
[ -z "$next" ] && next=$(rg -l '^status: todo' .spec/tasks/ 2>/dev/null | head -1)
```

**If no todo tasks**: "All tasks complete! 🎉" Stop.

**Load task content:**

Read the task file. Extract `implements:` link.

**Load linked requirement** (if any):

```bash
req_id=$(rg '^implements:' "$next" -o | cut -d' ' -f2)
[ -n "$req_id" ] && fd "$req_id.md" .spec/reqs/
```

Read requirement file if found.

**Log:**

```bash
task_id=$(basename "$next" .md)
echo "$(date +%H:%M) SELECT $task_id" >> .spec/PROGRESS.md
```

**Present:**

```
## Session

**Progress**: {done_count}/{total}
**Task**: {task_id}
**Priority**: {priority}
**Implements**: {req_id or "none"}

---

{task content}

---

### Linked Requirement
{requirement content or "none"}
```

**STOP**: `AskUserQuestion` - "Work on this? [Yes / Different task]"

---

## Step 2: Plan

**Spawn spec-planner:**

```
Task(
  subagent_type="spec-planner",
  prompt="Create implementation plan.
  Task: {task content}
  Requirement: {requirement content}
  Learn codebase style, return actionable plan."
)
```

**Log:**

```bash
echo "$(date +%H:%M) PLAN $task_id" >> .spec/PROGRESS.md
```

**Persist plan:** Append plan summary to task file under `## Plan` section.

**Present plan. STOP**: `AskUserQuestion` - "Approve? [Yes / Modify]"

---

## Step 3: Implement

**Create branch:**

```bash
git checkout -b "task/$task_id" 2>/dev/null || git checkout "task/$task_id"
echo "$(date +%H:%M) BRANCH task/$task_id" >> .spec/PROGRESS.md
```

**TodoWrite** from plan steps.

**Spawn engineer agent:**

```
Task(
  subagent_type="{go|python|typescript}-engineer",
  prompt="Implement: {task description}
  Plan: {plan}
  Return proposals only."
)
```

**Apply proposals** with user approval.

**Log:**

```bash
echo "$(date +%H:%M) IMPL $task_id" >> .spec/PROGRESS.md
```

---

## Step 4: Verify (Max 3 Attempts)

```bash
make build && make test && make lint
```

**If pass**: Continue to Step 5.

**If fail (attempt < 3)**:

```bash
echo "$(date +%H:%M) VERIFY fail $task_id attempt N" >> .spec/PROGRESS.md
```

Fix issues and re-verify.

**If fail (attempt = 3)**:

```bash
echo "$(date +%H:%M) VERIFY blocked $task_id" >> .spec/PROGRESS.md
```

**STOP**: `AskUserQuestion` - "Verify failed 3x. [Help fix / Skip verify / Stop]"

---

## Step 5: Complete

**Mark done:**

```
Edit: status: todo → status: done
```

**Log:**

```bash
echo "$(date +%H:%M) DONE $task_id" >> .spec/PROGRESS.md
```

**Commit:**

```
Skill(skill="committing-code")
```

**Push + PR:**

```bash
git push -u origin "task/$task_id"
gh pr create --title "task: {description}" --body "Implements $task_id"
```

**Cleanup PROGRESS.md** - keep last 5 entries:

```bash
tail -5 .spec/PROGRESS.md > /tmp/progress.tmp && mv /tmp/progress.tmp .spec/PROGRESS.md
```

**Summary:**

```
## Done

**Task**: {task_id}
**PR**: {url}
**Progress**: {done_count}/{total} → {new}

Next: `/spec:work`
```
