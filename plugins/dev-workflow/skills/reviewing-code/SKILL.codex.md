---
name: reviewing-code
description: Sequential code review for security, quality, and architecture. Detects languages in the diff, runs linters and static checks, reviews for OWASP security issues, quality patterns, and test coverage gaps, then reports findings grouped by severity.
---

# Code Review

Review the current diff or specified scope for security, quality, and test coverage issues. Work sequentially through each language detected. Keep going until every check has been run and all findings are reported.

## Step 1: Determine scope

Read the diff to understand what changed. Use tools — do not guess file names.

```bash
git diff --name-only HEAD
git diff HEAD
```

If the user supplied explicit file paths or a branch name, use those instead.

## Step 2: Detect languages

Categorize changed files by extension:

- `.go` — Go
- `.py` — Python
- `.ts`, `.tsx` — TypeScript
- `.html`, `.css`, `.js` — Web

Record the list. You will work through each language in subsequent steps.

## Step 3: Run linters and static checks

For each detected language, run the appropriate tools and capture output. Use real tool calls — read actual output before drawing conclusions.

**Go:**

```bash
golangci-lint run ./... 2>&1 | head -100
go vet ./...
go test -race ./... 2>&1 | head -100
```

**Python:**

```bash
ruff check . 2>&1 | head -100
mypy . 2>&1 | head -100
pytest --tb=short 2>&1 | head -100
```

**TypeScript:**

```bash
bun lint 2>&1 | head -100
bun tsc --noEmit 2>&1 | head -100
bun test 2>&1 | head -100
```

**Web (HTML/CSS/JS):**

```bash
bunx html-validate "**/*.html" 2>&1 | head -50
bunx stylelint "**/*.css" 2>&1 | head -50
bunx eslint "**/*.js" 2>&1 | head -50
```

## Step 4: Review changed files for security (OWASP)

Read each changed file. Check for the following per language:

**All languages:** hardcoded secrets, credentials, or tokens; SQL/command injection risks; unsafe deserialization; insecure direct object references.

**Go:** unchecked errors, goroutine leaks, use of `unsafe`, missing context propagation.

**Python:** `eval`/`exec` on user input, pickle deserialization, missing input validation.

**TypeScript:** XSS via `innerHTML`, prototype pollution, missing auth checks on API routes.

**Web:** inline event handlers with user data, missing CSP headers, missing ARIA roles.

## Step 5: Review for quality patterns

For each changed file, check:

- Functions longer than 40 lines — split them
- Missing error handling or silent error swallowing
- Duplicated logic that should be extracted
- Unclear variable names or missing doc comments on exported symbols
- Dead code or commented-out blocks

Reflect on what you have read before noting findings. Prioritize substance over volume.

## Step 6: Identify test coverage gaps

Scan for corresponding test files. For each changed function or method, check whether a test exists that covers:

- The happy path
- At least one error or edge case
- Boundary values for numeric inputs

Note functions that have no test at all as IMPORTANT findings.

## Step 7: Report findings

Group all findings by severity. Use the exact format below — one line per finding, no preamble.

```
## Code Review

**Scope:** <description of what was reviewed>
**Languages:** <list>

---

### CRITICAL (must fix before merge)
- `file:line` — <issue>. Fix: <action>.

### IMPORTANT (should fix)
- `file:line` — <issue>. Fix: <action>.

### SUGGESTIONS
- `file:line` — <issue>. Fix: <action>.

### Test gaps
- `func/method` in `file` — no test for <scenario>.

---

**Summary:** X critical, Y important, Z suggestions, W test gaps.
```

If no issues are found in a severity category, omit that section.

## Output format

Deliver the report from Step 7 directly in the chat. No preamble, no "I noticed that…", no hedging. State what IS wrong. Use file:line references throughout.
