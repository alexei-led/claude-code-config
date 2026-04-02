---
name: improving-tests
description: Sequential test improvement — scan test structure, identify gaps (missing edge cases, non-table-driven tests), refactor to table-driven or parametrized form, add missing coverage, and verify tests pass after each change.
---

# Test Improvement

Improve test quality by reviewing structure, refactoring repetitive tests into table-driven or parametrized form, and filling coverage gaps. Work through each phase sequentially. Run tests after every change to confirm nothing breaks.

## Step 1: Determine mode

Check `$ARGUMENTS`:

- `review` — analyze current tests, identify issues only
- `refactor` — combine repetitive tests into table-driven/parametrized form, remove duplicates
- `coverage` — generate tests for uncovered business logic
- `full` — all of the above in sequence
- (empty) — ask the user in plain prose: "What should I focus on — reviewing existing tests, refactoring them into table-driven form, filling coverage gaps, or all three?"

Wait for the user's answer before proceeding.

## Step 2: Scan test structure

Use Glob and Read to explore the test layout. Do not guess — use tool calls.

Find test files:

- Go: `*_test.go`
- Python: `test_*.py`, `*_test.py`
- TypeScript: `*.test.ts`, `*.spec.ts`, `*.test.tsx`

For each test file found, note:

- Testing framework in use (testify, pytest, vitest, jest)
- Whether table-driven/parametrized patterns are already used
- Presence of test helpers, fixtures, or shared setup
- Mock patterns in use

Record the language, framework, and a list of test files. Reflect on the overall structure before moving on.

## Step 3: Run coverage analysis

Run the appropriate coverage tool and capture output:

**Go:**

```bash
go test -coverprofile=/tmp/cov.out ./...
go tool cover -func=/tmp/cov.out | sort -k3 -rn | head -40
```

**Python:**

```bash
pytest --cov=. --cov-report=term-missing 2>&1 | head -80
```

**TypeScript:**

```bash
bun test --coverage 2>&1 | head -80
```

Exclude from analysis: test files themselves, generated code (`*_gen.go`, `generated/`), mock files (`mocks/`, `mock_*.go`), CLI entrypoints (`main.go`, `cmd/`, `__main__.py`), and type-definition-only files.

Record packages or modules below 70% coverage and any uncovered business logic functions.

## Step 4: Identify specific improvements

Read the test files for the areas with lowest coverage or most obvious structural problems. For each file, look for:

- **Repetitive tests** — multiple `TestFoo_case1`, `TestFoo_case2` functions testing the same function with slight variations. These should be one table-driven test.
- **Missing edge cases** — no test for empty input, zero values, nil/None, or error paths.
- **Duplicate setup** — the same boilerplate repeated in 3+ tests with no shared helper.
- **Pointless tests** — trivial getter/constructor tests that add no value.
- **Mock inconsistency** — mix of mock patterns when the project should standardize on one.

Produce a concrete list: file, test name or function name, problem, recommended action.

## Step 5: Apply refactoring (if mode includes refactor or full)

Work through the refactoring list one file at a time.

**Table-driven patterns:**

| Language   | Pattern                                                                                                        |
| ---------- | -------------------------------------------------------------------------------------------------------------- |
| Go         | `tests := []struct{ name, input, want string }{ ... }` with `for _, tc := range tests { t.Run(tc.name, ...) }` |
| Python     | `@pytest.mark.parametrize("input,expected", [ ... ])` with `pytest.param()` for named cases                    |
| TypeScript | `test.each([ { input, expected, desc } ])("%s", ({ input, expected }) => { ... })`                             |

**Extracting helpers:**

- Go: helper function in `*_test.go` calling `t.Helper()` at the top, or shared helpers in a `testhelper/` package
- Python: `conftest.py` fixture
- TypeScript: `test-utils.ts` utility exported from a shared location

After each file edit, run the tests to confirm nothing broke:

```bash
go test ./...     # or pytest -q   or bun test
```

If a test fails after refactoring, read the failure, fix it, and re-run before moving to the next file.

## Step 6: Add missing coverage (if mode includes coverage or full)

For each uncovered function identified in Step 3, write a test that covers:

1. The happy path with representative input
2. At least one error or edge case (nil input, empty slice, invalid value)
3. Boundary values where applicable (zero, max, off-by-one)

Place new tests in the existing test file for that package/module, following the same style and naming conventions already present. Do not create new test files unless the source file has none at all.

After adding tests, re-run coverage to confirm the numbers improved.

## Step 7: Final verification

Run the full test suite one more time:

```bash
go test -race ./...    # or pytest -v   or bun test
```

All tests must pass before declaring done.

## Output format

```
TEST IMPROVEMENT COMPLETE
=========================
Mode: <review|refactor|coverage|full>

Review:
- Issues found: X
- Issues addressed: Y

Refactoring:
- Tests combined: N individual → M table-driven
- Duplicates removed: X
- Helpers extracted: Y

Coverage:
- Before: XX%
- After: YY%

Files modified:
- <list>
```

If no tests exist or the test framework is not configured, report this and ask the user how to proceed rather than inventing a test setup from scratch.
