# TypeScript Testing Reference

## Framework: Vitest

```bash
bun add -d vitest @testing-library/react @testing-library/jest-dom
```

## Unit Tests

```typescript
import { describe, it, expect } from "vitest";

describe("validateEmail", () => {
  it("accepts valid email", () => {
    expect(validateEmail("user@example.com")).toBe(true);
  });

  it("rejects empty string", () => {
    expect(validateEmail("")).toBe(false);
  });

  it("rejects invalid format", () => {
    expect(validateEmail("invalid")).toBe(false);
  });
});
```

## Async Tests

```typescript
describe("fetchUser", () => {
  it("returns user data", async () => {
    const user = await fetchUser("123");
    expect(user.id).toBe("123");
  });

  it("throws on not found", async () => {
    await expect(fetchUser("unknown")).rejects.toThrow("Not found");
  });
});
```

## Mocking

```typescript
import { vi, describe, it, expect, beforeEach } from "vitest";

const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

describe("api", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls fetch with correct url", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: "123" }),
    });

    await getUser("123");

    expect(mockFetch).toHaveBeenCalledWith("/api/users/123");
  });
});
```

## Module Mocking

```typescript
import { vi, describe, it, expect } from "vitest";
import { sendEmail } from "./email";
import { createUser } from "./user-service";

vi.mock("./email", () => ({
  sendEmail: vi.fn(),
}));

describe("createUser", () => {
  it("sends welcome email", async () => {
    await createUser({ email: "test@example.com" });

    expect(sendEmail).toHaveBeenCalledWith(
      expect.objectContaining({ to: "test@example.com" }),
    );
  });
});
```

## React Component Tests

```typescript
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

describe("Button", () => {
  it("renders label", () => {
    render(<Button label="Click me" onClick={() => {}} />);
    expect(screen.getByText("Click me")).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const handleClick = vi.fn();
    render(<Button label="Click" onClick={handleClick} />);

    fireEvent.click(screen.getByRole("button"));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("is disabled when disabled prop is true", () => {
    render(<Button label="Click" onClick={() => {}} disabled />);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
```

## Hook Tests

```typescript
import { renderHook, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

describe("useUser", () => {
  it("fetches user data", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: "123", name: "Test" }),
    } as Response);

    const { result } = renderHook(() => useUser("123"));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toEqual({ id: "123", name: "Test" });
  });
});
```

## API Route Tests

```typescript
import { describe, it, expect } from "vitest";

describe("POST /api/users", () => {
  it("creates user with valid data", async () => {
    const response = await app.request("/api/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "test@example.com", name: "Test" }),
    });

    expect(response.status).toBe(201);
    const data = await response.json();
    expect(data.id).toBeDefined();
  });

  it("returns 400 for invalid data", async () => {
    const response = await app.request("/api/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "invalid" }),
    });

    expect(response.status).toBe(400);
  });
});
```

## Coverage

```bash
vitest --coverage
vitest --coverage --coverage.thresholds.lines=80
```

## Configuration (vitest.config.ts)

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    coverage: {
      reporter: ["text", "html"],
      exclude: ["node_modules/", "tests/"],
    },
  },
});
```

## Guidelines

- Test behavior, not implementation
- Use descriptive test names
- One assertion per test (when practical)
- Mock external dependencies
- Keep tests independent
