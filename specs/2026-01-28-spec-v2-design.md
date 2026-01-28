# Spec-Driven Development v2 Design

## Overview

Enhance the spec-driven development system by adopting the best patterns from flow-next while maintaining user control and simplicity.

**Core Philosophy:** DESIGN → PLAN → IMPLEMENT with user approval at every step.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     DESIGN      │     │      PLAN       │     │   IMPLEMENT     │
│  /spec:interview│ ──▶ │   /spec:plan    │ ──▶ │   /spec:work    │
│                 │     │                 │     │                 │
│ Input: idea     │     │ Input: REQ-*.md │     │ Input: EPIC-*   │
│ Output: REQ-*.md│     │ Output: EPIC+   │     │ Output: code    │
│                 │     │   TASK files    │     │ + evidence      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
      │                       │                       │
      ▼                       ▼                       ▼
   WHAT/WHY               HOW/TASKS              EXECUTION
 (requirements)         (with deps)           (user control)
```

## File Structure

```
.spec/
├── PROGRESS.md          # Session state (auto-managed)
├── reqs/
│   └── REQ-*.md         # Requirements (WHAT) - from interview
├── epics/
│   └── EPIC-*.md        # Epics grouping tasks
├── tasks/
│   └── TASK-*.md        # Tasks with dependencies
└── config.yaml          # Optional defaults

scripts/
└── specctl.py           # CLI helper (~400 LOC)
```

## Commands

### `/spec:interview` (NEW)

Deep requirement gathering via 30-40 structured questions.

**Input Types:**
- Idea text: `"add OAuth login"` → Create new REQ-*.md
- Doc path: `docs/auth-spec.md` → Extract into REQ
- Existing REQ: `REQ-auth` → Refine with deeper questions

**Output:** Comprehensive REQ-*.md with problem, users, criteria, constraints, edge cases.

### `/spec:plan` (NEW)

Create epic with sized tasks and dependencies.

**Input:** REQ-*.md or existing EPIC to refine

**Output:** EPIC-*.md + TASK-*.md files with dependency graph

### `/spec:work` (ENHANCED)

Execute tasks with full user control.

**Changes:**
- Respects task dependencies via `specctl ready`
- Shows each edit for approval
- Tracks evidence on completion
- Suggests review + commit (doesn't auto-do)

### `/spec:help` (NEW)

Single-screen methodology guide with smart "start here" based on current state.

### Existing Commands (Unchanged)

- `/spec:init` - Initialize project
- `/spec:status` - Progress overview
- `/spec:done` - Mark complete (enhanced with evidence)
- `/spec:new` - Create files (enhanced with epic support)

## specctl.py CLI

**Location:** `~/.claude/scripts/specctl.py`

| Command | Purpose |
|---------|---------|
| `specctl init` | Create .spec/ structure |
| `specctl ready [--epic ID]` | Show unblocked tasks in dependency order |
| `specctl start <id>` | Mark task in-progress |
| `specctl done <id> --evidence "..."` | Mark done with evidence |
| `specctl validate [--all]` | Check for issues (cycles, missing fields) |
| `specctl status [ID]` | Progress overview |
| `specctl dep add <a> <b>` | A depends on B |

**Design:**
- ~400 LOC Python (simpler than flowctl's 1000)
- No JSON state - status in YAML frontmatter
- Git-friendly - all state in tracked markdown
- `--json` flag for machine-readable output

## File Formats

### REQ-*.md

```yaml
---
id: REQ-auth
version: 1
priority: critical
created: 2026-01-28
---
# User Authentication

## Problem
[What problem does this solve?]

## Users Affected
[Who benefits?]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Constraints
[Technical or business constraints]

## Edge Cases
[Known edge cases and handling]
```

### EPIC-*.md

```yaml
---
id: EPIC-auth
status: open
priority: critical
implements: REQ-auth
created: 2026-01-28
tasks:
  - TASK-auth-config
  - TASK-auth-google
---
# Authentication Implementation

## Overview
[Brief description]

## Approach
[High-level technical approach]

## Acceptance
- [ ] All REQ criteria met
- [ ] Tests pass
```

### TASK-*.md

```yaml
---
id: TASK-auth-config
status: todo
priority: normal
epic: EPIC-auth
blocked-by: []
size: S
---
# Configure OAuth Infrastructure

## Description
[What to build]

## Files
[Expected files to change]

## Acceptance
- [ ] Criterion 1
```

After completion, specctl appends:
```yaml
done-at: 2026-01-28T15:32:00Z
done-summary: |
  What was done
done-files: [file1, file2]
done-commits: [abc123]
done-tests: "test results"
```

## Key Design Decisions

### User Control (Not Worker Model)

Unlike flow-next's hidden worker:
- Each edit shown for approval
- User decides when to commit
- User decides if review needed
- Suggestions, not automation

### Simple State (No JSON)

Unlike flow-next's JSON + markdown split:
- All state in YAML frontmatter
- Single source of truth per file
- Git-friendly diffs
- No separate state directory

### Clean Abstractions

- REQ = WHAT (requirements, success criteria)
- EPIC = Grouping (tasks, dependencies, overview)
- TASK = HOW (implementation, acceptance)

## What NOT to Copy from flow-next

| flow-next Feature | Why Skip |
|-------------------|----------|
| Hidden worker agents | No visibility, can't course-correct |
| Auto-commit | Lose control of commit granularity |
| Auto-review | Can't skip for trivial changes |
| JSON state files | Overly complex, merge conflicts |
| Ralph autonomous mode | Over-engineered for interactive use |
| 20 specialized agents | Overkill - spec-planner + engineers sufficient |

## Implementation Order

1. **specctl.py** - Core CLI with init, ready, start, done, validate
2. **/spec:help** - Quick methodology reference
3. **/spec:interview** - Deep requirement gathering
4. **/spec:plan** - Epic + task creation with dependencies
5. **Enhance /spec:work** - Dependency-aware, evidence tracking
6. **Update /spec:status** - Show epic progress, dependencies
7. **Update /spec:done** - Integrate with specctl evidence

## Success Metrics

- Interview captures 2x more edge cases than brainstorming
- Dependency ordering prevents blocked task starts
- Evidence tracking provides audit trail
- User maintains full control over all edits
- Simpler than flow-next (~400 vs 1000 LOC CLI)
