#!/usr/bin/env bash
# CLIProxyAPI for Claude Code - Codex and Gemini subscriptions
# Wraps cliproxyapi to provide OAuth-based access to GPT-5/Gemini models
#
# Usage:
#   cliproxy.sh                  # Start proxy in background
#   cliproxy.sh --fg             # Start in foreground
#   cliproxy.sh --stop           # Stop running proxy
#   cliproxy.sh --status         # Check if proxy is running
#   cliproxy.sh --login-codex    # OAuth login for Codex subscription
#   cliproxy.sh --login-gemini   # OAuth login for Gemini subscription
#   cliproxy.sh --import-gemini  # Import from existing Gemini CLI creds

set -euo pipefail

# Port configured in /opt/homebrew/etc/cliproxyapi.conf (default 8317)
PORT="${CLIPROXY_PORT:-8317}"
PID_FILE="${TMPDIR:-/tmp}/cliproxy.pid"
LOG_FILE="${TMPDIR:-/tmp}/cliproxy.log"
# Auth dir configured in cliproxyapi.conf as auth-dir: "~/.cli-proxy-api"
AUTH_DIR="${HOME}/.cli-proxy-api"

check_binary() {
	if ! command -v cliproxyapi >/dev/null 2>&1; then
		echo "❌ cliproxyapi not found"
		echo ""
		echo "Install: brew install cliproxyapi"
		exit 1
	fi
}

is_running() {
	[[ -f "$PID_FILE" ]] || return 1
	local pid
	pid=$(<"$PID_FILE") 2>/dev/null || return 1
	kill -0 "$pid" 2>/dev/null
}

start_proxy() {
	local foreground="${1:-false}"

	check_binary

	if is_running; then
		echo "CLIProxyAPI already running (PID: $(<"$PID_FILE"))"
		echo "Use 'cliproxy.sh --stop' to stop it first"
		exit 1
	fi

	# Check if any auth exists
	if [[ ! -d "$AUTH_DIR" ]] || [[ -z "$(ls -A "$AUTH_DIR" 2>/dev/null)" ]]; then
		echo "⚠️  No OAuth credentials found in $AUTH_DIR"
		echo ""
		echo "Login first:"
		echo "  cliproxy.sh --login-codex   # For Codex/GPT subscription"
		echo "  cliproxy.sh --login-gemini  # For Gemini subscription"
		exit 1
	fi

	echo "Starting CLIProxyAPI on port $PORT..."

	if [[ "$foreground" == "true" ]]; then
		exec cliproxyapi
	else
		nohup cliproxyapi >"$LOG_FILE" 2>&1 &

		echo "$!" >"$PID_FILE"
		sleep 2

		if is_running; then
			echo "✅ Proxy started (PID: $(<"$PID_FILE"))"
			echo "   Port: $PORT"
			echo "   Logs: $LOG_FILE"
			echo "   Auth: $AUTH_DIR"
		else
			echo "❌ Failed to start proxy. Check logs: $LOG_FILE"
			tail -20 "$LOG_FILE" 2>/dev/null || :
			exit 1
		fi
	fi
}

stop_proxy() {
	if [[ -f "$PID_FILE" ]]; then
		local pid
		pid=$(<"$PID_FILE") 2>/dev/null || {
			echo "Failed to read PID file, cleaning up"
			rm -f "$PID_FILE"
			return
		}
		if kill -0 "$pid" 2>/dev/null; then
			echo "Stopping CLIProxyAPI (PID: $pid)..."
			kill "$pid"
			rm -f "$PID_FILE"
			echo "✅ Proxy stopped"
		else
			echo "Process not running, cleaning up PID file"
			rm -f "$PID_FILE"
		fi
	else
		echo "No PID file found. Proxy may not be running."
		if pkill -f "cliproxyapi" 2>/dev/null; then echo "Killed orphan proxy process"; fi
	fi
}

show_status() {
	if is_running; then
		echo "✅ CLIProxyAPI is running (PID: $(<"$PID_FILE"))"
		echo "   Port: $PORT"
		echo "   Logs: $LOG_FILE"

		if curl -s --max-time 2 "http://localhost:$PORT" >/dev/null 2>&1; then
			echo "   Health: OK"
		else
			echo "   Health: Not responding (may still be starting)"
		fi

		# Show available OAuth sessions
		echo ""
		echo "OAuth sessions:"
		if [[ -d "$AUTH_DIR" ]]; then
			local found=false
			for auth_file in "$AUTH_DIR"/*; do
				[[ -e "$auth_file" ]] || continue
				if [[ -f "$auth_file" ]]; then
					echo "   ✓ $(basename "$auth_file")"
					found=true
				fi
			done
			$found || echo "   (none)"
		else
			echo "   (none)"
		fi
	else
		echo "❌ CLIProxyAPI is not running"
	fi
}

login_codex() {
	check_binary
	echo "Starting Codex OAuth login..."
	echo "A browser window will open for GitHub/OpenAI authentication."
	echo ""
	if ! cliproxyapi -codex-login; then
		echo "❌ Codex login failed"
		exit 1
	fi
	echo ""
	echo "✅ Codex credentials saved to $AUTH_DIR"
}

login_gemini() {
	check_binary
	echo "Starting Gemini OAuth login..."
	echo "A browser window will open for Google authentication."
	echo ""
	if ! cliproxyapi -login; then
		echo "❌ Gemini login failed"
		exit 1
	fi
	echo ""
	echo "✅ Gemini credentials saved to $AUTH_DIR"
}

import_gemini() {
	local script_dir
	script_dir="$(cd "$(dirname "$0")" && pwd)"
	echo "Importing Gemini CLI credentials into CLIProxyAPI..."
	echo ""
	if ! python3 "${script_dir}/cliproxy-import-gemini.py" "$@"; then
		echo "❌ Import failed"
		exit 1
	fi
}

show_usage() {
	cat <<EOF
CLIProxyAPI for Claude Code

Provides OAuth-based access to Codex (GPT-5) and Gemini models.

Usage:
  cliproxy.sh [OPTIONS]

Options:
  (none)          Start proxy in background
  --fg            Start proxy in foreground
  --stop          Stop running proxy
  --status        Check proxy status
  --login-codex   OAuth login for Codex/GPT subscription
  --login-gemini  OAuth login for Gemini subscription
  --import-gemini Import from existing Gemini CLI credentials
  --help          Show this help

Config: /opt/homebrew/etc/cliproxyapi.conf
  Port: $PORT (edit 'port:' in config to change)
  Auth: $AUTH_DIR

Models (from active model profile, see: ce --show-models):
  Codex:  ce --show-models --json | ... .codex
  Gemini: ce --show-models --json | ... .gemini

First-time setup:
  1. Install: brew install cliproxyapi
  2. Login:   cliproxy.sh --login-codex    # or --login-gemini
             cliproxy.sh --import-gemini  # alt: import from Gemini CLI
  3. Start:   cliproxy.sh
  4. Use:     ce codex  # or: ce gemini
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
--login-codex)
	login_codex
	;;
--login-gemini)
	login_gemini
	;;
--import-gemini)
	shift
	import_gemini "$@"
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
