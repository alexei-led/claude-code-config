#!/bin/bash
set -euo pipefail

# Read hook input from stdin
INPUT=$(cat)
NAME=$(echo "$INPUT" | jq -r '.name // empty')
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

[ -z "$NAME" ] && exit 1
[ -z "$CWD" ] && CWD="$(pwd)"

cd "$CWD"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 1
PROJECT=$(basename "$REPO_ROOT")
PARENT=$(dirname "$REPO_ROOT")

# Slugify: feature/auth → feature-auth
SLUG=$(echo "$NAME" | tr '/' '-')
WORKTREE_PATH="$PARENT/$PROJECT-$SLUG"

# Create sibling worktree
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "main")
git worktree add "$WORKTREE_PATH" -b "worktree-$SLUG" "$DEFAULT_BRANCH" >&2

# Print path to stdout (required by hook contract)
echo "$WORKTREE_PATH"
