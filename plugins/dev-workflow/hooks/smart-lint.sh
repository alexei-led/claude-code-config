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
#   0 - All checks passed successfully
#   2 - Blocking issues found that need to be fixed

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=smart-lint/main.sh
source "$SCRIPT_DIR/smart-lint/main.sh"
