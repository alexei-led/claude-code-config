---
name: go-patterns
description: Idiomatic Go development. Use when writing Go code or discussing Go design. Emphasizes stdlib, concrete types, simple error handling, and minimal dependencies.
---

# Go Principles

## Design

- Stdlib first, external deps only when justified
- Concrete types over interfaces (define interfaces at consumer)
- Composition over inheritance
- Accept interfaces, return structs
- Fail fast with clear errors

## Structure

- `cmd/` entry points, `internal/` private code, `pkg/` only if truly reusable
- One package = one purpose
- Flat over nested when possible

## Style

- Early returns, reduce nesting
- Meaningful names: `userID` not `id`, `cfg` not `c`
- Short variable names in small scopes
- No stuttering: `user.Name` not `user.UserName`

## Errors

- `fmt.Errorf("context: %w", err)` - wrap with context
- Handle errors where you can act, propagate otherwise
- No custom error hierarchies unless truly needed

## Concurrency

- Channels for synchronization, not sleep
- Context for cancellation and timeouts
- `select` with timeout, never busy loops

## Testing

- Table-driven for multiple cases
- Testify for assertions
- Mockery for interface mocks
- Test behavior, not implementation

## CLI Pattern

- urfave/cli for complex CLIs
- Multiple output formats (table, JSON, CSV)
- Embedded data for offline resilience
- Dry-run mode for destructive operations
