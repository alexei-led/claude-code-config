#!/bin/bash
# SessionStart hook - Initialize agent with project context
# Provides context recovery for spec-driven projects and git state

set -euo pipefail

# Cleanup old files (background, silent, non-blocking)
(
	find ~/.claude/todos -type f -mtime +7 -delete 2>/dev/null
	find ~/.claude/debug -type f -mtime +30 -delete 2>/dev/null
	find ~/.claude/plans -type f -name "*.md" -mtime +30 -exec gzip {} \; 2>/dev/null
) &

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get working directory from stdin JSON or fallback to pwd
if [ -t 0 ]; then
	WORKDIR="$(pwd)"
else
	INPUT=$(cat)
	WORKDIR=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null || pwd)
	[ -z "$WORKDIR" ] && WORKDIR="$(pwd)"
fi

cd "$WORKDIR" 2>/dev/null || exit 0

# Always show git context if available
if [ -d ".git" ]; then
	BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
	LAST_COMMIT=$(git log --oneline -1 2>/dev/null || echo "no commits")
	echo -e "${BLUE}🌿 Branch:${NC} $BRANCH"
	echo -e "${BLUE}📝 Last:${NC} $LAST_COMMIT"
fi

# .spec/ project detection
if [ -d ".spec" ] && command -v specctl &>/dev/null; then
	echo ""
	echo -e "${CYAN}📋 Spec-Driven Project${NC}"
	if command -v jq &>/dev/null; then
		STATUS=$(specctl status --json 2>/dev/null) || true
		if [ -n "$STATUS" ]; then
			DONE=$(echo "$STATUS" | jq -r '.done // 0')
			TOTAL=$(echo "$STATUS" | jq -r '.total // 0')
			IN_PROG=$(echo "$STATUS" | jq -r '.in_progress // 0')
			echo -e "${GREEN}📊 Tasks:${NC} ${DONE}/${TOTAL} done, ${IN_PROG} in progress"
		fi
		SESSION=$(specctl session show --json 2>/dev/null) || true
		if [ -n "$SESSION" ] && [ "$(echo "$SESSION" | jq -r '.task // empty')" != "" ]; then
			STASK=$(echo "$SESSION" | jq -r '.task')
			SSTEP=$(echo "$SESSION" | jq -r '.step')
			echo -e "${YELLOW}⚠️  Session:${NC} ${STASK} at ${SSTEP} — run \`specctl session resume\`"
		else
			READY=$(specctl ready --json 2>/dev/null) || true
			if [ -n "$READY" ] && [ "$READY" != "[]" ]; then
				echo -e "${GREEN}✅ Ready:${NC}"
				echo "$READY" | jq -r '.[:3][] | "    \(.id) [\(.priority)] \(.title)"' 2>/dev/null || true
			fi
		fi
	else
		specctl status 2>/dev/null | head -5 || true
	fi
fi

# feature_list.json project detection
if [ -f "feature_list.json" ]; then
	echo ""
	echo -e "${CYAN}📋 Spec-Driven Project${NC}"

	# Feature count
	if command -v jq &>/dev/null; then
		PASSING=$(jq '[.[] | select(.passes==true)] | length' feature_list.json 2>/dev/null || echo "?")
		TOTAL=$(jq 'length' feature_list.json 2>/dev/null || echo "?")

		if [ "$PASSING" != "?" ] && [ "$TOTAL" != "?" ]; then
			PERCENT=$((PASSING * 100 / TOTAL))
			echo -e "${GREEN}📊 Features:${NC} $PASSING/$TOTAL passing (${PERCENT}%)"
		fi
	fi

	# Progress notes
	if [ -f "claude-progress.txt" ]; then
		echo ""
		echo -e "${YELLOW}📝 Progress Notes:${NC}"
		# Show status line and "What to work on next" section
		grep -E "^## Current Status:|^## Session|Priority features|What to work on next" claude-progress.txt 2>/dev/null | head -5 || head -8 claude-progress.txt
	fi

	# Uncommitted changes warning
	if [ -d ".git" ]; then
		CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
		if [ "$CHANGES" -gt 0 ]; then
			echo ""
			echo -e "${YELLOW}⚠️  Uncommitted changes:${NC} $CHANGES files"
		fi
	fi
fi

# Standard project detection (Makefile, package.json, go.mod, etc.)
if [ ! -f "feature_list.json" ]; then
	# Show project type hints
	[ -f "go.mod" ] && echo -e "${CYAN}🐹 Go project${NC}"
	[ -f "package.json" ] && echo -e "${CYAN}📦 Node.js project${NC}"
	[ -f "pyproject.toml" ] && echo -e "${CYAN}🐍 Python project${NC}"
	[ -f "Cargo.toml" ] && echo -e "${CYAN}🦀 Rust project${NC}"

	# Show README hint if exists
	[ -f "README.md" ] && echo -e "${BLUE}📖 README.md available${NC}"
	[ -f "CLAUDE.md" ] && echo -e "${BLUE}🤖 CLAUDE.md available${NC}"
fi

exit 0
