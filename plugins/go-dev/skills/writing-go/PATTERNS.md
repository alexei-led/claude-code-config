# Go Patterns Reference

## Contents

- [Project Structure](#project-structure)
- [Interfaces: Private at Consumer](#interfaces-private-at-consumer)
- [Flat Control Flow: No Nested IFs](#flat-control-flow-no-nested-ifs)
- [Concrete Types Over `any`](#concrete-types-over-any)
- [Error Handling](#error-handling)
- [Design Patterns](#design-patterns)
- [Concurrency](#concurrency)
- [Configuration](#configuration)
- [Comments](#comments)
- [Style Summary](#style-summary)

## Project Structure

```
cmd/           # Entry points (main.go per binary)
internal/      # Private application code
├── domain/    # Business entities and logic
├── service/   # Business operations
├── handler/   # HTTP/gRPC handlers
└── repo/      # Data access
pkg/           # Public libraries (rarely needed)
```

## Interfaces: Private at Consumer

Interfaces belong where they're USED, not where implemented. Always private (lowercase).

### Pattern

```go
// internal/service/user.go - consumer defines what it needs
type userStore interface {  // private!
    Get(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
}

type Service struct {
    store userStore  // depends on interface
}

func NewService(store userStore) *Service {
    return &Service{store: store}
}
```

```go
// internal/repo/postgres.go - implementation returns concrete
type PostgresStore struct{ db *sql.DB }

func NewPostgresStore(db *sql.DB) *PostgresStore {  // returns concrete!
    return &PostgresStore{db: db}
}

func (s *PostgresStore) Get(ctx context.Context, id string) (*User, error) {
    // implementation
}
```

### Why Private Interfaces?

- **Decoupling**: Consumer defines contract, not provider
- **Testability**: Easy to mock in tests
- **Flexibility**: Multiple implementations satisfy same interface
- **No import cycles**: Interface lives with consumer

### Keep Interfaces Small

```go
// GOOD: focused interfaces
type reader interface { Read(ctx context.Context, id string) (*Entity, error) }
type writer interface { Write(ctx context.Context, e *Entity) error }

// Compose when needed
type readWriter interface {
    reader
    writer
}
```

```go
// BAD: kitchen sink interface
type Repository interface {
    Get(ctx context.Context, id string) (*Entity, error)
    List(ctx context.Context, filter Filter) ([]*Entity, error)
    Save(ctx context.Context, e *Entity) error
    Delete(ctx context.Context, id string) error
    Archive(ctx context.Context, id string) error
    // ... too many methods
}
```

## Flat Control Flow: No Nested IFs

### Guard Clauses Pattern

```go
// GOOD: flat, readable
func processOrder(order *Order) error {
    if order == nil {
        return ErrNilOrder
    }
    if order.ID == "" {
        return ErrMissingOrderID
    }
    if len(order.Items) == 0 {
        return ErrEmptyOrder
    }
    if order.Total <= 0 {
        return ErrInvalidTotal
    }

    // Happy path at lowest nesting level
    return s.store.Save(ctx, order)
}

// BAD: deeply nested
func processOrder(order *Order) error {
    if order != nil {
        if order.ID != "" {
            if len(order.Items) > 0 {
                if order.Total > 0 {
                    return s.store.Save(ctx, order)
                }
            }
        }
    }
    return errors.New("invalid order")
}
```

### Extract Complex Conditions

```go
// GOOD: extract to functions
func (s *Service) canProcessPayment(user *User, amount float64) error {
    if !user.IsActive {
        return ErrInactiveUser
    }
    if user.Balance < amount {
        return ErrInsufficientFunds
    }
    if amount > s.maxTransaction {
        return ErrExceedsLimit
    }
    return nil
}

func (s *Service) ProcessPayment(ctx context.Context, userID string, amount float64) error {
    user, err := s.users.Get(ctx, userID)
    if err != nil {
        return fmt.Errorf("get user: %w", err)
    }

    if err := s.canProcessPayment(user, amount); err != nil {
        return err
    }

    return s.processTransaction(ctx, user, amount)
}
```

### Switch for Multi-Case Logic

```go
// GOOD: switch instead of if-else chain
func handleStatus(status Status) error {
    switch status {
    case StatusPending:
        return processPending()
    case StatusActive:
        return processActive()
    case StatusComplete:
        return nil
    case StatusFailed:
        return ErrFailed
    default:
        return fmt.Errorf("unknown status: %s", status)
    }
}

// BAD: if-else chain
func handleStatus(status Status) error {
    if status == StatusPending {
        return processPending()
    } else if status == StatusActive {
        return processActive()
    } else if status == StatusComplete {
        return nil
    } else if status == StatusFailed {
        return ErrFailed
    } else {
        return fmt.Errorf("unknown status: %s", status)
    }
}
```

## Concrete Types Over `any`

### Use Concrete Types

```go
// GOOD: concrete types
func ProcessUsers(users []User) error { ... }
func GetConfig() *Config { ... }
func ParseResponse(data []byte) (*Response, error) { ... }

// BAD: unnecessary any
func ProcessItems(items []any) error { ... }
func GetConfig() any { ... }
func ParseResponse(data []byte) (any, error) { ... }
```

### When Generics Are Appropriate

```go
// GOOD: generic utility for reuse
func Map[T, U any](items []T, fn func(T) U) []U {
    result := make([]U, len(items))
    for i, item := range items {
        result[i] = fn(item)
    }
    return result
}

// GOOD: generic retry logic
func Retry[T any](ctx context.Context, fn func() (T, error), maxAttempts int) (T, error) {
    var result T
    var err error
    for i := 0; i < maxAttempts; i++ {
        result, err = fn()
        if err == nil {
            return result, nil
        }
        select {
        case <-ctx.Done():
            return result, ctx.Err()
        case <-time.After(time.Second * time.Duration(i+1)):
        }
    }
    return result, err
}
```

### Generics vs Concrete: Decision Guide

| Use Case              | Choice         |
| --------------------- | -------------- |
| Business logic        | Concrete types |
| Domain entities       | Concrete types |
| Hot paths             | Concrete types |
| Utility functions     | Generics       |
| Collection helpers    | Generics       |
| Retry/circuit breaker | Generics       |

## Error Handling

### Always Wrap with Context

```go
// GOOD: meaningful context
if err := db.QueryRow(ctx, query, id).Scan(&user); err != nil {
    if errors.Is(err, sql.ErrNoRows) {
        return nil, ErrNotFound
    }
    return nil, fmt.Errorf("query user %s: %w", id, err)
}

// BAD: bare return
if err := db.QueryRow(ctx, query, id).Scan(&user); err != nil {
    return nil, err  // no context!
}
```

### Sentinel Errors

```go
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrConflict     = errors.New("conflict")
)

// Check with errors.Is
if errors.Is(err, ErrNotFound) {
    return http.StatusNotFound
}
```

### Error Inspection

```go
// errors.Is for sentinel errors
if errors.Is(err, context.DeadlineExceeded) {
    return nil, ErrTimeout
}

// errors.As for typed errors
var validationErr *ValidationError
if errors.As(err, &validationErr) {
    return nil, fmt.Errorf("validation failed: %s", validationErr.Field)
}
```

## Design Patterns

### Functional Options

```go
type Option func(*Config)

func WithTimeout(d time.Duration) Option {
    return func(c *Config) { c.Timeout = d }
}

func WithRetries(n int) Option {
    return func(c *Config) { c.Retries = n }
}

func New(opts ...Option) *Client {
    cfg := &Config{Timeout: 30 * time.Second, Retries: 3}
    for _, opt := range opts {
        opt(cfg)
    }
    return &Client{cfg: cfg}
}
```

### Context Propagation

```go
func (s *service) Process(ctx context.Context, req Request) error {
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()

    data, err := s.fetch(ctx, req.ID)
    if err != nil {
        return fmt.Errorf("fetch: %w", err)
    }
    return s.store(ctx, data)
}
```

### Graceful Shutdown

```go
func main() {
    ctx, stop := signal.NotifyContext(context.Background(),
        syscall.SIGINT, syscall.SIGTERM)
    defer stop()

    srv := &http.Server{Addr: ":8080", Handler: handler}

    go func() {
        if err := srv.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    <-ctx.Done()

    shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    srv.Shutdown(shutdownCtx)
}
```

## Concurrency

### Worker Pool with errgroup

```go
func ProcessBatch(ctx context.Context, items []Item, workers int) error {
    g, ctx := errgroup.WithContext(ctx)
    ch := make(chan Item)

    for range workers {
        g.Go(func() error {
            for item := range ch {
                if err := process(ctx, item); err != nil {
                    return err
                }
            }
            return nil
        })
    }

    g.Go(func() error {
        defer close(ch)
        for _, item := range items {
            select {
            case ch <- item:
            case <-ctx.Done():
                return ctx.Err()
            }
        }
        return nil
    })

    return g.Wait()
}
```

## Configuration

```go
type config struct {
    Port        int           `env:"PORT" envDefault:"8080"`
    DatabaseURL string        `env:"DATABASE_URL,required"`
    Timeout     time.Duration `env:"TIMEOUT" envDefault:"30s"`
}

func loadConfig() (*config, error) {
    var cfg config
    if err := env.Parse(&cfg); err != nil {
        return nil, fmt.Errorf("parse config: %w", err)
    }
    return &cfg, nil
}
```

## Comments

Write comments that explain WHY, not WHAT.

```go
// BAD: obvious
// GetUser gets a user
func GetUser(id string) (*User, error)

// GOOD: explains non-obvious behavior
// GetUser returns ErrNotFound if user doesn't exist, not nil.
func GetUser(id string) (*User, error)

// GOOD: explains tuning decision
// Batch size tuned for Postgres query planner; larger batches cause seq scans.
const batchSize = 100
```

## Style Summary

- Early returns reduce nesting (max 2 levels)
- Meaningful names: `userID` not `id`, `cfg` not `c`
- Short names in small scopes: `for i, v := range items`
- No stuttering: `user.Name` not `user.UserName`
- Group imports: stdlib, external, internal
- Private by default, public only when necessary
