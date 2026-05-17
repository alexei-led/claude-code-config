# Go Architecture Reference

Language-specific over-abstraction and dead-code patterns for Go 1.25+. The shared modularity model lives in [LANGUAGE.md](LANGUAGE.md) and [DEEPENING.md](DEEPENING.md) — this file supplies only the Go-specific smells and detection.

## Run tooling first

```bash
# Dead code, complexity, and duplication analysis (2 min timeout)
golangci-lint run --timeout=2m --enable=unused,unparam,wastedassign,ineffassign,gocyclo,gocognit,cyclop,funlen,nestif,maintidx,dupl ./... 2>&1
```

LSP navigation for unused and over-abstracted code:

- `findReferences` — check if exported symbols are actually used
- `goToImplementation` — find how many implementations an interface has
- `incomingCalls` — verify functions are called (dead code detection)
- `workspaceSymbol` — search for duplicate/similar function names

Include tool output in findings. Unused code and high complexity are primary targets.

## Over-abstraction

### Unnecessary generics

Type parameters where concrete types work fine — the generic adds interface surface with no leverage. Apply the deletion test from [LANGUAGE.md](LANGUAGE.md): would removing the type parameter reveal that only one concrete type was ever used?

### Excessive options pattern

Functional options on structs with 1–2 fields. Replace with a struct literal. The pattern earns its keep when optional fields genuinely vary at call sites — not for boilerplate.

### Factory overkill

Factory or builder pattern when direct construction works. A `New*` that does nothing but `return &T{field: x}` is a pass-through (see the deletion test).

### Layer cake

Service → Repository → Store → DB when Service → DB works. Each shallow layer adds interface surface with no depth. Apply the deletion test: does the middle layer concentrate any logic, or does complexity scatter back to callers if you delete it?

### Single-impl interfaces: keep vs delete

Keep (enables testing/decoupling):

- External deps (DB, API, filesystem) — see [DEEPENING.md](DEEPENING.md) for seam discipline
- Anything you need to mock
- Structs needing non-trivial initialization

Delete (no value added):

- Pure computation
- Internal utilities
- Simple structs with safe zero values

### External service wrappers: NOT over-abstraction

Thin wrapper structs for external services (DB, APIs, queues) with multiple consumer-side interfaces is idiomatic Go. Do not flag this pattern:

```go
// GOOD: thin wrapper, no interface at producer
// internal/sqs/wrapper.go
type Wrapper struct { client *sqs.Client; queueURL string }
func (w *Wrapper) Send(ctx context.Context, body string) (string, error) { ... }
func (w *Wrapper) Receive(ctx context.Context) ([]Message, error) { ... }

// GOOD: each consumer defines its own minimal interface
// package notifier
type queue interface { Send(ctx context.Context, body string) (string, error) }

// package worker
type queue interface { Receive(ctx context.Context) ([]Message, error) }
```

This pattern enables vendor encapsulation, interface segregation, easy mocking, and vendor swappability — all real seams (see [DEEPENING.md](DEEPENING.md)).

## Pass-through functions

### One-line wrappers

Functions that just call another function with no transformation — inline or delete:

```go
// DELETE: pointless wrapper
func (s *Service) FindUser(id string) (*User, error) {
    return s.repo.Find(id)
}

// KEEP: adds value (ctx, validation, logging)
func (s *Service) FindUser(ctx context.Context, id string) (*User, error) {
    return s.repo.Find(ctx, id)
}
```

### Getters for fields

`GetName() string { return u.name }` — make the field public instead.

## Dead code

- Unused exports: exported functions/types with no external callers (use `findReferences`)
- Commented-out code: delete it — git has history
- Unused parameters: function parameters never referenced (`unparam` linter catches these)
- Backwards-compat shims: old names, re-exports, `_`-prefixed vars with no callers

## Failure handling

- If `golangci-lint` fails to run: use `golangci-lint --help` and `golangci-lint linters` to diagnose; proceed with LSP-based dead-code review and note the gap.
- If LSP tools are unavailable: skip unused-symbol detection; flag this limitation in findings.
- If no simplification opportunities are found in a focus area: report "No issues in {area}." explicitly.
