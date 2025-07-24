#!/usr/bin/env bash

# Read JSON input (from stdin or first argument)
json_input="${1:-$(cat)}"

# Parse JSON to extract title and message
title=$(echo "$json_input" | jq -r '.title // "Notification"')
message=$(echo "$json_input" | jq -r '.message // "No message"')

# Ghostty's bundle ID
GHOSTTY_BUNDLE_ID="com.mitchellh.ghostty"

# Send a clickable notification that activates Ghostty
terminal-notifier -title "$title" \
                  -message "$message" \
                  -activate "$GHOSTTY_BUNDLE_ID"
