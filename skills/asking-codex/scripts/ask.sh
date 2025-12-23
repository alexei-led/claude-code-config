#!/bin/bash
# Codex CLI wrapper with context-aware modes
# Usage: ask.sh [MODE] "prompt" [--auto]
# Modes: exec (default), review, plan, implement

set -euo pipefail

MODE="${1:-exec}"
shift 2>/dev/null || true

# Check for --auto flag
AUTO=""
ARGS=()
for arg in "$@"; do
	if [ "$arg" = "--auto" ]; then
		AUTO="--full-auto"
	else
		ARGS+=("$arg")
	fi
done
PROMPT="${ARGS[*]:-}"

# If no prompt after mode, treat mode as the prompt
if [ -z "$PROMPT" ] && [ "$MODE" != "exec" ]; then
	PROMPT="$MODE"
	MODE="exec"
fi

case "$MODE" in
review)
	# Use dedicated review command
	codex review "$PROMPT"
	;;
plan)
	codex exec "Create implementation plan: $PROMPT

Break into:
1. Required changes
2. Files to modify
3. Implementation steps
4. Testing approach"
	;;
implement)
	codex exec $AUTO "Implement: $PROMPT

Requirements:
- Follow existing code patterns
- Add appropriate error handling
- Maintain consistency with codebase style"
	;;
exec | *)
	if [ "$MODE" = "exec" ]; then
		codex exec $AUTO "$PROMPT"
	else
		codex exec $AUTO "$MODE $PROMPT"
	fi
	;;
esac
