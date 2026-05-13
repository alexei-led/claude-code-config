#!/usr/bin/env bash
# notify.sh - Notification hook for AI coding agents (Claude Code, Pi, Codex, Gemini)
#
# Input JSON fields (common): title, message, notification_type, session_id, cwd
# Input JSON fields (CC only): transcript_path, permission_mode
#
# Env vars used:
#   CLAUDE_CODE_VERSION                            - Claude Code detection (title fallback)
#   KITTY_LISTEN_ON, KITTY_PID, KITTY_WINDOW_ID  - kitty detection + navigation
#   TMUX_PANE                                      - tmux pane navigation
#   TERM_PROGRAM                                   - fallback terminal detection
#   CLAUDE_TERMINAL_BUNDLE_ID                      - manual override (all agents)

set -uo pipefail

# --- Parse input ---
json_input="${1:-$(cat)}"

title=$(echo "$json_input" | jq -r '.title // ""')
message=$(echo "$json_input" | jq -r '.message // "Done"')
cwd=$(echo "$json_input" | jq -r '.cwd // ""')
notification_type=$(echo "$json_input" | jq -r '.notification_type // ""')
session_id=$(echo "$json_input" | jq -r '.session_id // ""')
permission_mode=$(echo "$json_input" | jq -r '.permission_mode // ""')

# --- Agent name: JSON title → env detection → generic fallback ---
if [[ -z "$title" ]]; then
	if [[ -n "${CLAUDE_CODE_VERSION:-}" ]]; then
		title="Claude Code"
	else
		title="Agent"
	fi
fi

# Slug for -group: lowercase, spaces → hyphens (e.g. "Claude Code" → "claude-code")
agent_slug=$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

# --- Title: prepend project name ---
if [[ -n "$cwd" ]]; then
	title="[$(basename "$cwd")] $title"
fi

# --- Git context: branch for subtitle, last commit for idle message ---
git_branch=""
git_last_commit=""
if [[ -n "$cwd" && -d "$cwd/.git" ]]; then
	git_branch=$(git -C "$cwd" branch --show-current 2>/dev/null || true)
	git_last_commit=$(git -C "$cwd" log --oneline -1 2>/dev/null | sed 's/^[a-f0-9]* //' || true)
fi

# --- Emoji prefix + subtitle by type ---
subtitle=""
case "$notification_type" in
permission_prompt)
	title="🔐 $title"
	if [[ -n "$permission_mode" && "$permission_mode" != "default" ]]; then
		subtitle="Permission required · $permission_mode mode"
	else
		subtitle="Action required"
	fi
	;;
idle_prompt)
	title="💤 $title"
	subtitle="Waiting for input"
	[[ -n "$git_branch" ]] && subtitle="$subtitle · $git_branch"
	# Replace generic agent message with last commit subject (more useful context)
	[[ -n "$git_last_commit" ]] && message="$git_last_commit"
	;;
esac

# --- Sound by type ---
sound_flag=()
case "$notification_type" in
permission_prompt) sound_flag=(-sound Funk) ;;
idle_prompt) sound_flag=(-sound default) ;;
esac

# --- Fallback if no terminal-notifier ---
if ! command -v terminal-notifier &>/dev/null; then
	echo "📢 $title: $message" >&2
	exit 0
fi

# --- Resolve tool paths (needed for -execute which runs in minimal-PATH /bin/sh) ---
kitty_bin=$(command -v kitty 2>/dev/null || echo "/opt/homebrew/bin/kitty")
tmux_bin=$(command -v tmux 2>/dev/null || echo "/opt/homebrew/bin/tmux")

# --- Detect parent terminal via kitty socket ---
kitty_socket=""
if [[ -n "${KITTY_LISTEN_ON:-}" ]]; then
	kitty_socket="$KITTY_LISTEN_ON"
elif [[ -n "${KITTY_PID:-}" ]]; then
	kitty_socket="unix:/tmp/kitty-${KITTY_PID}"
fi
kitty_socket_path="${kitty_socket#unix:}"

if [[ -n "$kitty_socket" && -S "$kitty_socket_path" ]]; then
	BUNDLE_ID="net.kovidgoyal.kitty"
else
	case "${TERM_PROGRAM:-}" in
	iTerm.app) BUNDLE_ID="com.googlecode.iterm2" ;;
	WezTerm) BUNDLE_ID="com.github.wez.wezterm" ;;
	Alacritty) BUNDLE_ID="org.alacritty" ;;
	kitty) BUNDLE_ID="net.kovidgoyal.kitty" ;;
	*) BUNDLE_ID="com.apple.Terminal" ;;
	esac
fi
BUNDLE_ID="${CLAUDE_TERMINAL_BUNDLE_ID:-$BUNDLE_ID}"

# --- Build click-to-navigate command (kitty + tmux) ---
execute_cmd=""
if [[ -n "$kitty_socket" && -S "$kitty_socket_path" ]]; then
	nav_parts=("/usr/bin/open -b net.kovidgoyal.kitty")

	if [[ -n "${KITTY_WINDOW_ID:-}" ]]; then
		nav_parts+=("${kitty_bin} @ --to ${kitty_socket} focus-tab -m window_id:${KITTY_WINDOW_ID} 2>/dev/null")
	fi

	if [[ -n "${TMUX_PANE:-}" ]]; then
		nav_parts+=("${tmux_bin} select-pane -t ${TMUX_PANE} 2>/dev/null")
	fi

	execute_cmd=$(printf '%s; ' "${nav_parts[@]}")
	execute_cmd="${execute_cmd%; }"
fi

# --- Send notification ---
tn_args=(
	-title "$title"
	-message "$message"
	-activate "$BUNDLE_ID"
)
[[ -n "$subtitle" ]] && tn_args+=(-subtitle "$subtitle")
[[ -n "$session_id" ]] && tn_args+=(-group "${agent_slug}-${session_id}")
[[ ${#sound_flag[@]} -gt 0 ]] && tn_args+=("${sound_flag[@]}")
[[ -n "$execute_cmd" ]] && tn_args+=(-execute "$execute_cmd")

terminal-notifier "${tn_args[@]}" 2>/dev/null ||
	echo "📢 $title: $message" >&2
