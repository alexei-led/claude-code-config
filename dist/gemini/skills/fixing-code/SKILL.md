---
description: Fix code problems with disciplined diagnosis — run checks, build a repro
  for bugs, rank falsifiable hypotheses, fix one issue at a time, and verify until
  clean. Use when fixing, debugging, diagnosing, or resolving lint/test/build failures.
name: fixing-code
---

# Fix and Diagnose Code

Fix until clean. For hard bugs, diagnose before editing. No guessing. Confirm before any destructive command; never use `git reset --hard`, `git clean`, or force push as a fix.

## Role-gated action

Detect your capability from your tools, not from prose:

- Write-capable role (engineer): run all steps — diagnose, apply the fix, run verification.
- Read-only role (reviewer): run Steps 1–3 to diagnose (a reviewer has no Bash — work from the files in scope and caller-supplied error/diff context, skipping any command), then stop before Step 4. Instead of editing, emit the fix in the Proposed Changes contract below. Apply nothing; run nothing.

## Language detection

Detect the language from the file extensions in scope and use the matching toolchain in Step 1 (build/test/lint commands shown per language). This skill has no per-language reference files — operate from the generic procedure; the language only selects which verification commands to run.

## Step 1: Build a feedback loop

For lint/build/test failures, run validation first:

```bash
make lint 2>&1 | head -150
make test 2>&1 | head -150
```

No Makefile? Detect language:

```bash
# Go
golangci-lint run ./... 2>&1 | head -150
go test -race ./... 2>&1 | head -150

# Python
ruff check . 2>&1 | head -150
pytest --tb=short 2>&1 | head -150

# TypeScript
bun lint 2>&1 | head -150
bun test 2>&1 | head -150
```

If all checks pass, report `All checks pass` and stop.

For reported bugs, first build a fast pass/fail signal that reproduces the user's symptom:

1. Failing test at the right seam.
2. CLI or HTTP script with fixture input.
3. Browser script for UI bugs.
4. Replay captured payload/log/trace.
5. Throwaway harness around the smallest real code path.
6. Property/fuzz loop for intermittent wrong output.
7. `git bisect run` harness for regressions.

Do not proceed to fixes until the loop reproduces the symptom. If no loop is possible, stop and ask for access, logs, captured payloads, or permission to add temporary instrumentation.

## Step 2: Analyze root causes

Catalog every distinct issue:

- file:line
- exact error/test failure
- tool that reported it
- priority: critical / important / minor

For hard bugs, write **3–5 ranked falsifiable hypotheses** before testing one:

```text
If <cause> is true, then <probe/change> will make <specific symptom> disappear or change.
```

Read files and tool output. Do not guess at code content.

## Step 3: Instrument carefully

Probe one hypothesis at a time.

- Prefer debugger/REPL inspection when available.
- Otherwise add targeted logs at boundaries that distinguish hypotheses.
- Tag temporary logs with a unique prefix like `[DEBUG-a4f2]`.
- For performance regressions: measure baseline first, then bisect/profile.

## Step 4: Fix one issue at a time

For each issue, in priority order:

1. Read the exact code path.
2. Apply the smallest root-cause fix.
3. Add or update a regression test at the correct seam when possible.
4. Run the narrow check.
5. Run broader lint/test before moving on.

If the only available test seam is too shallow, report that. Do not write fake-confidence tests against helpers while the real bug path stays uncovered.

If a fix causes new failures, revert or adjust it before touching the next issue.

## Step 5: Final verification and cleanup

Required before done:

- Original repro no longer reproduces.
- Regression test passes, or missing test seam is explicitly reported.
- Full validation passes.
- All `[DEBUG-...]` probes are removed.
- Throwaway harnesses are deleted or moved into test fixtures.

Run:

```bash
make lint && make test
```

Or language equivalents. Loop back to root-cause analysis if anything still fails.

## Output format

Engineer (applied the fix):

```text
FIX COMPLETE
============
Mode: standard | diagnose
Issues found: X
Fixed: Y
Remaining: Z
Status: CLEAN | NEEDS ATTENTION

Root cause:
- <short verified cause>

Changes:
- file:line — fix

Verification:
- <command> — pass/fail
```

If unresolved, state the blocker and exact artifact/access needed. Do not pretend clean.

Reviewer (diagnosed only — emit the fix as a proposal, apply nothing):

```text
## Proposed Changes

Root cause:
- <short verified cause>

### Change 1: <brief description>

File: `path/to/file`
Action: CREATE | MODIFY | DELETE

Code:
<complete code block, in the file's language>

Rationale: <why this change>
```

For MODIFY, include enough surrounding context (signatures, nearby lines) to locate the change precisely. For large fixes, show one representative change and describe the pattern rather than every file.
