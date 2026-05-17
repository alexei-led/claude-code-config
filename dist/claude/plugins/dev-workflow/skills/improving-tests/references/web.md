# Web Test Slice

Language-specific test material for E2E tests with Playwright. The host skill supplies scope, workflow, and the output contract — this file supplies only the Playwright tooling, patterns, and focus-area checks.

## Run tooling first

```bash
npx playwright test --list                  # list tests (or bunx)
npx playwright test --reporter=list         # run only when explicitly asked (or bunx)
```

If Playwright is not configured, say so in the report rather than guessing.

## Locator strategy

Prefer in this order:

1. `getByRole()` — semantic
2. `getByLabel()` — forms
3. `getByText()` — visible text
4. `getByTestId()` — last resort

Avoid XPath, deep CSS selectors, and generated IDs.

```javascript
// GOOD
await page.getByRole("button", { name: "Submit" }).click();
await page.getByLabel("Email").fill("test@test.com");

// BAD
await page.click(".btn-primary");
```

## Waiting

Playwright auto-waits — do not add sleeps. Use `expect(locator).toBeVisible()` for assertions.

```javascript
// GOOD
await expect(page.getByText("Success")).toBeVisible();

// BAD
await page.waitForTimeout(2000);
```

## Test quality

- One flow per test
- Descriptive names: `test('user can submit form')`
- No duplicate tests
- Delete pointless tests (tests that only check the page loads)

## HTMX testing

```javascript
// Wait for HTMX to complete
await page.getByRole("button", { name: "Load" }).click();
await expect(page.getByText("Loaded content")).toBeVisible();

// Check partial update
await page.getByRole("button", { name: "Delete" }).click();
await expect(page.getByRole("row", { name: "Item 1" })).not.toBeVisible();
```

## Failure handling

- If Playwright is not configured, note it in the report and skip test execution steps.
- If `playwright test --list` returns no tests, report that and do not make assumptions about test coverage.
- If tests fail during execution (when explicitly asked to run), quote the failure output and identify whether the cause is a locator issue, timing issue, or test logic issue.
- If test files exist but have no assertions, flag each as a finding — a test without assertions proves nothing.
- If no issues are found, output "No issues found." — do not invent findings.
