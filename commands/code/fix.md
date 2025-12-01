---
allowed-tools: all
description: Fix ALL issues via parallel agents - zero tolerance quality enforcement
---

# Fix All Issues

This is a FIXING task, not a reporting task.

## Workflow

1. Run validation:

   ```bash
   ~/.claude/hooks/smart-lint.sh
   make lint && make test
   ```

2. If issues found, spawn parallel agents:
   - "Found X issues. Spawning Agent 1 (linting), Agent 2 (tests), Agent 3 (build)"

3. Fix issues and verify by re-running checks

4. Repeat until clean

## Priority Levels

**Must Fix (blocking):**

- Syntax errors, type errors, build failures
- Test failures
- Security issues (hardcoded secrets, SQL injection, etc.)
- Logical bugs

**Should Fix:**

- Significant linting violations
- Missing error handling
- Performance issues

**Can Ignore (non-blocking):**

- Line length warnings
- Whitespace/spacing between sections
- Minor formatting inconsistencies
- Markdown file linting (documentation doesn't need strict formatting)

## Ready When

- Build passes
- All tests pass
- No blocking issues remain

Re-read ~/.claude/CLAUDE.md if needed.

**Executing validation and FIXING issues...**
