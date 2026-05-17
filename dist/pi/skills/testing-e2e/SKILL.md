---
description: Sequential E2E workflow. Use when running existing Playwright tests,
  generating browser checks, recording a visible session, or verifying a user flow
  end-to-end. Not for unit tests, API-only tests, or logic tests where curl or JSDOM
  suffices — use improving-tests or fixing-code instead.
name: testing-e2e
---

<!-- Pi platform guidance -->
<!-- Use Pi tool names exactly: read, bash, edit, write, ask_user_question, structured_output, todo, Agent, get_subagent_result, steer_subagent, web_search, web_answer, web_research. -->
<!-- Use Agent, get_subagent_result, and steer_subagent for delegated work. -->
<!-- Use ctx7 or npx ctx7@latest through bash when Context7 documentation lookup is required. -->

# E2E Testing with Playwright

Run browser tests against real user flows. Keep scripts temporary unless the
user asks to add permanent tests.

## Workflow

1. Ask what to run if the user did not specify: existing tests, generate a new
   check, record a session, or verify a feature.
2. Read existing test context:
   - `playwright.config.*`
   - `package.json` scripts
   - `**/*.spec.ts`, `**/*.test.ts`, `**/e2e/**`
   - fixture, seed, and database reset docs
3. Detect or start the dev server from project docs/scripts.
4. Use deterministic fixtures. No production data, random order, wall-clock
   dependence, or leftover state.
5. Generate temporary scripts under `/tmp` when needed.
6. Prefer semantic locators: role, label, text, test id, CSS last.
7. Run the test, read the full output, fix failures, and rerun.

## Playwright Helper Skill

If the bundled `playwright-skill` helper is installed alongside this skill,
find its directory from the loaded skill path and run helper scripts from
there:

```bash
cd <playwright-skill-dir> && node scripts/run.js /tmp/e2e-check.js
```

If the helper is unavailable, use project-local Playwright commands instead:

```bash
npx playwright test --reporter=list
npx playwright test /tmp/e2e-check.spec.ts --reporter=list
```

## Generated Test Rules

- Write temporary tests to `/tmp/e2e-<name>.spec.ts` or `/tmp/e2e-<name>.js`.
- Never use fixed `waitForTimeout` delays.
- Use `waitForSelector`, `waitForURL`, or assertions on visible UI state.
- Capture screenshots, traces, or HTML reports when failures need evidence.
- Do not declare success while tests fail.

## Failure handling

- No dev server running: read project docs and `package.json` scripts for a start command; ask the user if none found.
- Test still failing after two fix attempts: capture a screenshot/trace, report the exact failure line, and stop — do not loop blindly.
- No `playwright.config.*` found: generate a minimal temporary config under `/tmp`; do not write into the project without asking.

## Output Contract

```markdown
## E2E Result

### Target

<app/flow tested>

### Commands

- `<command>`

### Result

pass | fail | blocked

### Evidence

- screenshot/trace/output path or key failure line

### Next Fix

- <if failing>
```
