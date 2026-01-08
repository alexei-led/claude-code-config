---
context: fork
allowed-tools:
  - Task
  - TaskOutput
  - TodoWrite
  - Read
  - Write
  - AskUserQuestion
  - Bash(jq:*)
  - Bash(git:*)
  - Bash(mkdir:*)
  - Bash(make:*)
  - Bash(chmod:*)
description: Initialize spec-driven project with feature_list.json
---

# Spec Init

Initialize a new spec-driven development project. Session 1 of many.

## Documentation Hierarchy

Spec-driven projects maintain layered documentation:

| Document              | Focus                  | Contains                                      |
| --------------------- | ---------------------- | --------------------------------------------- |
| `/docs/*.md`          | WHY (business context) | Research, architecture, guidelines, decisions |
| `app_spec.txt`        | WHY + WHAT             | Technical/functional requirements             |
| `feature_list.json`   | HOW                    | Implementation tasks (references app_spec)    |
| `claude-progress.txt` | STATE                  | Current session progress                      |

**Use TodoWrite** to track these 6 phases:

1. Project discovery
2. High-level documentation (docs/)
3. App specification
4. Feature list generation
5. Project setup
6. Summary

## Guardrails

- **Agent-first exploration**: Use agents for codebase analysis
- **User approval**: Confirm spec and feature list before creating
- **Quality over speed**: Thorough feature coverage is critical

---

## Phase 1: Project Discovery (Parallel)

**Spawn exploration agents in a single message:**

```
Task(
  subagent_type="Explore",
  run_in_background=true,
  description="Project structure scan",
  prompt="Project discovery: pwd, ls -la, detect language/framework (go.mod, package.json, pyproject.toml, Cargo.toml). Check for existing Makefile. Return: what exists, tech stack detected."
)

Task(
  subagent_type="Explore",
  run_in_background=true,
  description="Spec files check",
  prompt="Check spec-driven files: app_spec.txt existence, feature_list.json state, claude-progress.txt. Git status. Return: fresh start or continuation, what needs creation."
)
```

**Collect results:**

```
TaskOutput(task_id=<structure_id>, block=true)
TaskOutput(task_id=<spec_id>, block=true)
```

---

## Phase 2: High-Level Documentation

**If `/docs/` exists:** Read existing documents for context.

**If no `/docs/` directory:**

Use `AskUserQuestion` to gather high-level context:

| Header | Question                                              | Options                            |
| ------ | ----------------------------------------------------- | ---------------------------------- |
| Docs   | Do you have architecture/design documents to include? | Yes (will provide), None yet, Skip |

If user provides documents or context:

1. Create `docs/` directory
2. Create relevant files (architecture.md, guidelines.md, decisions.md)
3. Capture business context, constraints, and design decisions

**docs/architecture.md template:**

```markdown
# Architecture

## Overview

<System purpose and high-level design>

## Components

<Major components and their responsibilities>

## Constraints

<Technical and business constraints>
```

---

## Phase 3: App Specification

`app_spec.txt` captures **WHY and WHAT**, not HOW:

- Purpose and goals (WHY this exists)
- Requirements and success criteria (WHAT it must do)
- Constraints and boundaries (WHAT limits apply)

Implementation details (HOW) belong in `feature_list.json`.

**If `app_spec.txt` doesn't exist:**

Use `AskUserQuestion` to gather:

| Header  | Question                            | Options                                                                     |
| ------- | ----------------------------------- | --------------------------------------------------------------------------- |
| Purpose | What are you building?              | (free text via "Other")                                                     |
| Stack   | Which tech stack?                   | Go + stdlib, Python + FastAPI, TypeScript + React, TypeScript + Node, Other |
| Scope   | How complex is the initial version? | MVP (10-30 features), Standard (30-100 features), Comprehensive (100+)      |

Then create `app_spec.txt` using the gathered information.

**If `app_spec.txt` exists:** Read it for context.

---

## Phase 4: Feature List Generation

**Spawn agent for comprehensive feature generation:**

```
Task(
  subagent_type="Explore",
  description="Feature generation",
  prompt="Read app_spec.txt. Generate feature_list.json covering:
  - Every explicit and implied feature
  - Happy paths AND failure paths
  - API endpoints (valid/invalid/auth failure)
  - Form validation (required fields, edge values)
  - State transitions, error handling
  - Security boundaries

  Format: {category, description, steps[], passes: false}
  Categories: core|edge-case|error|integration|security|performance|style
  Target scope: [from user selection]
  Order by dependency: foundational first.
  Return complete JSON array."
)
```

**Present to user**: Summary of coverage (N features across M categories).

**STOP**: Use `AskUserQuestion` - "Review feature list? [Proceed / Show full list / Add more]"

---

## Phase 5: Project Setup

1. **Write `feature_list.json`** with generated features

2. **Create `init.sh`** (environment setup script):

```bash
#!/bin/bash
# init.sh - Run at session start to verify state
set -e

echo "=== Spec-Driven Session Start ==="

# Verify build
make build 2>/dev/null && echo "✓ Build passes" || echo "✗ Build needs attention"

# Verify tests
make test 2>/dev/null && echo "✓ Tests pass" || echo "✗ Tests need attention"

# Show next feature
echo ""
echo "Next feature to implement:"
jq '[.[] | select(.passes==false)][0] | .description' feature_list.json

# Show progress
total=$(jq 'length' feature_list.json)
passing=$(jq '[.[] | select(.passes==true)] | length' feature_list.json)
echo ""
echo "Progress: $passing/$total features passing"
```

3. **Create Makefile** (if not exists) - language-appropriate targets

4. **Initialize git** (if not a repo):

```bash
git init
chmod +x init.sh
git add feature_list.json Makefile app_spec.txt init.sh
git commit -m "Initial setup: spec-driven development scaffold"
```

5. **Create `claude-progress.txt`**:

```
# Progress Tracker

## Session 1 - Init

**Completed:**
- Created app_spec.txt
- Generated feature_list.json with N features
- Set up Makefile and init.sh

**Progress:** 0/N features (0%)

**Next Session:**
- Run `./init.sh` to verify state
- Start with first core feature
- Run /spec:work to continue
```

---

## Phase 6: Summary

Present to user:

```
## Init Complete

**Project**: <name>
**Features**: N total (M categories)
**Files Created**:
- app_spec.txt
- feature_list.json
- Makefile
- init.sh
- claude-progress.txt

**Next Step**: Run `/spec:work` to start implementing features
```

---

## CRITICAL INSTRUCTION

**Features are immutable after init.**

Removing or editing feature descriptions causes drift between spec and implementation, leading to untested functionality and broken contracts.

Preserve all feature descriptions exactly. Only modify the `"passes"` field: `false` → `true`

Request new init if additional features are needed.
