---
allowed-tools: Task, TaskOutput, Read, Write, Edit, AskUserQuestion, Bash(jq:*), Bash(git:*), Bash(mkdir:*), Bash(make:*), Bash(jq:*)
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

**Spawn `Explore` agent to analyze current state:**

```
Task(
  subagent_type="Explore",
  prompt="""
Explore the current directory:

1. Run `pwd` and `ls -la`
2. Check if `app_spec.txt` exists - summarize if yes
3. Check if `feature_list.json` exists - report state if yes
4. Check git status
5. Check for Makefile
6. Identify project structure (src/, pkg/, etc.)
7. Detect language/framework (go.mod, package.json, pyproject.toml)

Return structured summary:
- What exists already?
- What needs to be created?
- Is this fresh start or continuation?
"""
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

**Spawn agent to generate comprehensive feature list:**

```
Task(
  subagent_type="Explore",
  prompt="""
Based on app_spec.txt, generate a comprehensive feature_list.json.

Read app_spec.txt first, then create features covering:
- Every feature mentioned (explicit and implied)
- Happy path AND failure path for each flow
- API endpoints: valid, invalid, auth failure cases
- Form inputs: required fields, validation, edge values
- State transitions
- Error handling
- Security boundaries

Format for each feature:
{
  "category": "core|edge-case|error|integration|security|performance|style",
  "description": "What this test verifies",
  "steps": ["Step 1", "Step 2", "Step 3"],
  "passes": false
}

Aim for thorough coverage (typically 100-300 features).
Order by dependency: foundational features first.

Return the complete JSON array.
"""
)
```

**Present to user**: Summary of coverage (N features across M categories).

**STOP**: Use `AskUserQuestion` - "Review feature list? [Proceed / Show full list / Add more]"

---

## Phase 4: Project Setup

1. **Write `feature_list.json`** with generated features

2. **Create Makefile** (if not exists):

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

3. **Initialize git** (if not a repo):

```bash
git init
git add feature_list.json Makefile app_spec.txt
git commit -m "Initial setup: spec-driven development scaffold"
```

4. **Create `claude-progress.txt`**:

```
# Progress Tracker

## Session 1 - Init

**Completed:**
- Created app_spec.txt
- Generated feature_list.json with N features
- Set up Makefile

**Progress:** 0/N features (0%)

**Next Session:**
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
- claude-progress.txt

**Next Step**: Run `/spec:work` to start implementing features
```

---

## CRITICAL INSTRUCTION

**Features are immutable after init.**

Future sessions can ONLY:

- Mark `"passes": false` → `"passes": true`
- Never remove, reorder, or edit descriptions
- Never add new features (request new init if needed)

This ensures no functionality is missed.
