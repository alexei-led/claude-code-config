---
allowed-tools: Task, Bash, Read, Grep, Glob, LS, AskUserQuestion, mcp__perplexity-ask__perplexity_ask
description: Generate tests following Go/Python/TypeScript best practices - zero tolerance for waste
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
git diff --name-only HEAD | grep -E "\.(go|py|ts|tsx)$"
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

- Use table-driven tests with `t.Run()` subtests
- Use testify assertions:
  - `require` for prerequisites (nil checks, error checks, setup validation)
  - `assert` for independent property checks
- **NEVER write mocks manually** - use mockery for interface mocks
- Check existing test patterns in `*_test.go` files

**Mockery generation (mandatory):**

```bash
# For private interfaces (avoid import cycles) - generate in-package
mockery --name=userStore --inpackage --with-expecter

# For public interfaces - generate in mocks package
mockery --name=UserStore --with-expecter --dir=internal/service --output=internal/service/mocks
```

**Mock argument matchers (CRITICAL):**

| Matcher          | Use When                                                    |
| ---------------- | ----------------------------------------------------------- |
| Exact value      | Business-critical values (table names, IDs, partition keys) |
| `mock.Anything`  | ONLY for `context.Context`, loggers, tracers                |
| `mock.MatchedBy` | SQL queries, complex structs, partial matching              |

```go
// GOOD: Exact values for business-critical parameters
state.EXPECT().
    SetRunning(mock.Anything, "project.dataset.table", "20241201", "wu-123").
    Return(nil)

// GOOD: mock.MatchedBy for SQL
db.EXPECT().
    Exec(mock.MatchedBy(func(q string) bool {
        return strings.Contains(strings.Join(strings.Fields(q), " "), "INSERT INTO")
    }), mock.Anything).
    Return(result, nil)
```

### Python Projects

- Use pytest fixtures
- Use unittest.mock or pytest-mock
- Follow existing test patterns in `test_*.py` files

### TypeScript Projects

- Use Vitest with test.each for parameterized tests
- Use Testing Library for React components
- Use msw for API mocking
- Follow existing test patterns in `*.test.ts` or `*.spec.ts` files

## Step 4: Generate Tests

Spawn appropriate agent:

### Go Tests

```
Task with go-engineer agent:
"Generate tests for:
{file path and function signatures}

CRITICAL REQUIREMENTS:
- MUST use table-driven tests - combine ALL similar cases into single test
- Include edge cases: nil, empty, zero, boundary, error cases
- NO pointless tests (trivial getters/constructors)
- NO duplicate tests - each scenario tested exactly once
- NO comments in tests unless logic is genuinely non-obvious
- Use require for prerequisites (nil/error checks)
- Use assert for independent property checks

MOCKING REQUIREMENTS (CRITICAL):
- NEVER write mocks manually - use mockery with go:generate
- For private interfaces: mockery --name=interfaceName --inpackage --with-expecter
- For public interfaces: mockery --name=InterfaceName --with-expecter --output=./mocks
- Use mock.Anything ONLY for context.Context, loggers, tracers
- Use EXACT VALUES for business-critical parameters (table names, IDs, partition keys)
- Use mock.MatchedBy for SQL queries, complex structs, partial matching

Example mock expectation:
state.EXPECT().
    SetRunning(mock.Anything, \"project.dataset.table\", \"20241201\", \"wu-123\").
    Return(nil)

Reference existing tests:
{snippet from similar test file}"
```

### Python Tests

```
Task with python-engineer agent:
"Generate pytest tests for:
{file path and function signatures}

CRITICAL REQUIREMENTS:
- MUST use @pytest.mark.parametrize - combine ALL similar cases
- Use pytest.param(..., id="desc") for readable test names
- Include edge cases: None, empty, zero, boundary, exception cases
- NO pointless tests (trivial getters/constructors)
- NO duplicate tests - each scenario tested exactly once
- NO comments in tests unless logic is genuinely non-obvious
- Use fixtures for setup, mock with pytest-mock

Reference existing tests:
{snippet from similar test file}"
```

### TypeScript Tests

```
Task with typescript-engineer agent:
"Generate Vitest tests for:
{file path and function signatures}

CRITICAL REQUIREMENTS:
- MUST use test.each/it.each - combine ALL similar cases
- Use object syntax with descriptive template: { input, expected, desc }
- Include edge cases: null, undefined, empty, boundary, rejection cases
- NO pointless tests (trivial prop renders, default state)
- NO duplicate tests - each scenario tested exactly once
- NO comments in tests unless logic is genuinely non-obvious
- Use Testing Library for React (query by role)
- Use msw for API mocking

Reference existing tests:
{snippet from similar test file}"
```

## Step 5: Verify Generated Tests

```bash
# Go
go test -v -run TestNewFunction ./...

# Python
pytest -v test_new_module.py

# TypeScript
bun test --run new_module.test.ts
```

## Guidelines (CRITICAL - Zero Tolerance for Waste)

**AVOID POINTLESS, NAIVE, AND DUPLICATE TESTS**

- **No pointless tests**: Don't test trivial behavior (getters, constructors, prop rendering)
- **No naive tests**: Don't just test obvious happy paths—include edge cases, errors, boundaries
- **No duplicate tests**: Never test same scenario multiple ways
- **Combine tests**: 2+ tests for same function → single table-driven/parametrized test (mandatory)
- **No comments in tests**: Tests should be self-explanatory

**Language-Specific Combining**

- **Go**: Table-driven tests with `t.Run()` - combine ALL similar tests
- **Python**: `@pytest.mark.parametrize` with `pytest.param(..., id="desc")`
- **TypeScript**: `it.each([...])` with template strings for descriptions

**Standard Guidelines**

- Learn from existing tests - Match repo style and patterns
- Prefer adding to existing test files - Don't create new files unnecessarily
- Test behavior, not implementation - Focus on inputs/outputs
- Descriptive names: `TestValidateEmail_EmptyReturnsError`, `test_validate_email_empty_raises`, `"validates empty → error"`

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
