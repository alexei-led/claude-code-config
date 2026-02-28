#!/usr/bin/env bash
# Copilot API Proxy for Claude Code
# Starts proxy with Anthropic model mapping for use when hitting API limits
#
# Usage:
#   copilot-proxy.sh          # Start in background
#   copilot-proxy.sh --fg     # Start in foreground
#   copilot-proxy.sh --stop   # Stop running proxy
#   copilot-proxy.sh --status # Check if proxy is running

set -euo pipefail

PORT="${COPILOT_PROXY_PORT:-4141}"
PID_FILE="${TMPDIR:-/tmp}/copilot-proxy.pid"
LOG_FILE="${TMPDIR:-/tmp}/copilot-proxy.log"

# Model IDs from centralized profiles; fall back to hardcoded defaults
if command -v python3 >/dev/null 2>&1 && json=$(ce --show-models --json 2>/dev/null) && [[ -n "$json" ]]; then
	CLAUDE_MODEL=$(python3 -c "import sys,json; d=json.load(sys.stdin).get('copilot',{}); print(d.get('ANTHROPIC_MODEL', d.get('ANTHROPIC_DEFAULT_OPUS_MODEL','')))" <<<"$json" 2>/dev/null) || true
	CLAUDE_SONNET_MODEL=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('copilot',{}).get('ANTHROPIC_DEFAULT_SONNET_MODEL',''))" <<<"$json" 2>/dev/null) || true
	CLAUDE_HAIKU_MODEL=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('copilot',{}).get('ANTHROPIC_DEFAULT_HAIKU_MODEL',''))" <<<"$json" 2>/dev/null) || true
fi
CLAUDE_MODEL="${CLAUDE_MODEL:-claude-opus-4.6}"
CLAUDE_SONNET_MODEL="${CLAUDE_SONNET_MODEL:-claude-sonnet-4.5}"
CLAUDE_HAIKU_MODEL="${CLAUDE_HAIKU_MODEL:-claude-haiku-4.5}"

start_proxy() {
	local foreground="${1:-false}"

	if is_running; then
		echo "Copilot proxy already running (PID: $(cat "$PID_FILE"))"
		echo "Use 'copilot-proxy.sh --stop' to stop it first"
		exit 1
	fi

	echo "Starting Copilot API proxy on port $PORT..."

	if [[ "$foreground" == "true" ]]; then
		# --claude-code enables interactive model selection (requires TTY)
		exec bunx --reload copilot-api@latest start \
			--claude-code \
			--port "$PORT"
	else
		# Background mode: skip --claude-code (requires TTY for interactive prompts)
		nohup bunx --reload copilot-api@latest start \
			--port "$PORT" \
			>"$LOG_FILE" 2>&1 &

		echo $! >"$PID_FILE"
		sleep 2

		if is_running; then
			echo "✅ Proxy started (PID: $(cat "$PID_FILE"))"
			echo "   Port: $PORT"
			echo "   Logs: $LOG_FILE"
			echo ""
			echo "Run this to configure Claude Code:"
			echo "  eval \"\$($0 --env)\""
		else
			echo "❌ Failed to start proxy. Check logs: $LOG_FILE"
			exit 1
		fi
	fi
}

print_env() {
	cat <<EOF
export ANTHROPIC_BASE_URL="http://localhost:$PORT"
export ANTHROPIC_AUTH_TOKEN="dummy"
export ANTHROPIC_MODEL="$CLAUDE_MODEL"
export ANTHROPIC_DEFAULT_SONNET_MODEL="$CLAUDE_SONNET_MODEL"
export ANTHROPIC_SMALL_FAST_MODEL="$CLAUDE_HAIKU_MODEL"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="$CLAUDE_HAIKU_MODEL"
export DISABLE_NON_ESSENTIAL_MODEL_CALLS=1
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
EOF
}

stop_proxy() {
	if [[ -f "$PID_FILE" ]]; then
		local pid
		pid=$(cat "$PID_FILE")
		if kill -0 "$pid" 2>/dev/null; then
			echo "Stopping Copilot proxy (PID: $pid)..."
			kill "$pid"
			rm -f "$PID_FILE"
			echo "✅ Proxy stopped"
		else
			echo "Process not running, cleaning up PID file"
			rm -f "$PID_FILE"
		fi
	else
		echo "No PID file found. Proxy may not be running."
		# Try to find and kill any running proxy
		if pkill -f "copilot-api.*start" 2>/dev/null; then echo "Killed orphan proxy process"; fi
	fi
}

is_running() {
	if [[ -f "$PID_FILE" ]]; then
		local pid
		pid=$(cat "$PID_FILE")
		kill -0 "$pid" 2>/dev/null
		return $?
	fi
	return 1
}

show_status() {
	if is_running; then
		echo "✅ Copilot proxy is running (PID: $(cat "$PID_FILE"))"
		echo "   Port: $PORT"
		echo "   Logs: $LOG_FILE"

		# Check if port is actually responding
		if curl -s "http://localhost:$PORT" >/dev/null 2>&1; then
			echo "   Health: OK"
		else
			echo "   Health: Not responding (may still be starting)"
		fi
	else
		echo "❌ Copilot proxy is not running"
	fi
}

show_usage() {
	cat <<EOF
Copilot API Proxy for Claude Code

Usage:
  copilot-proxy.sh [OPTIONS]

Options:
  (none)      Start proxy in background
  --fg        Start proxy in foreground (interactive model selection)
  --stop      Stop running proxy
  --status    Check proxy status
  --env       Print environment variables for Claude Code
  --help      Show this help

Environment:
  COPILOT_PROXY_PORT    Port to run on (default: 4141)

Models (from active model profile, see: ce --show-models):
  ANTHROPIC_MODEL              = $CLAUDE_MODEL
  ANTHROPIC_DEFAULT_SONNET_MODEL = $CLAUDE_SONNET_MODEL
  ANTHROPIC_SMALL_FAST_MODEL   = $CLAUDE_HAIKU_MODEL

To configure Claude Code after starting:
  eval "\$(copilot-proxy.sh --env)"

Note: First run requires GitHub authentication via browser.
EOF
}

case "${1:-}" in
--fg | --foreground)
	start_proxy true
	;;
--stop)
	stop_proxy
	;;
--status)
	show_status
	;;
--env)
	print_env
	;;
--help | -h)
	show_usage
	;;
"")
	start_proxy false
	;;
*)
	echo "Unknown option: $1"
	show_usage
	exit 1
	;;
esac
