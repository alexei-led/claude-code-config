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

start_proxy() {
	local foreground="${1:-false}"

	if is_running; then
		echo "Copilot proxy already running (PID: $(cat "$PID_FILE"))"
		echo "Use 'copilot-proxy.sh --stop' to stop it first"
		exit 1
	fi

	echo "Starting Copilot API proxy on port $PORT..."
	echo "Models: claude-opus-4.5, claude-sonnet-4.5, claude-haiku-4.5"

	if [[ "$foreground" == "true" ]]; then
		exec bunx copilot-api@latest start \
			--claude-code \
			--port "$PORT"
	else
		nohup bunx copilot-api@latest start \
			--claude-code \
			--port "$PORT" \
			>"$LOG_FILE" 2>&1 &

		echo $! >"$PID_FILE"
		sleep 2

		if is_running; then
			echo "✅ Proxy started (PID: $(cat "$PID_FILE"))"
			echo "   Logs: $LOG_FILE"
			echo ""
			echo "Configure Claude Code with:"
			echo "  ANTHROPIC_BASE_URL=http://localhost:$PORT"
		else
			echo "❌ Failed to start proxy. Check logs: $LOG_FILE"
			exit 1
		fi
	fi
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
		pkill -f "copilot-api.*start" 2>/dev/null && echo "Killed orphan proxy process" || true
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
	cat <<'EOF'
Copilot API Proxy for Claude Code

Usage:
  copilot-proxy.sh [OPTIONS]

Options:
  (none)      Start proxy in background
  --fg        Start proxy in foreground (for debugging)
  --stop      Stop running proxy
  --status    Check proxy status
  --help      Show this help

Environment:
  COPILOT_PROXY_PORT  Port to run on (default: 4141)

Models mapped:
  claude-opus-4.5    → gpt-4.1 (via Copilot)
  claude-sonnet-4.5  → gpt-4.1 (via Copilot)
  claude-haiku-4.5   → gpt-4.1 (via Copilot)

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
