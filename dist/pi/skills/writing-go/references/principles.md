# Go principles and verification

Read this before generating Go code. Covers the stdlib-first stance, control-flow
and error-handling principles, the no-destructive-commands safety rule, and the
post-generation verification loop.

## Safety

Do not run destructive shell commands. For broad or risky changes, state the risk and ask before acting.

## Core Philosophy

### Stdlib and Mature Libraries First

- Prefer Go stdlib solutions; add a library only when concrete requirements beat stdlib simplicity
- Choose mature, well-maintained libs when needed

### Concrete Types Over `any`

- Never use `interface{}` or `any` when a concrete type works
- Generics for reusable utilities, concrete types for business logic
- Accept interfaces, return structs

### Private Interfaces at Consumer

- Define interfaces private (lowercase) where used
- Decouples code, enables testing
- Implementation returns concrete types

### Flat Control Flow

- Early returns, guard clauses
- No nested IFs—max 2 levels
- Switch for multi-case logic

### Explicit Error Handling

- Always wrap with context
- Use `errors.Is()`/`errors.As()`
- No bare `return err`

## Verify Generated Code

After generating code, always verify it compiles, tests pass, and lint runs when configured:

```bash
go test ./...
go test -race ./...
go vet ./...
golangci-lint run ./...
```

Use the project's configured commands if different.
