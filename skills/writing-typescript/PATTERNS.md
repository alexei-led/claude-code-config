# TypeScript Patterns Reference

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

## Type Patterns

### Avoid `any`, Use `unknown`

```typescript
// Bad
function parse(data: any): User { ... }

// Good
function parse(data: unknown): User {
  if (!isUser(data)) throw new Error("Invalid user data");
  return data;
}
```

### Discriminated Unions

```typescript
type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };

function render<T>(state: RequestState<T>) {
  switch (state.status) {
    case "idle":
      return null;
    case "loading":
      return <Spinner />;
    case "success":
      return <Data data={state.data} />;
    case "error":
      return <Error error={state.error} />;
  }
}
```

### Type Guards

```typescript
function isString(value: unknown): value is string {
  return typeof value === "string";
}

function hasId(value: unknown): value is { id: string } {
  return typeof value === "object" && value !== null && "id" in value;
}
```

### Generic Constraints

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

type WithId = { id: string };
function updateById<T extends WithId>(
  items: T[],
  id: string,
  update: Partial<T>,
): T[] {
  return items.map((item) => (item.id === id ? { ...item, ...update } : item));
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

## Error Handling

### Result Type

```typescript
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

function ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

function err<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

async function fetchUser(id: string): Promise<Result<User, ApiError>> {
  try {
    const response = await fetch(`/users/${id}`);
    if (!response.ok) return err(new ApiError(response.status));
    return ok(await response.json());
  } catch (e) {
    return err(new ApiError(500, e));
  }
}
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

## Async Patterns

### Concurrent Requests

```typescript
async function fetchAll<T>(urls: string[]): Promise<T[]> {
  const results = await Promise.all(
    urls.map((url) => fetch(url).then((r) => r.json())),
  );
  return results;
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
      await new Promise((r) => setTimeout(r, delay * Math.pow(2, i)));
    }
  }
  throw new Error("Unreachable");
}
```

## Configuration

```typescript
const ConfigSchema = z.object({
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  NODE_ENV: z
    .enum(["development", "production", "test"])
    .default("development"),
});

export const config = ConfigSchema.parse(process.env);
```

## Module Organization

### Barrel Exports

```typescript
// domain/index.ts
export { User } from "./user";
export { Product } from "./product";
export type { UserService } from "./user-service";
```

### Dependency Injection

```typescript
interface Dependencies {
  userRepo: UserRepository;
  emailService: EmailService;
  logger: Logger;
}

function createUserService(deps: Dependencies): UserService {
  return {
    async createUser(data: CreateUserInput) {
      const user = await deps.userRepo.create(data);
      await deps.emailService.sendWelcome(user.email);
      deps.logger.info("User created", { userId: user.id });
      return user;
    },
  };
}
```

## Style Guidelines

- Use `const` by default, `let` when needed
- Prefer `interface` for object shapes
- Use `type` for unions, intersections, mapped types
- Export types explicitly
- No `any` - use `unknown` and narrow
- Prefer `readonly` for immutable data
