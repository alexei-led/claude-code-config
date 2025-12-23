---
allowed-tools: Task, Bash
description: Fix ALL issues via parallel agents - zero tolerance quality enforcement
---

# Fix All Issues

Execute until clean. This is a FIXING task, not reporting.

## Step 1: Run Validation

```bash
make lint 2>&1 | head -100
make test 2>&1 | head -100
```

No Makefile? Detect language:

- **Go**: `golangci-lint run ./... && go test -race ./...`
- **Python**: `ruff check . && pytest`

## Step 2: Spawn Language Agent

Spawn appropriate language-specific agent:

```
Task with {go|python}-engineer agent:
"Fix these {language} issues:
{list with file:line}
Verify with: {appropriate lint/test command}"
```

## Step 3: Verify & Repeat

```bash
make lint && make test
```

If issues remain, return to Step 2.

## Step 4: Deep Fix (Complex Issues)

When fixes are tricky, user asks for deeper analysis, or initial fixes fail—use Codex AND Gemini CLIs (via **asking-codex** and **asking-gemini** skills):

**Codex** (autonomous fix with `codex exec --full-auto`):

```bash
codex exec --full-auto "Analyze and fix these complex issues:
{list with file:line and context}
Explain root cause and verify fix."
```

**Gemini** (analysis with `gemini`):

```bash
gemini "Analyze these issues deeply:
{list with file:line and context}
Suggest fixes with side-effect analysis."
```

## Exit Criteria

- Build passes
- All tests pass
- No BLOCKING issues

```
FIX COMPLETE
============
Fixed: X issues
Remaining: Y non-blocking
Status: CLEAN / NEEDS ATTENTION
```

**Execute validation now.**
