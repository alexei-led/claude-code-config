---
allowed-tools: Task, Bash, Read, Grep, Glob, LS
description: Test coverage analysis via quality-guardian - 80% minimum enforced
---

# Test Coverage Analysis

Analyze test coverage and identify gaps. 80% minimum on business logic.

## Step 1: Gather Coverage Data

Spawn an **Explore** agent (subagent_type: Explore) to run coverage and analyze:

```
Analyze test coverage for this project:

1. Detect language (look for go.mod, pyproject.toml, package.json)

2. Run coverage commands:
   - Go: `go test -race -coverprofile=coverage.out ./... && go tool cover -func=coverage.out`
   - Python: `pytest --cov=. --cov-report=term-missing`

3. Parse results and extract:
   - Overall coverage percentage
   - Per-package/module breakdown
   - Files below 80% threshold
   - Uncovered functions/methods

4. Identify critical gaps (focus on business logic, not):
   - Generated code, test files
   - Main/CLI entrypoints
   - Simple getters/setters

5. Flag uncovered:
   - Error handling paths
   - Edge cases
   - Public API functions
   - Security-related code

Return structured report:
- Overall coverage: XX%
- Packages below 80%: [list with percentages]
- Critical uncovered functions: [file:line - function name]
- Recommended priority for test generation
```

Review the agent's analysis, then proceed to Step 2.

## Step 2: Spawn Coverage Agents

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

## Step 3: Report

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
