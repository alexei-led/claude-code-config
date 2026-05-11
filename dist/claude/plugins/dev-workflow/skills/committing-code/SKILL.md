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

Any commit plan must explicitly say the first inspection commands are `git status --short`, `git diff --stat HEAD`, `git diff HEAD`, and `git log --oneline -8`. Any commit summary must include a final `git status --short` plus recent `git log --oneline -n <created>` output.

## Step 1: Gather State

Run before any commit (in parallel if supported):

```bash
git status --short
git diff --stat HEAD
git diff HEAD
git log --oneline -8
```

**If no changes:** Say "Nothing to commit" → stop.

## Step 2: Analyze & Present

Group files by: feature (impl+tests), fix (bug+test), refactor, docs, config.

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

## Step 3: Execute

Never stage files matching `.env`, `*.pem`, `*credentials*`, or `*secret*`. Flag to user if detected in changes. Safe source/test files may still be grouped and committed separately after approval.

Pause for user approval before each `git add` and `git commit`.

## Step 4: Summary

Run final checks and show the result:

```bash
git status --short
git log --oneline -n <number-of-created-commits>
```

Summarize commits created and any remaining uncommitted files.
