---
allowed-tools: Task, SlashCommand, AskUserQuestion, TodoWrite, Bash(git checkout:*), Bash(git branch:*), Bash(git status:*), mcp__sequential-thinking__sequentialthinking
description: Continue spec-driven development session
---

# Spec Work

Continue spec-driven development. This is a fresh context window.

## Context Recovery (if session was interrupted)

Check for interrupted work FIRST:

1. `git status` - any uncommitted changes?
2. Read `claude-progress.txt` - what was "next"?
3. If mid-implementation: continue from that phase
4. If changes uncommitted: review and commit or discard

## Guardrails

- **Progress-first**: Always start with `claude-progress.txt`
- **Branch-per-feature**: Work in `feature/<name>` branch, not main
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
2. **Ultrathink**: Use `mcp__sequential-thinking__sequentialthinking` to reason through:
   - Architecture decisions and trade-offs
   - Implementation approach and risks
   - How this feature integrates with existing code
3. Spawn appropriate engineer agent (go-engineer, python-engineer, typescript-engineer):
   - Provide: feature description, steps, and ultrathink conclusions
   - Request: detailed implementation steps, testing strategy
4. **Clarify ambiguities**: Use AskUserQuestion for any unclear requirements:
   - Implementation choices (library, pattern, approach)
   - UI/UX decisions not specified in app_spec.txt
   - Edge cases and error handling preferences
5. Present plan summary to user

**STOP**: Use AskUserQuestion for approval before implementation.

---

## Phase 3: Implementation

1. **Create feature branch**: `git checkout -b feature/<feature-name>`
2. Create TodoWrite from approved plan
3. Implement step-by-step (language skills will guide patterns)

---

## Phase 3.5: Verification

Before marking feature complete, verify ALL:

1. **Build**: `make build` or equivalent compiles clean
2. **Test**: `make test` - ALL tests pass
3. **Lint**: `make lint` - ZERO issues
4. **Functionality**: `/test:e2e` or manual verification
5. **Regression check**: Quick test 1-2 previously passing features still work

Only after ALL pass: Update `feature_list.json` with `"passes": true`

If regression found: mark affected feature `"passes": false`, fix before proceeding.

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
