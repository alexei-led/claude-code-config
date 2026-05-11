# TypeScript Patterns Reference

## Contents

- [Project Structure](#project-structure)
- [Interface vs Type](#interface-vs-type)
- [Discriminated Unions](#discriminated-unions)
- [Flat Control Flow: No Nested Conditions](#flat-control-flow-no-nested-conditions)
- [Avoid `any`, Use `unknown`](#avoid-any-use-unknown)
- [Result Type Pattern](#result-type-pattern)
- [Dependency Injection](#dependency-injection)
- [Async Patterns](#async-patterns)
- [Validation (Zod)](#validation-zod)
- [Style Summary](#style-summary)

## Project Structure

```
src/
├── domain/         # Business logic, entities
├── application/    # Use cases, services
├── infrastructure/ # External integrations
└── presentation/   # HTTP handlers, UI
tests/
tsconfig.json
package.json
```

## Interface vs Type

### When to Use Each

| Use Case             | Choice    |
| -------------------- | --------- |
| Object shapes        | interface |
| React props          | interface |
| Public APIs          | interface |
| Unions/intersections | type      |
| Mapped types         | type      |
| Utility types        | type      |

```typescript
// interface: object shapes, extensible
interface User {
  id: string;
  name: string;
}

interface Admin extends User {
  permissions: string[];
}

// type: unions, intersections, utilities
type UserId = string | number;
type Role = "user" | "admin";
type UserSummary = Pick<User, "id" | "name"> & { role: Role };
```

## Discriminated Unions

Model states as unions with literal tags, not boolean flags.

### Pattern

```typescript
// GOOD: discriminated union
type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };

// BAD: boolean flags
type RequestState<T> = {
  isLoading: boolean;
  isError: boolean;
  data: T | null;
  error: Error | null;
};
```

### Exhaustive Switch

```typescript
function render<T>(state: RequestState<T>): JSX.Element {
  switch (state.status) {
    case "idle":
      return <Idle />;
    case "loading":
      return <Spinner />;
    case "success":
      return <Data data={state.data} />;
    case "error":
      return <Error error={state.error} />;
    default: {
      const _exhaustive: never = state;  // Compile error if case missed
      return _exhaustive;
    }
  }
}
```

## Flat Control Flow: No Nested Conditions

### Guard Clauses Pattern

```typescript
// GOOD: flat, readable
function processOrder(order: Order | null): Result<Receipt> {
  if (!order) return err("order required");
  if (!order.id) return err("order ID required");
  if (order.items.length === 0) return err("order must have items");
  if (order.total <= 0) return err("invalid total");

  // Happy path at lowest nesting level
  return ok(saveOrder(order));
}

// BAD: deeply nested
function processOrder(order: Order | null): Result<Receipt> {
  if (order) {
    if (order.id) {
      if (order.items.length > 0) {
        if (order.total > 0) {
          return ok(saveOrder(order));
        }
      }
    }
  }
  return err("invalid order");
}
```

### Type Guard Predicates

```typescript
// Type guard for narrowing
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

// Usage: flat conditional
if (isActiveAdmin(user)) {
  // user is narrowed to User & { role: "admin" }
}
```

### Switch for Multi-Case

```typescript
// GOOD: switch instead of if-else chain
function handleEvent(event: AppEvent): void {
  switch (event.type) {
    case "click":
      handleClick(event.x, event.y);
      break;
    case "key":
      handleKey(event.code);
      break;
    case "scroll":
      handleScroll(event.delta);
      break;
  }
}
```

## Avoid `any`, Use `unknown`

```typescript
// BAD: any bypasses type checking
function parse(data: any): User { ... }

// GOOD: unknown requires narrowing
function parse(data: unknown): User {
  if (!isUser(data)) throw new Error("Invalid user data");
  return data;  // narrowed to User
}
```

## Result Type Pattern

### Implementation

```typescript
type Ok<T> = { ok: true; value: T };
type Err<E> = { ok: false; error: E };
type Result<T, E = Error> = Ok<T> | Err<E>;

const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
const err = <E>(error: E): Err<E> => ({ ok: false, error });
```

### Usage

```typescript
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

// Caller handles explicitly
const result = await fetchUser("123");
if (!result.ok) {
  if (result.error === "not-found") {
    // handle not found
  }
  return;
}
// result.value is User here
```

### Custom Errors

```typescript
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
  ) {
    super(message);
    this.name = "AppError";
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} not found: ${id}`, "NOT_FOUND", 404);
  }
}
```

## Dependency Injection

### Interface-Based DI

```typescript
interface UserRepo {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
}

interface Logger {
  info(msg: string): void;
  error(msg: string, error?: unknown): void;
}

interface Services {
  userRepo: UserRepo;
  logger: Logger;
}

function createUserService({ userRepo, logger }: Services) {
  return {
    async getUser(id: string): Promise<Result<User, "not-found">> {
      const user = await userRepo.findById(id);
      if (!user) {
        logger.info(`User ${id} not found`);
        return err("not-found");
      }
      return ok(user);
    },
  };
}
```

### React Context for DI

```typescript
const ServiceContext = createContext<Services | null>(null);

export function useServices(): Services {
  const ctx = useContext(ServiceContext);
  if (!ctx) throw new Error("ServiceContext not provided");
  return ctx;
}
```

## Async Patterns

### Concurrent Requests

```typescript
async function fetchAll<T>(urls: string[]): Promise<T[]> {
  return Promise.all(urls.map((url) => fetch(url).then((r) => r.json())));
}

async function fetchAllSettled<T>(urls: string[]): Promise<Result<T>[]> {
  const results = await Promise.allSettled(
    urls.map((url) => fetch(url).then((r) => r.json())),
  );
  return results.map((r) =>
    r.status === "fulfilled" ? ok(r.value) : err(r.reason),
  );
}
```

### Retry Logic

```typescript
async function retry<T>(
  fn: () => Promise<T>,
  attempts: number,
  delay: number,
): Promise<T> {
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === attempts - 1) throw error;
      await new Promise((r) => setTimeout(r, delay * 2 ** i));
    }
  }
  throw new Error("Unreachable");
}
```

## Validation (Zod)

```typescript
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1),
  role: z.enum(["admin", "user"]),
});

type User = z.infer<typeof UserSchema>;

function parseUser(data: unknown): User {
  return UserSchema.parse(data);
}
```

## Style Summary

- Guard clauses reduce nesting (max 2 levels)
- Discriminated unions for state (not boolean flags)
- Exhaustive switch with never check
- interface for objects, type for unions
- unknown for untrusted input (never any)
- Result type for explicit error handling
- Pass dependencies as parameters
- `const` by default, `let` when needed
- Export types explicitly
