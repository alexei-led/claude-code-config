# TypeScript principles and verification

Read this before generating TypeScript code. Covers strict-typing, control-flow
and error-handling principles, the no-destructive-commands safety rule, and the
post-generation verification loop.

## Safety

Do not run destructive shell commands. For broad or risky changes, state the risk and ask before acting.

## Core Philosophy

### Strict Mode Always

- Enable all strict checks in tsconfig
- Treat `any` as a bug—use `unknown` for untrusted input
- noUncheckedIndexedAccess, exactOptionalPropertyTypes

### Interface vs Type

- interface for object shapes (extensible, mergeable)
- type for unions, intersections, mapped types
- interface for React props and public APIs

### Discriminated Unions

- Literal `kind`/`type` tag for variants
- Exhaustive switch with never check
- Model states as unions, not boolean flags

### Flat Control Flow

- Guard clauses with early returns
- Type guards and predicate helpers
- Maximum 2 levels of nesting

### Result Type Pattern

- Result<T, E> for explicit error handling
- Discriminated union for success/failure
- Custom Error subclasses for instanceof

## Verify Generated Code

After generating code, always verify it compiles, tests pass, and lint runs when configured:

```bash
bunx tsc --noEmit
bun test
bun run lint
bun run format --check
```

Use the project's configured commands if different.
