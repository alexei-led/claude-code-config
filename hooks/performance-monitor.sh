#!/usr/bin/env bash
# performance-monitor.sh - Monitor Claude Code performance metrics with historical tracking
#
# DESCRIPTION
#   Tracks token usage, context length, and provides optimization insights.
#   Stores historical metrics for trend analysis.
#
# USAGE
#   ./performance-monitor.sh           # Run analysis and save metrics
#   ./performance-monitor.sh --history # Show historical trends
#   ./performance-monitor.sh --json    # Output as JSON
#
# EXIT CODES
#   0 - Success, metrics gathered
#   1 - Error in monitoring

set -euo pipefail

# --- CONFIGURATION ---
CONFIG_FILE="$HOME/.claude/hook-config.json"
METRICS_DIR="$HOME/.claude/metrics"
METRICS_FILE="$METRICS_DIR/history.jsonl"

# Load config or use defaults
if [[ -f "$CONFIG_FILE" ]] && command -v jq &>/dev/null; then
	CONTEXT_WARNING=$(jq -r '.performanceMonitor.contextWarningThreshold // 0.10' "$CONFIG_FILE")
	LARGE_FILE_THRESHOLD=$(jq -r '.performanceMonitor.largeFileThreshold // 1000' "$CONFIG_FILE")
	MAX_COMMANDS_WARNING=$(jq -r '.performanceMonitor.maxCommandsWarning // 10' "$CONFIG_FILE")
	RETENTION_DAYS=$(jq -r '.performanceMonitor.metricsRetentionDays // 30' "$CONFIG_FILE")
else
	CONTEXT_WARNING=0.10
	LARGE_FILE_THRESHOLD=1000
	MAX_COMMANDS_WARNING=10
	RETENTION_DAYS=30
fi

# --- UTILITIES ---
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# Ensure metrics directory exists
mkdir -p "$METRICS_DIR"

