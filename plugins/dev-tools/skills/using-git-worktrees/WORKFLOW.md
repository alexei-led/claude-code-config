# Git Worktrees Workflow

## Directory Selection Process

### 1. Detect Project Name and Root

```bash
repo_root=$(git rev-parse --show-toplevel)
project=$(basename "$repo_root")
parent=$(dirname "$repo_root")
```

### 2. Determine Worktree Path

**Priority order:**

1. Check CLAUDE.md for explicit preference
2. Use sibling directory pattern (default): `../<project>-<branch-slug>`

```bash
# Slugify branch name: feature/auth → feature-auth
slug=$(echo "$BRANCH_NAME" | tr '/' '-')
path="$parent/$project-$slug"
```

### 3. Check for Conflicts

```bash
# Verify path doesn't already exist
[ -d "$path" ] && echo "Directory already exists: $path" && exit 1

# Verify branch isn't already checked out
git worktree list | grep -q "\[$BRANCH_NAME\]" && echo "Branch already checked out" && exit 1
```

## Creation Steps

### 1. Create Worktree

```bash
# New branch from base
git worktree add "$path" -b "$BRANCH_NAME" "$BASE_BRANCH"

# Existing branch
git worktree add "$path" "$BRANCH_NAME"
```

### 2. Run Project Setup

Auto-detect and run appropriate setup:

```bash
cd "$path"

# Node.js
[ -f package.json ] && npm install

# Go
[ -f go.mod ] && go mod download

# Python
[ -f pyproject.toml ] && uv sync
[ -f requirements.txt ] && pip install -r requirements.txt

# Rust
[ -f Cargo.toml ] && cargo build
```

### 3. Verify Clean Baseline

Run tests to ensure worktree starts clean:

```bash
make test  # or npm test, cargo test, pytest, go test ./...
```

**If tests fail:** Report failures, ask whether to proceed.
**If tests pass:** Report ready.

### 4. Report Location

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>

To work in this worktree:
  cd <full-path>
```

## Cleanup Workflow

### After Merging a Branch

```bash
# Remove the worktree
git worktree remove ../myproject-feature-auth

# Delete the branch (if merged)
git branch -d feature/auth
```

### Periodic Maintenance

```bash
# List all worktrees — check for stale ones
git worktree list

# Prune entries for manually deleted directories
git worktree prune

# Check for locked or prunable worktrees
git worktree list --verbose
```

## Quick Reference

| Situation                  | Action                                  |
| -------------------------- | --------------------------------------- |
| Creating worktree          | Sibling: `../<project>-<branch-slug>`   |
| CLAUDE.md has preference   | Use specified location                  |
| Path already exists        | Report conflict, ask user               |
| Branch already checked out | Report, suggest existing worktree       |
| Tests fail during baseline | Report failures + ask                   |
| Done with feature          | `git worktree remove` + `git branch -d` |
| Stale worktrees            | `git worktree prune`                    |

## Common Commands

```bash
# List all worktrees
git worktree list

# Remove worktree (after merging branch)
git worktree remove ../myproject-feature-name

# Prune stale worktree entries
git worktree prune

# Move worktree to new location
git worktree move ../old-name ../new-name

# Lock worktree (prevent pruning, e.g. on removable drive)
git worktree lock ../myproject-feature-name
```

## Common Mistakes

**Nesting worktrees inside the repo**

- Requires .gitignore management, pollutes git status
- Fix: Always use sibling directories

**Non-descriptive directory names**

- `../temp`, `../wt2` — requires inspection to understand purpose
- Fix: Use `<project>-<branch-slug>` convention

**Forgetting to clean up**

- Each worktree duplicates working files, wastes disk space
- Fix: Remove worktrees promptly after merging; run `git worktree prune` periodically

**Assuming directory location**

- Creates inconsistency, violates project conventions
- Fix: Follow priority: CLAUDE.md preference > sibling default
