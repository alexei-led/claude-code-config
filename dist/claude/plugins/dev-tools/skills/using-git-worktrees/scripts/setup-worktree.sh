#!/usr/bin/env bash
# Create a git worktree under the per-project root <project>.worktrees/<slug>
# Usage: setup-worktree.sh <branch-name> [base-branch]

set -euo pipefail

BRANCH_NAME="${1:?Usage: setup-worktree.sh <branch-name> [base-branch]}"
BASE_BRANCH="${2:-main}"

porcelain=$(git worktree list --porcelain 2>/dev/null) || {
	echo "Error: Not in a git repository"
	exit 1
}

# Root derives from the MAIN worktree (first porcelain entry) so it is the
# same whether invoked from the main repo or from inside another worktree.
MAIN_WT=$(awk '/^worktree /{print $2; exit}' <<<"$porcelain")
PROJECT=$(basename "$MAIN_WT")
ROOT="$(dirname "$MAIN_WT")/$PROJECT.worktrees"

SLUG=$(echo "$BRANCH_NAME" | tr '/' '-')
WORKTREE_PATH="$ROOT/$SLUG"

mkdir -p "$ROOT"

echo "Creating worktree at $WORKTREE_PATH from $BASE_BRANCH..."
git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" "$BASE_BRANCH"

cd "$WORKTREE_PATH"

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
echo "When the PR merges, clean up with:"
echo "  scripts/cleanup-worktree.sh $BRANCH_NAME"
