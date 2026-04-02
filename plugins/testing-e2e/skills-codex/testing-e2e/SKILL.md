---
name: testing-e2e
description: Sequential E2E workflow — identify test targets, generate Playwright test scripts written to /tmp, run them with node, capture failures, fix and re-run until passing. Supports TypeScript tests and Go/HTMX applications.
---

# E2E Testing with Playwright

Generate and run end-to-end tests using Playwright. Work through the steps sequentially. Keep going after failures — read the error, fix the script, and re-run until all tests pass.

## Step 1: Parse arguments

Check `$ARGUMENTS`:

- `run` — run existing E2E tests in the project
- `record` — generate a script that launches a visible browser for recording
- `generate <description>` — generate a new test for the described flow
- `verify <feature>` — verify a specific feature works end-to-end
- (empty) — ask the user in plain prose: "What E2E task should I run — execute existing tests, generate a new test, record a session, or verify a feature?"

Wait for their answer if nothing was supplied.

## Step 2: Find existing test context

Use Glob and Read to understand what already exists. Do not assume.

Look for:

- Existing test files: `**/*.spec.ts`, `**/*.test.ts`, `**/e2e/**`
- A `playwright.config.ts` or `playwright.config.js` — read it to understand base URLs, timeouts, and project settings
- A dev server start command in `package.json` scripts (`dev`, `start`, `serve`)

Note the base URL the app runs on. Note whether Playwright is already installed (`node_modules/@playwright/test`).

## Step 3: Execute based on action

### Run existing tests

```bash
npx playwright test --reporter=list 2>&1
```

For a specific file:

```bash
npx playwright test <path-to-spec> --reporter=list 2>&1
```

If Playwright is not installed, install it first:

```bash
npm install --save-dev @playwright/test && npx playwright install chromium
```

### Generate a new test

Write a Playwright test script to `/tmp/e2e-<name>.spec.ts`. Use this structure:

```typescript
import { test, expect } from "@playwright/test";

test("<description of what is verified>", async ({ page }) => {
  await page.goto("http://localhost:<port>");

  // Navigate and interact using semantic locators
  await page.getByRole("button", { name: "Submit" }).click();
  await page.waitForURL("**/success");

  // Assert outcomes
  await expect(page.getByRole("heading", { name: "Done" })).toBeVisible();
});
```

Locator rules — always prefer in this order:

1. `getByRole` — accessible role + name
2. `getByLabel` — form label
3. `getByText` — visible text
4. `getByTestId` — `data-testid` attribute
5. CSS selector last resort only

Never use fixed `waitForTimeout` delays. Use `waitForSelector`, `waitForURL`, or `waitForLoadState` instead.

For HTMX applications, verify partial page updates explicitly:

- Check that the swapped target element changed
- Assert `hx-swap` results by checking the updated DOM region, not the full page

### Record a session

Write a recording script to `/tmp/e2e-record.js`:

```javascript
const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();
  await page.goto("http://localhost:<port>");
  // Browser stays open — user interacts manually
  // Close the browser window to end the session
  await page.waitForEvent("close", { timeout: 300000 });
  await browser.close();
})();
```

Run it:

```bash
cd ~/.claude/skills/playwright-skill && node /tmp/e2e-record.js
```

### Verify a feature

Write a focused verification script to `/tmp/e2e-verify-<feature>.spec.ts` that:

1. Navigates to the relevant page
2. Executes the user flow step by step
3. Asserts the expected outcome at each step
4. Captures a screenshot on failure

## Step 4: Run the generated test

```bash
cd ~/.claude/skills/playwright-skill && node run.js /tmp/e2e-<name>.spec.ts 2>&1
```

Or if running from the project root with a config:

```bash
npx playwright test /tmp/e2e-<name>.spec.ts --reporter=list 2>&1
```

Read the full output. Note which assertions failed and on which line.

## Step 5: Fix failures and re-run

For each failure, diagnose before editing:

| Failure type      | Likely cause                           | Fix                                             |
| ----------------- | -------------------------------------- | ----------------------------------------------- |
| Locator not found | Selector doesn't match DOM             | Use accessible role/label instead of CSS class  |
| Timeout           | Element not visible or action too slow | Add `waitForSelector` or `waitForLoadState`     |
| Wrong assertion   | Page state differs from expectation    | Read the actual page state and update assertion |
| Navigation error  | Wrong URL or server not running        | Verify base URL and that dev server is up       |

Fix the script, re-run, and repeat until all tests pass. Do not declare done with failing tests.

## Step 6: Report results

```
E2E TESTING
===========
Action: <run|generate|record|verify>
Tests written: <count>
Pass: <count>
Fail: <count>

Results:
- <test name>: PASS
- <test name>: FAIL — <brief reason>

Coverage added:
- <user flow now tested>

Next steps:
- <additional flows worth testing>
```
