---
allowed-tools: Task, Bash, Read, Write, Edit, Grep, Glob, LS, AskUserQuestion, mcp__perplexity-ask__perplexity_ask
description: Generate tests following Go/Python best practices
---

# Test Generation

Generate high-quality tests for specified code.

## Step 1: Ask What to Test

Use AskUserQuestion:

| Header      | Question                          | Options                                                                                                                                                            |
| ----------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Test target | What should I generate tests for? | 1. **Recent changes** - Test uncommitted or recent code 2. **Specific file** - I'll provide the file path 3. **Uncovered code** - Generate tests for coverage gaps |

## Step 2: Analyze Target Code

Based on choice:

### Recent Changes

```bash
git diff --name-only HEAD | grep -E "\.(go|py)$"
```

### Specific File

Read the file and identify:

- Public functions/methods
- Complex logic paths
- Error handling branches
- Edge cases

### Coverage Gaps

Run coverage first, then target uncovered lines.

## Step 3: Detect Language & Patterns

### Go Projects

- Use table-driven tests
- Use testify/assert and testify/require
- Use mockery for interface mocks
- Check existing test patterns in `*_test.go` files

### Python Projects

- Use pytest fixtures
- Use unittest.mock or pytest-mock
- Follow existing test patterns in `test_*.py` files

## Step 4: Generate Tests

Spawn appropriate agent:

### Go Tests

```
Task with go-engineer agent:
"Generate comprehensive tests for:
{file path and function signatures}

Requirements:
- Table-driven tests with descriptive names
- Test happy path AND error cases
- Use testify assertions
- Mock external dependencies
- Follow patterns from existing tests in this repo

Reference existing tests:
{snippet from similar test file}"
```

### Python Tests

```
Task with python-engineer agent:
"Generate pytest tests for:
{file path and function signatures}

Requirements:
- Use pytest fixtures for setup
- Test success and failure cases
- Mock external dependencies with pytest-mock
- Follow patterns from existing tests

Reference existing tests:
{snippet from similar test file}"
```

## Step 5: Verify Generated Tests

```bash
# Go
go test -v -run TestNewFunction ./...

# Python
pytest -v test_new_module.py
```

## Guidelines (Always Follow)

- **No pointless tests** - Each test verifies meaningful behavior
- **Learn from existing tests** - Match repo style and patterns
- **Prefer adding to existing files** - Don't create new test files unnecessarily
- **Test behavior, not implementation** - Focus on inputs/outputs
- **Descriptive names** - Test name should explain what's being verified

## Output

```
TESTS GENERATED
===============
Created: pkg/auth/handler_test.go
  - TestHandler_Authenticate (5 cases)
  - TestHandler_Authenticate_Errors (3 cases)

Verified: All tests pass
Coverage: auth package 72% → 89%
```

**Execute test generation now.**
