#!/bin/bash
# Claude Code auth helper - dynamically provides auth based on active env
# Called by Claude Code via apiKeyHelper setting to get the API token
#
# Reads active env from ~/.claude/active-env.json
# Reads API keys from ~/.claude/secrets.json (baked by chezmoi from 1Password)
#
# Priority: This script is only used when ANTHROPIC_AUTH_TOKEN and
# ANTHROPIC_API_KEY are not set in the environment.

set -euo pipefail

ACTIVE_ENV_FILE="${HOME}/.claude/active-env.json"
SECRETS_FILE="${HOME}/.claude/secrets.json"

# Get active environment
ACTIVE_ENV=$(jq -r '.env // "default"' "$ACTIVE_ENV_FILE" 2>/dev/null || echo "default")

case "$ACTIVE_ENV" in
copilot)
	# Copilot proxy uses dummy token - ensure proxy is running
	PID_FILE="${TMPDIR:-/tmp}/copilot-proxy.pid"
	PROXY_RUNNING=false

	if [ -f "$PID_FILE" ]; then
		PID=$(cat "$PID_FILE" 2>/dev/null || echo "")
		if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
			PROXY_RUNNING=true
		fi
	fi

	if [ "$PROXY_RUNNING" = false ]; then
		# Start proxy in background
		"${HOME}/.claude/scripts/copilot-proxy.sh" >/dev/null 2>&1 &
		sleep 2 # Give proxy time to start
	fi

	# Check if proxy actually started successfully
	if [ -f "$PID_FILE" ]; then
		PID=$(cat "$PID_FILE" 2>/dev/null || echo "")
		if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
			echo "dummy"
			exit 0
		fi
	fi

	# Proxy failed to start - fall through to empty (SSO auth)
	echo ""
	;;
default)
	# Default (Max subscription) - return empty to use Claude.ai SSO
	echo ""
	;;
*)
	# Other providers (zai, deepseek, vertex) - read from chezmoi-baked secrets
	TOKEN=$(jq -r ".\"${ACTIVE_ENV}\" // empty" "$SECRETS_FILE" 2>/dev/null || echo "")
	if [ -n "$TOKEN" ]; then
		echo "$TOKEN"
	else
		echo ""
	fi
	;;
esac
