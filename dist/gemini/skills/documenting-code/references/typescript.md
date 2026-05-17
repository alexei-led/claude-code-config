# TypeScript Documentation Slice

Language-specific documentation conventions for TypeScript 5.x. The host skill supplies workflow and verification — this file supplies only the TypeScript doc-comment conventions and examples.

## run tooling first

```bash
# type-check
bunx tsc --noEmit

# generate API docs (if typedoc configured)
bunx typedoc --out docs src/
```

Use LSP to verify coverage:

- `documentSymbol` — list all exported symbols in a file
- `hover` — check existing JSDoc/TSDoc on symbols
- `findReferences` — verify documented APIs are used correctly

## JSDoc/TSDoc conventions

Use TSDoc for library APIs. Type annotations in signatures reduce the need to repeat type info in comment bodies.

- `@param` and `@returns` for exported functions
- `@throws` when a function can throw
- `@deprecated` with migration path for old APIs
- `@example` blocks for complex functions

```typescript
/**
 * Creates an API client with the given config.
 *
 * @param config - Client configuration including base URL and auth token
 * @returns Configured client ready to make requests
 * @throws {ConfigError} If required fields are missing
 *
 * @example
 * const client = createClient({ url: "https://api.example.com", token: "..." });
 */
export function createClient(config: ClientConfig): Client
```

## type documentation

Document when the type itself is not self-evident:

- Complex generics — describe type parameters

```typescript
/**
 * Resolves a value of type T or captures an error of type E.
 * @typeParam T - The success value type
 * @typeParam E - The error type, defaults to Error
 */
type Resolver<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };
```

- Discriminated unions — document the discriminator field

```typescript
/** UI state machine; use `kind` to narrow. */
type ViewState =
  | { kind: "loading" }
  | { kind: "ready"; data: Data }
  | { kind: "error"; message: string };
```

- Utility/mapped types — explain what they produce
- `interface` vs `type` — document the reason for the choice on public APIs

## inline comment quality

Delete:

```typescript
const user = getUser(); // get the user
if (!user) return null; // return null if no user
items.map((x) => x.id); // map to ids
```

Keep:

```typescript
// timeout is 30s to match upstream API SLA
const TIMEOUT_MS = 30_000;

// use Map instead of object—need non-string keys
const cache = new Map<Symbol, Data>();

// explicit any here because library types are wrong (see issue #456)
const result = lib.call() as any;
```

## test files: minimal comments

Tests self-document through descriptive names and clear structure.

```typescript
// prefer this
it("returns error for invalid email", () => { ... });

// over this
it("test1", () => {
  // validate email  ← delete
  expect(validate("bad")).toBe(false);
});
```

Delete comments unless explaining non-obvious external system behavior or why a specific edge case matters.

## readme accuracy

- `npm install` / `bun add` commands must work.
- Usage examples must compile and run with current types.
- API documentation must match current exported API.
- Document tsconfig requirements if unusual.

## failure handling

- If typedoc is not configured, note the gap, skip that check, and continue with JSDoc review via LSP and manual inspection.
- If LSP is unavailable, read files directly; note the limitation.
- If README examples compile but behavior is wrong, flag as a documentation accuracy issue with the specific discrepancy.
- If JSDoc partially matches current code, report what is wrong and what the correct description should be — do not guess at intent.
- If no exported symbols are found, state that no public API was detected and skip JSDoc checks.
