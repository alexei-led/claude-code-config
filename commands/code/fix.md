---
allowed-tools: Task, Bash, Read, Grep, Glob, LS, mcp__codex__spawn_agent
description: Fix ALL issues via parallel agents - zero tolerance quality enforcement
---

# Fix All Issues

This is a FIXING task, not a reporting task. Execute until clean.

## Step 1: Run Validation

```bash
make lint 2>&1 | head -100
make test 2>&1 | head -100
```

If no Makefile, detect language and run appropriate commands:

- **Go**: `golangci-lint run ./... && go test -race ./...`
- **Python**: `ruff check . && pytest`

## Step 2: Categorize Issues

Parse output and categorize:

| Priority | Category                   | Action        |
| -------- | -------------------------- | ------------- |
| BLOCKING | Build/syntax errors        | Fix first     |
| BLOCKING | Test failures              | Fix second    |
| BLOCKING | Security issues            | Fix third     |
| SHOULD   | Significant lint warnings  | Fix if simple |
| IGNORE   | Line length, minor spacing | Skip          |

## Step 3: Spawn Parallel Agents

For 3+ issues, spawn agents IN PARALLEL by category:

### Go Issues

```
Task with go-engineer agent:
"Fix these Go issues in the codebase:
{list of issues with file:line references}
Run 'go build ./...' after fixing to verify."
```

### Python Issues

```
Task with quality-guardian agent:
"Fix these Python issues:
{list of issues with file:line references}
Run 'ruff check .' after fixing to verify."
```

### External Verification (Optional)

For complex fixes, get second opinion:

```
mcp__codex__spawn_agent:
"Review this fix for correctness:
{the fix diff}
Does this properly address the issue without side effects?"
```

## Step 4: Verify Fixes

After agents complete, re-run validation:

```bash
make lint && make test
```

## Step 5: Repeat Until Clean

If issues remain, return to Step 2.

## Exit Criteria

- Build passes
- All tests pass
- No BLOCKING issues remain

Report final status:

```
FIX COMPLETE
============
Fixed: X issues
Remaining: Y non-blocking (ignored)
Status: CLEAN / NEEDS ATTENTION
```

**Execute validation now.**
