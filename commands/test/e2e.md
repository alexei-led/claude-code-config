---
model: sonnet
context: fork
allowed-tools:
  - Task
  - TaskOutput
  - TodoWrite
  - Bash(npx playwright *)
  - Bash(npm *)
  - Bash(bun *)
  - Read
  - Grep
  - Glob
  - LS
  - AskUserQuestion
  - mcp__playwright__*
description: E2E testing with Playwright MCP - browser automation, test generation, and execution
argument-hint: [run|record|generate|verify <feature>]
---

# E2E Testing with Playwright

Execute E2E testing workflows using Playwright MCP.

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

---

### Determine Action

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

Use Playwright MCP tools for browser interaction:

1. `browser_navigate` - Go to target URL
2. `browser_snapshot` - Inspect page structure
3. `browser_click`, `browser_type`, `browser_fill_form` - Interact
4. Generate test file with Page Object pattern

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

```bash
npx playwright test --headed
```

If tests fail, review output and fix issues.

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

**Execute E2E testing workflow now.**
