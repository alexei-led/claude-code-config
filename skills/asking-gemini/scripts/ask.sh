#!/bin/bash
# Gemini CLI wrapper with context-aware modes
# Usage: ask.sh [MODE] "prompt"
# Modes: prompt (default), brainstorm, review, compare
#
# SANDBOX WORKAROUND: Gemini CLI writes to ~/.gemini/ which is blocked
# by Claude Code's sandbox. We redirect HOME to /tmp/claude and copy
# credentials on first run.

set -euo pipefail

TIMEOUT="${TIMEOUT:-60}"

if ! command -v gemini &>/dev/null; then
	echo "Error: gemini CLI not found" >&2
	exit 1
fi

if [[ "${1:-}" =~ ^(-h|--help)$ ]]; then
	echo "Usage: ask.sh [MODE] \"prompt\""
	echo "Modes: brainstorm, review, compare, prompt (default)"
	exit 0
fi

# Sandbox workaround: use ephemeral session directory
SANDBOX_HOME=$(mktemp -d -t claude-gemini.XXXXXX)
chmod 700 "$SANDBOX_HOME"
trap 'rm -rf "$SANDBOX_HOME"' EXIT

SANDBOX_GEMINI="$SANDBOX_HOME/.gemini"
REAL_GEMINI="$HOME/.gemini"

# Copy essential config files
mkdir -p "$SANDBOX_GEMINI"
for f in settings.json oauth_creds.json; do
	[[ -f "$REAL_GEMINI/$f" ]] && cp "$REAL_GEMINI/$f" "$SANDBOX_GEMINI/"
done

MODE="${1:-prompt}"
shift 2>/dev/null || true
PROMPT="${*:-}"

# If no prompt after mode, treat mode as the prompt
if [ -z "$PROMPT" ] && [ "$MODE" != "prompt" ]; then
	PROMPT="$MODE"
	MODE="prompt"
fi

# Run gemini with timeout (stderr suppressed for clean output)
run_gemini() {
	if timeout "$TIMEOUT" env HOME="$SANDBOX_HOME" gemini -o text "$@" 2>/dev/null; then
		return 0
	fi
	local exit_code=$?
	if [ $exit_code -eq 124 ]; then
		echo "Error: Gemini CLI timed out after ${TIMEOUT}s" >&2
	else
		echo "Error: Gemini CLI failed (exit code $exit_code)" >&2
	fi
	return 1
}

case "$MODE" in
brainstorm)
	run_gemini "Brainstorm solutions for: $PROMPT

Generate 5-10 creative approaches. For each:
- Brief description
- Key advantages
- Potential drawbacks
- When to prefer this approach"
	;;
review)
	run_gemini "Review and analyze: $PROMPT

Provide:
1. Trade-offs of current approach
2. Alternative patterns to consider
3. Potential scaling or maintenance concerns
4. Recommendations with rationale"
	;;
compare)
	run_gemini "Compare options: $PROMPT

For each option analyze:
- Performance characteristics
- Maintainability
- Complexity
- When to prefer each"
	;;
prompt | *)
	if [ "$MODE" = "prompt" ]; then
		run_gemini "$PROMPT"
	else
		run_gemini "$MODE $PROMPT"
	fi
	;;
esac
