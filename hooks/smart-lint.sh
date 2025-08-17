#!/usr/bin/env bash
# smart-lint.sh - Concise, project-aware code quality checks.
#
# DESCRIPTION
#   Auto-detects project type and runs formatters and linters.
#   All issues are blocking; the script attempts to auto-fix where possible.
#
# OPTIONS
#   --debug       Enable debug output.
#
# EXIT CODES
#   2 - Always exits with 2 to show output to the Claude agent.
#       The content of the output indicates success or failure.

set -o pipefail
set +e

# --- UTILITIES ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
CLAUDE_HOOKS_DEBUG="${CLAUDE_HOOKS_DEBUG:-0}"

log_debug() { [[ "$CLAUDE_HOOKS_DEBUG" == "1" ]] && echo -e "${CYAN}[DEBUG]${NC} $*" >&2; }
log_info() { echo -e "${BLUE}[INFO]${NC} $*" >&2; }
command_exists() { command -v "$1" &>/dev/null; }

# --- ERROR & SUMMARY ---
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
    else
        # Include token monitoring inline
        local context_files=( ~/.claude/CLAUDE.md ~/.claude/commands/@*.md ~/.claude/settings.json )
        local total_words=0
        for file in "${context_files[@]}"; do
            if [[ -f "$file" ]]; then
                local words
                words=$(wc -w < "$file" 2>/dev/null || echo 0)
                total_words=$((total_words + words))
            fi
        done
        local approx_tokens=$((total_words * 4 / 3))
        echo -e "${PROJECT_TYPE} project ${GREEN}✅ Style OK${NC} ${CYAN}📊 ~${approx_tokens} tokens${NC}" >&2
    fi
    exit 2 # Always exit 2 to show output to Claude
}

# --- CHANGED FILES DETECTION ---
get_changed_files() {
    # Usage: get_changed_files ".go" or get_changed_files ".js" ".ts" ".jsx" ".tsx"
    local extensions=("$@")
    
    # If not in git repo, return empty
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        return
    fi
    
    # Get modified and untracked files
    local changed_files
    changed_files=$(git status --porcelain 2>/dev/null | grep -E '^[AM?]' | cut -c4- || echo "")
    
    # Filter by extensions and return existing files
    while IFS= read -r file; do
        if [[ -n "$file" && -f "$file" ]]; then
            for ext in "${extensions[@]}"; do
                if [[ "$file" == *"$ext" ]]; then
                    echo "$file"
                    break
                fi
            done
        fi
    done <<< "$changed_files"
}

# --- FORMATTER HELPERS ---
run_formatter_on_files() {
    local name="$1" format_cmd="$2" check_cmd="$3"; shift 3
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
    local name="$1"; shift
    if output=$("$@" 2>&1); then
        log_debug "$name passed."
        return 0
    else
        add_error "$name found issues" "$output"
    fi
}

