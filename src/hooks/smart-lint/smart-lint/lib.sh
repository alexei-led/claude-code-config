#!/usr/bin/env bash
# Shared utilities for smart-lint modules: colors, logging, error collection, formatters.

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
CLAUDE_HOOKS_DEBUG="${CLAUDE_HOOKS_DEBUG:-0}"
PROJECT_TYPE="${PROJECT_TYPE:-unknown}"

log_debug() { [[ "$CLAUDE_HOOKS_DEBUG" == "1" ]] && echo -e "${CYAN}[DEBUG]${NC} $*" >&2; }
log_info() { echo -e "${BLUE}[INFO]${NC} $*" >&2; }
command_exists() { command -v "$1" &>/dev/null; }

declare -a ERRORS=()
add_error() {
	ERRORS+=("${RED}❌ $1${NC}\n$2")
}

print_summary_and_exit() {
	if [ ${#ERRORS[@]} -gt 0 ]; then
		echo -e "${RED}❌ ${#ERRORS[@]} blocking issue(s):${NC}" >&2
		for err in "${ERRORS[@]}"; do
			echo -e "$err" >&2
		done
		# Exit code 2 = blocking error in Claude Code hooks
		# Sends stderr to Claude for automatic processing and fixing
		# See: https://docs.claude.com/en/docs/claude-code/hooks
		exit 2
	else
		local total_words=0
		local w
		# CLAUDE.md + settings
		for f in ~/.claude/CLAUDE.md ~/.claude/settings.json; do
			[[ -f "$f" ]] && {
				w=$(wc -w <"$f" 2>/dev/null | tr -d ' ')
				total_words=$((total_words + w))
			}
		done
		# Commands, skills, agents
		shopt -s globstar 2>/dev/null
		for f in ~/.claude/commands/**/*.md \
			~/.claude/skills/*/SKILL.md ~/.claude/agents/**/*.md; do
			[[ -f "$f" ]] && {
				w=$(wc -w <"$f" 2>/dev/null | tr -d ' ')
				total_words=$((total_words + w))
			}
		done
		local approx_tokens=$((total_words * 4 / 3))
		echo -e "${PROJECT_TYPE} project ${GREEN}✅ Style OK${NC} ${CYAN}📊 ~${approx_tokens} tokens${NC}" >&2
		exit 0
	fi
}

get_changed_files() {
	# Usage: get_changed_files ".go" or get_changed_files ".js" ".ts" ".jsx" ".tsx"
	local extensions=("$@")

	if ! git rev-parse --git-dir >/dev/null 2>&1; then
		return
	fi

	local exclude_patterns=(
		"node_modules/"
		"vendor/"
		"venv/"
		".venv/"
		"env/"
		"virtualenv/"
		"dist/"
		"build/"
		"target/"
		".tox/"
		".eggs/"
		"__pycache__/"
		".pytest_cache/"
		".mypy_cache/"
		".cargo/"
		".next/"
		".nuxt/"
		"coverage/"
	)

	# ACMRTUXB = Added, Copied, Modified, Renamed, Type-changed, Unmerged, Unknown, Broken
	# Exclude D (Deleted) as those files don't exist to lint
	{
		git diff --name-only --diff-filter=ACMRTUXB --cached HEAD 2>/dev/null || true
		git diff --name-only --diff-filter=ACMRTUXB 2>/dev/null || true
		git ls-files --others --exclude-standard 2>/dev/null || true
	} | sort -u | while IFS= read -r file; do
		if [[ -n "$file" && -f "$file" ]]; then
			local skip=0
			for pattern in "${exclude_patterns[@]}"; do
				if [[ "$file" == *"$pattern"* ]]; then
					skip=1
					break
				fi
			done
			if [[ $skip -eq 0 ]]; then
				for ext in "${extensions[@]}"; do
					if [[ "$file" == *"$ext" ]]; then
						echo "$file"
						break
					fi
				done
			fi
		fi
	done
}

run_formatter_on_files() {
	local name="$1" format_cmd="$2" check_cmd="$3"
	shift 3
	local files=("$@")

	if [[ "${#files[@]}" -eq 0 ]]; then
		log_debug "No files to format, skipping $name"
		return 0
	fi

	log_debug "Running $name on files: ${files[*]}"

	# Format files
	$format_cmd "${files[@]}" >/dev/null 2>&1

	# Check if issues remain
	if output=$($check_cmd "${files[@]}" 2>&1); then
		return 0 # All good
	else
		add_error "$name needs fixing" "$output"
	fi
}

run_linter() {
	local name="$1"
	shift
	if output=$("$@" 2>&1); then
		log_debug "$name passed."
		return 0
	else
		add_error "$name found issues" "$output"
	fi
}
