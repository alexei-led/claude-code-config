#!/usr/bin/env bash
# notify.sh - Notification hook for Claude Code with project context
#
# Available input fields:
#   session_id, cwd, message, notification_type, transcript_path, permission_mode

# Read JSON input (from stdin or first argument)
json_input="${1:-$(cat)}"

# Parse JSON - extract all available context
title=$(echo "$json_input" | jq -r '.title // "Claude Code"')
message=$(echo "$json_input" | jq -r '.message // "No message"')
cwd=$(echo "$json_input" | jq -r '.cwd // ""')
notification_type=$(echo "$json_input" | jq -r '.notification_type // ""')
# session_id available but not used currently
# session_id=$(echo "$json_input" | jq -r '.session_id // ""')

# Extract project name from cwd (last directory component)
project_name=""
if [[ -n "$cwd" ]]; then
	project_name=$(basename "$cwd")
	title="[$project_name] $title"
fi

# Add notification type context
case "$notification_type" in
permission_prompt) title="🔐 $title" ;;
idle_prompt) title="💤 $title" ;;
esac

# Check if terminal-notifier is available
if ! command -v terminal-notifier &>/dev/null; then
	echo "📢 $title: $message" >&2
	exit 0
fi

# Map $TERM_PROGRAM to bundle ID (works across machines)
case "${TERM_PROGRAM:-Terminal}" in
ghostty | Ghostty) BUNDLE_ID="com.mitchellh.ghostty" ;;
iTerm.app) BUNDLE_ID="com.googlecode.iterm2" ;;
WezTerm) BUNDLE_ID="com.github.wez.wezterm" ;;
Alacritty) BUNDLE_ID="org.alacritty" ;;
kitty) BUNDLE_ID="net.kovidgoyal.kitty" ;;
*) BUNDLE_ID="com.apple.Terminal" ;;
esac

# Allow override via environment variable
BUNDLE_ID="${CLAUDE_TERMINAL_BUNDLE_ID:-$BUNDLE_ID}"

# Send notification
terminal-notifier -title "$title" \
	-message "$message" \
	-activate "$BUNDLE_ID" \
	2>/dev/null || echo "📢 $title: $message" >&2
