---
allowed-tools:
  - Task
  - Read
  - Bash(jq:*)
  - Bash(git status:*)
description: Quick progress check for spec-driven development
---

# Spec Status

Quick snapshot of spec-driven development progress.

## Step 1: Check for Spec Files

```bash
ls feature_list.json 2>/dev/null && echo "SPEC_EXISTS" || echo "NO_SPEC"
```

**If NO_SPEC**: Report "Not a spec-driven project. Run `/spec:init` to initialize." and stop.

## Step 2: Spawn Discovery Agent

```
Task(
  subagent_type="spec-discover",
  prompt="Quick status check - return concise summary:
  - Progress: X/Y features passing (Z%)
  - Current branch and status
  - Next failing feature (description only)
  - Any blockers from progress file"
)
```

## Step 3: Present Status

Display agent's report directly. Format (5-7 lines max):

```
## Spec Status

**Progress**: X/Y passing (Z%)
**Branch**: feature/<name> | main
**Next**: <feature description>
**State**: Ready | Needs attention | Blocked
```

If build/test/lint failing, add warning line.

---

**Execute now.**
