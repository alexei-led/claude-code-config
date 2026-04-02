---
name: fixing-code
description: Sequential fix workflow — identify all failing checks (lint, tests, type errors), root-cause each issue, apply fixes one at a time, and verify each fix passes. Keep going until all checks are green.
---

# Fix All Issues

Identify every failing check, root-cause it, fix it, and verify the fix. Repeat until the build, tests, and linter are all clean. Do not declare done until every check passes.

## Step 1: Run all checks

Run the full validation suite and capture output. If a Makefile exists, prefer `make`:

```bash
make lint 2>&1 | head -150
make test 2>&1 | head -150
```

No Makefile? Detect language and run directly:

**Go:**

```bash
golangci-lint run ./... 2>&1 | head -150
go test -race ./... 2>&1 | head -150
```

**Python:**

```bash
ruff check . 2>&1 | head -150
pytest --tb=short 2>&1 | head -150
```

**TypeScript:**

```bash
bun lint 2>&1 | head -150
bun test 2>&1 | head -150
```

**Web:**

```bash
bunx eslint "**/*.js" 2>&1 | head -100
bunx stylelint "**/*.css" 2>&1 | head -100
```

If all checks pass, report "All checks pass" and stop.

## Step 2: Catalog issues

Read the full output from Step 1. List every distinct issue:

- File and line number
- Error message or test failure description
- Which tool reported it (lint / test / type-check)

Group by priority:

1. **Critical** — compilation errors, panics, test failures
2. **Important** — lint errors, type errors
3. **Minor** — style warnings

Reflect on the full list before proceeding. Make sure you understand each issue before attempting a fix.

## Step 3: Root-cause each issue

For each issue in priority order, read the relevant file and surrounding context. Identify the root cause — not just the symptom. Ask: what condition allows this error to exist? A missing nil check, a wrong type, an untested code path?

For recurring or mysterious issues, apply 5-Why thinking:

1. Why did it fail? (immediate symptom)
2. Why was that possible? (missing guard or contract)
3. Why was the guard missing? (design gap)
4. Why was there a design gap? (systemic cause)
5. Why was that systemic cause present? (root cause)

Use tool calls to read files — do not guess at code content.

## Step 4: Fix issues one at a time

Work through the issue list in priority order. For each issue:

1. Read the file at the relevant line.
2. Apply the minimal fix that addresses the root cause.
3. Immediately verify the fix did not introduce new failures:
   ```bash
   make lint 2>&1 | head -50
   make test 2>&1 | head -50
   ```
   Or run the language-specific commands from Step 1.
4. If the fix causes new failures, revert it and try an alternative approach before moving on.

Fix one issue at a time. Do not batch edits across unrelated files in a single step.

## Step 5: Final verification

After all fixes are applied, run the full suite once more:

```bash
make lint && make test
```

Or language equivalents. All checks must pass with zero errors.

If issues remain, return to Step 3 with the new output. Keep going until clean.

## Output format

```
FIX COMPLETE
============
Issues found: X
Issues fixed: Y
Remaining: Z (list if non-zero)
Status: CLEAN | NEEDS ATTENTION

Changes:
- file:line — description of fix
- file:line — description of fix
```

Report the final status directly. If any issues remain unresolved, explain why (e.g., requires external change, test environment missing) and what the user needs to do.
