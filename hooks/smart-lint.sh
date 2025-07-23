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
    echo -e "────────────────────────────────────────────" >&2
    if [ ${#ERRORS[@]} -gt 0 ]; then
        echo -e "${RED}🛑 FAILED - Fix ${#ERRORS[@]} blocking issue(s):${NC}" >&2
        for err in "${ERRORS[@]}"; do
            echo -e "\n$err" >&2
        done
        echo -e "\n${YELLOW}Run linters locally, fix issues, then proceed.${NC}" >&2
    else
        echo -e "${GREEN}✅ Style OK${NC} | Code is clean. Continue with your task." >&2
    fi
    exit 2 # Always exit 2 to show output to Claude
}

# --- LINTER HELPERS ---
run_formatter() {
    local name="$1" cmd="$2" check_cmd="$3"
    log_debug "Running $name formatter..."
    # First, try to fix silently
    $cmd >/dev/null 2>&1
    # Then, check if issues remain
    if output=$($check_cmd 2>&1); then
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
    # Rust project
    if [[ -f "Cargo.toml" ]] || [[ -n "$(find . -maxdepth 3 -name "*.rs" -type f -print -quit 2>/dev/null)" ]]; then
        types+=("rust")
    fi
    # Nix project
    if [[ -f "flake.nix" ]] || [[ -f "default.nix" ]] || [[ -f "shell.nix" ]]; then
        types+=("nix")
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
    log_info "Running Go checks..."
    if [[ -f "Makefile" ]] && grep -q -E "^lint:" Makefile; then
        run_linter "Go (make lint)" make lint
    else
        command_exists gofmt && run_formatter "Go Formatter (gofmt)" "gofmt -w ." "gofmt -l ."
        if command_exists golangci-lint; then
            run_golangci_lint
        elif command_exists go; then
            run_linter "Go (go vet)" go vet ./...
        fi
    fi
}

lint_python() {
    log_info "Running Python checks..."
    command_exists black && run_formatter "Python Formatter (black)" "black ." "black . --check"
    if command_exists ruff; then
        run_linter "Python Linter (ruff)" ruff check --fix .
    elif command_exists flake8; then
        run_linter "Python Linter (flake8)" flake8 .
    fi
}

lint_javascript() {
    log_info "Running JS/TS checks..."
    local pm="npm"
    [[ -f "yarn.lock" ]] && pm="yarn"
    [[ -f "pnpm-lock.yaml" ]] && pm="pnpm"

    if command_exists prettier || command_exists npx; then
        run_formatter "JS Formatter (prettier)" "npx prettier --write ." "npx prettier --check ."
    fi
    if grep -q '"lint":' package.json 2>/dev/null; then
        run_linter "JS Linter (eslint)" "$pm" run lint --if-present
    fi
}

lint_rust() {
    log_info "Running Rust checks..."
    if ! command_exists cargo; then log_debug "cargo not found"; return; fi
    run_formatter "Rust Formatter (cargo fmt)" "cargo fmt" "cargo fmt -- --check"
    run_linter "Rust Linter (clippy)" cargo clippy -- -D warnings
}

lint_nix() {
    log_info "Running Nix checks..."
    local formatter
    command_exists alejandra && formatter="alejandra"
    command_exists nixpkgs-fmt && formatter="nixpkgs-fmt"

    if [[ -n "$formatter" ]]; then
        run_formatter "Nix Formatter ($formatter)" "$formatter ." "$formatter . --check"
    fi
    command_exists statix && run_linter "Nix Linter (statix)" statix check .
}

# --- MAIN EXECUTION ---
[[ "$1" == "--debug" ]] && export CLAUDE_HOOKS_DEBUG=1

echo "🔍 Style Check - Validating code..." >&2

# Project-specific config overrides
[[ -f ".claude-hooks-config.sh" ]] && source ".claude-hooks-config.sh"

PROJECT_TYPE=$(detect_project_type)
log_info "Detected project type: $PROJECT_TYPE"

if [[ "$PROJECT_TYPE" == "unknown" ]]; then
    log_info "No recognized project type, skipping."
    print_summary_and_exit
fi

# Run linters based on detected types
IFS=',' read -ra types <<< "${PROJECT_TYPE#mixed:}"
for type in "${types[@]}"; do
    case "$type" in
        go) lint_go ;;
        python) lint_python ;;
        javascript) lint_javascript ;;
        rust) lint_rust ;;
        nix) lint_nix ;;
    esac
done

print_summary_and_exit
