---
allowed-tools: Task, Bash, Read, Edit, Write, Grep, Glob, LS, AskUserQuestion
description: Review, refactor, and improve tests - eliminate waste, combine to tabular, align style
---

# Test Improvement

Improve test quality: review existing, refactor structure, fill coverage gaps.

## Step 1: Choose Mode

Use AskUserQuestion:

| Header | Question                | Options                                                                                                                                                                                                                                             |
| ------ | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mode   | What should I focus on? | 1. **Review existing** - Analyze current tests, identify issues 2. **Refactor tests** - Combine to tabular, remove duplicates, align style 3. **Fill coverage gaps** - Generate tests for uncovered code 4. **Full improvement** - All of the above |

## Step 2: Background Exploration

Run exploration in background to keep main context clean:

```
Task(
  subagent_type="Explore",
  prompt="Explore test structure in this codebase:
  1. Find test files: fd -e go -e py -e ts . | rg '(_test\.go|test_.*\.py|\.test\.ts)'
  2. Identify test frameworks (testify, pytest, vitest)
  3. Find existing patterns: table-driven, parametrize, test.each usage
  4. Locate test helpers and fixtures
  5. Check mock patterns (mockery, pytest-mock, vi.mock)
  Return: language, framework, patterns found, helper locations",
  run_in_background=true
)
```

## Step 3: Run Coverage Analysis (Background)

```
Task(
  subagent_type="Explore",
  prompt="Run coverage and identify gaps:

  Go: go test -coverprofile=/tmp/claude/cov.out ./... && go tool cover -func=/tmp/claude/cov.out
  Python: pytest --cov=. --cov-report=term-missing
  TypeScript: bun test --coverage

  EXCLUDE from coverage (don't test these):
  - Test files, test helpers, fixtures
  - Generated code (*_gen.go, generated/)
  - Mock files (mocks/, mock_*.go)
  - CLI entrypoints (main.go, cmd/, __main__.py)
  - Type definitions only files

  Return: overall %, packages below 70%, uncovered business logic functions",
  run_in_background=true
)
```

## Step 4: Spawn Language-Specific Test Agent

Wait for exploration results, then spawn appropriate agent:

### Go Tests

```
Task(
  subagent_type="go-tests",
  prompt="Review Go tests for quality issues.

  FOCUS ON:
  - Tests that should be table-driven (combine similar)
  - Pointless tests (trivial getters, constructors)
  - Duplicate tests (same scenario multiple ways)
  - Mock patterns (prefer mockery --with-expecter)
  - Setup duplication (extract helpers)

  Return structured findings with file:line references."
)
```

### Python Tests

```
Task(
  subagent_type="py-tests",
  prompt="Review Python tests for quality issues.

  FOCUS ON:
  - Tests that should use @pytest.mark.parametrize
  - Pointless tests (trivial behavior)
  - Duplicate tests
  - Mock patterns (pytest-mock with spec=)
  - Fixture reuse opportunities

  Return structured findings with file:line references."
)
```

### TypeScript Tests

```
Task(
  subagent_type="ts-tests",
  prompt="Review TypeScript tests for quality issues.

  FOCUS ON:
  - Tests that should use test.each
  - Pointless tests (prop renders, default state)
  - Duplicate tests
  - Mock patterns (vi.fn, vi.mock, vi.mocked)
  - React Testing Library best practices

  Return structured findings with file:line references."
)
```

## Step 5: Apply Improvements

Based on agent findings, apply changes:

### Combining Tests Pattern

**Go**: Table-driven → `t.Run()`
**Python**: `@pytest.mark.parametrize` with `pytest.param(..., id="")`
**TypeScript**: `test.each([{input, expected, desc}])`

### Extracting Helpers

Look for repeated setup (3+ occurrences) → extract to:

- Go: `testhelper/` or `*_test.go` helpers with `t.Helper()`
- Python: `conftest.py` fixtures
- TypeScript: `test-utils.ts` utilities

### Mock Alignment

Standardize on one pattern per project:

- Go: mockery `--with-expecter --inpackage`
- Python: `mocker.Mock(spec=Class)`
- TypeScript: `vi.mocked()` for type safety

## Step 6: Verify & Report

```bash
# Verify all tests pass
go test -v ./...
pytest -v
bun test

# Check improved coverage
go tool cover -func=/tmp/claude/cov.out | tail -1
pytest --cov=. --cov-report=term | tail -5
bun test --coverage
```

## Output

```
TEST IMPROVEMENT COMPLETE
=========================
Mode: [selected mode]

Review:
- Issues found: X
- Issues addressed: Y

Refactoring:
- Tests combined: N → M table-driven
- Duplicates removed: X
- Helpers extracted: Y

Coverage:
- Before: XX%
- After: YY% (excluding non-business code)

Files modified:
- [list]
```

**Execute test improvement now.**
