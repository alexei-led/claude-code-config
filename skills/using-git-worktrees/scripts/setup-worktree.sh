#!/bin/bash
# Setup a new git worktree with proper safety checks
# Usage: setup-worktree.sh <branch-name> [base-branch]

set -euo pipefail

BRANCH_NAME="${1:?Usage: setup-worktree.sh <branch-name> [base-branch]}"
BASE_BRANCH="${2:-main}"
WORKTREE_DIR=".worktrees"

# Ensure we're in a git repo
git rev-parse --show-toplevel >/dev/null 2>&1 || {
	echo "Error: Not in a git repository"
	exit 1
}

# Check/create worktree directory
if [ -d ".worktrees" ]; then
	WORKTREE_DIR=".worktrees"
elif [ -d "worktrees" ]; then
	WORKTREE_DIR="worktrees"
else
	WORKTREE_DIR=".worktrees"
	mkdir -p "$WORKTREE_DIR"

	# Ensure .gitignore includes worktree dir
	if ! grep -q "^\.worktrees/$" .gitignore 2>/dev/null; then
		echo ".worktrees/" >>.gitignore
		git add .gitignore
		git commit -m "chore: add .worktrees to gitignore"
		echo "Added .worktrees/ to .gitignore"
	fi
fi

WORKTREE_PATH="$WORKTREE_DIR/$BRANCH_NAME"

# Check if worktree already exists
if [ -d "$WORKTREE_PATH" ]; then
	echo "Worktree already exists at $WORKTREE_PATH"
	exit 1
fi

# Create worktree
echo "Creating worktree at $WORKTREE_PATH from $BASE_BRANCH..."
git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" "$BASE_BRANCH"

cd "$WORKTREE_PATH"

# Auto-detect and run setup
if [ -f "package.json" ]; then
	echo "Installing npm dependencies..."
	npm install
elif [ -f "go.mod" ]; then
	echo "Downloading Go modules..."
	go mod download
elif [ -f "pyproject.toml" ]; then
	echo "Installing Python dependencies..."
	uv sync 2>/dev/null || pip install -e ".[dev]" 2>/dev/null || true
elif [ -f "Cargo.toml" ]; then
	echo "Building Rust project..."
	cargo build
fi

echo ""
echo "Worktree ready at: $(pwd)"
echo "Branch: $BRANCH_NAME"
echo ""
echo "To switch to this worktree:"
echo "  cd $WORKTREE_PATH"
