#!/usr/bin/env bash
# .claude-hooks-config.sh - Project-specific hook configuration
#
# This file allows you to override default hook behavior for your project.
# Copy this to your project root and modify as needed.

# ============================================================================
# GENERAL SETTINGS
# ============================================================================

# Enable/disable all hooks (true/false)
export CLAUDE_HOOKS_ENABLED=true

# Fail on first error instead of collecting all issues (true/false)
export CLAUDE_HOOKS_FAIL_FAST=false

# Show timing information for each check (true/false)
export CLAUDE_HOOKS_SHOW_TIMING=false

# Enable debug output (true/false)
export CLAUDE_HOOKS_DEBUG=false

# ============================================================================
# LANGUAGE-SPECIFIC SETTINGS
# ============================================================================

# Go settings
export CLAUDE_HOOKS_GO_ENABLED=true
export CLAUDE_HOOKS_GO_EXTRA_CHECKS=""  # e.g., "staticcheck"

# Python settings
export CLAUDE_HOOKS_PYTHON_ENABLED=true
export CLAUDE_HOOKS_PYTHON_FORMATTER="black"  # or "yapf", "autopep8"
export CLAUDE_HOOKS_PYTHON_LINTER="ruff"      # or "flake8", "pylint"

# JavaScript/TypeScript settings
export CLAUDE_HOOKS_JS_ENABLED=true
export CLAUDE_HOOKS_JS_PACKAGE_MANAGER="npm"  # or "yarn", "pnpm"

# Rust settings
export CLAUDE_HOOKS_RUST_ENABLED=true
export CLAUDE_HOOKS_RUST_CLIPPY_ARGS="-- -D warnings"

# Nix settings
export CLAUDE_HOOKS_NIX_ENABLED=true
export CLAUDE_HOOKS_NIX_FORMATTER="nixpkgs-fmt"  # or "alejandra"

# ============================================================================
# QUALITY THRESHOLDS
# ============================================================================

# Minimum test coverage percentage (0-100)
export CLAUDE_HOOKS_MIN_COVERAGE=80

# Maximum cyclomatic complexity
export CLAUDE_HOOKS_MAX_COMPLEXITY=10

# Maximum file size in KB
export CLAUDE_HOOKS_MAX_FILE_SIZE=500

# ============================================================================
# CUSTOM CHECKS
# ============================================================================

# Add custom check functions here
# They should return 0 for success, non-zero for failure

check_no_todos() {
    local todos=$(grep -r "TODO\|FIXME\|XXX" --include="*.go" --include="*.py" --include="*.js" --include="*.ts" . 2>/dev/null | grep -v vendor/ | grep -v node_modules/ || true)
    if [[ -n "$todos" ]]; then
        echo "Found TODO/FIXME comments:"
        echo "$todos"
        return 1
    fi
    return 0
}

# Uncomment to enable custom checks
# export CLAUDE_HOOKS_CUSTOM_CHECKS="check_no_todos"