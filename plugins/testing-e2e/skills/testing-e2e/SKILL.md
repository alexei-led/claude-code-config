---
name: testing-e2e
description: E2E testing with Playwright — the primary user-facing skill for writing, running, and generating browser tests. Use when user asks to "write e2e tests", "test this page", "run playwright tests", "generate browser tests", "check accessibility", or "visual regression". Supports TypeScript tests and Go/HTMX web applications.
user-invocable: true
context: fork
argument-hint: "[run|record|generate|verify <feature>]"
allowed-tools: "Task, TaskOutput, TodoWrite, Bash(npx playwright *), Bash(npm *), Bash(bun *), Bash(node *), Read, Grep, Glob, LS, AskUserQuestion"
---

# E2E Testing with Playwright

Execute E2E testing workflows using Playwright scripts (via playwright-skill).

**Use TodoWrite** to track these 4 phases:

1. Determine action (parse args or ask)
2. Execute action (run/record/generate/verify)
3. Verify results
4. Present output

---

## Phase 1: Parse Arguments

**$ARGUMENTS:**

- `run` → Run existing E2E tests
- `record` → Record browser session for test generation
- `generate` → Generate test from URL or page description
- `verify <feature>` → Verify specific feature works in browser
- (empty) → Ask what to do

If no argument provided, use AskUserQuestion:

| Header | Question                      | Options                                                                                                                                                                      |
| ------ | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Action | What E2E testing task to run? | 1. **Run tests** - Execute existing Playwright tests 2. **Record** - Record browser session 3. **Generate** - Create test from URL/description 4. **Verify** - Check feature |

---

## Phase 2: Execute Action

### Run Tests

```bash
npx playwright test
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

**Spawn playwright-tester agent:**

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

**Spawn playwright-tester agent for feature verification:**

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

---

## Phase 3: Verify Results

Run the test suite and validate:

```bash
npx playwright test --headed
```

**Pass criteria:** All tests green, no flaky failures on re-run.

**If tests fail:**

1. Read the Playwright error output — identify failing locator or assertion
2. Fix the test or application code
3. Re-run: `npx playwright test <failed-spec> --headed`
4. Repeat until all tests pass
5. Run full suite once more to confirm no regressions: `npx playwright test`

---

## Phase 4: Output

```
E2E TESTING
===========
Action: {run|record|generate|verify}
Result: {outcome}
Tests: {pass/fail count}

Details:
- [test results or generation summary]
```

---

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

## Troubleshooting

| Problem            | Diagnosis                        | Fix                                                 |
| ------------------ | -------------------------------- | --------------------------------------------------- |
| Element not found  | Selector changed or not rendered | Use `getByRole`/`getByText` instead of CSS selectors |
| Timeout            | Slow load or not interactable    | `waitForLoadState("networkidle")`, increase timeout  |
| Flaky failures     | Timing or animation dependency   | Replace `waitForTimeout` with `waitForSelector`      |
| Network errors     | API dependency                   | Mock with `page.route()` for isolation               |

**Debug:** Run `npx playwright test --trace on`, then `npx playwright show-trace trace.zip`.

---

**Execute E2E testing workflow now.**
