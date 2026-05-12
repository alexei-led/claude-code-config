---
allowed-tools:
- Bash(git status *)
- Bash(git diff *)
- Bash(git log *)
- Bash(git show *)
- Bash(git branch *)
context: fork
description: Smart git commits with logical grouping. Use when user says "commit",
  "commit changes", "save changes", "create commit", "bundle commits", "git commit",
  or wants to commit their work.
name: committing-code
user-invocable: true
---

# Smart Commit

Group changed files logically into focused, atomic commits.

Scope: only inspect changes, group them, and create normal commits. Do not rewrite history, amend existing commits, force-push, or stage secrets. Include relevant `git status`, `git diff`, and `git log` output in the proposal.

Not for squashing, rebasing, or cherry-picking — those rewrite history.

## Step 1: Gather State

Run before any commit (in parallel if supported):

```bash
git status --short
git diff --stat HEAD
git diff HEAD
git log --oneline -8
```

**If no changes:** Say "Nothing to commit" → stop.
**If not a git repository:** Report "Not a git repository" → stop.
**If detached HEAD or interrupted rebase/merge:** Report the git state verbatim → stop.

## Step 2: Analyze & Present

Group files by: feature (impl+tests), fix (bug+test), refactor, docs, config. Base grouping on diff output only — do not infer purpose from filename alone.

Match commit style from recent history.

### Present proposed commits

```
Proposed commits:

1. feat: add user validation
   - src/validate.ts
   - src/validate_test.ts

2. docs: update README
   - README.md
```

**If user rejects the grouping:** Ask for revised grouping; do not proceed until approved.

## Step 3: Execute

Never stage files matching `.env`, `*.pem`, `*.key`, `*.p12`, `*credentials*`, `*secret*`, `*password*`, or `*token*`. Flag to user if detected in changes. Safe source/test files may still be grouped and committed separately after approval.

Pause for user approval before each `git add` and `git commit`.

**If pre-commit hook rejects:** Report the hook error verbatim; do not retry with `--no-verify`.

## Step 4: Summary

Run final checks and show the result:

```bash
git status --short
git log --oneline -n <number-of-created-commits>
```

Summarize commits created and any remaining uncommitted files.
