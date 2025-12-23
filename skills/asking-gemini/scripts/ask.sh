#!/bin/bash
# Gemini CLI wrapper with context-aware modes
# Usage: ask.sh [MODE] "prompt"
# Modes: prompt (default), brainstorm, review, compare

set -euo pipefail

MODE="${1:-prompt}"
shift 2>/dev/null || true
PROMPT="${*:-}"

# If no prompt after mode, treat mode as the prompt
if [ -z "$PROMPT" ] && [ "$MODE" != "prompt" ]; then
	PROMPT="$MODE"
	MODE="prompt"
fi

case "$MODE" in
brainstorm)
	gemini -p "Brainstorm solutions for: $PROMPT

Generate 5-10 creative approaches. For each:
- Brief description
- Key advantages
- Potential drawbacks
- When to prefer this approach"
	;;
review)
	gemini -p "Review and analyze: $PROMPT

Provide:
1. Trade-offs of current approach
2. Alternative patterns to consider
3. Potential scaling or maintenance concerns
4. Recommendations with rationale"
	;;
compare)
	gemini -p "Compare options: $PROMPT

For each option analyze:
- Performance characteristics
- Maintainability
- Complexity
- When to prefer each"
	;;
prompt | *)
	if [ "$MODE" = "prompt" ]; then
		gemini -p "$PROMPT"
	else
		gemini -p "$MODE $PROMPT"
	fi
	;;
esac
