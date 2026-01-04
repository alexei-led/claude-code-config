---
allowed-tools: Task, TaskOutput, Read, Edit, Write, Skill, AskUserQuestion, TodoWrite, Bash(jq:*), Bash(git checkout:*), Bash(git branch:*), Bash(git status:*), Bash(git log:*), Bash(make:*), Bash(git push:*), Bash(gh pr:*)
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

## Phase 5.5: Review/Fix Loop

**Run multi-agent code review:**

```
Skill(skill="code:review", args="deep")
```

**If CRITICAL or IMPORTANT issues found:**

```
Skill(skill="code:fix")
```

**Re-verify** with `spec-verifier` after fixes.

**Loop until:**

- Zero CRITICAL issues
- Build/test/lint all pass
- spec-verifier returns YES

---

## Phase 6: Commit & PR

**STOP**: Use `AskUserQuestion` before committing.

**Step 1: Commit changes**

```
Skill(skill="code:commit")
```

**Step 2: Sync with remote master**

```bash
git fetch origin master
git log --oneline HEAD..origin/master  # Check what changed
```

**Decision logic:**

- If only minor changes (badges, docs, CI config): **rebase**
  ```bash
  git rebase origin/master
  ```
- If significant changes or conflicts likely: **merge**
  ```bash
  git merge origin/master -m "Merge master into feature/<name>"
  ```
- If conflicts occur: resolve, then re-run verification

**Step 3: Push and create PR**

```bash
git push -u origin feature/<feature-name>
```

```bash
gh pr create --title "feat: <feature description>" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points from implementation>

## Verification
- [x] Build passes
- [x] Tests pass
- [x] Lint clean
- [x] Feature verified against spec

## Feature Steps
<steps from feature_list.json>
EOF
)"
```

**Step 4: Update progress**

Update `claude-progress.txt`:

- Feature completed with PR link
- Progress: X/Y → A/B passing
- Next feature recommendation

**Step 5: Present summary**

```
## Session Complete

**Feature**: <name> - DONE
**PR**: <pr_url>
**Progress**: X/Y → A/B passing (Z%)

**Next Session**: <next failing feature>
```
