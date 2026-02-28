---
name: improving-tests
description: Review, refactor, and improve test quality. Use when user says "improve tests", "refactor tests", "test coverage", "combine tests", "table-driven", "parametrize", "test.each", "eliminate test waste", or wants to optimize test structure.
user-invocable: true
context: fork
argument-hint: "[review|refactor|coverage|full]"
allowed-tools:
  - Task
  - TaskOutput
  - TodoWrite
  - Bash(go test *)
  - Bash(pytest *)
  - Bash(bun test *)
  - Bash(npm test *)
  - Read
  - Grep
  - Glob
  - LS
  - AskUserQuestion
---

# Test Improvement

Improve test quality: review existing, refactor structure, fill coverage gaps.

**Use TodoWrite** to track these 6 phases:

1. Choose mode
2. Explore test structure
3. Run coverage analysis
4. Review with language agent
5. Apply improvements
6. Verify & report

---

## Phase 1: Choose Mode

**$ARGUMENTS:**

- `review` → Analyze current tests, identify issues
- `refactor` → Combine to tabular, remove duplicates, align style
- `coverage` → Generate tests for uncovered code
- `full` → All of the above
- (empty) → Ask what to do

If no argument provided, use AskUserQuestion:

| Header | Question                | Options                                                                                                                                                                                                                                             |
| ------ | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mode   | What should I focus on? | 1. **Review existing** - Analyze current tests, identify issues 2. **Refactor tests** - Combine to tabular, remove duplicates, align style 3. **Fill coverage gaps** - Generate tests for uncovered code 4. **Full improvement** - All of the above |

---

## Phase 2: Background Exploration (Parallel)

**Spawn BOTH agents in a single message:**

```
Task(
  subagent_type="Explore",
  run_in_background=true,
  description="Test structure scan",
  prompt="Explore test structure:
  1. Find test files: Glob for *_test.go, test_*.py, *.test.ts, *.spec.ts
  2. Identify frameworks (testify, pytest, vitest, jest)
  3. Find patterns: table-driven, parametrize, test.each usage
  4. Locate test helpers and fixtures
  5. Check mock patterns (mockery, pytest-mock, vi.mock)
  Return: language, framework, patterns found, helper locations"
)

Task(
  subagent_type="Explore",
  run_in_background=true,
  description="Coverage analysis",
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

  Return: overall %, packages below 70%, uncovered business logic functions"
)
```

**Save agent IDs** for potential resumption if session is interrupted.

---

## Phase 3: Collect Exploration Results

```
TaskOutput(task_id=<structure_agent_id>, block=true)
TaskOutput(task_id=<coverage_agent_id>, block=true)
```

Merge findings to inform next phase.

---

## Phase 4: Spawn Language-Specific Test Agent

Based on detected language, spawn ONE appropriate agent:

### Go Tests

```
Task(
  subagent_type="go-tests",
  description="Go test review",
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
  description="Python test review",
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
  description="TypeScript test review",
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

---

## Phase 5: Apply Improvements

Based on agent findings, apply changes:

### Combining Tests Pattern

| Language   | Pattern                                          |
| ---------- | ------------------------------------------------ |
| Go         | Table-driven with `t.Run(tc.name, ...)`          |
| Python     | `@pytest.mark.parametrize` with `pytest.param()` |
| TypeScript | `test.each([{input, expected, desc}])`           |

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

---

## Phase 6: Verify & Report

```bash
# Verify all tests pass
go test -v ./...
# or
pytest -v
# or
bun test
```

## Output

```
TEST IMPROVEMENT COMPLETE
=========================
Mode: [selected mode]
Agent IDs: [list for resumption if needed]

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

---

**Execute test improvement now.**