# --- PROJECT DETECTION ---
detect_project_type() {
    local project_type="unknown"
    local types=()
    
    # Go project
    if [[ -f "go.mod" ]] || [[ -f "go.sum" ]] || [[ -n "$(find . -maxdepth 3 -name "*.go" -type f -print -quit 2>/dev/null)" ]]; then
        types+=("go")
    fi
    # Python project
    if [[ -f "pyproject.toml" ]] || [[ -f "setup.py" ]] || [[ -f "requirements.txt" ]] || [[ -n "$(find . -maxdepth 3 -name "*.py" -type f -print -quit 2>/dev/null)" ]]; then
        types+=("python")
    fi
    # JavaScript/TypeScript project
    if [[ -f "package.json" ]] || [[ -f "tsconfig.json" ]] || [[ -n "$(find . -maxdepth 3 \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" \) -type f -print -quit 2>/dev/null)" ]]; then
        types+=("javascript")
    fi
    # YAML files
    if [[ -n "$(find . -maxdepth 3 \( -name "*.yaml" -o -name "*.yml" \) -type f -print -quit 2>/dev/null)" ]]; then
        types+=("yaml")
    fi
    # JSON files
    if [[ -n "$(find . -maxdepth 3 -name "*.json" -type f -print -quit 2>/dev/null)" ]]; then
        types+=("json")
    fi
    # Shell scripts
    if [[ -n "$(find . -maxdepth 3 \( -name "*.sh" -o -name "*.bash" \) -type f -print -quit 2>/dev/null)" ]]; then
        types+=("shell")
    fi
    # GitHub Actions
    if [[ -d ".github/workflows" ]]; then
        types+=("github_actions")
    fi
    # Terraform
    if [[ -n "$(find . -maxdepth 3 \( -name "*.tf" -o -name "*.tfvars" \) -type f -print -quit 2>/dev/null)" ]]; then
        types+=("terraform")
    fi
    # Markdown files
    if [[ -n "$(find . -maxdepth 3 -name "*.md" -type f -print -quit 2>/dev/null)" ]]; then
        types+=("markdown")
    fi

    # Return primary type or "mixed" if multiple
    if [[ ${#types[@]} -eq 1 ]]; then
        project_type="${types[0]}"
    elif [[ ${#types[@]} -gt 1 ]]; then
        project_type="mixed:$(IFS=,; echo "${types[*]}")"
    fi
    log_debug "Detected project type: $project_type"
    echo "$project_type"
}

# --- LANGUAGE LINTERS ---

# Helper for version-aware golangci-lint execution
run_golangci_lint() {
    # Detect version and set appropriate flags
    local version
    version=$(golangci-lint version --short 2>/dev/null)
    local base_cmd=("golangci-lint" "run" "--fix" "--new")
    if [[ "$version" == 2* ]]; then
        log_debug "Detected golangci-lint v2 ($version), using --fast-only"
        base_cmd+=("--fast-only")
    else
        log_debug "Detected golangci-lint v1 ($version), using --fast"
        base_cmd+=("--fast")
    fi

    # Attempt 1: Run with default config
    local output
    output=$("${base_cmd[@]}" 2>&1)
    local exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        return 0 # Success
    fi

    # Attempt 2: If config error, retry with --no-config
    if echo "$output" | grep -q "Error: can't load config"; then
        log_info "Config error detected, retrying with --no-config..."
        output=$("${base_cmd[@]}" --no-config 2>&1)
        [[ $? -eq 0 ]] && return 0 # Success on retry
    fi

    # If we reach here, a real error occurred
    add_error "Go (golangci-lint)" "$output"
}

lint_go() {
    log_debug "go checks"
    if [[ -f "Makefile" ]] && grep -q -E "^lint:" Makefile; then
        run_linter "Go (make lint)" make lint
    else
        if command_exists gofmt; then
            local files=($(get_changed_files ".go"))
            run_formatter_on_files "Go Formatter (gofmt)" "gofmt -w" "gofmt -l" "${files[@]}"
        fi
        if command_exists golangci-lint; then
            run_golangci_lint
        elif command_exists go; then
            run_linter "Go (go vet)" go vet ./...
        fi
    fi
}

lint_python() {
    log_debug "python checks"
    if command_exists black; then
        local files=($(get_changed_files ".py"))
        run_formatter_on_files "Python Formatter (black)" "black" "black --check" "${files[@]}"
    fi
    if command_exists ruff; then
        run_linter "Python Linter (ruff)" ruff check --fix .
    elif command_exists flake8; then
        run_linter "Python Linter (flake8)" flake8 .
    fi
}

lint_javascript() {
    log_debug "js/ts checks"
    local pm="npm"
    [[ -f "yarn.lock" ]] && pm="yarn"
    [[ -f "pnpm-lock.yaml" ]] && pm="pnpm"

    if command_exists prettier || command_exists npx; then
        local files=($(get_changed_files ".js" ".ts" ".jsx" ".tsx"))
        run_formatter_on_files "JS Formatter (prettier)" "npx prettier --write" "npx prettier --check" "${files[@]}"
    fi
    if grep -q '"lint":' package.json 2>/dev/null; then
        run_linter "JS Linter (eslint)" "$pm" run lint --if-present
    fi
}

lint_yaml() {
    log_debug "yaml checks"
    if command_exists yq; then
        local files=($(get_changed_files ".yaml" ".yml"))
        run_formatter_on_files "YAML Formatter (yq)" "yq eval -P -i" "yq eval" "${files[@]}"
    fi
    if command_exists yamllint; then
        run_linter "YAML Linter (yamllint)" yamllint .
    fi
}

lint_json() {
    log_debug "json checks"
    if command_exists jq; then
        local files=($(get_changed_files ".json"))
        if [[ "${#files[@]}" -gt 0 ]]; then
            log_debug "Running JSON formatter on files: ${files[*]}"
            for file in "${files[@]}"; do
                if ! jq . "$file" > "${file}.tmp" 2>/dev/null; then
                    add_error "JSON Formatter (jq)" "Failed to format $file"
                else
                    mv "${file}.tmp" "$file"
                fi
            done
        fi
    elif command_exists prettier || command_exists npx; then
        local files=($(get_changed_files ".json"))
        run_formatter_on_files "JSON Formatter (prettier)" "npx prettier --write" "npx prettier --check" "${files[@]}"
    fi
}

lint_shell() {
    log_debug "shell checks"
    if command_exists shellcheck; then
        local files=($(get_changed_files ".sh" ".bash"))
        if [[ "${#files[@]}" -gt 0 ]]; then
            run_linter "Shell Linter (shellcheck)" shellcheck "${files[@]}"
        fi
    fi
    if command_exists shfmt; then
        local files=($(get_changed_files ".sh" ".bash"))
        run_formatter_on_files "Shell Formatter (shfmt)" "shfmt -w" "shfmt -d" "${files[@]}"
    fi
}

lint_github_actions() {
    log_debug "github actions checks"
    if command_exists actionlint && [[ -d ".github/workflows" ]]; then
        run_linter "GitHub Actions Linter (actionlint)" actionlint
    fi
}

lint_terraform() {
    log_debug "terraform checks"
    if command_exists terraform; then
        local files=($(get_changed_files ".tf" ".tfvars"))
        if [[ "${#files[@]}" -gt 0 ]]; then
            log_debug "Found changed Terraform files, running terraform fmt"
            if ! terraform fmt >/dev/null 2>&1; then
                add_error "Terraform Formatter" "terraform fmt failed"
            elif ! output=$(terraform fmt -check 2>&1); then
                add_error "Terraform Formatter needs fixing" "$output"
            fi
            # Run validate if we're in a terraform directory
            if [[ -f "main.tf" ]] || [[ -f "*.tf" ]]; then
                run_linter "Terraform Validator" terraform validate
            fi
        fi
    fi
    if command_exists tflint; then
        local files=($(get_changed_files ".tf" ".tfvars"))
        if [[ "${#files[@]}" -gt 0 ]]; then
            run_linter "Terraform Linter (tflint)" tflint
        fi
    fi
}

lint_markdown() {
    log_debug "markdown checks"
    if command_exists prettier || command_exists npx; then
        local files=($(get_changed_files ".md"))
        run_formatter_on_files "Markdown Formatter (prettier)" "npx prettier --write" "npx prettier --check" "${files[@]}"
    elif command_exists mdformat; then
        local files=($(get_changed_files ".md"))
        run_formatter_on_files "Markdown Formatter (mdformat)" "mdformat" "mdformat --check" "${files[@]}"
    fi
    if command_exists markdownlint-cli2; then
        local files=($(get_changed_files ".md"))
        if [[ "${#files[@]}" -gt 0 ]]; then
            run_linter "Markdown Linter (markdownlint-cli2)" markdownlint-cli2 "${files[@]}"
        fi
    elif command_exists markdownlint; then
        local files=($(get_changed_files ".md"))
        if [[ "${#files[@]}" -gt 0 ]]; then
            run_linter "Markdown Linter (markdownlint)" markdownlint "${files[@]}"
        fi
    fi
}


# --- MAIN EXECUTION ---
[[ "$1" == "--debug" ]] && export CLAUDE_HOOKS_DEBUG=1

# Project-specific config overrides
[[ -f ".claude-hooks-config.sh" ]] && source ".claude-hooks-config.sh"

PROJECT_TYPE=$(detect_project_type)

if [[ "$PROJECT_TYPE" == "unknown" ]]; then
    log_debug "No recognized project type, skipping."
    print_summary_and_exit
fi

# Run linters based on detected types
IFS=',' read -ra types <<< "${PROJECT_TYPE#mixed:}"
for type in "${types[@]}"; do
    case "$type" in
        go) lint_go ;;
        python) lint_python ;;
        javascript) lint_javascript ;;
        yaml) lint_yaml ;;
        json) lint_json ;;
        shell) lint_shell ;;
        github_actions) lint_github_actions ;;
        terraform) lint_terraform ;;
        markdown) lint_markdown ;;
    esac
done

print_summary_and_exit