# --- METRICS COLLECTION ---
collect_metrics() {
	local config_files=(
		~/.claude/CLAUDE.md
		~/.claude/settings.json
	)

	local total_words=0
	local total_lines=0
	local largest_file=""
	local largest_size=0

	for file in "${config_files[@]}"; do
		if [[ -f "$file" ]]; then
			local words lines
			words=$(wc -w <"$file" 2>/dev/null | tr -d ' ' || echo 0)
			lines=$(wc -l <"$file" 2>/dev/null | tr -d ' ' || echo 0)
			total_words=$((total_words + words))
			total_lines=$((total_lines + lines))

			if [[ $words -gt $largest_size ]]; then
				largest_size=$words
				largest_file=$(basename "$file")
			fi
		fi
	done

	# Count commands and skills
	local command_count skill_count agent_count hook_count
	command_count=$(find ~/.claude/commands -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
	skill_count=$(find ~/.claude/skills -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
	agent_count=$(find ~/.claude/agents -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
	hook_count=$(find ~/.claude/hooks -name "*.sh" 2>/dev/null | wc -l | tr -d ' ')

	# Token estimation
	local approx_tokens=$((total_words * 4 / 3))
	local context_percentage=$((approx_tokens * 100 / 200000))

	# Output as JSON
	cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "tokens": $approx_tokens,
  "words": $total_words,
  "lines": $total_lines,
  "contextPercent": $context_percentage,
  "largestFile": "$largest_file",
  "largestSize": $largest_size,
  "commands": $command_count,
  "skills": $skill_count,
  "agents": $agent_count,
  "hooks": $hook_count
}
EOF
}

# --- SAVE METRICS ---
save_metrics() {
	local metrics
	metrics=$(collect_metrics)
	echo "$metrics" >>"$METRICS_FILE"

	# Cleanup old entries (keep last N days)
	if [[ -f "$METRICS_FILE" ]]; then
		local cutoff_date
		cutoff_date=$(date -v-"${RETENTION_DAYS}"d +%Y-%m-%d 2>/dev/null || date -d "${RETENTION_DAYS} days ago" +%Y-%m-%d 2>/dev/null || echo "")
		if [[ -n "$cutoff_date" ]]; then
			local temp_file="${METRICS_FILE}.tmp"
			jq -c "select(.timestamp >= \"$cutoff_date\")" "$METRICS_FILE" >"$temp_file" 2>/dev/null || true
			mv "$temp_file" "$METRICS_FILE" 2>/dev/null || true
		fi
	fi

	echo "$metrics"
}

# --- DISPLAY ANALYSIS ---
display_analysis() {
	local metrics
	metrics=$(collect_metrics)

	echo -e "${CYAN}📊 Claude Code Performance Analysis${NC}"
	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

	local tokens words lines context_pct largest_file largest_size
	tokens=$(echo "$metrics" | jq -r '.tokens')
	words=$(echo "$metrics" | jq -r '.words')
	lines=$(echo "$metrics" | jq -r '.lines')
	context_pct=$(echo "$metrics" | jq -r '.contextPercent')
	largest_file=$(echo "$metrics" | jq -r '.largestFile')
	largest_size=$(echo "$metrics" | jq -r '.largestSize')

	echo -e "\n${CYAN}Context Usage:${NC}"
	echo -e "  Tokens:     ~${tokens} (~${context_pct}% of 200K limit)"
	echo -e "  Words:      ${words}"
	echo -e "  Lines:      ${lines}"
	echo -e "  Largest:    ${largest_file} (${largest_size} words)"

	echo -e "\n${CYAN}Components:${NC}"
	echo -e "  Commands:   $(echo "$metrics" | jq -r '.commands')"
	echo -e "  Skills:     $(echo "$metrics" | jq -r '.skills')"
	echo -e "  Agents:     $(echo "$metrics" | jq -r '.agents')"
	echo -e "  Hooks:      $(echo "$metrics" | jq -r '.hooks')"

	echo -e "\n${CYAN}Optimization Insights:${NC}"

	local warning_threshold_pct=$((${CONTEXT_WARNING%.*} * 100))
	if [[ $context_pct -gt $warning_threshold_pct ]]; then
		echo -e "${YELLOW}⚠️  High context usage (${context_pct}%) - consider trimming verbose content${NC}"
	else
		echo -e "${GREEN}✅ Context usage is efficient${NC}"
	fi

	if [[ $largest_size -gt $LARGE_FILE_THRESHOLD ]]; then
		echo -e "${YELLOW}⚠️  Large file: ${largest_file} (${largest_size} words)${NC}"
	else
		echo -e "${GREEN}✅ File sizes are reasonable${NC}"
	fi

	local cmd_count
	cmd_count=$(echo "$metrics" | jq -r '.commands')
	if [[ $cmd_count -gt $MAX_COMMANDS_WARNING ]]; then
		echo -e "${YELLOW}⚠️  Many commands (${cmd_count}) - consider consolidation${NC}"
	else
		echo -e "${GREEN}✅ Command count is optimal${NC}"
	fi

	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# --- HISTORICAL TRENDS ---
display_history() {
	if [[ ! -f "$METRICS_FILE" ]]; then
		echo -e "${YELLOW}No historical data yet. Run without --history to collect metrics.${NC}"
		exit 0
	fi

	echo -e "${CYAN}📈 Historical Metrics (Last ${RETENTION_DAYS} days)${NC}"
	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

	local entry_count
	entry_count=$(wc -l <"$METRICS_FILE" | tr -d ' ')
	echo -e "Total entries: ${entry_count}"

	if [[ $entry_count -gt 0 ]]; then
		echo -e "\n${CYAN}Token Usage Trend:${NC}"
		# Show last 10 entries
		tail -10 "$METRICS_FILE" | while IFS= read -r line; do
			local ts tokens pct
			ts=$(echo "$line" | jq -r '.timestamp' | cut -d'T' -f1)
			tokens=$(echo "$line" | jq -r '.tokens')
			pct=$(echo "$line" | jq -r '.contextPercent')
			printf "  %s: %6d tokens (%2d%%)\n" "$ts" "$tokens" "$pct"
		done

		echo -e "\n${CYAN}Statistics:${NC}"
		local avg_tokens min_tokens max_tokens
		avg_tokens=$(jq -s '[.[].tokens] | add / length | floor' "$METRICS_FILE" 2>/dev/null || echo "N/A")
		min_tokens=$(jq -s '[.[].tokens] | min' "$METRICS_FILE" 2>/dev/null || echo "N/A")
		max_tokens=$(jq -s '[.[].tokens] | max' "$METRICS_FILE" 2>/dev/null || echo "N/A")
		echo -e "  Average: ${avg_tokens} tokens"
		echo -e "  Min:     ${min_tokens} tokens"
		echo -e "  Max:     ${max_tokens} tokens"
	fi

	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# --- MAIN EXECUTION ---
main() {
	case "${1:-}" in
	--history)
		display_history
		;;
	--json)
		save_metrics
		;;
	*)
		display_analysis
		save_metrics >/dev/null
		echo -e "\n${GREEN}✅ Metrics saved to ${METRICS_FILE}${NC}"
		;;
	esac
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
	main "$@"
fi
