---
description:
  Idiomatic TypeScript development. Use when writing TypeScript code, Node.js
  services, React apps, or discussing TS patterns. Emphasizes strict typing, composition,
  and modern tooling (bun/vite). NOT for Go, Python, plain HTML/CSS/JS, or
  server-rendered templates (use writing-web for those).
name: writing-typescript
---

# TypeScript Development (5.x)

## Critical Output Rules

- State strict TypeScript choices explicitly: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, no `any` by default, and `unknown` for untrusted input.
- Validate untrusted API/JSON responses at the boundary before returning typed data.
- Favor composition and small functions/hooks over large classes, global state, or mixed concerns.
- Handle async errors explicitly with `Result`/discriminated unions or typed thrown errors at boundaries.
- Always mention behavior tests for success and failure paths. For React, include component or user-behavior tests for loading, success, error, and validation states.
- Include verification commands when code changes: `bunx tsc --noEmit`, `bun test`, and lint/format commands when configured.
- Keep dependencies minimal; add schema/form libraries only when real complexity beats a small type guard or helper.
- Do not run destructive shell commands. For broad or risky changes, state the risk and ask before acting.

## Core Philosophy

Strict-mode-always, interface-vs-type, discriminated unions, flat control flow, the Result-type error pattern, the no-destructive-commands safety rule, and the post-generation verification loop are in [references/principles.md](references/principles.md) — read it before generating code.

## Quick Patterns

### Discriminated Unions (Not Boolean Flags)

```typescript
// GOOD: discriminated union for state
type LoadState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: string };

// BAD: boolean flags
type LoadState = {
  isLoading: boolean;
  isError: boolean;
  data: T | null;
  error: string | null;
};
```

### Flat Control Flow (No Nesting)

```typescript
// GOOD: guard clauses, early returns
function process(user: User | null): Result<Data> {
  if (!user) return err("no user");
  if (!user.isActive) return err("inactive");
  if (user.role !== "admin") return err("not admin");
  return ok(doWork(user)); // happy path at end
}

// BAD: nested conditions
function process(user: User | null): Result<Data> {
  if (user) {
    if (user.isActive) {
      if (user.role === "admin") {
        return ok(doWork(user));
      }
    }
  }
  return err("invalid");
}
```

### Type Guards

```typescript
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "name" in value
  );
}

// Predicate helper for flat code
const isActiveAdmin = (u: User | null): u is User & { role: "admin" } =>
  !!u && u.isActive && u.role === "admin";
```

### Result Type

```typescript
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
const err = <E>(error: E): Result<never, E> => ({ ok: false, error });

async function fetchUser(
  id: string,
): Promise<Result<User, "not-found" | "network">> {
  try {
    const res = await fetch(`/users/${id}`);
    if (res.status === 404) return err("not-found");
    if (!res.ok) return err("network");
    return ok(await res.json());
  } catch {
    return err("network");
  }
}
```

### Exhaustive Switch

```typescript
function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "square":
      return shape.size ** 2;
    case "rect":
      return shape.width * shape.height;
    default: {
      const _exhaustive: never = shape; // Error if variant missed
      return _exhaustive;
    }
  }
}
```

## tsconfig.json Essentials

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noImplicitOverride": true,
    "isolatedModules": true
  }
}
```

## References

- [principles.md](references/principles.md) - Core philosophy, safety rule, and verification loop (read before generating code)
- [PATTERNS.md](references/PATTERNS.md) - Code patterns and style
- [REACT.md](references/REACT.md) - React component patterns
- [TESTING.md](references/TESTING.md) - Testing with vitest

## Commands

```bash
bun install              # Install deps
bun run build            # Build
bun test                 # Test
bun run lint             # Lint
bun run format           # Format
```

## Failure Cases

- **No tsconfig.json found**: run `find . -name 'tsconfig.json'` to locate the project root before generating code; do not assume a single root.
- **`tsc --noEmit` or test failure after generation**: quote the failing line, state the cause, show the exact fix. For `Type 'X' is not assignable to type 'Y'` errors, check discriminated union tags and generic constraints before widening types.
