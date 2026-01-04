---
allowed-tools: Task, Bash, Read, Edit, Write, Grep, Glob, LS
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
   - TypeScript: `bun test --coverage`

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

If gaps found, spawn appropriate agent by language to get test proposals.

**CRITICAL: Zero tolerance for test waste when generating coverage tests**

- NO pointless tests (trivial getters, constructors)
- NO duplicate tests - each scenario tested exactly once
- MUST combine similar cases into table-driven/parametrized tests
- NO comments in tests unless logic is genuinely non-obvious

### Go Coverage Gaps

```
Task with go-engineer agent:
"Propose tests for these uncovered Go functions:
{list with file:line references}

CRITICAL REQUIREMENTS:
- MUST use table-driven tests - combine ALL similar cases
- Include edge cases: nil, empty, zero, boundary, error cases
- NO pointless tests - each test must verify meaningful behavior
- NO duplicate tests - each scenario tested exactly once
- NO comments in tests unless logic is genuinely non-obvious
- Use require for prerequisites, assert for independent checks"
```

### Python Coverage Gaps

```
Task with python-engineer agent:
"Propose tests for these uncovered Python functions:
{list with file:line references}

CRITICAL REQUIREMENTS:
- MUST use @pytest.mark.parametrize - combine ALL similar cases
- Use pytest.param(..., id="desc") for readable test names
- Include edge cases: None, empty, zero, boundary, exception cases
- NO pointless tests - each test must verify meaningful behavior
- NO duplicate tests - each scenario tested exactly once
- NO comments in tests unless logic is genuinely non-obvious"
```

### TypeScript Coverage Gaps

```
Task with typescript-engineer agent:
"Propose tests for these uncovered TypeScript functions:
{list with file:line references}

CRITICAL REQUIREMENTS:
- MUST use test.each/it.each - combine ALL similar cases
- Use object syntax with descriptive template: { input, expected, desc }
- Include edge cases: null, undefined, empty, boundary, rejection cases
- NO pointless tests - each test must verify meaningful behavior
- NO duplicate tests - each scenario tested exactly once
- NO comments in tests unless logic is genuinely non-obvious
- Use Testing Library for React (query by role)"
```

## Step 3: Apply Proposals

- Engineer returns structured test proposals (no files written)
- Review proposals for quality and completeness
- Apply using Edit/Write tools (user sees approval prompts)
- User can modify proposals before applying

## Step 4: Report

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
