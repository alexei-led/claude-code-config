#!/usr/bin/env bash

# Read JSON input (from stdin or first argument)
json_input="${1:-$(cat)}"

# Parse JSON to extract title and message
title=$(echo "$json_input" | jq -r '.title // "Notification"')
message=$(echo "$json_input" | jq -r '.message // "No message"')

# Send notification with extracted values
osascript -e "display notification \"$message\" with title \"$title\""
