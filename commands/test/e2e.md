---
allowed-tools:
  - Task
  - Bash
  - Read
  - Grep
  - Glob
  - LS
  - AskUserQuestion
  - mcp__playwright__*
description: E2E testing with Playwright MCP - browser automation, test generation, and execution
argument-hint: [run|record|generate]
---

# E2E Testing with Playwright

Execute E2E testing workflows using Playwright MCP.

## Parse Arguments

**$ARGUMENTS:**

- `run` → Run existing E2E tests
- `record` → Record browser session for test generation
- `generate` → Generate test from URL or page description
- (empty) → Ask what to do

## Step 1: Determine Action

If no argument provided, use AskUserQuestion:

| Header | Question                      | Options                                                                                                                                        |
| ------ | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Action | What E2E testing task to run? | 1. **Run tests** - Execute existing Playwright tests 2. **Record** - Record browser session 3. **Generate** - Create test from URL/description |

## Step 2: Execute Action

### Run Tests

```bash
npx playwright test
```

For specific test:

```bash
npx playwright test login.spec.ts
```

For headed mode:

```bash
npx playwright test --headed
```

### Record Session

1. Use `browser_navigate` to go to target URL
2. Use `browser_snapshot` to inspect page structure
3. Interact with `browser_click`, `browser_type`, `browser_fill_form`
4. Generate test file with Page Object pattern

### Generate Test

Spawn playwright-tester agent:

```
Task with playwright-tester agent:
"Generate E2E test for:
URL: {target URL}
Flow: {user flow description}

Requirements:
- Use Page Object pattern
- Use semantic locators (getByRole, getByLabel, getByText)
- Include assertions for expected outcomes
- No hardcoded waits"
```

## Step 3: Verify

```bash
npx playwright test --headed
```

## Output

```
E2E TESTING
===========
Action: {run|record|generate}
Result: {outcome}
Tests: {pass/fail count}
```
