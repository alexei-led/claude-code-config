---
allowed-tools: Task, Bash, Read, Grep, Glob, LS
description: Test coverage analysis via quality-guardian - 80% minimum enforced
---

# Test Coverage Analysis

Analyze test coverage and identify gaps. 80% minimum on business logic.

## Step 1: Detect Language & Run Coverage

### Go

```bash
go test -race -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | tail -20
go tool cover -html=coverage.out -o coverage.html
```

### Python

```bash
pytest --cov=. --cov-report=term-missing --cov-report=html
```

## Step 2: Parse Results

Extract:

- Overall coverage percentage
- Per-package/module breakdown
- Files below 80% threshold
- Uncovered functions/methods

## Step 3: Identify Critical Gaps

Focus on business logic, not:

- Generated code
- Test files
- Main/CLI entrypoints
- Simple getters/setters

Flag uncovered:

- Error handling paths
- Edge cases
- Public API functions
- Security-related code

## Step 4: Spawn Coverage Agents

If gaps found, spawn appropriate agent by language:

### Go Coverage Gaps

```
Task with go-engineer agent:
"Generate tests for these uncovered Go functions:
{list with file:line references}

Use table-driven tests with t.Run() subtests.
Use require for prerequisites, assert for independent checks.
Focus on edge cases and error paths."
```

### Python Coverage Gaps

```
Task with python-engineer agent:
"Generate tests for these uncovered Python functions:
{list with file:line references}

Use pytest fixtures and parametrize.
Focus on edge cases and error paths."
```

## Step 5: Report

```
COVERAGE REPORT
===============
Overall: XX%
Threshold: 80%
Status: [PASS/FAIL]

By Package:
- pkg/auth: 95% ✓
- pkg/api: 72% ✗
- pkg/db: 88% ✓

Critical Gaps:
- pkg/api/handler.go:45 - ErrorHandler (0%)
- pkg/api/middleware.go:23 - AuthMiddleware (50%)

Recommendations:
1. Add error path tests for ErrorHandler
2. Test auth failure cases in AuthMiddleware
```

**Execute coverage analysis now.**
