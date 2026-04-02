---
allowed-tools:
  - Bash(git status *)
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(git show *)
  - Bash(git branch *)
description:
  Smart git commits with logical grouping. Use when user says "commit",
  "commit changes", "save changes", "create commit", "bundle commits", "git commit",
  or wants to commit their work.
name: committing-code
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Smart Commit

Group changed files logically into focused, atomic commits.

## Step 1: Gather State

Run in parallel:

```bash
git status --porcelain
git diff --name-status HEAD
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

Show `git status` and list commits created.

---
