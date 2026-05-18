# Go Test Slice

Language-specific test material for Go 1.25+. The host skill supplies scope, workflow, and the output contract — this file supplies only the Go tooling, patterns, and focus-area checks.

## Run tooling first

```bash
# Run tests with race detector (5 min timeout)
go test -race -short -timeout=5m ./... 2>&1

# Test-specific linters (2 min timeout)
golangci-lint run --timeout=2m --enable=tparallel,paralleltest,testifylint,testableexamples,thelper,usetesting ./... 2>&1

# Coverage report
go test -short -timeout=5m -coverprofile=/tmp/claude/coverage.out ./... 2>&1 && go tool cover -func=/tmp/claude/coverage.out 2>&1
```

If `golangci-lint` fails, explore the tool to debug:

```bash
golangci-lint --help          # main help
golangci-lint run --help      # run command options
golangci-lint linters         # list available linters
```

## LSP navigation

- `findReferences` — check which functions have tests
- `goToDefinition` — trace mock implementations to interfaces
- `incomingCalls` — find all test functions calling a helper

## Learn existing patterns

Before reviewing, scan existing tests:

- Read 2-3 nearby `*_test.go` files for structure
- Check for test helpers in `testhelper/` or shared `_test.go` files
- Note: testify usage (assert vs require), table-driven style, mock patterns

Flag issues that deviate from both project patterns and best practices.

## Table-driven tests

Mandatory for any 2+ tests with the same structure and different inputs — no exceptions.

- Combine threshold: 2+ tests with same structure but different inputs
- Test case naming: use descriptive `name` field — `"valid_email"`, `"empty_returns_error"`, `"zero_value_handled"`
- Every table must include: nil, empty, zero, boundary, and error cases
- Add `t.Parallel()` for independent test cases
- Use `t.Run(tc.name, func(t *testing.T) {...})`
- Keep tables under 15-20 rows; split logically if larger

## Testify assert vs require

- `require` for setup: use when failure should stop the test (setup, preconditions)
- `assert` for verification: use for actual test assertions (multiple can fail)
- `require.NoError(t, err)`: always check errors that would cause nil panics
- `assert.Equal` order: `assert.Equal(t, expected, actual)` — expected first

## Test design quality

Avoid pointless, naive, and duplicate tests:

- Pointless: tests verifying trivial behavior (getters returning fields, constructors setting fields) → delete
- Naive: tests covering only the obvious happy path without edge cases → expand or delete
- Duplicate: same scenario tested multiple ways → keep one, delete others
- Related: tests for the same function with different inputs → combine into a single table-driven test
- No comments in tests: tests should be self-explanatory; only add when logic is genuinely non-obvious

Combine aggressively: 3+ tests for the same function → almost always a single table-driven test.

## Complex setup = design smell

When test setup is complex, recommend implementation refactoring:

- Many mocks needed → extract smaller interface (Interface Segregation)
- Deep dependency chain → introduce facade or factory
- Global state setup → inject dependencies instead
- Private interface pattern: define interface in consumer package, not provider

```go
// GOOD: private interface in consumer package
type userRepo interface {  // lowercase = private
    Get(ctx context.Context, id string) (*User, error)
}

type Service struct {
    repo userRepo  // depends on private interface
}
```

### Mocking external service wrappers

When a thin wrapper exists for external services (DB, APIs, queues), mocks only need to implement the consumer's interface — not the entire wrapper:

```go
// Wrapper has 5 methods, but consumer only uses 2
// internal/stripe/client.go
type Client struct { ... }
func (c *Client) Charge(...) { ... }
func (c *Client) Refund(...) { ... }
func (c *Client) GetCustomer(...) { ... }
func (c *Client) CreateCustomer(...) { ... }
func (c *Client) UpdateCustomer(...) { ... }

// Consumer defines minimal interface
// package billing
type paymentGateway interface {
    Charge(ctx context.Context, amount int64, currency, customerID string) (string, error)
}

// Test mock only implements Charge — no bloat
type mockPaymentGateway struct{}
func (m *mockPaymentGateway) Charge(ctx context.Context, amount int64, currency, customerID string) (string, error) {
    return "ch_test_123", nil
}
```

This is correct design: consumer-side interfaces mean mocks are minimal (1-2 methods, not 10), tests are focused on behavior being tested, and different consumers can have different mock implementations.

## Mockery with EXPECT

Never write mocks manually — use mockery for all mock generation:

```bash
# Private interfaces (avoid import cycles) — generate in-package
mockery --name=userStore --inpackage --with-expecter

# Public interfaces — generate in mocks subpackage
mockery --name=UserStore --with-expecter --dir=internal/service --output=internal/service/mocks
```

Interface annotation for go:generate:

```go
// Private interface — use --inpackage
//go:generate mockery --name=userStore --inpackage --with-expecter
type userStore interface {
    Get(ctx context.Context, id string) (*User, error)
}
```

## Mock argument matchers

Overusing `mock.Anything` weakens tests — choose matchers deliberately:

- Exact value: business-critical values — table names, partition IDs, customer IDs, work unit IDs
- `mock.Anything`: only for `context.Context`, loggers, tracers, truly don't-care values
- `mock.MatchedBy`: SQL queries, complex structs, generated IDs, partial matching

Decision tree:

1. `context.Context`, logger, tracer? → `mock.Anything`
2. Business value from test fixture? → exact value (mandatory)
3. Complex object with important fields? → `mock.MatchedBy`
4. SQL/JSON with variable formatting? → `mock.MatchedBy` with normalization
5. Generated ID/timestamp? → `mock.MatchedBy` with type check

```go
// GOOD: exact values for business-critical parameters
state.EXPECT().
    SetRunning(mock.Anything, "project.dataset.table", "20241201", "wu-123").
    Return(nil)

// GOOD: mock.MatchedBy for SQL pattern validation
db.EXPECT().
    Exec(mock.MatchedBy(func(q string) bool {
        normalized := strings.Join(strings.Fields(q), " ")
        return strings.HasPrefix(normalized, "INSERT INTO users")
    }), mock.Anything).
    Return(result, nil)

// GOOD: mock.MatchedBy for struct field validation
store.EXPECT().
    Save(mock.Anything, mock.MatchedBy(func(u *User) bool {
        return u.Email == "test@example.com" && u.ID != ""
    })).
    Return(nil)

// BAD: mock.Anything for business values
state.EXPECT().
    SetRunning(mock.Anything, mock.Anything, mock.Anything, mock.Anything). // WRONG
    Return(nil)
```

Mock constructor and assertions:

```go
func TestService_GetUser(t *testing.T) {
    mockRepo := NewMockuserStore(t)  // auto-cleanup with t
    mockRepo.EXPECT().Get(mock.Anything, "123").Return(&User{ID: "123"}, nil).Once()

    svc := NewService(mockRepo)
    user, err := svc.GetUser(context.Background(), "123")

    require.NoError(t, err)
    assert.Equal(t, "123", user.ID)
    // AssertExpectations called automatically when using NewMock*(t)
}
```

## Test organization

- One test file per source file: `user.go` → `user_test.go`
- Test helper package: `internal/testhelper/` for shared test utilities
- Fixtures: `testdata/` directory for test files (ignored by go tools)
- Integration tests: use build tags `//go:build integration`

## Failure handling

- Race conditions are blocking issues — include in findings before anything else.
- Test failures and coverage gaps belong in findings.
- If `golangci-lint` fails to run, use the debug commands above and report the linter error verbatim.
- If LSP tools are unavailable, skip reference-tracing and rely on manual file inspection.
