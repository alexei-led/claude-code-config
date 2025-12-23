#!/bin/bash
# Gemini CLI wrapper with context-aware modes
# Usage: ask.sh [MODE] "prompt"
# Modes: prompt (default), brainstorm, review, compare
# Designed to run as subagent - returns clean output only

set -euo pipefail

if ! command -v gemini &>/dev/null; then
	echo "Error: gemini CLI not found" >&2
	exit 1
fi

if [[ "${1:-}" =~ ^(-h|--help)$ ]]; then
	echo "Usage: ask.sh [MODE] \"prompt\""
	echo "Modes: brainstorm, review, compare, prompt (default)"
	exit 0
fi

MODE="${1:-prompt}"
shift 2>/dev/null || true
PROMPT="${*:-}"

# If no prompt after mode, treat mode as the prompt
if [ -z "$PROMPT" ] && [ "$MODE" != "prompt" ]; then
	PROMPT="$MODE"
	MODE="prompt"
fi

# Run gemini with clean text output (no streaming, no progress)
run_gemini() {
	gemini -o text "$@" 2>/dev/null
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
