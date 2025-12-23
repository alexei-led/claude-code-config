#!/bin/bash
# Minimal skill reminder - trusts Claude's natural skill selection
# Claude uses skill descriptions from <available_skills> to choose relevant skills

set -euo pipefail

# Read prompt from stdin (JSON input from Claude Code)
INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // .' 2>/dev/null || echo "$INPUT")

# Skip very short prompts (greetings, confirmations)
[[ ${#PROMPT} -lt 15 ]] && exit 0

# Skip if user is already explicitly activating skills
[[ "$PROMPT" =~ [Ss]kill\( ]] && exit 0

# Skip common follow-up patterns
PROMPT_LOWER=$(echo "$PROMPT" | tr '[:upper:]' '[:lower:]')
[[ "$PROMPT_LOWER" =~ ^(yes|no|ok|okay|sure|thanks|continue|proceed|go ahead|do it|looks good|lgtm)$ ]] && exit 0

# Minimal guidance - Claude decides relevance based on skill descriptions
echo "SKILL ACTIVATION: Check <available_skills> for relevance."
