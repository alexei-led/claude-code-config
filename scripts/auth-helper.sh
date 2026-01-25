#!/bin/bash
# Claude Code auth helper - dynamically provides auth based on _activeEnv
# Called by Claude Code via apiKeyHelper setting to get the API token
#
# Priority: This script is only used when ANTHROPIC_AUTH_TOKEN and
# ANTHROPIC_API_KEY are not set in the environment.

set -euo pipefail

SETTINGS_FILE="${HOME}/.claude/settings.json"

# Get active environment
ACTIVE_ENV=$(jq -r '._activeEnv // "default"' "$SETTINGS_FILE" 2>/dev/null || echo "default")

# Get env config for active environment
ENV_CONFIG=$(jq -r ".\"env.${ACTIVE_ENV}\" // {}" "$SETTINGS_FILE" 2>/dev/null)

# Check for keychain service in env config
KEYCHAIN_SERVICE=$(echo "$ENV_CONFIG" | jq -r '._keychain // empty' 2>/dev/null)

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
	# Note: Empty output means Claude Code falls back to SSO auth
	echo ""
	;;
*)
	# Other providers (zai, deepseek, vertex) - get from keychain
	if [ -n "$KEYCHAIN_SERVICE" ]; then
		TOKEN=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null || echo "")
		if [ -n "$TOKEN" ]; then
			echo "$TOKEN"
		else
			# Keychain lookup failed, return empty for SSO fallback
			echo ""
		fi
	else
		# No keychain configured, return empty for SSO fallback
		echo ""
	fi
	;;
esac
