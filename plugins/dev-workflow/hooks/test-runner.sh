#!/usr/bin/env bash
# test-runner.sh - Automated test execution after code changes
#
# DESCRIPTION
#   Auto-detects project type and runs appropriate tests
#
# EXIT CODES
#   0 - All tests passed
#   1 - Test failures or errors
#   2 - No test framework found

set +e # Don't exit on test failures, we want to report them

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "" >&2
echo "🧪 Running tests..." >&2
echo "──────────────────" >&2

# Detect project type (reuse logic from smart-lint.sh)
detect_project_type() {
	if [[ -f "go.mod" ]]; then
		echo "go"
	elif [[ -f "package.json" ]]; then
		echo "javascript"
	elif [[ -f "pyproject.toml" ]] || [[ -f "setup.py" ]]; then
		echo "python"
	elif [[ -f "Cargo.toml" ]]; then
		echo "rust"
	else
		echo "unknown"
	fi
}

PROJECT_TYPE=$(detect_project_type)
EXIT_CODE=0

case "$PROJECT_TYPE" in
"go")
	if [[ -f "Makefile" ]] && grep -q "^test:" Makefile; then
		echo -e "${BLUE}[INFO]${NC} Running: make test" >&2
		make test
		EXIT_CODE=$?
	else
		echo -e "${BLUE}[INFO]${NC} Running: go test ./..." >&2
		go test ./... -v
		EXIT_CODE=$?
	fi
	;;

"javascript")
	if [[ -f "package.json" ]] && grep -q '"test"' package.json; then
		echo -e "${BLUE}[INFO]${NC} Running: npm test" >&2
		npm test
		EXIT_CODE=$?
	else
		echo -e "${YELLOW}[WARN]${NC} No test script found in package.json" >&2
		EXIT_CODE=2
	fi
	;;

"python")
	if command -v pytest &>/dev/null; then
		echo -e "${BLUE}[INFO]${NC} Running: pytest" >&2
		pytest -v
		EXIT_CODE=$?
	elif python -c "import pytest" 2>/dev/null; then
		echo -e "${BLUE}[INFO]${NC} Running: python -m pytest" >&2
		python -m pytest -v
		EXIT_CODE=$?
	else
		echo -e "${YELLOW}[WARN]${NC} No pytest found" >&2
		EXIT_CODE=2
	fi
	;;

"rust")
	if command -v cargo &>/dev/null; then
		echo -e "${BLUE}[INFO]${NC} Running: cargo test" >&2
		cargo test
		EXIT_CODE=$?
	else
		echo -e "${YELLOW}[WARN]${NC} Cargo not found" >&2
		EXIT_CODE=2
	fi
	;;

*)
	echo -e "${YELLOW}[WARN]${NC} Unknown project type, cannot run tests" >&2
	EXIT_CODE=2
	;;
esac

# Report results
echo "" >&2
if [[ $EXIT_CODE -eq 0 ]]; then
	echo -e "${GREEN}✅ All tests passed!${NC}" >&2
elif [[ $EXIT_CODE -eq 2 ]]; then
	echo -e "${YELLOW}⚠️  No test framework found${NC}" >&2
else
	echo -e "${RED}❌ Tests failed!${NC}" >&2
fi

exit $EXIT_CODE
