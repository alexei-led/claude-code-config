#!/bin/bash
set -euo pipefail

INPUT=$(cat)
WORKTREE_PATH=$(echo "$INPUT" | jq -r '.worktree_path // empty')

[ -z "$WORKTREE_PATH" ] && exit 0

# Remove worktree and its branch
BRANCH=$(git -C "$WORKTREE_PATH" branch --show-current 2>/dev/null || true)
git worktree remove "$WORKTREE_PATH" 2>/dev/null || rm -rf "$WORKTREE_PATH"
[ -n "$BRANCH" ] && git branch -D "$BRANCH" 2>/dev/null || true
