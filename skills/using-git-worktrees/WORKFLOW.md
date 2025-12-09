# Git Worktrees Workflow

## Directory Selection Process

### 1. Check Existing Directories

```bash
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

If found: Use that directory. If both exist, `.worktrees` wins.

### 2. Check CLAUDE.md

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

If preference specified: Use it without asking.

### 3. Ask User

```
No worktree directory found. Where should I create worktrees?

1. .worktrees/ (project-local, hidden)
2. ~/.config/superpowers/worktrees/<project-name>/ (global location)
```

## Safety Verification

### For Project-Local Directories

**MUST verify .gitignore before creating worktree:**

```bash
grep -q "^\.worktrees/$" .gitignore || grep -q "^worktrees/$" .gitignore
```

**If NOT in .gitignore:**

1. Add appropriate line to .gitignore
2. Commit the change
3. Proceed with worktree creation

### For Global Directory

No .gitignore verification needed - outside project entirely.

## Creation Steps

### 1. Detect Project Name

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

### 2. Create Worktree

```bash
# Determine full path
case $LOCATION in
  .worktrees|worktrees)
    path="$LOCATION/$BRANCH_NAME"
    ;;
  ~/.config/superpowers/worktrees/*)
    path="~/.config/superpowers/worktrees/$project/$BRANCH_NAME"
    ;;
esac

# Create worktree with new branch
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### 3. Run Project Setup

Auto-detect and run appropriate setup:

```bash
# Node.js
[ -f package.json ] && npm install

# Rust
[ -f Cargo.toml ] && cargo build

# Python
[ -f requirements.txt ] && pip install -r requirements.txt
[ -f pyproject.toml ] && uv sync

# Go
[ -f go.mod ] && go mod download
```

### 4. Verify Clean Baseline

Run tests to ensure worktree starts clean:

```bash
# Use project-appropriate command
make test  # or npm test, cargo test, pytest, go test ./...
```

**If tests fail:** Report failures, ask whether to proceed.
**If tests pass:** Report ready.

### 5. Report Location

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Quick Reference

| Situation                   | Action                      |
| --------------------------- | --------------------------- |
| `.worktrees/` exists        | Use it (verify .gitignore)  |
| `worktrees/` exists         | Use it (verify .gitignore)  |
| Both exist                  | Use `.worktrees/`           |
| Neither exists              | Check CLAUDE.md → Ask user  |
| Directory not in .gitignore | Add it immediately + commit |
| Tests fail during baseline  | Report failures + ask       |

## Common Commands

```bash
# List all worktrees
git worktree list

# Remove worktree (after merging branch)
git worktree remove .worktrees/feature-name

# Prune stale worktrees
git worktree prune

# Move worktree
git worktree move .worktrees/old-name .worktrees/new-name
```

## Common Mistakes

**Skipping .gitignore verification**

- Worktree contents get tracked, pollute git status
- Fix: Always check .gitignore before creating project-local worktree

**Assuming directory location**

- Creates inconsistency, violates project conventions
- Fix: Follow priority: existing > CLAUDE.md > ask

**Proceeding with failing tests**

- Can't distinguish new bugs from pre-existing issues
- Fix: Report failures, get explicit permission
