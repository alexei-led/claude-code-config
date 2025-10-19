#!/usr/bin/env bash
# notify.sh - Cross-platform notification hook for Claude Code

# Read JSON input (from stdin or first argument)
json_input="${1:-$(cat)}"

# Parse JSON to extract title and message
title=$(echo "$json_input" | jq -r '.title // "Notification"')
message=$(echo "$json_input" | jq -r '.message // "No message"')

# Check if terminal-notifier is available
if ! command -v terminal-notifier &>/dev/null; then
    echo "📢 $title: $message" >&2
    exit 0
fi

# Map $TERM_PROGRAM to bundle ID (works across machines)
case "${TERM_PROGRAM:-Terminal}" in
    ghostty|Ghostty) BUNDLE_ID="com.mitchellh.ghostty" ;;
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
