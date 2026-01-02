---
allowed-tools: Task, SlashCommand, AskUserQuestion, TodoWrite
description: Continue spec-driven development session
---

# Spec Work

Continue spec-driven development. This is a fresh context window.

## Guardrails

- **Progress-first**: Always start with `claude-progress.txt`
- **User-approval**: Explicit approval before implementation and commits
- **Passes-only**: Only modify `"passes"` field in `feature_list.json`
- **Fix-first**: Repair regressions before implementing new features
- **Clean-exit**: End sessions with committed code and updated progress

---

## Phase 1: Discovery

Spawn **Explore** agent (Task with subagent_type: Explore, thoroughness: very thorough):

```
Explore this spec-driven development project:

1. Read `claude-progress.txt` first - what was done last, what's next
2. Read `app_spec.txt` - what's being built
3. Read `feature_list.json`:
   - Calculate: total, passing, failing features
   - Identify highest priority failing feature
4. Run `git log --oneline -10`
5. Analyze codebase: primary language/framework, patterns, reusable components

Return:
- Project overview and progress (X/Y, Z%)
- Last session accomplishments
- Recommended next feature (with priority reasoning)
- Key patterns to follow
```

Start servers if needed: `make init && make run`

**Regression check**: Before new work, verify 1-2 core features still work.
If regressions found: mark feature `"passes": false`, fix before proceeding.

---

## Phase 2: Planning

1. Select highest-priority failing feature from `feature_list.json`
2. Spawn appropriate engineer agent (go-engineer, python-engineer, typescript-engineer):
   - Provide: feature description and steps from `feature_list.json`
   - Request: architecture overview, implementation steps, testing strategy, risks
3. Present plan summary to user

**STOP**: Use AskUserQuestion for approval before implementation.

---

## Phase 3: Implementation

1. Create TodoWrite from approved plan
2. Implement step-by-step (language skills will guide patterns)
3. Verify with `/test:e2e` - browser automation with screenshots
4. Update `feature_list.json`: only `"passes": false` → `true` after verification

---

## Phase 4: Review & Commit

**STOP**: Use AskUserQuestion before committing.

1. Run `/code:review` - fix all CRITICAL and IMPORTANT issues
2. Run `/code:commit` for logical, atomic commits
3. Update `claude-progress.txt`:
   - What accomplished this session
   - Features completed
   - Issues found/fixed
   - Next recommended work
   - Current progress (X/Y passing)

**Clean exit**: No uncommitted changes, app in working state.
