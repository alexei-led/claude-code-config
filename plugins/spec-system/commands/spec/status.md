---
model: haiku
argument-hint: [TASK-xxx | list | todo | completed | check]
allowed-tools:
  - Read
  - Grep
  - Bash(rg *)
  - Bash(fd *)
  - Bash(wc *)
  - Bash(head *)
  - Bash(cat *)
  - Bash(git branch *)
description: Progress overview with optional details
---

# Spec Status

Show progress. Use arguments for details.

## Usage

```
/spec:status                    # overview
/spec:status TASK-xxx           # show specific task + linked req
/spec:status list               # all tasks
/spec:status todo               # pending tasks only
/spec:status completed          # completed tasks only
/spec:status check              # quality audit
```

## Arguments

$ARGUMENTS

Parse: optional TASK-ID or mode (list, todo, completed, check).

---

## Mode: Default (Overview)

If no arguments:

```bash
ls .spec/tasks 2>/dev/null || echo "NO_SPEC"
```

**If NO_SPEC**: "No .spec/ folder. Run `/spec:init`." Stop.

```bash
total=$(fd -e md . .spec/tasks/ | wc -l | tr -d ' ')
done=$(rg -l '^status: done' .spec/tasks/ 2>/dev/null | wc -l | tr -d ' ')
branch=$(git branch --show-current 2>/dev/null || echo "no-git")

# Priority-ordered next task
next=$(rg -l '^priority: critical' .spec/tasks/ 2>/dev/null | xargs rg -l '^status: todo' 2>/dev/null | head -1)
[ -z "$next" ] && next=$(rg -l '^priority: normal' .spec/tasks/ 2>/dev/null | xargs rg -l '^status: todo' 2>/dev/null | head -1)
[ -z "$next" ] && next=$(rg -l '^status: todo' .spec/tasks/ 2>/dev/null | head -1)
```

**Requirement rollup** (top 5):

```bash
for req in $(fd -e md . .spec/reqs/ 2>/dev/null | head -5); do
  req_id=$(basename "$req" .md)
  req_total=$(rg -l "^implements: $req_id" .spec/tasks/ 2>/dev/null | wc -l | tr -d ' ')
  req_done=$(rg -l "^implements: $req_id" .spec/tasks/ 2>/dev/null | xargs rg -l '^status: done' 2>/dev/null | wc -l | tr -d ' ')
  [ "$req_total" -gt 0 ] && echo "$req_id: $req_done/$req_total"
done
```

**Recent progress:**

```bash
cat .spec/PROGRESS.md 2>/dev/null | tail -3
```

**Output:**

```
## Status

**Progress**: {done}/{total} tasks
**Branch**: {branch}
**Next**: {basename of next, or "all done"}

### Requirements
{rollup}

### Recent
{last 3 PROGRESS entries}
```

---

## Mode: Show Task (TASK-xxx argument)

If argument looks like a task ID (contains TASK- or matches task pattern):

```bash
fd "TASK-{id}.md" .spec/tasks/
```

Read task file. Extract `implements:` link. If found, read linked requirement.

**Output:**

```
## TASK-{id}

{task content}

---

### Linked: {REQ-id} (v{version})
{requirement content}
```

---

## Mode: List (list, todo, completed)

```bash
# list: all
fd -e md . .spec/tasks/

# todo: pending only
rg -l '^status: todo' .spec/tasks/

# completed: done only
rg -l '^status: done' .spec/tasks/
```

For each file, extract summary:

```bash
rg '^(id|status|priority|implements):' FILE | head -4
```

**Output:**

```
## Tasks ({filter})

| ID | Status | Priority | Implements |
|----|--------|----------|------------|
| TASK-auth-login | todo | critical | REQ-auth |
| TASK-auth-logout | todo | normal | REQ-auth |

{N} tasks
```

---

## Mode: Check (check)

Quality audit (read-only).

**Check requirements for HOW leakage:**

```bash
rg -l '(src/|\.go|\.ts|\.py|/api/|POST |GET )' .spec/reqs/ 2>/dev/null
```

**Check tasks for WHY leakage:**

```bash
rg -l '(users need|stakeholders|as a user|revenue)' .spec/tasks/ 2>/dev/null
```

**Check missing fields:**

```bash
for f in $(fd -e md . .spec/tasks/); do
  rg -q '^status:' "$f" || echo "Missing status: $f"
done
```

**Output:**

```
## Quality Check

### Abstraction Violations
{list or "none"}

### Missing Fields
{list or "none"}

### Summary
{N} issues found
```

---
