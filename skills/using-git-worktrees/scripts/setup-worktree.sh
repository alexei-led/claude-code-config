#!/bin/bash
# Setup a new git worktree as a sibling directory
# Usage: setup-worktree.sh <branch-name> [base-branch]

set -euo pipefail

BRANCH_NAME="${1:?Usage: setup-worktree.sh <branch-name> [base-branch]}"
BASE_BRANCH="${2:-main}"

# Ensure we're in a git repo
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
	echo "Error: Not in a git repository"
	exit 1
}

PROJECT=$(basename "$REPO_ROOT")
PARENT=$(dirname "$REPO_ROOT")

# Slugify branch name: feature/auth → feature-auth
SLUG=$(echo "$BRANCH_NAME" | tr '/' '-')
WORKTREE_PATH="$PARENT/$PROJECT-$SLUG"

# Check if worktree already exists
if [ -d "$WORKTREE_PATH" ]; then
	echo "Error: Directory already exists at $WORKTREE_PATH"
	exit 1
fi

# Check if branch is already checked out in another worktree
if git worktree list | grep -q "\[$BRANCH_NAME\]"; then
	echo "Error: Branch '$BRANCH_NAME' is already checked out"
	git worktree list
	exit 1
fi

# Create worktree as sibling directory
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
echo "Worktree ready at: $WORKTREE_PATH"
echo "Branch: $BRANCH_NAME (based on $BASE_BRANCH)"
echo ""
echo "To work in this worktree:"
echo "  cd $WORKTREE_PATH"
echo ""
echo "When done:"
echo "  git worktree remove $WORKTREE_PATH"
