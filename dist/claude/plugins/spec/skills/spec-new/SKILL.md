---
allowed-tools:
- Write
- Bash(scripts/specctl *)
- Bash(mkdir *)
- Bash(date *)
- Bash(basename *)
- Bash(ls *)
- Bash(echo *)
argument-hint: <task|req> <name>
context: fork
description: Create a single TASK or REQ file from a template. Use for one-off artifact
  creation without the full planning workflow.
model: sonnet
name: spec-new
user-invocable: true
---

# `spec new` — create a single task or req from template

CLI at `scripts/specctl`. Input: `<type> <name>` where `<type>` is `task` or `req`. If `<name>` contains `/`, the leading part is a topic folder.

## Step 1: Ensure `.spec/` exists

```bash
ls .spec/ 2>/dev/null || mkdir -p .spec/tasks .spec/reqs
```

## Step 2: Determine path

- `task <name>` → `.spec/tasks/TASK-<name>.md`
- `task <topic>/<name>` → `.spec/tasks/<topic>/TASK-<name>.md`
- `req <name>` → `.spec/reqs/REQ-<name>.md`
- `req <topic>/<name>` → `.spec/reqs/<topic>/REQ-<name>.md`

## Step 3: Generate content

### Task template

```markdown
---
id: TASK-<name>
status: todo
priority: normal
implements:
---

# <Title>

(Describe the vertical slice, acceptance criteria, and out-of-scope boundaries.)
```

### Req template

```markdown
---
id: REQ-<name>
version: 1
priority: normal
---

# <Title>

(Describe requirements and success criteria.)
```

## Step 4: Write + log

Write the file, then append to the progress log:

```bash
echo "$(date +%H:%M) NEW <TYPE>-<name>" >> .spec/PROGRESS.md
```

Output:

```
Created: .spec/<type>s/<TYPE>-<name>.md
```
