---
name: committing-code
description: Smart git commits with logical grouping. Use when user says "commit", "commit changes", "save changes", "create commit", "bundle commits", "git commit", or wants to commit their work.
user-invocable: true
context: fork
allowed-tools:
  - Bash(git status *)
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(git show *)
  - Bash(git branch *)
---

# Smart Commit

Group changed files logically into focused, atomic commits.

Scope: only inspect changes, group them, and create normal commits. Do not rewrite history, amend existing commits, force-push, or stage secrets. Include relevant `git status`, `git diff`, and `git log` output in the proposal.

## Step 1: Gather State

Run in parallel before any commit:

```bash
git status --short
git diff --stat HEAD
git diff HEAD
git log --oneline -8
```

**If no changes:** Say "Nothing to commit" → stop.

## Step 2: Analyze & Present

Group files by: feature (impl+tests), fix (bug+test), refactor, docs, config

Match commit style from recent history.

**Present proposed commits:**

```
Proposed commits:

1. feat: add user validation
   - src/validate.ts
   - src/validate_test.ts

2. docs: update README
   - README.md
```

## Step 3: Execute

Never stage files matching `.env`, `*.pem`, `*credentials*`, or `*secret*`. Flag to user if detected in changes.

For each group, run git add + commit.

User will be prompted to approve each write operation (git add/commit not pre-allowed).

## Step 4: Summary

Run final checks and show the result:

```bash
git status --short
git log --oneline -n <number-of-created-commits>
```

Summarize commits created and any remaining uncommitted files.

---
