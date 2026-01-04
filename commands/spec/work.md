---
allowed-tools: Task, TaskOutput, Read, Edit, Write, Skill, AskUserQuestion, TodoWrite, Bash(jq:*), Bash(git checkout:*), Bash(git branch:*), Bash(git status:*), Bash(git log:*), Bash(make:*)
description: Continue spec-driven development session
---

# Spec Work

Continue spec-driven development. Main context = orchestration only.

## Guardrails

- **Agent-first**: All exploration/analysis in subagents
- **Progress-first**: Always start with discovery
- **Branch-per-feature**: Work in `feature/<name>` branch
- **User-approval**: Explicit approval before implementation
- **Passes-only**: Only modify `"passes"` field in `feature_list.json`
- **Clean-exit**: End with committed code and updated progress

---

## Phase 1: Discovery (Parallel Background)

**Spawn BOTH agents in a single message for parallel execution:**

```
Task(
  subagent_type="spec-discover",
  run_in_background=true,
  description="Discovery scan",
  prompt="Full project discovery - return structured summary"
)

Task(
  subagent_type="spec-planner",
  run_in_background=true,
  description="Style learning",
  prompt="Learn codebase patterns only (skip planning). Return style guide section."
)
```

## Phase 2: Collect & Present

**Collect results:**

```
TaskOutput(task_id=<discover_id>)
TaskOutput(task_id=<planner_id>)
```

**Present to user** (10 lines max):

```
## Session Start

**Project**: <name>
**Progress**: X/Y passing (Z%)
**Next Feature**: <description>

Ready to plan implementation?
```

**STOP**: Use `AskUserQuestion` - "Proceed with planning for this feature?"

---

## Phase 3: Planning

**Spawn `spec-planner` agent with feature context:**

```
Task(
  subagent_type="spec-planner",
  prompt="""
Create implementation plan for:

Feature: <description>
Steps: <steps from feature_list.json>

App Context: <from discovery>
Style Guide: <from style learning>

Return full implementation plan.
"""
)
```

**Spawn language-appropriate reviewer in parallel** (based on detected language):

- Go: `go-idioms`
- Python: `py-idioms`
- TypeScript: `ts-docs`

```
Task(
  subagent_type="<language>-idioms",
  run_in_background=true,
  prompt="Review this plan for idiomatic code: <plan summary>"
)
```

**Present plan summary to user** (bullet points only).

**STOP**: Use `AskUserQuestion` - "Approve this plan? [Yes / Modify / Different approach]"

---

## Phase 4: Implementation

1. **Create feature branch**: `git checkout -b feature/<feature-name>`

2. **Create TodoWrite** from approved plan

3. **Spawn appropriate engineer agent:**
   - Go: `go-engineer`
   - Python: `python-engineer`
   - TypeScript: `typescript-engineer`

```
Task(
  subagent_type="<language>-engineer",
  prompt="""
Implement this feature:

Plan: <approved plan>
Style Guide: <from Phase 1>
Reference Files: <from plan>

Follow the plan exactly. Run verification after each step.
"""
)
```

---

## Phase 5: Verification

**Spawn `spec-verifier` agent:**

```
Task(
  subagent_type="spec-verifier",
  prompt="Verify feature: <description>\nSteps: <steps>"
)
```

If verdict is YES:

- Update `feature_list.json` with `"passes": true`
- Proceed to commit

If verdict is NO:

- Present missing items to user
- Fix issues before proceeding

---

## Phase 6: Commit & Close

**STOP**: Use `AskUserQuestion` before committing.

1. Run `/code:commit` for logical commits

2. Update `claude-progress.txt`:
   - What accomplished
   - Feature completed
   - Next recommended work
   - Current progress (X/Y passing)

3. Present session summary:

```
## Session Complete

**Feature**: <name> - DONE
**Progress**: X/Y → A/B passing (Z%)
**Committed**: <commit hash>

**Next Session**: <recommendation>
```
