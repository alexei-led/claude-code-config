---
allowed-tools:
- Task
- TaskOutput
- TaskCreate
- TaskUpdate
- TaskList
- Bash(npx playwright *)
- Bash(bunx playwright *)
- Bash(npm *)
- Bash(bun *)
- Bash(bunx *)
- Bash(node *)
- Bash(curl *)
- Bash(lsof *)
- Bash(make *)
- Bash(go run *)
- Read
- Grep
- Glob
- LS
- AskUserQuestion
argument-hint: '[run|record|generate|verify <feature>]'
context: fork
description: Sequential E2E workflow. Use when running existing Playwright tests,
  generating browser checks, recording a visible session, or verifying a user flow
  end-to-end. Not for unit tests, API-only tests, or logic tests where curl or JSDOM
  suffices — use improving-tests or fixing-code instead.
name: testing-e2e
user-invocable: true
---

# E2E Testing with Playwright

Execute E2E testing workflows using Playwright scripts (via playwright-skill). Do not delete, reset, or mutate non-test data without explicit user confirmation. If the app cannot be started or fixtures are unavailable, report BLOCKED instead of inventing passing results.

> **Runner**: Examples below use `npx playwright`. If the project uses Bun, substitute `bunx playwright` everywhere. Both runners work; pick the one matching the project's lockfile (`package-lock.json`/`pnpm-lock.yaml` → `npx`; `bun.lock`/`bun.lockb` → `bunx`).

**Use TaskCreate / TaskUpdate** to track these 5 phases:

1. Determine action (parse args or ask)
2. Prepare app, dev server, and deterministic test data
3. Execute action (run/record/generate/verify)
4. Verify results and collect artifacts
5. Present output

## Phase 1: Parse Arguments

### $ARGUMENTS

- `run` → Run existing E2E tests
- `record` → Record browser session for test generation
- `generate` → Generate test from URL or page description
- `verify <feature>` → Verify specific feature works in browser
- (empty) → Ask what to do

If no argument provided, use AskUserQuestion. Ask one question at a time:

- **Action** — What E2E testing task to run? Options: 1. **Run tests** - Execute existing Playwright tests 2. **Record** - Record browser session 3. **Generate** - Create test from URL/description 4. **Verify** - Check feature

## Phase 2: Prepare App and Data

Before any browser test run or test-generation plan, explicitly include dev-server detection/startup and deterministic test data setup. Do not jump straight to browser steps.

1. Detect the app start command from Playwright config, package scripts, Makefile, README, or existing dev server docs.
2. If tests need a running app, check whether the dev server is already reachable at the configured `baseURL`; start it if missing, or report the blocker if no start command is known.
3. Use deterministic fixtures: seeded users, fixed dates, stable IDs, known database state, and mocked external services where needed.
4. Avoid tests depending on production data, local user state, random order, wall-clock time, or previous test runs.

## Phase 3: Execute Action

### Run Tests

```bash
npx playwright test
# or, with Bun:
bunx playwright test
```

For specific test:

```bash
npx playwright test login.spec.ts
```

For headed mode (visible browser):

```bash
npx playwright test --headed
```

### Record Session

Write a Playwright script to `/tmp/playwright-record-*.js` that:

1. Launches browser with `headless: false` and `slowMo: 100`
2. Navigates to target URL
3. Captures interactions and generates test with Page Object pattern
4. Execute via: `cd ~/.claude/skills/playwright-skill && node run.js /tmp/playwright-record-*.js`

### Generate Test

Translate manual flows into Playwright actions and assertions, but first define deterministic fixtures: seeded users/items/coupons, fixed dates, stable IDs, reset database state, and mocked external services where needed.

### Spawn playwright-tester agent

```
Task(
  subagent_type="playwright-tester",
  description="Generate E2E test",
  prompt="Generate E2E test for:
  URL: {target URL}
  Flow: {user flow description}

  Requirements:
  - Use Page Object pattern
  - Use semantic locators (getByRole, getByLabel, getByText)
  - Include assertions for expected outcomes
  - No hardcoded waits (use waitFor patterns)
  - Include accessibility checks where appropriate"
)
```

### Verify Feature

### Spawn playwright-tester agent for feature verification

