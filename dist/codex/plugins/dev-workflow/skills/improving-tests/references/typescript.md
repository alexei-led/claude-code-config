# TypeScript Test Slice

Language-specific test material for TypeScript with Vitest. The host skill supplies scope, workflow, and the output contract — this file supplies only the TypeScript tooling, patterns, and focus-area checks.

## Run tooling first

```bash
# Run tests
bun test 2>&1

# Run tests with coverage
bun test --coverage 2>&1

# Type check tests
bun run tsc --noEmit 2>&1
```

Type errors in test files are blocking — include tsc output verbatim in findings.

## LSP navigation

- `findReferences` — check which functions have tests
- `goToDefinition` — trace mock implementations to interfaces
- `incomingCalls` — find all test functions calling a helper

## Learn existing patterns

Before reviewing, scan existing tests:

- Read nearby `*.test.ts` files for structure
- Check for shared test utilities in `tests/` or `__tests__/`
- Note: describe grouping, mock patterns, test.each usage

Flag issues that deviate from both project patterns and best practices.

## Test design quality

Avoid pointless, naive, and duplicate tests:

- Pointless: tests verifying trivial behavior (prop renders, default state) → delete
- Naive: tests covering only the obvious happy path → expand or delete
- Duplicate: same scenario tested multiple ways → keep one, delete others
- Related: tests for the same function with different inputs → combine with test.each
- No comments in tests: tests should be self-explanatory; only add when logic is genuinely non-obvious

Combine aggressively: 2+ tests for the same function with different inputs → single test.each.

## test.each pattern

Mandatory for any 2+ tests with the same structure and different inputs — no exceptions.

- Combine threshold: 2+ tests with same structure but different inputs
- Template strings: use `("description for %s", ...)` for readable names
- Object syntax: prefer objects for multi-param — `test.each([{ input, expected }])`

```typescript
// GOOD: combined with test.each
it.each([
  { email: "valid@example.com", valid: true },
  { email: "", valid: false },
  { email: "invalid", valid: false },
])("validates $email → $valid", ({ email, valid }) => {
  expect(validateEmail(email)).toBe(valid);
});

// BAD: separate tests for same function
it("validates valid email", () => {...});
it("rejects empty email", () => {...});
it("rejects invalid email", () => {...});
```

## Vitest best practices

- `describe` grouping: group related tests, don't over-nest (max 2 levels)
- `beforeEach` cleanup: reset mocks with `vi.clearAllMocks()`
- Async handling: use `async/await`, not callbacks
- Mock verification: check `toHaveBeenCalledWith` for important calls
- Snapshot testing: use sparingly — only for complex output structures

## React Testing Library

- Query priority: `getByRole` > `getByLabelText` > `getByText` > `getByTestId`
- User events: use `@testing-library/user-event` over `fireEvent`
- Async queries: use `findBy*` for async content, `waitFor` for assertions
- No implementation testing: don't test state/hooks directly; test behavior
- Accessibility: querying by role also validates accessibility

```typescript
// GOOD: testing behavior via role
it("submits form with valid data", async () => {
  const user = userEvent.setup();
  render(<LoginForm onSubmit={mockSubmit} />);

  await user.type(screen.getByRole("textbox", { name: /email/i }), "test@example.com");
  await user.click(screen.getByRole("button", { name: /submit/i }));

  expect(mockSubmit).toHaveBeenCalledWith({ email: "test@example.com" });
});
```

## Mocking

- `vi.fn()`: for simple function mocks
- `vi.mock()`: for module mocks (must be at top level — hoisted)
- `vi.spyOn()`: for partial mocks (use sparingly — prefer full mocks)
- `vi.mocked()`: for type-safe mock access
- Mock Service Worker: prefer msw for API mocking over `vi.mock`
- Cleanup: always use `afterEach(() => { vi.restoreAllMocks() })`

## Mock argument matching

Choose matchers deliberately — overusing loose matching weakens tests:

- Exact value: business-critical values (IDs, keys, table names)
- `expect.any(Type)`: type check without exact value (generated IDs, timestamps)
- `expect.objectContaining()`: partial object matching
- `expect.stringContaining()`: partial string/SQL matching

Decision tree:

1. Business value from test fixture? → exact value (mandatory)
2. Complex object with some important fields? → `expect.objectContaining()`
3. Generated ID/timestamp? → `expect.any(String)` or `expect.any(Date)`
4. SQL or JSON pattern? → `expect.stringContaining()`

```typescript
// GOOD: exact values for business-critical parameters
expect(mockRepo.save).toHaveBeenCalledWith("order-123", "customer-456");

// GOOD: partial match with exact business values
expect(mockRepo.save).toHaveBeenCalledWith(
  expect.objectContaining({
    email: "test@example.com", // exact
    id: expect.any(String),    // generated
  }),
);

// BAD: no verification of mock calls
mockService.process(); // called but never verified!

// BAD: missing vi.mocked() loses type safety
const mock = vi.fn(); // should use vi.mocked(realFn)
```

## Type-safe mocking

- `vi.mocked()`: always wrap for type inference
- `MockedFunction`: use for explicit typing
- Module mock factories: ensure return types match the original

## Coverage gaps

- Error paths: missing tests for rejection/throw cases
- Edge cases: empty arrays, null, undefined, boundary values
- Async errors: missing tests for failed async operations
- Component states: missing loading, error, empty states

## Failure handling

- Tests fail to run: report the failure output verbatim; include as a blocking finding — do not guess at the fix.
- Coverage tool unavailable: note the gap and continue with manual review of visible test files.
- Ambiguous consolidation: if combining with test.each would lose meaningful test-name context, flag and ask — don't force a merge.
- No existing test patterns found: state that no project conventions were detected and apply general Vitest best practices.
- Type errors in test files: treat as blocking; include the tsc output line in findings.
