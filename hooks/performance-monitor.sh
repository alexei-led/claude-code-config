#!/usr/bin/env bash
# performance-monitor.sh - Monitor Claude Code performance metrics
#
# DESCRIPTION
#   Tracks token usage, context length, and provides optimization insights.
#   Can be called manually or integrated into workflows.
#
# EXIT CODES
#   0 - Success, metrics gathered
#   1 - Error in monitoring

set -euo pipefail

# --- UTILITIES ---
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# --- METRICS COLLECTION ---
analyze_context_usage() {
    echo -e "${CYAN}📊 Claude Code Performance Analysis${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Configuration files analysis
    local config_files=(
        ~/.claude/CLAUDE.md
        ~/.claude/settings.json
        ~/.claude/commands/@*.md
    )
    
    local total_words=0
    local total_lines=0
    local largest_file=""
    local largest_size=0
    
    echo -e "\n${CYAN}Context Files:${NC}"
    for pattern in "${config_files[@]}"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                local words lines
                words=$(wc -w < "$file" 2>/dev/null || echo 0)
                lines=$(wc -l < "$file" 2>/dev/null || echo 0)
                total_words=$((total_words + words))
                total_lines=$((total_lines + lines))
                
                if [[ $words -gt $largest_size ]]; then
                    largest_size=$words
                    largest_file=$(basename "$file")
                fi
                
                printf "  %-20s %6d words %4d lines\n" "$(basename "$file")" "$words" "$lines"
            fi
        done
    done
    
    # Token estimation (GPT-style: ~1.33 words per token)
    local approx_tokens=$((total_words * 4 / 3))
    local context_percentage=$((approx_tokens * 100 / 200000))  # Against 200k context limit
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}Total Context:${NC} ~${approx_tokens} tokens (${total_words} words, ${total_lines} lines)"
    echo -e "${GREEN}Context Usage:${NC} ~${context_percentage}% of 200K limit"
    echo -e "${GREEN}Largest File:${NC} ${largest_file} (${largest_size} words)"
    
    # Optimization recommendations
    echo -e "\n${CYAN}Optimization Insights:${NC}"
    if [[ $context_percentage -gt 10 ]]; then
        echo -e "${YELLOW}⚠️  High context usage (>${context_percentage}%) - consider trimming verbose commands${NC}"
    else
        echo -e "✅ Context usage is efficient"
    fi
    
    if [[ $largest_size -gt 1000 ]]; then
        echo -e "${YELLOW}⚠️  Large file detected: ${largest_file} - consider optimization${NC}"
    else
        echo -e "✅ File sizes are reasonable"
    fi
    
    # Command count analysis
    local command_count
    command_count=$(find ~/.claude/commands -name "@*.md" 2>/dev/null | wc -l)
    echo -e "📝 Active commands: ${command_count}"
    
    if [[ $command_count -gt 10 ]]; then
        echo -e "${YELLOW}⚠️  Many commands (${command_count}) - consider consolidation${NC}"
    else
        echo -e "✅ Command count is optimal"
    fi
}

# --- HOOK PERFORMANCE ---
analyze_hook_performance() {
    echo -e "\n${CYAN}Hook Performance:${NC}"
    
    local hook_files=(
        ~/.claude/hooks/smart-lint.sh
        ~/.claude/hooks/notify.sh
        ~/.claude/hooks/test-runner.sh
    )
    
    for hook in "${hook_files[@]}"; do
        if [[ -f "$hook" ]]; then
            local lines
            lines=$(wc -l < "$hook" 2>/dev/null || echo 0)
            printf "  %-20s %4d lines\n" "$(basename "$hook")" "$lines"
        fi
    done
}

# --- MAIN EXECUTION ---
main() {
    analyze_context_usage
    analyze_hook_performance
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✅ Performance analysis complete${NC}"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi