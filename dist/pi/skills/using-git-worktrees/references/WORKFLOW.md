# Git Worktrees Workflow

## Directory Selection Process

### 1. Detect Project Name and Root

Derive from the **main** worktree (first porcelain entry), so the path is identical whether invoked from the main repo or from inside another worktree:

```bash
main_wt=$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')
project=$(basename "$main_wt")
parent=$(dirname "$main_wt")
root="$parent/$project.worktrees"
```

### 2. Determine Worktree Path

**Priority order:**

1. Check CLAUDE.md for explicit preference
2. Use the per-project root (default): `<project>.worktrees/<branch-slug>`

```bash
# Slugify branch name: feature/auth → feature-auth
slug=$(echo "$BRANCH_NAME" | tr '/' '-')
path="$root/$slug"
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
mkdir -p "$root"   # per-project root, created on first use

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

### After a PR Merges

State what is being removed before running it. Run from the main worktree — never from inside the worktree being deleted.

```bash
branch=feature/auth
main_wt=$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')
wt=$(git worktree list --porcelain | awk -v b="refs/heads/$branch" '
  /^worktree /{p=$2} $0=="branch "b{print p; exit}')

# 1. Confirm the PR actually merged (source of truth — not local ancestry)
gh pr view "$branch" --json state,mergedAt

# 2. Remove the worktree from the main repo
cd "$main_wt"
git worktree remove "$wt"          # --force only if dirty, after confirming with user

# 3. Delete the branch. -d refuses after squash/rebase merge ("not fully
#    merged"); that is expected once the PR is MERGED — fall back to -D.
git branch -d "$branch" 2>/dev/null || git branch -D "$branch"

# 4. Sync refs and drop the per-project root if it is now empty
git fetch --prune
rmdir "$(dirname "$wt")" 2>/dev/null || true
```

Do not auto-run `git pull`: the main worktree may not be on main, may be dirty, or may have no upstream. Pull only after confirming state.

Scripted equivalent: `scripts/cleanup-worktree.sh [branch]` (defaults to the current worktree's branch). Strict by default — refuses unless `gh` confirms the PR is MERGED; pass `--force` to override (gh absent, or abandoning an unmerged branch).

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

- **Creating worktree** — `<project>.worktrees/<branch-slug>`
- **CLAUDE.md has preference** — Use specified location
- **Path already exists** — Report conflict, ask user
- **Branch already checked out** — Report, suggest existing worktree
- **Tests fail during baseline** — Report failures + ask
- **PR merged** — `git worktree remove` + `git branch -d` (fall back to `-D` after squash/rebase)
- **Stale worktrees** — `git worktree prune`

## Common Commands

```bash
# List all worktrees
git worktree list

# Remove worktree (after PR merges)
git worktree remove myproject.worktrees/feature-name

# Prune stale worktree entries
git worktree prune

# Move worktree to new location
git worktree move myproject.worktrees/old-name myproject.worktrees/new-name

# Lock worktree (prevent pruning, e.g. on removable drive)
git worktree lock myproject.worktrees/feature-name
```

## Common Mistakes

**Nesting worktrees inside the repo**

- Requires .gitignore management, pollutes git status
- Fix: Keep all worktrees under the sibling `<project>.worktrees/` root

**Scattering worktrees as flat siblings**

- `../proj-a`, `../proj-b` clutter the parent dir, no per-project grouping
- Fix: One root per project — `<project>.worktrees/<slug>`

**Non-descriptive directory names**

- `temp`, `wt2` — requires inspection to understand purpose
- Fix: Use the branch slug as the directory name

**Forgetting to clean up**

- Each worktree duplicates working files, wastes disk space
- Fix: Remove worktree + branch promptly after the PR merges; run `git worktree prune` periodically

**Assuming directory location**

- Creates inconsistency, violates project conventions
- Fix: Follow priority: CLAUDE.md preference > sibling default
