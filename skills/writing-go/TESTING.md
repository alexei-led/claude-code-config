# Go Testing Reference

## Frameworks

- **testify**: Assertions (`require`, `assert`)
- **mockery**: Interface mock generation with EXPECT pattern

```bash
go install github.com/vektra/mockery/v2@latest

mockery --all --keeptree
mockery --name=UserStore --dir=internal/service
```

## require vs assert

**require** stops test immediately on failure (`t.FailNow()`) — use for **prerequisites**.
**assert** logs failure but continues (`t.Fail()`) — use for **independent checks**.

```go
func TestUser(t *testing.T) {
    user, err := GetUser("123")

    // Prerequisites: must pass or test is meaningless
    require.NoError(t, err)
    require.NotNil(t, user)

    // Independent assertions: collect all failures
    assert.Equal(t, "123", user.ID)
    assert.Equal(t, "test@example.com", user.Email)
    assert.True(t, user.IsActive)
}
```

**When to use require:**

- Nil checks before accessing fields/methods
- Error checks when success is required to proceed
- Setup validation (db connection, file exists)
- Any precondition where failure makes remaining assertions meaningless

**When to use assert:**

- Multiple property checks on same object
- Validating several independent conditions
- When you want to see all failures in one run

**Never call require/assert from goroutines** — must be called from test goroutine.

## Table-Driven Tests

```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        wantErr string
    }{
        {"valid", "user@example.com", ""},
        {"empty", "", "email required"},
        {"no_at", "invalid", "invalid format"},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidateEmail(tt.email)
            if tt.wantErr == "" {
                require.NoError(t, err)
            } else {
                require.ErrorContains(t, err, tt.wantErr)
            }
        })
    }
}
```

## Mocking with Mockery

Generate mocks with EXPECT pattern (typesafe):

```go
//go:generate mockery --name=UserStore
type UserStore interface {
    Get(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
}
```

```go
func TestService_GetUser(t *testing.T) {
    store := mocks.NewUserStore(t)
    svc := NewService(store)

    expected := &User{ID: "123", Name: "Test"}
    store.EXPECT().
        Get(mock.Anything, "123").
        Return(expected, nil)

    user, err := svc.GetUser(context.Background(), "123")
    require.NoError(t, err)
    assert.Equal(t, expected, user)
}

func TestService_CreateUser(t *testing.T) {
    store := mocks.NewUserStore(t)
    svc := NewService(store)

    store.EXPECT().
        Save(mock.Anything, mock.MatchedBy(func(u *User) bool {
            return u.Email == "test@example.com"
        })).
        Return(nil)

    err := svc.CreateUser(context.Background(), "test@example.com")
    require.NoError(t, err)
}

func TestService_GetUser_NotFound(t *testing.T) {
    store := mocks.NewUserStore(t)
    svc := NewService(store)

    store.EXPECT().
        Get(mock.Anything, "unknown").
        Return(nil, ErrNotFound)

    _, err := svc.GetUser(context.Background(), "unknown")
    require.ErrorIs(t, err, ErrNotFound)
}
```

## HTTP Handler Tests

```go
func TestHandler_CreateUser(t *testing.T) {
    svc := mocks.NewUserService(t)
    h := NewHandler(svc)

    svc.EXPECT().
        CreateUser(mock.Anything, mock.AnythingOfType("CreateUserRequest")).
        Return(&User{ID: "123"}, nil)

    body := `{"name": "Test", "email": "test@example.com"}`
    req := httptest.NewRequest(http.MethodPost, "/users", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    rec := httptest.NewRecorder()

    h.CreateUser(rec, req)

    assert.Equal(t, http.StatusCreated, rec.Code)
}
```

## Go 1.25: testing/synctest

Deterministic concurrent testing:

```go
func TestRetryWithBackoff(t *testing.T) {
    synctest.Run(func() {
        attempts := 0
        client := &RetryClient{
            Do: func() error {
                attempts++
                if attempts < 3 {
                    return errors.New("temporary")
                }
                return nil
            },
            MaxRetries: 3,
            Backoff:    time.Second,
        }

        err := client.Execute()
        require.NoError(t, err)
        assert.Equal(t, 3, attempts)
    })
}
```

## Integration Tests

```go
//go:build integration

func TestDatabase_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }

    db, cleanup := setupTestDB(t)
    defer cleanup()

    store := NewPostgresStore(db)
    user := &User{Name: "Test", Email: "test@example.com"}

    err := store.Save(context.Background(), user)
    require.NoError(t, err)

    got, err := store.Get(context.Background(), user.ID)
    require.NoError(t, err)
    assert.Equal(t, user.Name, got.Name)
}
```

## Benchmarks

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData(1000)
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}

func BenchmarkProcess_Parallel(b *testing.B) {
    data := generateTestData(1000)
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            Process(data)
        }
    })
}
```

## Test Fixtures

```go
func loadFixture(t *testing.T, name string) []byte {
    t.Helper()
    data, err := os.ReadFile(filepath.Join("testdata", name))
    require.NoError(t, err)
    return data
}
```

## Coverage

```bash
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
go tool cover -func=coverage.out | grep total
```

## Guidelines

- Test behavior, not implementation
- One logical assertion per test case
- Use `t.Parallel()` for independent tests
- Prefer table-driven for multiple cases
- Keep tests focused and readable
