# Go Patterns Reference

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

## Interfaces

### Define at Consumer

Interfaces belong where they're USED, not where they're implemented.

```go
// service/user.go - consumer defines what it needs
type UserStore interface {
    Get(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
}

type Service struct {
    store UserStore
}
```

```go
// repo/postgres.go - implementation returns concrete type
type PostgresStore struct{ db *sql.DB }

func (s *PostgresStore) Get(ctx context.Context, id string) (*User, error) {
    // ...
}
```

### Keep Interfaces Focused

Small interfaces are better. Prefer composition.

```go
// Good: focused interfaces
type Reader interface { Read(ctx context.Context, id string) (*Entity, error) }
type Writer interface { Write(ctx context.Context, e *Entity) error }
type Deleter interface { Delete(ctx context.Context, id string) error }

// Compose when needed
type ReadWriter interface {
    Reader
    Writer
}
```

```go
// Bad: kitchen sink interface
type Repository interface {
    Get(ctx context.Context, id string) (*Entity, error)
    List(ctx context.Context, filter Filter) ([]*Entity, error)
    Save(ctx context.Context, e *Entity) error
    Delete(ctx context.Context, id string) error
    Archive(ctx context.Context, id string) error
    // ... 10 more methods
}
```

## Type Visibility

Prefer private (lowercase) types unless they need external access.

```go
// internal/service/user.go

// userService is private - exposed via interface or constructor
type userService struct {
    store UserStore
    cache cache
}

// NewUserService exposes a public interface, not the struct
func NewUserService(store UserStore) *userService {
    return &userService{store: store}
}

// config is private, no reason to export
type config struct {
    timeout time.Duration
    retries int
}
```

Public types only when:

- Part of your API contract
- Needed by external packages
- Used in function signatures that must be public

## Comments

Write comments that explain WHY, not WHAT. Avoid obvious comments.

```go
// Bad: obvious
// GetUser gets a user
func GetUser(id string) (*User, error)

// incrementCounter increments the counter by 1
counter++

// Good: explains non-obvious behavior
// GetUser returns ErrNotFound if user doesn't exist, not nil.
func GetUser(id string) (*User, error)

// Batch size tuned for Postgres query planner; larger batches cause seq scans.
const batchSize = 100
```

Package comments are useful:

```go
// Package ratelimit provides token bucket rate limiting with
// automatic backpressure and circuit breaking for HTTP clients.
package ratelimit
```

## Design Patterns

### Functional Options

```go
type Option func(*Config)

func WithTimeout(d time.Duration) Option {
    return func(c *Config) { c.Timeout = d }
}

func New(opts ...Option) *Client {
    cfg := &Config{Timeout: 30 * time.Second}
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

## Error Handling

### Wrap with Context

```go
if err := db.QueryRow(ctx, query, id).Scan(&user); err != nil {
    if errors.Is(err, sql.ErrNoRows) {
        return nil, ErrNotFound
    }
    return nil, fmt.Errorf("query user %s: %w", id, err)
}
```

### Sentinel Errors

```go
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

if errors.Is(err, ErrNotFound) {
    return http.StatusNotFound
}
```

## Concurrency

### Worker Pool

```go
func ProcessBatch(ctx context.Context, items []Item, workers int) error {
    g, ctx := errgroup.WithContext(ctx)
    ch := make(chan Item)

    for i := 0; i < workers; i++ {
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

## Style

- Early returns reduce nesting
- Meaningful names: `userID` not `id`, `cfg` not `c`
- Short names in small scopes: `for i, v := range items`
- No stuttering: `user.Name` not `user.UserName`
- Group imports: stdlib, external, internal
