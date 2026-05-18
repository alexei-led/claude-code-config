# Python Test Slice

Language-specific test material for Python 3.12+. The host skill supplies scope, workflow, and the output contract — this file supplies only the Python tooling, patterns, and focus-area checks.

## Run tooling first

```bash
# Run tests with verbose output
pytest -v

# Coverage report
pytest --cov=src --cov-report=term-missing

# Run only fast tests
pytest -m "not slow"

# Async test support
pytest --asyncio-mode=auto
```

## LSP navigation

- `findReferences` — check which functions have tests
- `goToDefinition` — trace mock implementations to interfaces
- `incomingCalls` — find all test functions calling a helper

## Learn existing patterns

Before reviewing, scan existing tests:

- Read `conftest.py` for shared fixtures
- Read 2-3 nearby `test_*.py` files for structure
- Note: fixture scope, parametrize style, mock setup patterns

Flag issues that deviate from both project patterns and best practices.

## Test design quality

Avoid pointless, naive, and duplicate tests:

- Pointless: tests verifying trivial behavior (getters, constructors) → delete
- Naive: tests covering only the obvious happy path → expand or delete
- Duplicate: same scenario tested multiple ways → keep one, delete others
- Related: tests for the same function → combine with `@pytest.mark.parametrize`
- No comments in tests: tests should be self-explanatory; only add when logic is genuinely non-obvious

Combine aggressively: 2+ tests for the same function with different inputs → single parametrized test.

## Pytest best practices

- Fixture scope: using `function` scope when `session` or `module` would be faster
- Fixture reuse: duplicated setup code instead of shared fixtures
- Parametrize: multiple similar tests → must use `@pytest.mark.parametrize` (no exceptions)
- Parametrize with ids: use `pytest.param(..., id="desc")` for readable test names
- Marks: missing `@pytest.mark.asyncio` for async tests
- Assertions: using `assert x == True` instead of `assert x`

## Test structure

- Arrange-Act-Assert: tests that don't follow AAA pattern
- One assertion per test: tests verifying too many things (unless parametrized)
- Test names: non-descriptive names like `test_1` → use `test_validate_email_empty_raises_error`
- Test isolation: tests depending on other tests or shared state
- Parametrize over duplication: similar tests → combine with parametrize, not copy-paste

## Async and free-threading considerations

- AsyncMock: ensure async functions use `AsyncMock` not `Mock`
- Asyncio introspection: use 3.14's async debugging tools for stuck tests
- Thread safety: add tests for concurrent access when using free-threaded build
- Deferred annotations: no need for `TYPE_CHECKING` blocks in test files
- Protocol testing: test Protocol implementations with structural typing

## Mocking and patching

- pytest-mock preferred: use `mocker` fixture over raw `unittest.mock` decorators
- Patch target: patch where object is used, not where it is defined
- spec/autospec: use `spec=` or `create_autospec` for important boundaries
- AsyncMock: using `Mock` for async functions is wrong — use `AsyncMock`
- Over-mocking: mocking too much loses integration value
- Mock assertions: not verifying mocks were called correctly

## Mock argument matching

Choose matchers deliberately — overusing loose matching weakens tests:

- Exact value: business-critical values (IDs, table names, keys)
- `call_args` inspection: checking specific args without full match
- Custom `__eq__` matcher: partial object matching

Decision tree:

1. Business value from test fixture? → exact value (mandatory)
2. Complex object with some important fields? → custom matcher or `call_args`
3. Generated ID/timestamp? → check exists, not exact value

```python
# GOOD: exact values for business-critical parameters
mock_repo.save.assert_called_once_with("order-123", "customer-456")

# GOOD: check specific args without matching everything
call_args = mock_repo.save.call_args
assert call_args.kwargs["email"] == "test@example.com"

# BAD: no assertions on mock at all
mock_repo.save()  # called but never verified!

# BAD: missing spec allows wrong method calls
mock_repo = Mock()  # should be Mock(spec=Repository)
mock_repo.nonexistent_method()  # silently passes!
```

## Type-safe mocking

- `create_autospec`: use for important boundaries to catch signature mismatches
- `spec` parameter: use `Mock(spec=ClassName)` or `mocker.Mock(spec=ClassName)`
- Protocol testing: test Protocol implementations with structural typing

## Coverage gaps

- Error paths: only testing happy path, missing exception cases
- Edge cases: missing boundary tests (empty list, None, zero)
- Async coverage: sync tests for async code
- Thread safety tests: missing concurrent access tests for shared state

## Failure handling

- If `pytest` fails to run (missing deps, import errors), report the error and skip coverage analysis.
- If `pytest --cov` is unavailable, continue without coverage findings; note coverage gaps cannot be assessed.
- If LSP tools are unavailable, skip reference-tracing and rely on manual file inspection.
- If the test suite has no tests at all, flag this as a critical finding before other findings.
