#!/bin/bash
# Codex CLI wrapper with context-aware modes
# Usage: ask.sh [MODE] "prompt" [--auto]
# Modes: exec (default), review, plan, implement
#
# SANDBOX NOTE: Codex CLI uses macOS SystemConfiguration APIs for network
# proxy detection. These APIs are blocked by Claude Code's sandbox, causing
# a Rust panic. This script must be run with sandbox disabled:
#   dangerouslyDisableSandbox: true

set -euo pipefail

# Codex is slow - 10 minutes recommended per Perplexity research
TIMEOUT="${TIMEOUT:-600}"
MAX_RETRIES="${MAX_RETRIES:-0}"

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

# Run codex with timeout and clean output (suppress verbose logs)
# Usage: run_codex_exec [options] "prompt"
# Usage: run_codex_review [options]
run_codex_exec() {
	local tmpfile
	tmpfile=$(mktemp)
	trap 'rm -f "$tmpfile"' RETURN

	if timeout "$TIMEOUT" codex exec -o "$tmpfile" "$@" >/dev/null 2>&1; then
		cat "$tmpfile"
		return 0
	fi
	local exit_code=$?
	if [ $exit_code -eq 124 ]; then
		echo "Error: Codex CLI timed out after ${TIMEOUT}s" >&2
	else
		echo "Error: Codex CLI failed (exit code $exit_code)" >&2
	fi
	return 1
}

run_codex_review() {
	local tmpfile
	tmpfile=$(mktemp)
	trap 'rm -f "$tmpfile"' RETURN

	if timeout "$TIMEOUT" codex review -o "$tmpfile" "$@" >/dev/null 2>&1; then
		cat "$tmpfile"
		return 0
	fi
	local exit_code=$?
	if [ $exit_code -eq 124 ]; then
		echo "Error: Codex CLI timed out after ${TIMEOUT}s" >&2
	else
		echo "Error: Codex CLI failed (exit code $exit_code)" >&2
	fi
	return 1
}

case "$MODE" in
review)
	# Review uncommitted changes with optional custom instructions
	if [ -n "$PROMPT" ]; then
		run_codex_review --uncommitted "$PROMPT"
	else
		run_codex_review --uncommitted
	fi
	;;
plan)
	run_codex_exec -s read-only "Create implementation plan: $PROMPT

Break into:
1. Required changes
2. Files to modify
3. Implementation steps
4. Testing approach"
	;;
implement)
	run_codex_exec -s workspace-write ${AUTO:+"$AUTO"} "Implement: $PROMPT

Requirements:
- Follow existing code patterns
- Add appropriate error handling
- Maintain consistency with codebase style"
	;;
exec | *)
	if [ "$MODE" = "exec" ]; then
		run_codex_exec -s read-only ${AUTO:+"$AUTO"} "$PROMPT"
	else
		run_codex_exec -s read-only ${AUTO:+"$AUTO"} "$MODE $PROMPT"
	fi
	;;
esac
