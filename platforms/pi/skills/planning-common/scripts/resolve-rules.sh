#!/bin/bash
set -euo pipefail

filename="${1:-planning-rules.md}"

if [ -f ".pi/$filename" ] && [ -s ".pi/$filename" ]; then
	cat ".pi/$filename"
	exit 0
fi

if [ -f ".claude/$filename" ] && [ -s ".claude/$filename" ]; then
	cat ".claude/$filename"
	exit 0
fi

user_file="$HOME/.pi/agent/$filename"
if [ -f "$user_file" ] && [ -s "$user_file" ]; then
	cat "$user_file"
fi