```
Task(
  subagent_type="playwright-tester",
  description="Verify feature",
  prompt="Verify this feature works correctly in the browser:
  Feature: {feature description}

  Steps:
  1. Navigate to appropriate page
  2. Execute user flow
  3. Assert expected outcomes
  4. Report PASS/FAIL with evidence (screenshots if needed)"
)
```

## Phase 4: Verify Results

Run the test suite and validate:

```bash
npx playwright test --headed
```

**Pass criteria:** all tests green, no flaky failures on re-run, deterministic fixtures reset cleanly, and traces/screenshots/videos are saved or linked when failures occur.

If tests fail:

1. Read the Playwright error output — identify failing locator or assertion
2. Fix the test or application code
3. Re-run: `npx playwright test <failed-spec> --headed`
4. Repeat until all tests pass
5. Run full suite once more to confirm no regressions: `npx playwright test`

## Phase 5: Output

The final report must include PASS/FAIL/BLOCKED, dev server status, fixture/reset summary, test results, and artifact paths for traces/screenshots/videos/reports when relevant. If tests were not run, report BLOCKED or explain exactly why; do not imply success.

```
E2E TESTING
===========
Action: {run|record|generate|verify}
Result: PASS | FAIL | BLOCKED
Tests: {pass/fail count}
Dev server: {reused|started|not needed|blocked: reason}
Fixtures: {deterministic data/reset summary}
Artifacts: {trace/screenshots/videos/report paths or "none"}

Details:
- [test results or generation summary]
```

## Execution

Write Playwright scripts to `/tmp/` and run via the playwright-skill executor:

```bash
cd ~/.claude/skills/playwright-skill && node run.js /tmp/playwright-test-*.js
```

The executor handles module resolution, auto-installs Chromium if needed, and provides helper utilities. See `playwright-skill/SKILL.md` for full patterns.

## Supported Stacks

- **TypeScript**: Playwright Test with Page Objects
- **Go/HTMX**: Test HTMX interactions, form submissions, partial updates

## HTMX Testing Tips

- Use `browser_snapshot` to verify DOM updates after HTMX swaps
- Test `hx-trigger`, `hx-swap`, `hx-target` behaviors
- Verify `HX-*` response headers in network requests
- Assert partial page updates without full reload

## Error Scenarios & Handling

### Element Not Found

```typescript
// BAD: Immediate failure
await page.click("#submit-btn");

// GOOD: Wait with timeout + fallback
const btn = page.locator("#submit-btn");
if ((await btn.count()) === 0) {
  // Try alternative selector
  await page.click('button[type="submit"]');
} else {
  await btn.click();
}
```

### Recovery strategies

1. Use `browser_snapshot` to inspect current DOM state
2. Try alternative locators (text, role, data-testid)
3. Check if element is in iframe/shadow DOM
4. Verify page loaded correctly (check URL, title)

### Timeout Errors

- **Navigation timeout** — Slow page load; increase timeout, check network
- **Action timeout** — Element not interactable; wait for visibility/enabled state
- **Expect timeout** — Assertion failed; verify DOM state with snapshot

```typescript
// Configure timeouts
test.setTimeout(60000); // Test timeout
page.setDefaultTimeout(30000); // Action timeout

// Or per-action
await page.click("#btn", { timeout: 10000 });
```

### Network Issues

```typescript
// Wait for network idle
await page.waitForLoadState("networkidle");

// Mock failing endpoints
await page.route("**/api/**", (route) => {
  route.fulfill({ status: 500, body: "Server Error" });
});
```

### Flaky Test Patterns

### Avoid

- Fixed `page.waitForTimeout(1000)` delays
- Brittle selectors like `.btn-23`
- Tests depending on animation timing

### Prefer

- `waitForSelector`, `waitForLoadState`
- Role/text-based selectors: `getByRole('button', { name: 'Submit' })`
- Retry patterns for known flaky operations

### Debugging Failed Tests

1. **Get snapshot**: `browser_snapshot` shows accessibility tree
2. **Screenshot**: Capture current visual state
3. **Console logs**: Check browser console for JS errors
4. **Network tab**: Verify API calls succeeded
5. **Trace**: Enable Playwright trace for post-mortem

```bash
# Run with trace
npx playwright test --trace on

# View trace
npx playwright show-trace trace.zip
```

### Execute E2E testing workflow now
