#!/bin/bash
# Codex CLI wrapper with context-aware modes
# Usage: ask.sh [MODE] "prompt" [--auto]
# Modes: exec (default), review, plan, implement
# Designed to run as subagent - returns clean output only

set -euo pipefail

if ! command -v codex &>/dev/null; then
	echo "Error: codex CLI not found" >&2
	exit 1
fi

if [[ "${1:-}" =~ ^(-h|--help)$ ]]; then
	echo "Usage: ask.sh [MODE] \"prompt\" [--auto]"
	echo "Modes: exec (default), review, plan, implement"
	exit 0
fi

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

# Run codex with full access (already inside Claude's sandbox) and suppress progress
run_codex() {
	codex --sandbox danger-full-access "$@" 2>/dev/null
}

case "$MODE" in
review)
	run_codex review "$PROMPT"
	;;
plan)
	run_codex exec "Create implementation plan: $PROMPT

Break into:
1. Required changes
2. Files to modify
3. Implementation steps
4. Testing approach"
	;;
implement)
	run_codex exec ${AUTO:+"$AUTO"} "Implement: $PROMPT

Requirements:
- Follow existing code patterns
- Add appropriate error handling
- Maintain consistency with codebase style"
	;;
exec | *)
	if [ "$MODE" = "exec" ]; then
		run_codex exec ${AUTO:+"$AUTO"} "$PROMPT"
	else
		run_codex exec ${AUTO:+"$AUTO"} "$MODE $PROMPT"
	fi
	;;
esac
