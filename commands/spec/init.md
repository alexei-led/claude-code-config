---
allowed-tools: Task, TaskOutput, Read, Write, AskUserQuestion, Bash(jq:*), Bash(git:*), Bash(mkdir:*), Bash(make:*), Bash(chmod:*)
description: Initialize spec-driven project with feature_list.json
---

# Spec Init

Initialize a new spec-driven development project. Session 1 of many.

## Guardrails

- **Agent-first exploration**: Use agents for codebase analysis
- **User approval**: Confirm spec and feature list before creating
- **Quality over speed**: Thorough feature coverage is critical

---

## Phase 1: Project Discovery

**Spawn `Explore` agent:**

```
Task(
  subagent_type="Explore",
  prompt="Project discovery: pwd, ls -la, app_spec.txt existence, feature_list.json state, git status, Makefile check, detect language/framework (go.mod, package.json, pyproject.toml). Return structured summary: what exists, what needs creation, fresh start or continuation."
)
```

---

## Phase 2: App Specification

**If `app_spec.txt` doesn't exist:**

Use `AskUserQuestion` to gather:

- What is being built? (purpose, target users)
- Tech stack preference? (Go/Python/TypeScript, framework)
- Key features? (list main functionality)

Then create `app_spec.txt` using the gathered information.

**If `app_spec.txt` exists:** Read it for context.

---

## Phase 3: Feature List Generation

**Spawn agent for comprehensive feature generation:**

```
Task(
  subagent_type="Explore",
  prompt="Read app_spec.txt. Generate feature_list.json covering: every explicit and implied feature, happy paths AND failure paths, API endpoints (valid/invalid/auth failure), form validation (required fields, edge values), state transitions, error handling, security boundaries. Format: {category, description, steps[], passes: false}. Categories: core|edge-case|error|integration|security|performance|style. Target 100-300 features. Order by dependency: foundational first. Return complete JSON array."
)
```

**Present to user**: Summary of coverage (N features across M categories).

**STOP**: Use `AskUserQuestion` - "Review feature list? [Proceed / Show full list / Add more]"

---

## Phase 4: Project Setup

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

3. **Create Makefile** (if not exists):

```makefile
.PHONY: init test build lint clean run help

help:          ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

init:          ## Install dependencies
test:          ## Run tests
build:         ## Build project
lint:          ## Run linters
clean:         ## Clean build artifacts
run:           ## Start application
```

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

## Phase 5: Summary

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
