# TypeScript Architecture Reference

Language-specific over-abstraction and dead-code patterns for TypeScript 5.x. The shared modularity model lives in [LANGUAGE.md](LANGUAGE.md) and [DEEPENING.md](DEEPENING.md) — this file supplies only the TypeScript-specific smells and detection.

## Run tooling first

```bash
# Type checking
bunx tsc --noEmit 2>&1

# Find unused exports (if knip configured)
bunx knip 2>&1

# Lint for complexity
bun run lint 2>&1
```

LSP navigation for unused and over-abstracted code:

- `findReferences` — check if exported symbols are actually used
- `goToImplementation` — find how many implementations an interface has
- `incomingCalls` — verify functions are called (dead code detection)
- `workspaceSymbol` — search for duplicate/similar function names

Include tool output in findings. Unused exports and high complexity are primary targets.

## Over-abstraction

### Single-implementation interfaces

An `interface` with only one class implementing it adds a seam with no real variation (see [DEEPENING.md](DEEPENING.md): one adapter = hypothetical seam).

When a single-impl interface IS valuable:

- External dependencies (DB, APIs) that need mocking
- Dependency injection boundaries
- Testing seams where a second adapter is planned and confirmed

When it is NOT valuable:

- Internal utilities
- Pure functions
- Simple data transformations

```typescript
// BAD: unnecessary interface for internal utility
interface StringFormatter {
  format(s: string): string;
}
class UpperCaseFormatter implements StringFormatter {
  format(s: string) { return s.toUpperCase(); }
}

// GOOD: just use a function
const toUpperCase = (s: string) => s.toUpperCase();
```

### Excessive generics

Type parameters where concrete types work fine. If `T` only ever resolves to one type at call sites, the generic adds interface surface with no depth.

### Factory overkill

Factory or builder pattern when direct construction works. A factory that returns `new Foo(x, y)` with no logic is a pass-through.

### Layer cake

Service → Repository → Store → Client when fewer layers work. Apply the deletion test from [LANGUAGE.md](LANGUAGE.md): does the middle layer concentrate any logic?

### Over-engineered types

Complex mapped or conditional types for cases where a simple concrete type works. Type gymnastics that obscure intent without adding safety.

## Pass-through functions

Functions that just delegate with no transformation — inline or delete:

```typescript
// BAD: pointless wrapper
function getUser(id: string) {
  return userRepo.findById(id);
}

// KEEP only if: satisfies an interface, adds logging/metrics/validation,
// or provides a meaningfully simpler public API
```

Getters for public fields: `getName() { return this.name; }` — make the field public instead.

## Dead code

- Unused exports: exported functions/types with no importers (use `knip` or `findReferences`)
- Commented-out code: delete it — git has history
- Unused parameters: function parameters never referenced
- Unreachable code: code after `return`/`throw`
- Legacy compatibility: old type aliases, re-exports, deprecated wrappers

```typescript
// BAD: unused export, no importers
export function legacyHelper() { ... }

// BAD: commented-out block
// function oldImplementation() { ...50 lines... }

// GOOD: delete both
```

## Nested ternaries

Replace with switch or object lookup — the TypeScript-idiomatic simplification:

```typescript
// BAD: nested ternary
const status = isAdmin
  ? "admin"
  : isUser
    ? "user"
    : isGuest
      ? "guest"
      : "unknown";

// GOOD: object lookup
const roleMap = { admin: "admin", user: "user", guest: "guest" } as const;
const status = roleMap[role] ?? "unknown";
```

## Failure handling

- If `knip` is not configured: note the gap; skip unused-export detection and rely on LSP `findReferences` instead.
- If LSP is unavailable: fall back to reading files directly; note the limitation in findings.
- If lint tool is unavailable: note the gap and continue with manual complexity review.
- If a simplification would change behavior: do not propose it — flag the complexity and note that a safe refactor requires tests first.
- If an abstraction looks unnecessary but has no tests: flag as a simplification candidate and note that removal requires test coverage to verify behavior is preserved.
