---
allowed-tools:
- Task
- TaskCreate
- TaskUpdate
- TaskList
- AskUserQuestion
- Read
- Bash(git diff *)
- Bash(git status *)
- Bash(make *)
- Bash(npm *)
- Bash(go test *)
- Bash(pytest *)
- Bash(uv *)
- Bash(ctx7 *)
- Bash(npx ctx7@latest *)
- Bash(bunx ctx7@latest *)
context: fork
description: Update project documentation based on code changes. Use when the user
  asks to update docs, document behavior, add README content, or align docs with recent
  implementation changes. NOT for extracting session learnings (use learning-patterns)
  or code-quality feedback (use reviewing-code).
name: documenting-code
user-invocable: true
---

# Documentation Update

Scope: documentation files only. Not for session-learning extraction (use learning-patterns) or code-quality review (use reviewing-code).

Update project documentation to reflect current code state. Do not delete or overwrite existing docs without confirmation. If verification fails or required evidence is unavailable, report the failure instead of claiming docs are current.

**Use TaskCreate / TaskUpdate** to track these 4 phases:

1. Determine documentation scope
2. Analyze recent changes
3. Analyze and update documentation
4. Verify and report

## Phase 1: Determine Scope

Ask one question at a time:

- **Doc scope** — What documentation should I update?
  1. **Auto-detect** — scan for outdated docs based on recent changes
  2. **README** — update project README
  3. **API docs** — update API/function documentation
  4. **All** — comprehensive documentation refresh

## Phase 2-3: Analyze and Update Documentation

Use a documentation subagent when available; otherwise inspect and update docs directly.

```
Task with docs-keeper agent:
"Update documentation for this project.

## Your Task

1. Analyze current state:
   - Run `git diff --name-only HEAD~5` for recent changes
   - Find existing docs: `find . -name '*.md' -o -name 'doc.go'`
   - Check project structure and dependencies

2. Scope: {user's choice from Step 1}

3. Update focus:
   - Accurate function/method documentation
   - README sections matching current state
   - API endpoint documentation
   - Architecture notes if significant changes

4. Verify:
   - No broken links
   - Code examples compile/run
   - Markdown renders correctly

## Output Format

DOCUMENTATION UPDATE
====================
Updated:
- file.md (what changed)
- pkg/doc.go (added GoDoc)

Verified: All links valid, examples compile"
```

## Phase 4: Verify and Present Summary

**Independent verification** (do not trust the agent's self-report):

When describing parent verification, explicitly mention checking runnable code examples or documented commands when practical. If examples/commands cannot be run, state why.

1. Run `git diff --stat` to confirm files were actually changed
2. For each changed file, verify the diff looks correct (no broken links, no placeholder text)
3. Run or compile documented code examples and commands when practical; if not practical, state why the check was skipped
4. If no files changed, report that no documentation modifications were needed

If no recent changes are found or documentation scope is unclear, ask the user what to document rather than generating speculative documentation.

Report using this format:

```
## Documentation Update

Updated:
- <file> — <one-line change summary>

Verified:
- git diff confirmed N files changed
- <check>: passed / skipped (<reason>)

Issues: <issue> or "none"
```
