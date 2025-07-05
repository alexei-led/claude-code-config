#!/usr/bin/env bash
# pre-commit-verify.sh - Prevent commits with any code quality issues
#
# DESCRIPTION
#   Runs smart-lint before allowing commits. ALL issues must be fixed.
#
# EXIT CODES
#   0 - All checks passed, commit allowed
#   1 - Issues found, commit blocked

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Pre-commit verification..." >&2
echo "────────────────────────────" >&2

# Run smart-lint
"${SCRIPT_DIR}/smart-lint.sh" "$@"
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    echo "" >&2
    echo "🚫 COMMIT BLOCKED: Fix all issues above before committing!" >&2
    echo "" >&2
    exit 1
fi

echo "✅ All checks passed - commit allowed" >&2
exit 0